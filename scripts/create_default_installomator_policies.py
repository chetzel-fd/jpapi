#!/usr/bin/env python3
"""
Create Default Installomator Policies
Creates standard Install and Latest Version policies for any app
"""

import sys
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


def create_default_policies(
    app_name, label, category="Productivity", scope_groups=None
):
    """Create default Install and Latest Version policies for an app"""
    if scope_groups is None:
        scope_groups = ["All Computers"]

    factory = InstallomatorFactory()
    service = factory.create_installomator_service()

    # Create Install policy
    install_config = PolicyConfig(
        app_name=app_name,
        label=label,
        policy_name=f"Install {app_name}",
        policy_type=PolicyType.INSTALL,
        trigger=TriggerType.EVENT,
        category=category,
        description=f"Install {app_name} using Installomator",
        scope_groups=scope_groups,
        frequency="Ongoing",
        retry_attempts=3,
        notify_on_failure=True,
    )

    # Create Latest Version policy
    latest_config = PolicyConfig(
        app_name=app_name,
        label=label,
        policy_name=f"{app_name} Install Latest Version",
        policy_type=PolicyType.LATEST_VERSION,
        trigger=TriggerType.EVENT,
        category=category,
        description=f"Install latest version of {app_name} using Installomator",
        scope_groups=scope_groups,
        frequency="Ongoing",
        retry_attempts=3,
        notify_on_failure=True,
    )

    print(f"🎯 Creating Default Policies for {app_name}")
    print("=" * 60)

    # Create install policy
    print(f"\n📋 Creating Install Policy...")
    install_result = service.create_policy(install_config)
    if install_result.success:
        print(f"✅ Install policy created: {install_result.policy_name}")
        print(f"   ID: {install_result.policy_id}")
    else:
        print(f"❌ Failed to create install policy: {install_result.error_message}")

    # Create latest version policy
    print(f"\n📋 Creating Latest Version Policy...")
    latest_result = service.create_policy(latest_config)
    if latest_result.success:
        print(f"✅ Latest version policy created: {latest_result.policy_name}")
        print(f"   ID: {latest_result.policy_id}")
    else:
        print(
            f"❌ Failed to create latest version policy: {latest_result.error_message}"
        )

    # Show policy configurations
    print(f"\n📄 Policy Configurations:")
    print(f"\nInstall Policy:")
    install_jamf = install_config.to_jamf_policy()
    print(f"   Name: {install_jamf['general']['name']}")
    print(f"   Trigger: {install_jamf['general']['trigger']}")
    print(f"   Script: {install_jamf['scripts'][0]['parameter4']}")

    print(f"\nLatest Version Policy:")
    latest_jamf = latest_config.to_jamf_policy()
    print(f"   Name: {latest_jamf['general']['name']}")
    print(f"   Trigger: {latest_jamf['general']['trigger']}")
    print(f"   Script: {latest_jamf['scripts'][0]['parameter4']}")

    return install_result.success and latest_result.success


def main():
    parser = argparse.ArgumentParser(
        description="Create default Installomator policies"
    )
    parser.add_argument("app_name", help="Name of the app")
    parser.add_argument("label", help="Installomator label")
    parser.add_argument(
        "--category", default="Productivity", help="Category for policies"
    )
    parser.add_argument(
        "--scope-groups",
        nargs="+",
        default=["All Computers"],
        help="Computer groups to scope policies to",
    )

    args = parser.parse_args()

    success = create_default_policies(
        args.app_name, args.label, args.category, args.scope_groups
    )

    if success:
        print(f"\n🎉 Successfully created default policies for {args.app_name}!")
        return 0
    else:
        print(f"\n❌ Some policies failed to create")
        return 1


if __name__ == "__main__":
    sys.exit(main())
