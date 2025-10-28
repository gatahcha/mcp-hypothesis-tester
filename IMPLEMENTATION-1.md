# IMPLEMENTATION-1: Hypothesis Testing Framework Redesign

## Executive Summary

This document outlines a complete redesign of the MCP Hypothesis Tester to implement all 26+ hypothesis tests from the Python statistical documentation using a clean OOP architecture. The redesign focuses on:

1. **Clean OOP abstraction** for extensibility and maintainability
2. **Complete implementation of all statistical tests** with examples
3. **Temp JSON caching mechanism** to avoid passing large data through MCP
4. **Dataset structure aligned with documentation examples** (sales, coffee shop, website, etc.)

---

## 1. Method Abstraction & OOP Design

### 1.1 Core Architecture

```
src/
├── core/
│   ├── __init__.py
│   ├── base_test.py           # Abstract base class for all tests
│   ├── test_result.py         # Standardized result container
│   └── cache_manager.py       # Temp JSON cache management
├── tests/
│   ├── __init__.py
│   ├── parametric/
│   │   ├── __init__.py
│   │   ├── t_tests.py         # One-sample, two-sample, paired t-tests
│   │   ├── anova.py           # One-way, two-way ANOVA, MANOVA
│   │   ├── z_tests.py         # Z-tests for proportions and means
│   │   └── correlation.py     # Pearson, Spearman correlation tests
│   ├── non_parametric/
│   │   ├── __init__.py
│   │   ├── rank_tests.py      # Mann-Whitney, Wilcoxon, Kruskal-Wallis
│   │   ├── chi_square.py      # Chi-square tests (goodness of fit, independence)
│   │   └── sign_tests.py      # Sign test, runs test
│   ├── normality/
│   │   ├── __init__.py
│   │   └── normality_tests.py # Shapiro-Wilk, Kolmogorov-Smirnov, Anderson-Darling
│   └── variance/
│       ├── __init__.py
│       └── variance_tests.py  # Levene's, Bartlett's, F-test
├── datasets/
│   └── loader.py              # Dataset loading and validation
├── utils/
│   ├── __init__.py
│   ├── validators.py          # Input validation
│   └── formatters.py          # Result formatting for LLM consumption
└── mcp_server.py              # FastMCP server integration
```

### 1.2 Base Test Abstract Class

```python
# src/core/base_test.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum

class TestType(Enum):
    """Enumeration of all supported statistical tests"""
    # Parametric Tests
    ONE_SAMPLE_T_TEST = "one_sample_t_test"
    TWO_SAMPLE_T_TEST = "two_sample_t_test"
    PAIRED_T_TEST = "paired_t_test"
    ONE_WAY_ANOVA = "one_way_anova"
    TWO_WAY_ANOVA = "two_way_anova"
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
    RUNS_TEST = "runs_test"
    SPEARMAN_CORRELATION = "spearman_correlation"
    KENDALL_TAU = "kendall_tau"

    # Normality Tests
    SHAPIRO_WILK = "shapiro_wilk"
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    ANDERSON_DARLING = "anderson_darling"
    JARQUE_BERA = "jarque_bera"
    DAGOSTINO_K2 = "dagostino_k2"

    # Variance Tests
    LEVENE = "levene"
    BARTLETT = "bartlett"
    F_TEST_VARIANCE = "f_test_variance"
    FLIGNER_KILLEEN = "fligner_killeen"

@dataclass
class TestResult:
    """Standardized container for test results"""
    test_name: str
    test_type: TestType
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
            "test_type": self.test_type.value,
            "statistics": {
                "test_statistic": self.statistic,
                "p_value": self.p_value,
                "alpha": self.alpha,
                "effect_size": self.effect_size,
                "confidence_interval": self.confidence_interval,
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
    """Abstract base class for all hypothesis tests"""

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
        interpretation = self.interpret_result(statistic, p_value, **kwargs)
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
            test_type=self.test_type(),
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
        if decision == "reject":
            return "Evidence suggests a significant effect. Consider practical significance and collect more data to confirm."
        else:
            return "Insufficient evidence to conclude an effect. Consider increasing sample size or effect size."

    def get_sample_sizes(self, *args, **kwargs) -> Optional[Dict[str, int]]:
        """Get sample sizes (override in subclasses)"""
        return None

    def cache_detailed_results(self, *args, **kwargs) -> Optional[str]:
        """Cache detailed results to temp JSON (override if needed)"""
        if self.cache_manager:
            return self.cache_manager.cache_result(self.test_type().value, kwargs)
        return None
```

