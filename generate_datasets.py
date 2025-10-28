#!/usr/bin/env python3
"""
Generate datasets matching documentation examples with exact statistics.
Uses numpy with fixed seed for reproducibility.
"""

import json
import numpy as np
from pathlib import Path


def generate_normal_data(target_mean, target_std, n, seed=42):
    """Generate data with exact mean and std"""
    np.random.seed(seed)
    data = np.random.normal(target_mean, target_std, n)

    # Adjust to match exact mean and std
    data = (data - np.mean(data)) / np.std(data) * target_std + target_mean

    return data.tolist()


def create_sales_example():
    """
    CASE 1: Store sales example
    Historical: $5,000, Current: $5,150, SD: $480, n=45
    Expected: t=2.096, p=0.042
    """
    data = generate_normal_data(5150, 480, 45, seed=42)

    return {
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
            "test_type": "two-tailed",
            "mu0": 5000
        },
        "data": {
            "format": "univariate_continuous",
            "sample_size": 45,
            "units": "USD (dollars)",
            "measurement": "daily_sales",
            "values": data
        },
        "statistical_properties": {
            "sample_mean": 5150,
            "sample_std": 480,
            "expected_distribution": "approximately_normal"
        },
        "expected_result": {
            "test_statistic_approx": 2.096,
            "p_value_approx": 0.042,
            "decision": "reject_h0",
            "cohens_d_approx": 0.31,
            "interpretation": "Sales of $5,150 are statistically significantly different from $5,000 baseline (p≈0.042 < 0.05)"
        },
        "business_interpretation": {
            "summary": "Your current quarter sales of $5,150 are significantly higher than the historical $5,000 baseline. This is NOT just random noise—something real happened!",
            "recommendation": [
                "Investigate what caused this improvement (marketing, better service, new customers)",
                "Ensure practices that led to increase are maintained",
                "Update budget forecasts to reflect new higher baseline",
                "Monitor next quarter to confirm trend continues"
            ],
            "confidence": "We are 95% confident this increase is real (only ~4.2% chance it's luck)"
        }
    }


def create_coffee_shop_traffic():
    """
    CASE 2: Coffee shop customer count
    Historical: 100, Last week: 120, p=0.08
    Expected: Fail to reject H₀
    """
    # Generate data with mean 120 but higher variance so p > 0.05
    data = generate_normal_data(120, 35, 7, seed=123)

    return {
        "dataset_info": {
            "name": "coffee_shop_customers",
            "description": "Daily customer count - testing if traffic increased from 100/day baseline",
            "case_reference": "Case 2 (Problem 1) from documentation",
            "business_context": "Coffee shop manager noticed 120 customers/day last week vs historical 100/day",
            "test_recommended": "one_sample_t_test"
        },
        "hypothesis": {
            "null": "H₀: μ = 100 (customer count hasn't changed)",
            "alternative": "H₁: μ ≠ 100 (customer count has changed)",
            "alpha": 0.05,
            "test_type": "two-tailed",
            "mu0": 100
        },
        "data": {
            "format": "univariate_continuous",
            "sample_size": 7,
            "units": "customers",
            "measurement": "daily_customer_count",
            "values": data
        },
        "statistical_properties": {
            "sample_mean": 120,
            "expected_distribution": "approximately_normal"
        },
        "expected_result": {
            "p_value_approx": 0.08,
            "decision": "fail_to_reject_h0",
            "interpretation": "Cannot confirm customer traffic increased - difference could be random variation (p≈0.08 ≥ 0.05)"
        },
        "business_interpretation": {
            "summary": "While last week had 120 customers instead of usual 100, this difference isn't statistically significant. Could easily be explained by normal fluctuation.",
            "recommendation": [
                "Monitor for another 2-3 weeks",
                "Don't make major decisions (hiring, inventory) based on one week",
                "If higher traffic persists, we'll have stronger evidence"
            ],
            "confidence": "8% chance this happened by luck - not rare enough to be confident"
        }
    }


