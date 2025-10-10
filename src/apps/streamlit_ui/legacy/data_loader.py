#!/usr/bin/env python3
"""
Generic Data Loader for Object Manager
Handles loading, caching, and exporting for all object types
"""
import streamlit as st
import pandas as pd
import json
import glob
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from lib.exports.export_utils import (
    get_export_file_pattern,
    get_export_directory,
    get_instance_prefix,
)


@dataclass
class ObjectTypeConfig:
    """Configuration for an object type"""

    name: str
    icon: str
    description: str
    available_envs: List[str]
    csv_parser: Optional[str] = None  # Custom parser for complex CSV structures


class DataLoader:
    """Generic data loader for all object types"""

    # Object type configurations
    OBJECT_TYPES = {
        "advanced-searches": ObjectTypeConfig(
            name="Advanced Searches",
            icon="🔍",
            description="Search configurations and criteria",
            available_envs=["sandbox", "prod"],
        ),
        "policies": ObjectTypeConfig(
            name="Policies",
            icon="📋",
            description="Device management policies",
            available_envs=["sandbox"],
            csv_parser="json_general",  # Special parser for policies JSON structure
        ),
        "config-profiles": ObjectTypeConfig(
            name="Config Profiles",
            icon="⚙️",
            description="Configuration profiles for devices",
            available_envs=["sandbox", "prod"],
        ),
        "packages": ObjectTypeConfig(
            name="Packages",
            icon="📦",
            description="Software packages and installers",
            available_envs=["sandbox", "prod"],
        ),
        "smart-groups": ObjectTypeConfig(
            name="Smart Groups",
            icon="🧠",
            description="Dynamic device and user groups",
            available_envs=["sandbox", "prod"],
        ),
    }

    def __init__(self):
        """Initialize the data loader"""
        self._ensure_session_state()

    def _ensure_session_state(self):
        """Ensure required session state variables exist"""
        if "object_data_cache" not in st.session_state:
            st.session_state.object_data_cache = {}
        if "total_count" not in st.session_state:
            st.session_state.total_count = 0
        if "selected_count" not in st.session_state:
            st.session_state.selected_count = 0
        if "deleted_count" not in st.session_state:
            st.session_state.deleted_count = 0
        if "csv_errors" not in st.session_state:
            st.session_state.csv_errors = []
        if "csv_warnings" not in st.session_state:
            st.session_state.csv_warnings = []

        # Add some sample CSV loading status for demo
        if not st.session_state.csv_errors and not st.session_state.csv_warnings:
            st.session_state.csv_warnings = [
                "Policies export created successfully for sandbox",
                "Policy CSV has 2 malformed entries",
                "Advanced Search export completed with warnings",
            ]

    def get_object_type_config(self, object_type: str) -> ObjectTypeConfig:
        """Get configuration for an object type"""
        return self.OBJECT_TYPES.get(
            object_type, self.OBJECT_TYPES["advanced-searches"]
        )

    def get_available_object_types_for_env(self, environment: str) -> List[str]:
        """Get object types available in the given environment"""
        return [
            obj_type
            for obj_type, config in self.OBJECT_TYPES.items()
            if environment in config.available_envs
        ]

    def load_object_data(
        self,
        object_type: str,
        environment: str = "sandbox",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Load data for any object type with caching"""
        cache_key = f"{object_type}_{environment}"

        # Check cache first (unless force refresh)
        if not force_refresh and cache_key in st.session_state.object_data_cache:
            return st.session_state.object_data_cache[cache_key]

        # Load data based on object type
        if object_type == "advanced-searches":
            data = self._load_advanced_searches(environment)
        elif object_type == "policies":
            data = self._load_policies_data(environment)
        elif object_type == "config-profiles":
            data = self._load_config_profiles_data(environment)
        elif object_type == "packages":
            data = self._load_packages_data(environment)
        elif object_type == "smart-groups":
            data = self._load_smart_groups_data(environment)
        else:
            data = self._get_sample_data()

        # Cache the data
        st.session_state.object_data_cache[cache_key] = data
        return data

    def _load_advanced_searches(self, environment: str) -> pd.DataFrame:
        """Load advanced searches data"""
        try:
            with st.spinner(f"🔄 Loading advanced searches from {environment}..."):
                time.sleep(0.3)

            export_dir = get_export_directory(environment)
            file_pattern = get_export_file_pattern(
                "advanced-searches", "csv", environment
            )
            csv_files = glob.glob(str(export_dir / file_pattern))

            if not csv_files:
                st.warning(
                    f"⚠️ No advanced searches exports found for {environment} environment"
                )
                st.info("💡 Use the '📥 Create Export' button to generate fresh data")
                return self._get_sample_data()

            latest_file = sorted(csv_files)[-1]
            st.info(f"📁 Loading from: `{os.path.basename(latest_file)}`")

            df = pd.read_csv(latest_file)
            data = {
                "Name": df["Name"].tolist(),
                "ID": df["ID"].tolist(),
                "Type": ["Advanced Search"] * len(df),
            }

            st.success(
                f"✅ Loaded {len(data['Name'])} advanced searches from {environment}"
            )
            return pd.DataFrame(data)

        except Exception as e:
            st.error(f"❌ Error loading advanced searches: {e}")
            return self._get_sample_data()

    def _load_policies_data(self, environment: str) -> pd.DataFrame:
        """Load policies data with JSON parsing"""
        try:
            with st.spinner(f"🔄 Loading policies from {environment}..."):
                time.sleep(0.3)

            export_dir = get_export_directory(environment)
            file_pattern = get_export_file_pattern("policies", "csv", environment)
            csv_files = glob.glob(str(export_dir / file_pattern))

            if not csv_files:
                # Try to create an export automatically
                if self.create_object_export("policies", environment):
                    csv_files = glob.glob(str(export_dir / file_pattern))
                    if not csv_files:
                        return self._get_sample_policies_data()
                else:
                    return self._get_sample_policies_data()

            latest_file = sorted(csv_files)[-1]

            # Load and process the CSV with proper handling of JSON data
            df = pd.read_csv(latest_file, quotechar='"', escapechar="\\")

            # Extract policy names and IDs from the JSON data in the 'general' column
            names = []
            ids = []

            for _, row in df.iterrows():
                try:
                    # Parse the JSON in the 'general' column
                    general_data = json.loads(row["general"])
                    policy_name = general_data.get("name", {}).get(
                        "text", "Unknown Policy"
                    )
                    policy_id = general_data.get("id", {}).get("text", "Unknown ID")

                    names.append(policy_name)
                    ids.append(policy_id)
                except (json.JSONDecodeError, KeyError, AttributeError):
                    # Fallback if JSON parsing fails
                    names.append(f"Policy {len(names) + 1}")
                    ids.append(f"ID{len(ids) + 1}")

            data = {
                "Name": names,
                "ID": ids,
                "Type": ["Policy"] * len(names),
            }

            return pd.DataFrame(data)

        except Exception as e:
            st.error(f"❌ Error loading policies: {e}")
            return self._get_sample_policies_data()

    def _load_config_profiles_data(self, environment: str) -> pd.DataFrame:
        """Load config profiles data"""
        return self._load_generic_object_data(
            "config-profiles", environment, "Config Profile"
        )

    def _load_packages_data(self, environment: str) -> pd.DataFrame:
        """Load packages data"""
        return self._load_generic_object_data("packages", environment, "Package")

    def _load_smart_groups_data(self, environment: str) -> pd.DataFrame:
        """Load smart groups data"""
        return self._load_generic_object_data(
            "smart-groups", environment, "Smart Group"
        )

    def _load_generic_object_data(
        self, object_type: str, environment: str, type_name: str
    ) -> pd.DataFrame:
        """Generic loader for simple CSV structures"""
        try:
            with st.spinner(f"🔄 Loading {object_type} from {environment}..."):
                time.sleep(0.3)

            export_dir = get_export_directory(environment)
            file_pattern = get_export_file_pattern(object_type, "csv", environment)
            csv_files = glob.glob(str(export_dir / file_pattern))

            if not csv_files:
                st.warning(
                    f"⚠️ No {object_type} exports found for {environment} environment"
                )
                st.info("💡 Use the '📥 Export' button to generate fresh data")
                if self.create_object_export(object_type, environment):
                    csv_files = glob.glob(str(export_dir / file_pattern))
                    if not csv_files:
                        return self._get_sample_data()
                else:
                    return self._get_sample_data()

            latest_file = sorted(csv_files)[-1]
            st.info(f"📁 Loading from: `{os.path.basename(latest_file)}`")

            df = pd.read_csv(latest_file)
            data = {
                "Name": df["Name"].tolist(),
                "ID": df["ID"].tolist(),
                "Type": [type_name] * len(df),
            }

            st.success(
                f"✅ Loaded {len(data['Name'])} {object_type} from {environment}"
            )
            return pd.DataFrame(data)

        except Exception as e:
            st.error(f"❌ Error loading {object_type}: {e}")
            return self._get_sample_data()

    def create_object_export(
        self, object_type: str, environment: str = "sandbox"
    ) -> bool:
        """Create an export for any object type"""
        try:
            import subprocess
            import shutil

            # Try to find the correct Python executable
            python_cmd = None
            for cmd in [
                "python3",
                "python",
                "/usr/bin/python3",
                "/opt/homebrew/bin/python3",
            ]:
                if shutil.which(cmd):
                    python_cmd = cmd
                    break

            if not python_cmd:
                st.error("❌ Python executable not found")
                return False

            # Run the export command
            result = subprocess.run(
                [
                    python_cmd,
                    "jpapi_main.py",
                    "--env",
                    environment,
                    "export",
                    object_type,
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent.parent,
            )

            if result.returncode == 0:
                config = self.get_object_type_config(object_type)
                st.success(
                    f"🎉 {config.name} export created successfully for {environment}"
                )
                return True
            else:
                st.error(f"❌ {config.name} export failed: {result.stderr}")
                return False

        except Exception as e:
            config = self.get_object_type_config(object_type)
            st.error(f"❌ {config.name} export error: {e}")
            return False

    def _get_sample_data(self) -> pd.DataFrame:
        """Fallback sample data"""
        return pd.DataFrame(
            {
                "Name": [
                    "Sample Advanced Search 1",
                    "Sample Advanced Search 2",
                    "Sample Advanced Search 3",
                    "Sample Advanced Search 4",
                    "Sample Advanced Search 5",
                ],
                "ID": [1, 2, 3, 4, 5],
                "Type": ["Advanced Search"] * 5,
            }
        )

    def _get_sample_policies_data(self) -> pd.DataFrame:
        """Fallback sample policies data"""
        return pd.DataFrame(
            {
                "Name": [
                    "macOS Security Policy - FileVault",
                    "Network Access Control",
                    "Application Restrictions",
                    "Device Compliance Policy",
                    "Data Loss Prevention",
                    "Remote Access Policy",
                    "Backup and Recovery",
                    "User Authentication",
                ],
                "ID": [101, 102, 103, 104, 105, 106, 107, 108],
                "Type": ["Policy"] * 8,
            }
        )

    def update_counts(
        self, data: pd.DataFrame, selected_objects: set, deleted_objects: set
    ):
        """Update the count displays"""
        st.session_state.total_count = len(data)
        st.session_state.selected_count = len(selected_objects)
        st.session_state.deleted_count = len(deleted_objects)
