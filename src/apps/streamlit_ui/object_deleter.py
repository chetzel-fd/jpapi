#!/usr/bin/env python3
"""
Object Deleter Implementation - SOLID Principles
"""

import streamlit as st
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

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
ObjectDeleter = _interfaces.ObjectDeleter


class MockObjectDeleter(ObjectDeleter):
    """Concrete implementation of ObjectDeleter with mock deletion"""

    def delete_objects(self, object_ids: List[str]) -> Dict[str, Any]:
        """Delete objects by their IDs (mock implementation)"""
        try:
            # Simulate deletion process
            result = {
                "success": True,
                "deleted_count": len(object_ids),
                "deleted_objects": object_ids,
                "errors": [],
            }

            # Simulate API calls
            for obj_id in object_ids:
                # Mock verification
                time.sleep(0.1)
                # Mock deletion
                time.sleep(0.1)
                # Mock logging
                time.sleep(0.1)

            return result

        except Exception as e:
            return {
                "success": False,
                "deleted_count": 0,
                "deleted_objects": [],
                "errors": [str(e)],
            }


class JPAPIObjectDeleter(ObjectDeleter):
    """Concrete implementation using actual JPAPI deletion"""

    def __init__(self, jpapi_path: str = "src/jpapi_main.py"):
        self.jpapi_path = jpapi_path

    def delete_objects(self, object_ids: List[str]) -> Dict[str, Any]:
        """Delete objects using JPAPI CLI"""
        try:
            result = {
                "success": True,
                "deleted_count": 0,
                "deleted_objects": [],
                "errors": [],
            }

            for obj_id in object_ids:
                try:
                    # Construct delete command
                    cmd = [
                        "python3",
                        self.jpapi_path,
                        "delete",
                        "object",
                        "--id",
                        obj_id,
                    ]

                    # Execute delete command
                    import subprocess

                    delete_result = subprocess.run(cmd, capture_output=True, text=True)

                    if delete_result.returncode == 0:
                        result["deleted_count"] += 1
                        result["deleted_objects"].append(obj_id)
                    else:
                        result["errors"].append(
                            f"Failed to delete {obj_id}: {delete_result.stderr}"
                        )

                except Exception as e:
                    result["errors"].append(f"Error deleting {obj_id}: {str(e)}")

            result["success"] = len(result["errors"]) == 0
            return result

        except Exception as e:
            return {
                "success": False,
                "deleted_count": 0,
                "deleted_objects": [],
                "errors": [str(e)],
            }
