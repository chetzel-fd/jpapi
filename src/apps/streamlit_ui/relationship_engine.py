#!/usr/bin/env python3
"""
Relationship Engine - Core Analysis Logic
Analyzes object relationships from CSV data
"""

import json
import pandas as pd
from typing import Dict, List, Any, Set, Optional
from pathlib import Path
from analyzer_interfaces import RelationshipEngine, DataProvider


class CSVRelationshipEngine(RelationshipEngine):
    """Relationship engine that analyzes CSV data"""

    def __init__(
        self, data_provider: DataProvider, config_path: str = "analyzer_config.json"
    ):
        self.data_provider = data_provider
        self.config = self._load_config(config_path)
        self._relationship_cache: Dict[str, Any] = {}
        self._object_cache: Dict[str, Dict[str, Any]] = {}

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load analyzer configuration"""
        try:
            full_path = Path(__file__).parent / config_path
            with open(full_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"relationship_types": {}}

    def analyze_object(self, obj_type: str, obj_id: str) -> Dict[str, Any]:
        """Analyze relationships for a single object"""
        # Check cache
        cache_key = f"{obj_type}_{obj_id}"
        if cache_key in self._relationship_cache:
            return self._relationship_cache[cache_key]

        # Get object details
        obj_data = self.data_provider.get_object_by_id(obj_type, obj_id)
        if not obj_data:
            return {
                "object": {"type": obj_type, "id": obj_id, "name": "Unknown"},
                "uses": [],
                "used_by": [],
                "usage_count": 0,
                "error": "Object not found",
            }

        # Analyze relationships
        uses = self._find_objects_used_by(obj_type, obj_id, obj_data)
        used_by = self._find_objects_using(obj_type, obj_id)

        result = {
            "object": {
                "type": obj_type,
                "id": obj_id,
                "name": obj_data.get("Name", "Unknown"),
            },
            "uses": uses,
            "used_by": used_by,
            "usage_count": len(used_by),
        }

        # Cache result
        self._relationship_cache[cache_key] = result
        return result

    def analyze_batch(self, object_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze relationships for multiple objects"""
        results = []
        all_dependencies = set()
        shared_dependencies = {}

        for obj in object_list:
            obj_type = obj.get("type")
            obj_id = obj.get("id")

            analysis = self.analyze_object(obj_type, obj_id)
            results.append(analysis)

            # Track dependencies
            for dep in analysis["uses"]:
                dep_key = f"{dep['type']}:{dep['id']}"
                all_dependencies.add(dep_key)
                if dep_key not in shared_dependencies:
                    shared_dependencies[dep_key] = []
                shared_dependencies[dep_key].append(f"{obj_type}:{obj_id}")

        # Find truly shared dependencies (used by 2+ objects)
        shared = [
            {"dependency": key, "used_by": users}
            for key, users in shared_dependencies.items()
            if len(users) > 1
        ]

        # Build dependency matrix
        matrix_data = []
        for obj in object_list:
            row = {
                "object": f"{obj['type']}:{obj['id']}",
                "uses_count": len(
                    [
                        a
                        for a in results
                        if a["object"]["type"] == obj["type"]
                        and a["object"]["id"] == obj["id"]
                    ][0]["uses"]
                ),
                "used_by_count": len(
                    [
                        a
                        for a in results
                        if a["object"]["type"] == obj["type"]
                        and a["object"]["id"] == obj["id"]
                    ][0]["used_by"]
                ),
            }
            matrix_data.append(row)

        return {
            "objects": results,
            "shared_dependencies": shared,
            "dependency_matrix": (
                pd.DataFrame(matrix_data) if matrix_data else pd.DataFrame()
            ),
            "total_dependencies": len(all_dependencies),
        }

    def get_usage_count(self, obj_type: str, obj_id: str) -> int:
        """Get number of times object is referenced"""
        used_by = self._find_objects_using(obj_type, obj_id)
        return len(used_by)

    def get_dependent_objects(self, obj_type: str, obj_id: str) -> List[Dict[str, Any]]:
        """Get list of objects that depend on this object"""
        return self._find_objects_using(obj_type, obj_id)

    def build_dependency_tree(
        self, obj_type: str, obj_id: str, max_depth: int = 3
    ) -> Dict[str, Any]:
        """Build hierarchical dependency tree"""
        obj_data = self.data_provider.get_object_by_id(obj_type, obj_id)
        if not obj_data:
            return {"error": "Object not found"}

        def build_tree_recursive(
            current_type: str, current_id: str, depth: int, visited: Set[str]
        ) -> Dict[str, Any]:
            """Recursively build tree, avoiding circular dependencies"""
            node_key = f"{current_type}:{current_id}"

            # Prevent circular dependencies
            if node_key in visited or depth >= max_depth:
                return None

            visited.add(node_key)

            # Get object data
            current_obj = self.data_provider.get_object_by_id(current_type, current_id)
            if not current_obj:
                return None

            # Find what this object uses
            uses = self._find_objects_used_by(current_type, current_id, current_obj)

            # Build children nodes
            children = []
            for used_obj in uses:
                child_tree = build_tree_recursive(
                    used_obj["type"],
                    used_obj["id"],
                    depth + 1,
                    visited.copy(),  # Pass copy to allow siblings to visit same nodes
                )
                if child_tree:
                    children.append(child_tree)

            return {
                "type": current_type,
                "id": current_id,
                "name": current_obj.get("Name", "Unknown"),
                "depth": depth,
                "children": children,
            }

        tree = build_tree_recursive(obj_type, obj_id, 0, set())

        return {
            "root": {
                "type": obj_type,
                "id": obj_id,
                "name": obj_data.get("Name", "Unknown"),
            },
            "tree": tree,
            "max_depth": max_depth,
        }

    def _find_objects_used_by(
        self, obj_type: str, obj_id: str, obj_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find objects that this object uses (outbound relationships)"""
        uses = []

        relationship_config = self.config.get("relationship_types", {}).get(
            obj_type, {}
        )
        can_use = relationship_config.get("can_use", [])

        if not can_use:
            return uses

        # Load JSON file for detailed relationship data
        json_data = self._load_json_file(obj_type, obj_data)
        if not json_data:
            return uses

        # For policies: look for scope (groups), scripts, packages
        if obj_type == "policies":
            # Get computer groups from scope
            scope = json_data.get("scope", {})
            computer_groups = scope.get("computer_groups", [])
            for group in computer_groups:
                uses.append(
                    {
                        "type": "groups",
                        "id": str(group.get("id", "")),
                        "name": group.get("name", "Unknown"),
                    }
                )

            # Get scripts
            scripts_list = json_data.get("scripts", [])
            for script in scripts_list:
                if isinstance(script, dict):
                    uses.append(
                        {
                            "type": "scripts",
                            "id": str(script.get("id", "")),
                            "name": script.get("name", "Unknown"),
                        }
                    )

            # Get packages
            package_config = json_data.get("package_configuration", {})
            packages = package_config.get("packages", [])
            for package in packages:
                if isinstance(package, dict):
                    uses.append(
                        {
                            "type": "packages",
                            "id": str(package.get("id", "")),
                            "name": package.get("name", "Unknown"),
                        }
                    )

        # For profiles: look for scope (groups)
        elif obj_type == "profiles":
            scope = json_data.get("scope", {})
            computer_groups = scope.get("computer_groups", [])
            for group in computer_groups:
                uses.append(
                    {
                        "type": "groups",
                        "id": str(group.get("id", "")),
                        "name": group.get("name", "Unknown"),
                    }
                )

        return uses

    def _find_objects_using(self, obj_type: str, obj_id: str) -> List[Dict[str, Any]]:
        """Find objects that use this object (inbound relationships)"""
        used_by = []

        relationship_config = self.config.get("relationship_types", {}).get(
            obj_type, {}
        )
        can_be_used_by = relationship_config.get("can_be_used_by", [])

        if not can_be_used_by:
            return used_by

        # For each type that can use this object, scan all objects of that type
        for using_type in can_be_used_by:
            try:
                # Load all objects of the using type
                using_objects_df = self.data_provider.load_objects(
                    using_type, "sandbox"
                )  # Default to sandbox

                # Scan each object to see if it references this object
                for _, using_obj in using_objects_df.iterrows():
                    using_obj_dict = using_obj.to_dict()
                    using_obj_id = str(using_obj_dict.get("ID", ""))

                    # Check if this object uses our target object
                    uses = self._find_objects_used_by(
                        using_type, using_obj_id, using_obj_dict
                    )
                    for used in uses:
                        if used["type"] == obj_type and str(used["id"]) == str(obj_id):
                            used_by.append(
                                {
                                    "type": using_type,
                                    "id": using_obj_id,
                                    "name": using_obj_dict.get("Name", "Unknown"),
                                }
                            )
                            break  # Found reference, move to next object

            except Exception as e:
                print(
                    f"Error scanning {using_type} for references to {obj_type}:{obj_id}: {e}"
                )

        return used_by

    def _load_json_file(
        self, obj_type: str, obj_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Load JSON file for detailed object data"""
        import json
        import os

        # Check if there's a reference to a JSON file
        json_path = None

        # Different object types store the path differently
        if "policy_file" in obj_data:
            json_path = obj_data["policy_file"]
        elif "profile_file" in obj_data:
            json_path = obj_data["profile_file"]
        elif "script_file" in obj_data:
            json_path = obj_data["script_file"]
        elif "package_file" in obj_data:
            json_path = obj_data["package_file"]
        elif "group_file" in obj_data:
            json_path = obj_data["group_file"]

        if not json_path or pd.isna(json_path):
            return None

        # Use the path as-is since CSVs already have the correct path
        json_path_str = str(json_path)

        # Try to load the JSON file
        # The path in CSV might be relative to project root
        # Get project root dynamically (4 levels up from this file)
        project_root = str(Path(__file__).parent.parent.parent.parent)
        base_paths = [
            "",  # Relative to current directory
            project_root + "/",  # Dynamic project root path
        ]

        for base_path in base_paths:
            full_path = os.path.join(base_path, json_path_str)
            try:
                with open(full_path, "r") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue

        return None

    def _parse_scope_groups(self, scope_str: str) -> List[Dict[str, str]]:
        """Parse group references from scope string (legacy/fallback)"""
        # Simplified parser - in production this would handle actual JAMF scope format
        groups = []

        if not scope_str or pd.isna(scope_str):
            return groups

        # Example formats to handle:
        # "Group: All Macs (123)"
        # "Groups: Group1 (1), Group2 (2)"

        import re

        # Look for pattern: GroupName (ID)
        matches = re.findall(r"([^(]+)\((\d+)\)", str(scope_str))
        for name, group_id in matches:
            groups.append({"id": group_id.strip(), "name": name.strip()})

        return groups

    def _parse_scripts(self, scripts_str: str) -> List[Dict[str, str]]:
        """Parse script references"""
        scripts = []

        if not scripts_str or pd.isna(scripts_str):
            return scripts

        import re

        matches = re.findall(r"([^(]+)\((\d+)\)", str(scripts_str))
        for name, script_id in matches:
            scripts.append({"id": script_id.strip(), "name": name.strip()})

        return scripts

    def _parse_packages(self, packages_str: str) -> List[Dict[str, str]]:
        """Parse package references"""
        packages = []

        if not packages_str or pd.isna(packages_str):
            return packages

        import re

        matches = re.findall(r"([^(]+)\((\d+)\)", str(packages_str))
        for name, package_id in matches:
            packages.append({"id": package_id.strip(), "name": name.strip()})

        return packages

    def clear_cache(self):
        """Clear relationship cache"""
        self._relationship_cache.clear()
        self._object_cache.clear()
