# Project Structure

## Clean Codebase Overview

```
mcp-hypothesis-tester/
├── .venv/                              # Python virtual environment
├── datasets/                           # Test datasets (documentation-aligned)
│   ├── coffee_machine_ratings.json    # Two-sample comparison example
│   ├── coffee_shop_traffic.json       # Case 2: Fail to reject (p=0.08)
│   ├── normality_test_example.json    # For assumption checking
│   ├── sales_example.json             # Case 1: Reject H₀ (p=0.042)
│   ├── sales_three_stores.json        # ANOVA example
│   └── website_redesign.json          # Case 3: Paired test (p=0.02)
│
├── src/                                # Main source code
│   ├── core/                           # Core framework
│   │   ├── __init__.py
│   │   ├── base_test.py               # Abstract base class (Template Method)
│   │   └── cache_manager.py           # Temp JSON caching
│   │
│   ├── tests/                          # Statistical test implementations
│   │   ├── __init__.py
│   │   ├── parametric/
│   │   │   ├── __init__.py
│   │   │   ├── t_tests.py             # One-sample, two-sample, paired
│   │   │   └── anova.py               # One-way ANOVA
│   │   ├── non_parametric/
│   │   │   ├── __init__.py
│   │   │   └── rank_tests.py          # Mann-Whitney, Wilcoxon, Kruskal-Wallis
│   │   ├── normality/
│   │   │   ├── __init__.py
│   │   │   └── normality_tests.py     # Shapiro-Wilk, K-S, Anderson-Darling, Jarque-Bera
│   │   └── variance/
│   │       ├── __init__.py
│   │       └── variance_tests.py      # Levene's, Bartlett's, F-test
│   │
│   ├── datasets/
│   │   ├── __init__.py
│   │   └── loader.py                  # Dataset loading and management
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── test_suggester.py          # Auto test suggestion
│   │
│   ├── __init__.py
│   └── mcp_server.py                  # FastMCP server integration
│
├── IMPLEMENTATION-1.md                 # Original implementation plan
├── IMPLEMENTATION_COMPLETE.md          # Completion summary
├── USAGE_GUIDE.md                      # How to use the system
├── PROJECT_STRUCTURE.md                # This file
├── README.md                           # Project overview
├── LLM_USAGE_GUIDE.md                  # Guide for LLM users
│
├── hypothesis-tester-for-megginners.md # Documentation (Case explanations)
├── sample-cases-and-explanation.md     # Detailed case studies
│
├── generate_datasets.py                # Script to generate datasets
├── test_implementation.py              # Test script for validation
│
├── fastmcp.json                        # MCP server configuration
├── pyproject.toml                      # Project metadata
├── requirements.txt                    # Python dependencies
└── uv.lock                             # Dependency lock file
```

---

## File Descriptions

### Core Implementation (`src/`)

#### `src/core/base_test.py`
- Abstract base class for all hypothesis tests
- Implements Template Method pattern
- Defines workflow: validate → check assumptions → compute → interpret
- 200+ lines

#### `src/core/cache_manager.py`
- Manages temporary JSON cache in `/tmp/mcp-hypothesis-cache/`
- 24-hour TTL with auto-cleanup
- Serializes numpy arrays automatically
- 180+ lines

#### `src/tests/parametric/t_tests.py`
- `OneSampleTTest` - Compare sample mean to known value
- `TwoSampleTTest` - Compare two independent groups
- `PairedTTest` - Compare paired observations
- 250+ lines

#### `src/tests/parametric/anova.py`
- `OneWayANOVA` - Compare 3+ independent groups
- Includes eta-squared effect size
- 130+ lines

#### `src/tests/non_parametric/rank_tests.py`
- `MannWhitneyUTest` - Non-parametric two-sample
- `WilcoxonSignedRankTest` - Non-parametric paired
- `KruskalWallisTest` - Non-parametric ANOVA
- 180+ lines

#### `src/tests/normality/normality_tests.py`
- `ShapiroWilkTest` - Best for n ≤ 50
- `KolmogorovSmirnovTest` - General distribution test
- `AndersonDarlingTest` - Sensitive to tails
- `JarqueBeraTest` - Best for large samples
- 220+ lines

#### `src/tests/variance/variance_tests.py`
- `LeveneTest` - Robust to non-normality
- `BartlettTest` - Most powerful for normal data
- `FTestVariance` - Two-sample variance comparison
- 200+ lines

