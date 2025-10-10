#!/usr/bin/env python3
"""
Script Export Handler for jpapi CLI
Handles export and download of JAMF scripts
"""

from typing import Dict, Any, List
from argparse import Namespace
from .export_base import ExportBase
from core.logging.command_mixin import log_operation, with_progress
import fnmatch
import time
from src.lib.utils import create_jamf_hyperlink


class ExportScripts(ExportBase):
    """Handler for exporting JAMF scripts"""

    def __init__(self, auth):
        super().__init__(auth, "scripts")
        self.endpoint = "/JSSResource/scripts"
        self.detail_endpoint = "/JSSResource/scripts"

    @log_operation("Script Data Fetch")
    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch script data from JAMF API"""
        self.log_info("Fetching scripts from JAMF API")
        response = self.auth.api_request("GET", self.endpoint)

        if "scripts" not in response:
            self.log_warning("No scripts found in API response")
            return []

        scripts = response["scripts"]

        # Handle both list and dict formats
        if isinstance(scripts, dict) and "script" in scripts:
            scripts = scripts["script"]

        result = scripts if isinstance(scripts, list) else []
        self.log_success(f"Found {len(result)} scripts")
        return result

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format script data for export"""
        self.log_info(f"Formatting {len(data)} scripts for export")

        # Apply filters if specified
        filtered_data = self._apply_filters(data, args)
        self.log_info(f"After filtering: {len(filtered_data)} scripts")

        export_data = []
        downloaded_files = []

        with self.progress_tracker(len(filtered_data), "Processing scripts") as tracker:
            for i, script in enumerate(filtered_data):
                script_name = script.get("name", "Unknown")
                self.log_progress(
                    i + 1, len(filtered_data), script_name, "Processing script"
                )

                script_data = self._get_basic_script_data(
                    script, getattr(args, "env", "dev")
                )

                # Include script content if requested
                if getattr(args, "include_content", False):
                    tracker.update(description=f"Fetching content for: {script_name}")
                    detailed_data = self._get_detailed_script_data(script)
                    if detailed_data:
                        script_data.update(detailed_data)

                export_data.append(script_data)

                # Always create individual script files for comprehensive export
                tracker.update(description=f"Downloading: {script_name}")
                script_file = self._download_script_file(script)
                if script_file:
                    script_data["script_file"] = script_file
                    downloaded_files.append(script_file)
                    self.log_success(f"Downloaded: {script_name} → {script_file}")

                tracker.update()

        # Store downloaded files for summary
        if downloaded_files:
            self._downloaded_files = downloaded_files

        return export_data

    def _apply_filters(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Apply filtering to script data"""
        filtered = data

        if getattr(args, "category", None):
            filtered = [
                s
                for s in filtered
                if getattr(args, "category", "").lower()
                in s.get("category", "").lower()
            ]

        if getattr(args, "name", None):
            filtered = [
                s
                for s in filtered
                if fnmatch.fnmatch(
                    s.get("name", "").lower(), getattr(args, "name", "").lower()
                )
            ]

        if getattr(args, "id", None):
            filtered = [
                s
                for s in filtered
                if str(s.get("id", "")) == str(getattr(args, "id", ""))
            ]

        return filtered

    def _get_basic_script_data(
        self, script: Dict[str, Any], environment: str = "dev"
    ) -> Dict[str, Any]:
        """Get basic script information"""
        return {
            "delete": "",  # Empty column for manual deletion tracking
            "ID": create_jamf_hyperlink("scripts", script.get("id", ""), environment),
            "Name": script.get("name", ""),
            "Description": script.get("info", ""),  # Use info as description
            "Category": script.get("category", ""),
            "Priority": script.get("priority", ""),
            "Info": script.get("info", ""),
            "Parameters": script.get("parameter4", ""),
            "OS_Requirements": script.get("os_requirements", ""),
            "Filename": script.get("filename", ""),
            "Created_Date": script.get("created", ""),
            "Modified_Date": script.get("modified", ""),
            "script_file": "",  # Will be set below
        }

    def _get_detailed_script_data(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed script information including content"""
        try:
            detail_response = self.auth.api_request(
                "GET", f'{self.detail_endpoint}/id/{script.get("id")}'
            )
            if "script" in detail_response:
                detail_script = detail_response["script"]
                return {
                    "category": detail_script.get("category", ""),
                    "priority": detail_script.get("priority", ""),
                    "info": detail_script.get("info", ""),
                    "parameters": detail_script.get("parameter4", ""),
                    "os_requirements": detail_script.get("os_requirements", ""),
                    "filename": detail_script.get("filename", ""),
                }
        except Exception as e:
            print(
                f"   ⚠️ Could not fetch detailed content for {script.get('name', '')}: {e}"
            )

        return {}

    def _download_script_file(self, script: Dict[str, Any]) -> str:
        """Download individual script file"""
        try:
            # Get detailed script info for content
            detail_response = self.auth.api_request(
                "GET", f'{self.detail_endpoint}/id/{script.get("id")}'
            )
            if "script" in detail_response:
                detail_script = detail_response["script"]
                script_content = detail_script.get("script_contents", "")

                if script_content:
                    # Create script file with header
                    script_header = self._create_script_header(script, detail_script)
                    full_content = script_header + script_content

                    # Create safe filename
                    safe_name = self._create_safe_filename(
                        script.get("name", ""), script.get("id", ""), "sh"
                    )

                    # Download script file
                    script_file = self._download_file(
                        full_content, safe_name, "data/csv-exports/scripts"
                    )

                    # Return relative path format to match expected CSV format
                    return f"data/csv-exports/scripts/{safe_name}"

        except Exception as e:
            print(f"   ⚠️ Failed to download {script.get('name', '')}: {e}")

        return ""

    def _create_script_header(
        self, script: Dict[str, Any], detail_script: Dict[str, Any]
    ) -> str:
        """Create header for script file"""
        return f"""#!/bin/bash
# JAMF Script: {script.get('name', '')}
# Script ID: {script.get('id', '')}
# Category: {script.get('category', 'N/A')}
# Priority: {script.get('priority', 'N/A')}
# Parameters: {script.get('parameter4', 'None')}
#
# Exported from JAMF Pro
# Export Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
#

"""

    def export(self, args: Namespace) -> int:
        """Override export to handle downloaded files summary"""
        result = super().export(args)

        # Show downloaded files summary if any
        if hasattr(self, "_downloaded_files") and self._downloaded_files:
            print(f"📁 Downloaded {len(self._downloaded_files)} script files")
            print(f"   Files saved to: data/csv-exports/scripts")
            print(f"\n📋 Downloaded Files:")
            for file_path in self._downloaded_files[:10]:  # Show first 10
                print(f"   {file_path}")
            if len(self._downloaded_files) > 10:
                print(f"   ... and {len(self._downloaded_files) - 10} more files")

        return result
