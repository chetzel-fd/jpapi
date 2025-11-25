#!/usr/bin/env python3
"""
Safety Validator for CLI Commands
Handles production environment safety checks and confirmations
Extracted from BaseCommand for SRP compliance
"""

from argparse import Namespace
from typing import Optional
from datetime import datetime

try:
    from core.checks.check_manager import SafetyManager
except ImportError:
    # Fallback if module not found
    SafetyManager = None


class SafetyValidator:
    """Handles production safety validations for CLI commands"""

    def __init__(self, safety_manager: Optional[any] = None):
        if SafetyManager:
            self.safety_manager = safety_manager or SafetyManager()
        else:
            self.safety_manager = safety_manager

    def is_production_environment(self, environment: str) -> bool:
        """Check if current environment is production"""
        return self.safety_manager.is_production_environment(environment)

    def require_production_confirmation(
        self,
        environment: str,
        operation: str,
        details: str = "",
        changes_summary: str = "",
        args: Optional[Namespace] = None,
    ) -> bool:
        """
        Require explicit confirmation for production operations

        Args:
            environment: Current environment
            operation: Operation being performed
            details: Additional operation details
            changes_summary: Summary of changes to be made
            args: Command arguments (for force flag)

        Returns:
            True if confirmed, False if cancelled
        """
        if not self.is_production_environment(environment):
            return True

        # Check for force flag
        if args and getattr(args, "force", False):
            print("🔒 Force flag detected - skipping production confirmation")
            return True

        print("🚨 PRODUCTION ENVIRONMENT DETECTED 🚨")
        print("=" * 60)
        print(f"Operation: {operation}")
        if details:
            print(f"Details: {details}")
        print(f"Environment: {environment}")
        print(f"Timestamp: {self._get_timestamp()}")
        print("=" * 60)

        # Show comprehensive changes summary
        if changes_summary:
            print("\n📋 CHANGES SUMMARY:")
            print("-" * 40)
            print(changes_summary)
            print("-" * 40)

        print("\n⚠️  This will modify PRODUCTION data.")
        print("💡 Use --dry-run to test operations safely")
        print("🔒 Use --force to skip this confirmation")
        print()

        # Enhanced confirmation
        print("🔐 SAFETY CONFIRMATION REQUIRED")
        print("=" * 40)
        response = (
            input("Do you want to proceed with this PRODUCTION operation? (y/N): ")
            .strip()
            .lower()
        )

        if response not in ["y", "yes"]:
            print("❌ Operation cancelled")
            return False

        # Additional confirmation for high-risk operations
        safety_word = (
            input("Are you absolutely sure you want to proceed? (y/N): ")
            .strip()
            .lower()
        )
        if safety_word not in ["y", "yes"]:
            print("❌ Operation cancelled - second confirmation failed")
            return False

        print("✅ Production operation confirmed. Proceeding...")
        return True

    def require_dry_run_confirmation(self, environment: str, operation: str) -> bool:
        """Suggest dry-run mode for production operations"""
        if not self.is_production_environment(environment):
            return True

        print("🔍 DRY-RUN MODE RECOMMENDED")
        print("=" * 40)
        print(f"Operation: {operation}")
        print(f"Environment: {environment}")
        print()
        print("💡 Consider using --dry-run to test first:")
        print(f"   jpapi {operation} --dry-run ...")
        print()

        response = (
            input("Continue without dry-run? (type 'yes' to proceed): ").strip().lower()
        )
        return response == "yes"

    def check_destructive_operation(
        self, environment: str, operation: str, resource_name: str = ""
    ) -> bool:
        """Check if operation is destructive and requires confirmation"""
        if not self.safety_manager:
            return True
        if not self.safety_manager.should_require_confirmation(environment, operation):
            return True

        details = f"Resource: {resource_name}" if resource_name else ""
        return self.require_production_confirmation(
            environment, f"Destructive Operation: {operation}", details
        )

    def create_bulk_changes_summary(self, operation_type: str, objects: list) -> str:
        """
        Create a comprehensive summary for bulk operations

        Args:
            operation_type: Type of operation (Update, Delete, etc.)
            objects: List of objects being operated on

        Returns:
            Formatted summary string
        """
        summary = f"\n{operation_type} Summary:\n"
        summary += f"  • Total Objects: {len(objects)}\n"

        # Group by type
        by_type: dict = {}
        for obj in objects:
            obj_type = obj.get("type", "Unknown")
            if obj_type not in by_type:
                by_type[obj_type] = []
            by_type[obj_type].append(obj)

        for obj_type, items in by_type.items():
            summary += f"\n  {obj_type.upper()} ({len(items)} items):\n"
            for item in items[:5]:  # Show first 5 items
                name = item.get("name", "Unknown")
                summary += f"    • {name}\n"
            if len(items) > 5:
                summary += f"    • ... and {len(items) - 5} more\n"

        summary += (
            f"\n  Impact: Will {operation_type.lower()} "
            f"{len(objects)} objects in PRODUCTION"
        )
        return summary

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp for logging"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
