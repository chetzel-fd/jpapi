#!/usr/bin/env python3
"""
Fix Internal Imports Script
Remove 'src.' prefix from imports within src/ directory
With pure src/ layout (package_dir={"": "src"}), imports should be relative to src/
"""

import os
import re
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"

# Import patterns to fix (remove src. prefix)
PATTERNS = [
    # from src.core → from core (with or without trailing dot)
    (r"\bfrom src\.core\b", "from core"),
    # from src.lib → from lib
    (r"\bfrom src\.lib\b", "from lib"),
    # from src.resources → from resources
    (r"\bfrom src\.resources\b", "from resources"),
    # from src.cli → from cli
    (r"\bfrom src\.cli\b", "from cli"),
    # from src.apps → from apps
    (r"\bfrom src\.apps\b", "from apps"),
    # from src.interfaces → from interfaces
    (r"\bfrom src\.interfaces\b", "from interfaces"),
    # from src.services → from services
    (r"\bfrom src\.services\b", "from services"),
    # from src.controllers → from controllers
    (r"\bfrom src\.controllers\b", "from controllers"),
    # from src.dashboard → from dashboard
    (r"\bfrom src\.dashboard\b", "from dashboard"),
    # from src.tools → from tools
    (r"\bfrom src\.tools\b", "from tools"),
    # from src.addons → from addons
    (r"\bfrom src\.addons\b", "from addons"),
    # import src.core → import core
    (r"\bimport src\.core\b", "import core"),
    # import src.lib → import lib
    (r"\bimport src\.lib\b", "import lib"),
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
            matches = re.findall(pattern, content)
            if matches:
                changes += len(matches)
            content = re.sub(pattern, replacement, content)

        # Only write if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return changes

        return 0

    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return 0


def main():
    print("🔄 Fixing Internal Imports (removing src. prefix)")
    print("=" * 60)
    print()

    files_updated = 0
    total_changes = 0

    # Find all Python files in src/ recursively
    print(f"📁 Processing all files in {SRC_DIR.relative_to(PROJECT_ROOT)}...")
    for py_file in SRC_DIR.rglob("*.py"):
        changes = update_file(py_file)
        if changes > 0:
            files_updated += 1
            total_changes += changes
            print(
                f"  ✅ Updated {py_file.relative_to(PROJECT_ROOT)} ({changes} changes)"
            )

    print()
    print("=" * 60)
    print(f"✨ Import fix complete!")
    print(f"   Total files updated: {files_updated}")
    print(f"   Total changes made: {total_changes}")
    print()


if __name__ == "__main__":
    main()
