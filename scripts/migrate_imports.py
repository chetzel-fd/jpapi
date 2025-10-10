#!/usr/bin/env python3
"""
Import Migration Script
Converts old import paths to new src. prefixed paths
"""

import os
import re
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Directories to update
DIRECTORIES_TO_UPDATE = [
    PROJECT_ROOT / "src" / "cli" / "commands",
    PROJECT_ROOT / "src" / "cli" / "base",
    PROJECT_ROOT / "src" / "cli" / "handlers",
    PROJECT_ROOT / "src" / "apps",
    PROJECT_ROOT / "src" / "interfaces",
    PROJECT_ROOT / "src" / "lib",
    PROJECT_ROOT / "src" / "core",  # Moved from root
    PROJECT_ROOT / "src" / "resources",  # Moved from root
    PROJECT_ROOT / "src" / "services",
    PROJECT_ROOT / "src" / "controllers",
    PROJECT_ROOT / "src" / "dashboard",
    PROJECT_ROOT / "src" / "tools",
    PROJECT_ROOT / "src" / "addons",
    PROJECT_ROOT / "tests",
]

# Import patterns to replace
PATTERNS = [
    # Pattern 1: from core. → from src.core.
    (r"\bfrom core\.", "from src.core."),
    # Pattern 2: from lib. → from src.lib.
    (r"\bfrom lib\.", "from src.lib."),
    # Pattern 3: from resources. → from src.resources.
    (r"\bfrom resources\.", "from src.resources."),
    # Pattern 4: import core. → import src.core.
    (r"\bimport core\.", "import src.core."),
    # Pattern 5: import lib. → import src.lib.
    (r"\bimport lib\.", "import src.lib."),
    # Pattern 6: import resources. → import src.resources.
    (r"\bimport resources\.", "import src.resources."),
]


def update_file(file_path: Path) -> int:
    """Update imports in a single file. Returns number of changes made."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes = 0

        # Apply all patterns
        for pattern, replacement in PATTERNS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes += content.count(pattern.replace(r"\b", ""))
                content = new_content

        # Only write if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return changes

        return 0

    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return 0


def migrate_directory(directory: Path) -> tuple:
    """Migrate all Python files in directory. Returns (files_updated, total_changes)"""
    if not directory.exists():
        print(f"  ⚠️  Directory not found: {directory}")
        return (0, 0)

    files_updated = 0
    total_changes = 0

    # Find all Python files recursively
    for py_file in directory.rglob("*.py"):
        changes = update_file(py_file)
        if changes > 0:
            files_updated += 1
            total_changes += changes
            print(
                f"  ✅ Updated {py_file.relative_to(PROJECT_ROOT)} ({changes} changes)"
            )

    return (files_updated, total_changes)


def main():
    print("🔄 JPAPI Import Migration")
    print("=" * 50)
    print()

    grand_total_files = 0
    grand_total_changes = 0

    for directory in DIRECTORIES_TO_UPDATE:
        if directory.exists():
            print(f"📁 Processing {directory.relative_to(PROJECT_ROOT)}...")
            files, changes = migrate_directory(directory)
            grand_total_files += files
            grand_total_changes += changes
            print(f"   → {files} files updated, {changes} changes")
            print()

    print("=" * 50)
    print(f"✨ Migration complete!")
    print(f"   Total files updated: {grand_total_files}")
    print(f"   Total changes made: {grand_total_changes}")
    print()


if __name__ == "__main__":
    main()
