#!/usr/bin/env python3
"""
Category Export Handler for jpapi CLI
Handles export of JAMF categories
"""

from typing import Dict, Any, List
from argparse import Namespace
from .export_base import ExportBase
import json
from lib.utils import create_jamf_hyperlink


class ExportCategories(ExportBase):
    """Handler for exporting JAMF categories"""

    def __init__(self, auth):
        super().__init__(auth, "categories")
        self.endpoint = "/JSSResource/categories"
        self.detail_endpoint = "/JSSResource/categories"

    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch category data from JAMF API"""
        response = self.auth.api_request("GET", self.endpoint)

        if "categories" not in response:
            return []

        categories = response["categories"]

        # Handle both list and dict formats
        if isinstance(categories, dict) and "category" in categories:
            categories = categories["category"]

        return categories if isinstance(categories, list) else []

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format category data for export"""
        export_data = []

        for i, category in enumerate(data):
            print(
                f"   Processing category {i+1}/{len(data)}: {category.get('name', 'Unknown')}"
            )

            category_data = {
                "delete": "",  # Empty column for manual deletion tracking
                "ID": create_jamf_hyperlink(
                    "categories",
                    category.get("id", ""),
                    getattr(args, "env", "sandbox"),
                ),
                "Name": category.get("name", ""),
                "Priority": category.get("priority", ""),
                "Site": (
                    category.get("site", {}).get("name", "")
                    if isinstance(category.get("site"), dict)
                    else category.get("site", "")
                ),
                "category_file": "",  # Will be set below
            }

            # Always create individual category JSON files for comprehensive export
            if category.get("id"):
                category_file = self._download_category_file(category)
                if category_file:
                    category_data["category_file"] = category_file

            export_data.append(category_data)

        return export_data

    def _download_category_file(self, category: Dict[str, Any]) -> str:
        """Download individual category JSON file"""
        try:
            # Get detailed category info
            category_id = category.get("id")
            detail_response = self.auth.api_request(
                "GET", f"{self.detail_endpoint}/id/{category_id}"
            )

            if not detail_response:
                return ""

            # Create safe filename
            safe_name = self._create_safe_filename(
                category.get("name", ""), category.get("id", ""), "json"
            )

            # Save category file as JSON
            category_file = self._download_file(
                json.dumps(detail_response, indent=2),
                safe_name,
                "data/csv-exports/categories",
            )

            # Return relative path format to match expected CSV format
            return f"data/csv-exports/categories/{safe_name}"

        except Exception as e:
            print(f"   ⚠️ Failed to download {category.get('name', '')}: {e}")
            return ""