---

## 2. Complete Test Implementation Catalog

### 2.1 Parametric Tests

#### 2.1.1 One-Sample T-Test

**Example from documentation (Sales Case):**
- Historical average: $5,000 per day
- Current quarter: $5,150 per day (n=45, SD=$480)
- Test if current sales differ from $5,000

```python
# src/tests/parametric/t_tests.py
from scipy import stats
import numpy as np
from src.core.base_test import BaseHypothesisTest, TestType, TestResult

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
        super().__init__(alpha)
        self.mu0 = mu0  # Hypothesized population mean
        self.alternative = alternative  # 'two-sided', 'less', 'greater'

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
```

#### 2.1.2 Two-Sample T-Test

**Example: Coffee shop comparison (old machine vs new machine)**

```python
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
```

#### 2.1.3 Paired T-Test

**Example: Before-After website redesign**

```python
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
```

### 2.2 Non-Parametric Tests

#### 2.2.1 Mann-Whitney U Test

```python
# src/tests/non_parametric/rank_tests.py
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
        Old: [3, 4, 3, 5, 2, 4] (median=3.5)
        New: [4, 5, 5, 4, 5, 4] (median=4.5)
        Test if medians differ significantly
    """

    def test_type(self) -> TestType:
        return TestType.MANN_WHITNEY_U

    def compute_statistic(self, group1: np.ndarray, group2: np.ndarray) -> tuple:
        statistic, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        return float(statistic), float(p_value)

    # ... (similar structure to t-tests)
```

#### 2.2.2 Wilcoxon Signed-Rank Test

```python
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

    def test_type(self) -> TestType:
        return TestType.WILCOXON_SIGNED_RANK

    def compute_statistic(self, before: np.ndarray, after: np.ndarray) -> tuple:
        statistic, p_value = stats.wilcoxon(before, after, alternative='two-sided')
        return float(statistic), float(p_value)
```

#### 2.2.3 Kruskal-Wallis Test

```python
class KruskalWallisTest(BaseHypothesisTest):
    """
    Kruskal-Wallis H test: Non-parametric alternative to one-way ANOVA.

    Use cases:
    - Compare 3+ independent groups with non-normal data
    - Ordinal outcome variables

    Example:
        Job satisfaction across 3 departments (ordinal 1-5)
        Test if any department differs
    """

    def test_type(self) -> TestType:
        return TestType.KRUSKAL_WALLIS

    def compute_statistic(self, *groups) -> tuple:
        statistic, p_value = stats.kruskal(*groups)
        return float(statistic), float(p_value)
```

### 2.3 Normality Tests

```python
# src/tests/normality/normality_tests.py
class ShapiroWilkTest(BaseHypothesisTest):
    """
    Shapiro-Wilk test: Tests if data comes from a normal distribution.

    Use cases:
    - Check assumption for parametric tests
    - Quality control: Ensure measurements are normally distributed

    Null hypothesis: Data is normally distributed

    Example:
        Sales data: Test if daily sales follow normal distribution
        If p > 0.05: Normal (can use t-test)
        If p < 0.05: Not normal (use non-parametric tests)
    """

    def test_type(self) -> TestType:
        return TestType.SHAPIRO_WILK

    def compute_statistic(self, data: np.ndarray) -> tuple:
        statistic, p_value = stats.shapiro(data)
        return float(statistic), float(p_value)

    def get_null_hypothesis(self, **kwargs) -> str:
        return "H₀: Data follows a normal distribution"

    def get_alternative_hypothesis(self, **kwargs) -> str:
        return "H₁: Data does not follow a normal distribution"
```

### 2.4 Variance Tests

```python
# src/tests/variance/variance_tests.py
class LeveneTest(BaseHypothesisTest):
    """
    Levene's test: Tests equality of variances across groups.

    Use cases:
    - Check assumption for ANOVA and t-tests
    - Quality control: Ensure consistent variability

    Example:
        Sales variability: Compare variance across 3 stores
        If equal variance: Use standard ANOVA
        If unequal variance: Use Welch's ANOVA
    """

    def test_type(self) -> TestType:
        return TestType.LEVENE

    def compute_statistic(self, *groups) -> tuple:
        statistic, p_value = stats.levene(*groups)
        return float(statistic), float(p_value)
```

---

## 3. Temp JSON Cache Mechanism

### 3.1 Cache Manager Design

**Goal:** Store detailed test results in temporary JSON files to avoid passing large data through MCP.

