"""
ANOVA tests: One-way ANOVA for comparing means across multiple groups
"""

from typing import Dict, List, Optional
import numpy as np
from scipy import stats

from src.core.base_test import BaseHypothesisTest, TestType


class OneWayANOVA(BaseHypothesisTest):
    """
    One-way ANOVA: Compare means of three or more independent groups.

    Use cases:
    - Sales across 3+ stores: Test if any store differs
    - Multiple treatment groups vs control
    - Comparing customer satisfaction across regions

    Assumptions:
    - Data are continuous
    - Data are approximately normally distributed in each group
    - Groups have equal variances (homoscedasticity)
    - Observations are independent

    Example:
        Sales across 3 stores: H₀: μ_A = μ_B = μ_C
        Store A: mean=$5000, Store B: mean=$5200, Store C: mean=$4800
        Test if at least one store differs significantly
    """

    def __init__(self, alpha: float = 0.05):
        super().__init__(alpha)

    def test_type(self) -> TestType:
        return TestType.ONE_WAY_ANOVA

    def validate_input(self, *groups) -> bool:
        """Validate that we have at least 2 groups with sufficient data"""
        if len(groups) < 2:
            return False

        for group in groups:
            if not isinstance(group, np.ndarray):
                group = np.array(group)
            if len(group) < 2 or np.any(np.isnan(group)):
                return False

        return True

    def check_assumptions(self, *groups) -> Dict[str, bool]:
        """Check ANOVA assumptions"""
        assumptions = {
            "independence": True,  # Assumed
            "sufficient_groups": len(groups) >= 2,
        }

        # Check normality for each group
        all_normal = True
        for i, group in enumerate(groups):
            if len(group) < 5000:
                _, p_norm = stats.shapiro(group)
                if p_norm <= 0.05 and len(group) <= 30:
                    all_normal = False
                    break

        assumptions["normality"] = all_normal

        # Check equal variances (Levene's test)
        if len(groups) >= 2:
            _, p_levene = stats.levene(*groups)
            assumptions["equal_variances"] = p_levene > 0.05
        else:
            assumptions["equal_variances"] = True

        return assumptions

    def compute_statistic(self, *groups) -> tuple:
        """Compute F-statistic and p-value"""
        statistic, p_value = stats.f_oneway(*groups)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        n_groups = kwargs.get('n_groups', 'k')
        return f"H₀: μ₁ = μ₂ = ... = μ_{n_groups} (all group means are equal)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return "H₁: At least one group mean differs from the others"

    def interpret_result(self, statistic: float, p_value: float, *groups, **kwargs) -> str:
        if len(groups) > 0:
            group_means = [np.mean(group) for group in groups]
            n_groups = len(groups)

            if p_value < self.alpha:
                means_str = ", ".join([f"Group {i+1}: {m:.2f}" for i, m in enumerate(group_means)])
                return (f"At least one group differs significantly (F={statistic:.2f}, p={p_value:.4f}). "
                       f"Group means: {means_str}. With p < α={self.alpha}, we reject H₀. "
                       f"Post-hoc tests recommended to identify which groups differ.")
            else:
                return (f"No significant differences among {n_groups} groups (F={statistic:.2f}, p={p_value:.4f}). "
                       f"With p ≥ α={self.alpha}, we fail to reject H₀. All groups may have similar means.")
        return "Insufficient data"

    def calculate_effect_size(self, *groups, **kwargs) -> Optional[float]:
        """Calculate eta-squared (η²) effect size"""
        # Flatten all groups
        all_data = np.concatenate(groups)
        grand_mean = np.mean(all_data)

        # Between-group sum of squares
        ss_between = sum(len(group) * (np.mean(group) - grand_mean)**2 for group in groups)

        # Total sum of squares
        ss_total = np.sum((all_data - grand_mean)**2)

        if ss_total == 0:
            return None

        eta_squared = ss_between / ss_total
        return float(eta_squared)

    def get_sample_sizes(self, *groups, **kwargs) -> Dict[str, int]:
        return {f"group_{i+1}": len(group) for i, group in enumerate(groups)}

    def generate_recommendation(self, decision: str, assumptions: Dict[str, bool], **kwargs) -> str:
        """Generate ANOVA-specific recommendations"""
        unmet = [k for k, v in assumptions.items() if not v]

        base_rec = super().generate_recommendation(decision, assumptions, **kwargs)

        if decision == "reject":
            base_rec += " Consider post-hoc tests (Tukey HSD, Bonferroni) to identify which specific groups differ."

        if not assumptions.get("equal_variances", True):
            base_rec += " WARNING: Equal variance assumption violated. Consider Welch's ANOVA or Kruskal-Wallis test."

        return base_rec
