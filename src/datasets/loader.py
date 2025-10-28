"""
Dataset loader for hypothesis testing
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List


class DatasetLoader:
    """Load and manage datasets for hypothesis testing"""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = Path(datasets_dir)

    def load_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Load dataset from JSON file.

        Args:
            dataset_name: Name of dataset (with or without .json extension)

        Returns:
            Dictionary containing dataset information and data
        """
        # Handle .json extension
        if not dataset_name.endswith('.json'):
            dataset_name = f"{dataset_name}.json"

        filepath = self.datasets_dir / dataset_name

        if not filepath.exists():
            raise FileNotFoundError(f"Dataset not found: {filepath}")

        with open(filepath, 'r') as f:
            dataset = json.load(f)

        return dataset

    def get_data_array(self, dataset: Dict[str, Any]) -> np.ndarray:
        """
        Extract data array from dataset dictionary.

        Handles different data formats:
        - Single array: dataset['data']['values']
        - Paired data: dataset['data']['before'] and dataset['data']['after']
        - Grouped data: dataset['data']['groups']['group1'], etc.
        """
        data_section = dataset.get('data', {})

        # Single sample
        if 'values' in data_section:
            return np.array(data_section['values'])

        # Paired samples
        elif 'before' in data_section and 'after' in data_section:
            return {
                'before': np.array(data_section['before']),
                'after': np.array(data_section['after'])
            }

        # Multiple groups
        elif 'groups' in data_section:
            groups = {}
            for group_name, group_data in data_section['groups'].items():
                groups[group_name] = np.array(group_data)
            return groups

        else:
            raise ValueError(f"Unsupported data format in dataset")

    def list_datasets(self) -> List[str]:
        """List all available datasets"""
        if not self.datasets_dir.exists():
            return []

        datasets = []
        for file in self.datasets_dir.glob('*.json'):
            datasets.append(file.stem)

        return sorted(datasets)

    def get_dataset_info(self, dataset_name: str) -> Dict[str, Any]:
        """Get metadata about dataset without loading full data"""
        dataset = self.load_dataset(dataset_name)

        return {
            "name": dataset.get('dataset_info', {}).get('name', dataset_name),
            "description": dataset.get('dataset_info', {}).get('description', ''),
            "test_recommended": dataset.get('dataset_info', {}).get('test_recommended', ''),
            "case_reference": dataset.get('dataset_info', {}).get('case_reference', ''),
            "hypothesis": dataset.get('hypothesis', {}),
            "sample_size": dataset.get('data', {}).get('sample_size', 'unknown')
        }
