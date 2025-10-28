#!/usr/bin/env python3
"""
Quick test script to verify the implementation works
"""

import sys
import numpy as np

# Add src to path
sys.path.insert(0, '/Users/charisma/project/mcp-hypothesis-tester')

from src.datasets.loader import DatasetLoader
from src.tests.parametric.t_tests import OneSampleTTest, TwoSampleTTest, PairedTTest
from src.tests.non_parametric.rank_tests import MannWhitneyUTest
from src.tests.normality.normality_tests import ShapiroWilkTest
from src.utils.test_suggester import TestSuggester
from src.core.cache_manager import CacheManager


def test_dataset_loading():
    """Test dataset loading"""
    print("\n=== Testing Dataset Loading ===")
    loader = DatasetLoader()

    # List datasets
    datasets = loader.list_datasets()
    print(f"✓ Found {len(datasets)} datasets: {', '.join(datasets)}")

    # Load sales example
    sales_data = loader.load_dataset('sales_example')
    print(f"✓ Loaded sales_example: {sales_data['dataset_info']['name']}")

    data_array = loader.get_data_array(sales_data)
    print(f"✓ Extracted data array: n={len(data_array)}, mean={np.mean(data_array):.2f}")


def test_one_sample_t_test():
    """Test one-sample t-test with sales example"""
    print("\n=== Testing One-Sample T-Test (Sales Example) ===")

    loader = DatasetLoader()
    sales_data = loader.load_dataset('sales_example')
    data = loader.get_data_array(sales_data)

    # Run test
    test = OneSampleTTest(alpha=0.05, mu0=5000)
    result = test.run(data)

    print(f"✓ Test: {result.test_name}")
    print(f"✓ Statistic: {result.statistic:.3f}")
    print(f"✓ P-value: {result.p_value:.4f}")
    print(f"✓ Decision: {result.decision}")
    print(f"✓ Significant: {result.significant}")
    print(f"✓ Effect size (Cohen's d): {result.effect_size:.3f}")
    print(f"✓ Interpretation: {result.interpretation[:100]}...")


def test_paired_t_test():
    """Test paired t-test with website redesign"""
    print("\n=== Testing Paired T-Test (Website Redesign) ===")

    loader = DatasetLoader()
    website_data = loader.load_dataset('website_redesign')
    data = loader.get_data_array(website_data)

    # Run test
    test = PairedTTest(alpha=0.05)
    result = test.run(data['before'], data['after'])

    print(f"✓ Test: {result.test_name}")
    print(f"✓ Statistic: {result.statistic:.3f}")
    print(f"✓ P-value: {result.p_value:.4f}")
    print(f"✓ Decision: {result.decision}")
    print(f"✓ Significant: {result.significant}")


def test_normality_test():
    """Test normality test"""
    print("\n=== Testing Shapiro-Wilk Normality Test ===")

    loader = DatasetLoader()
    data_dict = loader.load_dataset('normality_test_example')
    data = loader.get_data_array(data_dict)

    # Run test
    test = ShapiroWilkTest(alpha=0.05)
    result = test.run(data)

    print(f"✓ Test: {result.test_name}")
    print(f"✓ Statistic: {result.statistic:.4f}")
    print(f"✓ P-value: {result.p_value:.4f}")
    print(f"✓ Decision: {result.decision}")
    print(f"✓ Data is normal: {result.decision == 'fail_to_reject'}")


def test_auto_suggestion():
    """Test auto test suggestion"""
    print("\n=== Testing Auto Test Suggestion ===")

    loader = DatasetLoader()
    suggester = TestSuggester()

    # Test with sales data (single sample)
    sales_data = loader.load_dataset('sales_example')
    data = loader.get_data_array(sales_data)
    suggestion = suggester.suggest_test(data, mu0=5000)

    print(f"✓ Suggested test: {suggestion['test_name']}")
    print(f"✓ Reason: {suggestion['reason']}")
    print(f"✓ Confidence: {suggestion['confidence']}")

    # Test with website data (paired)
    website_data = loader.load_dataset('website_redesign')
    data_dict = loader.get_data_array(website_data)
    suggestion2 = suggester.suggest_test(data_dict['before'], data_dict['after'])

    print(f"✓ Suggested test for paired data: {suggestion2['test_name']}")
    print(f"✓ Reason: {suggestion2['reason']}")


def test_cache_manager():
    """Test cache manager"""
    print("\n=== Testing Cache Manager ===")

    cache = CacheManager()

    # Create test result
    test_result = {
        "test_name": "Test",
        "p_value": 0.042,
        "decision": "reject"
    }

    # Cache it
    cache_id = cache.cache_result("test_type", test_result)
    print(f"✓ Cached result with ID: {cache_id}")

    # Retrieve it
    retrieved = cache.get_result(cache_id)
    print(f"✓ Retrieved result: p_value={retrieved['p_value']}")

    # List cached tests
    cached_tests = cache.list_cached_tests()
    print(f"✓ Total cached tests: {len(cached_tests)}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING MCP HYPOTHESIS TESTER IMPLEMENTATION")
    print("=" * 60)

    try:
        test_dataset_loading()
        test_one_sample_t_test()
        test_paired_t_test()
        test_normality_test()
        test_auto_suggestion()
        test_cache_manager()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
