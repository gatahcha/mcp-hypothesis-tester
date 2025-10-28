"""
Normality tests: Shapiro-Wilk, Kolmogorov-Smirnov, Anderson-Darling, Jarque-Bera
"""

from typing import Dict, Optional
import numpy as np
from scipy import stats

from src.core.base_test import BaseHypothesisTest, TestType


class ShapiroWilkTest(BaseHypothesisTest):
    """
    Shapiro-Wilk test: Tests if data comes from a normal distribution.

    Use cases:
    - Check assumption for parametric tests (t-test, ANOVA)
    - Quality control: Ensure measurements are normally distributed
    - Pre-analysis validation

    Null hypothesis: Data is normally distributed

    Example:
        Sales data: Test if daily sales follow normal distribution
        If p > 0.05: Normal (can use t-test)
        If p < 0.05: Not normal (use non-parametric tests)
    """

    def __init__(self, alpha: float = 0.05):
        super().__init__(alpha)

    def test_type(self) -> TestType:
        return TestType.SHAPIRO_WILK

    def validate_input(self, data: np.ndarray) -> bool:
        return len(data) >= 3 and len(data) <= 5000 and not np.any(np.isnan(data))

    def check_assumptions(self, data: np.ndarray) -> Dict[str, bool]:
        return {
            "sufficient_sample_size": 3 <= len(data) <= 5000,
            "no_missing_values": not np.any(np.isnan(data))
        }

    def compute_statistic(self, data: np.ndarray) -> tuple:
        statistic, p_value = stats.shapiro(data)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: Data follows a normal distribution"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return "H₁: Data does not follow a normal distribution"

    def interpret_result(self, statistic: float, p_value: float, data: np.ndarray = None, **kwargs) -> str:
        if p_value < self.alpha:
            return (f"Data is NOT normally distributed (W={statistic:.4f}, p={p_value:.4f}). "
                   f"With p < α={self.alpha}, we reject H₀. "
                   f"Consider using non-parametric tests (Mann-Whitney, Kruskal-Wallis).")
        else:
            return (f"Data appears normally distributed (W={statistic:.4f}, p={p_value:.4f}). "
                   f"With p ≥ α={self.alpha}, we fail to reject H₀. "
                   f"Safe to use parametric tests (t-test, ANOVA).")

    def get_sample_sizes(self, data: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"n": len(data)}

    def generate_recommendation(self, decision: str, assumptions: Dict[str, bool], **kwargs) -> str:
        if decision == "reject":
            return ("Data violates normality assumption. Recommendations: "
                   "(1) Use non-parametric alternatives, "
                   "(2) Transform data (log, sqrt), "
                   "(3) Increase sample size (n > 30) for CLT to apply.")
        else:
            return "Data meets normality assumption. Parametric tests are appropriate."


class KolmogorovSmirnovTest(BaseHypothesisTest):
    """
    Kolmogorov-Smirnov test: Tests if data comes from a specific distribution.

    Use cases:
    - Compare sample to theoretical distribution (normal, uniform, etc.)
    - More general than Shapiro-Wilk
    - Works with larger samples

    Example:
        Test if sales follow normal distribution with known parameters
    """

    def __init__(self, alpha: float = 0.05, distribution: str = 'norm'):
        super().__init__(alpha)
        self.distribution = distribution

    def test_type(self) -> TestType:
        return TestType.KOLMOGOROV_SMIRNOV

    def validate_input(self, data: np.ndarray) -> bool:
        return len(data) >= 5 and not np.any(np.isnan(data))

    def check_assumptions(self, data: np.ndarray) -> Dict[str, bool]:
        return {
            "sufficient_sample_size": len(data) >= 5,
            "continuous_data": True
        }

    def compute_statistic(self, data: np.ndarray) -> tuple:
        """Test against specified distribution"""
        if self.distribution == 'norm':
            # Standardize data
            mean, std = np.mean(data), np.std(data, ddof=1)
            standardized = (data - mean) / std
            statistic, p_value = stats.kstest(standardized, 'norm')
        else:
            statistic, p_value = stats.kstest(data, self.distribution)

        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return f"H₀: Data follows a {self.distribution} distribution"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return f"H₁: Data does not follow a {self.distribution} distribution"

    def interpret_result(self, statistic: float, p_value: float, data: np.ndarray = None, **kwargs) -> str:
        if p_value < self.alpha:
            return (f"Data does NOT follow {self.distribution} distribution (D={statistic:.4f}, p={p_value:.4f}). "
                   f"With p < α={self.alpha}, we reject H₀.")
        else:
            return (f"Data appears to follow {self.distribution} distribution (D={statistic:.4f}, p={p_value:.4f}). "
                   f"With p ≥ α={self.alpha}, we fail to reject H₀.")

    def get_sample_sizes(self, data: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"n": len(data)}


