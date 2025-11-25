#!/usr/bin/env python3
"""
Create Complete Installomator Setup
Creates policy with script and uploads configuration profiles
"""

import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from addons.installomator import (
    InstallomatorFactory,
    PolicyConfig,
    PolicyType,
    TriggerType,
)
from addons.installomator.profile_generator import InstallomatorProfileGenerator


def create_complete_setup(app_name, label, environment="sandbox"):
    """Create complete Installomator setup with policy and profiles"""

    print(f"🎯 Creating Complete Installomator Setup for {app_name}")
    print("=" * 60)

    # Initialize services
    factory = InstallomatorFactory()
    service = factory.create_installomator_service()
    profile_generator = InstallomatorProfileGenerator()

    # Check if app exists
    apps = service.search_apps(label)
    target_app = None
    for app in apps:
        if app.label == label:
            target_app = app
            break

    if not target_app:
        print(f"❌ App with label '{label}' not found!")
        return False

    print(f"✅ Found app: {target_app.app_name}")

    # Create policy configuration
    policy_config = PolicyConfig(
        app_name=target_app.app_name,
        label=target_app.label,
        policy_name=f"{app_name} Install Latest Version",
        policy_type=PolicyType.LATEST_VERSION,
        trigger=TriggerType.EVENT,
        category="Productivity",
        description=f"Installomator policy for {target_app.app_name}",
        scope_groups=["All Computers"],
        frequency="Ongoing",
        retry_attempts=3,
        notify_on_failure=True,
    )

    # Generate JAMF policy JSON
    jamf_policy = policy_config.to_jamf_policy()

    print(f"\n📋 Policy Configuration:")
    print(f"   Name: {jamf_policy['general']['name']}")
    print(f"   Trigger: {jamf_policy['general']['trigger']}")
    print(f"   Script ID: {jamf_policy['scripts'][0]['id']}")
    print(f"   App Label: {jamf_policy['scripts'][0]['parameter4']}")
    print(f"   App Name: {jamf_policy['scripts'][0]['parameter5']}")

    # Generate profiles
    print(f"\n🔧 Generating Configuration Profiles...")
    try:
        profile_results = profile_generator.generate_profiles_for_app(label)

        print(f"✅ Generated {len(profile_results['generated_profiles'])} profiles:")
        for profile in profile_results["generated_profiles"]:
            print(f"   • {profile['type']}: {profile['name']}")
            print(f"     File: {profile['file']}")

        print(f"\n📂 Profile output: {profile_results['output_directory']}")

    except Exception as e:
        print(f"⚠️  Error generating profiles: {e}")
        return False

    # Save policy JSON
    policy_file = f"{label}_policy.json"
    with open(policy_file, "w") as f:
        json.dump(jamf_policy, f, indent=2)

    print(f"\n💾 Policy JSON saved to: {policy_file}")

    print(f"\n🎉 Complete setup created successfully!")
    print(f"\n📋 Next Steps:")
    print(f"   1. Import policy JSON into JAMF Pro: {policy_file}")
    print(f"   2. Upload .mobileconfig files to JAMF Pro:")
    for profile in profile_results["generated_profiles"]:
        print(f"      • {profile['file']}")
    print(f"   3. Deploy to target computers")

    return True


def main():
    parser = argparse.ArgumentParser(description="Create complete Installomator setup")
    parser.add_argument("app_name", help="Name of the app")
    parser.add_argument("label", help="Installomator label")
    parser.add_argument("--env", default="sandbox", help="Environment (sandbox/prod)")

    args = parser.parse_args()

    success = create_complete_setup(args.app_name, args.label, args.env)

    if success:
        print(f"\n🎉 Successfully created complete setup for {args.app_name}!")
        return 0
    else:
        print(f"\n❌ Failed to create setup for {args.app_name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
