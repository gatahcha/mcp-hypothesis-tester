"""
Parametric t-tests: One-sample, Two-sample (independent), and Paired t-tests
"""

from typing import Dict, Optional
import numpy as np
from scipy import stats

from src.core.base_test import BaseHypothesisTest, TestType


class OneSampleTTest(BaseHypothesisTest):
    """
    One-sample t-test: Tests if the mean of a single sample differs from a known value.

    Use cases:
    - Sales example: Test if current sales ($5,150) differ from historical baseline ($5,000)
    - Quality control: Test if product measurements meet specifications
    - Before-after studies: Test if measurements changed from baseline

    Assumptions:
    - Data is continuous
    - Data is approximately normally distributed (or n > 30)
    - Observations are independent

    Example from documentation:
        Store sales: H₀: μ = 5000, H₁: μ ≠ 5000
        Data: mean=$5,150, SD=$480, n=45
        Result: t=2.096, p=0.042 → Reject H₀ (sales increased!)
    """

    def __init__(self, alpha: float = 0.05, mu0: float = 0.0, alternative: str = 'two-sided'):
        """
        Args:
            alpha: Significance level (default: 0.05)
            mu0: Hypothesized population mean
            alternative: 'two-sided', 'less', or 'greater'
        """
        super().__init__(alpha)
        self.mu0 = mu0
        self.alternative = alternative

    def test_type(self) -> TestType:
        return TestType.ONE_SAMPLE_T_TEST

    def validate_input(self, data: np.ndarray) -> bool:
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        return len(data) > 1 and not np.any(np.isnan(data))

    def check_assumptions(self, data: np.ndarray) -> Dict[str, bool]:
        """Check test assumptions"""
        # Normality check (Shapiro-Wilk)
        if len(data) < 5000:
            _, p_norm = stats.shapiro(data)
            is_normal = p_norm > 0.05
        else:
            is_normal = True  # Assume normal for large samples (CLT)

        return {
            "normality": is_normal or len(data) > 30,  # CLT kicks in
            "independence": True,  # Assume independent (can't test automatically)
            "sufficient_sample_size": len(data) >= 2
        }

    def compute_statistic(self, data: np.ndarray) -> tuple:
        """Compute t-statistic and p-value"""
        statistic, p_value = stats.ttest_1samp(data, self.mu0, alternative=self.alternative)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return f"H₀: μ = {self.mu0} (population mean equals {self.mu0})"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        if self.alternative == 'two-sided':
            return f"H₁: μ ≠ {self.mu0} (population mean differs from {self.mu0})"
        elif self.alternative == 'greater':
            return f"H₁: μ > {self.mu0} (population mean is greater than {self.mu0})"
        else:
            return f"H₁: μ < {self.mu0} (population mean is less than {self.mu0})"

    def interpret_result(self, statistic: float, p_value: float, data: np.ndarray = None, **kwargs) -> str:
        if data is not None:
            mean = np.mean(data)
            diff = mean - self.mu0
            pct_change = (diff / self.mu0 * 100) if self.mu0 != 0 else 0

            if p_value < self.alpha:
                return (f"The sample mean ({mean:.2f}) is statistically significantly different from "
                       f"the hypothesized value ({self.mu0}). This represents a {pct_change:.1f}% change. "
                       f"With p={p_value:.4f} < α={self.alpha}, we reject H₀.")
            else:
                return (f"The sample mean ({mean:.2f}) is not statistically significantly different from "
                       f"the hypothesized value ({self.mu0}). With p={p_value:.4f} ≥ α={self.alpha}, "
                       f"we fail to reject H₀. The observed difference could be due to random variation.")
        else:
            return "Insufficient data for interpretation"

    def calculate_effect_size(self, data: np.ndarray, **kwargs) -> Optional[float]:
        """Calculate Cohen's d effect size"""
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        if std == 0:
            return None
        cohens_d = (mean - self.mu0) / std
        return float(cohens_d)

    def calculate_confidence_interval(self, data: np.ndarray, **kwargs) -> Optional[tuple]:
        """Calculate confidence interval for the mean"""
        mean = np.mean(data)
        se = stats.sem(data)
        ci = stats.t.interval(1 - self.alpha, len(data) - 1, loc=mean, scale=se)
        return (float(ci[0]), float(ci[1]))

    def get_sample_sizes(self, data: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"n": len(data)}


