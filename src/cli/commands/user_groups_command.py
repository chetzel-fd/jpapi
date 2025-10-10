#!/usr/bin/env python3
"""
User Groups Command for jpapi CLI
Handles smart and static user groups
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


class UserGroupsCommand(BaseCommand):
    """User groups command for JAMF Pro user group functionality"""

    def __init__(self):
        super().__init__(
            name="user-groups",
            description="👥 User groups (smart and static user groups)",
        )
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup conversational patterns for user groups"""

        # Smart user groups
        self.add_conversational_pattern(
            pattern="smart groups",
            handler="_list_smart_groups",
            description="List smart user groups",
            aliases=["smart", "dynamic groups"],
        )

        # Static user groups
        self.add_conversational_pattern(
            pattern="static groups",
            handler="_list_static_groups",
            description="List static user groups",
            aliases=["static", "manual groups"],
        )

        # All user groups
        self.add_conversational_pattern(
            pattern="all groups",
            handler="_list_all_groups",
            description="List all user groups",
            aliases=["all", "groups"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        super().add_arguments(parser)

        # Add group type filtering
        parser.add_argument(
            "--type",
            choices=["smart", "static", "all"],
            default="all",
            help="Filter by group type",
        )

        # Add site filtering
        parser.add_argument(
            "--site",
            help="Filter by site name",
        )

    def _list_smart_groups(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List smart user groups"""
        return self._list_groups("smart", args)

    def _list_static_groups(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List static user groups"""
        return self._list_groups("static", args)

    def _list_all_groups(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List all user groups"""
        return self._list_groups("all", args)

    def _list_groups(self, group_type: str, args: Namespace) -> int:
        """Generic method to list user groups"""
        try:
            # API endpoint mapping
            endpoints = {
                "smart": "/JSSResource/smartusergroups",
                "static": "/JSSResource/staticusergroups",
            }

            if group_type == "all":
                # List all types
                all_groups = []
                for group_type_name, endpoint in endpoints.items():
                    groups = self._fetch_groups(endpoint, group_type_name)
                    all_groups.extend(groups)
                groups = all_groups
            else:
                endpoint = endpoints.get(group_type)
                if not endpoint:
                    print(f"❌ Unknown group type: {group_type}")
                    return 1
                groups = self._fetch_groups(endpoint, group_type)

            if not groups:
                print(f"❌ No {group_type} user groups found")
                return 1

            # Apply filtering
            filtered_groups = self._apply_group_filters(groups, args)

            # Format and output
            formatted_data = self._format_groups_for_display(
                filtered_groups, args
            )
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)

            print(f"\n✅ Found {len(filtered_groups)} {group_type} user groups")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _fetch_groups(self, endpoint: str, group_type: str) -> List[Dict[str, Any]]:
        """Fetch groups from API endpoint"""
        print(f"👥 Fetching {group_type} user groups...")
        response = self.auth.api_request("GET", endpoint)

        # Extract groups from response based on type
        if group_type == "smart":
            if "user_groups" in response:
                groups_data = response["user_groups"]
                if "user_group" in groups_data:
                    groups = groups_data["user_group"]
                    return groups if isinstance(groups, list) else [groups]

        elif group_type == "static":
            if "user_groups" in response:
                groups_data = response["user_groups"]
                if "user_group" in groups_data:
                    groups = groups_data["user_group"]
                    return groups if isinstance(groups, list) else [groups]

        return []

    def _apply_group_filters(
        self, groups: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Apply filters to groups"""
        filtered = groups

        # Name filtering
        if hasattr(args, "filter") and args.filter:
            from src.lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(filtered)
            filtered = filter_obj.filter_objects(filtered, "name", args.filter)
            print(f"🔍 Filtered from {original_count} to {len(filtered)} groups")

        # Site filtering
        if hasattr(args, "site") and args.site:
            filtered = [
                group for group in filtered
                if self._group_matches_site(group, args.site)
            ]

        return filtered

    def _group_matches_site(self, group: Dict[str, Any], site_name: str) -> bool:
        """Check if group matches site filter"""
        if "site" in group:
            site = group["site"]
            if isinstance(site, dict):
                return site_name.lower() in site.get("name", "").lower()
            else:
                return site_name.lower() in str(site).lower()
        return False

    def _format_groups_for_display(
        self, groups: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format groups for display"""
        if not groups:
            return []

        formatted = []
        for group in groups:
            formatted_group = {
                "ID": group.get("id", ""),
                "Name": group.get("name", ""),
                "Type": self._determine_group_type(group),
                "Smart": group.get("is_smart", False),
                "Site": self._get_group_site(group),
            }

            # Add detailed fields if requested
            if hasattr(args, "detailed") and args.detailed:
                if "description" in group:
                    formatted_group["Description"] = group.get("description", "")

                if "criteria" in group and group["criteria"]:
                    criteria_count = len(group["criteria"]) if isinstance(group["criteria"], list) else 1
                    formatted_group["Criteria Count"] = criteria_count

                if "users" in group and group["users"]:
                    users_count = len(group["users"]) if isinstance(group["users"], list) else 1
                    formatted_group["User Count"] = users_count

                if "user_additions" in group and group["user_additions"]:
                    additions_count = len(group["user_additions"]) if isinstance(group["user_additions"], list) else 1
                    formatted_group["User Additions"] = additions_count

                if "user_deletions" in group and group["user_deletions"]:
                    deletions_count = len(group["user_deletions"]) if isinstance(group["user_deletions"], list) else 1
                    formatted_group["User Deletions"] = deletions_count

            formatted.append(formatted_group)

        return formatted

    def _determine_group_type(self, group: Dict[str, Any]) -> str:
        """Determine group type from group data"""
        # This is a simplified approach - in practice, you might need to track
        # the source endpoint or add metadata to determine the type
        if "smartusergroups" in str(group) or group.get("is_smart", False):
            return "Smart"
        elif "staticusergroups" in str(group) or not group.get("is_smart", True):
            return "Static"
        else:
            return "Unknown"

    def _get_group_site(self, group: Dict[str, Any]) -> str:
        """Get site name from group"""
        if "site" in group:
            site = group["site"]
            if isinstance(site, dict):
                return site.get("name", "")
            else:
                return str(site)
        return ""
