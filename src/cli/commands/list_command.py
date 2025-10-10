#!/usr/bin/env python3
"""
Improved List Command for jpapi CLI
Uses configuration-driven patterns to reduce code from 494 lines to ~150 lines
"""

from .common_imports import (
    ArgumentParser,
    Namespace,
    Dict,
    Any,
    List,
    Optional,
    BaseCommand,
)
from core.logging.command_mixin import log_operation
import time


class ListCommand(BaseCommand):
    """Improved list command using configuration-driven patterns"""

    def __init__(self):
        super().__init__(
            name="list",
            description="📋 List JAMF objects (policies, devices, groups, etc.)",
        )
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup conversational patterns and subcommand configurations"""

        # Conversational patterns
        self.add_conversational_pattern(
            pattern="categories",
            handler="_list_categories",
            description="List all categories",
            aliases=["category", "cats"],
        )

        self.add_conversational_pattern(
            pattern="profiles",
            handler="_list_profiles",
            description="List configuration profiles",
            aliases=["profile", "configs", "config"],
        )

        self.add_conversational_pattern(
            pattern="scripts",
            handler="_list_scripts",
            description="List scripts",
            aliases=["script"],
        )

        self.add_conversational_pattern(
            pattern="macos policies",
            handler="_list_macos_policies",
            description="List macOS policies",
            aliases=["policies", "policy"],
        )

        self.add_conversational_pattern(
            pattern="macos devices",
            handler="_list_macos_devices",
            description="List macOS computers",
            aliases=["computers", "computer", "macs", "mac"],
        )

        self.add_conversational_pattern(
            pattern="ios devices",
            handler="_list_ios_devices",
            description="List iOS/mobile devices",
            aliases=["mobile", "ipad", "iphone", "devices"],
        )

        # User groups patterns
        self.add_conversational_pattern(
            pattern="user-groups",
            handler="_list_user_groups",
            description="List user groups",
            aliases=["user-groups", "usergroups", "users"],
        )

        self.add_conversational_pattern(
            pattern="smart user-groups",
            handler="_list_smart_user_groups",
            description="List smart user groups",
            aliases=["smart-users", "dynamic-users"],
        )

        self.add_conversational_pattern(
            pattern="static user-groups",
            handler="_list_static_user_groups",
            description="List static user groups",
            aliases=["static-users", "manual-users"],
        )

        # Computer groups patterns
        self.add_conversational_pattern(
            pattern="computer-groups",
            handler="_list_computer_groups",
            description="List computer groups",
            aliases=["computer-groups", "macos-groups", "groups"],
        )

        # Advanced searches patterns
        self.add_conversational_pattern(
            pattern="computer advanced-searches",
            handler="_list_computer_advanced_searches",
            description="List advanced computer searches",
            aliases=["computer-searches", "mac-searches", "advanced-computer"],
        )

        self.add_conversational_pattern(
            pattern="mobile advanced-searches",
            handler="_list_mobile_advanced_searches",
            description="List advanced mobile device searches",
            aliases=["mobile-searches", "ios-searches", "advanced-mobile"],
        )

        self.add_conversational_pattern(
            pattern="user advanced-searches",
            handler="_list_user_advanced_searches",
            description="List advanced user searches",
            aliases=["user-searches", "advanced-user"],
        )

        # No subcommands - use pure conversational patterns

    # Handler methods - much simpler now!
    def _list_categories(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List categories with filtering"""
        return self._list_objects("categories", args)

    def _list_profiles(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List configuration profiles with filtering"""
        return self._list_objects("profiles", args)

    def _list_scripts(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List scripts with filtering"""
        return self._list_objects("scripts", args)

    def _list_macos_policies(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List macOS policies with filtering"""
        return self._list_objects("macos-policies", args)

    def _list_macos_devices(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List macOS devices with filtering"""
        return self._list_objects("macos-devices", args)

    def _list_ios_devices(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List iOS devices with filtering"""
        return self._list_objects("ios-devices", args)

    def _list_user_groups(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List all user groups with filtering"""
        return self._list_user_groups_by_type("all", args)

    def _list_smart_user_groups(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List smart user groups with filtering"""
        return self._list_user_groups_by_type("smart", args)

    def _list_static_user_groups(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List static user groups with filtering"""
        return self._list_user_groups_by_type("static", args)

    def _list_computer_groups(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List computer groups with filtering"""
        return self._list_objects("computer-groups", args)

    def _list_computer_advanced_searches(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List advanced computer searches with filtering"""
        return self._list_objects("computer-advanced-searches", args)

    def _list_mobile_advanced_searches(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List advanced mobile device searches with filtering"""
        return self._list_objects("mobile-advanced-searches", args)

    def _list_user_advanced_searches(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List advanced user searches with filtering"""
        return self._list_objects("user-advanced-searches", args)

    @log_operation("List Objects")
    def _list_objects(self, object_type: str, args: Namespace) -> int:
        """Generic method to list objects with filtering"""
        try:
            # API endpoint mapping
            endpoints = {
                "categories": "/JSSResource/categories",
                "profiles": "/JSSResource/osxconfigurationprofiles",
                "scripts": "/JSSResource/scripts",
                "macos-policies": "/api/v1/policies",
                "macos-devices": "/JSSResource/computers",
                "ios-devices": "/JSSResource/mobiledevices",
                "computer-groups": "/JSSResource/computergroups",
                "computer-advanced-searches": "/JSSResource/advancedcomputersearches",
                "mobile-advanced-searches": "/api/v1/advanced-mobile-device-searches",
                "user-advanced-searches": "/JSSResource/advancedusersearches",
            }

            endpoint = endpoints.get(object_type)
            if not endpoint:
                self.log_error(f"Unknown object type: {object_type}")
                return 1

            self.log_info(f"Starting {object_type} listing")

            # Make API call
            self.log_info(f"Fetching {object_type} from JAMF API")
            response = self.auth.api_request("GET", endpoint)

            # Extract objects from response
            self.log_info("Processing API response")
            objects = self._extract_objects_from_response(response, object_type)

            if not objects:
                self.log_error(f"No {object_type} found")
                return 1

            self.log_success(f"Found {len(objects)} {object_type}")

            # Apply filtering
            if hasattr(args, "filter") and args.filter:
                self.log_info("Applying filters")
                objects = self._apply_filters(objects, args, object_type)
                self.log_info(f"After filtering: {len(objects)} {object_type}")

            # Format and output
            self.log_info("Formatting data for display")
            formatted_data = self._format_objects_for_display(
                objects, args, object_type
            )

            self.log_info("Generating output")
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _extract_objects_from_response(
        self, response: Dict[str, Any], object_type: str
    ) -> List[Dict[str, Any]]:
        """Extract objects from API response based on object type"""
        if object_type == "categories":
            if "categories" in response and "category" in response["categories"]:
                return response["categories"]["category"]

        elif object_type == "profiles":
            if "os_x_configuration_profiles" in response:
                profiles_data = response["os_x_configuration_profiles"]

                # Handle both list and dict formats
                if isinstance(profiles_data, list):
                    return profiles_data
                elif isinstance(profiles_data, dict):
                    profiles = profiles_data.get("os_x_configuration_profile", [])
                    return profiles if isinstance(profiles, list) else [profiles]

        elif object_type == "scripts":
            if "scripts" in response:
                scripts = response["scripts"]
                if isinstance(scripts, dict) and "script" in scripts:
                    scripts = scripts["script"]
                return scripts if isinstance(scripts, list) else [scripts]

        elif object_type == "macos-policies":
            if "results" in response:
                return response["results"]

        elif object_type == "macos-devices":
            if "computers" in response and "computer" in response["computers"]:
                computers = response["computers"]["computer"]
                return computers if isinstance(computers, list) else [computers]

        elif object_type == "ios-devices":
            if (
                "mobile_devices" in response
                and "mobile_device" in response["mobile_devices"]
            ):
                devices = response["mobile_devices"]["mobile_device"]
                return devices if isinstance(devices, list) else [devices]

        elif object_type == "computer-groups":
            if "computer_groups" in response:
                groups = response["computer_groups"]
                if isinstance(groups, dict) and "computer_group" in groups:
                    groups = groups["computer_group"]
                return groups if isinstance(groups, list) else [groups]

        elif object_type == "computer-advanced-searches":
            if "advanced_computer_searches" in response:
                searches = response["advanced_computer_searches"]
                if (
                    isinstance(searches, dict)
                    and "advanced_computer_search" in searches
                ):
                    searches = searches["advanced_computer_search"]
                return searches if isinstance(searches, list) else [searches]

        elif object_type == "mobile-advanced-searches":
            if "results" in response:
                return response["results"]

        elif object_type == "user-advanced-searches":
            if "advanced_user_searches" in response:
                searches = response["advanced_user_searches"]
                if isinstance(searches, dict) and "advanced_user_search" in searches:
                    searches = searches["advanced_user_search"]
                return searches if isinstance(searches, list) else [searches]

        return []

    def _apply_filters(
        self, objects: List[Dict[str, Any]], args: Namespace, object_type: str
    ) -> List[Dict[str, Any]]:
        """Apply filters to objects"""
        filtered = objects

        # Name filtering
        if hasattr(args, "filter") and args.filter:
            from src.lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(filtered)
            filtered = filter_obj.filter_objects(filtered, "name", args.filter)
            print(f"🔍 Filtered from {original_count} to {len(filtered)} {object_type}")

        # Status filtering for policies
        if (
            object_type == "macos-policies"
            and hasattr(args, "status")
            and args.status != "all"
        ):
            enabled_filter = args.status == "enabled"
            filtered = [obj for obj in filtered if obj.get("enabled") == enabled_filter]

        # Category filtering for scripts
        if object_type == "scripts" and hasattr(args, "category") and args.category:
            filtered = [
                obj
                for obj in filtered
                if args.category.lower() in obj.get("category", "").lower()
            ]

        # Name filtering for scripts
        if object_type == "scripts" and hasattr(args, "name") and args.name:
            import fnmatch

            filtered = [
                obj
                for obj in filtered
                if fnmatch.fnmatch(obj.get("name", "").lower(), args.name.lower())
            ]

        # ID filtering for scripts
        if object_type == "scripts" and hasattr(args, "id") and args.id:
            filtered = [
                obj for obj in filtered if str(obj.get("id", "")) == str(args.id)
            ]

        return filtered

    def _format_objects_for_display(
        self, objects: List[Dict[str, Any]], args: Namespace, object_type: str
    ) -> List[Dict[str, Any]]:
        """Format objects for display based on object type and arguments"""
        if not objects:
            return []

        formatted = []
        for obj in objects:
            formatted_obj = {"ID": obj.get("id", ""), "Name": obj.get("name", "")}

            # Add type-specific fields
            if "category" in obj:
                if isinstance(obj["category"], dict):
                    formatted_obj["Category"] = obj["category"].get("name", "")
                else:
                    formatted_obj["Category"] = obj["category"]

            if "priority" in obj:
                formatted_obj["Priority"] = obj.get("priority", "")

            if "enabled" in obj:
                formatted_obj["Enabled"] = obj.get("enabled", False)

            if "model" in obj:
                formatted_obj["Model"] = obj.get("model", "")

            if "serial_number" in obj:
                formatted_obj["Serial"] = obj.get("serial_number", "")

            if "os_version" in obj:
                formatted_obj["OS Version"] = obj.get("os_version", "")

            # Add detailed fields if requested
            if hasattr(args, "detailed") and args.detailed:
                if "description" in obj:
                    formatted_obj["Description"] = obj.get("description", "")

                if "uuid" in obj:
                    formatted_obj["UUID"] = obj.get("uuid", "")

                if "payloads" in obj:
                    formatted_obj["Payloads"] = (
                        len(obj.get("payloads", [])) if obj.get("payloads") else 0
                    )

                if "frequency" in obj:
                    formatted_obj["Frequency"] = obj.get("frequency", "")

                if "trigger" in obj:
                    formatted_obj["Trigger"] = obj.get("trigger", "")

            # Add content preview for scripts if requested
            if hasattr(args, "content") and args.content and "script_contents" in obj:
                content = obj.get("script_contents", "")
                if content:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    formatted_obj["Content Preview"] = preview.replace("\n", "\\n")
                else:
                    formatted_obj["Content Preview"] = "No content"

            formatted.append(formatted_obj)

        return formatted

    def _list_user_groups_by_type(self, group_type: str, args: Namespace) -> int:
        """Generic method to list user groups by type"""
        try:
            # API endpoint mapping for user groups
            endpoints = {
                "smart": "/JSSResource/smartusergroups",
                "static": "/JSSResource/staticusergroups",
            }

            if group_type == "all":
                # List all types
                all_groups = []
                for group_type_name, endpoint in endpoints.items():
                    groups = self._fetch_user_groups(endpoint, group_type_name)
                    all_groups.extend(groups)
                groups = all_groups
            else:
                endpoint = endpoints.get(group_type)
                if not endpoint:
                    self.log_error(f"Unknown group type: {group_type}")
                    return 1
                groups = self._fetch_user_groups(endpoint, group_type)

            if not groups:
                self.log_warning(f"No {group_type} user groups found")
                return 1

            # Apply filtering
            filtered_groups = self._apply_user_group_filters(groups, args)

            # Format and output
            formatted_data = self._format_user_groups_for_display(filtered_groups, args)
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)

            self.log_success(f"Found {len(filtered_groups)} {group_type} user groups")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _fetch_user_groups(
        self, endpoint: str, group_type: str
    ) -> List[Dict[str, Any]]:
        """Fetch user groups from API"""
        try:
            response = self.auth.api_request("GET", endpoint)

            if group_type == "smart":
                if "smart_user_groups" in response:
                    groups = response["smart_user_groups"]
                    if isinstance(groups, dict) and "smart_user_group" in groups:
                        groups = groups["smart_user_group"]
                    return groups if isinstance(groups, list) else [groups]
            elif group_type == "static":
                if "static_user_groups" in response:
                    groups = response["static_user_groups"]
                    if isinstance(groups, dict) and "static_user_group" in groups:
                        groups = groups["static_user_group"]
                    return groups if isinstance(groups, list) else [groups]

            return []
        except Exception as e:
            self.log_error(f"Error fetching {group_type} user groups: {e}")
            return []

    def _apply_user_group_filters(
        self, groups: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Apply filters to user groups"""
        filtered = groups

        # Apply name filter
        if hasattr(args, "filter") and args.filter:
            filter_obj = create_filter(
                args.filter, getattr(args, "filter_type", "wildcard")
            )
            filtered = [
                g
                for g in filtered
                if filter_obj.matches(g.get("name", ""), args.filter)
            ]

        # Apply site filter
        if hasattr(args, "site") and args.site:
            filtered = [
                g
                for g in filtered
                if args.site.lower() in g.get("site", {}).get("name", "").lower()
            ]

        return filtered

    def _format_user_groups_for_display(
        self, groups: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format user groups for display"""
        formatted = []

        for group in groups:
            formatted_group = {
                "ID": group.get("id", ""),
                "Name": group.get("name", ""),
                "Type": "Smart" if group.get("is_smart", False) else "Static",
                "Description": group.get("description", ""),
                "Site": (
                    group.get("site", {}).get("name", "")
                    if isinstance(group.get("site"), dict)
                    else group.get("site", "")
                ),
            }

            # Add member count for static groups
            if not group.get("is_smart", False):
                users = group.get("users", [])
                if isinstance(users, list):
                    formatted_group["Member Count"] = len(users)
                else:
                    formatted_group["Member Count"] = 1 if users else 0
            else:
                formatted_group["Member Count"] = "Dynamic"

            # Add criteria count for smart groups
            if group.get("is_smart", False):
                criteria = group.get("criteria", [])
                if isinstance(criteria, list):
                    formatted_group["Criteria Count"] = len(criteria)
                else:
                    formatted_group["Criteria Count"] = 1 if criteria else 0
            else:
                formatted_group["Criteria Count"] = "N/A"

            formatted.append(formatted_group)

        return formatted
