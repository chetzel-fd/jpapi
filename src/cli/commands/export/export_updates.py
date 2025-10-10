#!/usr/bin/env python3
"""
Update Handler for jpapi CLI
Handles CSV-based updates to JAMF objects
"""

from typing import Dict, Any, List
from argparse import Namespace
import csv
from pathlib import Path


class ExportUpdates:
    """Handler for updating JAMF objects from CSV files"""

    def __init__(self, auth):
        self.auth = auth

    def update_from_csv(self, args: Namespace) -> int:
        """Update JAMF objects from CSV file"""
        try:
            csv_file = Path(args.csv_file)
            if not csv_file.exists():
                print(f"❌ CSV file not found: {csv_file}")
                return 1

            object_type = args.object_type.lower()
            print(f"🔄 Updating {object_type} from: {csv_file}")

            # Route to appropriate update handler
            if object_type in ["computer-groups", "macos-groups", "groups"]:
                return self._update_computer_groups_from_csv(args)
            elif object_type in ["policies", "policy", "pol"]:
                return self._update_policies_from_csv(args)
            elif object_type in ["scripts", "script"]:
                return self._update_scripts_from_csv(args)
            elif object_type in [
                "advanced-searches",
                "adv",
                "advanced",
                "searches",
                "computer-searches",
            ]:
                return self._update_advanced_searches_from_csv(args)
            else:
                print(f"❌ Update not supported for object type: {object_type}")
                print(
                    "   Supported types: computer-groups, policies, scripts, advanced-searches, adv, advanced, searches"
                )
                return 1

        except Exception as e:
            print(f"❌ Error updating {args.object_type}: {e}")
            return 1

    def _update_computer_groups_from_csv(self, args: Namespace) -> int:
        """Update computer groups from CSV file"""
        try:
            csv_file = Path(args.csv_file)

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

            print(f"\n📊 UPDATE RESULTS")
            print(f"   ✅ Successfully deleted: {deleted_count}")
            print(f"   ❌ Failed to delete: {failed_count}")

            return 0 if failed_count == 0 else 1

        except Exception as e:
            print(f"❌ Error updating computer groups: {e}")
            return 1

    def _update_policies_from_csv(self, args: Namespace) -> int:
        """Update policies from CSV file"""
        print("⚠️  Policy updates not yet implemented")
        return 1

    def _update_scripts_from_csv(self, args: Namespace) -> int:
        """Update scripts from CSV file"""
        print("⚠️  Script updates not yet implemented")
        return 1

    def _update_advanced_searches_from_csv(self, args: Namespace) -> int:
        """Update advanced computer searches from CSV file"""
        try:
            csv_file = Path(args.csv_file)

            # Read CSV file
            searches_to_delete = []
            with open(csv_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check if delete column has a value (any non-empty value means delete)
                    delete_value = row.get("delete", "").strip()
                    if delete_value:
                        searches_to_delete.append(
                            {
                                "id": row.get("id", ""),
                                "name": row.get("name", ""),
                                "delete_reason": delete_value,
                            }
                        )

            if not searches_to_delete:
                print("✅ No advanced searches marked for deletion in CSV file")
                return 0

            print(
                f"\n📋 Found {len(searches_to_delete)} advanced searches marked for deletion:"
            )
            for search in searches_to_delete:
                print(
                    f"   • {search['name']} (ID: {search['id']}) - Reason: {search['delete_reason']}"
                )

            if args.dry_run:
                print("\n🔍 DRY RUN - No changes will be made")
                return 0

            # Confirm deletion
            if not args.confirm:
                response = input(
                    f"\n⚠️  Are you sure you want to delete {len(searches_to_delete)} advanced computer searches? (yes/no): "
                )
                if response.lower() not in ["yes", "y"]:
                    print("❌ Deletion cancelled")
                    return 0

            # Delete searches
            deleted_count = 0
            failed_count = 0

            for search in searches_to_delete:
                try:
                    print(
                        f"🗑️  Deleting advanced search: {search['name']} (ID: {search['id']})"
                    )

                    # Delete via JAMF API
                    response = self.auth.api_request(
                        "DELETE",
                        f'/JSSResource/advancedcomputersearches/id/{search["id"]}',
                    )

                    if response is not None:
                        print(f"   ✅ Deleted: {search['name']}")
                        deleted_count += 1
                    else:
                        print(f"   ❌ Failed to delete: {search['name']}")
                        failed_count += 1

                except Exception as e:
                    print(f"   ❌ Error deleting {search['name']}: {e}")
                    failed_count += 1

            print(f"\n📊 UPDATE RESULTS")
            print(f"   ✅ Successfully deleted: {deleted_count}")
            print(f"   ❌ Failed to delete: {failed_count}")

            return 0 if failed_count == 0 else 1

        except Exception as e:
            print(f"❌ Error updating advanced searches: {e}")
            return 1
