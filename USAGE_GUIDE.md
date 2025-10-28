# MCP Hypothesis Tester v2 - Usage Guide

## Quick Start

### 1. List Available Datasets

```python
list_available_datasets()
```

**Returns:**
```json
{
  "datasets": [
    {
      "name": "sales_example",
      "description": "Daily sales - testing if Q1 2024 differs from $5,000",
      "test_recommended": "one_sample_t_test",
      "case_reference": "Case 1 from documentation"
    },
    ...
  ],
  "count": 6
}
```

---

### 2. Get Test Suggestion (Recommended!)

```python
suggest_test(
    dataset_name="sales_example",
    test_params={"mu0": 5000}
)
```

**Returns:**
```json
{
  "primary_test": "one_sample_t_test",
  "test_name": "One-Sample T-Test",
  "reason": "Data is continuous and approximately normal (or n ≥ 30)",
  "confidence": "high",
  "parameters": {"mu0": 5000},
  "alternative_tests": ["sign_test", "wilcoxon_signed_rank"],
  "assumptions_met": true
}
```

---

### 3. Check Assumptions (Optional but Recommended)

```python
check_assumptions(
    dataset_name="sales_example",
    test_type="one_sample_t_test"
)
```

**Returns:**
```json
{
  "assumptions": {
    "normality": true,
    "independence": true,
    "sufficient_sample_size": true
  },
  "all_met": true,
  "violations": [],
  "recommendation": "one_sample_t_test is appropriate for this data."
}
```

---

### 4. Run the Test

```python
run_hypothesis_test(
    test_type="one_sample_t_test",
    dataset_name="sales_example",
    alpha=0.05,
    test_params={"mu0": 5000}
)
```

**Returns (Lightweight Summary):**
```json
{
  "summary": {
    "test_name": "One Sample T Test",
    "decision": "reject",
    "p_value": 0.0441,
    "alpha": 0.05,
    "significant": true,
    "interpretation": "The sample mean (5150.00) is statistically significantly different from the hypothesized value (5000). This represents a 3.0% change. With p=0.0441 < α=0.05, we reject H₀.",
    "recommendation": "Evidence suggests a significant effect. Consider practical significance and collect more data to confirm.",
    "effect_size": 0.309,
    "warnings": null
  },
  "cache_id": "abc123def456",
  "note": "Full details cached. Use get_cached_result() to retrieve detailed analysis."
}
```

---

### 5. Get Full Details (If Needed)

```python
get_cached_result(
    cache_id="abc123def456",
    include_raw_data=False
)
```

**Returns (Complete Analysis):**
```json
{
  "test_name": "One Sample T Test",
  "test_type": "one_sample_t_test",
  "statistics": {
    "test_statistic": 2.073,
    "p_value": 0.0441,
    "alpha": 0.05,
    "effect_size": 0.309,
    "confidence_interval": [5007.2, 5292.8],
    "power": null
  },
  "hypothesis": {
    "null": "H₀: μ = 5000 (population mean equals 5000)",
    "alternative": "H₁: μ ≠ 5000 (population mean differs from 5000)",
    "decision": "reject",
    "significant": true
  },
  "interpretation": {
    "summary": "The sample mean (5150.00) is statistically significantly different...",
    "recommendation": "Evidence suggests a significant effect..."
  },
  "metadata": {
    "sample_sizes": {"n": 45},
    "assumptions_met": {
      "normality": true,
      "independence": true,
      "sufficient_sample_size": true
    },
    "warnings": []
  }
}
```

---

## Complete Workflow Examples

### Example 1: Sales Analysis (One-Sample T-Test)

**Business Question:** "Has daily sales changed from our historical $5,000 baseline?"

```python
# Step 1: Suggest test
suggestion = suggest_test("sales_example", {"mu0": 5000})
# Recommends: one_sample_t_test

# Step 2: Check assumptions
assumptions = check_assumptions("sales_example", "one_sample_t_test")
# All assumptions met ✓

# Step 3: Run test
result = run_hypothesis_test(
    "one_sample_t_test",
    "sales_example",
    test_params={"mu0": 5000}
)

# Step 4: Interpret
print(f"Decision: {result['summary']['decision']}")  # reject
print(f"P-value: {result['summary']['p_value']}")     # 0.0441
print(f"Significant: {result['summary']['significant']}")  # True

# Business conclusion:
# "Sales of $5,150 are significantly higher than $5,000 baseline (p=0.044).
#  This is a real increase, not just luck. Investigate what caused this improvement!"
```