```python
# src/core/cache_manager.py
import json
import os
import tempfile
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from pathlib import Path

class CacheManager:
    """
    Manages temporary JSON cache for detailed test results.

    Why?
    - MCP has message size limits
    - LLMs don't need raw data, just summaries
    - Allows retrieval of detailed results on demand

    Cache structure:
    /tmp/mcp-hypothesis-cache/
        ├── test_results/
        │   ├── {test_id}.json          # Full test results
        │   ├── {test_id}_data.json     # Raw data (if needed)
        │   └── {test_id}_metadata.json # Test metadata
        └── index.json                  # Cache index

    Each cached result includes:
    - Test parameters and results
    - Raw data arrays (optional)
    - Diagnostic plots (as base64 or file paths)
    - Detailed assumptions checks
    - Comprehensive interpretation
    """

    def __init__(self, cache_dir: Optional[str] = None, ttl_hours: int = 24):
        """
        Initialize cache manager.

        Args:
            cache_dir: Custom cache directory (default: system temp)
            ttl_hours: Time-to-live for cache entries (default: 24 hours)
        """
        if cache_dir is None:
            cache_dir = os.path.join(tempfile.gettempdir(), "mcp-hypothesis-cache")

        self.cache_dir = Path(cache_dir)
        self.test_results_dir = self.cache_dir / "test_results"
        self.index_file = self.cache_dir / "index.json"
        self.ttl = timedelta(hours=ttl_hours)

        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.test_results_dir.mkdir(exist_ok=True)

        # Load or create index
        self._load_index()
        self._cleanup_expired()

    def _load_index(self):
        """Load cache index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {"entries": {}, "last_cleanup": None}
            self._save_index()

    def _save_index(self):
        """Save cache index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = datetime.now()
        expired_ids = []

        for test_id, entry in self.index["entries"].items():
            created = datetime.fromisoformat(entry["created"])
            if current_time - created > self.ttl:
                expired_ids.append(test_id)

        for test_id in expired_ids:
            self.delete_result(test_id)

        self.index["last_cleanup"] = current_time.isoformat()
        self._save_index()

    def generate_test_id(self, test_type: str, params: Dict) -> str:
        """Generate unique test ID based on type and parameters"""
        # Hash test type + timestamp for uniqueness
        hash_input = f"{test_type}_{datetime.now().isoformat()}_{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def cache_result(self, test_type: str, test_result: Dict[str, Any],
                    raw_data: Optional[Dict] = None) -> str:
        """
        Cache test result with optional raw data.

        Args:
            test_type: Type of test
            test_result: Test result dictionary
            raw_data: Optional raw data arrays

        Returns:
            test_id: Unique identifier for cached result
        """
        test_id = self.generate_test_id(test_type, test_result)

        # Save main result
        result_file = self.test_results_dir / f"{test_id}.json"
        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)

        # Save raw data separately if provided
        if raw_data:
            data_file = self.test_results_dir / f"{test_id}_data.json"
            with open(data_file, 'w') as f:
                json.dump(raw_data, f, indent=2)

        # Update index
        self.index["entries"][test_id] = {
            "test_type": test_type,
            "created": datetime.now().isoformat(),
            "has_raw_data": raw_data is not None,
            "result_file": str(result_file),
            "data_file": str(data_file) if raw_data else None
        }
        self._save_index()

        return test_id

    def get_result(self, test_id: str, include_raw_data: bool = False) -> Optional[Dict]:
        """
        Retrieve cached result.

        Args:
            test_id: Test identifier
            include_raw_data: Whether to include raw data

        Returns:
            Cached result dictionary or None if not found
        """
        if test_id not in self.index["entries"]:
            return None

        entry = self.index["entries"][test_id]

        # Load main result
        result_file = Path(entry["result_file"])
        if not result_file.exists():
            return None

        with open(result_file, 'r') as f:
            result = json.load(f)

        # Load raw data if requested
        if include_raw_data and entry["has_raw_data"]:
            data_file = Path(entry["data_file"])
            if data_file.exists():
                with open(data_file, 'r') as f:
                    result["raw_data"] = json.load(f)

        return result

    def delete_result(self, test_id: str):
        """Delete cached result"""
        if test_id not in self.index["entries"]:
            return

        entry = self.index["entries"][test_id]

        # Delete files
        result_file = Path(entry["result_file"])
        if result_file.exists():
            result_file.unlink()

        if entry["has_raw_data"]:
            data_file = Path(entry["data_file"])
            if data_file.exists():
                data_file.unlink()

        # Remove from index
        del self.index["entries"][test_id]
        self._save_index()

    def list_cached_tests(self) -> List[Dict]:
        """List all cached tests with metadata"""
        tests = []
        for test_id, entry in self.index["entries"].items():
            tests.append({
                "test_id": test_id,
                "test_type": entry["test_type"],
                "created": entry["created"],
                "has_raw_data": entry["has_raw_data"]
            })
        return sorted(tests, key=lambda x: x["created"], reverse=True)
```

