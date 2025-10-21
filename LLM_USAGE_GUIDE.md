# MCP Hypothesis Tester - LLM Usage Guide

## 🎯 Overview

The MCP Hypothesis Tester is a **pass-by-reference** statistical analysis server designed for AI data scientists. Instead of passing large data arrays through function parameters (which is slow and token-intensive), you reference datasets stored in JSON files.

## 🚀 Key Benefits

- **⚡ Speed**: 10-100x faster than passing data arrays
- **🎯 Token Efficiency**: Use 1 token instead of thousands for data references
- **📊 Scalability**: Handle datasets too large for LLM context
- **🧠 AI-Friendly**: Rich metadata helps AI understand data context

## 📁 Data Storage System

### Dataset Location
All datasets are stored in the `datasets/` directory as JSON files.

### Supported JSON Formats

#### 1. Simple Array Format
```json
[1.2, 3.4, 5.6, 7.8, 9.1, 2.3, 4.5, 6.7, 8.9, 1.0]
```

#### 2. Rich Schema Format (Recommended)
```json
{
  "dataset_info": {
    "name": "experiment_1",
    "description": "Clinical trial results for drug efficacy",
    "version": "1.2.0",
    "tags": ["clinical", "drug_trial", "efficacy"],
    "domain": "healthcare"
  },
  
  "data_structure": {
    "format": "univariate",
    "data_type": "continuous",
    "units": "mg/dL",
    "precision": 1,
    "missing_values": 0
  },
  
  "data": [1.2, 3.4, 5.6, 7.8, 9.1, 2.3, 4.5, 6.7, 8.9, 1.0],
  
  "statistical_properties": {
    "sample_size": 10,
    "expected_distribution": "normal",
    "expected_mean": 5.0,
    "expected_std": 2.0,
    "confidence_level": 0.95
  },
  
  "experimental_design": {
    "study_type": "randomized_controlled_trial",
    "groups": ["control", "treatment"],
    "randomization": true,
    "blinding": "double_blind"
  },
  
  "data_quality": {
    "completeness": 1.0,
    "accuracy_score": 0.95,
    "consistency_check": "passed"
  },
  
  "context": {
    "research_question": "Does the new drug reduce blood glucose levels?",
    "hypothesis": "H1: Treatment group will have significantly lower glucose levels",
    "null_hypothesis": "H0: No difference between treatment and control groups"
  },
  
  "recommended_analyses": [
    "descriptive_stats",
    "t_test",
    "effect_size_calculation",
    "histogram_visualization"
  ],
  
  "metadata": {
    "researcher": "Dr. Jane Smith",
    "institution": "Medical Research Institute",
    "funding_source": "NIH Grant #12345"
  }
}
```

## 🛠️ Available Tools

### 1. `list_datasets()`
**Purpose**: Discover available datasets
**Parameters**: None
**Returns**: List of available dataset names

```json
{
  "datasets": ["example", "clinical_trial", "customer_satisfaction"],
  "count": 3,
  "message": "Found 3 dataset(s) in datasets/"
}
```

### 2. `statistical_test(test_type, data_source, alpha)`
**Purpose**: Perform hypothesis tests
**Parameters**:
- `test_type` (string): Type of test
  - `t_test`: One-sample t-test
  - `chi_square`: Chi-square goodness of fit test
  - `mann_whitney`: Mann-Whitney U test
  - `wilcoxon`: Wilcoxon signed-rank test
- `data_source` (string): Dataset name (e.g., "example", "clinical_trial")
- `alpha` (number, optional): Significance level (default: 0.05)

**Example**:
```json
{
  "test_type": "t_test",
  "data_source": "clinical_trial",
  "alpha": 0.05
}
```

### 3. `descriptive_stats(data_source)`
**Purpose**: Calculate descriptive statistics
**Parameters**:
- `data_source` (string): Dataset name

**Example**:
```json
{
  "data_source": "customer_satisfaction"
}
```

### 4. `create_visualization(data_source, plot_type)`
**Purpose**: Create data visualizations
**Parameters**:
- `data_source` (string): Dataset name
- `plot_type` (string, optional): Type of plot
  - `histogram`: Data distribution histogram
  - `boxplot`: Box plot for distribution analysis
  - `qqplot`: Q-Q plot for normality assessment

**Example**:
```json
{
  "data_source": "example",
  "plot_type": "histogram"
}
```

**Returns**:
```json
{
  "plot_type": "histogram",
  "filename": "example_histogram_20240115_143022.png",
  "file_path": "plots/example_histogram_20240115_143022.png",
  "data_points": 20,
  "dataset": "example",
  "message": "Histogram plot saved as example_histogram_20240115_143022.png in plots/ directory"
}
```

