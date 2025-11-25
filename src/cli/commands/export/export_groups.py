#!/usr/bin/env python3
"""
Group Export Handler for jpapi CLI
Handles export of computer groups and advanced searches
"""

from typing import Dict, Any, List
from argparse import Namespace
from .export_base import ExportBase
from core.logging.command_mixin import log_operation, with_progress
import json
from lib.utils import create_jamf_hyperlink


class ExportComputerGroups(ExportBase):
    """Handler for exporting computer groups"""

    def __init__(self, auth):
        super().__init__(auth, "computer groups")
        self.endpoint = "/JSSResource/computergroups"
        self.detail_endpoint = "/JSSResource/computergroups"

    @log_operation("Computer Group Data Fetch")
    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch computer group data from JAMF API"""
        self.log_info("Fetching computer groups from JAMF API")
        response = self.auth.api_request("GET", self.endpoint)

        if "computer_groups" not in response:
            self.log_warning("No computer groups found in API response")
            return []

        groups = response["computer_groups"]

        # Handle both list and dict formats
        if isinstance(groups, dict) and "computer_group" in groups:
            groups = groups["computer_group"]

        return groups if isinstance(groups, list) else []

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format computer group data for export"""
        export_data = []

        for i, group in enumerate(data):
            print(
                f"   Processing group {i+1}/{len(data)}: {group.get('name', 'Unknown')}"
            )

            # Basic group data
            group_data = self._get_basic_group_data(
                group, getattr(args, "env", "sandbox")
            )

            # Get detailed info for all groups to make CSV more useful
            if group.get("id"):
                detailed_data = self._get_detailed_group_data(group["id"])
                if detailed_data:
                    group_data.update(detailed_data)

                # Always create individual group JSON files for comprehensive export
                group_file = self._download_group_file(group)
                if group_file:
                    group_data["group_file"] = group_file

            export_data.append(group_data)

        return export_data

    def _download_group_file(self, group: Dict[str, Any]) -> str:
        """Download individual group JSON file"""
        try:
            # Get detailed group info
            group_id = group.get("id")
            detail_response = self.auth.api_request(
                "GET", f"{self.detail_endpoint}/id/{group_id}"
            )

            if not detail_response:
                return ""

            # Create safe filename
            safe_name = self._create_safe_filename(
                group.get("name", ""), group.get("id", ""), "json"
            )

            # Save group file as JSON
            group_file = self._download_file(
                json.dumps(detail_response, indent=2),
                safe_name,
                "data/csv-exports/computer_groups",
            )

            # Return relative path format to match expected CSV format
            return f"data/csv-exports/computer_groups/{safe_name}"

        except Exception as e:
            print(f"   ⚠️ Failed to download {group.get('name', '')}: {e}")
            return ""

    def _get_basic_group_data(
        self, group: Dict[str, Any], environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """Get basic group information"""
        return {
            "delete": "",  # Empty column for manual deletion tracking
            "ID": create_jamf_hyperlink("groups", group.get("id", ""), environment),
            "Name": group.get("name", ""),
            "Smart": group.get("is_smart", False),
            "Description": group.get("description", ""),
            "Site": (
                group.get("site", {}).get("name", "")
                if isinstance(group.get("site"), dict)
                else group.get("site", "")
            ),
            "Member Count": (
                len(group.get("computers", []))
                if isinstance(group.get("computers"), list)
                else 0
            ),
            "group_file": "",  # Will be set below
        }

    def _get_detailed_group_data(self, group_id: str) -> Dict[str, Any]:
        """Get detailed group information"""
        detail = self._get_detailed_info(group_id, self.detail_endpoint)
        if not detail:
            return {"Criteria Count": 0, "Computers": "", "Criteria": ""}

        return {
            "Criteria Count": len(detail.get("criteria", [])),
            "Computers": ", ".join(
                [comp.get("name", "") for comp in detail.get("computers", [])]
            ),
            "Criteria": "; ".join(
                [
                    f"{c.get('name', '')} {c.get('operator', '')} {c.get('value', '')}"
                    for c in detail.get("criteria", [])
                ]
            ),
        }


class ExportAdvancedSearches(ExportBase):
    """Handler for exporting advanced computer searches"""

    def __init__(self, auth):
        super().__init__(auth, "advanced computer searches")
        self.endpoint = "/JSSResource/advancedcomputersearches"
        self.detail_endpoint = "/JSSResource/advancedcomputersearches"

    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch advanced search data from JAMF API"""
        response = self.auth.api_request("GET", self.endpoint)

        if "advanced_computer_searches" not in response:
            return []

        searches = response["advanced_computer_searches"]

        # Handle both list and dict formats
        if isinstance(searches, dict) and "advanced_computer_search" in searches:
            searches = searches["advanced_computer_search"]

        return searches if isinstance(searches, list) else []

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format advanced search data for export"""
        # Apply filters if specified
        filtered_data = self._apply_filters(data, args)

        export_data = []

        for i, search in enumerate(filtered_data):
            print(
                f"   Processing search {i+1}/{len(filtered_data)}: {search.get('name', 'Unknown')}"
            )

            # Basic search data
            search_data = self._get_basic_search_data(search)

            # Add detailed info if requested
            if args.detailed and search.get("id"):
                detailed_data = self._get_detailed_search_data(search["id"])
                if detailed_data:
                    search_data.update(detailed_data)

            export_data.append(search_data)

        return export_data

    def _apply_filters(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Apply filtering to search data using unified filter system"""
        from lib.utils import create_filter

        filtered = data

        if hasattr(args, "name") and args.name:
            filter_obj = create_filter("wildcard")
            filtered = filter_obj.filter_objects(filtered, "name", args.name)

        if hasattr(args, "id") and args.id:
            filter_obj = create_filter("exact")
            filtered = filter_obj.filter_objects(filtered, "id", str(args.id))

        return filtered

    def _get_basic_search_data(self, search: Dict[str, Any]) -> Dict[str, Any]:
        """Get basic search information"""
        return {
            "id": search.get("id", ""),
            "name": search.get("name", ""),
            "view_as": search.get("view_as", ""),
            "sort_1": search.get("sort_1", ""),
            "sort_2": search.get("sort_2", ""),
            "sort_3": search.get("sort_3", ""),
            "site": (
                search.get("site", {}).get("name", "")
                if isinstance(search.get("site"), dict)
                else search.get("site", "")
            ),
            "criteria_count": len(search.get("criteria", [])),
            "display_fields_count": len(search.get("display_fields", [])),
            "computer_count": len(search.get("computers", [])),
            "delete": "",  # Empty column for manual deletion tracking
        }

    def _get_detailed_search_data(self, search_id: str) -> Dict[str, Any]:
        """Get detailed search information"""
        detail = self._get_detailed_info(search_id, self.detail_endpoint)
        if not detail:
            return {
                "criteria": "",
                "display_fields": "",
                "computers": "",
                "site_id": "",
                "view_as": "",
                "sort_1": "",
                "sort_2": "",
                "sort_3": "",
            }

        # Format criteria for CSV
        criteria_list = []
        for criterion in detail.get("criteria", []):
            criteria_str = f"{criterion.get('name', '')} {criterion.get('search_type', '')} {criterion.get('value', '')}"
            if criterion.get("and_or"):
                criteria_str = f"{criterion.get('and_or', '').upper()} {criteria_str}"
            criteria_list.append(criteria_str)

        # Format display fields
        display_fields_list = [
            field.get("name", "") for field in detail.get("display_fields", [])
        ]

        # Format computer names
        computer_names = [comp.get("name", "") for comp in detail.get("computers", [])]

        return {
            "criteria": "; ".join(criteria_list),
            "display_fields": "; ".join(display_fields_list),
            "computers": "; ".join(computer_names),
            "site_id": (
                detail.get("site", {}).get("id", "")
                if isinstance(detail.get("site"), dict)
                else ""
            ),
            "view_as": detail.get("view_as", ""),
            "sort_1": detail.get("sort_1", ""),
            "sort_2": detail.get("sort_2", ""),
            "sort_3": detail.get("sort_3", ""),
        }