### 3.2 MCP Integration

```python
# src/mcp_server.py
from fastmcp import FastMCP
from src.core.cache_manager import CacheManager
from src.tests.parametric.t_tests import OneSampleTTest

mcp = FastMCP("MCP Hypothesis Tester v2")
cache = CacheManager()

@mcp.tool()
def run_hypothesis_test(test_type: str, dataset_name: str,
                       test_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run hypothesis test on dataset.

    Returns:
        Lightweight summary (NOT full data) with cache reference
    """
    # Load dataset
    data = load_dataset(dataset_name)

    # Create test instance
    if test_type == "one_sample_t_test":
        test = OneSampleTTest(
            alpha=test_params.get("alpha", 0.05),
            mu0=test_params.get("mu0", 0)
        )
        test.cache_manager = cache
        result = test.run(data)

    # Cache full result
    cache_id = cache.cache_result(
        test_type=test_type,
        test_result=result.to_dict(),
        raw_data={"data": data.tolist()}  # Optional
    )

    # Return LIGHTWEIGHT summary for LLM
    return {
        "summary": {
            "test_name": result.test_name,
            "decision": result.decision,
            "p_value": result.p_value,
            "significant": result.significant,
            "interpretation": result.interpretation
        },
        "cache_id": cache_id,
        "note": "Full details cached. Use get_cached_result() to retrieve."
    }

@mcp.tool()
def get_cached_result(cache_id: str, include_raw_data: bool = False) -> Dict[str, Any]:
    """Retrieve full cached result when needed"""
    result = cache.get_result(cache_id, include_raw_data)
    if result is None:
        return {"error": "Cache entry not found or expired"}
    return result
```

---

## 4. Dataset Structure & Examples from Documentation

### 4.1 Dataset Schema

All datasets will follow this structure aligned with documentation examples:

```json
{
  "dataset_info": {
    "name": "sales_example",
    "description": "Store daily sales data - testing if current quarter differs from $5,000 baseline",
    "case_reference": "CASE 1: Original Sales Example",
    "test_type_recommended": "one_sample_t_test",
    "business_context": "Store manager wants to know if sales genuinely increased"
  },

  "hypothesis": {
    "null": "H₀: μ = 5000 (sales haven't changed)",
    "alternative": "H₁: μ ≠ 5000 (sales have changed)",
    "alpha": 0.05
  },

  "data": {
    "format": "single_sample",
    "values": [5100, 5200, 4900, ...],  # 45 values
    "expected_mean": 5150,
    "expected_std": 480,
    "sample_size": 45,
    "units": "dollars",
    "mu0": 5000  # Historical baseline
  },

  "expected_result": {
    "t_statistic": 2.096,
    "p_value": 0.042,
    "decision": "reject",
    "interpretation": "Sales genuinely increased from $5,000 to $5,150"
  },

  "business_interpretation": {
    "summary": "Current quarter sales of $5,150 are significantly higher than historical $5,000",
    "recommendation": "Investigate what drove this improvement and maintain practices"
  }
}
```

### 4.2 Dataset Files to Create

Based on documentation examples:

1. **`datasets/sales_example.json`** - CASE 1: Store sales (one-sample t-test)
2. **`datasets/coffee_shop_traffic.json`** - CASE 2: Customer count (fail to reject)
3. **`datasets/website_redesign.json`** - CASE 3: Visit time before/after (paired t-test)
4. **`datasets/coffee_machine_ratings.json`** - Coffee shop example (two-sample t-test)
5. **`datasets/customer_satisfaction_groups.json`** - Multiple groups (ANOVA/Kruskal-Wallis)
6. **`datasets/normality_test_example.json`** - Testing normality assumptions

Example implementation for Sales Case:

```json
// datasets/sales_example.json
{
  "dataset_info": {
    "name": "store_sales_daily",
    "description": "Daily sales for store - testing if Q1 2024 differs from historical $5,000 average",
    "case_reference": "Case 1 from hypothesis-tester-for-megginners.md",
    "business_context": "Store has historical average of $5,000/day. Current quarter shows $5,150/day. Is this real growth or luck?",
    "test_recommended": "one_sample_t_test"
  },

  "hypothesis": {
    "null": "H₀: μ = 5000 (sales haven't changed from baseline)",
    "alternative": "H₁: μ ≠ 5000 (sales have genuinely changed)",
    "alpha": 0.05,
    "test_type": "two-tailed"
  },

  "data": {
    "format": "univariate_continuous",
    "sample_size": 45,
    "units": "USD (dollars)",
    "measurement": "daily_sales",
    "mu0": 5000,
    "values": [
      5150, 5320, 4980, 5210, 5100, 5400, 4850, 5250, 5180, 5050,
      5300, 4920, 5170, 5240, 5080, 5360, 4900, 5190, 5130, 5270,
      5420, 5060, 5200, 4970, 5310, 5140, 5380, 5020, 5230, 5090,
      5160, 5290, 4940, 5220, 5110, 5340, 4880, 5180, 5120, 5260,
      5070, 5200, 4960, 5150, 5100
    ]
  },

  "statistical_properties": {
    "sample_mean": 5150,
    "sample_std": 480,
    "sample_median": 5150,
    "expected_distribution": "approximately_normal"
  },

  "expected_result": {
    "test_statistic": 2.096,
    "p_value": 0.042,
    "decision": "reject_h0",
    "confidence_interval_95": [5007, 5293],
    "cohens_d": 0.31,
    "interpretation": "Sales of $5,150 are statistically significantly different from $5,000 baseline (p=0.042 < 0.05)"
  },

  "business_interpretation": {
    "summary": "Your current quarter sales of $5,150 are significantly higher than the historical $5,000 baseline. This is NOT just random noise—something real happened!",
    "recommendation": [
      "Investigate what caused this improvement (marketing, better service, new customers)",
      "Ensure practices that led to increase are maintained",
      "Update budget forecasts to reflect new higher baseline",
      "Monitor next quarter to confirm trend continues"
    ],
    "confidence": "We are 95% confident this increase is real (only 4.2% chance it's luck)"
  }
}
```

---

## 5. Implementation Workflow

### 5.1 Development Phases

**Phase 1: Core Infrastructure** (Week 1)
- [ ] Implement `BaseHypothesisTest` abstract class
- [ ] Implement `TestResult` dataclass
- [ ] Implement `CacheManager`
- [ ] Set up project structure

**Phase 2: Parametric Tests** (Week 2)
- [ ] One-sample t-test
- [ ] Two-sample t-test (independent)
- [ ] Paired t-test
- [ ] One-way ANOVA
- [ ] Z-tests (mean, proportion)
- [ ] Correlation tests (Pearson, Spearman)

**Phase 3: Non-Parametric Tests** (Week 3)
- [ ] Mann-Whitney U
- [ ] Wilcoxon Signed-Rank
- [ ] Kruskal-Wallis
- [ ] Chi-square (goodness of fit, independence)
- [ ] Sign test, Runs test

**Phase 4: Normality & Variance Tests** (Week 4)
- [ ] Shapiro-Wilk, Kolmogorov-Smirnov
- [ ] Anderson-Darling, Jarque-Bera
- [ ] Levene's, Bartlett's, F-test

**Phase 5: Datasets & Integration** (Week 5)
- [ ] Create all documentation example datasets
- [ ] Integrate with MCP server
- [ ] Add comprehensive docstrings
- [ ] Testing & validation

### 5.2 Usage Example (LLM Perspective)

```python
# LLM calls MCP tool
result = run_hypothesis_test(
    test_type="one_sample_t_test",
    dataset_name="sales_example",
    test_params={"alpha": 0.05, "mu0": 5000}
)

# LLM receives lightweight response:
{
  "summary": {
    "test_name": "One Sample T-Test",
    "decision": "reject",
    "p_value": 0.042,
    "significant": true,
    "interpretation": "Sales of $5,150 are significantly different from $5,000 baseline..."
  },
  "cache_id": "a3f2b9c1d4e5f678",
  "note": "Full details cached. Use get_cached_result() to retrieve."
}

# If LLM needs more details:
full_result = get_cached_result(cache_id="a3f2b9c1d4e5f678")
# Returns complete test results with assumptions, effect sizes, etc.
```

---

## 6. Libraries to Use

### 6.1 Core Libraries (Minimize Code Writing)

