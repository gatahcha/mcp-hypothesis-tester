"""
MCP Server for Hypothesis Testing with new OOP architecture
"""

import sys
import numpy as np
from typing import Dict, Any, Optional
from fastmcp import FastMCP

# Import core components
from src.core.cache_manager import CacheManager
from src.datasets.loader import DatasetLoader
from src.utils.test_suggester import TestSuggester

# Import test classes
from src.tests.parametric.t_tests import OneSampleTTest, TwoSampleTTest, PairedTTest
from src.tests.parametric.anova import OneWayANOVA
from src.tests.non_parametric.rank_tests import (
    MannWhitneyUTest, WilcoxonSignedRankTest, KruskalWallisTest
)
from src.tests.normality.normality_tests import (
    ShapiroWilkTest, KolmogorovSmirnovTest, AndersonDarlingTest, JarqueBeraTest
)
from src.tests.variance.variance_tests import LeveneTest, BartlettTest, FTestVariance


# Initialize MCP server
mcp = FastMCP("MCP Hypothesis Tester v2")

# Initialize components
cache_manager = CacheManager()
dataset_loader = DatasetLoader()
test_suggester = TestSuggester()


# Registry of available tests
TEST_REGISTRY = {
    "one_sample_t_test": OneSampleTTest,
    "two_sample_t_test": TwoSampleTTest,
    "paired_t_test": PairedTTest,
    "one_way_anova": OneWayANOVA,
    "mann_whitney_u": MannWhitneyUTest,
    "wilcoxon_signed_rank": WilcoxonSignedRankTest,
    "kruskal_wallis": KruskalWallisTest,
    "shapiro_wilk": ShapiroWilkTest,
    "kolmogorov_smirnov": KolmogorovSmirnovTest,
    "anderson_darling": AndersonDarlingTest,
    "jarque_bera": JarqueBeraTest,
    "levene": LeveneTest,
    "bartlett": BartlettTest,
    "f_test_variance": FTestVariance,
}


