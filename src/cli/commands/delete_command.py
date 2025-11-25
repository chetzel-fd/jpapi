#!/usr/bin/env python3
"""
Delete Command for jpapi CLI
Handles deletion of JAMF objects with production safeguards
"""

from argparse import ArgumentParser, Namespace
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add base to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.command import BaseCommand
from resources.config.api_endpoints import APIRegistry


class DeleteCommand(BaseCommand):
    """Command for deleting JAMF objects"""

    def __init__(self):
        super().__init__(
            name="delete",
            description="🗑️ Delete JAMF objects (policies, profiles, etc.)",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add delete command arguments"""
        subparsers = parser.add_subparsers(
            dest="delete_object", help="Object type to delete"
        )

        # Policy delete command (with aliases)
        policy_parser = subparsers.add_parser(
            "policy", aliases=["policies", "pol"], help="Delete policies"
        )
        policy_parser.add_argument("name_or_id", help="Policy name or ID to delete")
        policy_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(policy_parser)

        # Profile delete command (with aliases)
        profile_parser = subparsers.add_parser(
            "profile",
            aliases=["profiles", "prof"],
            help="Delete configuration profiles",
        )
        profile_parser.add_argument("name_or_id", help="Profile name or ID to delete")
        profile_parser.add_argument(
            "--type",
            choices=["macos", "ios"],
            default="macos",
            help="Profile type (default: macos)",
        )
        profile_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(profile_parser)

        # Script delete command (with aliases)
        script_parser = subparsers.add_parser(
            "script", aliases=["scripts"], help="Delete scripts"
        )
        script_parser.add_argument("name_or_id", help="Script name or ID to delete")
        script_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(script_parser)

        # Package delete command (with aliases)
        package_parser = subparsers.add_parser(
            "package", aliases=["packages", "pkg"], help="Delete packages"
        )
        package_parser.add_argument("name_or_id", help="Package name or ID to delete")
        package_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(package_parser)

        # Group delete command (with aliases)
        group_parser = subparsers.add_parser(
            "group",
            aliases=["groups", "computer-group", "computer-groups"],
            help="Delete computer groups",
        )
        group_parser.add_argument("name_or_id", help="Group name or ID to delete")
        group_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(group_parser)

        # Search delete command (with aliases)
        search_parser = subparsers.add_parser(
            "search",
            aliases=["searches", "advanced-search", "advanced-searches"],
            help="Delete advanced searches",
        )
        search_parser.add_argument("name_or_id", help="Search name or ID to delete")
        search_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(search_parser)

        # Extension attribute delete command
        ext_attr_parser = subparsers.add_parser(
            "extension-attribute",
            aliases=["ext-attr", "attribute"],
            help="Delete extension attributes",
        )
        ext_attr_parser.add_argument("id", help="Extension attribute ID")
        ext_attr_parser.add_argument(
            "--type",
            choices=["computer", "mobile", "user"],
            default="computer",
            help="Attribute type (default: computer)",
        )
        ext_attr_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(ext_attr_parser)

        # Bulk delete command
        bulk_parser = subparsers.add_parser("bulk", help="Delete multiple objects")
        bulk_parser.add_argument(
            "--policies", nargs="+", help="Policy names or IDs to delete"
        )
        bulk_parser.add_argument(
            "--profiles", nargs="+", help="Profile names or IDs to delete"
        )
        bulk_parser.add_argument(
            "--type",
            choices=["macos", "ios"],
            default="macos",
            help="Profile type for bulk deletion (default: macos)",
        )
        bulk_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(bulk_parser)

    def execute(self, args: Namespace) -> int:
        """Execute the delete command"""
        # Set environment on command instance
        if hasattr(args, "env"):
            self.environment = args.env

        # Enhanced production safety warnings
        if self.is_production_environment():
            print("🚨 PRODUCTION ENVIRONMENT DETECTED 🚨")
            print("=" * 60)
            print(f"Environment: {self.environment.upper()}")
            print(f"Timestamp: {self._get_timestamp()}")
            print("=" * 60)
            print("⚠️  WARNING: You are about to DELETE objects in PRODUCTION!")
            print("   • This will permanently remove data from JAMF Pro")
            print("   • Deleted objects cannot be easily recovered")
            print("   • This may affect all managed devices")
            print("   • Use --dry-run to test operations safely")
            print("   • Use --force to skip confirmation prompts")
            print("   • Consider testing in DEV environment first")
            print("=" * 60)
            print()

        if not self.check_auth(args):
            return 1

        # Additional production safety check
        if self.is_production_environment() and not getattr(args, "force", False):
            print("🔍 FINAL PRODUCTION SAFETY CHECK")
            print("=" * 50)
            print("You are about to DELETE objects in PRODUCTION environment.")
            print("This will permanently remove data from JAMF Pro.")
            print()
            print("Before proceeding, confirm:")
            print("1. You have tested this operation in DEV environment")
            print("2. You understand this will permanently delete data")
            print("3. You have proper authorization for this change")
            print("4. You have verified the correct objects to delete")
            print()

            final_confirm = (
                input(
                    "Do you want to proceed with deleting objects in PRODUCTION? (y/N): "
                )
                .strip()
                .lower()
            )
            if final_confirm not in ["y", "yes"]:
                print("❌ Operation cancelled - safety check failed")
                return 1
            print("✅ Final safety check passed")
            print()

        try:
            # Handle subcommand structure
            if not args.delete_object:
                print("🗑️ Delete JAMF Objects:")
                print()
                print("💬 Quick Delete:")
                print("   jpapi delete policy 'Policy Name'")
                print("   jpapi delete profile 'Profile Name'")
                print("   jpapi delete script 'Script Name'")
                print("   jpapi delete package 'Package Name'")
                print("   jpapi delete group 'Group Name'")
                print("   jpapi delete search 'Search Name'")
                print("   jpapi delete bulk --policies 'Policy 1' 'Policy 2'")
                print()
                print("🔧 Available Objects (with aliases):")
                print("   Policies: policy, policies, pol")
                print("   Profiles: profile, profiles, prof")
                print("   Scripts: script, scripts")
                print("   Packages: package, packages, pkg")
                print("   Groups: group, groups, computer-group, computer-groups")
                print(
                    "   Searches: search, searches, advanced-search, advanced-searches"
                )
                print("   Bulk: bulk")
                print()
                print("⚠️  Use --force to skip confirmation prompts")
                return 0

            # Handle policy and its aliases
            if args.delete_object in ["policy", "policies", "pol"]:
                return self._delete_policy(args)
            # Handle profile and its aliases
            elif args.delete_object in ["profile", "profiles", "prof"]:
                return self._delete_profile(args)
            # Handle script and its aliases
            elif args.delete_object in ["script", "scripts"]:
                return self._delete_script(args)
            # Handle package and its aliases
            elif args.delete_object in ["package", "packages", "pkg"]:
                return self._delete_package(args)
            # Handle group and its aliases
            elif args.delete_object in [
                "group",
                "groups",
                "computer-group",
                "computer-groups",
            ]:
                return self._delete_group(args)
            # Handle search and its aliases
            elif args.delete_object in [
                "search",
                "searches",
                "advanced-search",
                "advanced-searches",
            ]:
                return self._delete_search(args)
            # Handle extension-attribute and its aliases
            elif args.delete_object in [
                "extension-attribute",
                "ext-attr",
                "attribute",
            ]:
                return self._delete_extension_attribute(args)
            # Handle bulk delete
            elif args.delete_object == "bulk":
                return self._delete_bulk(args)
            else:
                print(f"❌ Unknown delete object: {args.delete_object}")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _delete_policy(self, args: Namespace) -> int:
        """Delete a policy"""
        try:
            # Find the policy by name or ID
            policy_info = self._find_policy(args.name_or_id)
            if not policy_info:
                print(f"❌ Policy not found: {args.name_or_id}")
                return 1

            policy_id = policy_info.get("id")
            policy_name = policy_info.get("name")

            if not policy_id:
                print(f"❌ Policy ID not found for: {args.name_or_id}")
                return 1

            # Create comprehensive summary for production confirmation
            if self.is_production_environment():
                changes_summary = f"""
Policy Deletion Summary:
  • ID: {policy_id}
  • Name: {policy_name}
  • Enabled: {policy_info.get('enabled', 'Unknown')}
  • Impact: Will permanently delete this policy from PRODUCTION
  • Warning: This action cannot be undone
"""

                if not self.require_production_confirmation(
                    "Delete Policy", f"Deleting policy: {policy_name}", changes_summary
                ):
                    return 1

            print(f"🗑️ Deleting Policy: {policy_name} (ID: {policy_id})")

            # Delete the policy
            response = self.auth.api_request(
                "DELETE", f"/JSSResource/policies/id/{policy_id}"
            )

            if response is not None:
                print(f"✅ Policy deleted successfully!")
                print(f"   ID: {policy_id}")
                print(f"   Name: {policy_name}")
                return 0
            else:
                print(f"❌ Failed to delete policy")
                return 1

        except Exception as e:
            print(f"❌ Error deleting policy: {e}")
            return 1

    def _delete_profile(self, args: Namespace) -> int:
        """Delete a configuration profile"""
        try:
            # Find the profile by name or ID
            profile_info = self._find_profile(args.name_or_id, args.type)
            if not profile_info:
                print(f"❌ Profile not found: {args.name_or_id}")
                return 1

            # Normalize profile id/name from nested or flat structures
            general = (
                profile_info.get("general", {})
                if isinstance(profile_info, dict)
                else {}
            )
            profile_id = (
                general.get("id") if isinstance(general, dict) else None
            ) or profile_info.get("id")
            profile_name = (
                general.get("name") if isinstance(general, dict) else None
            ) or profile_info.get("name")

            if not profile_id:
                print(f"❌ Profile ID not found for: {args.name_or_id}")
                return 1

            # Create comprehensive summary for production confirmation
            if self.is_production_environment():
                changes_summary = f"""
Profile Deletion Summary:
  • ID: {profile_id}
  • Name: {profile_name}
  • Type: {args.type.upper()}
  • Impact: Will permanently delete this profile from PRODUCTION
  • Risk Level: HIGH (permanent data loss)
  • Warning: This action cannot be undone
  • Recovery: Profile must be recreated from scratch
  • Scope Impact: Any devices with this profile will lose configuration
"""

                if not self.require_production_confirmation(
                    "Delete Profile",
                    f"Deleting {args.type} profile: {profile_name}",
                    changes_summary,
                ):
                    return 1

            print(f"🗑️ Deleting Profile: {profile_name} (ID: {profile_id})")

            # Delete the profile
            endpoint = (
                "/JSSResource/osxconfigurationprofiles"
                if args.type == "macos"
                else "/JSSResource/mobiledeviceconfigurationprofiles"
            )
            response = self.auth.api_request("DELETE", f"{endpoint}/id/{profile_id}")

            if response is not None:
                print(f"✅ Profile deleted successfully!")
                print(f"   ID: {profile_id}")
                print(f"   Name: {profile_name}")
                return 0
            else:
                print(f"❌ Failed to delete profile")
                return 1

        except Exception as e:
            print(f"❌ Error deleting profile: {e}")
            return 1

    def _delete_bulk(self, args: Namespace) -> int:
        """Delete multiple objects"""
        try:
            objects_to_delete = []

            # Collect policies to delete
            if args.policies:
                for policy_name in args.policies:
                    policy_info = self._find_policy(policy_name)
                    if policy_info:
                        objects_to_delete.append(
                            {
                                "type": "Policy",
                                "id": policy_info["id"],
                                "name": policy_info["name"],
                            }
                        )
                    else:
                        print(f"⚠️ Policy not found: {policy_name}")

            # Collect profiles to delete
            if args.profiles:
                for profile_identifier in args.profiles:
                    profile_info = self._find_profile(profile_identifier, args.type)
                    if profile_info:
                        general = (
                            profile_info.get("general", {})
                            if isinstance(profile_info, dict)
                            else {}
                        )
                        pid = (
                            general.get("id") if isinstance(general, dict) else None
                        ) or profile_info.get("id")
                        pname = (
                            general.get("name") if isinstance(general, dict) else None
                        ) or profile_info.get("name")

                        if pid:
                            objects_to_delete.append(
                                {
                                    "type": f"{args.type.upper()} Profile",
                                    "id": pid,
                                    "name": pname or str(profile_identifier),
                                }
                            )
                        else:
                            print(
                                f"⚠️ Could not determine ID for profile: {profile_identifier}"
                            )
                    else:
                        print(f"⚠️ Profile not found: {profile_identifier}")

            if not objects_to_delete:
                print("❌ No objects found to delete")
                return 1

            # Create comprehensive summary for production confirmation
            if self.is_production_environment():
                changes_summary = self.create_bulk_changes_summary(
                    "Bulk Deletion", objects_to_delete
                )
                changes_summary += "\n  • Warning: This action cannot be undone"

                if not self.require_production_confirmation(
                    "Bulk Delete",
                    f"Deleting {len(objects_to_delete)} objects",
                    changes_summary,
                ):
                    return 1

            print(f"🗑️ Deleting {len(objects_to_delete)} objects...")

            # Delete each object
            deleted_count = 0
            failed_count = 0

            for obj in objects_to_delete:
                try:
                    if "Policy" in obj["type"]:
                        response = self.auth.api_request(
                            "DELETE", f"/JSSResource/policies/id/{obj['id']}"
                        )
                    else:  # Profile
                        endpoint = (
                            "/JSSResource/osxconfigurationprofiles"
                            if args.type == "macos"
                            else "/JSSResource/mobiledeviceconfigurationprofiles"
                        )
                        response = self.auth.api_request(
                            "DELETE", f"{endpoint}/id/{obj['id']}"
                        )

                    if response is not None:
                        print(f"✅ Deleted {obj['type']}: {obj['name']}")
                        deleted_count += 1
                    else:
                        print(f"❌ Failed to delete {obj['type']}: {obj['name']}")
                        failed_count += 1

                except Exception as e:
                    print(f"❌ Error deleting {obj['type']} {obj['name']}: {e}")
                    failed_count += 1

            print(f"\n📊 Deletion Summary:")
            print(f"   ✅ Successfully deleted: {deleted_count}")
            print(f"   ❌ Failed: {failed_count}")

            return 0 if failed_count == 0 else 1

        except Exception as e:
            print(f"❌ Error in bulk deletion: {e}")
            return 1

    def _find_policy(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Find a policy by name or ID"""
        try:
            # Try as ID first
            if name_or_id.isdigit():
                response = self.auth.api_request(
                    "GET", f"/JSSResource/policies/id/{name_or_id}"
                )
                if "policy" in response and "general" in response["policy"]:
                    policy_data = response["policy"]["general"]
                    policy_data["id"] = name_or_id  # Add ID to the policy data
                    return policy_data

            # Search by name
            response = self.auth.api_request("GET", "/JSSResource/policies")
            if "policies" in response and "policy" in response["policies"]:
                policies = response["policies"]["policy"]
                if not isinstance(policies, list):
                    policies = [policies]

                for policy in policies:
                    if policy.get("name", "").lower() == name_or_id.lower():
                        return policy

            return None

        except Exception:
            return None

    def _find_profile(
        self, name_or_id: str, profile_type: str
    ) -> Optional[Dict[str, Any]]:
        """Find a profile by name or ID"""
        try:
            endpoint = (
                "/JSSResource/osxconfigurationprofiles"
                if profile_type == "macos"
                else "/JSSResource/mobiledeviceconfigurationprofiles"
            )

            # Try as ID first
            if name_or_id.isdigit():
                response = self.auth.api_request("GET", f"{endpoint}/id/{name_or_id}")
                if (
                    "os_x_configuration_profile" in response
                    or "mobile_device_configuration_profile" in response
                ):
                    return response.get("os_x_configuration_profile") or response.get(
                        "mobile_device_configuration_profile"
                    )

            # Search by name
            response = self.auth.api_request("GET", endpoint)
            profile_key = (
                "os_x_configuration_profiles"
                if profile_type == "macos"
                else "mobile_device_configuration_profiles"
            )

            if (
                profile_key in response
                and "os_x_configuration_profile" in response[profile_key]
            ):
                profiles = response[profile_key]["os_x_configuration_profile"]
                if not isinstance(profiles, list):
                    profiles = [profiles]

                for profile in profiles:
                    if profile.get("name", "").lower() == name_or_id.lower():
                        return profile

            return None

        except Exception:
            return None

    def _delete_script(self, args: Namespace) -> int:
        """Delete a script"""
        try:
            print(f"🗑️ Delete Script: {args.name_or_id}")

            # Find the script
            script_info = self._find_script(args.name_or_id)
            if not script_info:
                print(f"❌ Script not found: {args.name_or_id}")
                return 1

            script_id = script_info["id"]
            script_name = script_info.get("name", "Unknown")

            # Check production safety
            if not self.check_destructive_operation(
                "Delete Script", f"ID: {script_id}, Name: {script_name}"
            ):
                return 1

            # Confirmation if not forced
            if not args.force:
                confirm = (
                    input(
                        f"⚠️  Permanently delete script '{script_name}' (ID: {script_id})? (y/N): "
                    )
                    .lower()
                    .strip()
                )
                if confirm not in ["y", "yes"]:
                    print("❌ Deletion cancelled")
                    return 1

            # Delete the script
            response = self.auth.api_request(
                "DELETE", f"/JSSResource/scripts/id/{script_id}"
            )

            if response is not None:
                print(f"✅ Script deleted successfully!")
                print(f"   ID: {script_id}")
                print(f"   Name: {script_name}")
                return 0
            else:
                print(f"❌ Failed to delete script")
                return 1

        except Exception as e:
            print(f"❌ Error deleting script: {e}")
            return 1

    def _delete_package(self, args: Namespace) -> int:
        """Delete a package"""
        try:
            print(f"🗑️ Delete Package: {args.name_or_id}")

            # Find the package
            package_info = self._find_package(args.name_or_id)
            if not package_info:
                print(f"❌ Package not found: {args.name_or_id}")
                return 1

            package_id = package_info["id"]
            package_name = package_info.get("name", "Unknown")

            # Check production safety
            if not self.check_destructive_operation(
                "Delete Package", f"ID: {package_id}, Name: {package_name}"
            ):
                return 1

            # Confirmation if not forced
            if not args.force:
                confirm = (
                    input(
                        f"⚠️  Permanently delete package '{package_name}' (ID: {package_id})? (y/N): "
                    )
                    .lower()
                    .strip()
                )
                if confirm not in ["y", "yes"]:
                    print("❌ Deletion cancelled")
                    return 1

            # Delete the package
            response = self.auth.api_request(
                "DELETE", f"/JSSResource/packages/id/{package_id}"
            )

            if response is not None:
                print(f"✅ Package deleted successfully!")
                print(f"   ID: {package_id}")
                print(f"   Name: {package_name}")
                return 0
            else:
                print(f"❌ Failed to delete package")
                return 1

        except Exception as e:
            print(f"❌ Error deleting package: {e}")
            return 1

    def _delete_group(self, args: Namespace) -> int:
        """Delete a computer group"""
        try:
            print(f"🗑️ Delete Computer Group: {args.name_or_id}")

            # Find the group
            group_info = self._find_group(args.name_or_id)
            if not group_info:
                print(f"❌ Computer group not found: {args.name_or_id}")
                return 1

            group_id = group_info["id"]
            group_name = group_info.get("name", "Unknown")

            # Check production safety
            if not self.check_destructive_operation(
                "Delete Computer Group", f"ID: {group_id}, Name: {group_name}"
            ):
                return 1

            # Confirmation if not forced
            if not args.force:
                confirm = (
                    input(
                        f"⚠️  Permanently delete computer group '{group_name}' (ID: {group_id})? (y/N): "
                    )
                    .lower()
                    .strip()
                )
                if confirm not in ["y", "yes"]:
                    print("❌ Deletion cancelled")
                    return 1

            # Delete the group
            response = self.auth.api_request(
                "DELETE", f"/JSSResource/computergroups/id/{group_id}"
            )

            if response is not None:
                print(f"✅ Computer group deleted successfully!")
                print(f"   ID: {group_id}")
                print(f"   Name: {group_name}")
                return 0
            else:
                print(f"❌ Failed to delete computer group")
                return 1

        except Exception as e:
            print(f"❌ Error deleting computer group: {e}")
            return 1

    def _delete_search(self, args: Namespace) -> int:
        """Delete an advanced search"""
        try:
            print(f"🗑️ Delete Advanced Search: {args.name_or_id}")

            # Find the search
            search_info = self._find_search(args.name_or_id)
            if not search_info:
                print(f"❌ Advanced search not found: {args.name_or_id}")
                return 1

            search_id = search_info["id"]
            search_name = search_info.get("name", "Unknown")

            # Check production safety
            if not self.check_destructive_operation(
                "Delete Advanced Search", f"ID: {search_id}, Name: {search_name}"
            ):
                return 1

            # Confirmation if not forced
            if not args.force:
                confirm = (
                    input(
                        f"⚠️  Permanently delete advanced search '{search_name}' (ID: {search_id})? (y/N): "
                    )
                    .lower()
                    .strip()
                )
                if confirm not in ["y", "yes"]:
                    print("❌ Deletion cancelled")
                    return 1

            # Delete the search
            response = self.auth.api_request(
                "DELETE", f"/JSSResource/advancedcomputersearches/id/{search_id}"
            )

            if response is not None:
                print(f"✅ Advanced search deleted successfully!")
                print(f"   ID: {search_id}")
                print(f"   Name: {search_name}")
                return 0
            else:
                print(f"❌ Failed to delete advanced search")
                return 1

        except Exception as e:
            print(f"❌ Error deleting advanced search: {e}")
            return 1

    def _find_script(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Find a script by name or ID"""
        try:
            # Try as ID first
            if name_or_id.isdigit():
                response = self.auth.api_request(
                    "GET", f"/JSSResource/scripts/id/{name_or_id}"
                )
                if "script" in response:
                    return response["script"]

            # Search by name
            response = self.auth.api_request("GET", "/JSSResource/scripts")
            if "scripts" in response and "script" in response["scripts"]:
                scripts = response["scripts"]["script"]
                if not isinstance(scripts, list):
                    scripts = [scripts]

                for script in scripts:
                    if script.get("name", "").lower() == name_or_id.lower():
                        return script

            return None

        except Exception:
            return None

    def _find_package(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Find a package by name or ID"""
        try:
            # Try as ID first
            if name_or_id.isdigit():
                response = self.auth.api_request(
                    "GET", f"/JSSResource/packages/id/{name_or_id}"
                )
                if "package" in response:
                    return response["package"]

            # Search by name
            response = self.auth.api_request("GET", "/JSSResource/packages")
            if "packages" in response and "package" in response["packages"]:
                packages = response["packages"]["package"]
                if not isinstance(packages, list):
                    packages = [packages]

                for package in packages:
                    if package.get("name", "").lower() == name_or_id.lower():
                        return package

            return None

        except Exception:
            return None

    def _find_group(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Find a computer group by name or ID"""
        try:
            # Try as ID first
            if name_or_id.isdigit():
                response = self.auth.api_request(
                    "GET", f"/JSSResource/computergroups/id/{name_or_id}"
                )
                if "computer_group" in response:
                    return response["computer_group"]

            # Search by name
            response = self.auth.api_request("GET", "/JSSResource/computergroups")
            if (
                "computer_groups" in response
                and "computer_group" in response["computer_groups"]
            ):
                groups = response["computer_groups"]["computer_group"]
                if not isinstance(groups, list):
                    groups = [groups]

                for group in groups:
                    if group.get("name", "").lower() == name_or_id.lower():
                        return group

            return None

        except Exception:
            return None

    def _find_search(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Find an advanced search by name or ID"""
        try:
            # Try as ID first
            if name_or_id.isdigit():
                response = self.auth.api_request(
                    "GET", f"/JSSResource/advancedcomputersearches/id/{name_or_id}"
                )
                if "advanced_computer_search" in response:
                    return response["advanced_computer_search"]

            # Search by name
            response = self.auth.api_request(
                "GET", "/JSSResource/advancedcomputersearches"
            )
            if (
                "advanced_computer_searches" in response
                and "advanced_computer_search" in response["advanced_computer_searches"]
            ):
                searches = response["advanced_computer_searches"][
                    "advanced_computer_search"
                ]
                if not isinstance(searches, list):
                    searches = [searches]

                for search in searches:
                    if search.get("name", "").lower() == name_or_id.lower():
                        return search

            return None

        except Exception:
            return None

    def _delete_extension_attribute(self, args: Namespace) -> int:
        """Delete an extension attribute"""
        try:
            attr_type = getattr(args, "type", "computer")
            attr_id = args.id

            print(f"🗑️ Deleting {attr_type} extension attribute: ID {attr_id}")

            # Get endpoint from APIRegistry
            try:
                endpoint = APIRegistry.get_single_endpoint(attr_type, attr_id)
            except ValueError:
                print(f"❌ Unknown attribute type: {attr_type}")
                return 1

            # Get attribute details for confirmation
            try:
                response = self.auth.api_request("GET", endpoint)

                attr_name = "Unknown"
                if response:
                    if (
                        attr_type == "computer"
                        and "computer_extension_attribute" in response
                    ):
                        attr_name = response["computer_extension_attribute"].get(
                            "name", "Unknown"
                        )
                    elif (
                        attr_type == "mobile"
                        and "mobile_device_extension_attribute" in response
                    ):
                        attr_name = response["mobile_device_extension_attribute"].get(
                            "name", "Unknown"
                        )
                    elif attr_type == "user" and "user_extension_attribute" in response:
                        attr_name = response["user_extension_attribute"].get(
                            "name", "Unknown"
                        )

                print(f"   Name: {attr_name}")
            except Exception:
                pass  # Continue even if we can't get the name

            # Confirmation
            if not getattr(args, "force", False):
                confirm = input(
                    f"Are you sure you want to delete this {attr_type} extension attribute? (y/N): "
                )
                if confirm.lower() not in ["y", "yes"]:
                    print("❌ Deletion cancelled")
                    return 1

            # Delete the attribute
            response = self.auth.api_request("DELETE", endpoint)

            if response is not None:  # DELETE can return empty response
                print("✅ Extension attribute deleted successfully!")
                return 0
            else:
                print("❌ Failed to delete: No response from API")
                return 1

        except Exception as e:
            print(f"❌ Failed to delete extension attribute: {e}")
            return 1
