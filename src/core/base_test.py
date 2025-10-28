"""
Base classes for hypothesis testing framework.
Provides abstract base class and standardized result container.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum


class TestType(Enum):
    """Enumeration of all supported statistical tests"""
    # Parametric Tests
    ONE_SAMPLE_T_TEST = "one_sample_t_test"
    TWO_SAMPLE_T_TEST = "two_sample_t_test"
    PAIRED_T_TEST = "paired_t_test"
    ONE_WAY_ANOVA = "one_way_anova"
    Z_TEST_MEAN = "z_test_mean"
    Z_TEST_PROPORTION = "z_test_proportion"
    PEARSON_CORRELATION = "pearson_correlation"

    # Non-Parametric Tests
    MANN_WHITNEY_U = "mann_whitney_u"
    WILCOXON_SIGNED_RANK = "wilcoxon_signed_rank"
    KRUSKAL_WALLIS = "kruskal_wallis"
    FRIEDMAN = "friedman"
    CHI_SQUARE_GOODNESS = "chi_square_goodness"
    CHI_SQUARE_INDEPENDENCE = "chi_square_independence"
    SIGN_TEST = "sign_test"
    SPEARMAN_CORRELATION = "spearman_correlation"
    KENDALL_TAU = "kendall_tau"

    # Normality Tests
    SHAPIRO_WILK = "shapiro_wilk"
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    ANDERSON_DARLING = "anderson_darling"
    JARQUE_BERA = "jarque_bera"

    # Variance Tests
    LEVENE = "levene"
    BARTLETT = "bartlett"
    F_TEST_VARIANCE = "f_test_variance"


@dataclass
class TestResult:
    """Standardized container for test results"""
    test_name: str
    test_type: str  # TestType enum value
    statistic: float
    p_value: float
    alpha: float
    significant: bool

    # Hypothesis information
    null_hypothesis: str
    alternative_hypothesis: str
    decision: str  # "reject" or "fail_to_reject"

    # Business interpretation
    interpretation: str
    recommendation: str

    # Additional statistics
    effect_size: Optional[float] = None
    confidence_interval: Optional[tuple] = None
    power: Optional[float] = None

    # Metadata
    sample_sizes: Optional[Dict[str, int]] = None
    assumptions_met: Optional[Dict[str, bool]] = None
    warnings: Optional[List[str]] = None

    # Cache reference
    cache_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "test_name": self.test_name,
            "test_type": self.test_type,
            "statistics": {
                "test_statistic": self.statistic,
                "p_value": self.p_value,
                "alpha": self.alpha,
                "effect_size": self.effect_size,
                "confidence_interval": list(self.confidence_interval) if self.confidence_interval else None,
                "power": self.power
            },
            "hypothesis": {
                "null": self.null_hypothesis,
                "alternative": self.alternative_hypothesis,
                "decision": self.decision,
                "significant": self.significant
            },
            "interpretation": {
                "summary": self.interpretation,
                "recommendation": self.recommendation
            },
            "metadata": {
                "sample_sizes": self.sample_sizes,
                "assumptions_met": self.assumptions_met,
                "warnings": self.warnings or []
            },
            "cache_id": self.cache_id
        }


class BaseHypothesisTest(ABC):
    """Abstract base class for all hypothesis tests using Template Method pattern"""

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.cache_manager = None  # Injected by factory

    @abstractmethod
    def test_type(self) -> TestType:
        """Return the test type"""
        pass

    @abstractmethod
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate input data meets test requirements"""
        pass

    @abstractmethod
    def check_assumptions(self, *args, **kwargs) -> Dict[str, bool]:
        """Check if test assumptions are met"""
        pass

    @abstractmethod
    def compute_statistic(self, *args, **kwargs) -> tuple:
        """
        Compute test statistic and p-value
        Returns: (statistic, p_value)
        """
        pass

    @abstractmethod
    def interpret_result(self, statistic: float, p_value: float, **kwargs) -> str:
        """Generate human-readable interpretation"""
        pass

    @abstractmethod
    def get_null_hypothesis(self, **kwargs) -> str:
        """Return null hypothesis statement"""
        pass

    @abstractmethod
    def get_alternative_hypothesis(self, **kwargs) -> str:
        """Return alternative hypothesis statement"""
        pass

    def run(self, *args, **kwargs) -> TestResult:
        """
        Main execution method - Template Method pattern
        Orchestrates the entire test workflow
        """
        # 1. Validate input
        if not self.validate_input(*args, **kwargs):
            raise ValueError(f"Input validation failed for {self.test_type().value}")

        # 2. Check assumptions
        assumptions = self.check_assumptions(*args, **kwargs)
        warnings = [k for k, v in assumptions.items() if not v]

        # 3. Compute test statistic
        statistic, p_value = self.compute_statistic(*args, **kwargs)

        # 4. Make decision
        significant = p_value < self.alpha
        decision = "reject" if significant else "fail_to_reject"

        # 5. Interpret result
        interpretation = self.interpret_result(statistic, p_value, *args, **kwargs)
        recommendation = self.generate_recommendation(decision, assumptions, **kwargs)

        # 6. Calculate effect size (if applicable)
        effect_size = self.calculate_effect_size(*args, **kwargs)

        # 7. Calculate confidence interval (if applicable)
        ci = self.calculate_confidence_interval(*args, **kwargs)

        # 8. Cache detailed results
        cache_id = self.cache_detailed_results(*args, **kwargs,
                                               statistic=statistic,
                                               p_value=p_value)

        # 9. Create result object
        return TestResult(
            test_name=self.get_test_name(),
            test_type=self.test_type().value,
            statistic=statistic,
            p_value=p_value,
            alpha=self.alpha,
            significant=significant,
            null_hypothesis=self.get_null_hypothesis(**kwargs),
            alternative_hypothesis=self.get_alternative_hypothesis(**kwargs),
            decision=decision,
            interpretation=interpretation,
            recommendation=recommendation,
            effect_size=effect_size,
            confidence_interval=ci,
            sample_sizes=self.get_sample_sizes(*args, **kwargs),
            assumptions_met=assumptions,
            warnings=warnings if warnings else None,
            cache_id=cache_id
        )

    def get_test_name(self) -> str:
        """Get human-readable test name"""
        return self.test_type().value.replace('_', ' ').title()

    def calculate_effect_size(self, *args, **kwargs) -> Optional[float]:
        """Calculate effect size (override in subclasses if applicable)"""
        return None

    def calculate_confidence_interval(self, *args, **kwargs) -> Optional[tuple]:
        """Calculate confidence interval (override in subclasses if applicable)"""
        return None

    def generate_recommendation(self, decision: str, assumptions: Dict[str, bool], **kwargs) -> str:
        """Generate actionable recommendation"""
        unmet_assumptions = [k for k, v in assumptions.items() if not v]

        if unmet_assumptions:
            warning = f" WARNING: Assumptions not met: {', '.join(unmet_assumptions)}. Consider non-parametric alternatives."
        else:
            warning = ""

        if decision == "reject":
            return f"Evidence suggests a significant effect. Consider practical significance and collect more data to confirm.{warning}"
        else:
            return f"Insufficient evidence to conclude an effect. Consider increasing sample size or effect size.{warning}"

    def get_sample_sizes(self, *args, **kwargs) -> Optional[Dict[str, int]]:
        """Get sample sizes (override in subclasses)"""
        return None

    def cache_detailed_results(self, *args, **kwargs) -> Optional[str]:
        """Cache detailed results to temp JSON (override if needed)"""
        if self.cache_manager:
            return self.cache_manager.cache_result(self.test_type().value, kwargs)
        return None
