# MCP Hypothesis Tester

A FastMCP server that provides statistical hypothesis testing and analysis tools through the Model Context Protocol (MCP).

## Features

- **Statistical Tests**: Perform various hypothesis tests including t-tests, chi-square tests, Mann-Whitney U tests, and Wilcoxon signed-rank tests
- **Descriptive Statistics**: Calculate comprehensive descriptive statistics for datasets
- **Data Visualization**: Create histograms, box plots, and Q-Q plots for data analysis
- **Pass-by-Reference**: Ultra-fast data loading from JSON files (10-100x faster than passing arrays)
- **Rich Data Schemas**: AI-friendly metadata for better analysis context
- **FastMCP Integration**: Built with FastMCP for easy integration with MCP-compatible clients

## Installation

1. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare the environment** (optional, for production deployment):
   ```bash
   fastmcp project prepare fastmcp.json --output-dir ./env
   ```

## Usage

### Development Mode
```bash
python main.py --dev
```

### Production Mode
```bash
python main.py
```

### Using FastMCP CLI
```bash
fastmcp run fastmcp.json
```

## Available Tools

### 1. list_datasets
List all available datasets in the datasets directory.

**Parameters:** None

**Returns:** List of available dataset names

### 2. statistical_test
Perform various statistical hypothesis tests.

**Parameters:**
- `test_type` (string): Type of test to perform
  - `t_test`: One-sample t-test
  - `chi_square`: Chi-square goodness of fit test
  - `mann_whitney`: Mann-Whitney U test
  - `wilcoxon`: Wilcoxon signed-rank test
- `data_source` (string): Dataset name (e.g., "example", "clinical_trial")
- `alpha` (number, optional): Significance level (default: 0.05)

**Example:**
```json
{
  "test_type": "t_test",
  "data_source": "clinical_trial",
  "alpha": 0.05
}
```

### 3. descriptive_stats
Calculate descriptive statistics for a dataset.

**Parameters:**
- `data_source` (string): Dataset name

**Example:**
```json
{
  "data_source": "example"
}
```

### 4. create_visualization
Create visualizations for the data.

**Parameters:**
- `data_source` (string): Dataset name
- `plot_type` (string, optional): Type of plot
  - `histogram`: Data distribution histogram
  - `boxplot`: Box plot for distribution analysis
  - `qqplot`: Q-Q plot for normality assessment

**Example:**
```json
{
  "data_source": "example",
  "plot_type": "histogram"
}
```

## Data Storage

### Dataset Location
All datasets are stored in the `datasets/` directory as JSON files.

### Supported Formats

#### Simple Array Format
```json
[1.2, 3.4, 5.6, 7.8, 9.1]
```

#### Rich Schema Format (Recommended)
```json
{
  "dataset_info": {
    "name": "experiment_1",
    "description": "Clinical trial results",
    "tags": ["clinical", "drug_trial"]
  },
  "data_structure": {
    "format": "univariate",
    "data_type": "continuous",
    "units": "mg/dL"
  },
  "data": [1.2, 3.4, 5.6, 7.8, 9.1],
  "recommended_analyses": ["descriptive_stats", "t_test"]
}
```

## Usage Examples

### Basic Workflow
```bash
# 1. List available datasets
{"tool": "list_datasets"}

# 2. Get descriptive statistics
{"tool": "descriptive_stats", "data_source": "example"}

# 3. Perform hypothesis test
{"tool": "statistical_test", "test_type": "t_test", "data_source": "example"}

# 4. Create visualization
{"tool": "create_visualization", "data_source": "example", "plot_type": "histogram"}
```

## Documentation

For detailed LLM usage instructions, see [LLM_USAGE_GUIDE.md](LLM_USAGE_GUIDE.md).

## Configuration

The `fastmcp.json` file contains the server configuration including:
- Project metadata
- Python version requirements
- Dependencies
- Available tools and their schemas
- Script definitions

## Development

### Project Structure
```
mcp-hypothesis-tester/
├── main.py              # Main server implementation
├── fastmcp.json         # FastMCP configuration
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── venv/               # Virtual environment (created during setup)
```

### Adding New Tools

To add a new statistical tool:

1. Create a new function decorated with `@mcp.tool()`
2. Add the tool definition to `fastmcp.json`
3. Implement the tool logic with proper error handling
4. Update this README with usage examples

## Testing

Run tests (when available):
```bash
python -m pytest tests/
```

## License

This project is open source. Please check the license file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
