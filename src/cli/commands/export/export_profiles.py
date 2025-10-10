#!/usr/bin/env python3
"""
Profile Export Handler for jpapi CLI
Handles export of macOS and iOS configuration profiles
"""

from typing import Dict, Any, List
from argparse import Namespace
from .export_base import ExportBase
from .profile_analyzers import ProfileAnalyzerFactory
from core.logging.command_mixin import log_operation, with_progress
from src.lib.utils import create_jamf_hyperlink


class ExportProfiles(ExportBase):
    """Handler for exporting configuration profiles"""

    def __init__(self, auth, profile_type: str):
        super().__init__(auth, f"{profile_type} profiles")
        self.profile_type = profile_type

        if profile_type == "macos":
            self.endpoint = "/JSSResource/osxconfigurationprofiles"
            self.detail_endpoint = "/JSSResource/osxconfigurationprofiles"
            self.response_key = "os_x_configuration_profiles"
            self.item_key = "os_x_configuration_profile"
        else:  # ios
            self.endpoint = "/JSSResource/mobiledeviceconfigurationprofiles"
            self.detail_endpoint = "/JSSResource/mobiledeviceconfigurationprofiles"
            self.response_key = "mobile_device_configuration_profiles"
            self.item_key = "mobile_device_configuration_profile"

    @log_operation("Profile Data Fetch")
    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch profile data from JAMF API"""
        self.log_info(f"Fetching {self.profile_type} profiles from JAMF API")
        response = self.auth.api_request("GET", self.endpoint)

        if self.response_key not in response:
            self.log_warning(f"No {self.profile_type} profiles found in API response")
            return []

        profiles = response[self.response_key]

        # Handle both list and dict formats
        if isinstance(profiles, dict) and self.item_key in profiles:
            profiles = profiles[self.item_key]

        result = profiles if isinstance(profiles, list) else []
        self.log_success(f"Found {len(result)} {self.profile_type} profiles")
        return result

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format profile data for export"""
        export_data = []
        downloaded_files = []

        # Apply filtering if specified (before detailed processing)
        if hasattr(args, "filter") and args.filter:
            from src.lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(data)

            # Try filtering by ID first, then by name if no matches
            id_filtered = filter_obj.filter_objects(data, "id", args.filter)
            if id_filtered:
                data = id_filtered
                print(
                    f"🔍 Filtered by ID from {original_count} to {len(data)} {self.profile_type} profiles"
                )
            else:
                data = filter_obj.filter_objects(data, "name", args.filter)
                print(
                    f"🔍 Filtered by name from {original_count} to {len(data)} {self.profile_type} profiles"
                )

        for i, profile in enumerate(data):
            print(
                f"   Processing {self.profile_type} profile {i+1}/{len(data)}: {profile.get('name', 'Unknown')}"
            )

            # Basic profile data
            profile_data = self._get_basic_profile_data(
                profile, getattr(args, "env", "dev")
            )

            # Always add detailed info for config profiles (comprehensive analysis)
            if profile.get("id"):
                detailed_data = self._get_detailed_profile_data(profile["id"])
                if detailed_data:
                    profile_data.update(detailed_data)

            # Always create individual profile JSON files for comprehensive export
            if profile.get("id"):
                profile_file = self._download_profile_file(profile)
                if profile_file:
                    profile_data["profile_file"] = profile_file
                    downloaded_files.append(profile_file)

            export_data.append(profile_data)

        # Store downloaded files for summary
        if downloaded_files:
            self._downloaded_files = downloaded_files

        return export_data

    def _get_basic_profile_data(
        self, profile: Dict[str, Any], environment: str = "dev"
    ) -> Dict[str, Any]:
        """Get basic profile information with enhanced data collection"""
        # Initialize with all possible fields to ensure CSV consistency
        return {
            "delete": "",  # Empty column for manual deletion tracking
            "ID": create_jamf_hyperlink("profiles", profile.get("id", ""), environment),
            "Name": profile.get("name", ""),
            "Description": profile.get("description", ""),
            "Category": (
                profile.get("category", {}).get("name", "")
                if isinstance(profile.get("category"), dict)
                else profile.get("category", "")
            ),
            "Site": (
                profile.get("site", {}).get("name", "")
                if isinstance(profile.get("site"), dict)
                else profile.get("site", "")
            ),
            "Distribution Method": profile.get("distribution_method", ""),
            "User Removal": profile.get("user_removable", False),
            "Level": profile.get("level", ""),
            "UUID": profile.get("uuid", ""),
            "Redeploy on Update": profile.get("redeploy_on_update", ""),
            "Created Date": profile.get("created", ""),
            "Modified Date": profile.get("modified", ""),
            "Version": profile.get("version", ""),
            "profile_file": "",  # Will be set below
            # Initialize all detailed fields to empty values
            "General UUID": "",
            "Scope All Computers": "",
            "Scope All Mobile Devices": "",
            "Scope All JSS Users": "",
            "Computer Group Names": "",
            "Computer Group IDs": "",
            "Building Names": "",
            "Building IDs": "",
            "Department Names": "",
            "Department IDs": "",
            "Excluded Computer Names": "",
            "Excluded Computer Count": "",
            "Excluded Group Names": "",
            "Limited User Names": "",
            "Limited User Count": "",
            "Self Service Display Name": "",
            "Install Button Text": "",
            "User Licensed": "",
            "Feature on Main Page": "",
            "Self Service Description": "",
            "Payload Count": "",
            "Payload Types": "",
            "Payload Organizations": "",
            "Payload Identifiers": "",
            "Specific Payload Types": "",
            "PPPC Services": "",
            "Has Screen Saver Password": "",
            "Has Auto Unlock Setting": "",
            "Has Full Disk Access": "",
        }

    def _get_detailed_profile_data(self, profile_id: str) -> Dict[str, Any]:
        """Get comprehensive detailed profile information from actual JSON data"""
        detail = self._get_detailed_info(profile_id, self.detail_endpoint)
        if not detail:
            return {}

        detailed_data = {}

        # Extract general information
        general = detail.get("general", {})
        detailed_data.update(
            {
                "General UUID": general.get("uuid", ""),
                "Redeploy on Update": general.get("redeploy_on_update", ""),
                "Created Date": general.get("created", ""),
                "Modified Date": general.get("modified", ""),
                "Version": general.get("version", ""),
            }
        )

        # Extract scope information
        scope = detail.get("scope", {})
        detailed_data.update(
            {
                "Scope All Computers": scope.get("all_computers", False),
                "Scope All Mobile Devices": scope.get("all_mobile_devices", False),
                "Scope All JSS Users": scope.get("all_jss_users", False),
            }
        )

        # Extract computer groups
        computer_groups = scope.get("computer_groups", []) or scope.get(
            "mobile_device_groups", []
        )
        if computer_groups:
            detailed_data["Computer Group Names"] = ", ".join(
                [g.get("name", "") for g in computer_groups]
            )
            detailed_data["Computer Group IDs"] = ", ".join(
                [str(g.get("id", "")) for g in computer_groups]
            )

        # Extract buildings
        buildings = scope.get("buildings", [])
        if buildings:
            detailed_data["Building Names"] = ", ".join(
                [b.get("name", "") for b in buildings]
            )
            detailed_data["Building IDs"] = ", ".join(
                [str(b.get("id", "")) for b in buildings]
            )

        # Extract departments
        departments = scope.get("departments", [])
        if departments:
            detailed_data["Department Names"] = ", ".join(
                [d.get("name", "") for d in departments]
            )
            detailed_data["Department IDs"] = ", ".join(
                [str(d.get("id", "")) for d in departments]
            )

        # Extract exclusions
        exclusions = scope.get("exclusions", {})
        excluded_computers = exclusions.get("computers", []) or exclusions.get(
            "mobile_devices", []
        )
        if excluded_computers:
            detailed_data["Excluded Computer Names"] = ", ".join(
                [c.get("name", "") for c in excluded_computers[:10]]
            )  # Limit to first 10
            detailed_data["Excluded Computer Count"] = len(excluded_computers)

        excluded_groups = exclusions.get("computer_groups", []) or exclusions.get(
            "mobile_device_groups", []
        )
        if excluded_groups:
            detailed_data["Excluded Group Names"] = ", ".join(
                [g.get("name", "") for g in excluded_groups]
            )

        # Extract limitations
        limitations = scope.get("limitations", {})
        limited_users = limitations.get("users", [])
        if limited_users:
            detailed_data["Limited User Names"] = ", ".join(
                [u.get("name", "") for u in limited_users[:10]]
            )  # Limit to first 10
            detailed_data["Limited User Count"] = len(limited_users)

        # Extract self service information
        self_service = detail.get("self_service", {})
        detailed_data.update(
            {
                "Self Service Display Name": self_service.get(
                    "self_service_display_name", ""
                ),
                "Install Button Text": self_service.get("install_button_text", ""),
                "User Licensed": self_service.get("user_licensed", False),
                "Feature on Main Page": self_service.get("feature_on_main_page", False),
                "Self Service Description": self_service.get(
                    "self_service_description", ""
                ),
            }
        )

        # Extract payload information from the XML payloads string
        payloads_xml = general.get("payloads", "")
        if payloads_xml:
            detailed_data.update(self._extract_payload_data(payloads_xml))

        return detailed_data

    def _extract_payload_data(self, payloads_xml: str) -> Dict[str, Any]:
        """Extract meaningful data from the payloads XML using regex"""
        import re

        payload_data = {
            "Payload Count": 0,
            "Payload Types": "",
            "Payload Organizations": "",
            "Payload Identifiers": "",
        }

        # Count payloads
        payload_count = payloads_xml.count("<key>PayloadType</key>")
        payload_data["Payload Count"] = payload_count

        # Extract payload types
        payload_types = re.findall(
            r"<key>PayloadType</key>\s*<string>([^<]+)</string>", payloads_xml
        )
        payload_data["Payload Types"] = ", ".join(set(payload_types))

        # Extract organizations
        organizations = re.findall(
            r"<key>PayloadOrganization</key>\s*<string>([^<]+)</string>", payloads_xml
        )
        payload_data["Payload Organizations"] = ", ".join(set(organizations))

        # Extract identifiers
        identifiers = re.findall(
            r"<key>PayloadIdentifier</key>\s*<string>([^<]+)</string>", payloads_xml
        )
        payload_data["Payload Identifiers"] = ", ".join(
            identifiers[:5]
        )  # Limit to first 5

        # Extract specific payload details
        payload_data.update(self._extract_specific_payloads_regex(payloads_xml))

        return payload_data

    def _extract_specific_payloads_regex(self, payloads_xml: str) -> Dict[str, Any]:
        """Extract specific payload information using regex"""
        import re

        specific_data = {}

        # Look for specific payload types and their configurations
        payload_types = [
            "com.apple.TCC.configuration-profile-policy",
            "com.apple.applicationaccess",
            "com.apple.loginwindow",
            "com.apple.screensaver",
            "com.apple.security.firewall",
            "com.apple.systempolicy.control",
            "com.apple.MCX",
            "com.apple.Safari",
            "com.apple.SoftwareUpdate",
            "com.apple.Terminal",
        ]

        found_types = []
        for payload_type in payload_types:
            if payload_type in payloads_xml:
                found_types.append(payload_type.replace("com.apple.", ""))

        specific_data["Specific Payload Types"] = ", ".join(found_types)

        # Look for PPPC services
        pppc_services = re.findall(
            r"<key>(SystemPolicy[^<]+|Photos|Calendar|AddressBook|Reminders)</key>",
            payloads_xml,
        )
        if pppc_services:
            specific_data["PPPC Services"] = ", ".join(set(pppc_services))

        # Look for specific settings
        if "askForPassword" in payloads_xml:
            specific_data["Has Screen Saver Password"] = True
        if "allowAutoUnlock" in payloads_xml:
            specific_data["Has Auto Unlock Setting"] = True
        if "SystemPolicyAllFiles" in payloads_xml:
            specific_data["Has Full Disk Access"] = True

        return specific_data

    def _download_profile_file(self, profile: Dict[str, Any]) -> str:
        """Download individual profile file as JSON"""
        try:
            # Get detailed profile info
            detail_response = self.auth.api_request(
                "GET", f'{self.detail_endpoint}/id/{profile.get("id")}'
            )

            if self.item_key in detail_response:
                detail_profile = detail_response[self.item_key]

                # Create safe filename
                safe_name = self._create_safe_filename(
                    profile.get("name", ""), profile.get("id", ""), "json"
                )

                # Save profile file as JSON
                import json

                profile_file = self._download_file(
                    json.dumps(detail_profile, indent=2),
                    safe_name,
                    f"data/csv-exports/{self.profile_type}-profiles",
                )

                # Return relative path format to match expected CSV format
                return f"data/csv-exports/{self.profile_type}-profiles/{safe_name}"
            else:
                print(f"   ⚠️ No detailed profile data for: {profile.get('name', '')}")
                return ""

        except Exception as e:
            print(f"   ⚠️ Failed to download {profile.get('name', '')}: {e}")
            return ""

    def export(self, args: Namespace) -> int:
        """Override export to handle downloaded files summary"""
        result = super().export(args)

        # Show downloaded files summary if any
        if hasattr(self, "_downloaded_files") and self._downloaded_files:
            print(
                f"📁 Downloaded {len(self._downloaded_files)} {self.profile_type} profile files"
            )
            print(f"   Files saved to: data/csv-exports/{self.profile_type}-profiles")
            print(f"\n📋 Downloaded Files:")
            for file_path in self._downloaded_files[:10]:  # Show first 10
                print(f"   {file_path}")
            if len(self._downloaded_files) > 10:
                print(f"   ... and {len(self._downloaded_files) - 10} more files")

        return result


class ExportAllProfiles(ExportBase):
    """Handler for exporting all configuration profiles (macOS and iOS)"""

    def __init__(self, auth):
        super().__init__(auth, "all profiles")
        self.macos_handler = ProfileExportHandler(auth, "macos")
        self.ios_handler = ProfileExportHandler(auth, "ios")

    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch all profile data"""
        # This handler doesn't fetch data directly, it delegates to sub-handlers
        return []

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format all profile data"""
        # This handler doesn't format data directly, it delegates to sub-handlers
        return []

    def export(self, args: Namespace) -> int:
        """Export all configuration profiles"""
        try:
            print("📤 Exporting All Configuration Profiles...")

            # Export macOS profiles
            print("   📱 Exporting macOS profiles...")
            macos_result = self.macos_handler.export(args)

            # Export iOS profiles
            print("   📱 Exporting iOS profiles...")
            ios_result = self.ios_handler.export(args)

            if macos_result == 0 and ios_result == 0:
                print("\n✅ Exported all configuration profiles successfully")
                return 0
            else:
                print("\n⚠️ Some profile exports completed with warnings")
                return 1

        except Exception as e:
            return self._handle_error(e)
