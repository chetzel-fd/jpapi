#!/usr/bin/env python3
"""
Analyzer Data Provider
Reuses data loading logic from jpapi_manager
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from analyzer_interfaces import DataProvider

# Reuse existing data loader from jpapi_manager
from data_loader import FileDataLoader
from ui_utils import normalize_environment


class AnalyzerDataProvider(DataProvider):
    """Data provider that reuses jpapi_manager's data loading infrastructure"""

    def __init__(self):
        self.file_loader = FileDataLoader()
        self._data_cache: Dict[str, pd.DataFrame] = {}
        self._current_environment = "sandbox"

    def load_objects(self, obj_type: str, environment: str) -> pd.DataFrame:
        """Load objects of specific type for environment"""
        # Normalize environment name
        normalized_env = normalize_environment(environment)

        # Check cache
        cache_key = f"{obj_type}_{normalized_env}"
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]

        # Load data using FileDataLoader from jpapi_manager
        try:
            data = self.file_loader.load_data(obj_type, normalized_env)

            # Cache the data
            if not data.empty:
                self._data_cache[cache_key] = data

            return data
        except Exception as e:
            print(f"Error loading {obj_type} for {normalized_env}: {e}")
            return pd.DataFrame()

    def get_all_object_types(self) -> List[str]:
        """Get list of all available object types"""
        # These are the object types we support
        return ["policies", "profiles", "groups", "scripts", "packages", "searches"]

    def get_object_by_id(self, obj_type: str, obj_id: str) -> Optional[Dict[str, Any]]:
        """Get single object by type and ID"""
        try:
            # Load all objects of this type
            objects_df = self.load_objects(obj_type, self._current_environment)

            if objects_df.empty:
                return None

            # Find object by ID
            # Handle different ID column formats
            if "ID" in objects_df.columns:
                # Extract ID from hyperlink if needed
                matching_rows = objects_df[
                    objects_df["ID"].apply(lambda x: self._extract_id(x) == str(obj_id))
                ]
            else:
                return None

            if len(matching_rows) > 0:
                return matching_rows.iloc[0].to_dict()

            return None
        except Exception as e:
            print(f"Error getting object {obj_type}:{obj_id}: {e}")
            return None

    def reload_data(self, obj_type: Optional[str] = None) -> bool:
        """Reload data from source"""
        try:
            if obj_type:
                # Reload specific type
                cache_keys = [
                    k for k in self._data_cache.keys() if k.startswith(f"{obj_type}_")
                ]
                for key in cache_keys:
                    del self._data_cache[key]
            else:
                # Reload all
                self._data_cache.clear()

            return True
        except Exception as e:
            print(f"Error reloading data: {e}")
            return False

    def set_environment(self, environment: str):
        """Set current environment for data loading"""
        self._current_environment = normalize_environment(environment)

    def get_environment(self) -> str:
        """Get current environment"""
        return self._current_environment

    def _extract_id(self, id_value: Any) -> str:
        """Extract ID from various formats (including hyperlinks)"""
        if pd.isna(id_value):
            return ""

        id_str = str(id_value)

        # Handle Excel hyperlink format: =HYPERLINK("url", "123")
        if "=HYPERLINK(" in id_str:
            import re

            match = re.search(r'=HYPERLINK\("[^"]*",\s*"(\d+)"\)', id_str)
            if match:
                return match.group(1)

        # Handle HTML hyperlink format: <a href="...">123</a>
        if "<a href=" in id_str:
            import re

            match = re.search(r">(\d+)<", id_str)
            if match:
                return match.group(1)

        # Plain ID
        return id_str.strip()

    def get_object_count(self, obj_type: str, environment: Optional[str] = None) -> int:
        """Get count of objects for a specific type"""
        env = environment or self._current_environment
        objects_df = self.load_objects(obj_type, env)
        return len(objects_df)

    def get_all_objects_summary(
        self, environment: Optional[str] = None
    ) -> Dict[str, int]:
        """Get count summary for all object types"""
        env = environment or self._current_environment
        summary = {}

        for obj_type in self.get_all_object_types():
            try:
                count = self.get_object_count(obj_type, env)
                summary[obj_type] = count
            except Exception:
                summary[obj_type] = 0

        return summary
