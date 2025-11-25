#!/usr/bin/env python3
"""
Orphan Detector - Find Unused/Orphaned Objects
Identifies objects with no references in the JAMF environment
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from analyzer_interfaces import OrphanDetector, RelationshipEngine, DataProvider


class CSVOrphanDetector(OrphanDetector):
    """Orphan detector that works with CSV data"""

    def __init__(
        self,
        relationship_engine: RelationshipEngine,
        data_provider: DataProvider,
        config_path: str = "analyzer_config.json",
    ):
        self.relationship_engine = relationship_engine
        self.data_provider = data_provider
        self.config = self._load_config(config_path)
        self._orphan_cache: Dict[str, List[Dict[str, Any]]] = {}

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load analyzer configuration"""
        try:
            full_path = Path(__file__).parent / config_path
            with open(full_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def find_orphaned_objects(
        self, obj_type: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find orphaned objects by type"""
        orphans = {}

        # Determine which types to check
        types_to_check = [obj_type] if obj_type else ["groups", "scripts", "packages"]

        for check_type in types_to_check:
            try:
                type_orphans = self._find_orphans_for_type(check_type)
                if type_orphans:
                    orphans[check_type] = type_orphans
            except Exception as e:
                print(f"Error finding orphans for {check_type}: {e}")
                orphans[check_type] = []

        return orphans

    def _find_orphans_for_type(self, obj_type: str) -> List[Dict[str, Any]]:
        """Find orphaned objects for specific type"""
        orphans = []

        # Get exclude patterns from config
        exclude_patterns = self.config.get("orphan_detection", {}).get(
            "exclude_patterns", []
        )
        min_age_days = self.config.get("orphan_detection", {}).get("min_age_days", 30)

        try:
            # Load all objects of this type
            objects_df = self.data_provider.load_objects(
                obj_type, "sandbox"
            )  # Default to sandbox

            if objects_df.empty:
                return orphans

            # Check each object
            for _, obj_row in objects_df.iterrows():
                obj_dict = obj_row.to_dict()
                obj_id = str(obj_dict.get("ID", ""))
                obj_name = obj_dict.get("Name", "Unknown")

                # Skip excluded patterns
                if any(
                    pattern.lower() in obj_name.lower() for pattern in exclude_patterns
                ):
                    continue

                # Check if object is used
                usage_count = self.relationship_engine.get_usage_count(obj_type, obj_id)

                if usage_count == 0:
                    # Object is orphaned!
                    last_modified = obj_dict.get(
                        "Last Modified", obj_dict.get("Modified", "Unknown")
                    )

                    # Check age if we have modification date
                    is_old_enough = True
                    if last_modified != "Unknown" and min_age_days > 0:
                        try:
                            modified_date = datetime.strptime(
                                str(last_modified), "%Y-%m-%d"
                            )
                            days_old = (datetime.now() - modified_date).days
                            is_old_enough = days_old >= min_age_days
                        except (ValueError, TypeError):
                            # If we can't parse date, include it anyway
                            pass

                    if is_old_enough:
                        orphans.append(
                            {
                                "id": obj_id,
                                "name": obj_name,
                                "type": obj_type,
                                "last_modified": last_modified,
                                "usage_count": 0,
                                "status": obj_dict.get("Status", "Unknown"),
                            }
                        )

        except Exception as e:
            print(f"Error finding orphans for {obj_type}: {e}")

        return orphans

    def generate_cleanup_report(self) -> Dict[str, Any]:
        """Generate comprehensive cleanup report"""
        # Find all orphans
        all_orphans = self.find_orphaned_objects()

        # Count totals
        total_orphans = sum(len(orphans) for orphans in all_orphans.values())
        by_type = {obj_type: len(orphans) for obj_type, orphans in all_orphans.items()}

        # Generate recommendations
        recommendations = self._generate_recommendations(all_orphans)

        # Identify safe to delete (very old, definitely unused)
        safe_delete_threshold = self.config.get("orphan_detection", {}).get(
            "safe_delete_threshold", {"usage_count": 0, "min_age_days": 90}
        )

        safe_to_delete = []
        for obj_type, orphans in all_orphans.items():
            for orphan in orphans:
                # Check if old enough to be safe
                last_modified = orphan.get("last_modified", "Unknown")
                if last_modified != "Unknown":
                    try:
                        modified_date = datetime.strptime(
                            str(last_modified), "%Y-%m-%d"
                        )
                        days_old = (datetime.now() - modified_date).days

                        if days_old >= safe_delete_threshold["min_age_days"]:
                            safe_to_delete.append(
                                {
                                    "type": obj_type,
                                    "id": orphan["id"],
                                    "name": orphan["name"],
                                    "days_old": days_old,
                                }
                            )
                    except (ValueError, TypeError):
                        pass

        return {
            "total_orphans": total_orphans,
            "by_type": by_type,
            "recommendations": recommendations,
            "safe_to_delete": safe_to_delete,
            "all_orphans": all_orphans,
            "generated_at": datetime.now().isoformat(),
        }

    def _generate_recommendations(
        self, orphans: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """Generate cleanup recommendations"""
        recommendations = []

        for obj_type, orphan_list in orphans.items():
            if not orphan_list:
                continue

            count = len(orphan_list)

            if obj_type == "groups":
                recommendations.append(
                    f"Found {count} orphaned groups. These groups are not used by any policies or profiles. "
                    f"Review and consider deleting if no longer needed."
                )
            elif obj_type == "scripts":
                recommendations.append(
                    f"Found {count} orphaned scripts. These scripts are not used by any policies. "
                    f"Archive or delete if they are deprecated."
                )
            elif obj_type == "packages":
                recommendations.append(
                    f"Found {count} orphaned packages. These packages are not deployed by any policies. "
                    f"Consider removing to free up storage space."
                )

        # General recommendations
        if sum(len(o) for o in orphans.values()) > 20:
            recommendations.append(
                "⚠️ Large number of orphans detected. Consider implementing a regular cleanup schedule."
            )

        if not recommendations:
            recommendations.append(
                "✅ No orphaned objects found. Your environment is clean!"
            )

        return recommendations

    def is_orphaned(self, obj_type: str, obj_id: str) -> bool:
        """Check if specific object is orphaned"""
        usage_count = self.relationship_engine.get_usage_count(obj_type, obj_id)
        return usage_count == 0

    def get_orphan_count(self, obj_type: Optional[str] = None) -> int:
        """Get total count of orphaned objects"""
        orphans = self.find_orphaned_objects(obj_type)
        return sum(len(orphan_list) for orphan_list in orphans.values())

    def export_orphans_csv(self, orphans: Dict[str, List[Dict[str, Any]]]) -> str:
        """Export orphans to CSV format string"""
        import pandas as pd

        # Flatten orphans into single list
        all_orphans = []
        for obj_type, orphan_list in orphans.items():
            for orphan in orphan_list:
                orphan["object_type"] = obj_type
                all_orphans.append(orphan)

        if not all_orphans:
            return "No orphaned objects found."

        # Create DataFrame
        df = pd.DataFrame(all_orphans)

        # Select columns
        columns = [
            "object_type",
            "id",
            "name",
            "last_modified",
            "usage_count",
            "status",
        ]
        df = df[[col for col in columns if col in df.columns]]

        # Return as CSV string
        return df.to_csv(index=False)

    def clear_cache(self):
        """Clear orphan cache"""
        self._orphan_cache.clear()
