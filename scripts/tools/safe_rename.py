#!/usr/bin/env python3
"""
Safely rename files in jpapi
Updates all imports and references
"""

import os
import sys
from pathlib import Path
import ast
import json
from typing import Dict, Set, List
import shutil


class SafeRenamer:
    """Safely rename files and update all references"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def rename_file(self, old_path: str, new_path: str, dry_run: bool = True):
        """
        Rename a file and update all references

        Args:
            old_path: Current file path
            new_path: New file path
            dry_run: If True, just show what would change
        """
        old_file = Path(old_path)
        new_file = Path(new_path)

        print(f"\n🔄 {'Simulating' if dry_run else 'Performing'} rename:")
        print(f"  From: {old_file}")
        print(f"  To:   {new_file}")

        # Get all Python files
        py_files = list(self.root_dir.rglob("*.py"))

        # Track what needs updating
        files_to_update = []
        import_changes = []

        # Check each file for references
        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file) as f:
                    content = f.read()

                # Look for imports to update
                tree = ast.parse(content)
                imports_updated = False

                for node in ast.walk(tree):
                    # Check imports
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            old_name = self._path_to_module(old_file)
                            if name.name == old_name:
                                new_name = self._path_to_module(new_file)
                                import_changes.append(
                                    {
                                        "file": str(py_file),
                                        "old": name.name,
                                        "new": new_name,
                                    }
                                )
                                imports_updated = True

                    # Check from imports
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            old_name = self._path_to_module(old_file)
                            if node.module == old_name:
                                new_name = self._path_to_module(new_file)
                                import_changes.append(
                                    {
                                        "file": str(py_file),
                                        "old": node.module,
                                        "new": new_name,
                                    }
                                )
                                imports_updated = True

                if imports_updated:
                    files_to_update.append(str(py_file))

            except Exception as e:
                print(f"Error checking {py_file}: {e}")

        # Show what would change
        print("\nFiles to update:")
        for file in files_to_update:
            print(f"  - {file}")

        print("\nImport changes:")
        for change in import_changes:
            print(f"  - {change['file']}: {change['old']} → {change['new']}")

        # Make changes if not dry run
        if not dry_run:
            # Create new file's directory if needed
            new_file.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(str(old_file), str(new_file))
            print(f"\n✅ Moved file: {old_file} → {new_file}")

            # Update imports
            for file in files_to_update:
                try:
                    self._update_file_imports(
                        file, [(c["old"], c["new"]) for c in import_changes]
                    )
                    print(f"✅ Updated imports in: {file}")
                except Exception as e:
                    print(f"❌ Error updating {file}: {e}")

            print("\n✅ Rename complete!")
        else:
            print("\n✅ Dry run complete! Use --execute to perform the rename.")

    def _path_to_module(self, path: Path) -> str:
        """Convert file path to module path"""
        rel_path = path.relative_to(self.root_dir)
        return str(rel_path.with_suffix("")).replace("/", ".")

    def _update_file_imports(self, file_path: str, changes: List[tuple]):
        """Update imports in a file"""
        with open(file_path) as f:
            content = f.read()

        # Make replacements
        for old, new in changes:
            # Update standard imports
            content = content.replace(f"import {old}", f"import {new}")
            content = content.replace(f"from {old} import", f"from {new} import")

            # Update as imports
            content = content.replace(f"import {old} as", f"import {new} as")

        # Write changes
        with open(file_path, "w") as f:
            f.write(content)


def main():
    """Rename files safely"""
    if len(sys.argv) < 3:
        print("Usage: safe_rename.py <old_path> <new_path> [--execute]")
        print(
            "Example: safe_rename.py lib/comprehensive_relationships.py lib/jamf_connections.py"
        )
        return

    old_path = sys.argv[1]
    new_path = sys.argv[2]
    execute = "--execute" in sys.argv

    root = Path(__file__).parent.parent.parent
    renamer = SafeRenamer(root)
    renamer.rename_file(old_path, new_path, dry_run=not execute)


if __name__ == "__main__":
    main()
