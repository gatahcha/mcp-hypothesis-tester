#!/usr/bin/env python3
"""
MCP Hypothesis Tester Server

A FastMCP server that provides statistical hypothesis testing and analysis tools.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("MCP Hypothesis Tester")

# In-memory cache for loaded datasets
_dataset_cache = {}

def _convert_numpy_types(obj):
    """
    Convert NumPy types to native Python types for JSON serialization.
    
    Args:
        obj: Object that may contain NumPy types
    
    Returns:
        Object with NumPy types converted to Python types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: _convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_types(item) for item in obj]
    else:
        return obj

def _load_dataset_from_file(file_path: str) -> np.ndarray:
    """
    Load dataset from JSON file with caching support.
    Supports both simple arrays and rich schema formats.
    
    Args:
        file_path: Path to JSON file (supports relative paths like "experiment1" -> datasets/experiment1.json)
    
    Returns:
        numpy array of the data
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the JSON format is invalid
    """
    # Check cache first
    if file_path in _dataset_cache:
        return _dataset_cache[file_path]
    
    # Handle relative paths
    if not os.path.isabs(file_path) and not file_path.startswith('datasets/'):
        full_path = os.path.join('datasets', f"{file_path}.json")
    else:
        full_path = file_path
    
    # Load JSON file
    try:
        with open(full_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {full_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {full_path}: {e}")
    
    # Handle different JSON formats
    if isinstance(data, list):
        # Simple array format: [1.2, 3.4, ...]
        data_array = np.array(data, dtype=float)
    elif isinstance(data, dict):
        if 'data' in data:
            # Rich schema format: {"data": [...], "dataset_info": {...}, ...}
            data_content = data['data']
            
            if isinstance(data_content, list):
                # Univariate data: {"data": [1.2, 3.4, ...]}
                data_array = np.array(data_content, dtype=float)
            elif isinstance(data_content, dict):
                # Grouped data: {"data": {"control": [...], "treatment": [...]}}
                # For now, flatten all groups into a single array
                # TODO: In future, we could return group information
                all_values = []
                for group_name, group_data in data_content.items():
                    if isinstance(group_data, list):
                        all_values.extend(group_data)
                data_array = np.array(all_values, dtype=float)
            else:
                raise ValueError(f"Unsupported data format in {full_path}. Expected array or object with group data.")
            
            # Log dataset information for AI context
            if 'dataset_info' in data:
                info = data['dataset_info']
                print(f"📊 Loading dataset: {info.get('name', 'unknown')} - {info.get('description', 'no description')}", file=sys.stderr)
            
            if 'data_structure' in data:
                structure = data['data_structure']
                print(f"🔍 Data format: {structure.get('format', 'unknown')}, Type: {structure.get('data_type', 'unknown')}, Units: {structure.get('units', 'none')}", file=sys.stderr)
            
            if 'recommended_analyses' in data:
                analyses = data['recommended_analyses']
                print(f"💡 Recommended analyses: {', '.join(analyses)}", file=sys.stderr)
        else:
            raise ValueError(f"Unsupported JSON format in {full_path}. Expected array or object with 'data' key.")
    else:
        raise ValueError(f"Unsupported JSON format in {full_path}. Expected array or object with 'data' key.")
    
    # Cache the result
    _dataset_cache[file_path] = data_array
    return data_array

@mcp.tool()
def statistical_test(test_type: str, data_source: str, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Perform various statistical hypothesis tests.
    
    Args:
        test_type: Type of test to perform (t_test, chi_square, anova, mann_whitney, wilcoxon)
        data_source: Path to JSON file containing the dataset (e.g., "experiment1" or "datasets/data.json")
        alpha: Significance level (default: 0.05)
    
    Returns:
        Dictionary containing test results
    """
    try:
        data_array = _load_dataset_from_file(data_source)
        
        if test_type == "t_test":
            # One-sample t-test (testing if mean differs from 0)
            statistic, p_value = stats.ttest_1samp(data_array, 0)
            result = {
                "test_type": "One-sample t-test",
                "statistic": float(statistic),
                "p_value": float(p_value),
                "alpha": alpha,
                "significant": p_value < alpha,
                "interpretation": f"Mean significantly different from 0" if p_value < alpha else f"Mean not significantly different from 0"
            }
            
        elif test_type == "chi_square":
            # Chi-square goodness of fit test (assuming uniform distribution)
            observed_freq, _ = np.histogram(data_array, bins=5)
            expected_freq = np.full_like(observed_freq, len(data_array) / 5)
            statistic, p_value = stats.chisquare(observed_freq, expected_freq)
            result = {
                "test_type": "Chi-square goodness of fit test",
                "statistic": float(statistic),
                "p_value": float(p_value),
                "alpha": alpha,
                "significant": p_value < alpha,
                "interpretation": f"Data significantly deviates from uniform distribution" if p_value < alpha else f"Data does not significantly deviate from uniform distribution"
            }
            
        elif test_type == "mann_whitney":
            # Mann-Whitney U test (requires two groups, splitting data in half)
            mid_point = len(data_array) // 2
            group1 = data_array[:mid_point]
            group2 = data_array[mid_point:]
            statistic, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            result = {
                "test_type": "Mann-Whitney U test",
                "statistic": float(statistic),
                "p_value": float(p_value),
                "alpha": alpha,
                "significant": p_value < alpha,
                "interpretation": f"Groups significantly different" if p_value < alpha else f"Groups not significantly different"
            }
            
        elif test_type == "wilcoxon":
            # Wilcoxon signed-rank test (requires paired data, using first half vs second half)
            mid_point = len(data_array) // 2
            group1 = data_array[:mid_point]
            group2 = data_array[mid_point:mid_point + len(group1)]  # Make equal length
            if len(group1) == len(group2):
                statistic, p_value = stats.wilcoxon(group1, group2)
                result = {
                    "test_type": "Wilcoxon signed-rank test",
                    "statistic": float(statistic),
                    "p_value": float(p_value),
                    "alpha": alpha,
                    "significant": p_value < alpha,
                    "interpretation": f"Paired groups significantly different" if p_value < alpha else f"Paired groups not significantly different"
                }
            else:
                result = {"error": "Data length must be even for Wilcoxon test"}
        
        else:
            result = {"error": f"Unknown test type: {test_type}"}
            
        return _convert_numpy_types(result)
        
    except Exception as e:
        return {"error": f"Error performing test: {str(e)}"}

@mcp.tool()
def descriptive_stats(data_source: str) -> Dict[str, Any]:
    """
    Calculate descriptive statistics for a dataset.
    
    Args:
        data_source: Path to JSON file containing the dataset (e.g., "experiment1" or "datasets/data.json")
    
    Returns:
        Dictionary containing descriptive statistics
    """
    try:
        data_array = _load_dataset_from_file(data_source)
        
        stats_dict = {
            "count": len(data_array),
            "mean": float(np.mean(data_array)),
            "median": float(np.median(data_array)),
            "mode": float(stats.mode(data_array, keepdims=True)[0][0]) if len(data_array) > 0 else None,
            "std": float(np.std(data_array)),
            "variance": float(np.var(data_array)),
            "min": float(np.min(data_array)),
            "max": float(np.max(data_array)),
            "range": float(np.max(data_array) - np.min(data_array)),
            "skewness": float(stats.skew(data_array)),
            "kurtosis": float(stats.kurtosis(data_array)),
            "quartiles": {
                "q1": float(np.percentile(data_array, 25)),
                "q2": float(np.percentile(data_array, 50)),
                "q3": float(np.percentile(data_array, 75))
            }
        }
        
        return _convert_numpy_types(stats_dict)
        
    except Exception as e:
        return {"error": f"Error calculating descriptive statistics: {str(e)}"}

@mcp.tool()
def create_visualization(data_source: str, plot_type: str = "histogram") -> Dict[str, Any]:
    """
    Create visualizations for the data.
    
    Args:
        data_source: Path to JSON file containing the dataset (e.g., "experiment1" or "datasets/data.json")
        plot_type: Type of plot (histogram, boxplot, scatter, qqplot)
    
    Returns:
        Dictionary with plot information and save path
    """
    try:
        data_array = _load_dataset_from_file(data_source)
        
        # Create plots directory if it doesn't exist
        plots_dir = "plots"
        if not os.path.exists(plots_dir):
            os.makedirs(plots_dir)
        
        # Generate descriptive filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"{data_source}_{plot_type}_{timestamp}.png"
        plot_path = os.path.join(plots_dir, plot_filename)
        
        plt.figure(figsize=(10, 6))
        
        if plot_type == "histogram":
            plt.hist(data_array, bins=20, alpha=0.7, edgecolor='black')
            plt.title(f'Data Distribution - {data_source} (Histogram)')
            plt.xlabel('Value')
            plt.ylabel('Frequency')
            
        elif plot_type == "boxplot":
            plt.boxplot(data_array)
            plt.title(f'Data Distribution - {data_source} (Box Plot)')
            plt.ylabel('Value')
            
        elif plot_type == "qqplot":
            stats.probplot(data_array, dist="norm", plot=plt)
            plt.title(f'Q-Q Plot - {data_source} (Normal Distribution)')
            
        else:
            return {"error": f"Unknown plot type: {plot_type}"}
        
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {
            "plot_type": plot_type,
            "filename": plot_filename,
            "file_path": plot_path,
            "data_points": len(data_array),
            "dataset": data_source,
            "message": f"{plot_type.capitalize()} plot saved as {plot_filename} in plots/ directory"
        }
        
    except Exception as e:
        return {"error": f"Error creating visualization: {str(e)}"}

@mcp.tool()
def list_datasets() -> Dict[str, Any]:
    """
    List all available datasets in the datasets directory.
    
    Returns:
        Dictionary containing list of available dataset files
    """
    try:
        datasets_dir = "datasets"
        if not os.path.exists(datasets_dir):
            return {"datasets": [], "message": "No datasets directory found"}
        
        dataset_files = []
        for filename in os.listdir(datasets_dir):
            if filename.endswith('.json'):
                # Remove .json extension for cleaner display
                dataset_name = filename[:-5]
                dataset_files.append(dataset_name)
        
        return {
            "datasets": sorted(dataset_files),
            "count": len(dataset_files),
            "message": f"Found {len(dataset_files)} dataset(s) in {datasets_dir}/"
        }
        
    except Exception as e:
        return {"error": f"Error listing datasets: {str(e)}"}

@mcp.tool()
def list_plots() -> Dict[str, Any]:
    """
    List all available plots in the plots directory.
    
    Returns:
        Dictionary containing list of available plot files with metadata
    """
    try:
        plots_dir = "plots"
        if not os.path.exists(plots_dir):
            return {"plots": [], "count": 0, "message": "No plots directory found"}
        
        plot_files = []
        for filename in os.listdir(plots_dir):
            if filename.endswith('.png'):
                # Extract metadata from filename: dataset_plottype_timestamp.png
                parts = filename[:-4].split('_')  # Remove .png extension
                if len(parts) >= 3:
                    dataset = parts[0]
                    plot_type = parts[1]
                    timestamp = '_'.join(parts[2:])  # In case timestamp has underscores
                    
                    plot_files.append({
                        "filename": filename,
                        "dataset": dataset,
                        "plot_type": plot_type,
                        "timestamp": timestamp,
                        "file_path": os.path.join(plots_dir, filename)
                    })
                else:
                    # Fallback for files that don't match naming convention
                    plot_files.append({
                        "filename": filename,
                        "dataset": "unknown",
                        "plot_type": "unknown",
                        "timestamp": "unknown",
                        "file_path": os.path.join(plots_dir, filename)
                    })
        
        return {
            "plots": sorted(plot_files, key=lambda x: x['timestamp'], reverse=True),  # Most recent first
            "count": len(plot_files),
            "message": f"Found {len(plot_files)} plot(s) in {plots_dir}/"
        }
        
    except Exception as e:
        return {"error": f"Error listing plots: {str(e)}"}

def main():
    """Main function to run the MCP server."""
    parser = argparse.ArgumentParser(description="MCP Hypothesis Tester Server")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    
    args = parser.parse_args()
    
    if args.dev:
        print("🚀 Starting MCP Hypothesis Tester Server in development mode...", file=sys.stderr)
        print("📊 Available tools:", file=sys.stderr)
        print("  - statistical_test: Perform hypothesis tests (requires data_source)", file=sys.stderr)
        print("  - descriptive_stats: Calculate descriptive statistics (requires data_source)", file=sys.stderr)
        print("  - create_visualization: Create data visualizations (requires data_source)", file=sys.stderr)
        print("  - list_datasets: List available datasets in datasets/ directory", file=sys.stderr)
        print("  - list_plots: List available plots in plots/ directory", file=sys.stderr)
        print("💡 Usage: Place JSON files in datasets/ directory and reference by name", file=sys.stderr)
        print("📈 Plots are automatically saved to plots/ directory with timestamps", file=sys.stderr)
    
    # Run the MCP server (stdio mode for MCP protocol)
    mcp.run()

if __name__ == "__main__":
    main()
