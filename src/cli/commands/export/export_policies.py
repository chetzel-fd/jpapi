#!/usr/bin/env python3
"""
Policy Export Handler for jpapi CLI
Handles export of JAMF policies
"""

from typing import Dict, Any, List, Optional
from argparse import Namespace
from .export_base import ExportBase
import json
from lib.utils import create_jamf_hyperlink
from lib.exports.manage_exports import get_export_directory
from core.logging.command_mixin import log_operation, with_progress


class ExportPolicies(ExportBase):
    """Handler for exporting JAMF policies"""

    def __init__(self, auth):
        super().__init__(auth, "policies")
        self.endpoint = "/api/v1/policies"
        self.detail_endpoint = "/JSSResource/policies"
        self.environment = "sandbox"  # Default environment
        self.category_cache: Dict[int, Dict[str, Any]] = {}

    @log_operation("Policy Data Fetch")
    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch policy data from JAMF API with pagination"""
        all_policies = []
        page = 0
        page_size = 100

        self.log_info("Starting policy data fetch from JAMF API")

        while True:
            url = f"{self.endpoint}?page={page}&page-size={page_size}&sort=id"
            self.log_info(f"Fetching page {page + 1}...")

            try:
                response = self.auth.api_request("GET", url)
                if "results" in response:
                    policies = response["results"]
                    if not policies:
                        self.log_info("No more policies found, pagination complete")
                        break

                    all_policies.extend(policies)
                    self.log_success(
                        f"Found {len(policies)} policies on page {page + 1} "
                        f"(Total: {len(all_policies)})"
                    )

                    if len(policies) < page_size:
                        self.log_info("Last page reached")
                        break
                    page += 1
                else:
                    self.log_warning("No results in response, stopping pagination")
                    break
            except Exception as e:
                self.log_error(f"Error fetching page {page + 1}", e)
                break

        self.log_success(
            f"Policy fetch complete: {len(all_policies)} total policies retrieved"
        )
        return all_policies

    def _get_category_details(self, category_id: Optional[Any]) -> Dict[str, Any]:
        """Get category details from API with caching"""
        if not category_id:
            return {}

        # Convert to int if needed
        try:
            cat_id = int(category_id)
        except (TypeError, ValueError):
            return {}

        # Check cache first
        if cat_id in self.category_cache:
            return self.category_cache[cat_id]

        try:
            endpoint = f"/JSSResource/categories/id/{cat_id}"
            response = self.auth.api_request("GET", endpoint)
            if "category" in response:
                category_data = response["category"]
                self.category_cache[cat_id] = category_data
                return category_data
        except Exception as e:
            self.log_error(f"Could not fetch category {cat_id}", e)

        return {}

    def _extract_category_info(self, category_obj: Any) -> tuple[str, str]:
        """Extract category name and description from category object"""
        category_name = ""
        category_description = ""

        if isinstance(category_obj, dict):
            category_name = category_obj.get("name", "")
            category_id = category_obj.get("id", "")
            if category_id:
                cat_details = self._get_category_details(category_id)
                if cat_details:
                    category_description = cat_details.get("description", "")
        else:
            category_name = str(category_obj) if category_obj else ""

        return category_name, category_description

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format policy data for export"""
        export_data = []
        downloaded_files = []

        self.log_info(f"Starting data formatting for {len(data)} policies")

        # Apply filtering if specified (before detailed processing)
        if hasattr(args, "filter") and args.filter:
            from lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(data)

            # Try filtering by ID first, then by name if no matches
            id_filtered = filter_obj.filter_objects(data, "id", args.filter)
            if id_filtered:
                data = id_filtered
                self.log_info(
                    f"Filtered by ID from {original_count} to {len(data)} policies"
                )
            else:
                data = filter_obj.filter_objects(data, "name", args.filter)
                self.log_info(
                    f"Filtered by name from {original_count} to {len(data)} policies"
                )

        # Use progress tracker for policy processing
        with self.progress_tracker(len(data), "Processing policies") as tracker:
            for i, policy in enumerate(data):
                policy_name = policy.get("name", "Unknown")
                self.log_progress(i + 1, len(data), policy_name, "Processing policy")

                # Get detailed policy info to check enabled status
                enabled = False
                detail_policy = None
                try:
                    tracker.update(description=f"Fetching details for: {policy_name}")
                    detail_response = self.auth.api_request(
                        "GET", f'{self.detail_endpoint}/id/{policy.get("id")}'
                    )
                    if "policy" in detail_response:
                        detail_policy = detail_response["policy"]
                        enabled = detail_policy.get("general", {}).get("enabled", False)
                        # Handle both boolean and string values
                        if isinstance(enabled, str):
                            enabled = enabled.lower() in ["true", "1", "yes", "enabled"]
                except Exception as e:
                    self.log_error(
                        f"Could not get details for policy {policy.get('id')}", e
                    )

                status = "Enabled" if enabled else "Disabled"

                # Apply status filtering if specified
                if args.status != "all":
                    if args.status == "enabled" and not enabled:
                        tracker.update()
                        continue  # Skip disabled policies
                    elif args.status == "disabled" and enabled:
                        tracker.update()
                        continue  # Skip enabled policies

                # Extract script information
                scripts_info = self._extract_script_info(detail_policy or {})

                # Extract data from detailed policy if available, otherwise use basic policy
                if detail_policy:
                    general = detail_policy.get("general", {})
                    # Extract category info
                    cat_name, cat_desc = self._extract_category_info(
                        general.get("category", {})
                    )
                    policy_data = {
                        "delete": "",  # Empty column for manual deletion tracking
                        "ID": create_jamf_hyperlink(
                            "policies",
                            policy.get("id", ""),
                            getattr(args, "env", "sandbox"),
                        ),
                        "Name": policy.get("name", ""),
                        "Description": general.get(
                            "description", ""
                        ),  # Add description field
                        "Status": status,
                        "Enabled": enabled,
                        "Category": cat_name,
                        "Category Description": cat_desc,
                        "Frequency": general.get("frequency", ""),
                        "Trigger": general.get("trigger", ""),
                        "Event_Trigger": general.get("trigger_other", ""),
                        "Script_Name": scripts_info.get("script_name", ""),
                        "Script_Parameters": scripts_info.get("parameters", ""),
                        "Script_Priority": scripts_info.get("priority", ""),
                        "Created_Date": general.get("created", ""),
                        "Modified_Date": general.get("modified", ""),
                        "policy_file": "",  # Will be set below
                    }
                else:
                    # Fallback to basic policy data if detailed info not available
                    # Extract category info
                    cat_name, cat_desc = self._extract_category_info(
                        policy.get("category", {})
                    )
                    policy_data = {
                        "delete": "",  # Empty column for manual deletion tracking
                        "ID": create_jamf_hyperlink(
                            "policies",
                            policy.get("id", ""),
                            getattr(args, "env", "sandbox"),
                        ),
                        "Name": policy.get("name", ""),
                        "Description": policy.get(
                            "description", ""
                        ),  # Description from basic policy
                        "Status": status,
                        "Enabled": enabled,
                        "Category": cat_name,
                        "Category Description": cat_desc,
                        "Frequency": policy.get("frequency", ""),
                        "Trigger": policy.get("trigger", ""),
                        "Event_Trigger": "",
                        "Script_Name": scripts_info.get("script_name", ""),
                        "Script_Parameters": scripts_info.get("parameters", ""),
                        "Script_Priority": scripts_info.get("priority", ""),
                        "Created_Date": "",
                        "Modified_Date": "",
                        "policy_file": "",  # Will be set below
                    }

                # Always create individual policy JSON files for comprehensive export
                if detail_policy:
                    tracker.update(
                        description=f"Downloading policy file: {policy_name}"
                    )
                    policy_file = self._download_policy_file(detail_policy, policy)
                    if policy_file:
                        policy_data["policy_file"] = policy_file
                        downloaded_files.append(policy_file)
                        self.log_success(f"Downloaded: {policy_name} → {policy_file}")

                export_data.append(policy_data)
                tracker.update()

        # Store downloaded files for summary
        if downloaded_files:
            self._downloaded_files = downloaded_files

        self.log_success(
            f"Data formatting complete: {len(export_data)} policies processed"
        )
        return export_data

    def _extract_script_info(self, detail_policy: Dict[str, Any]) -> Dict[str, str]:
        """Extract script information from policy details"""
        if not detail_policy:
            return {"script_name": "", "parameters": "", "priority": ""}

        scripts = detail_policy.get("scripts", [])
        if not scripts:
            return {"script_name": "", "parameters": "", "priority": ""}

        # Handle both single script and multiple scripts
        if isinstance(scripts, dict):
            scripts = [scripts]

        script_info = []
        for script in scripts:
            script_name = script.get("name", "")
            priority = script.get("priority", "")

            # Extract parameters
            parameters = []
            for i in range(4, 12):  # Parameters 4-11
                param_key = f"parameter{i}"
                param_value = script.get(param_key, "")
                if param_value:
                    parameters.append(f"P{i}:{param_value}")

            param_str = "; ".join(parameters) if parameters else ""
            script_info.append(f"{script_name}({priority}): {param_str}")

        return {
            "script_name": "; ".join([s.get("name", "") for s in scripts]),
            "parameters": "; ".join(
                [
                    f"P{i}:{s.get(f'parameter{i}', '')}"
                    for s in scripts
                    for i in range(4, 12)
                    if s.get(f"parameter{i}", "")
                ]
            ),
            "priority": "; ".join([s.get("priority", "") for s in scripts]),
        }

    def _download_policy_file(
        self, detail_policy: Dict[str, Any], policy: Dict[str, Any]
    ) -> str:
        """Download individual policy file as JSON"""
        try:
            policy_name = policy.get("name", "Unknown")
            self.log_info(f"Downloading policy file: {policy_name}")

            # Create safe filename
            safe_name = self._create_safe_filename(
                policy.get("name", ""), policy.get("id", ""), "json"
            )

            # Save policy file as JSON
            # Get the proper export directory for the environment
            export_dir = get_export_directory(getattr(self, "environment", "sandbox"))
            policies_dir = export_dir / "policies"

            self._download_file(
                json.dumps(detail_policy, indent=2),
                safe_name,
                str(policies_dir),
            )

            # Return relative path format to match expected CSV format
            file_path = f"{policies_dir}/{safe_name}"
            self.log_success(f"Policy file saved: {file_path}")
            return file_path

        except Exception as e:
            self.log_error(f"Failed to download {policy.get('name', '')}", e)
            return ""

    def export(self, args: Namespace) -> int:
        """Override export to handle downloaded files summary"""
        # Set environment from args
        self.environment = getattr(args, "env", "sandbox")
        result = super().export(args)

        # Show downloaded files summary if any
        if hasattr(self, "_downloaded_files") and self._downloaded_files:
            self.log_success(f"Downloaded {len(self._downloaded_files)} policy files")
            # Get the proper export directory for the environment
            export_dir = get_export_directory(getattr(self, "environment", "sandbox"))
            policies_dir = export_dir / "policies"
            self.log_info(f"Files saved to: {policies_dir}")
            self.log_info("Downloaded Files:")
            for file_path in self._downloaded_files[:10]:  # Show first 10
                self.log_info(f"   {file_path}")
            if len(self._downloaded_files) > 10:
                remaining = len(self._downloaded_files) - 10
                self.log_info(f"   ... and {remaining} more files")

        return result
