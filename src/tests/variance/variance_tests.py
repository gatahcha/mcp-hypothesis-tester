"""
Variance tests: Levene's, Bartlett's, F-test for testing equality of variances
"""

from typing import Dict, Optional
import numpy as np
from scipy import stats

from src.core.base_test import BaseHypothesisTest, TestType


class LeveneTest(BaseHypothesisTest):
    """
    Levene's test: Tests equality of variances across groups.

    Use cases:
    - Check assumption for ANOVA and t-tests
    - Quality control: Ensure consistent variability
    - Robust to departures from normality

    Example:
        Sales variability: Compare variance across 3 stores
        If equal variance: Use standard ANOVA
        If unequal variance: Use Welch's ANOVA
    """

    def __init__(self, alpha: float = 0.05, center: str = 'median'):
        """
        Args:
            alpha: Significance level
            center: 'mean', 'median', or 'trimmed' for centering
                   'median' is most robust to outliers
        """
        super().__init__(alpha)
        self.center = center

    def test_type(self) -> TestType:
        return TestType.LEVENE

    def validate_input(self, *groups) -> bool:
        if len(groups) < 2:
            return False

        for group in groups:
            if not isinstance(group, np.ndarray):
                group = np.array(group)
            if len(group) < 2 or np.any(np.isnan(group)):
                return False

        return True

    def check_assumptions(self, *groups) -> Dict[str, bool]:
        return {
            "sufficient_groups": len(groups) >= 2,
            "sufficient_sample_size": all(len(g) >= 2 for g in groups),
            "continuous_data": True
        }

    def compute_statistic(self, *groups) -> tuple:
        statistic, p_value = stats.levene(*groups, center=self.center)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        n_groups = len(kwargs.get('groups', [])) if 'groups' in kwargs else 'k'
        return f"H₀: All {n_groups} groups have equal variances (homoscedasticity)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return "H₁: At least one group has different variance (heteroscedasticity)"

    def interpret_result(self, statistic: float, p_value: float, *groups, **kwargs) -> str:
        if len(groups) > 0:
            group_vars = [np.var(group, ddof=1) for group in groups]
            n_groups = len(groups)

            if p_value < self.alpha:
                vars_str = ", ".join([f"Group {i+1}: {v:.2f}" for i, v in enumerate(group_vars)])
                return (f"Variances are NOT equal (W={statistic:.2f}, p={p_value:.4f}). "
                       f"Group variances: {vars_str}. With p < α={self.alpha}, we reject H₀. "
                       f"Use Welch's t-test/ANOVA or transform data.")
            else:
                return (f"Variances appear equal (W={statistic:.2f}, p={p_value:.4f}). "
                       f"With p ≥ α={self.alpha}, we fail to reject H₀. "
                       f"Standard t-test/ANOVA assumptions met.")
        return "Insufficient data"

    def get_sample_sizes(self, *groups, **kwargs) -> Dict[str, int]:
        return {f"group_{i+1}": len(group) for i, group in enumerate(groups)}

    def generate_recommendation(self, decision: str, assumptions: Dict[str, bool], **kwargs) -> str:
        if decision == "reject":
            return ("Variances differ significantly. Recommendations: "
                   "(1) Use Welch's t-test (unequal variances), "
                   "(2) Use Welch's ANOVA, "
                   "(3) Transform data (log, sqrt) to stabilize variance, "
                   "(4) Use non-parametric tests.")
        else:
            return "Equal variance assumption met. Standard parametric tests are appropriate."


class BartlettTest(BaseHypothesisTest):
    """
    Bartlett's test: Tests equality of variances across groups.
    More sensitive to departures from normality than Levene's test.

    Use cases:
    - When data is known to be normally distributed
    - More powerful than Levene's for normal data
    - NOT recommended if normality is questionable

    Example:
        Compare measurement precision across 3 instruments
    """

    def __init__(self, alpha: float = 0.05):
        super().__init__(alpha)

    def test_type(self) -> TestType:
        return TestType.BARTLETT

    def validate_input(self, *groups) -> bool:
        if len(groups) < 2:
            return False

        for group in groups:
            if not isinstance(group, np.ndarray):
                group = np.array(group)
            if len(group) < 2 or np.any(np.isnan(group)):
                return False

        return True

    def check_assumptions(self, *groups) -> Dict[str, bool]:
        """Bartlett requires normality"""
        assumptions = {
            "sufficient_groups": len(groups) >= 2,
            "sufficient_sample_size": all(len(g) >= 2 for g in groups),
        }

        # Check normality for each group
        all_normal = True
        for group in groups:
            if len(group) < 5000:
                _, p_norm = stats.shapiro(group)
                if p_norm <= 0.05:
                    all_normal = False
                    break

        assumptions["normality"] = all_normal

        return assumptions

    def compute_statistic(self, *groups) -> tuple:
        statistic, p_value = stats.bartlett(*groups)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: All groups have equal variances"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return "H₁: At least one group has different variance"

    def interpret_result(self, statistic: float, p_value: float, *groups, **kwargs) -> str:
        if len(groups) > 0:
            group_vars = [np.var(group, ddof=1) for group in groups]

            if p_value < self.alpha:
                vars_str = ", ".join([f"Group {i+1}: {v:.2f}" for i, v in enumerate(group_vars)])
                return (f"Variances differ significantly (T={statistic:.2f}, p={p_value:.4f}). "
                       f"Group variances: {vars_str}. With p < α={self.alpha}, we reject H₀.")
            else:
                return (f"Variances appear equal (T={statistic:.2f}, p={p_value:.4f}). "
                       f"With p ≥ α={self.alpha}, we fail to reject H₀.")
        return "Insufficient data"

    def get_sample_sizes(self, *groups, **kwargs) -> Dict[str, int]:
        return {f"group_{i+1}": len(group) for i, group in enumerate(groups)}

    def generate_recommendation(self, decision: str, assumptions: Dict[str, bool], **kwargs) -> str:
        base_rec = super().generate_recommendation(decision, assumptions, **kwargs)

        if not assumptions.get("normality", True):
            base_rec = ("WARNING: Bartlett's test requires normality. Data may not be normal. "
                       "Use Levene's test instead (more robust). " + base_rec)

        return base_rec