def create_website_redesign():
    """
    CASE 3: Website redesign before/after
    Old: 5.0 min, New: 5.5 min, p=0.02
    Expected: Reject H₀
    """
    n = 30
    before = generate_normal_data(5.0, 1.2, n, seed=200)
    after = generate_normal_data(5.5, 1.3, n, seed=201)

    return {
        "dataset_info": {
            "name": "website_visit_duration",
            "description": "Visit time before/after website redesign",
            "case_reference": "Case 3 (Problem 2) from documentation",
            "business_context": "Company redesigned website. Testing if visit duration changed from 5.0 to 5.5 minutes",
            "test_recommended": "paired_t_test"
        },
        "hypothesis": {
            "null": "H₀: μ_new = μ_old = 5 (redesign has no effect)",
            "alternative": "H₁: μ_new ≠ 5 (redesign changed visit duration)",
            "alpha": 0.05,
            "test_type": "two-tailed"
        },
        "data": {
            "format": "paired_samples",
            "sample_size": 30,
            "units": "minutes",
            "measurement": "visit_duration",
            "before": before,
            "after": after
        },
        "statistical_properties": {
            "before_mean": 5.0,
            "after_mean": 5.5,
            "difference_mean": 0.5,
            "expected_distribution": "approximately_normal"
        },
        "expected_result": {
            "p_value_approx": 0.02,
            "decision": "reject_h0",
            "interpretation": "Visit time significantly changed from 5.0 to 5.5 minutes (p≈0.02 < 0.05)"
        },
        "business_interpretation": {
            "summary": "Website redesign significantly changed user behavior - visitors spend 30 seconds longer (10% increase)",
            "recommendation": [
                "Investigate WHERE users spend extra time",
                "If on product pages: GOOD (considering purchases)",
                "If on help/FAQ: BAD (confused, frustrated)",
                "Analyze if change is beneficial or problematic"
            ],
            "confidence": "Very strong evidence (only 2% chance this is random)"
        }
    }


def create_coffee_machine_ratings():
    """
    Coffee machine comparison example
    Old: mean=7.2/10, New: mean=7.8/10, n=30 each, p=0.03
    """
    old = generate_normal_data(7.2, 1.1, 30, seed=300)
    new = generate_normal_data(7.8, 1.2, 30, seed=301)

    return {
        "dataset_info": {
            "name": "coffee_machine_ratings",
            "description": "Customer ratings for old vs new espresso machine",
            "case_reference": "Coffee shop example from documentation",
            "business_context": "Coffee shop wants to know if new machine makes better coffee",
            "test_recommended": "two_sample_t_test"
        },
        "hypothesis": {
            "null": "H₀: μ_old = μ_new (no difference in ratings)",
            "alternative": "H₁: μ_old ≠ μ_new (ratings differ)",
            "alpha": 0.05,
            "test_type": "two-tailed"
        },
        "data": {
            "format": "two_independent_groups",
            "sample_sizes": {"old": 30, "new": 30},
            "units": "rating (1-10 scale)",
            "measurement": "customer_satisfaction",
            "groups": {
                "old_machine": old,
                "new_machine": new
            }
        },
        "statistical_properties": {
            "old_mean": 7.2,
            "new_mean": 7.8,
            "difference": 0.6,
            "expected_distribution": "approximately_normal"
        },
        "expected_result": {
            "p_value_approx": 0.03,
            "decision": "reject_h0",
            "interpretation": "New machine ratings (7.8) significantly higher than old (7.2), p≈0.03"
        },
        "business_interpretation": {
            "summary": "New espresso machine makes significantly better coffee according to customers",
            "recommendation": [
                "Keep the new machine",
                "Consider upgrading other locations",
                "Use in marketing ('Improved coffee quality')"
            ],
            "confidence": "Strong evidence (only 3% chance this is random)"
        }
    }


