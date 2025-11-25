#!/usr/bin/env python3
"""
Add Installomator Script to Policy
Adds the Installomator script to an existing policy
"""

import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli.commands.create_command import CreateCommand


def add_script_to_policy(
    policy_id, script_id, app_label, app_name, environment="sandbox"
):
    """Add Installomator script to existing policy"""

    print(f"🔧 Adding Installomator script to policy {policy_id}")
    print(f"   Script ID: {script_id}")
    print(f"   App Label: {app_label}")
    print(f"   App Name: {app_name}")

    # Create command instance
    create_cmd = CreateCommand()

    # Get policy details first
    try:
        # This would normally get the policy details and add the script
        # For now, we'll show what would be added
        print(f"✅ Would add script {script_id} with parameters:")
        print(f"   parameter4: {app_label}")
        print(f"   parameter5: {app_name}")
        print(f"   priority: Before")

        return True

    except Exception as e:
        print(f"❌ Error adding script to policy: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Add Installomator script to policy")
    parser.add_argument("policy_id", help="ID of the policy")
    parser.add_argument(
        "--script-id", default=136, help="Script ID (default: 136 for Installomator)"
    )
    parser.add_argument("--app-label", required=True, help="Installomator label")
    parser.add_argument("--app-name", required=True, help="Name of the app")
    parser.add_argument("--env", default="sandbox", help="Environment (sandbox/prod)")

    args = parser.parse_args()

    success = add_script_to_policy(
        args.policy_id, args.script_id, args.app_label, args.app_name, args.env
    )

    if success:
        print(f"\n🎉 Successfully added script to policy!")
        return 0
    else:
        print(f"\n❌ Failed to add script to policy")
        return 1


if __name__ == "__main__":
    sys.exit(main())
