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

        # Policy delete command
        policy_parser = subparsers.add_parser("policy", help="Delete policies")
        policy_parser.add_argument("name_or_id", help="Policy name or ID to delete")
        policy_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(policy_parser)

        # Profile delete command
        profile_parser = subparsers.add_parser(
            "profile", help="Delete configuration profiles"
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
                print("   jpapi delete bulk --policies 'Policy 1' 'Policy 2'")
                print()
                print("🔧 Available Objects:")
                print("   Policies: policy, pol")
                print("   Profiles: profile, prof")
                print("   Bulk: bulk, multiple")
                print()
                print("⚠️  Use --force to skip confirmation prompts")
                return 0

            if args.delete_object == "policy":
                return self._delete_policy(args)
            elif args.delete_object == "profile":
                return self._delete_profile(args)
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

            profile_id = profile_info.get("general", {}).get("id")
            profile_name = profile_info.get("general", {}).get("name")

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
                for profile_name in args.profiles:
                    profile_info = self._find_profile(profile_name, args.type)
                    if profile_info:
                        objects_to_delete.append(
                            {
                                "type": f"{args.type.upper()} Profile",
                                "id": profile_info["id"],
                                "name": profile_info["name"],
                            }
                        )
                    else:
                        print(f"⚠️ Profile not found: {profile_name}")

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