class TwoSampleTTest(BaseHypothesisTest):
    """
    Independent two-sample t-test: Compare means of two independent groups.

    Use cases:
    - Coffee shop: Old machine (avg=7.2/10) vs New machine (avg=7.8/10)
    - A/B testing: Control group vs Treatment group
    - Gender differences: Male performance vs Female performance

    Assumptions:
    - Data in both groups are continuous
    - Data are approximately normally distributed
    - Observations are independent between groups
    - Equal variances (or use Welch's t-test if unequal)

    Example from documentation:
        Coffee machine ratings: H₀: μ_old = μ_new, H₁: μ_old ≠ μ_new
        Old: mean=7.2, n=30
        New: mean=7.8, n=30
        Result: p=0.03 → Reject H₀ (new machine is better!)
    """

    def __init__(self, alpha: float = 0.05, equal_var: bool = True, alternative: str = 'two-sided'):
        """
        Args:
            alpha: Significance level
            equal_var: If True, assume equal variances (standard t-test)
                      If False, use Welch's t-test (unequal variances)
            alternative: 'two-sided', 'less', or 'greater'
        """
        super().__init__(alpha)
        self.equal_var = equal_var
        self.alternative = alternative

    def test_type(self) -> TestType:
        return TestType.TWO_SAMPLE_T_TEST

    def validate_input(self, group1: np.ndarray, group2: np.ndarray) -> bool:
        return (len(group1) > 1 and len(group2) > 1 and
                not np.any(np.isnan(group1)) and not np.any(np.isnan(group2)))

    def check_assumptions(self, group1: np.ndarray, group2: np.ndarray) -> Dict[str, bool]:
        # Normality for both groups
        _, p1 = stats.shapiro(group1) if len(group1) < 5000 else (0, 1)
        _, p2 = stats.shapiro(group2) if len(group2) < 5000 else (0, 1)

        # Equal variance (Levene's test)
        _, p_levene = stats.levene(group1, group2)

        return {
            "group1_normality": p1 > 0.05 or len(group1) > 30,
            "group2_normality": p2 > 0.05 or len(group2) > 30,
            "equal_variances": p_levene > 0.05,
            "independence": True
        }

    def compute_statistic(self, group1: np.ndarray, group2: np.ndarray) -> tuple:
        statistic, p_value = stats.ttest_ind(group1, group2,
                                              equal_var=self.equal_var,
                                              alternative=self.alternative)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: μ₁ = μ₂ (both groups have equal means)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        if self.alternative == 'two-sided':
            return "H₁: μ₁ ≠ μ₂ (groups have different means)"
        elif self.alternative == 'greater':
            return "H₁: μ₁ > μ₂ (group 1 mean is greater)"
        else:
            return "H₁: μ₁ < μ₂ (group 1 mean is less)"

    def interpret_result(self, statistic: float, p_value: float,
                        group1: np.ndarray = None, group2: np.ndarray = None, **kwargs) -> str:
        if group1 is not None and group2 is not None:
            mean1, mean2 = np.mean(group1), np.mean(group2)
            diff = mean1 - mean2

            if p_value < self.alpha:
                return (f"Group 1 (mean={mean1:.2f}) and Group 2 (mean={mean2:.2f}) are "
                       f"statistically significantly different (difference={diff:.2f}). "
                       f"With p={p_value:.4f} < α={self.alpha}, we reject H₀.")
            else:
                return (f"No significant difference between Group 1 (mean={mean1:.2f}) and "
                       f"Group 2 (mean={mean2:.2f}). With p={p_value:.4f} ≥ α={self.alpha}, "
                       f"we fail to reject H₀.")
        return "Insufficient data for interpretation"

    def calculate_effect_size(self, group1: np.ndarray, group2: np.ndarray, **kwargs) -> Optional[float]:
        """Calculate Cohen's d"""
        mean1, mean2 = np.mean(group1), np.mean(group2)
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        if pooled_std == 0:
            return None

        cohens_d = (mean1 - mean2) / pooled_std
        return float(cohens_d)

    def get_sample_sizes(self, group1: np.ndarray, group2: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"group1": len(group1), "group2": len(group2)}