#### `src/datasets/loader.py`
- Loads datasets from JSON files
- Handles different data formats (single, paired, grouped)
- Provides dataset metadata
- 80+ lines

#### `src/utils/test_suggester.py`
- Analyzes data characteristics
- Suggests appropriate statistical test
- Provides reasoning and alternatives
- 280+ lines

#### `src/mcp_server.py`
- FastMCP server with 6 tools
- Integrates all components
- Lightweight responses with caching
- 250+ lines

---

### Datasets (`datasets/`)

All datasets follow standardized schema:
- `dataset_info` - Metadata and context
- `hypothesis` - H₀, H₁, alpha
- `data` - Actual data arrays
- `expected_result` - For validation
- `business_interpretation` - Practical meaning

#### `sales_example.json`
- **Case 1** from documentation
- One-sample t-test: $5,150 vs $5,000
- Expected: t≈2.096, p≈0.042 → Reject H₀

#### `coffee_shop_traffic.json`
- **Case 2** from documentation
- One-sample t-test: 120 vs 100 customers
- Expected: p≈0.08 → Fail to reject H₀

#### `website_redesign.json`
- **Case 3** from documentation
- Paired t-test: 5.0 min vs 5.5 min
- Expected: p≈0.02 → Reject H₀

#### `coffee_machine_ratings.json`
- Two-sample t-test example
- Old: 7.2/10, New: 7.8/10
- Expected: p≈0.03 → Reject H₀

#### `sales_three_stores.json`
- One-way ANOVA example
- Three independent groups
- Store A: $5,000, B: $5,200, C: $4,800

#### `normality_test_example.json`
- For testing normality assumptions
- Normally distributed data (n=50)
- Expected: Fail to reject H₀ (data is normal)

---

### Documentation

#### `IMPLEMENTATION-1.md`
- Original implementation plan
- OOP architecture design
- Test catalog with examples
- Dataset structure specifications

#### `IMPLEMENTATION_COMPLETE.md`
- Completion summary
- Test results
- Success metrics
- File count and statistics

#### `USAGE_GUIDE.md`
- Complete usage examples
- Workflow patterns
- Troubleshooting guide
- Best practices

#### `README.md`
- Project overview
- Quick start guide
- Features summary

#### `LLM_USAGE_GUIDE.md`
- Guide for LLM users
- Tool descriptions
- Example queries

#### `hypothesis-tester-for-megginners.md`
- Beginner-friendly explanation
- Sales, coffee shop, website examples
- H₀ and H₁ explanations
- P-value interpretation

#### `sample-cases-and-explanation.md`
- Detailed case studies
- Complete walkthrough of each example
- Type I and Type II errors
- Business interpretations

---

### Scripts

#### `generate_datasets.py`
- Generates all 6 datasets
- Uses numpy with fixed seed for reproducibility
- Ensures exact statistics match documentation

#### `test_implementation.py`
- Validates entire implementation
- Tests dataset loading, test execution, caching
- Ensures all components work together

---

### Configuration

#### `fastmcp.json`
- MCP server configuration
- Server path: `python -m src.mcp_server`
- Dependencies list

#### `requirements.txt`
- Python dependencies:
  - fastmcp >= 2.12.0
  - numpy >= 1.24.0
  - scipy >= 1.10.0
  - pandas >= 2.0.0
  - matplotlib >= 3.7.0
  - seaborn >= 0.12.0
  - statsmodels >= 0.14.0

#### `pyproject.toml`
- Project metadata
- Build system configuration

---

## Statistics

- **Total Python modules:** 19
- **Total lines of code:** ~2,600
- **Number of tests implemented:** 14
- **Number of datasets:** 6
- **Documentation files:** 7

---

## Removed During Cleanup

✅ Removed unused files:
- `main.py` (old server)
- `plot_boxplot.png`, `plot_histogram.png`, `plot_qqplot.png` (old plots)
- `plots/` directory (unused)
- `__pycache__/` (Python cache)
- `venv/` (duplicate virtual environment)
- `downloader.ipynb` (unused notebook)
- `runner.sh` (unused script)
- Old dataset files: `clinical_trial.json`, `customer_satisfaction.json`, `example.json`, `inventory_forecast.json`

---

## Clean and Ready! ✅

The codebase is now clean, organized, and production-ready with:
- ✅ No unused files
- ✅ Clear structure
- ✅ Comprehensive documentation
- ✅ All tests passing
