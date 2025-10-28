"""
Non-parametric rank tests: Mann-Whitney U, Wilcoxon, Kruskal-Wallis
"""

from typing import Dict, Optional
import numpy as np
from scipy import stats

from src.core.base_test import BaseHypothesisTest, TestType


class MannWhitneyUTest(BaseHypothesisTest):
    """
    Mann-Whitney U test: Non-parametric alternative to two-sample t-test.

    Use cases:
    - Ordinal data: Customer satisfaction ratings (1-5 stars)
    - Non-normal data: Skewed distributions
    - Small sample sizes: When normality assumption is violated

    Assumptions:
    - Independent observations
    - Ordinal or continuous data
    - No assumption of normality

    Example:
        Customer satisfaction: Old process vs New process
        Test if medians differ significantly
    """

    def __init__(self, alpha: float = 0.05, alternative: str = 'two-sided'):
        super().__init__(alpha)
        self.alternative = alternative

    def test_type(self) -> TestType:
        return TestType.MANN_WHITNEY_U

    def validate_input(self, group1: np.ndarray, group2: np.ndarray) -> bool:
        return (len(group1) > 0 and len(group2) > 0 and
                not np.any(np.isnan(group1)) and not np.any(np.isnan(group2)))

    def check_assumptions(self, group1: np.ndarray, group2: np.ndarray) -> Dict[str, bool]:
        return {
            "independence": True,
            "ordinal_or_continuous": True,
            "sufficient_sample_size": len(group1) >= 3 and len(group2) >= 3
        }

    def compute_statistic(self, group1: np.ndarray, group2: np.ndarray) -> tuple:
        statistic, p_value = stats.mannwhitneyu(group1, group2, alternative=self.alternative)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: The two groups have the same distribution (medians are equal)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        if self.alternative == 'two-sided':
            return "H₁: The two groups have different distributions (medians differ)"
        elif self.alternative == 'greater':
            return "H₁: Group 1 has larger values than Group 2"
        else:
            return "H₁: Group 1 has smaller values than Group 2"

    def interpret_result(self, statistic: float, p_value: float,
                        group1: np.ndarray = None, group2: np.ndarray = None, **kwargs) -> str:
        if group1 is not None and group2 is not None:
            median1, median2 = np.median(group1), np.median(group2)

            if p_value < self.alpha:
                return (f"Groups differ significantly (U={statistic:.2f}, p={p_value:.4f}). "
                       f"Group 1 median={median1:.2f}, Group 2 median={median2:.2f}. "
                       f"With p < α={self.alpha}, we reject H₀.")
            else:
                return (f"No significant difference between groups (U={statistic:.2f}, p={p_value:.4f}). "
                       f"With p ≥ α={self.alpha}, we fail to reject H₀.")
        return "Insufficient data"

    def get_sample_sizes(self, group1: np.ndarray, group2: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"group1": len(group1), "group2": len(group2)}


