#!/usr/bin/env python3
"""
Simple script to safely rename Python files and update imports
Usage: rename_py.py <old_path> <new_path> [--execute]

Example:
    # Check what would change
    python rename_py.py lib/old_name.py lib/new_name.py

    # Actually do the rename
    python rename_py.py lib/old_name.py lib/new_name.py --execute
"""

import os
import sys
from pathlib import Path
import ast
import shutil
from typing import Dict, Set, List
import re


def map_imports(py_file: Path, root: Path) -> Set[str]:
    """Find what this file imports"""
    imports = set()

    try:
        # Parse imports
        with open(py_file) as f:
            content = f.read()

        # Look for import lines directly
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                # Skip comments
                if "#" in line:
                    line = line[: line.index("#")].strip()

                if line.startswith("import "):
                    module = line[7:].strip()
                    if " as " in module:
                        module = module[: module.index(" as ")].strip()
                    imports.add(module)

                elif line.startswith("from "):
                    if " import " in line:
                        module = line[5 : line.index(" import ")].strip()
                        imports.add(module)

                        # Try to find actual file
                        parts = [p for p in module.split(".") if p]  # Skip empty parts
                        if parts:  # Only try if we have parts
                            for i in range(len(parts)):
                                test_path = Path(*parts[: (i + 1)]).with_suffix(".py")
                                if (root / test_path).exists():
                                    imports.add(str(test_path))
    except Exception as e:
        print(f"Error reading {py_file}: {e}")

    return imports


def find_dependent_files(old_path: Path, root: Path) -> List[Path]:
    """Find files that import the file being renamed"""
    old_rel = old_path.relative_to(root)
    old_module = str(old_rel.with_suffix("")).replace("/", ".")

    dependent_files = []

    # Check all Python files
    for py_file in root.rglob("*.py"):
        # Skip venv and other non-project files
        if any(x in str(py_file) for x in ["venv", "__pycache__", ".git"]):
            continue

        try:
            # Read file content
            with open(py_file) as f:
                content = f.read()

            # Look for imports of the old file
            imports_found = False

            # Check for direct imports
            if re.search(rf"from\s+{re.escape(old_module)}\s+import", content):
                imports_found = True
            elif re.search(rf"import\s+{re.escape(old_module)}", content):
                imports_found = True

            # Check for relative imports
            py_file_rel = py_file.relative_to(root)
            rel_path = os.path.relpath(str(old_rel), str(py_file_rel.parent))
            rel_module = str(Path(rel_path).with_suffix("")).replace("/", ".")

            if re.search(rf"from\s+\.+{re.escape(rel_module)}\s+import", content):
                imports_found = True

            if imports_found:
                dependent_files.append(py_file)
        except Exception as e:
            print(f"Error checking {py_file}: {e}")

    return dependent_files


def update_imports(file_path: Path, old_path: Path, new_path: Path, root: Path):
    """Update imports in a file"""
    old_rel = old_path.relative_to(root)
    new_rel = new_path.relative_to(root)

    old_module = str(old_rel.with_suffix("")).replace("/", ".")
    new_module = str(new_rel.with_suffix("")).replace("/", ".")

    try:
        with open(file_path) as f:
            content = f.read()

        # Update imports
        content = content.replace(f"import {old_module}", f"import {new_module}")
        content = content.replace(
            f"from {old_module} import", f"from {new_module} import"
        )
        content = content.replace(f"import {old_module} as", f"import {new_module} as")

        # Write changes
        with open(file_path, "w") as f:
            f.write(content)

        print(f"✅ Updated imports in: {file_path}")
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")


def rename_file(old_path: str, new_path: str, execute: bool = False):
    """Rename a file and update all imports"""
    root = Path.cwd()
    old_file = Path(old_path)
    new_file = Path(new_path)

    print(f"\n🔄 {'Performing' if execute else 'Simulating'} rename:")
    print(f"  From: {old_file}")
    print(f"  To:   {new_file}")

    # Find dependent files
    dependent_files = find_dependent_files(old_file, root)

    print("\nFiles to update:")
    for file in dependent_files:
        print(f"  - {file}")

    if execute:
        # Create new directory if needed
        new_file.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        shutil.move(str(old_file), str(new_file))
        print(f"\n✅ Moved file: {old_file} → {new_file}")

        # Update imports
        for file in dependent_files:
            update_imports(file, old_file, new_file, root)

        print("\n✅ Rename complete!")
    else:
        print("\n✅ Dry run complete! Use --execute to perform the rename.")


def main():
    """Rename files safely"""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    old_path = sys.argv[1]
    new_path = sys.argv[2]
    execute = "--execute" in sys.argv

    rename_file(old_path, new_path, execute)


if __name__ == "__main__":
    main()
