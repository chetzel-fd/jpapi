"""
CSV Data Loader - Single Responsibility Principle
Handles CSV file discovery, loading, and environment filtering
"""

import os
import glob
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
from .interfaces import DataLoaderInterface, DataValidatorInterface
from ..config.settings import Settings


class CSVLoader(DataLoaderInterface):
    """CSV data loader implementation with environment filtering"""

    def __init__(self, validator: DataValidatorInterface, settings: Settings):
        self.validator = validator
        self.settings = settings
        self.csv_dirs = settings.CSV_EXPORT_DIRS
        self.object_types = settings.OBJECT_TYPES

    def load(self, object_type: str, environment: str) -> pd.DataFrame:
        """Load data for given object type and environment with proper filtering"""
        try:
            # Get available files
            files = self.get_available_files(object_type, environment)
            if not files:
                return self._get_sample_data(object_type)

            # Find the most recent file
            latest_file = self._find_latest_file(files)
            if not latest_file:
                return self._get_sample_data(object_type)

            # Load and validate data
            df = pd.read_csv(latest_file)
            if self.validator.validate(df):
                return df
            else:
                return self._get_sample_data(object_type)

        except Exception as e:
            print(f"Error loading data: {e}")
            return self._get_sample_data(object_type)

    def get_available_files(self, object_type: str, environment: str) -> List[str]:
        """Get list of available files for object type and environment"""
        files = []

        if object_type not in self.object_types:
            return files

        config = self.object_types[object_type]
        patterns = config.get("file_patterns", [])

        # Search in all configured directories
        for csv_dir in self.csv_dirs:
            if not os.path.exists(csv_dir):
                continue

            for pattern in patterns:
                # Replace {env} placeholder with actual environment
                env_pattern = pattern.format(env=environment)
                search_path = os.path.join(csv_dir, env_pattern)
                found_files = glob.glob(search_path)
                files.extend(found_files)

        return files

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate loaded data"""
        return self.validator.validate(df)

    def _find_latest_file(self, files: List[str]) -> Optional[str]:
        """Find the most recent file based on modification time"""
        if not files:
            return None

        return max(files, key=os.path.getmtime)

    def _get_sample_data(self, object_type: str) -> pd.DataFrame:
        """Get sample data when real data is not available"""
        sample_data = {
            "searches": {
                "Name": ["Sample Search 1", "Sample Search 2", "Sample Search 3"],
                "Smart": [True, False, True],
                "Status": ["Active", "Active", "Deleted"],
                "Modified": ["2024-01-15", "2024-01-14", "2024-01-13"],
            },
            "policies": {
                "Name": ["Sample Policy 1", "Sample Policy 2", "Sample Policy 3"],
                "Smart": [False, True, False],
                "Status": ["Active", "Active", "Deleted"],
                "Modified": ["2024-01-15", "2024-01-14", "2024-01-13"],
            },
        }

        if object_type in sample_data:
            return pd.DataFrame(sample_data[object_type])
        else:
            return pd.DataFrame(
                {
                    "Name": ["Sample Object"],
                    "Smart": [False],
                    "Status": ["Active"],
                    "Modified": ["2024-01-15"],
                }
            )
