"""
Auto-suggest appropriate hypothesis tests based on data characteristics.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from scipy import stats
from dataclasses import dataclass


@dataclass
class DataCharacteristics:
    """Container for data characteristics analysis"""
    n_samples: int
    n_groups: int
    is_paired: bool
    is_normal: bool
    equal_variances: bool
    data_type: str  # 'continuous', 'ordinal', 'nominal'
    has_outliers: bool
    sample_size_adequate: bool


class TestSuggester:
    """
    Suggests appropriate statistical tests based on data characteristics.

    Decision tree logic:
    1. Determine data structure (single sample, two groups, multiple groups, paired)
    2. Check data type (continuous, ordinal, nominal)
    3. Check assumptions (normality, equal variance, sample size)
    4. Recommend parametric or non-parametric test
    """

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha

    def analyze_data(self, *data_groups) -> DataCharacteristics:
        """
        Analyze data characteristics to guide test selection.

        Args:
            *data_groups: One or more numpy arrays

        Returns:
            DataCharacteristics object with analysis results
        """
        n_groups = len(data_groups)

        if n_groups == 0:
            raise ValueError("At least one data group required")

        # Sample sizes
        sample_sizes = [len(group) for group in data_groups]
        total_n = sum(sample_sizes)
        min_n = min(sample_sizes)

        # Determine if paired (equal sample sizes, typically n_groups=2)
        is_paired = (n_groups == 2 and sample_sizes[0] == sample_sizes[1] and sample_sizes[0] < 100)

        # Check normality
        is_normal = self._check_normality(data_groups)

        # Check equal variances (if multiple groups)
        equal_variances = True
        if n_groups >= 2:
            equal_variances = self._check_equal_variances(data_groups)

        # Determine data type
        data_type = self._infer_data_type(data_groups[0])

        # Check for outliers
        has_outliers = self._check_outliers(data_groups)

        # Check sample size adequacy
        sample_size_adequate = min_n >= 30 or (min_n >= 20 and is_normal)

        return DataCharacteristics(
            n_samples=total_n,
            n_groups=n_groups,
            is_paired=is_paired,
            is_normal=is_normal,
            equal_variances=equal_variances,
            data_type=data_type,
            has_outliers=has_outliers,
            sample_size_adequate=sample_size_adequate
        )

    def _check_normality(self, data_groups: Tuple) -> bool:
        """Check if all groups are approximately normal"""
        for group in data_groups:
            if len(group) >= 3 and len(group) <= 5000:
                _, p_value = stats.shapiro(group)
                if p_value < 0.05 and len(group) < 30:
                    return False
        return True

    def _check_equal_variances(self, data_groups: Tuple) -> bool:
        """Check if variances are equal across groups"""
        if len(data_groups) < 2:
            return True

        try:
            _, p_value = stats.levene(*data_groups)
            return p_value >= 0.05
        except:
            return True

    def _infer_data_type(self, data: np.ndarray) -> str:
        """Infer if data is continuous, ordinal, or nominal"""
        unique_values = len(np.unique(data))
        n = len(data)

        # If few unique values relative to sample size, likely ordinal/nominal
        if unique_values <= 10:
            return 'ordinal'
        elif unique_values / n < 0.05:
            return 'nominal'
        else:
            return 'continuous'

    def _check_outliers(self, data_groups: Tuple) -> bool:
        """Check for presence of outliers using IQR method"""
        for group in data_groups:
            q1 = np.percentile(group, 25)
            q3 = np.percentile(group, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = np.sum((group < lower_bound) | (group > upper_bound))
            if outliers > 0:
                return True

        return False

    def suggest_test(self, *data_groups, **kwargs) -> Dict:
        """
        Suggest the most appropriate statistical test.

        Args:
            *data_groups: One or more data groups
            **kwargs: Additional parameters like 'mu0' for one-sample tests

        Returns:
            Dictionary with test suggestions and reasoning
        """
        chars = self.analyze_data(*data_groups)

        # Decision logic
        if chars.n_groups == 1:
            return self._suggest_one_sample_test(chars, **kwargs)
        elif chars.n_groups == 2:
            return self._suggest_two_sample_test(chars)
        else:
            return self._suggest_multi_sample_test(chars)

    def _suggest_one_sample_test(self, chars: DataCharacteristics, **kwargs) -> Dict:
        """Suggest test for single sample"""
        mu0 = kwargs.get('mu0', None)

        if chars.data_type in ['continuous']:
            if chars.is_normal or chars.sample_size_adequate:
                return {
                    "primary_test": "one_sample_t_test",
                    "test_name": "One-Sample T-Test",
                    "reason": "Data is continuous and approximately normal (or n ≥ 30)",
                    "confidence": "high",
                    "parameters": {"mu0": mu0} if mu0 else {},
                    "alternative_tests": ["sign_test", "wilcoxon_signed_rank"],
                    "assumptions_met": True
                }
            else:
                return {
                    "primary_test": "wilcoxon_signed_rank",
                    "test_name": "Wilcoxon Signed-Rank Test",
                    "reason": "Data is continuous but not normal with small sample size",
                    "confidence": "high",
                    "parameters": {},
                    "alternative_tests": ["sign_test"],
                    "assumptions_met": True
                }
        else:
            return {
                "primary_test": "sign_test",
                "test_name": "Sign Test",
                "reason": "Data is ordinal/nominal",
                "confidence": "medium",
                "parameters": {},
                "alternative_tests": [],
                "assumptions_met": True
            }

    def _suggest_two_sample_test(self, chars: DataCharacteristics) -> Dict:
        """Suggest test for two samples"""

        if chars.is_paired:
            # Paired samples
            if chars.data_type == 'continuous':
                if chars.is_normal or chars.sample_size_adequate:
                    return {
                        "primary_test": "paired_t_test",
                        "test_name": "Paired T-Test",
                        "reason": "Paired data, continuous, and approximately normal",
                        "confidence": "high",
                        "parameters": {},
                        "alternative_tests": ["wilcoxon_signed_rank"],
                        "assumptions_met": True
                    }
                else:
                    return {
                        "primary_test": "wilcoxon_signed_rank",
                        "test_name": "Wilcoxon Signed-Rank Test",
                        "reason": "Paired data, continuous, but not normal with small sample",
                        "confidence": "high",
                        "parameters": {},
                        "alternative_tests": ["sign_test"],
                        "assumptions_met": True
                    }
            else:
                return {
                    "primary_test": "wilcoxon_signed_rank",
                    "test_name": "Wilcoxon Signed-Rank Test",
                    "reason": "Paired ordinal data",
                    "confidence": "high",
                    "parameters": {},
                    "alternative_tests": ["sign_test"],
                    "assumptions_met": True
                }
        else:
            # Independent samples
            if chars.data_type == 'continuous':
                if chars.is_normal or chars.sample_size_adequate:
                    if chars.equal_variances:
                        return {
                            "primary_test": "two_sample_t_test",
                            "test_name": "Independent Two-Sample T-Test",
                            "reason": "Independent groups, continuous, normal, equal variances",
                            "confidence": "high",
                            "parameters": {"equal_var": True},
                            "alternative_tests": ["mann_whitney_u"],
                            "assumptions_met": True
                        }
                    else:
                        return {
                            "primary_test": "two_sample_t_test",
                            "test_name": "Welch's T-Test",
                            "reason": "Independent groups, continuous, normal, but unequal variances",
                            "confidence": "high",
                            "parameters": {"equal_var": False},
                            "alternative_tests": ["mann_whitney_u"],
                            "assumptions_met": False,
                            "warning": "Equal variance assumption violated - using Welch's test"
                        }
                else:
                    return {
                        "primary_test": "mann_whitney_u",
                        "test_name": "Mann-Whitney U Test",
                        "reason": "Independent groups, continuous, but not normal with small sample",
                        "confidence": "high",
                        "parameters": {},
                        "alternative_tests": [],
                        "assumptions_met": True
                    }
            else:
                return {
                    "primary_test": "mann_whitney_u",
                    "test_name": "Mann-Whitney U Test",
                    "reason": "Independent groups with ordinal data",
                    "confidence": "high",
                    "parameters": {},
                    "alternative_tests": [],
                    "assumptions_met": True
                }

    def _suggest_multi_sample_test(self, chars: DataCharacteristics) -> Dict:
        """Suggest test for multiple samples"""

        if chars.data_type == 'continuous':
            if chars.is_normal or chars.sample_size_adequate:
                if chars.equal_variances:
                    return {
                        "primary_test": "one_way_anova",
                        "test_name": "One-Way ANOVA",
                        "reason": f"{chars.n_groups} groups, continuous, normal, equal variances",
                        "confidence": "high",
                        "parameters": {},
                        "alternative_tests": ["kruskal_wallis"],
                        "assumptions_met": True,
                        "post_hoc": "Consider Tukey HSD if significant"
                    }
                else:
                    return {
                        "primary_test": "kruskal_wallis",
                        "test_name": "Kruskal-Wallis Test",
                        "reason": f"{chars.n_groups} groups, continuous, but unequal variances",
                        "confidence": "high",
                        "parameters": {},
                        "alternative_tests": [],
                        "assumptions_met": False,
                        "warning": "Equal variance assumption violated - using non-parametric test",
                        "post_hoc": "Consider Dunn's test if significant"
                    }
            else:
                return {
                    "primary_test": "kruskal_wallis",
                    "test_name": "Kruskal-Wallis Test",
                    "reason": f"{chars.n_groups} groups, continuous, not normal with small sample",
                    "confidence": "high",
                    "parameters": {},
                    "alternative_tests": [],
                    "assumptions_met": True,
                    "post_hoc": "Consider Dunn's test if significant"
                }
        else:
            return {
                "primary_test": "kruskal_wallis",
                "test_name": "Kruskal-Wallis Test",
                "reason": f"{chars.n_groups} groups with ordinal data",
                "confidence": "high",
                "parameters": {},
                "alternative_tests": [],
                "assumptions_met": True,
                "post_hoc": "Consider Dunn's test if significant"
            }

    def suggest_normality_test(self, data: np.ndarray) -> Dict:
        """Suggest appropriate normality test"""
        n = len(data)

        if n < 7:
            return {
                "primary_test": None,
                "reason": "Sample size too small for normality testing (n < 7)",
                "recommendation": "Assume non-normal and use non-parametric tests"
            }
        elif n <= 50:
            return {
                "primary_test": "shapiro_wilk",
                "test_name": "Shapiro-Wilk Test",
                "reason": "Most powerful for small to moderate samples (n ≤ 50)",
                "confidence": "high",
                "alternative_tests": ["kolmogorov_smirnov", "anderson_darling"]
            }
        elif n <= 5000:
            return {
                "primary_test": "shapiro_wilk",
                "test_name": "Shapiro-Wilk Test",
                "reason": "Good for moderate samples",
                "confidence": "high",
                "alternative_tests": ["anderson_darling", "jarque_bera"]
            }
        else:
            return {
                "primary_test": "jarque_bera",
                "test_name": "Jarque-Bera Test",
                "reason": "Best for large samples (n > 5000)",
                "confidence": "high",
                "alternative_tests": ["anderson_darling"]
            }

    def suggest_variance_test(self, *data_groups) -> Dict:
        """Suggest appropriate test for variance equality"""
        n_groups = len(data_groups)

        if n_groups < 2:
            return {
                "primary_test": None,
                "reason": "Need at least 2 groups to test variance equality"
            }

        # Check if data is normal
        chars = self.analyze_data(*data_groups)

        if chars.is_normal:
            if n_groups == 2:
                return {
                    "primary_test": "f_test_variance",
                    "test_name": "F-Test for Variance",
                    "reason": "Two normal groups - F-test is most powerful",
                    "confidence": "high",
                    "alternative_tests": ["levene"],
                    "warning": "Sensitive to non-normality - consider Levene's test if normality questionable"
                }
            else:
                return {
                    "primary_test": "bartlett",
                    "test_name": "Bartlett's Test",
                    "reason": f"{n_groups} normal groups - Bartlett's is most powerful",
                    "confidence": "high",
                    "alternative_tests": ["levene"],
                    "warning": "Sensitive to non-normality - consider Levene's test if normality questionable"
                }
        else:
            return {
                "primary_test": "levene",
                "test_name": "Levene's Test",
                "reason": "Data not normal or normality uncertain - Levene's is robust",
                "confidence": "high",
                "alternative_tests": [],
                "parameters": {"center": "median"}
            }
