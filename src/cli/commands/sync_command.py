#!/usr/bin/env python3
"""
Sync Command for jpapi CLI
Handles syncing API roles and other objects between environments and CSV files
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
import argparse
import csv
import json
import sys
from pathlib import Path

# Using proper package structure via pip install -e .

from core.role_manager import JAMFRoleManager, APIRole


class SyncCommand(BaseCommand):
    """Command for syncing API roles and other objects between environments"""

    def __init__(self):
        super().__init__(
            name="sync",
            description="🔄 Sync API roles and objects between environments",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add sync command arguments"""
        subparsers = parser.add_subparsers(
            dest="sync_object", help="Object type to sync"
        )

        # API Roles sync - Primary functionality
        roles_parser = subparsers.add_parser(
            "api-roles", help="Sync API roles between environments"
        )
        roles_parser.add_argument(
            "--source-env",
            default="production",
            help="Source environment to sync from (default: production)",
        )
        roles_parser.add_argument(
            "--target-env",
            default="sandbox",
            help="Target environment to sync to (default: sandbox)",
        )
        roles_parser.add_argument(
            "--role",
            choices=["read", "create", "update", "delete"],
            help="Sync specific role (default: all)",
        )
        roles_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be synced without actually syncing",
        )
        roles_parser.add_argument(
            "--force",
            action="store_true",
            help="Force sync even if roles exist in target",
        )
        self.setup_common_args(roles_parser)

        # Computer groups sync (legacy functionality)
        groups_parser = subparsers.add_parser(
            "computer-groups", help="Sync computer groups from CSV"
        )
        groups_parser.add_argument("csv_file", help="CSV file to sync from")
        groups_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
        groups_parser.add_argument(
            "--confirm", action="store_true", help="Skip confirmation prompts"
        )
        self.setup_common_args(groups_parser)

        # Hidden aliases
        for alias in ["macos-groups", "groups"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument("csv_file", help="CSV file to sync from")
            alias_parser.add_argument(
                "--dry-run",
                action="store_true",
                help="Show what would be deleted without actually deleting",
            )
            alias_parser.add_argument(
                "--confirm", action="store_true", help="Skip confirmation prompts"
            )
            self.setup_common_args(alias_parser)

    def execute(self, args: Namespace) -> int:
        """Execute the sync command"""
        if not self.check_auth(args):
            return 1

        try:
            if args.sync_object == "api-roles":
                return self._sync_api_roles(args)
            elif args.sync_object in ["computer-groups", "macos-groups", "groups"]:
                return self._sync_computer_groups(args)
            else:
                print(f"❌ Unknown sync object: {args.sync_object}")
                print("Available: api-roles, computer-groups")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _sync_api_roles(self, args: Namespace) -> int:
        """Sync API roles between environments"""
        try:
            source_env = args.source_env
            target_env = args.target_env
            specific_role = args.role

            print(f"🔄 Syncing API roles from {source_env} to {target_env}")
            print("=" * 60)

            # Initialize role managers for both environments
            source_manager = JAMFRoleManager(source_env)
            target_manager = JAMFRoleManager(target_env)

            # Check authentication for both environments
            if not source_manager.is_authenticated():
                print(f"❌ Not authenticated with source environment: {source_env}")
                print(f"Run: jpapi auth setup {source_env}")
                return 1

            if not target_manager.is_authenticated():
                print(f"❌ Not authenticated with target environment: {target_env}")
                print(f"Run: jpapi auth setup {target_env}")
                return 1

            print(f"✅ Authenticated with both environments")
            print()

            # Get roles to sync
            roles_to_sync = [APIRole(specific_role)] if specific_role else list(APIRole)

            # Check existing roles in target environment
            existing_target_roles = target_manager.list_existing_roles()
            existing_role_names = {
                role.get("displayName") for role in existing_target_roles
            }

            sync_results = {}

            for role in roles_to_sync:
                role_name = f"jpapi-{role.value}"
                config = target_manager.role_configs[role]

                print(f"🔍 Processing role: {config.display_name}")

                # Check if role exists in target
                if role_name in existing_role_names:
                    if args.force:
                        print(f"   🔄 Updating existing role: {role_name}")
                        result = target_manager.update_role(role)
                        sync_results[role] = result
                    else:
                        print(
                            f"   ⚠️  Role already exists: {role_name} (use --force to update)"
                        )
                        sync_results[role] = False
                else:
                    print(f"   ➕ Creating new role: {role_name}")
                    result = target_manager.create_role(role)
                    sync_results[role] = result

                if args.dry_run:
                    print(f"   🔍 DRY RUN: Would sync {role_name}")
                    sync_results[role] = True
                else:
                    status = "✅" if sync_results[role] else "❌"
                    print(f"   {status} {role_name}")

                print()

            # Summary
            if not args.dry_run:
                success_count = sum(1 for success in sync_results.values() if success)
                total_count = len(sync_results)

                print("📊 SYNC SUMMARY")
                print("=" * 20)
                print(f"✅ Successfully synced: {success_count}/{total_count}")

                if success_count < total_count:
                    failed_roles = [
                        role.value
                        for role, success in sync_results.items()
                        if not success
                    ]
                    print(f"❌ Failed roles: {', '.join(failed_roles)}")

                print(f"\n🎯 Next steps:")
                print(f"1. Verify roles in {target_env} JAMF Pro Admin Console")
                print(f"2. Test API access with updated role assignments")
                print(f"3. Run: jpapi roles list --env {target_env}")

                return 0 if success_count == total_count else 1
            else:
                print("🔍 DRY RUN COMPLETE - No changes made")
                return 0

        except Exception as e:
            print(f"❌ Error syncing API roles: {e}")
            return 1

    def _sync_computer_groups(self, args: Namespace) -> int:
        """Sync computer groups from CSV file"""
        try:
            csv_file = Path(args.csv_file)
            if not csv_file.exists():
                print(f"❌ CSV file not found: {csv_file}")
                return 1

            print(f"🔄 Syncing computer groups from: {csv_file}")

            # Read CSV file
            groups_to_delete = []
            with open(csv_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check if delete column has a value (any non-empty value means delete)
                    delete_value = row.get("delete", "").strip()
                    if delete_value:
                        groups_to_delete.append(
                            {
                                "id": row.get("ID", ""),
                                "name": row.get("Name", ""),
                                "delete_reason": delete_value,
                            }
                        )

            if not groups_to_delete:
                print("✅ No groups marked for deletion in CSV file")
                return 0

            print(f"\n📋 Found {len(groups_to_delete)} groups marked for deletion:")
            for group in groups_to_delete:
                print(
                    f"   • {group['name']} (ID: {group['id']}) - Reason: {group['delete_reason']}"
                )

            if args.dry_run:
                print("\n🔍 DRY RUN - No changes will be made")
                return 0

            # Confirm deletion
            if not args.confirm:
                response = input(
                    f"\n⚠️  Are you sure you want to delete {len(groups_to_delete)} computer groups? (yes/no): "
                )
                if response.lower() not in ["yes", "y"]:
                    print("❌ Deletion cancelled")
                    return 0

            # Delete groups
            deleted_count = 0
            failed_count = 0

            for group in groups_to_delete:
                try:
                    print(f"🗑️  Deleting group: {group['name']} (ID: {group['id']})")

                    # Delete via JAMF API
                    response = self.auth.api_request(
                        "DELETE", f'/JSSResource/computergroups/id/{group["id"]}'
                    )

                    if response is not None:
                        print(f"   ✅ Deleted: {group['name']}")
                        deleted_count += 1
                    else:
                        print(f"   ❌ Failed to delete: {group['name']}")
                        failed_count += 1

                except Exception as e:
                    print(f"   ❌ Error deleting {group['name']}: {e}")
                    failed_count += 1

            print(f"\n📊 SYNC RESULTS")
            print(f"   ✅ Successfully deleted: {deleted_count}")
            print(f"   ❌ Failed to delete: {failed_count}")

            return 0 if failed_count == 0 else 1

        except Exception as e:
            return self.handle_api_error(e)
