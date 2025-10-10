"""
Dashboard Command - SOLID SRP compliance
"""

import subprocess
import sys
import os
from typing import List, Optional


class DashboardCommand:
    """Dashboard command handler - SOLID SRP compliance"""

    def __init__(self):
        self.name = "dashboard"
        self.description = "Launch the jpapi dashboard for managing JAMF objects"

    def execute(self, args: List[str]) -> int:
        """Execute the dashboard command"""
        try:
            # Get the path to the dashboard app
            dashboard_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "dashboard", "app.py"
            )
            dashboard_path = os.path.abspath(dashboard_path)

            # Run the dashboard
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    dashboard_path,
                    "--server.port",
                    "8505",
                    "--server.headless",
                    "true",
                ],
                check=True,
            )

            return result.returncode

        except subprocess.CalledProcessError as e:
            print(f"Error launching dashboard: {e}")
            return e.returncode
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 1

    def help(self) -> str:
        """Return help text for the dashboard command"""
        return """
Dashboard Command:
  Launch the jpapi dashboard for managing JAMF objects

Usage:
  jpapi dashboard

Description:
  Opens a web-based dashboard for managing JAMF Pro objects including:
  - Advanced searches
  - Policies
  - Other JAMF objects (as they are added)

The dashboard provides:
  - Visual grid interface for object management
  - Sorting and filtering capabilities
  - Bulk selection and deletion
  - Real-time data refresh from JAMF Pro
  - Apple-style dark theme UI

The dashboard will open in your default web browser at http://localhost:8505
        """
