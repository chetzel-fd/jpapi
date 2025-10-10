#!/usr/bin/env python3
"""
Mobile Device Search Manager for JPAPI
Handles advanced mobile device searches using JAMF Pro API v1 endpoints
"""

from typing import Dict, List, Any, Optional
from core.auth.login_manager import UnifiedJamfAuth
from core.logging.command_mixin import log_operation


class MobileSearchManager:
    """Manager for advanced mobile device searches using API v1 endpoints"""

    def __init__(self, auth: UnifiedJamfAuth):
        self.auth = auth
        self.base_endpoint = "/api/v1/advanced-mobile-device-searches"

    @log_operation("Get Mobile Searches")
    def get_all_searches(self) -> List[Dict[str, Any]]:
        """Get all advanced mobile device searches"""
        try:
            response = self.auth.api_request("GET", self.base_endpoint)
            if "results" in response:
                return response["results"]
            return []
        except Exception as e:
            print(f"❌ Error fetching mobile searches: {e}")
            return []

    @log_operation("Get Search by ID")
    def get_search_by_id(self, search_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific advanced mobile device search by ID"""
        try:
            response = self.auth.api_request("GET", f"{self.base_endpoint}/{search_id}")
            return response
        except Exception as e:
            print(f"❌ Error fetching search {search_id}: {e}")
            return None

    @log_operation("Get Search Criteria Choices")
    def get_criteria_choices(self) -> Dict[str, Any]:
        """Get available criteria choices for mobile device searches"""
        try:
            response = self.auth.api_request("GET", f"{self.base_endpoint}/choices")
            return response
        except Exception as e:
            print(f"❌ Error fetching criteria choices: {e}")
            return {}

    @log_operation("Create Mobile Search")
    def create_search(self, search_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new advanced mobile device search"""
        try:
            response = self.auth.api_request(
                "POST", self.base_endpoint, data=search_data
            )
            return response
        except Exception as e:
            print(f"❌ Error creating search: {e}")
            return None

    @log_operation("Update Mobile Search")
    def update_search(
        self, search_id: int, search_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing advanced mobile device search"""
        try:
            response = self.auth.api_request(
                "PUT", f"{self.base_endpoint}/{search_id}", data=search_data
            )
            return response
        except Exception as e:
            print(f"❌ Error updating search {search_id}: {e}")
            return None

    @log_operation("Delete Mobile Search")
    def delete_search(self, search_id: int) -> bool:
        """Delete a specific advanced mobile device search"""
        try:
            self.auth.api_request("DELETE", f"{self.base_endpoint}/{search_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting search {search_id}: {e}")
            return False

    @log_operation("Delete Multiple Mobile Searches")
    def delete_multiple_searches(self, search_ids: List[int]) -> bool:
        """Delete multiple advanced mobile device searches"""
        try:
            data = {"ids": search_ids}
            self.auth.api_request(
                "POST", f"{self.base_endpoint}/delete-multiple", data=data
            )
            return True
        except Exception as e:
            print(f"❌ Error deleting multiple searches: {e}")
            return False

    def format_search_for_display(self, search: Dict[str, Any]) -> Dict[str, Any]:
        """Format a search object for display"""
        return {
            "ID": search.get("id", ""),
            "Name": search.get("name", ""),
            "Description": search.get("description", ""),
            "Site": (
                search.get("site", {}).get("name", "")
                if isinstance(search.get("site"), dict)
                else search.get("site", "")
            ),
            "Criteria Count": len(search.get("criteria", [])),
            "Display Fields": len(search.get("displayFields", [])),
            "Created": search.get("created", ""),
            "Modified": search.get("modified", ""),
        }

    def create_search_template(
        self,
        name: str,
        description: str = "",
        criteria: List[Dict[str, Any]] = None,
        display_fields: List[str] = None,
    ) -> Dict[str, Any]:
        """Create a search template with common structure"""
        template = {
            "name": name,
            "description": description,
            "criteria": criteria or [],
            "displayFields": display_fields
            or [
                "Device Name",
                "Serial Number",
                "UDID",
                "Model",
                "OS Version",
                "Last Inventory Update",
            ],
        }
        return template

    def get_common_criteria_choices(self) -> Dict[str, List[str]]:
        """Get commonly used criteria choices for mobile device searches"""
        try:
            choices = self.get_criteria_choices()
            common_choices = {}

            # Extract common criteria types
            if "criteria" in choices:
                for criterion in choices["criteria"]:
                    if "name" in criterion and "choices" in criterion:
                        common_choices[criterion["name"]] = criterion["choices"]

            return common_choices
        except Exception:
            # Fallback to common criteria if API call fails
            return {
                "Device Name": ["is", "is not", "like", "not like"],
                "Model": ["is", "is not", "like", "not like"],
                "OS Version": [
                    "is",
                    "is not",
                    "like",
                    "not like",
                    "greater than",
                    "less than",
                ],
                "Serial Number": ["is", "is not", "like", "not like"],
                "UDID": ["is", "is not", "like", "not like"],
                "Last Inventory Update": [
                    "is",
                    "is not",
                    "like",
                    "not like",
                    "greater than",
                    "less than",
                ],
                "Supervised": ["is", "is not"],
                "Managed": ["is", "is not"],
            }