class WilcoxonSignedRankTest(BaseHypothesisTest):
    """
    Wilcoxon signed-rank test: Non-parametric alternative to paired t-test.

    Use cases:
    - Paired ordinal data
    - Before-after comparisons with non-normal differences
    - Small sample sizes

    Example:
        Pain ratings before/after treatment (1-10 scale)
        Test if treatment reduced pain
    """

    def __init__(self, alpha: float = 0.05, alternative: str = 'two-sided'):
        super().__init__(alpha)
        self.alternative = alternative

    def test_type(self) -> TestType:
        return TestType.WILCOXON_SIGNED_RANK

    def validate_input(self, before: np.ndarray, after: np.ndarray) -> bool:
        return (len(before) == len(after) and len(before) > 0 and
                not np.any(np.isnan(before)) and not np.any(np.isnan(after)))

    def check_assumptions(self, before: np.ndarray, after: np.ndarray) -> Dict[str, bool]:
        differences = after - before
        non_zero_diffs = differences[differences != 0]

        return {
            "paired_data": len(before) == len(after),
            "ordinal_or_continuous": True,
            "sufficient_non_zero_differences": len(non_zero_diffs) >= 5
        }

    def compute_statistic(self, before: np.ndarray, after: np.ndarray) -> tuple:
        statistic, p_value = stats.wilcoxon(before, after, alternative=self.alternative)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: The median difference is zero (no change)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        if self.alternative == 'two-sided':
            return "H₁: The median difference is not zero (there is a change)"
        elif self.alternative == 'greater':
            return "H₁: After values are greater than before"
        else:
            return "H₁: After values are less than before"

    def interpret_result(self, statistic: float, p_value: float,
                        before: np.ndarray = None, after: np.ndarray = None, **kwargs) -> str:
        if before is not None and after is not None:
            median_before = np.median(before)
            median_after = np.median(after)
            median_diff = median_after - median_before

            if p_value < self.alpha:
                direction = "increased" if median_diff > 0 else "decreased"
                return (f"Values significantly {direction} (W={statistic:.2f}, p={p_value:.4f}). "
                       f"Median before={median_before:.2f}, after={median_after:.2f}. "
                       f"With p < α={self.alpha}, we reject H₀.")
            else:
                return (f"No significant change (W={statistic:.2f}, p={p_value:.4f}). "
                       f"With p ≥ α={self.alpha}, we fail to reject H₀.")
        return "Insufficient data"

    def get_sample_sizes(self, before: np.ndarray, after: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"n_pairs": len(before)}


class KruskalWallisTest(BaseHypothesisTest):
    """
    Kruskal-Wallis H test: Non-parametric alternative to one-way ANOVA.

    Use cases:
    - Compare 3+ independent groups with non-normal data
    - Ordinal outcome variables
    - Small sample sizes

    Example:
        Job satisfaction across 3 departments (ordinal 1-5)
        Test if any department differs
    """

    def __init__(self, alpha: float = 0.05):
        super().__init__(alpha)

    def test_type(self) -> TestType:
        return TestType.KRUSKAL_WALLIS

    def validate_input(self, *groups) -> bool:
        if len(groups) < 2:
            return False

        for group in groups:
            if not isinstance(group, np.ndarray):
                group = np.array(group)
            if len(group) < 1 or np.any(np.isnan(group)):
                return False

        return True

    def check_assumptions(self, *groups) -> Dict[str, bool]:
        return {
            "independence": True,
            "ordinal_or_continuous": True,
            "sufficient_groups": len(groups) >= 2,
            "sufficient_sample_size": all(len(g) >= 5 for g in groups)
        }

    def compute_statistic(self, *groups) -> tuple:
        statistic, p_value = stats.kruskal(*groups)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        n_groups = kwargs.get('n_groups', 'k')
        return f"H₀: All {n_groups} groups have the same distribution (medians are equal)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return "H₁: At least one group has a different distribution"

    def interpret_result(self, statistic: float, p_value: float, *groups, **kwargs) -> str:
        if len(groups) > 0:
            group_medians = [np.median(group) for group in groups]
            n_groups = len(groups)

            if p_value < self.alpha:
                medians_str = ", ".join([f"Group {i+1}: {m:.2f}" for i, m in enumerate(group_medians)])
                return (f"At least one group differs significantly (H={statistic:.2f}, p={p_value:.4f}). "
                       f"Group medians: {medians_str}. With p < α={self.alpha}, we reject H₀. "
                       f"Post-hoc tests recommended.")
            else:
                return (f"No significant differences among {n_groups} groups (H={statistic:.2f}, p={p_value:.4f}). "
                       f"With p ≥ α={self.alpha}, we fail to reject H₀.")
        return "Insufficient data"

    def get_sample_sizes(self, *groups, **kwargs) -> Dict[str, int]:
        return {f"group_{i+1}": len(group) for i, group in enumerate(groups)}

    def generate_recommendation(self, decision: str, assumptions: Dict[str, bool], **kwargs) -> str:
        base_rec = super().generate_recommendation(decision, assumptions, **kwargs)

        if decision == "reject":
            base_rec += " Consider post-hoc pairwise comparisons (Dunn's test) to identify which groups differ."

        return base_rec
