#!/usr/bin/env python3
"""
Roles Command for jpapi CLI
Manages JAMF Pro API roles for the jpapi CLI system
"""

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

# Using proper package structure via pip install -e .

from base.command import BaseCommand
from core.role_manager import JAMFRoleManager, create_roles_interactive, APIRole


class RolesCommand(BaseCommand):
    """Command for managing JAMF Pro API roles"""

    def __init__(self):
        super().__init__(
            name="roles", description="🔧 Manage JAMF Pro API roles for jpapi CLI"
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add roles command arguments"""
        subparsers = parser.add_subparsers(dest="roles_action", help="Role actions")

        # Create roles command
        create_parser = subparsers.add_parser(
            "create", help="Create jpapi roles in JAMF Pro"
        )
        create_parser.add_argument(
            "--all", action="store_true", help="Create all 4 roles"
        )
        create_parser.add_argument(
            "--role",
            choices=["read", "create", "update", "delete"],
            help="Create specific role",
        )
        self.setup_common_args(create_parser)

        # Update roles command
        update_parser = subparsers.add_parser(
            "update", help="Update existing jpapi roles in JAMF Pro"
        )
        update_parser.add_argument(
            "--all", action="store_true", help="Update all 4 roles"
        )
        update_parser.add_argument(
            "--role",
            choices=["read", "create", "update", "delete"],
            help="Update specific role",
        )
        self.setup_common_args(update_parser)

        # List roles command
        list_parser = subparsers.add_parser("list", help="List existing jpapi roles")
        self.setup_common_args(list_parser)

        # Info command
        info_parser = subparsers.add_parser("info", help="Show role information")
        self.setup_common_args(info_parser)

        # Interactive setup
        setup_parser = subparsers.add_parser("setup", help="Interactive role setup")
        self.setup_common_args(setup_parser)

        # Delete roles command
        delete_parser = subparsers.add_parser("delete", help="Delete API roles")
        delete_parser.add_argument(
            "--pattern",
            help="Pattern to match roles for deletion (supports wildcards and regex)",
        )
        delete_parser.add_argument(
            "--filter-type",
            choices=["wildcard", "regex", "exact", "contains"],
            default="regex",
            help="Type of filtering to use",
        )
        delete_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
        delete_parser.add_argument(
            "--force", action="store_true", help="Skip confirmation prompts"
        )

    def execute(self, args: Namespace) -> int:
        """Execute the roles command"""
        try:
            if not args.roles_action:
                self._show_help()
                return 1

            # Get environment from args
            environment = getattr(args, "env", "dev")

            if args.roles_action == "create":
                return self._handle_create_roles(args, environment)
            elif args.roles_action == "update":
                return self._handle_update_roles(args, environment)
            elif args.roles_action == "list":
                return self._handle_list_roles(args, environment)
            elif args.roles_action == "info":
                return self._handle_info(args, environment)
            elif args.roles_action == "setup":
                return self._handle_setup(args, environment)
            elif args.roles_action == "delete":
                return self._handle_delete_roles(args, environment)
            else:
                print(f"❌ Unknown action: {args.roles_action}")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_create_roles(self, args: Namespace, environment: str) -> int:
        """Handle role creation"""
        manager = JAMFRoleManager(environment)

        # Check authentication
        if not manager.is_authenticated():
            print(f"❌ Not authenticated with JAMF Pro ({environment})")
            print(f"Run: jpapi auth setup {environment}")
            return 1

        if args.all:
            # Create all roles
            print(f"🚀 Creating all jpapi roles in JAMF Pro ({environment})...")
            results = manager.create_all_roles()

            success_count = sum(1 for success in results.values() if success)
            if success_count == 4:
                print("\n✅ All roles created successfully!")
                print("\n📋 Next steps:")
                print("1. Create user accounts in JAMF Pro")
                print("2. Assign users to appropriate jpapi roles")
                print("3. Run: jpapi roles setup")
                return 0
            else:
                print(f"\n⚠️  {4 - success_count} roles failed to create")
                return 1

        elif args.role:
            # Create specific role
            role_enum = APIRole(args.role)
            print(f"🚀 Creating {args.role} role in JAMF Pro ({environment})...")

            if manager.create_role(role_enum):
                print(f"✅ {args.role} role created successfully!")
                return 0
            else:
                print(f"❌ Failed to create {args.role} role")
                return 1
        else:
            # Interactive creation
            return 0 if create_roles_interactive(environment) else 1

    def _handle_update_roles(self, args: Namespace, environment: str) -> int:
        """Handle role updates"""
        manager = JAMFRoleManager(environment)

        # Check authentication
        if not manager.is_authenticated():
            print(f"❌ Not authenticated with JAMF Pro ({environment})")
            print(f"Run: jpapi auth setup {environment}")
            return 1

        if args.all:
            # Update all roles
            print(f"🔄 Updating all jpapi roles in JAMF Pro ({environment})...")
            results = manager.update_all_roles()

            success_count = sum(1 for success in results.values() if success)
            if success_count == 4:
                print("\n✅ All roles updated successfully!")
                print("\n📋 Next steps:")
                print("1. Verify role permissions in JAMF Pro Admin Console")
                print("2. Test CLI access with updated role assignments")
                return 0
            else:
                print(f"\n⚠️  {4 - success_count} roles failed to update")
                return 1

        elif args.role:
            # Update specific role
            role_enum = APIRole(args.role)
            print(f"🔄 Updating {args.role} role in JAMF Pro ({environment})...")

            if manager.update_role(role_enum):
                print(f"✅ {args.role} role updated successfully!")
                return 0
            else:
                print(f"❌ Failed to update {args.role} role")
                return 1
        else:
            print("❌ Please specify --all or --role <role> for update command")
            return 1

    def _handle_list_roles(self, args: Namespace, environment: str) -> int:
        """Handle role listing"""
        manager = JAMFRoleManager(environment)

        if not manager.is_authenticated():
            print(f"❌ Not authenticated with JAMF Pro ({environment})")
            print(f"Run: jpapi auth setup {environment}")
            return 1

        print(f"📋 Existing jpapi roles in JAMF Pro ({environment}):")
        existing_roles = manager.list_existing_roles()

        if existing_roles:
            for role in existing_roles:
                print(
                    f"  • {role.get('displayName', 'Unknown')} (ID: {role.get('id', 'Unknown')})"
                )
        else:
            print("  No jpapi roles found")
            print("\n💡 To create roles, run: jpapi roles create --all")

        return 0

    def _handle_info(self, args: Namespace, environment: str) -> int:
        """Handle role information display"""
        manager = JAMFRoleManager(environment)

        print(f"🔧 JAMF Pro Role Manager Info ({environment})")
        print("=" * 50)

        info = manager.get_role_info()
        print(f"Environment: {info['environment']}")
        print(f"Authenticated: {'✅ Yes' if info['authenticated'] else '❌ No'}")
        print(f"Available roles: {len(info['roles'])}")
        print()

        print("📋 Role Definitions:")
        for role_name, role_info in info["roles"].items():
            print(f"  {role_info['display_name']}")
            print(f"     Description: {role_info['description']}")
            print(f"     Commands: {', '.join(role_info['cli_commands'])}")
            print(f"     Permissions: {role_info['permissions']} API endpoints")
            print()

        if not info["authenticated"]:
            print("💡 To authenticate, run: jpapi auth setup {environment}")

        return 0

    def _handle_setup(self, args: Namespace, environment: str) -> int:
        """Handle interactive setup"""
        print(f"🔧 Interactive Role Setup ({environment})")
        print("=" * 40)
        print()

        if create_roles_interactive(environment):
            print("\n🎉 Role setup complete!")
            print("\n📋 Next steps:")
            print("1. Create user accounts in JAMF Pro Admin Console")
            print("2. Assign users to appropriate jpapi roles")
            print("3. Test CLI access with different role assignments")
            return 0
        else:
            print("\n❌ Role setup failed")
            return 1

    def _handle_delete_roles(self, args: Namespace, environment: str) -> int:
        """Handle role deletion with filtering"""
        manager = JAMFRoleManager(environment)

        # Check authentication
        if not manager.is_authenticated():
            print(f"❌ Not authenticated with JAMF Pro ({environment})")
            print(f"Run: jpapi auth setup {environment}")
            return 1

        # Get all API roles
        try:
            response = manager.auth.api_request(
                "GET", "/api/v1/api-roles?page=0&page-size=100&sort=id%3Aasc"
            )
            if not response or "results" not in response:
                print("❌ Failed to retrieve API roles")
                return 1

            all_roles = response["results"]
            print(f"📋 Found {len(all_roles)} total API roles")

            # Apply filter if provided
            roles_to_delete = all_roles
            if args.pattern:
                from src.lib.utils import create_filter

                filter_obj = create_filter(args.filter_type)
                roles_to_delete = filter_obj.filter_objects(
                    all_roles, "displayName", args.pattern
                )
                print(
                    f"🔍 Pattern '{args.pattern}' matched {len(roles_to_delete)} roles"
                )

            if not roles_to_delete:
                print("❌ No roles found matching the filter")
                return 1

            # Show roles that will be deleted
            print(f"\n🗑️  Roles to be deleted ({len(roles_to_delete)}):")
            for role in roles_to_delete:
                print(
                    f"  • {role.get('displayName', 'Unknown')} (ID: {role.get('id', 'Unknown')})"
                )

            # Dry run check
            if args.dry_run:
                print(f"\n🔍 DRY RUN: Would delete {len(roles_to_delete)} roles")
                return 0

            # Production safety check
            if self.is_production_environment():
                changes_summary = f"""
API Role Deletion Summary:
  • Environment: {environment}
  • Roles to delete: {len(roles_to_delete)}
  • Pattern: {args.pattern if args.pattern else 'All roles'}
  • Filter type: {args.filter_type}
  • Impact: Will permanently delete these API roles from PRODUCTION
  • Warning: This action cannot be undone

Roles to be deleted:
{chr(10).join(f'  • {role.get("displayName", "Unknown")} (ID: {role.get("id", "Unknown")})' for role in roles_to_delete)}
"""

                if not self.require_production_confirmation(
                    "Delete API Roles",
                    f"Deleting {len(roles_to_delete)} API roles",
                    changes_summary,
                ):
                    return 1

            # Regular confirmation for non-production or if force flag is used
            elif not args.force:
                confirm = (
                    input(
                        f"\n⚠️  Are you sure you want to delete {len(roles_to_delete)} API roles? (yes/no): "
                    )
                    .lower()
                    .strip()
                )
                if confirm not in ["yes", "y"]:
                    print("❌ Deletion cancelled")
                    return 1

            # Delete roles
            deleted_count = 0
            failed_count = 0

            for role in roles_to_delete:
                role_id = role.get("id")
                role_name = role.get("displayName", "Unknown")

                try:
                    response = manager.auth.api_request(
                        "DELETE", f"/api/v1/api-roles/{role_id}"
                    )
                    print(f"✅ Deleted: {role_name} (ID: {role_id})")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Failed to delete {role_name} (ID: {role_id}): {e}")
                    failed_count += 1

            # Summary
            print(f"\n🎉 Deletion complete!")
            print(f"✅ Successfully deleted: {deleted_count}")
            if failed_count > 0:
                print(f"❌ Failed to delete: {failed_count}")

            return 0 if failed_count == 0 else 1

        except Exception as e:
            print(f"❌ Error during role deletion: {e}")
            return 1

    def _show_help(self):
        """Show help for roles command"""
        print("🔧 JAMF Pro Role Management")
        print("=" * 30)
        print()
        print("Available commands:")
        print("  create --all              # Create all 4 jpapi roles")
        print(
            "  create --role <role>      # Create specific role (read/create/update/delete)"
        )
        print("  update --all              # Update all 4 jpapi roles")
        print(
            "  update --role <role>      # Update specific role (read/create/update/delete)"
        )
        print("  list                      # List existing jpapi roles")
        print("  info                      # Show role information")
        print("  setup                     # Interactive role setup")
        print(
            "  delete --pattern <pattern> # Delete roles matching pattern (supports regex)"
        )
        print()
        print("Examples:")
        print("  jpapi roles create --all")
        print("  jpapi roles create --role read")
        print("  jpapi roles update --all")
        print("  jpapi roles update --role read")
        print("  jpapi roles list")
        print("  jpapi roles setup")
        print("  jpapi roles delete --pattern '^crud' --filter-type regex --dry-run")
        print("  jpapi roles delete --pattern 'test*' --filter-type wildcard")
        print()
        print("💡 Roles created:")
        print("  • jpapi-read    - Read-only access")
        print("  • jpapi-create  - Create access")
        print("  • jpapi-update  - Update access")
        print("  • jpapi-delete  - Delete access (HIGH RISK)")
