#!/usr/bin/env python3
"""
Export Mobile Searches Handler for JPAPI CLI
Handles exporting advanced mobile device searches
"""

from typing import Dict, List, Any, Optional
from .export_base import ExportBase
from lib.managers.mobile_search_manager import MobileSearchManager


class ExportMobileSearches(ExportBase):
    """Handler for exporting advanced mobile device searches"""

    def __init__(self, auth):
        super().__init__(auth, "mobile searches")
        self.mobile_search_manager = MobileSearchManager(auth)

    def fetch_data(self, args) -> List[Dict[str, Any]]:
        """Fetch mobile device searches from API"""
        try:
            self.log_info("Fetching mobile device searches from JAMF API")
            searches = self.mobile_search_manager.get_all_searches()

            if not searches:
                self.log_warning("No mobile device searches found")
                return []

            self.log_success(f"Found {len(searches)} mobile device searches")
            return searches

        except Exception as e:
            self.log_error(f"Error fetching mobile device searches: {e}")
            return []

    def format_data(self, searches: List[Dict[str, Any]], args) -> List[Dict[str, Any]]:
        """Format mobile device searches for export"""
        try:
            self.log_info(f"Starting data formatting for {len(searches)} searches")
            formatted_searches = []

            for i, search in enumerate(searches, 1):
                self.log_info(
                    f"Processing search {search.get('name', 'Unknown')} ({i}/{len(searches)} - {i/len(searches)*100:.1f}%)"
                )

                # Basic search information
                search_data = {
                    "ID": search.get("id", ""),
                    "Name": search.get("name", ""),
                    "Description": search.get("description", ""),
                    "Site": (
                        search.get("site", {}).get("name", "")
                        if isinstance(search.get("site"), dict)
                        else search.get("site", "")
                    ),
                    "Created": search.get("created", ""),
                    "Modified": search.get("modified", ""),
                }

                # Add detailed information if requested
                if getattr(args, "detailed", False):
                    search_data.update(
                        {
                            "Criteria Count": len(search.get("criteria", [])),
                            "Display Fields Count": len(
                                search.get("displayFields", [])
                            ),
                            "Display Fields": ", ".join(
                                search.get("displayFields", [])
                            ),
                        }
                    )

                    # Add criteria details
                    criteria = search.get("criteria", [])
                    if criteria:
                        criteria_details = []
                        for criterion in criteria:
                            criterion_str = f"{criterion.get('name', 'Unknown')}: {criterion.get('operator', 'Unknown')} {criterion.get('value', 'Unknown')}"
                            criteria_details.append(criterion_str)
                        search_data["Criteria Details"] = "; ".join(criteria_details)

                formatted_searches.append(search_data)

            self.log_success(
                f"Data formatting complete: {len(formatted_searches)} searches processed"
            )
            return formatted_searches

        except Exception as e:
            self.log_error(f"Error formatting mobile device searches: {e}")
            return []

    def save_data(self, formatted_data: List[Dict[str, Any]], args) -> str:
        """Save formatted mobile device searches data"""
        try:
            self.log_info("Saving mobile device searches data")

            # Generate filename with environment prefix
            from lib.exports.manage_exports import (
                generate_export_filename,
                get_export_directory,
            )

            filename = generate_export_filename(
                "mobile-searches", args.format, self.environment
            )
            output_dir = get_export_directory()
            output_path = output_dir / "mobile-searches" / filename

            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save the data
            self._save_output(formatted_data, str(output_path), args.format)

            self.log_success(f"Mobile device searches exported to: {output_path}")
            return str(output_path)

        except Exception as e:
            self.log_error(f"Error saving mobile device searches: {e}")
            return ""

    def export(self, args) -> int:
        """Main export method for mobile device searches"""
        try:
            self.environment = getattr(args, "env", "sandbox")
            self.log_info("Starting mobile device searches export")

            # Fetch data
            searches = self.fetch_data(args)
            if not searches:
                return 1

            # Format data
            formatted_data = self.format_data(searches, args)
            if not formatted_data:
                return 1

            # Save data
            output_path = self.save_data(formatted_data, args)
            if not output_path:
                return 1

            self.log_success(f"✅ Mobile device searches export completed successfully")
            self.log_info(
                f"📁 Exported {len(formatted_data)} searches to: {output_path}"
            )

            return 0

        except Exception as e:
            self.log_error(f"Error exporting mobile device searches: {e}")
            return 1
