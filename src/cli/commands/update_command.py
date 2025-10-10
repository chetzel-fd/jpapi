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
        parser.add_argument("csv_file", help="CSV file to update from")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without actually updating",
        )
        parser.add_argument(
            "--confirm", action="store_true", help="Skip confirmation prompts"
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the update command using improved patterns"""
        # Check authentication
        if not self.check_auth(args):
            return 1

        try:
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

        except Exception as e:
            return self.handle_api_error(e)

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
