#!/usr/bin/env python3
"""
Easy Installomator App Addition Script
Makes it simple to add any app to Installomator and create policies
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
from addons.installomator.installomator_service import AppInfo
from addons.installomator.profile_generator import InstallomatorProfileGenerator


def add_app_to_service(app_name, label, description="", category="Productivity"):
    """Add an app to the Installomator service"""
    factory = InstallomatorFactory()
    service = factory.create_installomator_service()

    # Check if app already exists
    existing_apps = service.search_apps(app_name.lower())
    for app in existing_apps:
        if app.label == label:
            print(f"⚠️  App with label '{label}' already exists!")
            return False, service

    # Add the new app
    new_app = AppInfo(
        app_name=app_name,
        label=label,
        description=description or f"{app_name} application",
        category=category,
    )

    service.apps_cache.append(new_app)
    print(f"✅ App '{app_name}' added successfully!")
    return True, service


def create_policy_for_app(
    service,
    app_name,
    label,
    policy_name=None,
    policy_type="install",
    scope_groups=None,
    category="Productivity",
    output_file=None,
):
    """Create a policy for an app"""

    # Find the app
    apps = service.list_all_apps()
    target_app = None
    for app in apps:
        if app.label == label:
            target_app = app
            break

    if not target_app:
        print(f"❌ App with label '{label}' not found!")
        print("Available apps:")
        for app in apps:
            print(f"   • {app.app_name} ({app.label})")
        return False

    # Create policy configuration
    policy_type_map = {
        "install": PolicyType.INSTALL,
        "daily_update": PolicyType.DAILY_UPDATE,
        "latest_version": PolicyType.LATEST_VERSION,
    }

    config = PolicyConfig(
        app_name=target_app.app_name,
        label=target_app.label,
        policy_name=policy_name or f"Install {target_app.app_name}",
        policy_type=policy_type_map[policy_type],
        trigger=TriggerType.EVENT,
        category=category,
        description=f"Installomator policy for {target_app.app_name}",
        scope_groups=scope_groups or ["All Computers"],
        frequency="Ongoing",
        retry_attempts=3,
        notify_on_failure=True,
    )

    # Generate JAMF policy JSON
    jamf_policy = config.to_jamf_policy()

    if output_file:
        with open(output_file, "w") as f:
            json.dump(jamf_policy, f, indent=2)
        print(f"✅ Policy JSON saved to: {output_file}")
    else:
        print(f"✅ Policy created for {target_app.app_name}")
        print(f"📄 JAMF Policy JSON:")
        print(json.dumps(jamf_policy, indent=2))

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Add Installomator app and create policy"
    )
    parser.add_argument(
        "app_name", help="Name of the app (e.g., 'Adobe Creative Cloud Desktop')"
    )
    parser.add_argument(
        "label", help="Installomator label (e.g., 'adobecreativeclouddesktop')"
    )
    parser.add_argument("--description", help="Description of the app", default="")
    parser.add_argument(
        "--category", help="Category for the app", default="Productivity"
    )
    parser.add_argument("--policy-name", help="Name for the policy")
    parser.add_argument(
        "--policy-type",
        choices=["install", "daily_update", "latest_version"],
        default="install",
        help="Type of policy to create",
    )
    parser.add_argument(
        "--scope-groups",
        nargs="+",
        default=["All Computers"],
        help="Computer groups to scope the policy to",
    )
    parser.add_argument("--output-file", help="Save policy JSON to file")
    parser.add_argument(
        "--generate-profiles",
        action="store_true",
        help="Generate configuration profiles (PPPC, preferences) for the app",
    )
    parser.add_argument(
        "--profile-output-dir", help="Output directory for generated profiles"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )

    args = parser.parse_args()

    print(f"🎯 Adding Installomator App: {args.app_name}")
    print("=" * 60)

    if args.dry_run:
        print("🧪 DRY RUN - No changes will be made")
        print(f"Would add app: {args.app_name} ({args.label})")
        print(f"Would create policy: {args.policy_name or f'Install {args.app_name}'}")
        return 0

    # Add the app
    success, service = add_app_to_service(
        args.app_name, args.label, args.description, args.category
    )
    if not success:
        return 1

    # Create the policy
    if not create_policy_for_app(
        service,
        args.app_name,
        args.label,
        args.policy_name,
        args.policy_type,
        args.scope_groups,
        args.category,
        args.output_file,
    ):
        return 1

    # Generate profiles if requested
    if args.generate_profiles:
        print(f"\n🔧 Generating configuration profiles...")
        profile_generator = InstallomatorProfileGenerator()

        try:
            results = profile_generator.generate_profiles_for_app(
                args.label, args.profile_output_dir
            )

            print(f"✅ Generated {len(results['generated_profiles'])} profiles:")
            for profile in results["generated_profiles"]:
                print(f"   • {profile['type']}: {profile['name']}")
                print(f"     File: {profile['file']}")

            print(f"📂 Profile output: {results['output_directory']}")
        except Exception as e:
            print(f"⚠️  Error generating profiles: {e}")

    print(f"\n🎉 Successfully set up {args.app_name} for Installomator!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
