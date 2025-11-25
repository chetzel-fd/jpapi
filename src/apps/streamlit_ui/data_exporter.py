#!/usr/bin/env python3
"""
Data Exporter Implementation - SOLID Principles
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Setup path and load local interfaces
_current_dir = Path(__file__).parent
_project_src = _current_dir.parent.parent
for p in [str(_current_dir), str(_project_src)]:
    while p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(_current_dir))
sys.path.insert(1, str(_project_src))

import importlib.util

_interfaces_path = os.path.join(str(_current_dir), "interfaces.py")
_spec = importlib.util.spec_from_file_location("streamlit_interfaces", _interfaces_path)
_interfaces = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_interfaces)
DataExporter = _interfaces.DataExporter


class JPAPIDataExporter(DataExporter):
    """Concrete implementation of DataExporter using JPAPI CLI"""

    def __init__(self, jpapi_path: str = "src/jpapi_main.py"):
        self.jpapi_path = jpapi_path

    def export_data(self, object_type: str, environment: str) -> bool:
        """Export data using JPAPI CLI (using list with export mode)"""
        try:
            # Get command from object type manager
            from core.config.object_type_manager import ObjectTypeManager

            object_manager = ObjectTypeManager()
            jpapi_command = object_manager.get_jpapi_command(object_type)

            # Construct command using list with export-mode
            # (export command is deprecated, list now handles exports)
            cmd = [
                "python3",
                self.jpapi_path,
                "--env",
                environment,
                "list",
                jpapi_command,
                "--export-mode",
                "--format",
                "csv",
            ]

            # Execute command
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=os.getcwd()
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
