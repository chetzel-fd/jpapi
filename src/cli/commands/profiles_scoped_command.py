#!/usr/bin/env python3
"""
List Profiles Scoped Command for jpapi CLI
Handles listing of configuration profiles scoped to all computers
"""

from argparse import ArgumentParser, Namespace
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Using proper package structure via pip install -e .

from base.command import BaseCommand


class ProfilesScopedCommand(BaseCommand):
    """Command for listing configuration profiles scoped to all computers"""

    def __init__(self):
        super().__init__(
            name="list-profiles-scoped",
            description="📋 List configuration profiles scoped to all computers",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command arguments"""
        parser.add_argument(
            "--scope-type",
            choices=["all", "computers", "groups"],
            default="all",
            help="Type of scope to check (default: all)",
        )
        parser.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed profile information including payloads and scope details",
        )
        self.setup_common_args(parser)

    def execute(self, args: Namespace) -> int:
        """Execute the list profiles scoped command"""
        if not self.check_auth(args):
            return 1

        try:
            print("📋 Listing Configuration Profiles Scoped to All Computers...")

            # Get all configuration profiles
            profiles_response = self.auth.api_request(
                "GET", "/JSSResource/osxconfigurationprofiles"
            )

            if "os_x_configuration_profiles" not in profiles_response:
                print("❌ No configuration profiles found")
                return 1

            profiles = profiles_response["os_x_configuration_profiles"]
            if isinstance(profiles, dict) and "os_x_configuration_profile" in profiles:
                profiles = profiles["os_x_configuration_profile"]

            if not isinstance(profiles, list):
                print("❌ Invalid profiles data format")
                return 1

            # Get detailed information for each profile to check scope
            scoped_profiles = []

            for profile_summary in profiles:
                try:
                    profile_id = profile_summary.get("id")
                    if not profile_id:
                        continue

                    # Get detailed profile information
                    profile_detail_response = self.auth.api_request(
                        "GET", f"/JSSResource/osxconfigurationprofiles/id/{profile_id}"
                    )

                    if "os_x_configuration_profile" not in profile_detail_response:
                        continue

                    profile_detail = profile_detail_response[
                        "os_x_configuration_profile"
                    ]

                    # Check if profile is scoped to all computers
                    if self._is_scoped_to_all_computers(
                        profile_detail, args.scope_type
                    ):
                        profile_data = {
                            "ID": profile_detail.get("id", ""),
                            "Name": profile_detail.get("name", ""),
                            "Category": (
                                profile_detail.get("category", {}).get("name", "")
                                if isinstance(profile_detail.get("category"), dict)
                                else profile_detail.get("category", "")
                            ),
                            "Distribution Method": profile_detail.get(
                                "distribution_method", ""
                            ),
                            "User Removable": profile_detail.get(
                                "user_removable", False
                            ),
                            "Level": profile_detail.get("level", ""),
                            "Scope Type": self._get_scope_type(profile_detail),
                        }

                        if args.detailed:
                            scope = profile_detail.get("scope", {})
                            profile_data.update(
                                {
                                    "Description": profile_detail.get(
                                        "description", ""
                                    ),
                                    "UUID": profile_detail.get("uuid", ""),
                                    "Payload Count": len(
                                        profile_detail.get("payloads", [])
                                    ),
                                    "Scoped Computers": len(scope.get("computers", [])),
                                    "Scoped Groups": len(
                                        scope.get("computer_groups", [])
                                    ),
                                    "Scoped Buildings": len(scope.get("buildings", [])),
                                    "Scoped Departments": len(
                                        scope.get("departments", [])
                                    ),
                                }
                            )

                        scoped_profiles.append(profile_data)

                except Exception as e:
                    print(
                        f"⚠️  Error processing profile {profile_summary.get('name', 'Unknown')}: {e}"
                    )
                    continue

            if not scoped_profiles:
                print("❌ No configuration profiles found scoped to all computers")
                return 1

            # Output results
            output = self.format_output(scoped_profiles, args.format)
            self.save_output(output, args.output)

            print(
                f"\n✅ Found {len(scoped_profiles)} configuration profiles scoped to all computers"
            )
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _is_scoped_to_all_computers(
        self, profile: Dict[str, Any], scope_type: str
    ) -> bool:
        """Check if a profile is scoped to all computers"""
        scope = profile.get("scope", {})

        if scope_type == "all":
            # Check if scoped to all computers (no specific computers, groups, buildings, or departments)
            computers = scope.get("computers", [])
            groups = scope.get("computer_groups", [])
            buildings = scope.get("buildings", [])
            departments = scope.get("departments", [])

            # If no specific scope is defined, it's scoped to all computers
            return (
                len(computers) == 0
                and len(groups) == 0
                and len(buildings) == 0
                and len(departments) == 0
            )

        elif scope_type == "computers":
            # Check if scoped to all computers (no specific computers)
            computers = scope.get("computers", [])
            return len(computers) == 0

        elif scope_type == "groups":
            # Check if scoped to all computers (no specific groups)
            groups = scope.get("computer_groups", [])
            return len(groups) == 0

        return False

    def _get_scope_type(self, profile: Dict[str, Any]) -> str:
        """Get the scope type for a profile"""
        scope = profile.get("scope", {})

        computers = scope.get("computers", [])
        groups = scope.get("computer_groups", [])
        buildings = scope.get("buildings", [])
        departments = scope.get("departments", [])

        if (
            len(computers) == 0
            and len(groups) == 0
            and len(buildings) == 0
            and len(departments) == 0
        ):
            return "All Computers"
        elif len(computers) > 0:
            return f"Specific Computers ({len(computers)})"
        elif len(groups) > 0:
            return f"Computer Groups ({len(groups)})"
        elif len(buildings) > 0:
            return f"Buildings ({len(buildings)})"
        elif len(departments) > 0:
            return f"Departments ({len(departments)})"
        else:
            return "Unknown"