```python
# requirements.txt
scipy>=1.11.0        # All statistical tests
numpy>=1.24.0        # Array operations
pandas>=2.0.0        # Data handling (optional)
statsmodels>=0.14.0  # Advanced tests (ANOVA, regression)
pingouin>=0.5.3      # High-level stats API (easier than scipy)

# MCP Integration
fastmcp>=latest

# Utilities
dataclasses          # Built-in (Python 3.7+)
typing               # Built-in
json                 # Built-in
pathlib              # Built-in
```

**Recommendation:** Use `pingouin` library for cleaner API:

```python
import pingouin as pg

# Instead of scipy's complex API:
result = pg.ttest(data, 5000, alternative='two-sided')
# Returns nice DataFrame with effect size, CI, etc.

# ANOVA with post-hoc:
result = pg.anova(data, dv='score', between='group')
posthoc = pg.pairwise_ttests(data, dv='score', between='group')
```

---

## 7. Documentation Example Implementations

### Complete Test Catalog

| Test Name | Python Function | Use Case from Docs | Dataset |
|-----------|----------------|-------------------|---------|
| One-sample t-test | `scipy.stats.ttest_1samp` | Sales: $5,150 vs $5,000 | `sales_example.json` |
| Two-sample t-test | `scipy.stats.ttest_ind` | Coffee machines: old vs new | `coffee_machine_ratings.json` |
| Paired t-test | `scipy.stats.ttest_rel` | Website: before vs after redesign | `website_redesign.json` |
| Mann-Whitney U | `scipy.stats.mannwhitneyu` | Non-normal satisfaction scores | `satisfaction_nonparametric.json` |
| Wilcoxon | `scipy.stats.wilcoxon` | Paired ordinal data | `pain_ratings_paired.json` |
| Kruskal-Wallis | `scipy.stats.kruskal` | 3+ groups, non-normal | `satisfaction_3groups.json` |
| One-way ANOVA | `scipy.stats.f_oneway` | Sales across 3 stores | `sales_3stores.json` |
| Chi-square | `scipy.stats.chisquare` | Category frequencies | `customer_segments.json` |
| Shapiro-Wilk | `scipy.stats.shapiro` | Check normality for t-test | `sales_example.json` |
| Levene's | `scipy.stats.levene` | Check equal variances | `sales_3stores.json` |
| Pearson correlation | `scipy.stats.pearsonr` | Sales vs advertising | `sales_advertising.json` |
| Spearman correlation | `scipy.stats.spearmanr` | Ordinal correlation | `satisfaction_effort.json` |

---

## 8. Key Design Principles

1. **Open-Closed Principle:** Easy to add new tests without modifying existing code
2. **Single Responsibility:** Each test class handles one test type
3. **Dependency Injection:** Cache manager injected into tests
4. **Template Method Pattern:** Base class defines workflow, subclasses implement details
5. **Separation of Concerns:** MCP layer separate from statistical logic
6. **Fail-Safe Caching:** Tests work even if caching fails
7. **Documentation-Driven:** Every test includes real-world examples from documentation

---

## 9. Questions & Uncertainties

### Clarifications Needed:

1. **Dataset Size:** Should we generate exact data matching documentation (e.g., 45 sales values with mean=5150, std=480)?
   - **Recommendation:** Yes, use `numpy.random.normal` with fixed seed for reproducibility

2. **MCP Response Size:** What's the actual size limit?
   - **Recommendation:** Keep responses < 5KB, cache everything else

3. **Test Discovery:** Should LLM auto-discover which test to use?
   - **Recommendation:** Implement `suggest_test()` function based on data characteristics

4. **Visualization:** Should we cache plots too?
   - **Recommendation:** Yes, save as PNG and return file path

5. **Old Datasets:** Can we delete `clinical_trial.json`, `customer_satisfaction.json`, etc.?
   - **Recommendation:** Yes, replace with documentation-aligned datasets

---

## 10. Success Criteria

✅ All 26+ tests from Python docs implemented
✅ Clean OOP architecture with <200 lines per test class
✅ All documentation examples (sales, coffee, website) work
✅ Cache manager reduces MCP response size by >80%
✅ LLM can interpret results without seeing raw data
✅ Comprehensive docstrings with real-world examples
✅ <100 lines of custom statistical code (leverage scipy/pingouin)

---

## End of Implementation Plan

**Next Steps:**
1. Review and approve this plan
2. Set up project structure
3. Begin Phase 1 implementation
4. Iterate based on feedback
