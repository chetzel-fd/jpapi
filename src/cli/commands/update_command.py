#!/usr/bin/env python3
"""
Improved Update Command for jpapi CLI
Refactored using configuration-driven approach and improved base class
"""

import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path
import csv

from ..base.command import BaseCommand
from .export import ExportUpdates
from resources.config.api_endpoints import APIRegistry

# from ...config import get_command_config


class UpdateCommand(BaseCommand):
    """Improved update command using configuration-driven approach"""

    def __init__(self):
        super().__init__(
            name="update", description="Update JAMF objects from CSV files"
        )
        self.update_handler = None

    def add_arguments(self, parser):
        """Add command arguments"""
        # Create subparsers for different update types
        subparsers = parser.add_subparsers(
            dest="update_type", help="Type of update operation"
        )

        # CSV-based bulk update (backward compatibility)
        csv_parser = subparsers.add_parser("csv", help="Update objects from CSV file")
        csv_parser.add_argument("csv_file", help="CSV file to update from")
        csv_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without actually updating",
        )
        csv_parser.add_argument(
            "--confirm", action="store_true", help="Skip confirmation prompts"
        )

        # Extension attribute update
        ext_attr_parser = subparsers.add_parser(
            "extension-attribute",
            aliases=["ext-attr", "attribute"],
            help="Update extension attribute",
        )
        ext_attr_parser.add_argument("id", help="Extension attribute ID")
        ext_attr_parser.add_argument(
            "--type",
            choices=["computer", "mobile", "user"],
            default="computer",
            help="Attribute type (default: computer)",
        )
        ext_attr_parser.add_argument("--name", help="New name")
        ext_attr_parser.add_argument("--description", help="New description")
        ext_attr_parser.add_argument(
            "--enabled",
            type=lambda x: x.lower() == "true",
            help="Enable/disable (true/false)",
        )
        self.setup_common_args(ext_attr_parser)

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the update command using improved patterns"""
        # Check authentication
        if not self.check_auth(args):
            return 1

        try:
            # Route based on update type
            if not hasattr(args, "update_type") or not args.update_type:
                print("🔄 Update JAMF Objects:")
                print()
                print("💬 Update Types:")
                print("   jpapi update csv <file> - Bulk update from CSV")
                print(
                    "   jpapi update extension-attribute <id> - Update extension attribute"
                )
                print()
                return 0

            if args.update_type == "csv":
                return self._update_from_csv(args)
            elif args.update_type in ["extension-attribute", "ext-attr", "attribute"]:
                return self._update_extension_attribute(args)
            else:
                print(f"❌ Unknown update type: {args.update_type}")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _update_from_csv(self, args: argparse.Namespace) -> int:
        """Update objects from CSV file"""
        # Initialize update handler if needed
        if not self.update_handler:
            self.update_handler = ExportUpdates(self.auth)

        # Validate object type
        object_type = self._normalize_object_type(args.object_type)
        if not object_type:
            print(f"❌ Update not supported for object type: {args.object_type}")
            print(
                "   Supported types: computer-groups, policies, scripts, advanced-searches"
            )
            return 1

        # Validate CSV file
        if not self._validate_csv_file(args.csv_file):
            return 1

        print(f"🔄 Updating {object_type} from: {args.csv_file}")

        # Route to appropriate update handler
        result = self.update_handler.update_from_csv(args)

        # Post-execution processing
        return self.post_execute(args, result)

    def _normalize_object_type(self, object_type: str) -> Optional[str]:
        """Normalize object type using alias manager"""
        from ..config import alias_manager

        normalized = alias_manager.get_command_name(object_type.lower())

        # Map to supported types
        type_mapping = {
            "computer-groups": "computer-groups",
            "policies": "policies",
            "scripts": "scripts",
            "advanced-searches": "advanced-searches",
            "adv": "advanced-searches",
            "advanced": "advanced-searches",
            "searches": "advanced-searches",
        }

        return type_mapping.get(normalized)

    def _validate_csv_file(self, csv_file: str) -> bool:
        """Validate CSV file exists and is readable"""
        try:
            file_path = Path(csv_file)
            if not file_path.exists():
                print(f"❌ CSV file not found: {csv_file}")
                return False

            if not file_path.is_file():
                print(f"❌ Path is not a file: {csv_file}")
                return False

            # Test if file is readable
            with open(file_path, "r", encoding="utf-8") as f:
                # Try to read first line to validate CSV format
                first_line = f.readline()
                if not first_line.strip():
                    print(f"❌ CSV file is empty: {csv_file}")
                    return False

            return True

        except Exception as e:
            print(f"❌ Error validating CSV file: {e}")
            return False

    def _update_extension_attribute(self, args: argparse.Namespace) -> int:
        """Update an extension attribute"""
        try:
            attr_type = getattr(args, "type", "computer")
            attr_id = args.id

            print(f"🔄 Updating {attr_type} extension attribute: ID {attr_id}")

            # Get endpoint from APIRegistry
            try:
                endpoint = APIRegistry.get_single_endpoint(attr_type, attr_id)
            except ValueError:
                print(f"❌ Unknown attribute type: {attr_type}")
                return 1

            # Get existing attribute data
            try:
                response = self.auth.api_request("GET", endpoint)
            except Exception as e:
                print(f"❌ Failed to fetch attribute: {e}")
                return 1

            # Extract the extension attribute data
            attr_key = f"{attr_type}_extension_attribute"
            if attr_key not in response:
                print(f"❌ Attribute with ID {attr_id} not found")
                return 1

            attr_data = response[attr_key]
            print(f"   Current Name: {attr_data.get('name', 'Unknown')}")

            # Update fields if provided
            updated = False
            if hasattr(args, "name") and args.name:
                attr_data["name"] = args.name
                print(f"   New Name: {args.name}")
                updated = True

            if hasattr(args, "description") and args.description is not None:
                attr_data["description"] = args.description
                print(f"   New Description: {args.description}")
                updated = True

            if hasattr(args, "enabled") and args.enabled is not None:
                attr_data["enabled"] = args.enabled
                print(f"   Enabled: {args.enabled}")
                updated = True

            if not updated:
                print(
                    "❌ No fields to update (use --name, --description, or --enabled)"
                )
                return 1

            # Prepare update data
            update_data = {attr_key: attr_data}

            # Make API request
            response = self.auth.api_request("PUT", endpoint, data=update_data)

            if response:
                print("✅ Extension attribute updated successfully!")
                return 0
            else:
                print("❌ Failed to update: No response from API")
                return 1

        except Exception as e:
            print(f"❌ Failed to update extension attribute: {e}")
            return 1

    def pre_execute(self, args: argparse.Namespace) -> bool:
        """Pre-execution validation"""
        # Check if running in production
        if self.is_production_environment():
            print("🚨 WARNING: You are operating in PRODUCTION environment!")
            print(f"   Environment: {self.environment}")
            print("   Use --dry-run to test operations safely")
            print("   Use --force to skip confirmation prompts")
            print()

        # Validate arguments
        if not self.validate_arguments(args):
            return False

        return True

    def validate_arguments(self, args: argparse.Namespace) -> bool:
        """Validate command arguments"""
        # Check for conflicting options
        if hasattr(args, "only_updates") and hasattr(args, "only_deletes"):
            if args.only_updates and args.only_deletes:
                print("❌ Cannot use --only-updates and --only-deletes together")
                return False

        # Validate filter pattern if provided
        if hasattr(args, "filter") and args.filter:
            if not self._validate_filter_pattern(args.filter):
                return False

        # Validate IDs if provided
        if hasattr(args, "ids") and args.ids:
            if not self._validate_ids(args.ids):
                return False

        return True

    def _validate_filter_pattern(self, pattern: str) -> bool:
        """Validate filter pattern"""
        if not pattern or not isinstance(pattern, str):
            print("❌ Filter pattern must be a non-empty string")
            return False

        # Check for dangerous patterns
        dangerous_patterns = ["..", "/", "\\", ";", "|", "&", "`"]
        for dangerous in dangerous_patterns:
            if dangerous in pattern:
                print(f"❌ Filter pattern contains dangerous character: {dangerous}")
                return False

        return True

    def _validate_ids(self, ids: List[str]) -> bool:
        """Validate ID list"""
        if not ids:
            return True

        for id in ids:
            if not id.isdigit():
                print(f"❌ Invalid ID format: {id}")
                return False

        return True

    def post_execute(self, args: argparse.Namespace, result: int) -> int:
        """Post-execution processing"""
        if result == 0:
            print("✅ Update completed successfully")
        else:
            print("❌ Update completed with errors")

        return result