class PairedTTest(BaseHypothesisTest):
    """
    Paired t-test: Compare means of two related samples.

    Use cases:
    - Website redesign: Visit time before (5 min) vs after (5.5 min)
    - Pre-test vs Post-test: Student scores before and after training
    - Repeated measures: Same subjects measured twice

    Assumptions:
    - Paired data (same subjects/units measured twice)
    - Differences are approximately normally distributed
    - Observations are independent between pairs

    Example from documentation:
        Website visit time: H₀: μ_diff = 0, H₁: μ_diff ≠ 0
        Before: 5.0 minutes
        After: 5.5 minutes
        Result: p=0.02 → Reject H₀ (visit time changed!)
    """

    def __init__(self, alpha: float = 0.05, alternative: str = 'two-sided'):
        super().__init__(alpha)
        self.alternative = alternative

    def test_type(self) -> TestType:
        return TestType.PAIRED_T_TEST

    def validate_input(self, before: np.ndarray, after: np.ndarray) -> bool:
        return (len(before) == len(after) and len(before) > 1 and
                not np.any(np.isnan(before)) and not np.any(np.isnan(after)))

    def check_assumptions(self, before: np.ndarray, after: np.ndarray) -> Dict[str, bool]:
        differences = after - before
        _, p_norm = stats.shapiro(differences) if len(differences) < 5000 else (0, 1)

        return {
            "differences_normality": p_norm > 0.05 or len(differences) > 30,
            "paired_data": len(before) == len(after),
            "independence": True
        }

    def compute_statistic(self, before: np.ndarray, after: np.ndarray) -> tuple:
        statistic, p_value = stats.ttest_rel(before, after, alternative=self.alternative)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: μ_diff = 0 (no difference between paired observations)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        if self.alternative == 'two-sided':
            return "H₁: μ_diff ≠ 0 (there is a difference)"
        elif self.alternative == 'greater':
            return "H₁: μ_diff > 0 (after is greater than before)"
        else:
            return "H₁: μ_diff < 0 (after is less than before)"

    def interpret_result(self, statistic: float, p_value: float,
                        before: np.ndarray = None, after: np.ndarray = None, **kwargs) -> str:
        if before is not None and after is not None:
            mean_before, mean_after = np.mean(before), np.mean(after)
            mean_diff = mean_after - mean_before

            if p_value < self.alpha:
                direction = "increased" if mean_diff > 0 else "decreased"
                return (f"Measurements significantly {direction} from {mean_before:.2f} to {mean_after:.2f} "
                       f"(difference={mean_diff:.2f}). With p={p_value:.4f} < α={self.alpha}, we reject H₀.")
            else:
                return (f"No significant change from {mean_before:.2f} to {mean_after:.2f}. "
                       f"With p={p_value:.4f} ≥ α={self.alpha}, we fail to reject H₀.")
        return "Insufficient data"

    def calculate_effect_size(self, before: np.ndarray, after: np.ndarray, **kwargs) -> Optional[float]:
        """Calculate Cohen's d for paired samples"""
        differences = after - before
        mean_diff = np.mean(differences)
        std_diff = np.std(differences, ddof=1)

        if std_diff == 0:
            return None

        cohens_d = mean_diff / std_diff
        return float(cohens_d)

    def calculate_confidence_interval(self, before: np.ndarray, after: np.ndarray, **kwargs) -> Optional[tuple]:
        """Calculate confidence interval for mean difference"""
        differences = after - before
        mean_diff = np.mean(differences)
        se = stats.sem(differences)
        ci = stats.t.interval(1 - self.alpha, len(differences) - 1, loc=mean_diff, scale=se)
        return (float(ci[0]), float(ci[1]))

    def get_sample_sizes(self, before: np.ndarray, after: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"n_pairs": len(before)}