class FTestVariance(BaseHypothesisTest):
    """
    F-test for equality of variances: Compares variances of two groups.

    Use cases:
    - Compare precision of two instruments
    - Check equal variance assumption for two-sample t-test
    - Quality control: Compare variability of two processes

    Note: Sensitive to departures from normality
    """

    def __init__(self, alpha: float = 0.05, alternative: str = 'two-sided'):
        super().__init__(alpha)
        self.alternative = alternative

    def test_type(self) -> TestType:
        return TestType.F_TEST_VARIANCE

    def validate_input(self, group1: np.ndarray, group2: np.ndarray) -> bool:
        return (len(group1) >= 2 and len(group2) >= 2 and
                not np.any(np.isnan(group1)) and not np.any(np.isnan(group2)))

    def check_assumptions(self, group1: np.ndarray, group2: np.ndarray) -> Dict[str, bool]:
        # Check normality
        _, p1 = stats.shapiro(group1) if len(group1) < 5000 else (0, 1)
        _, p2 = stats.shapiro(group2) if len(group2) < 5000 else (0, 1)

        return {
            "group1_normality": p1 > 0.05,
            "group2_normality": p2 > 0.05,
            "sufficient_sample_size": len(group1) >= 2 and len(group2) >= 2
        }

    def compute_statistic(self, group1: np.ndarray, group2: np.ndarray) -> tuple:
        """Compute F-statistic for variance ratio"""
        var1 = np.var(group1, ddof=1)
        var2 = np.var(group2, ddof=1)

        # F = larger variance / smaller variance
        if var1 >= var2:
            f_stat = var1 / var2
            df1, df2 = len(group1) - 1, len(group2) - 1
        else:
            f_stat = var2 / var1
            df1, df2 = len(group2) - 1, len(group1) - 1

        # Calculate p-value
        if self.alternative == 'two-sided':
            p_value = 2 * min(stats.f.cdf(f_stat, df1, df2), 1 - stats.f.cdf(f_stat, df1, df2))
        elif self.alternative == 'greater':
            p_value = 1 - stats.f.cdf(f_stat, df1, df2)
        else:  # less
            p_value = stats.f.cdf(f_stat, df1, df2)

        return float(f_stat), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: σ₁² = σ₂² (variances are equal)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        if self.alternative == 'two-sided':
            return "H₁: σ₁² ≠ σ₂² (variances are different)"
        elif self.alternative == 'greater':
            return "H₁: σ₁² > σ₂² (variance 1 is greater)"
        else:
            return "H₁: σ₁² < σ₂² (variance 1 is less)"

    def interpret_result(self, statistic: float, p_value: float,
                        group1: np.ndarray = None, group2: np.ndarray = None, **kwargs) -> str:
        if group1 is not None and group2 is not None:
            var1 = np.var(group1, ddof=1)
            var2 = np.var(group2, ddof=1)

            if p_value < self.alpha:
                return (f"Variances differ significantly (F={statistic:.2f}, p={p_value:.4f}). "
                       f"Var1={var1:.2f}, Var2={var2:.2f}, Ratio={var1/var2:.2f}. "
                       f"With p < α={self.alpha}, we reject H₀. Use Welch's t-test.")
            else:
                return (f"Variances appear equal (F={statistic:.2f}, p={p_value:.4f}). "
                       f"Var1={var1:.2f}, Var2={var2:.2f}. "
                       f"With p ≥ α={self.alpha}, we fail to reject H₀. Standard t-test OK.")
        return "Insufficient data"

    def get_sample_sizes(self, group1: np.ndarray, group2: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"group1": len(group1), "group2": len(group2)}

    def generate_recommendation(self, decision: str, assumptions: Dict[str, bool], **kwargs) -> str:
        base_rec = super().generate_recommendation(decision, assumptions, **kwargs)

        if not assumptions.get("group1_normality", True) or not assumptions.get("group2_normality", True):
            base_rec = ("WARNING: F-test requires normality. Use Levene's test instead (more robust). " + base_rec)

        return base_rec
