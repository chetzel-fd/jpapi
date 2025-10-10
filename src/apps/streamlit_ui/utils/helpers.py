"""
Helper Functions - General Utilities
General helper functions for the JPAPI Streamlit UI
"""

import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
import os
from pathlib import Path


class HelperFunctions:
    """General helper functions"""

    @staticmethod
    def safe_get_column(df: pd.DataFrame, column: str, default: Any = None) -> Any:
        """Safely get column from DataFrame"""
        if column in df.columns:
            return df[column]
        return default

    @staticmethod
    def filter_dataframe(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Filter DataFrame based on provided filters"""
        if df.empty:
            return df

        filtered_df = df.copy()

        for column, value in filters.items():
            if column in filtered_df.columns and value is not None:
                if isinstance(value, str):
                    # String filtering (case-insensitive)
                    filtered_df = filtered_df[
                        filtered_df[column]
                        .astype(str)
                        .str.contains(str(value), case=False, na=False)
                    ]
                elif isinstance(value, bool):
                    # Boolean filtering
                    filtered_df = filtered_df[filtered_df[column] == value]
                else:
                    # Exact match filtering
                    filtered_df = filtered_df[filtered_df[column] == value]

        return filtered_df

    @staticmethod
    def sort_dataframe(
        df: pd.DataFrame, sort_by: str, ascending: bool = True
    ) -> pd.DataFrame:
        """Sort DataFrame by specified column"""
        if df.empty or sort_by not in df.columns:
            return df

        return df.sort_values(by=sort_by, ascending=ascending)

    @staticmethod
    def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
        """Get unique values from DataFrame column"""
        if column not in df.columns:
            return []

        return df[column].dropna().unique().tolist()

    @staticmethod
    def get_column_info(df: pd.DataFrame) -> Dict[str, Any]:
        """Get information about DataFrame columns"""
        if df.empty:
            return {"columns": [], "dtypes": {}, "null_counts": {}}

        return {
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "row_count": len(df),
            "column_count": len(df.columns),
        }

    @staticmethod
    def create_download_link(data: str, filename: str, mime_type: str) -> str:
        """Create download link for data"""
        return f'<a href="data:{mime_type};base64,{data}" download="{filename}">Download {filename}</a>'

    @staticmethod
    def ensure_directory(path: str) -> str:
        """Ensure directory exists and return path"""
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get file information"""
        if not os.path.exists(file_path):
            return {"exists": False}

        stat = os.stat(file_path)
        return {
            "exists": True,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "is_file": os.path.isfile(file_path),
            "is_directory": os.path.isdir(file_path),
        }

    @staticmethod
    def find_files(pattern: str, search_dirs: List[str]) -> List[str]:
        """Find files matching pattern in search directories"""
        import glob

        found_files = []
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                search_pattern = os.path.join(search_dir, pattern)
                matches = glob.glob(search_pattern)
                found_files.extend(matches)

        return found_files

    @staticmethod
    def get_latest_file(files: List[str]) -> Optional[str]:
        """Get the most recent file from list"""
        if not files:
            return None

        return max(files, key=os.path.getmtime)

    @staticmethod
    def validate_environment(environment: str, valid_environments: List[str]) -> bool:
        """Validate environment string"""
        return environment in valid_environments

    @staticmethod
    def validate_object_type(object_type: str, valid_types: List[str]) -> bool:
        """Validate object type string"""
        return object_type in valid_types

    @staticmethod
    def create_info_card(title: str, content: str, icon: str = "ℹ️") -> str:
        """Create info card HTML"""
        return f"""
        <div style="
            background-color: #f0f2f6;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 18px; margin-right: 8px;">{icon}</span>
                <strong>{title}</strong>
            </div>
            <div style="color: #666; font-size: 14px;">
                {content}
            </div>
        </div>
        """

    @staticmethod
    def create_status_badge(status: str) -> str:
        """Create status badge HTML"""
        status_colors = {
            "Active": "#28a745",
            "Deleted": "#dc3545",
            "Inactive": "#6c757d",
        }

        color = status_colors.get(status, "#6c757d")

        return f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        ">
            {status}
        </span>
        """

    @staticmethod
    def truncate_text(text: str, max_length: int = 50) -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """Format timestamp for display"""
        from datetime import datetime

        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Get memory usage information"""
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss": memory_info.rss,  # Resident Set Size
            "vms": memory_info.vms,  # Virtual Memory Size
            "percent": process.memory_percent(),
        }
