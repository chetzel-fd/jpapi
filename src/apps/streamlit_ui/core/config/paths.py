"""
Path Configuration - Path Management
Centralized path management for the JPAPI Streamlit UI
"""

import os
from pathlib import Path
from typing import List, Optional


class Paths:
    """Path configuration and management"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root or self._find_project_root()
        self.app_root = os.path.join(self.project_root, "src", "apps", "streamlit_ui")

    def _find_project_root(self) -> str:
        """Find the project root directory"""
        current = Path(__file__).resolve()
        while current.parent != current:
            if (current / "jpapi_main.py").exists():
                return str(current)
            current = current.parent
        return str(Path.cwd())

    def get_csv_export_dirs(self) -> List[str]:
        """Get list of CSV export directories to search"""
        base_dirs = [
            os.path.join(self.project_root, "storage", "data", "csv-exports"),
            os.path.join(self.project_root, "data", "csv-exports"),
            os.path.join(self.project_root, "storage", "exports"),
            os.path.join(self.project_root, "exports"),
            os.path.join(self.project_root, "storage", "data"),
            os.path.join(self.project_root, "data"),
        ]

        # Filter to only existing directories
        existing_dirs = [d for d in base_dirs if os.path.exists(d)]

        # If no directories exist, create the default one
        if not existing_dirs:
            default_dir = os.path.join(self.project_root, "data", "csv-exports")
            os.makedirs(default_dir, exist_ok=True)
            existing_dirs = [default_dir]

        return existing_dirs

    def get_cache_dir(self) -> str:
        """Get cache directory path"""
        cache_dir = os.path.join(self.project_root, "storage", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def get_logs_dir(self) -> str:
        """Get logs directory path"""
        logs_dir = os.path.join(self.project_root, "storage", "logs")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir

    def get_temp_dir(self) -> str:
        """Get temporary directory path"""
        temp_dir = os.path.join(self.project_root, "tmp")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def get_legacy_dir(self) -> str:
        """Get legacy files directory path"""
        legacy_dir = os.path.join(self.app_root, "legacy")
        os.makedirs(legacy_dir, exist_ok=True)
        return legacy_dir

    def get_tests_dir(self) -> str:
        """Get tests directory path"""
        tests_dir = os.path.join(self.app_root, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        return tests_dir

    def resolve_path(self, path: str) -> str:
        """Resolve a path relative to project root"""
        if os.path.isabs(path):
            return path
        return os.path.join(self.project_root, path)

    def ensure_dir(self, path: str) -> str:
        """Ensure directory exists and return path"""
        os.makedirs(path, exist_ok=True)
        return path
