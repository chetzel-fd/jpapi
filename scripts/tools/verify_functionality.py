#!/usr/bin/env python3
"""
Verify jpapi functionality after renames
Runs key commands to ensure everything still works
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict
import json


class FunctionalityVerifier:
    """Verify jpapi functionality"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.results: Dict[str, List[Dict]] = {"passed": [], "failed": []}

    def verify_all(self):
        """Run all verifications"""
        print("🔍 Verifying jpapi functionality...")

        # Test imports
        self._verify_imports()

        # Test key commands
        self._verify_commands(
            [
                # Export commands
                "jpapi export policies",
                "jpapi export scripts",
                "jpapi export profiles",
                # List commands
                "jpapi list policies",
                "jpapi list scripts",
                "jpapi list devices",
                # Search commands
                "jpapi search policies",
                "jpapi search scripts",
                # Other commands
                "jpapi info",
                "jpapi tools",
            ]
        )

        # Show results
        self._show_results()

    def _verify_imports(self):
        """Verify all imports work"""
        print("\n📦 Verifying imports...")

        test_code = """
import sys
sys.path.insert(0, '.')
        
# Core imports
from core.auth import jamf_login
from core.safety import safety_checks

# Helper imports
from lib import jamf_connections
from lib import file_cache
from lib import search_filters

# CLI imports
from src.cli.commands.export import export_policies
from src.cli.commands.export import export_scripts
"""

        try:
            exec(test_code)
            self.results["passed"].append(
                {"test": "imports", "message": "All imports successful"}
            )
        except Exception as e:
            self.results["failed"].append(
                {"test": "imports", "message": f"Import error: {e}"}
            )

    def _verify_commands(self, commands: List[str]):
        """Verify CLI commands work"""
        print("\n🔧 Verifying commands...")

        for cmd in commands:
            print(f"\nTesting: {cmd}")
            try:
                # Run command
                result = subprocess.run(
                    cmd.split(), capture_output=True, text=True, cwd=self.root_dir
                )

                if result.returncode == 0:
                    self.results["passed"].append(
                        {"test": cmd, "message": "Command succeeded"}
                    )
                else:
                    self.results["failed"].append(
                        {"test": cmd, "message": f"Command failed: {result.stderr}"}
                    )
            except Exception as e:
                self.results["failed"].append(
                    {"test": cmd, "message": f"Error running command: {e}"}
                )

    def _show_results(self):
        """Show test results"""
        print("\n📊 Test Results:")
        print(f"Passed: {len(self.results['passed'])}")
        print(f"Failed: {len(self.results['failed'])}")

        if self.results["failed"]:
            print("\n❌ Failed Tests:")
            for test in self.results["failed"]:
                print(f"\n{test['test']}:")
                print(f"  {test['message']}")
        else:
            print("\n✅ All tests passed!")

        # Save results
        with open("verify_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: verify_results.json")


def main():
    """Run verification"""
    root = Path(__file__).parent.parent.parent
    verifier = FunctionalityVerifier(root)
    verifier.verify_all()


if __name__ == "__main__":
    main()