---

### Example 2: Website Redesign (Paired T-Test)

**Business Question:** "Did website redesign change visit duration?"

```python
# Step 1: Suggest test
suggestion = suggest_test("website_redesign")
# Recommends: paired_t_test

# Step 2: Run test
result = run_hypothesis_test(
    "paired_t_test",
    "website_redesign"
)

# Interpretation depends on result:
if result['summary']['significant']:
    print("Visit time changed significantly!")
    print("Analyze WHERE users spend extra time:")
    print("  - Product pages? GOOD (considering purchases)")
    print("  - Help pages? BAD (confused)")
else:
    print("No significant change in visit time")
```

---

### Example 3: Coffee Shop Traffic (Fail to Reject)

**Business Question:** "Did customer traffic increase?"

```python
# Run test
result = run_hypothesis_test(
    "one_sample_t_test",
    "coffee_shop_traffic",
    test_params={"mu0": 100}
)

# Result: p=0.08, fail to reject H₀
print(result['summary']['interpretation'])
# "No significant difference... p=0.08 ≥ α=0.05, we fail to reject H₀."

# Business conclusion:
# "120 customers last week vs usual 100 isn't statistically significant.
#  Could be random fluctuation. Monitor for 2-3 more weeks before making decisions."
```

---

### Example 4: Multiple Stores (ANOVA)

**Business Question:** "Do sales differ across 3 stores?"

```python
# Step 1: Suggest test
suggestion = suggest_test("sales_three_stores")
# Recommends: one_way_anova (3+ groups)

# Step 2: Check assumptions
assumptions = check_assumptions("sales_three_stores", "one_way_anova")
# Check equal_variances assumption

# Step 3: Run test
result = run_hypothesis_test(
    "one_way_anova",
    "sales_three_stores"
)

if result['summary']['significant']:
    print("At least one store differs significantly!")
    print("Recommendation:", result['summary']['recommendation'])
    # "Consider post-hoc tests (Tukey HSD) to identify which stores differ"
```

---

### Example 5: Checking Normality Before T-Test

**Question:** "Is my data normal enough for t-test?"

```python
# Step 1: Test normality
normality_result = run_hypothesis_test(
    "shapiro_wilk",
    "sales_example"
)

if normality_result['summary']['decision'] == 'fail_to_reject':
    print("Data is normal - use t-test ✓")
    # Run parametric test
    result = run_hypothesis_test("one_sample_t_test", "sales_example", {"mu0": 5000})
else:
    print("Data not normal - use non-parametric test")
    # Run non-parametric alternative
    result = run_hypothesis_test("wilcoxon_signed_rank", "sales_example")
```

---

## Available Tests

### List All Tests

```python
list_available_tests()
```

**Returns:**
```json
{
  "by_category": {
    "parametric": [
      {
        "test_id": "one_sample_t_test",
        "test_name": "One Sample T Test",
        "description": "One-sample t-test: Tests if the mean of a single sample differs from a known value."
      },
      ...
    ],
    "non_parametric": [...],
    "normality": [...],
    "variance": [...]
  },
  "total_count": 14
}
```

---

## Test Selection Guide

### Single Sample
- **Continuous + Normal:** `one_sample_t_test`
- **Continuous + Not Normal:** `wilcoxon_signed_rank`
- **Ordinal:** `sign_test`