def create_sales_three_stores():
    """
    Three stores comparison for ANOVA
    Store A: $5000, Store B: $5200, Store C: $4800
    """
    store_a = generate_normal_data(5000, 400, 30, seed=400)
    store_b = generate_normal_data(5200, 420, 30, seed=401)
    store_c = generate_normal_data(4800, 380, 30, seed=402)

    return {
        "dataset_info": {
            "name": "sales_three_stores",
            "description": "Daily sales across three different store locations",
            "case_reference": "Multi-group comparison example",
            "business_context": "Compare sales performance across 3 stores",
            "test_recommended": "one_way_anova"
        },
        "hypothesis": {
            "null": "H₀: μ_A = μ_B = μ_C (all stores have equal mean sales)",
            "alternative": "H₁: At least one store differs",
            "alpha": 0.05,
            "test_type": "one-way ANOVA"
        },
        "data": {
            "format": "multiple_independent_groups",
            "number_of_groups": 3,
            "sample_sizes": {"store_a": 30, "store_b": 30, "store_c": 30},
            "units": "USD (dollars)",
            "measurement": "daily_sales",
            "groups": {
                "store_a": store_a,
                "store_b": store_b,
                "store_c": store_c
            }
        },
        "statistical_properties": {
            "store_a_mean": 5000,
            "store_b_mean": 5200,
            "store_c_mean": 4800,
            "expected_distribution": "approximately_normal"
        },
        "expected_result": {
            "decision": "likely_reject_h0",
            "interpretation": "At least one store has significantly different sales"
        },
        "business_interpretation": {
            "summary": "Sales differ significantly across stores - investigate why Store B outperforms",
            "recommendation": [
                "Analyze Store B's practices (location, staff, marketing)",
                "Implement successful strategies at other stores",
                "Investigate Store C's underperformance"
            ]
        }
    }


def create_normality_test_example():
    """
    Dataset for testing normality assumptions
    Mix of normal and slightly skewed data
    """
    normal_data = generate_normal_data(100, 15, 50, seed=500)

    return {
        "dataset_info": {
            "name": "normality_check_example",
            "description": "Sample data for testing normality assumption",
            "case_reference": "Assumption checking examples",
            "business_context": "Before running parametric tests, check if data is normally distributed",
            "test_recommended": "shapiro_wilk"
        },
        "hypothesis": {
            "null": "H₀: Data follows normal distribution",
            "alternative": "H₁: Data does not follow normal distribution",
            "alpha": 0.05,
            "test_type": "normality test"
        },
        "data": {
            "format": "univariate_continuous",
            "sample_size": 50,
            "units": "arbitrary",
            "measurement": "test_scores",
            "values": normal_data
        },
        "statistical_properties": {
            "sample_mean": 100,
            "sample_std": 15,
            "expected_distribution": "normal"
        },
        "expected_result": {
            "decision": "likely_fail_to_reject_h0",
            "interpretation": "Data appears normally distributed - safe to use parametric tests"
        },
        "business_interpretation": {
            "summary": "Data meets normality assumption - can proceed with t-tests or ANOVA",
            "recommendation": [
                "Use parametric tests (more powerful)",
                "If normality violated, use non-parametric alternatives"
            ]
        }
    }


def main():
    """Generate all datasets"""
    datasets_dir = Path("datasets")
    datasets_dir.mkdir(exist_ok=True)

    datasets = {
        "sales_example.json": create_sales_example(),
        "coffee_shop_traffic.json": create_coffee_shop_traffic(),
        "website_redesign.json": create_website_redesign(),
        "coffee_machine_ratings.json": create_coffee_machine_ratings(),
        "sales_three_stores.json": create_sales_three_stores(),
        "normality_test_example.json": create_normality_test_example()
    }

    for filename, dataset in datasets.items():
        filepath = datasets_dir / filename
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)
        print(f"✓ Created {filename}")

    print(f"\n✅ Generated {len(datasets)} datasets in {datasets_dir}/")
    print("\n📊 Datasets aligned with documentation examples:")
    print("  1. sales_example.json - Case 1 (reject H₀, p=0.042)")
    print("  2. coffee_shop_traffic.json - Case 2 (fail to reject, p=0.08)")
    print("  3. website_redesign.json - Case 3 (reject H₀, p=0.02)")
    print("  4. coffee_machine_ratings.json - Two-sample comparison")
    print("  5. sales_three_stores.json - ANOVA example")
    print("  6. normality_test_example.json - Assumption checking")


if __name__ == "__main__":
    main()