class AndersonDarlingTest(BaseHypothesisTest):
    """
    Anderson-Darling test: Tests if data comes from a specific distribution.
    More sensitive to tails than Kolmogorov-Smirnov.

    Use cases:
    - Detect deviations in distribution tails
    - Quality control applications
    - More powerful than K-S test
    """

    def __init__(self, alpha: float = 0.05, distribution: str = 'norm'):
        super().__init__(alpha)
        self.distribution = distribution

    def test_type(self) -> TestType:
        return TestType.ANDERSON_DARLING

    def validate_input(self, data: np.ndarray) -> bool:
        return len(data) >= 7 and not np.any(np.isnan(data))

    def check_assumptions(self, data: np.ndarray) -> Dict[str, bool]:
        return {
            "sufficient_sample_size": len(data) >= 7,
            "continuous_data": True
        }

    def compute_statistic(self, data: np.ndarray) -> tuple:
        """Compute Anderson-Darling statistic"""
        result = stats.anderson(data, dist=self.distribution)
        statistic = result.statistic

        # Find p-value based on critical values
        # Anderson-Darling provides critical values at specific significance levels
        critical_values = result.critical_values
        significance_levels = result.significance_level

        # Estimate p-value
        if statistic < critical_values[0]:
            p_value = 0.15  # Greater than 15%
        elif statistic < critical_values[1]:
            p_value = 0.10  # Between 10-15%
        elif statistic < critical_values[2]:
            p_value = 0.05  # Between 5-10%
        elif statistic < critical_values[3]:
            p_value = 0.025  # Between 2.5-5%
        elif statistic < critical_values[4]:
            p_value = 0.01  # Between 1-2.5%
        else:
            p_value = 0.005  # Less than 1%

        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return f"H₀: Data follows a {self.distribution} distribution"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return f"H₁: Data does not follow a {self.distribution} distribution"

    def interpret_result(self, statistic: float, p_value: float, data: np.ndarray = None, **kwargs) -> str:
        if p_value < self.alpha:
            return (f"Data does NOT follow {self.distribution} distribution (A²={statistic:.4f}, p≈{p_value:.4f}). "
                   f"With p < α={self.alpha}, we reject H₀. "
                   f"Particularly sensitive to tail deviations.")
        else:
            return (f"Data appears to follow {self.distribution} distribution (A²={statistic:.4f}, p≈{p_value:.4f}). "
                   f"With p ≥ α={self.alpha}, we fail to reject H₀.")

    def get_sample_sizes(self, data: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"n": len(data)}


class JarqueBeraTest(BaseHypothesisTest):
    """
    Jarque-Bera test: Tests normality based on skewness and kurtosis.

    Use cases:
    - Financial data analysis
    - Large sample sizes (n > 2000)
    - Tests both skewness and kurtosis simultaneously

    Good for: Detecting departures from normality in shape
    """

    def __init__(self, alpha: float = 0.05):
        super().__init__(alpha)

    def test_type(self) -> TestType:
        return TestType.JARQUE_BERA

    def validate_input(self, data: np.ndarray) -> bool:
        return len(data) >= 7 and not np.any(np.isnan(data))

    def check_assumptions(self, data: np.ndarray) -> Dict[str, bool]:
        return {
            "sufficient_sample_size": len(data) >= 7,
            "works_best_large_n": len(data) > 2000
        }

    def compute_statistic(self, data: np.ndarray) -> tuple:
        statistic, p_value = stats.jarque_bera(data)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: Data has normal skewness and kurtosis (follows normal distribution)"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return "H₁: Data has non-normal skewness or kurtosis"

    def interpret_result(self, statistic: float, p_value: float, data: np.ndarray = None, **kwargs) -> str:
        if data is not None:
            skewness = stats.skew(data)
            kurtosis = stats.kurtosis(data)

            if p_value < self.alpha:
                return (f"Data is NOT normally distributed (JB={statistic:.4f}, p={p_value:.4f}). "
                       f"Skewness={skewness:.3f}, Excess Kurtosis={kurtosis:.3f}. "
                       f"With p < α={self.alpha}, we reject H₀.")
            else:
                return (f"Data appears normally distributed (JB={statistic:.4f}, p={p_value:.4f}). "
                       f"Skewness={skewness:.3f}, Excess Kurtosis={kurtosis:.3f}. "
                       f"With p ≥ α={self.alpha}, we fail to reject H₀.")
        return "Insufficient data"

    def get_sample_sizes(self, data: np.ndarray, **kwargs) -> Dict[str, int]:
        return {"n": len(data)}
