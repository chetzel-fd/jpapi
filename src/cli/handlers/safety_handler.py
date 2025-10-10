#!/usr/bin/env python3
"""
Safety Handler
Single Responsibility: Handles all safety checks and production guardrails
"""

from typing import List, Dict, Any, Optional
from argparse import Namespace
from core.checks.check_manager import SafetyManager
from core.checks.advanced_checks import RobustGuardrails


class SafetyHandler:
    """Handles safety operations following SRP"""

    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.safety_manager = SafetyManager()
        self.guardrails = RobustGuardrails(environment)

    def is_production_environment(self) -> bool:
        """Check if current environment is production"""
        return self.safety_manager.is_production_environment(self.environment)

    def require_production_confirmation(
        self,
        operation: str,
        details: str = "",
        changes_summary: str = "",
        args: Optional[Namespace] = None,
    ) -> bool:
        """Require explicit confirmation for production operations"""
        return self.guardrails.require_production_confirmation(
            operation=operation,
            details=details,
            changes_summary=changes_summary,
            args=args,
        )

    def check_destructive_operation(
        self, operation: str, resource_name: str = ""
    ) -> bool:
        """Check if operation is destructive and requires extra confirmation"""
        if not self.safety_manager.should_require_confirmation(
            self.environment, operation
        ):
            return True

        return self.require_production_confirmation(
            f"Destructive Operation: {operation}",
            f"Resource: {resource_name}" if resource_name else "",
        )

    def require_dry_run_confirmation(self, operation: str) -> bool:
        """Suggest dry-run mode for production operations"""
        if not self.is_production_environment():
            return True

        print("🔍 DRY-RUN MODE RECOMMENDED")
        print("=" * 40)
        print(f"Operation: {operation}")
        print(f"Environment: {self.environment}")
        print()
        print("💡 Consider using --dry-run to test first:")
        print(f"   jpapi {operation} --dry-run ...")
        print()

        response = (
            input("Continue without dry-run? (type 'yes' to proceed): ").strip().lower()
        )
        return response == "yes"

    def create_bulk_changes_summary(self, operation_type: str, objects: list) -> str:
        """Create a comprehensive summary for bulk operations"""
        summary = f"\n{operation_type} Summary:\n"
        summary += f"  • Total Objects: {len(objects)}\n"

        # Group by type
        by_type = {}
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

        summary += f"\n  Impact: Will {operation_type.lower()} {len(objects)} objects in PRODUCTION"
        return summary

    def validate_operation_safety(
        self, operation: str, args: Namespace
    ) -> Dict[str, Any]:
        """Validate operation safety and return safety report"""
        safety_report = {
            "is_safe": True,
            "warnings": [],
            "recommendations": [],
            "requires_confirmation": False,
        }

        # Check if production environment
        if self.is_production_environment():
            safety_report["warnings"].append("Running in PRODUCTION environment")
            safety_report["requires_confirmation"] = True

        # Check for destructive operations
        destructive_keywords = ["delete", "remove", "destroy", "wipe", "clear"]
        if any(keyword in operation.lower() for keyword in destructive_keywords):
            safety_report["warnings"].append("This is a destructive operation")
            safety_report["requires_confirmation"] = True

        # Check for bulk operations
        if hasattr(args, "objects") and len(getattr(args, "objects", [])) > 10:
            safety_report["warnings"].append(
                "This is a bulk operation affecting many objects"
            )
            safety_report["recommendations"].append("Consider using --dry-run first")

        # Check for force flag
        if hasattr(args, "force") and getattr(args, "force", False):
            safety_report["warnings"].append(
                "Force flag is enabled - safety checks bypassed"
            )

        # Overall safety assessment
        safety_report["is_safe"] = len(safety_report["warnings"]) == 0

        return safety_report

    def get_safety_recommendations(self, operation: str) -> List[str]:
        """Get safety recommendations for an operation"""
        recommendations = []

        if self.is_production_environment():
            recommendations.append("Use --dry-run to test changes first")
            recommendations.append("Review changes carefully before applying")
            recommendations.append("Consider running during maintenance window")

        if "delete" in operation.lower() or "remove" in operation.lower():
            recommendations.append("Verify you have backups before proceeding")
            recommendations.append("Double-check the objects you're about to delete")

        if "bulk" in operation.lower() or "batch" in operation.lower():
            recommendations.append("Test with a small subset first")
            recommendations.append("Monitor the operation progress")

        return recommendations

    def create_safety_checklist(self, operation: str) -> List[str]:
        """Create a safety checklist for an operation"""
        checklist = [
            "✅ Verified the correct environment",
            "✅ Confirmed the operation details",
            "✅ Reviewed affected objects/resources",
        ]

        if self.is_production_environment():
            checklist.extend(
                [
                    "✅ Tested changes in development first",
                    "✅ Notified relevant stakeholders",
                    "✅ Prepared rollback plan",
                ]
            )

        if "delete" in operation.lower():
            checklist.extend(
                [
                    "✅ Verified backups are current",
                    "✅ Confirmed no dependencies exist",
                    "✅ Double-checked object selection",
                ]
            )

        return checklist

    def log_safety_event(self, operation: str, details: Dict[str, Any]) -> None:
        """Log safety-related events"""
        import logging

        logger = logging.getLogger("SafetyHandler")

        logger.info(f"Safety event - Operation: {operation}")
        for key, value in details.items():
            logger.info(f"  {key}: {value}")

    def get_environment_safety_level(self) -> str:
        """Get safety level for current environment"""
        if self.environment.lower() == "prod":
            return "HIGH - Production environment requires extra caution"
        elif self.environment.lower() == "dev":
            return "LOW - Development environment is safe for testing"
        else:
            return "MEDIUM - Staging environment requires moderate caution"



