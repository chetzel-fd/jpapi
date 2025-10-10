"""
Scalable Data Loader - Configuration-Driven Data Loading
Eliminates repetitive patterns and enables easy scaling for new object types
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
from ..config.object_type_manager import ObjectTypeManager


class ScalableDataLoader:
    """Configuration-driven data loader that scales automatically"""

    def __init__(self, config_path: str = "core/config/object_types.json"):
        self.object_manager = ObjectTypeManager(config_path)
        self.csv_dir = Path("storage/data/csv-exports")
        self.csv_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, object_type: str, environment: str = "sandbox") -> pd.DataFrame:
        """Load data for any object type using configuration"""
        try:
            # Find CSV files using configuration patterns
            files = self.object_manager.find_csv_files(
                object_type, environment, self.csv_dir
            )

            if not files:
                st.warning(
                    f"⚠️ No {object_type} files found for {environment} environment"
                )
                st.info("💡 Click 'Gather Data' to export fresh data from JAMF Pro")
                return self.object_manager.get_sample_data(object_type)

            # Get the most recent file
            latest_file = max(files, key=lambda x: x.stat().st_mtime)

            # Load the CSV
            df = pd.read_csv(latest_file)

            # Standardize the dataframe
            df = self.object_manager.standardize_dataframe(df, object_type)

            st.success(f"✅ Loaded {len(df)} {object_type} from {latest_file.name}")
            return df

        except Exception as e:
            st.error(f"Error loading {object_type} data: {e}")
            return self.object_manager.get_sample_data(object_type)

    def build_export_command(
        self, object_type: str, environment: str, format_type: str = "csv"
    ) -> List[str]:
        """Build export command using configuration - eliminates repetitive if/elif chains"""
        return self.object_manager.build_jpapi_command(
            object_type, environment, format_type
        )

    def get_object_type_info(self, object_type: str) -> Dict[str, Any]:
        """Get object type information for UI display"""
        return self.object_manager.get_object_type_info(object_type)

    def get_available_object_types(self) -> List[str]:
        """Get list of available object types"""
        return self.object_manager.get_available_object_types()

    def add_new_object_type(self, object_type: str, config: Dict[str, Any]) -> bool:
        """Add new object type - enables easy scaling"""
        return self.object_manager.add_new_object_type(object_type, config)

    def validate_data(self, df: pd.DataFrame, object_type: str) -> bool:
        """Validate that data has required columns"""
        required_columns = self.object_manager.get_required_columns(object_type)
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.warning(f"Missing required columns: {missing_columns}")
            return False

        return True

    def get_sample_data_for_object_type(self, object_type: str) -> pd.DataFrame:
        """Get sample data for object type"""
        return self.object_manager.get_sample_data(object_type)

    def get_file_patterns_for_object_type(
        self, object_type: str, environment: str
    ) -> List[str]:
        """Get file patterns for object type"""
        return self.object_manager.get_file_patterns(object_type, environment)

    def find_latest_file_for_object_type(
        self, object_type: str, environment: str
    ) -> Optional[Path]:
        """Find the latest CSV file for object type"""
        files = self.object_manager.find_csv_files(
            object_type, environment, self.csv_dir
        )

        if not files:
            return None

        return max(files, key=lambda x: x.stat().st_mtime)

    def get_data_summary(self, object_type: str, environment: str) -> Dict[str, Any]:
        """Get data summary for object type"""
        latest_file = self.find_latest_file_for_object_type(object_type, environment)

        if latest_file:
            try:
                df = pd.read_csv(latest_file)
                return {
                    "file_name": latest_file.name,
                    "file_size": latest_file.stat().st_size,
                    "record_count": len(df),
                    "columns": list(df.columns),
                    "last_modified": latest_file.stat().st_mtime,
                }
            except Exception as e:
                return {"error": str(e)}

        return {"error": "No data file found"}
