"""
Cache manager for storing detailed test results in temporary JSON files.
Prevents large data from being passed through MCP protocol.
"""

import json
import os
import tempfile
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path


class CacheManager:
    """
    Manages temporary JSON cache for detailed test results.

    Why?
    - MCP has message size limits
    - LLMs don't need raw data, just summaries
    - Allows retrieval of detailed results on demand

    Cache structure:
    /tmp/mcp-hypothesis-cache/
        ├── test_results/
        │   ├── {test_id}.json          # Full test results
        │   └── {test_id}_data.json     # Raw data (if needed)
        └── index.json                  # Cache index
    """

    def __init__(self, cache_dir: Optional[str] = None, ttl_hours: int = 24):
        """
        Initialize cache manager.

        Args:
            cache_dir: Custom cache directory (default: system temp)
            ttl_hours: Time-to-live for cache entries (default: 24 hours)
        """
        if cache_dir is None:
            cache_dir = os.path.join(tempfile.gettempdir(), "mcp-hypothesis-cache")

        self.cache_dir = Path(cache_dir)
        self.test_results_dir = self.cache_dir / "test_results"
        self.index_file = self.cache_dir / "index.json"
        self.ttl = timedelta(hours=ttl_hours)

        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.test_results_dir.mkdir(exist_ok=True)

        # Load or create index
        self._load_index()
        self._cleanup_expired()

    def _load_index(self):
        """Load cache index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.index = {"entries": {}, "last_cleanup": None}
                self._save_index()
        else:
            self.index = {"entries": {}, "last_cleanup": None}
            self._save_index()

    def _save_index(self):
        """Save cache index"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save cache index: {e}")

    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = datetime.now()
        expired_ids = []

        for test_id, entry in self.index["entries"].items():
            try:
                created = datetime.fromisoformat(entry["created"])
                if current_time - created > self.ttl:
                    expired_ids.append(test_id)
            except (KeyError, ValueError):
                # Invalid entry, mark for deletion
                expired_ids.append(test_id)

        for test_id in expired_ids:
            self.delete_result(test_id)

        self.index["last_cleanup"] = current_time.isoformat()
        self._save_index()

    def generate_test_id(self, test_type: str, params: Dict) -> str:
        """Generate unique test ID based on type and timestamp"""
        hash_input = f"{test_type}_{datetime.now().isoformat()}_{id(params)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def cache_result(self, test_type: str, test_result: Dict[str, Any],
                    raw_data: Optional[Dict] = None) -> str:
        """
        Cache test result with optional raw data.

        Args:
            test_type: Type of test
            test_result: Test result dictionary
            raw_data: Optional raw data arrays

        Returns:
            test_id: Unique identifier for cached result
        """
        test_id = self.generate_test_id(test_type, test_result)

        try:
            # Save main result
            result_file = self.test_results_dir / f"{test_id}.json"
            with open(result_file, 'w') as f:
                json.dump(test_result, f, indent=2)

            # Save raw data separately if provided
            data_file_path = None
            if raw_data:
                data_file = self.test_results_dir / f"{test_id}_data.json"
                # Convert numpy arrays to lists for JSON serialization
                serializable_data = self._make_serializable(raw_data)
                with open(data_file, 'w') as f:
                    json.dump(serializable_data, f, indent=2)
                data_file_path = str(data_file)

            # Update index
            self.index["entries"][test_id] = {
                "test_type": test_type,
                "created": datetime.now().isoformat(),
                "has_raw_data": raw_data is not None,
                "result_file": str(result_file),
                "data_file": data_file_path
            }
            self._save_index()

            return test_id

        except (IOError, OSError) as e:
            print(f"Warning: Failed to cache result: {e}")
            return f"cache_error_{test_id}"

    def _make_serializable(self, obj: Any) -> Any:
        """Convert numpy arrays and other non-serializable objects to JSON-compatible types"""
        import numpy as np

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj

    def get_result(self, test_id: str, include_raw_data: bool = False) -> Optional[Dict]:
        """
        Retrieve cached result.

        Args:
            test_id: Test identifier
            include_raw_data: Whether to include raw data

        Returns:
            Cached result dictionary or None if not found
        """
        if test_id not in self.index["entries"]:
            return None

        entry = self.index["entries"][test_id]

        try:
            # Load main result
            result_file = Path(entry["result_file"])
            if not result_file.exists():
                return None

            with open(result_file, 'r') as f:
                result = json.load(f)

            # Load raw data if requested
            if include_raw_data and entry["has_raw_data"] and entry["data_file"]:
                data_file = Path(entry["data_file"])
                if data_file.exists():
                    with open(data_file, 'r') as f:
                        result["raw_data"] = json.load(f)

            return result

        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to retrieve cached result: {e}")
            return None

    def delete_result(self, test_id: str):
        """Delete cached result"""
        if test_id not in self.index["entries"]:
            return

        entry = self.index["entries"][test_id]

        try:
            # Delete files
            result_file = Path(entry["result_file"])
            if result_file.exists():
                result_file.unlink()

            if entry["has_raw_data"] and entry["data_file"]:
                data_file = Path(entry["data_file"])
                if data_file.exists():
                    data_file.unlink()

        except OSError as e:
            print(f"Warning: Failed to delete cache files: {e}")

        # Remove from index
        del self.index["entries"][test_id]
        self._save_index()

    def list_cached_tests(self) -> List[Dict]:
        """List all cached tests with metadata"""
        tests = []
        for test_id, entry in self.index["entries"].items():
            tests.append({
                "test_id": test_id,
                "test_type": entry["test_type"],
                "created": entry["created"],
                "has_raw_data": entry["has_raw_data"]
            })
        return sorted(tests, key=lambda x: x["created"], reverse=True)

    def clear_all(self):
        """Clear all cached results"""
        test_ids = list(self.index["entries"].keys())
        for test_id in test_ids:
            self.delete_result(test_id)
