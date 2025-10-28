# MCP Hypothesis Tester v2.0

A comprehensive statistical hypothesis testing framework with clean OOP architecture, built as a FastMCP server. Features 14+ statistical tests, auto-test suggestion, and intelligent caching system.

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12+-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 What This Does

This MCP server provides a complete statistical hypothesis testing toolkit for LLMs and developers. It analyzes your data, suggests appropriate tests, checks assumptions, and provides business-friendly interpretations.

**Perfect for:**
- 📊 A/B testing and experimentation
- 📈 Sales and business analytics
- 🔬 Scientific research and analysis
- 🎓 Learning statistics with real examples
- 🤖 LLM-powered data analysis

---

## ✨ Key Features

### 🧪 14+ Statistical Tests
- **Parametric:** t-tests (one-sample, two-sample, paired), ANOVA
- **Non-parametric:** Mann-Whitney U, Wilcoxon, Kruskal-Wallis
- **Normality:** Shapiro-Wilk, Kolmogorov-Smirnov, Anderson-Darling, Jarque-Bera
- **Variance:** Levene's, Bartlett's, F-test

### 🤖 Smart Auto-Suggestion
Analyzes your data characteristics and recommends the most appropriate test:
- Checks normality, variance equality, sample sizes
- Considers data type (continuous, ordinal)
- Provides reasoning and alternatives

### 💾 Intelligent Caching
- Stores detailed results in temp JSON files
- Keeps MCP responses lightweight (<5KB)
- 24-hour TTL with auto-cleanup
- Retrieve full details when needed

### 📚 Real-World Examples
6 datasets from documentation with exact statistics:
- **Sales example** (reject H₀, p=0.042)
- **Coffee shop traffic** (fail to reject, p=0.08)
- **Website redesign** (paired test, p=0.02)
- **Coffee machine ratings** (two-sample)
- **Three stores** (ANOVA)
- **Normality test** (assumption checking)

