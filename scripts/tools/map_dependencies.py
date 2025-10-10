#!/usr/bin/env python3
"""
Maps all file dependencies in jpapi
Shows what imports what so we can safely rename files
"""

import os
import sys
from pathlib import Path
from typing import Dict, Set, List
import ast
import json


class DependencyMapper:
    """Maps file dependencies"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.dependencies: Dict[str, Set[str]] = {}
        self.reverse_deps: Dict[str, Set[str]] = {}

    def map_dependencies(self):
        """Find all Python files and their imports"""
        print("🔍 Mapping dependencies...")

        # Find all Python files
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            rel_path = py_file.relative_to(self.root_dir)
            self.dependencies[str(rel_path)] = set()

            try:
                # Parse imports
                with open(py_file) as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    # Get imports
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            self.add_dependency(str(rel_path), name.name)

                    # Get from imports
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.add_dependency(str(rel_path), node.module)
            except Exception as e:
                print(f"Error parsing {rel_path}: {e}")

        # Build reverse dependencies
        for file, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.reverse_deps:
                    self.reverse_deps[dep] = set()
                self.reverse_deps[dep].add(file)

    def add_dependency(self, source: str, import_path: str):
        """Add dependency, resolving to actual file path if possible"""
        self.dependencies[source].add(import_path)

        # Try to find actual file
        parts = import_path.split(".")
        for i in range(len(parts)):
            test_path = Path(*parts[: (i + 1)]).with_suffix(".py")
            if (self.root_dir / test_path).exists():
                self.dependencies[source].add(str(test_path))

    def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """Get dependencies for a specific file"""
        rel_path = str(Path(file_path).relative_to(self.root_dir))
        return {
            "imports": sorted(list(self.dependencies.get(rel_path, set()))),
            "imported_by": sorted(
                list(
                    dep
                    for dep, imports in self.dependencies.items()
                    if rel_path in imports
                    or any(imp.endswith(rel_path) for imp in imports)
                )
            ),
        }

    def get_rename_impact(self, old_path: str, new_path: str) -> Dict[str, List[str]]:
        """Get files that would need updating for a rename"""
        old_rel = str(Path(old_path).relative_to(self.root_dir))
        new_rel = str(Path(new_path).relative_to(self.root_dir))

        # Find all files that import the old path
        impacted = set()
        for file, deps in self.dependencies.items():
            if old_rel in deps or any(d.endswith(old_rel) for d in deps):
                impacted.add(file)

        return {
            "files_to_update": sorted(list(impacted)),
            "old_path": old_rel,
            "new_path": new_rel,
        }

    def save_dependency_map(self, output_file: str):
        """Save full dependency map to file"""
        data = {
            "dependencies": {k: sorted(list(v)) for k, v in self.dependencies.items()},
            "reverse_dependencies": {
                k: sorted(list(v)) for k, v in self.reverse_deps.items()
            },
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Dependency map saved to: {output_file}")


def main():
    """Map dependencies and analyze renames"""
    if len(sys.argv) < 2:
        print("Usage: map_dependencies.py <command> [args]")
        print("Commands:")
        print("  map - Create full dependency map")
        print("  check-file <file> - Check specific file dependencies")
        print("  check-rename <old> <new> - Check rename impact")
        return

    # Initialize mapper
    root = Path(__file__).parent.parent.parent
    mapper = DependencyMapper(root)
    mapper.map_dependencies()

    command = sys.argv[1]

    if command == "map":
        # Save full dependency map
        mapper.save_dependency_map("dependency_map.json")

    elif command == "check-file" and len(sys.argv) > 2:
        # Check specific file
        file_path = sys.argv[2]
        deps = mapper.get_file_dependencies(file_path)
        print(f"\n📁 Dependencies for {file_path}:")
        print("\nImports:")
        for imp in deps["imports"]:
            print(f"  - {imp}")
        print("\nImported by:")
        for imp in deps["imported_by"]:
            print(f"  - {imp}")

    elif command == "check-rename" and len(sys.argv) > 3:
        # Check rename impact
        old_path = sys.argv[2]
        new_path = sys.argv[3]
        impact = mapper.get_rename_impact(old_path, new_path)
        print(f"\n🔄 Rename impact {impact['old_path']} → {impact['new_path']}")
        print("\nFiles to update:")
        for file in impact["files_to_update"]:
            print(f"  - {file}")

    else:
        print("Unknown command or missing arguments")


if __name__ == "__main__":
    main()
