#!/usr/bin/env python3
"""
Export Analysis Utilities
Enhanced analysis capabilities for export data
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re


class ExportAnalyzer:
    """Analyzer for export data with enhanced insights"""

    def __init__(self):
        self.security_keywords = [
            "security",
            "compliance",
            "audit",
            "firewall",
            "antivirus",
            "encryption",
            "certificate",
            "ssl",
            "tls",
            "vulnerability",
        ]
        self.maintenance_keywords = [
            "update",
            "patch",
            "maintenance",
            "cleanup",
            "backup",
            "restore",
            "upgrade",
            "install",
            "uninstall",
        ]
        self.critical_keywords = [
            "critical",
            "essential",
            "important",
            "urgent",
            "emergency",
        ]

    def analyze_export_data(
        self, data: List[Dict[str, Any]], data_type: str
    ) -> Dict[str, Any]:
        """Perform comprehensive analysis on export data"""
        if not data:
            return {"error": "No data to analyze"}

        analysis = {
            "summary": self._generate_summary(data, data_type),
            "insights": self._generate_insights(data, data_type),
            "recommendations": self._generate_recommendations(data, data_type),
            "statistics": self._calculate_statistics(data, data_type),
            "health_check": self._perform_health_check(data, data_type),
        }

        return analysis

    def _generate_summary(
        self, data: List[Dict[str, Any]], data_type: str
    ) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_count = len(data)

        # Count by status
        enabled_count = sum(
            1
            for item in data
            if item.get("Enabled", False) or item.get("Status") == "Enabled"
        )
        disabled_count = total_count - enabled_count

        # Count by category
        categories = {}
        for item in data:
            category = item.get("Category", "Uncategorized")
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_items": total_count,
            "enabled_items": enabled_count,
            "disabled_items": disabled_count,
            "enabled_percentage": (
                round((enabled_count / total_count) * 100, 2) if total_count > 0 else 0
            ),
            "category_distribution": categories,
            "most_common_category": (
                max(categories.items(), key=lambda x: x[1])[0] if categories else "None"
            ),
        }

    def _generate_insights(
        self, data: List[Dict[str, Any]], data_type: str
    ) -> List[str]:
        """Generate insights about the data"""
        insights = []

        # Check for patterns
        if data_type == "policies":
            insights.extend(self._analyze_policy_patterns(data))
        elif data_type == "scripts":
            insights.extend(self._analyze_script_patterns(data))
        elif data_type == "profiles":
            insights.extend(self._analyze_profile_patterns(data))

        # General insights
        insights.extend(self._analyze_general_patterns(data))

        return insights

    def _analyze_policy_patterns(self, data: List[Dict[str, Any]]) -> List[str]:
        """Analyze policy-specific patterns"""
        insights = []

        # Check for disabled policies
        disabled_policies = [p for p in data if not p.get("Enabled", False)]
        if disabled_policies:
            insights.append(
                f"⚠️ Found {len(disabled_policies)} disabled policies that may need review"
            )

        # Check for policies without scripts
        no_script_policies = [p for p in data if not p.get("Script_Name")]
        if no_script_policies:
            insights.append(
                f"📝 Found {len(no_script_policies)} policies without scripts"
            )

        # Check for security-related policies
        security_policies = [
            p
            for p in data
            if any(
                keyword in p.get("Name", "").lower()
                for keyword in self.security_keywords
            )
        ]
        if security_policies:
            insights.append(
                f"🔒 Found {len(security_policies)} security-related policies"
            )

        return insights

    def _analyze_script_patterns(self, data: List[Dict[str, Any]]) -> List[str]:
        """Analyze script-specific patterns"""
        insights = []

        # Check for scripts without descriptions
        no_desc_scripts = [s for s in data if not s.get("Description")]
        if no_desc_scripts:
            insights.append(
                f"📝 Found {len(no_desc_scripts)} scripts without descriptions"
            )

        # Check for maintenance scripts
        maintenance_scripts = [
            s
            for s in data
            if any(
                keyword in s.get("Name", "").lower()
                for keyword in self.maintenance_keywords
            )
        ]
        if maintenance_scripts:
            insights.append(
                f"🔧 Found {len(maintenance_scripts)} maintenance-related scripts"
            )

        return insights

    def _analyze_profile_patterns(self, data: List[Dict[str, Any]]) -> List[str]:
        """Analyze profile-specific patterns"""
        insights = []

        # Check for system-level profiles
        system_profiles = [p for p in data if p.get("Level") == "System"]
        if system_profiles:
            insights.append(f"🖥️ Found {len(system_profiles)} system-level profiles")

        # Check for user-removable profiles
        removable_profiles = [p for p in data if p.get("User Removal", False)]
        if removable_profiles:
            insights.append(
                f"👤 Found {len(removable_profiles)} user-removable profiles"
            )

        return insights

    def _analyze_general_patterns(self, data: List[Dict[str, Any]]) -> List[str]:
        """Analyze general patterns across all data types"""
        insights = []

        # Check for items without categories
        uncategorized = [item for item in data if not item.get("Category")]
        if uncategorized:
            insights.append(f"📂 Found {len(uncategorized)} uncategorized items")

        # Check for recent modifications
        recent_items = [item for item in data if self._is_recently_modified(item)]
        if recent_items:
            insights.append(f"🕒 Found {len(recent_items)} recently modified items")

        return insights

    def _is_recently_modified(self, item: Dict[str, Any]) -> bool:
        """Check if item was modified recently (within last 30 days)"""
        modified_date = item.get("Modified_Date", item.get("modified", ""))
        if not modified_date:
            return False

        try:
            # This would need proper date parsing in a real implementation
            # For now, just return False
            return False
        except:
            return False

    def _generate_recommendations(
        self, data: List[Dict[str, Any]], data_type: str
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # General recommendations
        recommendations.append(
            "📋 Review disabled items to determine if they're still needed"
        )
        recommendations.append("📝 Add descriptions to items that lack them")
        recommendations.append(
            "📂 Categorize uncategorized items for better organization"
        )

        # Type-specific recommendations
        if data_type == "policies":
            recommendations.append("🔍 Review policies without scripts")
            recommendations.append(
                "⚡ Consider enabling disabled policies if still relevant"
            )
        elif data_type == "scripts":
            recommendations.append(
                "📖 Add documentation to scripts without descriptions"
            )
            recommendations.append("🔧 Review maintenance scripts for updates")
        elif data_type == "profiles":
            recommendations.append("🎯 Review scope of system-level profiles")
            recommendations.append(
                "👤 Consider user-removable profiles for flexibility"
            )

        return recommendations

    def _calculate_statistics(
        self, data: List[Dict[str, Any]], data_type: str
    ) -> Dict[str, Any]:
        """Calculate detailed statistics"""
        stats = {
            "total_items": len(data),
            "by_category": {},
            "by_status": {},
            "by_priority": {},
            "complexity_distribution": {},
        }

        # Count by category
        for item in data:
            category = item.get("Category", "Uncategorized")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        # Count by status
        for item in data:
            if item.get("Enabled", False):
                stats["by_status"]["Enabled"] = stats["by_status"].get("Enabled", 0) + 1
            else:
                stats["by_status"]["Disabled"] = (
                    stats["by_status"].get("Disabled", 0) + 1
                )

        return stats

    def _perform_health_check(
        self, data: List[Dict[str, Any]], data_type: str
    ) -> Dict[str, Any]:
        """Perform health check on the data"""
        health = {"overall_score": 0, "issues": [], "warnings": [], "suggestions": []}

        score = 100

        # Check for disabled items
        disabled_count = sum(1 for item in data if not item.get("Enabled", False))
        if disabled_count > len(data) * 0.5:
            health["issues"].append(f"High number of disabled items ({disabled_count})")
            score -= 20

        # Check for missing descriptions
        no_desc_count = sum(1 for item in data if not item.get("Description"))
        if no_desc_count > len(data) * 0.3:
            health["warnings"].append(f"Many items lack descriptions ({no_desc_count})")
            score -= 10

        # Check for uncategorized items
        uncategorized_count = sum(1 for item in data if not item.get("Category"))
        if uncategorized_count > len(data) * 0.2:
            health["suggestions"].append(
                f"Consider categorizing items ({uncategorized_count})"
            )
            score -= 5

        health["overall_score"] = max(0, score)

        return health


def analyze_export_file(file_path: str, data_type: str) -> Dict[str, Any]:
    """Analyze an export file and return insights"""
    try:
        import csv
        import json
        from pathlib import Path

        file_path = Path(file_path)
        if not file_path.exists():
            return {"error": "File not found"}

        # Read the file based on extension
        data = []
        if file_path.suffix == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                data = list(reader)
        elif file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            return {"error": "Unsupported file format"}

        # Analyze the data
        analyzer = ExportAnalyzer()
        return analyzer.analyze_export_data(data, data_type)

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}
