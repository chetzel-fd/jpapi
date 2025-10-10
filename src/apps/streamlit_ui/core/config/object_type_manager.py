"""
Object Type Manager - Configuration-Driven Scalability
Manages object type configurations and eliminates repetitive code patterns
"""

import json
import streamlit as st
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd


class ObjectTypeManager:
    """Configuration-driven object type manager for maximum scalability"""

    def __init__(
        self, config_path: str = "src/apps/streamlit_ui/core/config/object_types.json"
    ):
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load object type configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    return json.load(f)
            else:
                st.error(f"Configuration file not found: {self.config_path}")
                return {"object_types": {}}
        except Exception as e:
            st.error(f"Error loading configuration: {e}")
            return {"object_types": {}}

    def get_available_object_types(self) -> List[str]:
        """Get list of all available object types"""
        return list(self._config.get("object_types", {}).keys())

    def get_object_type_config(self, object_type: str) -> Dict[str, Any]:
        """Get configuration for a specific object type"""
        return self._config.get("object_types", {}).get(object_type, {})

    def get_display_name(self, object_type: str) -> str:
        """Get display name for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("display_name", object_type.title())

    def get_icon(self, object_type: str) -> str:
        """Get icon for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("icon", "📄")

    def get_description(self, object_type: str) -> str:
        """Get description for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("description", "")

    def get_jpapi_command(self, object_type: str) -> str:
        """Get JPAPI command for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("jpapi_command", object_type)

    def get_file_patterns(
        self, object_type: str, environment: str = "sandbox"
    ) -> List[str]:
        """Get file patterns for object type with environment substitution"""
        config = self.get_object_type_config(object_type)
        patterns = config.get("file_patterns", [])

        # Replace {environment} placeholder with actual environment
        return [pattern.format(environment=environment) for pattern in patterns]

    def get_required_columns(self, object_type: str) -> List[str]:
        """Get required columns for object type"""
        config = self.get_object_type_config(object_type)
        return config.get(
            "required_columns", ["Name", "ID", "Type", "Status", "Last Modified"]
        )

    def get_sample_data(self, object_type: str) -> pd.DataFrame:
        """Get sample data for object type"""
        config = self.get_object_type_config(object_type)
        sample_data = config.get("sample_data", {})

        if sample_data:
            df = pd.DataFrame(sample_data)
            # Mark as sample data
            if "Name" in df.columns:
                df["Name"] = "Sample " + df["Name"].astype(str)
            return df
        else:
            # Fallback sample data
            return pd.DataFrame(
                {
                    "Name": [f"Sample {object_type.title()} {i}" for i in range(1, 6)],
                    "ID": [1000 + i for i in range(1, 6)],
                    "Type": [object_type.title()] * 5,
                    "Status": ["Active", "Active", "Draft", "Active", "Active"],
                    "Last Modified": [
                        "2024-01-15",
                        "2024-01-14",
                        "2024-01-13",
                        "2024-01-12",
                        "2024-01-11",
                    ],
                }
            )

    def build_jpapi_command(
        self, object_type: str, environment: str, format_type: str = "csv"
    ) -> List[str]:
        """Build JPAPI command for object type - eliminates repetitive if/elif chains"""
        jpapi_command = self.get_jpapi_command(object_type)

        return [
            "python3",
            "src/jpapi_main.py",
            "--env",
            environment,
            "export",
            jpapi_command,
            "--format",
            format_type,
        ]

    def find_csv_files(
        self, object_type: str, environment: str, csv_dir: Path
    ) -> List[Path]:
        """Find CSV files for object type using configuration patterns"""
        patterns = self.get_file_patterns(object_type, environment)
        files = []

        for pattern in patterns:
            found_files = list(csv_dir.glob(pattern))
            files.extend(found_files)

        # Remove duplicates
        return list(set(files))

    def standardize_dataframe(self, df: pd.DataFrame, object_type: str) -> pd.DataFrame:
        """Standardize dataframe columns based on object type requirements"""
        required_columns = self.get_required_columns(object_type)

        # Add missing columns with default values
        for col in required_columns:
            if col not in df.columns:
                if col == "Name":
                    df[col] = f"Sample {object_type.title()}"
                elif col == "ID":
                    df[col] = range(1001, 1001 + len(df))
                elif col == "Type":
                    df[col] = object_type.title()
                elif col == "Status":
                    df[col] = "Active"
                elif col == "Last Modified":
                    df[col] = "2024-01-15"

        return df

    def add_new_object_type(self, object_type: str, config: Dict[str, Any]) -> bool:
        """Add new object type configuration - enables easy scaling"""
        try:
            if "object_types" not in self._config:
                self._config["object_types"] = {}

            self._config["object_types"][object_type] = config

            # Save to file
            with open(self.config_path, "w") as f:
                json.dump(self._config, f, indent=2)

            return True
        except Exception as e:
            st.error(f"Error adding object type: {e}")
            return False

    def validate_object_type(self, object_type: str) -> bool:
        """Validate that object type has required configuration"""
        config = self.get_object_type_config(object_type)
        required_fields = ["display_name", "jpapi_command", "file_patterns"]

        return all(field in config for field in required_fields)

    def get_object_type_info(self, object_type: str) -> Dict[str, Any]:
        """Get comprehensive object type information"""
        config = self.get_object_type_config(object_type)
        return {
            "name": object_type,
            "display_name": config.get("display_name", object_type.title()),
            "icon": config.get("icon", "📄"),
            "description": config.get("description", ""),
            "jpapi_command": config.get("jpapi_command", object_type),
            "file_patterns": config.get("file_patterns", []),
            "required_columns": config.get("required_columns", []),
            "is_valid": self.validate_object_type(object_type),
        }
