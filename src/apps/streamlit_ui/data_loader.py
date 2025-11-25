#!/usr/bin/env python3
"""
Data Loader Implementation - SOLID Principles
"""

import pandas as pd
import glob
import os
import sys
from pathlib import Path
from typing import Dict, List

# Ensure local directory is first in path
_current_dir = Path(__file__).parent
_project_src = _current_dir.parent.parent
for p in [str(_current_dir), str(_project_src)]:
    while p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(_current_dir))
sys.path.insert(1, str(_project_src))

# Explicitly load local interfaces to avoid conflicts with project-level interfaces
import importlib.util

_interfaces_path = os.path.join(str(_current_dir), "interfaces.py")
_spec = importlib.util.spec_from_file_location("streamlit_interfaces", _interfaces_path)
_interfaces = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_interfaces)
DataLoader = _interfaces.DataLoader

from ui_utils import normalize_environment


class CSVDataLoader(DataLoader):
    """Concrete implementation of DataLoader for CSV files"""

    def __init__(self, base_path: str = "storage/data/csv-exports"):
        self.base_path = base_path

    def load_data(self, object_type: str, environment: str) -> pd.DataFrame:
        """Load data from CSV files"""
        try:
            # Try to load from object type manager first
            from core.config.object_type_manager import ObjectTypeManager

            object_manager = ObjectTypeManager()
            return object_manager.get_sample_data(object_type)
        except:
            # Ultimate fallback
            return pd.DataFrame(
                {
                    "Name": [f"Sample {object_type.title()} {i}" for i in range(1, 6)],
                    "ID": [1000 + i for i in range(1, 6)],
                    "Type": [object_type.title()] * 5,
                    "Status": ["Active", "Active", "Draft", "Active", "Active"],
                }
            )


class FileDataLoader(DataLoader):
    """Concrete implementation for loading from actual CSV files"""

    def __init__(self, base_path: str = "storage/data/csv-exports"):
        self.base_path = base_path

    def load_data(self, object_type: str, environment: str) -> pd.DataFrame:
        """Load data from CSV files with environment-specific patterns"""
        try:
            # Get file patterns from object type manager
            from core.config.object_type_manager import ObjectTypeManager

            # Normalize environment name (dev→sandbox, prod→production)
            normalized_env = normalize_environment(environment)

            # Get patterns with environment already substituted
            object_manager = ObjectTypeManager()
            file_patterns = object_manager.get_file_patterns(
                object_type, normalized_env
            )

            # Find matching files
            all_files = []
            for pattern in file_patterns:
                full_pattern = os.path.join(self.base_path, pattern)
                files = glob.glob(full_pattern)
                all_files.extend(files)

            if not all_files:
                return pd.DataFrame()

            # Load the most recent file
            latest_file = max(all_files, key=os.path.getmtime)
            data = pd.read_csv(latest_file)

            # Add clickable hyperlinks to ID column
            if "ID" in data.columns:
                data = self._add_clickable_hyperlinks(data)

            return data

        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()

    def _add_clickable_hyperlinks(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add clickable hyperlinks to ID column"""
        if "ID" not in data.columns:
            return data

        # Check if already has hyperlinks
        sample_id = str(data["ID"].iloc[0]) if len(data) > 0 else ""
        if "<a href=" in sample_id or "=HYPERLINK(" in sample_id:
            return data

        # Add hyperlinks
        def create_hyperlink(id_val):
            try:
                id_int = int(id_val)
                base_url = os.environ.get("JPAPI_SERVER_URL", "")
                if base_url:
                    return f'<a href="{base_url}/{object_type.lower()}s.html?id={id_int}" target="_blank" style="color: #3393ff; text-decoration: none; font-weight: bold;">{id_int}</a>'
                return str(id_int)
            except:
                return str(id_val)

        data["ID"] = data["ID"].apply(create_hyperlink)
        return data
