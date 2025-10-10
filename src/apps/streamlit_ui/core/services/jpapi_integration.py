"""
JPAPI Integration Service - Single Responsibility Principle
Handles integration with JPAPI CLI for data gathering
"""

import subprocess
import streamlit as st
from typing import Dict, Any, Optional, List
from pathlib import Path
import os


class JPAPIIntegrationService:
    """JPAPI CLI integration service"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.jpapi_main_path = os.path.join(project_root, "jpapi_main.py")

    def gather_data(self, object_type: str, environment: str) -> Dict[str, Any]:
        """Gather data using JPAPI CLI"""
        try:
            # Get JPAPI command for object type
            jpapi_command = self._get_jpapi_command(object_type)

            # Build command
            cmd = [
                "python",
                self.jpapi_main_path,
                "export",
                jpapi_command,
                "--env",
                environment,
            ]

            # Run command
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Data gathered successfully for {object_type} in {environment}",
                    "output": result.stdout,
                    "command": " ".join(cmd),
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to gather data: {result.stderr}",
                    "error": result.stderr,
                    "command": " ".join(cmd),
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Data gathering timed out after 5 minutes",
                "error": "Timeout",
                "command": " ".join(cmd),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error running JPAPI command: {str(e)}",
                "error": str(e),
                "command": " ".join(cmd),
            }

    def _get_jpapi_command(self, object_type: str) -> str:
        """Get JPAPI command for object type"""
        command_map = {
            "searches": "advanced-searches",
            "policies": "policies",
            "profiles": "profiles",
            "scripts": "scripts",
        }
        return command_map.get(object_type, object_type)

    def is_jpapi_available(self) -> bool:
        """Check if JPAPI is available"""
        return os.path.exists(self.jpapi_main_path)

    def get_jpapi_status(self) -> Dict[str, Any]:
        """Get JPAPI status information"""
        return {
            "available": self.is_jpapi_available(),
            "path": self.jpapi_main_path,
            "project_root": self.project_root,
        }

    def get_supported_commands(self) -> List[str]:
        """Get list of supported JPAPI commands"""
        return ["advanced-searches", "policies", "profiles", "scripts"]

    def validate_command(self, command: str) -> bool:
        """Validate JPAPI command"""
        return command in self.get_supported_commands()

    def get_command_help(self, command: str) -> str:
        """Get help text for JPAPI command"""
        help_texts = {
            "advanced-searches": "Export advanced searches (smart groups) from JAMF Pro",
            "policies": "Export policies from JAMF Pro",
            "profiles": "Export configuration profiles from JAMF Pro",
            "scripts": "Export scripts from JAMF Pro",
        }
        return help_texts.get(command, f"Export {command} from JAMF Pro")