### 5. `list_plots()`
**Purpose**: Discover available plots
**Parameters**: None
**Returns**: List of available plot files with metadata

```json
{
  "plots": [
    {
      "filename": "clinical_trial_histogram_20240115_143022.png",
      "dataset": "clinical_trial",
      "plot_type": "histogram",
      "timestamp": "20240115_143022",
      "file_path": "plots/clinical_trial_histogram_20240115_143022.png"
    }
  ],
  "count": 1,
  "message": "Found 1 plot(s) in plots/"
}
```

## 🎯 Usage Patterns

### 1. Discovery Workflow
```json
// Step 1: List available datasets
{"tool": "list_datasets"}

// Step 2: Analyze a specific dataset
{"tool": "descriptive_stats", "data_source": "clinical_trial"}
```

### 2. Statistical Analysis Workflow
```json
// Step 1: Get descriptive statistics
{"tool": "descriptive_stats", "data_source": "clinical_trial"}

// Step 2: Perform hypothesis test
{"tool": "statistical_test", "test_type": "t_test", "data_source": "clinical_trial", "alpha": 0.05}

// Step 3: Create visualization
{"tool": "create_visualization", "data_source": "clinical_trial", "plot_type": "boxplot"}
```

### 3. Plot Management Workflow
```json
// Step 1: Create visualization
{"tool": "create_visualization", "data_source": "clinical_trial", "plot_type": "histogram"}

// Step 2: List available plots
{"tool": "list_plots"}

// Step 3: Create additional visualizations
{"tool": "create_visualization", "data_source": "clinical_trial", "plot_type": "boxplot"}
{"tool": "create_visualization", "data_source": "clinical_trial", "plot_type": "qqplot"}
```

### 4. Comparative Analysis Workflow
```json
// Step 1: Analyze multiple datasets
{"tool": "descriptive_stats", "data_source": "control_group"}
{"tool": "descriptive_stats", "data_source": "treatment_group"}

// Step 2: Compare groups
{"tool": "statistical_test", "test_type": "mann_whitney", "data_source": "clinical_trial"}
```

## 📊 Data Schema Guidelines

### For AI Data Scientists

When creating datasets, include rich metadata to help AI understand:

1. **Dataset Context**: What the data represents
2. **Statistical Properties**: Expected distributions, sample sizes
3. **Experimental Design**: Study type, randomization, blinding
4. **Data Quality**: Completeness, accuracy, validation status
5. **Recommended Analyses**: Suggested statistical tests and visualizations

### Schema Components Explained

- **`dataset_info`**: Basic information about the dataset
- **`data_structure`**: Technical details about data format and type
- **`statistical_properties`**: Expected statistical characteristics
- **`experimental_design`**: Research methodology information
- **`data_quality`**: Quality metrics and validation status
- **`context`**: Research questions and hypotheses
- **`recommended_analyses`**: Suggested statistical approaches
- **`metadata`**: Researcher and institutional information

## 🔍 Best Practices

### 1. Dataset Naming
- Use descriptive names: `clinical_trial_glucose`, `customer_satisfaction_scores`
- Avoid spaces and special characters
- Include version numbers for iterative datasets

### 2. Metadata Completeness
- Always include `dataset_info` and `data_structure`
- Provide clear `research_question` and `hypothesis`
- Specify `recommended_analyses` to guide AI decisions

### 3. Data Quality
- Set `missing_values` count accurately
- Indicate `outliers_detected` status
- Provide `completeness` and `accuracy_score`

### 4. Statistical Guidance
- Specify `expected_distribution` when known
- Provide `expected_mean` and `expected_std` for power calculations
- Set appropriate `confidence_level` and `effect_size_expected`

## ⚠️ Important Notes

1. **Never pass data arrays directly** - always use `data_source` parameter
2. **Dataset names are case-sensitive** - use exact names from `list_datasets()`
3. **Rich metadata is logged** - AI receives context about loaded datasets
4. **Caching is automatic** - repeated access to same dataset is fast
5. **Error handling** - Clear error messages for missing or invalid datasets

## 🎉 Example Complete Workflow

```json
// 1. Discover datasets
{"tool": "list_datasets"}

// 2. Get overview of clinical trial data
{"tool": "descriptive_stats", "data_source": "clinical_trial"}

// 3. Test if treatment is effective
{"tool": "statistical_test", "test_type": "t_test", "data_source": "clinical_trial", "alpha": 0.05}

// 4. Visualize the results
{"tool": "create_visualization", "data_source": "clinical_trial", "plot_type": "boxplot"}

// 5. Check normality assumption
{"tool": "create_visualization", "data_source": "clinical_trial", "plot_type": "qqplot"}
```

This pass-by-reference system makes statistical analysis incredibly fast and efficient for AI data scientists! 🚀

