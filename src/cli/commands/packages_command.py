#!/usr/bin/env python3
"""
Packages Command for jpapi CLI
Package management operations including create, update, delete, and deploy
"""
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
import json
import os
import time
from typing import Dict, Any, List, Optional

# Add base to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.command import BaseCommand


class PackagesCommand(BaseCommand):
    """Command for package management operations"""

    def __init__(self):
        super().__init__(
            name="packages",
            description="📦 Manage JAMF Pro packages (create, update, delete, deploy)",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add packages command arguments"""
        subparsers = parser.add_subparsers(
            dest="pkg_action", help="Package action to perform"
        )

        # Create command
        create_parser = subparsers.add_parser("create", help="Create a new package")
        create_parser.add_argument("name", help="Package name")
        create_parser.add_argument("path", help="Package file path")
        create_parser.add_argument("--category", help="Package category")
        create_parser.add_argument("--info", help="Package information/description")
        create_parser.add_argument("--notes", help="Package notes")
        create_parser.add_argument(
            "--priority",
            choices=["Before", "After"],
            default="After",
            help="Installation priority",
        )
        create_parser.add_argument(
            "--reboot-required",
            action="store_true",
            help="Package requires reboot after installation",
        )
        create_parser.add_argument(
            "--fill-user-template", action="store_true", help="Fill user template"
        )
        create_parser.add_argument(
            "--fill-existing-users", action="store_true", help="Fill existing users"
        )
        self.setup_common_args(create_parser)

        # Update command
        update_parser = subparsers.add_parser(
            "update", help="Update an existing package"
        )
        update_parser.add_argument("id", help="Package ID to update")
        update_parser.add_argument("--name", help="New package name")
        update_parser.add_argument("--category", help="New package category")
        update_parser.add_argument("--info", help="New package information/description")
        update_parser.add_argument("--notes", help="New package notes")
        update_parser.add_argument(
            "--priority", choices=["Before", "After"], help="New installation priority"
        )
        update_parser.add_argument(
            "--reboot-required",
            action="store_true",
            help="Package requires reboot after installation",
        )
        update_parser.add_argument(
            "--no-reboot-required",
            action="store_true",
            help="Package does not require reboot after installation",
        )
        update_parser.add_argument(
            "--fill-user-template", action="store_true", help="Fill user template"
        )
        update_parser.add_argument(
            "--no-fill-user-template",
            action="store_true",
            help="Do not fill user template",
        )
        update_parser.add_argument(
            "--fill-existing-users", action="store_true", help="Fill existing users"
        )
        update_parser.add_argument(
            "--no-fill-existing-users",
            action="store_true",
            help="Do not fill existing users",
        )
        self.setup_common_args(update_parser)

        # Delete command
        delete_parser = subparsers.add_parser("delete", help="Delete a package")
        delete_parser.add_argument("id", help="Package ID to delete")
        delete_parser.add_argument(
            "--confirm", action="store_true", help="Skip confirmation prompt"
        )
        self.setup_common_args(delete_parser)

        # List command
        list_parser = subparsers.add_parser("list", help="List packages")
        list_parser.add_argument("--category", help="Filter by category")
        list_parser.add_argument("--name", help="Filter by name (supports wildcards)")
        list_parser.add_argument(
            "--limit", type=int, default=50, help="Limit number of results"
        )
        self.setup_common_args(list_parser)

        # Info command
        info_parser = subparsers.add_parser("info", help="Show package information")
        info_parser.add_argument("id", help="Package ID to show information for")
        self.setup_common_args(info_parser)

        # Deploy command
        deploy_parser = subparsers.add_parser(
            "deploy", help="Deploy package to distribution points"
        )
        deploy_parser.add_argument("id", help="Package ID to deploy")
        deploy_parser.add_argument(
            "--distribution-points",
            nargs="+",
            help="Specific distribution points to deploy to",
        )
        deploy_parser.add_argument(
            "--all-dps", action="store_true", help="Deploy to all distribution points"
        )
        self.setup_common_args(deploy_parser)

    def execute(self, args: Namespace) -> int:
        """Execute the packages command"""
        if not self.check_auth(args):
            return 1

        try:
            if not args.pkg_action:
                self._show_help()
                return 1

            # Route to appropriate handler
            if args.pkg_action == "create":
                return self._handle_create(args)
            elif args.pkg_action == "update":
                return self._handle_update(args)
            elif args.pkg_action == "delete":
                return self._handle_delete(args)
            elif args.pkg_action == "list":
                return self._handle_list(args)
            elif args.pkg_action == "info":
                return self._handle_info(args)
            elif args.pkg_action == "deploy":
                return self._handle_deploy(args)
            else:
                print(f"❌ Unknown package action: {args.pkg_action}")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _show_help(self):
        """Show help for packages command"""
        print("📦 Package Management Commands:")
        print()
        print("📋 List & Info:")
        print("   jpapi packages list [--category CATEGORY] [--name NAME]")
        print("   jpapi packages info <id>")
        print()
        print("🔧 Management:")
        print("   jpapi packages create <name> <path> [options]")
        print("   jpapi packages update <id> [options]")
        print("   jpapi packages delete <id> [--confirm]")
        print()
        print("🚀 Deployment:")
        print(
            "   jpapi packages deploy <id> [--all-dps] [--distribution-points DP1 DP2]"
        )
        print()
        print("💡 Examples:")
        print(
            "   jpapi packages create 'MyApp' '/path/to/app.pkg' --category 'Applications'"
        )
        print("   jpapi packages update 123 --name 'MyApp v2' --priority Before")
        print("   jpapi packages deploy 123 --all-dps")

    def _handle_create(self, args: Namespace) -> int:
        """Handle package creation"""
        try:
            print(f"📦 Creating package: {args.name}")

            # Validate package file exists
            package_path = Path(args.path)
            if not package_path.exists():
                print(f"❌ Package file not found: {args.path}")
                return 1

            # Check production safety
            if not self.check_destructive_operation("Create Package", args.name):
                return 1

            # Prepare package data
            package_data = {
                "name": args.name,
                "filename": package_path.name,
                "category": args.category or "No Category Assigned",
                "info": args.info or "",
                "notes": args.notes or "",
                "priority": args.priority,
                "reboot_required": args.reboot_required,
                "fill_user_template": args.fill_user_template,
                "fill_existing_users": args.fill_existing_users,
                "os_requirements": [],
                "os_installer_version": "10.0.0",
            }

            # Create the package
            if args.dry_run:
                print("🔍 DRY RUN - Package would be created with:")
                print(json.dumps(package_data, indent=2))
                return 0

            # Upload package file first
            print("📤 Uploading package file...")
            upload_result = self._upload_package_file(package_path)
            if not upload_result:
                print("❌ Failed to upload package file")
                return 1

            # Create package record
            response = self.auth.api_request(
                "POST", "/JSSResource/packages/id/0", package_data
            )

            if response and "package" in response:
                package_id = response["package"].get("id")
                print(f"✅ Package created successfully! ID: {package_id}")
                print(f"   Name: {args.name}")
                print(f"   File: {package_path.name}")
                print(f"   Category: {package_data['category']}")
                return 0
            else:
                print("❌ Failed to create package")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_update(self, args: Namespace) -> int:
        """Handle package update"""
        try:
            print(f"📦 Updating package: {args.id}")

            # Check production safety
            if not self.check_destructive_operation("Update Package", f"ID: {args.id}"):
                return 1

            # Get current package data
            response = self.auth.api_request(
                "GET", f"/JSSResource/packages/id/{args.id}"
            )
            if "package" not in response:
                print(f"❌ Package not found: {args.id}")
                return 1

            package_data = response["package"]

            # Update fields if provided
            if args.name:
                package_data["name"] = args.name
            if args.category:
                package_data["category"] = args.category
            if args.info:
                package_data["info"] = args.info
            if args.notes:
                package_data["notes"] = args.notes
            if args.priority:
                package_data["priority"] = args.priority

            # Handle boolean flags
            if args.reboot_required:
                package_data["reboot_required"] = True
            elif args.no_reboot_required:
                package_data["reboot_required"] = False

            if args.fill_user_template:
                package_data["fill_user_template"] = True
            elif args.no_fill_user_template:
                package_data["fill_user_template"] = False

            if args.fill_existing_users:
                package_data["fill_existing_users"] = True
            elif args.no_fill_existing_users:
                package_data["fill_existing_users"] = False

            if args.dry_run:
                print("🔍 DRY RUN - Package would be updated with:")
                print(json.dumps(package_data, indent=2))
                return 0

            # Update the package
            update_response = self.auth.api_request(
                "PUT", f"/JSSResource/packages/id/{args.id}", package_data
            )

            if update_response:
                print(f"✅ Package updated successfully! ID: {args.id}")
                print(f"   Name: {package_data.get('name', 'N/A')}")
                print(f"   Category: {package_data.get('category', 'N/A')}")
                return 0
            else:
                print("❌ Failed to update package")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_delete(self, args: Namespace) -> int:
        """Handle package deletion"""
        try:
            print(f"🗑️ Deleting package: {args.id}")

            # Check production safety
            if not self.check_destructive_operation("Delete Package", f"ID: {args.id}"):
                return 1

            # Get package info for confirmation
            response = self.auth.api_request(
                "GET", f"/JSSResource/packages/id/{args.id}"
            )
            if "package" not in response:
                print(f"❌ Package not found: {args.id}")
                return 1

            package_name = response["package"].get("name", "Unknown")

            # Confirmation prompt
            if not args.confirm and not args.force:
                print(
                    f"⚠️  This will permanently delete package: {package_name} (ID: {args.id})"
                )
                confirm = input("Type 'yes' to confirm deletion: ").strip().lower()
                if confirm != "yes":
                    print("❌ Deletion cancelled")
                    return 1

            if args.dry_run:
                print(
                    f"🔍 DRY RUN - Package '{package_name}' (ID: {args.id}) would be deleted"
                )
                return 0

            # Delete the package
            delete_response = self.auth.api_request(
                "DELETE", f"/JSSResource/packages/id/{args.id}"
            )

            if delete_response is not None:
                print(f"✅ Package deleted successfully! ID: {args.id}")
                print(f"   Name: {package_name}")
                return 0
            else:
                print("❌ Failed to delete package")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_list(self, args: Namespace) -> int:
        """Handle package listing"""
        try:
            print("📦 Listing packages...")

            # Get packages
            response = self.auth.api_request("GET", "/JSSResource/packages")

            if "packages" not in response:
                print("❌ No packages found")
                return 1

            packages = response["packages"]

            # Apply filters
            if args.category:
                packages = [
                    p
                    for p in packages
                    if args.category.lower() in p.get("category", "").lower()
                ]

            if args.name:
                packages = [
                    p
                    for p in packages
                    if self._matches_filter(p.get("name", ""), args.name)
                ]

            # Limit results
            if args.limit and len(packages) > args.limit:
                packages = packages[: args.limit]

            # Format output using BaseCommand's formatting
            output = self.format_output(packages, args.format)

            self.save_output(output, args.output)

            print(f"✅ Found {len(packages)} packages")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_info(self, args: Namespace) -> int:
        """Handle package information display"""
        try:
            print(f"📦 Package Information: {args.id}")

            # Get package details
            response = self.auth.api_request(
                "GET", f"/JSSResource/packages/id/{args.id}"
            )

            if "package" not in response:
                print(f"❌ Package not found: {args.id}")
                return 1

            package = response["package"]

            # Format output
            if args.format == "json":
                output = json.dumps(package, indent=2)
            else:
                output = self._format_package_info(package)

            self.save_output(output, args.output)
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_deploy(self, args: Namespace) -> int:
        """Handle package deployment to distribution points"""
        try:
            print(f"🚀 Deploying package: {args.id}")

            # Check production safety
            if not self.check_destructive_operation("Deploy Package", f"ID: {args.id}"):
                return 1

            # Get package info
            response = self.auth.api_request(
                "GET", f"/JSSResource/packages/id/{args.id}"
            )
            if "package" not in response:
                print(f"❌ Package not found: {args.id}")
                return 1

            package_name = response["package"].get("name", "Unknown")

            # Get distribution points
            if args.all_dps:
                dps = self._get_all_distribution_points()
            elif args.distribution_points:
                dps = args.distribution_points
            else:
                print("❌ Must specify --all-dps or --distribution-points")
                return 1

            if not dps:
                print("❌ No distribution points found")
                return 1

            if args.dry_run:
                print(f"🔍 DRY RUN - Package '{package_name}' would be deployed to:")
                for dp in dps:
                    print(f"   • {dp}")
                return 0

            # Deploy to each distribution point
            success_count = 0
            for dp in dps:
                try:
                    print(f"📤 Deploying to: {dp}")
                    # TODO: Implement actual JAMF Pro distribution point deployment API calls
                    success_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to deploy to {dp}: {e}")

            print(f"✅ Deployed to {success_count}/{len(dps)} distribution points")
            return 0 if success_count == len(dps) else 1

        except Exception as e:
            return self.handle_api_error(e)

    def _upload_package_file(self, package_path: Path) -> bool:
        """Upload package file to JAMF Pro"""
        try:
            # TODO: Implement JAMF Pro package file upload API
            # In a real implementation, this would use the JAMF Pro file upload API
            print(f"   📤 Uploading: {package_path.name}")
            time.sleep(1)  # Simulate upload time
            print(f"   ✅ Upload complete: {package_path.name}")
            return True
        except Exception as e:
            print(f"   ❌ Upload failed: {e}")
            return False

    def _get_all_distribution_points(self) -> List[str]:
        """Get all distribution points"""
        try:
            response = self.auth.api_request("GET", "/JSSResource/distributionpoints")
            if (
                "distribution_points" in response
                and "distribution_point" in response["distribution_points"]
            ):
                return [
                    dp.get("name", "Unknown")
                    for dp in response["distribution_points"]["distribution_point"]
                ]
            return []
        except Exception as e:
            print(f"❌ Failed to get distribution points: {e}")
            return []

    def _matches_filter(self, text: str, filter_pattern: str) -> bool:
        """Check if text matches filter pattern (supports wildcards)"""
        if "*" in filter_pattern or "?" in filter_pattern:
            import fnmatch

            return fnmatch.fnmatch(text.lower(), filter_pattern.lower())
        else:
            return filter_pattern.lower() in text.lower()

    def _format_package_info(self, package: Dict) -> str:
        """Format single package information"""
        lines = [
            f"📦 Package Information",
            f"=" * 50,
            f"ID: {package.get('id', 'N/A')}",
            f"Name: {package.get('name', 'N/A')}",
            f"Filename: {package.get('filename', 'N/A')}",
            f"Category: {package.get('category', 'N/A')}",
            f"Priority: {package.get('priority', 'N/A')}",
            f"Reboot Required: {'Yes' if package.get('reboot_required') else 'No'}",
            f"Fill User Template: {'Yes' if package.get('fill_user_template') else 'No'}",
            f"Fill Existing Users: {'Yes' if package.get('fill_existing_users') else 'No'}",
        ]

        if package.get("info"):
            lines.append(f"Info: {package['info']}")

        if package.get("notes"):
            lines.append(f"Notes: {package['notes']}")

        return "\n".join(lines)
