#!/usr/bin/env python3
"""
Impact Analyzer - Pre-Deletion Impact Assessment
Assesses the impact of deleting objects from JAMF environment
"""

import json
from typing import Dict, List, Any
from pathlib import Path
from analyzer_interfaces import ImpactAnalyzer, RelationshipEngine, DataProvider


class CSVImpactAnalyzer(ImpactAnalyzer):
    """Impact analyzer that works with CSV data"""

    def __init__(
        self,
        relationship_engine: RelationshipEngine,
        data_provider: DataProvider,
        config_path: str = "analyzer_config.json",
    ):
        self.relationship_engine = relationship_engine
        self.data_provider = data_provider
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load analyzer configuration"""
        try:
            full_path = Path(__file__).parent / config_path
            with open(full_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def assess_deletion_impact(self, obj_type: str, obj_id: str) -> Dict[str, Any]:
        """Assess impact of deleting a single object"""
        # Get object info
        obj_data = self.data_provider.get_object_by_id(obj_type, obj_id)
        if not obj_data:
            return {
                "object": {"type": obj_type, "id": obj_id, "name": "Unknown"},
                "risk_level": "unknown",
                "affected_objects": [],
                "affected_count": 0,
                "recommendations": ["Object not found"],
                "can_delete_safely": False,
                "error": "Object not found",
            }

        # Get relationships
        relationships = self.relationship_engine.analyze_object(obj_type, obj_id)

        # Find what uses this object
        used_by = relationships.get("used_by", [])
        affected_count = len(used_by)

        # Find what this object uses (will become orphaned)
        uses = relationships.get("uses", [])
        potentially_orphaned = []

        for used_obj in uses:
            # Check if any other objects use this dependency
            dep_usage = self.relationship_engine.get_usage_count(
                used_obj["type"], used_obj["id"]
            )
            if dep_usage == 1:  # Only this object uses it
                potentially_orphaned.append(used_obj)

        # Calculate risk level
        risk_level = self.calculate_risk_score(obj_type, obj_id)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            obj_type, obj_data, used_by, potentially_orphaned, risk_level
        )

        # Determine if safe to delete
        can_delete_safely = risk_level == "low" and affected_count == 0

        return {
            "object": {
                "type": obj_type,
                "id": obj_id,
                "name": obj_data.get("Name", "Unknown"),
            },
            "risk_level": risk_level,
            "affected_objects": used_by,
            "affected_count": affected_count,
            "potentially_orphaned": potentially_orphaned,
            "recommendations": recommendations,
            "can_delete_safely": can_delete_safely,
        }

    def assess_batch_impact(self, object_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """Assess impact of deleting multiple objects"""
        all_affected = set()
        individual_impacts = []
        cascading_deletions = []
        highest_risk = "low"

        # Assess each object
        for obj in object_list:
            obj_type = obj.get("type")
            obj_id = obj.get("id")

            impact = self.assess_deletion_impact(obj_type, obj_id)
            individual_impacts.append(impact)

            # Track affected objects
            for affected in impact["affected_objects"]:
                affected_key = f"{affected['type']}:{affected['id']}"
                all_affected.add(affected_key)

            # Track cascading deletions
            for orphaned in impact.get("potentially_orphaned", []):
                cascading_deletions.append(
                    {"orphaned_object": orphaned, "caused_by": f"{obj_type}:{obj_id}"}
                )

            # Track highest risk
            if impact["risk_level"] == "high":
                highest_risk = "high"
            elif impact["risk_level"] == "medium" and highest_risk != "high":
                highest_risk = "medium"

        # Generate batch recommendations
        batch_recommendations = self._generate_batch_recommendations(
            object_list, individual_impacts, len(all_affected), len(cascading_deletions)
        )

        return {
            "objects": object_list,
            "total_affected": len(all_affected),
            "risk_level": highest_risk,
            "individual_impacts": individual_impacts,
            "cascading_deletions": cascading_deletions,
            "recommendations": batch_recommendations,
        }

    def get_affected_objects(self, obj_type: str, obj_id: str) -> List[Dict[str, Any]]:
        """Get list of objects affected by deletion"""
        relationships = self.relationship_engine.analyze_object(obj_type, obj_id)
        return relationships.get("used_by", [])

    def calculate_risk_score(self, obj_type: str, obj_id: str) -> str:
        """Calculate risk level for deletion"""
        # Get usage count
        usage_count = self.relationship_engine.get_usage_count(obj_type, obj_id)

        # Get risk level thresholds from config
        risk_config = self.config.get("impact_analysis", {}).get("risk_levels", {})

        # Determine risk level based on usage
        if usage_count == 0:
            return "low"
        elif usage_count <= risk_config.get("low", {}).get("max_affected", 5):
            return "low"
        elif usage_count <= risk_config.get("medium", {}).get("max_affected", 20):
            return "medium"
        else:
            return "high"

    def _generate_recommendations(
        self,
        obj_type: str,
        obj_data: Dict[str, Any],
        used_by: List[Dict[str, Any]],
        potentially_orphaned: List[Dict[str, Any]],
        risk_level: str,
    ) -> List[str]:
        """Generate recommendations for single object deletion"""
        recommendations = []
        obj_name = obj_data.get("Name", "Unknown")

        # Risk-based recommendations
        if risk_level == "low":
            if len(used_by) == 0:
                recommendations.append(
                    f"✅ Safe to delete. No objects reference this {obj_type}."
                )
            else:
                recommendations.append(
                    f"⚠️ Low impact. {len(used_by)} object(s) will be affected."
                )
        elif risk_level == "medium":
            recommendations.append(
                f"⚠️ Medium risk. {len(used_by)} objects currently use this {obj_type}. "
                f"Review affected objects before deletion."
            )
        else:  # high
            recommendations.append(
                f"🔴 High risk! {len(used_by)} objects depend on this {obj_type}. "
                f"Deletion will cause significant disruption. Consider alternatives."
            )

        # Type-specific recommendations
        if obj_type == "groups":
            if used_by:
                policy_count = sum(1 for obj in used_by if obj["type"] == "policies")
                profile_count = sum(1 for obj in used_by if obj["type"] == "profiles")

                if policy_count > 0:
                    recommendations.append(
                        f"📋 {policy_count} policies will lose this group from their scope."
                    )
                if profile_count > 0:
                    recommendations.append(
                        f"⚙️ {profile_count} profiles will lose this group from their scope."
                    )

                recommendations.append(
                    "💡 Consider reassigning affected policies/profiles to a different group "
                    "before deleting this group."
                )

        elif obj_type == "scripts":
            if used_by:
                recommendations.append(
                    f"📋 {len(used_by)} policies will lose this script execution."
                )
                recommendations.append(
                    "💡 Review policies to either remove script steps or replace with alternative script."
                )

        elif obj_type == "packages":
            if used_by:
                recommendations.append(
                    f"📋 {len(used_by)} policies will lose this package deployment."
                )
                recommendations.append(
                    "💡 Update policies to remove package deployment or use alternative package."
                )

        elif obj_type == "policies":
            if potentially_orphaned:
                orphaned_names = ", ".join(
                    f"{o['type']}:{o['name']}" for o in potentially_orphaned[:3]
                )
                recommendations.append(
                    f"⚠️ {len(potentially_orphaned)} objects will become orphaned: {orphaned_names}"
                )
                if len(potentially_orphaned) > 3:
                    recommendations.append(
                        f"   ... and {len(potentially_orphaned) - 3} more"
                    )

        # Orphaned objects warning
        if potentially_orphaned:
            recommendations.append(
                f"🗑️ Deleting this will orphan {len(potentially_orphaned)} object(s). "
                f"Consider cleaning up orphaned objects after deletion."
            )

        return recommendations

    def _generate_batch_recommendations(
        self,
        object_list: List[Dict[str, str]],
        impacts: List[Dict[str, Any]],
        total_affected: int,
        cascading_count: int,
    ) -> List[str]:
        """Generate recommendations for batch deletion"""
        recommendations = []

        # Overall impact
        recommendations.append(
            f"📊 Batch deletion of {len(object_list)} objects will affect "
            f"{total_affected} other objects in total."
        )

        # Cascading deletions warning
        if cascading_count > 0:
            recommendations.append(
                f"⚠️ Warning: {cascading_count} objects will become orphaned as a result. "
                f"Plan for cleanup of orphaned objects."
            )

        # High risk objects
        high_risk = [i for i in impacts if i["risk_level"] == "high"]
        if high_risk:
            recommendations.append(
                f"🔴 {len(high_risk)} high-risk deletions detected. "
                f"Review these carefully before proceeding."
            )

        # Recommend deletion order
        if len(object_list) > 1:
            recommendations.append(
                "💡 Consider deleting objects in reverse dependency order: "
                "delete objects that use others first, then delete their dependencies."
            )

        return recommendations

    def get_risk_color(self, risk_level: str) -> str:
        """Get color code for risk level"""
        risk_config = self.config.get("impact_analysis", {}).get("risk_levels", {})
        return risk_config.get(risk_level, {}).get("color", "#888888")

    def get_risk_icon(self, risk_level: str) -> str:
        """Get icon for risk level"""
        risk_config = self.config.get("impact_analysis", {}).get("risk_levels", {})
        return risk_config.get(risk_level, {}).get("icon", "❓")
