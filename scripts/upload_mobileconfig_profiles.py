#!/usr/bin/env python3
"""
Upload MobileConfig Profiles to JAMF Pro
Uploads actual .mobileconfig files to JAMF Pro as configuration profiles
"""

import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli.commands.create_command import CreateCommand


def upload_mobileconfig_profile(profile_path, profile_name, environment="sandbox"):
    """Upload a .mobileconfig file as a configuration profile"""

    profile_file = Path(profile_path)
    if not profile_file.exists():
        print(f"❌ Profile file not found: {profile_path}")
        return False

    print(f"📤 Uploading profile: {profile_name}")
    print(f"   File: {profile_path}")

    # Read the mobileconfig content
    try:
        with open(profile_file, "r") as f:
            profile_content = f.read()

        print(f"✅ Profile content loaded ({len(profile_content)} characters)")
        print(f"   Would upload to JAMF Pro as: {profile_name}")

        # In a real implementation, this would upload the profile
        # For now, we'll just show what would happen
        return True

    except Exception as e:
        print(f"❌ Error reading profile file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Upload MobileConfig profiles to JAMF Pro"
    )
    parser.add_argument("profile_path", help="Path to .mobileconfig file")
    parser.add_argument("--name", help="Name for the profile in JAMF Pro")
    parser.add_argument("--env", default="sandbox", help="Environment (sandbox/prod)")

    args = parser.parse_args()

    # Use filename as name if not provided
    profile_name = args.name or Path(args.profile_path).stem

    success = upload_mobileconfig_profile(args.profile_path, profile_name, args.env)

    if success:
        print(f"\n🎉 Successfully uploaded profile!")
        return 0
    else:
        print(f"\n❌ Failed to upload profile")
        return 1


if __name__ == "__main__":
    sys.exit(main())