@mcp.tool()
def run_hypothesis_test(
    test_type: str,
    dataset_name: str,
    alpha: float = 0.05,
    test_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run hypothesis test on dataset.

    Args:
        test_type: Type of test (e.g., 'one_sample_t_test', 'mann_whitney_u')
        dataset_name: Name of dataset file (e.g., 'sales_example')
        alpha: Significance level (default: 0.05)
        test_params: Additional test parameters (e.g., {"mu0": 5000})

    Returns:
        Lightweight summary with cache reference

    Example:
        run_hypothesis_test("one_sample_t_test", "sales_example", alpha=0.05, test_params={"mu0": 5000})
    """
    try:
        # Load dataset
        dataset = dataset_loader.load_dataset(dataset_name)
        data = dataset_loader.get_data_array(dataset)

        # Get test class
        if test_type not in TEST_REGISTRY:
            return {
                "error": f"Unknown test type: {test_type}",
                "available_tests": list(TEST_REGISTRY.keys())
            }

        TestClass = TEST_REGISTRY[test_type]

        # Merge test params with defaults
        if test_params is None:
            test_params = {}

        # Get recommended parameters from dataset if available
        dataset_params = dataset.get('hypothesis', {})
        if 'mu0' in dataset_params and 'mu0' not in test_params:
            test_params['mu0'] = dataset_params['mu0']

        # Create test instance
        test_instance = TestClass(alpha=alpha, **test_params)
        test_instance.cache_manager = cache_manager

        # Run test with appropriate data format
        if isinstance(data, dict):
            if 'before' in data and 'after' in data:
                # Paired data
                result = test_instance.run(data['before'], data['after'])
            else:
                # Multiple groups
                groups = list(data.values())
                result = test_instance.run(*groups)
        else:
            # Single sample
            result = test_instance.run(data)

        # Cache full result
        cache_id = cache_manager.cache_result(
            test_type=test_type,
            test_result=result.to_dict(),
            raw_data={"dataset_name": dataset_name, "data_summary": _summarize_data(data)}
        )

        # Return lightweight summary for LLM
        return {
            "summary": {
                "test_name": result.test_name,
                "decision": result.decision,
                "p_value": result.p_value,
                "alpha": result.alpha,
                "significant": result.significant,
                "interpretation": result.interpretation,
                "recommendation": result.recommendation,
                "effect_size": result.effect_size,
                "warnings": result.warnings
            },
            "cache_id": cache_id,
            "note": "Full details cached. Use get_cached_result() to retrieve detailed analysis."
        }

    except Exception as e:
        return {"error": f"Error running test: {str(e)}"}


@mcp.tool()
def suggest_test(
    dataset_name: str,
    test_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Auto-suggest appropriate statistical test based on data characteristics.

    Args:
        dataset_name: Name of dataset file
        test_params: Additional parameters like 'mu0' for one-sample tests

    Returns:
        Test suggestion with reasoning

    Example:
        suggest_test("sales_example", test_params={"mu0": 5000})
    """
    try:
        # Load dataset
        dataset = dataset_loader.load_dataset(dataset_name)
        data = dataset_loader.get_data_array(dataset)

        # Convert to format for suggester
        if isinstance(data, dict):
            if 'before' in data and 'after' in data:
                data_groups = (data['before'], data['after'])
            else:
                data_groups = tuple(data.values())
        else:
            data_groups = (data,)

        # Get suggestion
        if test_params is None:
            test_params = {}

        suggestion = test_suggester.suggest_test(*data_groups, **test_params)

        # Add dataset context
        suggestion['dataset_info'] = dataset.get('dataset_info', {})
        suggestion['recommended_by_dataset'] = dataset.get('dataset_info', {}).get('test_recommended', '')

        return suggestion

    except Exception as e:
        return {"error": f"Error suggesting test: {str(e)}"}


@mcp.tool()
def get_cached_result(cache_id: str, include_raw_data: bool = False) -> Dict[str, Any]:
    """
    Retrieve full cached test result when needed.

    Args:
        cache_id: Cache identifier from test result
        include_raw_data: Whether to include raw data arrays

    Returns:
        Complete test result with all details
    """
    result = cache_manager.get_result(cache_id, include_raw_data)

    if result is None:
        return {"error": "Cache entry not found or expired"}

    return result


@mcp.tool()
def list_available_datasets() -> Dict[str, Any]:
    """
    List all available datasets in the datasets directory.

    Returns:
        Dictionary with dataset names and basic info
    """
    try:
        dataset_names = dataset_loader.list_datasets()
        datasets_info = []

        for name in dataset_names:
            try:
                info = dataset_loader.get_dataset_info(name)
                datasets_info.append({
                    "name": name,
                    "description": info.get('description', ''),
                    "test_recommended": info.get('test_recommended', ''),
                    "case_reference": info.get('case_reference', '')
                })
            except Exception as e:
                datasets_info.append({
                    "name": name,
                    "error": str(e)
                })

        return {
            "datasets": datasets_info,
            "count": len(datasets_info),
            "message": f"Found {len(datasets_info)} dataset(s)"
        }

    except Exception as e:
        return {"error": f"Error listing datasets: {str(e)}"}


@mcp.tool()
def list_available_tests() -> Dict[str, Any]:
    """
    List all available hypothesis tests.

    Returns:
        Dictionary with test names and descriptions
    """
    tests_info = []

    for test_name, TestClass in TEST_REGISTRY.items():
        try:
            # Create temporary instance to get docstring
            test = TestClass()
            doc = TestClass.__doc__ or "No description available"
            # Extract first line of docstring
            description = doc.strip().split('\n')[0]

            tests_info.append({
                "test_id": test_name,
                "test_name": test.get_test_name(),
                "description": description,
                "test_type": test.test_type().value
            })
        except:
            tests_info.append({
                "test_id": test_name,
                "error": "Could not load test information"
            })

    # Group by category
    parametric = [t for t in tests_info if 't_test' in t['test_id'] or 'anova' in t['test_id']]
    non_parametric = [t for t in tests_info if any(x in t['test_id'] for x in ['mann', 'wilcoxon', 'kruskal'])]
    normality = [t for t in tests_info if any(x in t['test_id'] for x in ['shapiro', 'kolmogorov', 'anderson', 'jarque'])]
    variance = [t for t in tests_info if any(x in t['test_id'] for x in ['levene', 'bartlett', 'f_test'])]

    return {
        "all_tests": tests_info,
        "by_category": {
            "parametric": parametric,
            "non_parametric": non_parametric,
            "normality": normality,
            "variance": variance
        },
        "total_count": len(tests_info)
    }


@mcp.tool()
def check_assumptions(dataset_name: str, test_type: str) -> Dict[str, Any]:
    """
    Check if dataset meets assumptions for specified test.

    Args:
        dataset_name: Name of dataset
        test_type: Type of test to check assumptions for

    Returns:
        Dictionary with assumption check results
    """
    try:
        # Load dataset
        dataset = dataset_loader.load_dataset(dataset_name)
        data = dataset_loader.get_data_array(dataset)

        # Get test class
        if test_type not in TEST_REGISTRY:
            return {"error": f"Unknown test type: {test_type}"}

        TestClass = TEST_REGISTRY[test_type]
        test_instance = TestClass()

        # Check assumptions based on data format
        if isinstance(data, dict):
            if 'before' in data and 'after' in data:
                assumptions = test_instance.check_assumptions(data['before'], data['after'])
            else:
                groups = list(data.values())
                assumptions = test_instance.check_assumptions(*groups)
        else:
            assumptions = test_instance.check_assumptions(data)

        violations = [k for k, v in assumptions.items() if not v]

        return {
            "test_type": test_type,
            "dataset": dataset_name,
            "assumptions": assumptions,
            "all_met": len(violations) == 0,
            "violations": violations,
            "recommendation": _get_assumption_recommendation(test_type, violations)
        }

    except Exception as e:
        return {"error": f"Error checking assumptions: {str(e)}"}


def _summarize_data(data) -> Dict[str, Any]:
    """Create lightweight summary of data (not full arrays)"""
    if isinstance(data, dict):
        summary = {}
        for key, arr in data.items():
            summary[key] = {
                "n": len(arr),
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std": float(np.std(arr))
            }
        return summary
    else:
        return {
            "n": len(data),
            "mean": float(np.mean(data)),
            "median": float(np.median(data)),
            "std": float(np.std(data))
        }


def _get_assumption_recommendation(test_type: str, violations: list) -> str:
    """Get recommendation based on assumption violations"""
    if not violations:
        return f"{test_type} is appropriate for this data."

    recommendations = {
        "normality": "Consider non-parametric alternative (Mann-Whitney, Kruskal-Wallis, Wilcoxon)",
        "equal_variances": "Use Welch's t-test or Welch's ANOVA instead",
        "independence": "Consider repeated measures or mixed effects models",
        "sufficient_sample_size": "Collect more data or use exact/permutation tests"
    }

    recs = [recommendations.get(v, f"Address {v} violation") for v in violations]
    return "; ".join(recs)


def main():
    """Run MCP server"""
    print("🚀 Starting MCP Hypothesis Tester v2...", file=sys.stderr)
    print(f"📊 Loaded {len(TEST_REGISTRY)} statistical tests", file=sys.stderr)
    print(f"📁 Datasets directory: {dataset_loader.datasets_dir}", file=sys.stderr)
    print(f"💾 Cache directory: {cache_manager.cache_dir}", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