### Two Independent Groups
- **Continuous + Normal + Equal Var:** `two_sample_t_test` (equal_var=True)
- **Continuous + Normal + Unequal Var:** `two_sample_t_test` (equal_var=False) [Welch's]
- **Continuous + Not Normal:** `mann_whitney_u`
- **Ordinal:** `mann_whitney_u`

### Two Paired Groups
- **Continuous + Normal:** `paired_t_test`
- **Continuous + Not Normal:** `wilcoxon_signed_rank`
- **Ordinal:** `wilcoxon_signed_rank`

### Three or More Groups
- **Continuous + Normal + Equal Var:** `one_way_anova`
- **Continuous + Not Normal or Unequal Var:** `kruskal_wallis`

### Check Normality
- **n ≤ 50:** `shapiro_wilk` (most powerful)
- **n > 50:** `shapiro_wilk` or `anderson_darling`
- **n > 5000:** `jarque_bera`

### Check Equal Variance
- **Normal data, 2 groups:** `f_test_variance`
- **Normal data, 3+ groups:** `bartlett`
- **Non-normal or uncertain:** `levene` (most robust)

---

## Common Patterns

### Pattern 1: Quick Test Without Assumptions Check

```python
# For experienced users who know their data
result = run_hypothesis_test(
    "one_sample_t_test",
    "sales_example",
    test_params={"mu0": 5000}
)
```

### Pattern 2: Full Workflow (Recommended)

```python
# 1. Suggest
suggestion = suggest_test("sales_example", {"mu0": 5000})

# 2. Check
assumptions = check_assumptions("sales_example", suggestion['primary_test'])

# 3. Run
result = run_hypothesis_test(
    suggestion['primary_test'],
    "sales_example",
    test_params=suggestion['parameters']
)

# 4. Interpret
if result['summary']['significant']:
    print("Significant effect found!")
else:
    print("No significant effect")
```

### Pattern 3: Robust Analysis (Check Normality First)

```python
# 1. Check normality
normality = run_hypothesis_test("shapiro_wilk", "sales_example")

# 2. Choose test based on normality
if normality['summary']['decision'] == 'fail_to_reject':
    test_type = "one_sample_t_test"  # Parametric
else:
    test_type = "wilcoxon_signed_rank"  # Non-parametric

# 3. Run chosen test
result = run_hypothesis_test(test_type, "sales_example", {"mu0": 5000})
```

---

## Interpreting Results

### P-Value Interpretation

- **p < 0.01:** Very strong evidence against H₀ (highly significant)
- **0.01 ≤ p < 0.05:** Strong evidence against H₀ (significant)
- **0.05 ≤ p < 0.10:** Weak evidence against H₀ (marginally significant)
- **p ≥ 0.10:** Insufficient evidence against H₀ (not significant)

### Decision Rules

- **p < α:** Reject H₀ (evidence of effect)
- **p ≥ α:** Fail to reject H₀ (insufficient evidence)

### Effect Size Interpretation (Cohen's d)

- **|d| < 0.2:** Negligible effect
- **0.2 ≤ |d| < 0.5:** Small effect
- **0.5 ≤ |d| < 0.8:** Medium effect
- **|d| ≥ 0.8:** Large effect

**Important:** Statistical significance ≠ Practical significance!
- p < 0.05 means "effect is real"
- Effect size tells you "how big is the effect"

---

## Troubleshooting

### Error: "Dataset not found"
```python
# List available datasets
datasets = list_available_datasets()
print(datasets['datasets'])
```

### Error: "Unknown test type"
```python
# List available tests
tests = list_available_tests()
print([t['test_id'] for t in tests['all_tests']])
```

### Warning: "Assumptions not met"
```python
# Check which assumptions failed
assumptions = check_assumptions("your_dataset", "your_test")
print(assumptions['violations'])
print(assumptions['recommendation'])

# Use suggested non-parametric alternative
```

### Result: "Cache entry not found"
```python
# Cache entries expire after 24 hours
# Re-run the test if needed
result = run_hypothesis_test(...)
```

---

## Advanced Usage

### Custom Alpha Level

```python
# Use α = 0.01 for more stringent test
result = run_hypothesis_test(
    "one_sample_t_test",
    "sales_example",
    alpha=0.01,  # More conservative
    test_params={"mu0": 5000}
)
```

### One-Tailed Tests

```python
# Test if mean > 5000 (one-tailed)
result = run_hypothesis_test(
    "one_sample_t_test",
    "sales_example",
    test_params={
        "mu0": 5000,
        "alternative": "greater"  # or "less"
    }
)
```

### Welch's T-Test (Unequal Variances)

```python
# When variances are not equal
result = run_hypothesis_test(
    "two_sample_t_test",
    "your_dataset",
    test_params={
        "equal_var": False  # Use Welch's test
    }
)
```

---

## Best Practices

1. ✅ **Always check assumptions** before parametric tests
2. ✅ **Use auto-suggestion** if uncertain which test to use
3. ✅ **Report effect sizes** along with p-values
4. ✅ **Consider practical significance** not just statistical significance
5. ✅ **Use non-parametric tests** when assumptions violated
6. ✅ **Pre-specify alpha** before looking at data
7. ✅ **Don't p-hack** (test multiple hypotheses without correction)

---

## Getting Help

```python
# List all datasets with descriptions
list_available_datasets()

# List all tests with descriptions
list_available_tests()

# Get test suggestion with reasoning
suggest_test("your_dataset")

# Check what assumptions your test needs
check_assumptions("your_dataset", "your_test")
```

---

**Happy Testing! 📊✨**