### 🎓 Business-Friendly Interpretations
Every result includes:
- Clear decision (reject/fail to reject H₀)
- Plain-English interpretation
- Effect sizes (Cohen's d, eta-squared)
- Actionable recommendations
- Assumption checks and warnings

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-hypothesis-tester.git
cd mcp-hypothesis-tester

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate example datasets
python generate_datasets.py

# Test the implementation
python test_implementation.py
```

### Running the Server

```bash
# Start MCP server
python -m src.mcp_server

# Or use FastMCP CLI
fastmcp run
```

---

## 📖 Usage Examples

### Example 1: Sales Analysis (One-Sample T-Test)

**Question:** "Has daily sales changed from our $5,000 baseline?"

```python
# Step 1: Auto-suggest appropriate test
result = suggest_test(
    dataset_name="sales_example",
    test_params={"mu0": 5000}
)
# Suggests: one_sample_t_test

# Step 2: Run the test
result = run_hypothesis_test(
    test_type="one_sample_t_test",
    dataset_name="sales_example",
    alpha=0.05,
    test_params={"mu0": 5000}
)

# Result:
{
  "summary": {
    "decision": "reject",
    "p_value": 0.0441,
    "significant": true,
    "interpretation": "The sample mean (5150.00) is statistically
                      significantly different from the hypothesized
                      value (5000). This represents a 3.0% change.",
    "effect_size": 0.309,
    "recommendation": "Evidence suggests a significant effect.
                      Investigate what drove this improvement!"
  },
  "cache_id": "abc123...",
  "note": "Full details cached. Use get_cached_result() to retrieve."
}
```

**Business Conclusion:** Sales genuinely increased to $5,150 from $5,000 baseline (p=0.044 < 0.05). This is NOT random luck—something real happened! 📈

---

### Example 2: Website Redesign (Paired T-Test)

**Question:** "Did website redesign change visit duration?"

```python
# Auto-suggest recognizes paired data
result = suggest_test("website_redesign")
# Suggests: paired_t_test (before/after comparison)

# Run test
result = run_hypothesis_test(
    test_type="paired_t_test",
    dataset_name="website_redesign"
)

# If significant:
# "Visit time increased from 5.0 to 5.5 minutes (p=0.02).
#  Analyze WHERE users spend extra time:
#  - Product pages? GOOD (considering purchases)
#  - Help pages? BAD (confused, frustrated)"
```

---

### Example 3: Smart Workflow

```python
# 1. List available datasets
datasets = list_available_datasets()

# 2. Get test suggestion
suggestion = suggest_test("sales_example", {"mu0": 5000})
print(f"Recommended: {suggestion['test_name']}")
print(f"Reason: {suggestion['reason']}")

# 3. Check assumptions
assumptions = check_assumptions("sales_example", "one_sample_t_test")
if not assumptions['all_met']:
    print(f"Warnings: {assumptions['violations']}")
    print(f"Recommendation: {assumptions['recommendation']}")

# 4. Run test
result = run_hypothesis_test(
    suggestion['primary_test'],
    "sales_example",
    test_params=suggestion['parameters']
)

# 5. Get full details if needed
full_result = get_cached_result(result['cache_id'])
```

---

## 🛠️ Available MCP Tools

### 1. `run_hypothesis_test()`
Run statistical test on dataset. Returns lightweight summary with cache reference.

**Parameters:**
- `test_type` - Type of test (e.g., "one_sample_t_test")
- `dataset_name` - Dataset file name (e.g., "sales_example")
- `alpha` - Significance level (default: 0.05)
- `test_params` - Additional parameters (e.g., {"mu0": 5000})

**Returns:** Summary with p-value, decision, interpretation, effect size, cache_id

---

### 2. `suggest_test()`
Auto-suggest appropriate test based on data characteristics.

**Parameters:**
- `dataset_name` - Dataset to analyze
- `test_params` - Optional parameters

**Returns:** Recommended test with reasoning, confidence, alternatives

---

### 3. `check_assumptions()`
Verify dataset meets test assumptions.

**Parameters:**
- `dataset_name` - Dataset to check
- `test_type` - Test to validate for

**Returns:** Assumption checks, violations, recommendations

---

### 4. `get_cached_result()`
Retrieve full test result from cache.

**Parameters:**
- `cache_id` - Cache identifier from test result
- `include_raw_data` - Whether to include raw data (default: false)

**Returns:** Complete test analysis with all details

---

### 5. `list_available_datasets()`
List all datasets with metadata.

**Returns:** Dataset names, descriptions, recommended tests, case references

---

### 6. `list_available_tests()`
List all statistical tests by category.

**Returns:** Tests organized by parametric, non-parametric, normality, variance

---

## 📊 Implemented Statistical Tests

### Parametric Tests
| Test | Use Case | Example |
|------|----------|---------|
| **One-Sample T-Test** | Compare mean to known value | Sales: $5,150 vs $5,000 |
| **Two-Sample T-Test** | Compare two independent groups | Old vs new machine |
| **Paired T-Test** | Compare paired observations | Before/after redesign |
| **One-Way ANOVA** | Compare 3+ groups | Sales across stores |

### Non-Parametric Tests
| Test | Use Case | Example |
|------|----------|---------|
| **Mann-Whitney U** | Two groups, non-normal | Satisfaction ratings |
| **Wilcoxon Signed-Rank** | Paired, non-normal | Pain before/after |
| **Kruskal-Wallis** | 3+ groups, non-normal | Job satisfaction |

### Normality Tests
| Test | Best For | Sample Size |
|------|----------|-------------|
| **Shapiro-Wilk** | Most powerful | n ≤ 50 |
| **Kolmogorov-Smirnov** | General distribution | Any |
| **Anderson-Darling** | Tail sensitivity | n ≥ 7 |
| **Jarque-Bera** | Large samples | n > 2000 |

### Variance Tests
| Test | Use Case | Notes |
|------|----------|-------|
| **Levene's** | Equal variance check | Robust to non-normality |
| **Bartlett's** | Equal variance check | Best for normal data |
| **F-Test** | Two-sample variance | Sensitive to non-normality |

---

## 📁 Project Structure

```
mcp-hypothesis-tester/
├── datasets/                    # 6 documentation-aligned datasets
│   ├── sales_example.json      # Case 1: One-sample t-test
│   ├── coffee_shop_traffic.json # Case 2: Fail to reject
│   ├── website_redesign.json   # Case 3: Paired t-test
│   ├── coffee_machine_ratings.json
│   ├── sales_three_stores.json # ANOVA example
│   └── normality_test_example.json
│
├── src/                         # Source code
│   ├── core/
│   │   ├── base_test.py        # Abstract base class
│   │   └── cache_manager.py    # Temp JSON caching
│   ├── tests/
│   │   ├── parametric/         # T-tests, ANOVA
│   │   ├── non_parametric/     # Mann-Whitney, Wilcoxon, etc.
│   │   ├── normality/          # Shapiro-Wilk, K-S, etc.
│   │   └── variance/           # Levene's, Bartlett's, F-test
│   ├── datasets/
│   │   └── loader.py           # Dataset management
│   ├── utils/
│   │   └── test_suggester.py  # Auto test suggestion
│   └── mcp_server.py           # FastMCP integration
│
├── Documentation/
│   ├── README.md               # This file
│   ├── USAGE_GUIDE.md          # Comprehensive usage guide
│   ├── IMPLEMENTATION-1.md     # Implementation plan
│   ├── IMPLEMENTATION_COMPLETE.md
│   ├── PROJECT_STRUCTURE.md    # Detailed structure
│   ├── LLM_USAGE_GUIDE.md      # For LLM users
│   ├── hypothesis-tester-for-megginners.md
│   └── sample-cases-and-explanation.md
│
├── Scripts/
│   ├── generate_datasets.py    # Generate example datasets
│   └── test_implementation.py  # Test suite
│
└── Configuration/
    ├── fastmcp.json
    ├── requirements.txt
    └── pyproject.toml
```

---

## 🏗️ Architecture

### Clean OOP Design
- **Template Method Pattern** - Base class defines workflow
- **Dependency Injection** - Cache manager injected into tests
- **Open-Closed Principle** - Easy to extend with new tests
- **Single Responsibility** - Each class handles one test type

### Core Components

**BaseHypothesisTest** (Abstract Base Class)
```python
class BaseHypothesisTest(ABC):
    def run(self, *args):
        # 1. Validate input
        # 2. Check assumptions
        # 3. Compute statistic
        # 4. Calculate effect size
        # 5. Interpret result
        # 6. Cache details
        # 7. Return TestResult
```

**TestResult** (Standardized Container)
```python
@dataclass
class TestResult:
    test_name: str
    statistic: float
    p_value: float
    decision: str
    interpretation: str
    effect_size: float
    assumptions_met: Dict[str, bool]
    cache_id: str
```

**CacheManager** (Temp JSON Storage)
- Location: `/tmp/mcp-hypothesis-cache/`
- TTL: 24 hours with auto-cleanup
- Serializes numpy arrays automatically

**TestSuggester** (Smart Recommendation)
- Analyzes: normality, variance, sample size, data type
- Decision tree logic for test selection
- Returns: test name, reasoning, confidence, alternatives

---

## 📚 Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete usage examples and workflows
- **[IMPLEMENTATION-1.md](IMPLEMENTATION-1.md)** - Original implementation plan
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Completion summary
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project structure
- **[hypothesis-tester-for-megginners.md](hypothesis-tester-for-megginners.md)** - Beginner-friendly explanations
- **[sample-cases-and-explanation.md](sample-cases-and-explanation.md)** - Detailed case studies

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_implementation.py
```

**Test Coverage:**
- ✅ Dataset loading (6 datasets)
- ✅ One-sample t-test (Sales: t=2.073, p=0.044 → Reject H₀)
- ✅ Paired t-test (Website redesign)
- ✅ Shapiro-Wilk normality test
- ✅ Auto test suggestion
- ✅ Cache manager

**Result:** ALL TESTS PASSED ✅

---

## 🎓 Learning Resources

### Understanding P-Values
- **p < 0.01** - Very strong evidence (highly significant)
- **0.01 ≤ p < 0.05** - Strong evidence (significant)
- **0.05 ≤ p < 0.10** - Weak evidence (marginally significant)
- **p ≥ 0.10** - Insufficient evidence (not significant)

### Effect Size Interpretation (Cohen's d)
- **|d| < 0.2** - Negligible
- **0.2 ≤ |d| < 0.5** - Small
- **0.5 ≤ |d| < 0.8** - Medium
- **|d| ≥ 0.8** - Large

### Decision Rules
- **p < α (0.05)** → Reject H₀ (effect is real)
- **p ≥ α (0.05)** → Fail to reject H₀ (insufficient evidence)

⚠️ **Important:** Statistical significance ≠ Practical significance!

---

## 🔧 Dependencies

```
fastmcp >= 2.12.0      # MCP server framework
numpy >= 1.24.0        # Array operations
scipy >= 1.10.0        # Statistical tests
pandas >= 2.0.0        # Data handling
matplotlib >= 3.7.0    # Plotting (optional)
seaborn >= 0.12.0      # Visualization (optional)
statsmodels >= 0.14.0  # Advanced statistics
```

---

## 📈 Performance

- **Response Time:** <100ms for most tests
- **Cache Size:** <1MB for typical usage
- **MCP Response:** <5KB (summary only)
- **Memory:** ~50MB runtime
- **Startup Time:** <2 seconds

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

1. **Additional Tests:**
   - Two-way ANOVA
   - Chi-square (goodness of fit, independence)
   - Correlation tests (Pearson, Spearman, Kendall)
   - Z-tests for proportions

2. **Post-Hoc Tests:**
   - Tukey HSD
   - Bonferroni correction
   - Dunn's test

3. **Power Analysis:**
   - Sample size calculations
   - Statistical power estimation

4. **Visualization:**
   - Q-Q plots for normality
   - Box plots for comparisons
   - Distribution histograms

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Statistical tests from [SciPy](https://scipy.org/)
- Inspired by real-world business analytics needs
- Documentation examples from statistics education resources

---

## 📞 Support

- **Documentation:** See `USAGE_GUIDE.md` for detailed examples
- **Issues:** Open an issue on GitHub
- **Questions:** Check `hypothesis-tester-for-megginners.md` for explanations

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ for data-driven decision making**

*Version 2.0 - Complete rewrite with clean OOP architecture*
