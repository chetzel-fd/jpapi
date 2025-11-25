#!/usr/bin/env python3
"""
Create Installomator Policy with Script
Creates a complete policy with Installomator script and proper configuration
"""

import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli.commands.create_command import CreateCommand


def create_installomator_policy(
    policy_name,
    app_label,
    app_name,
    environment="sandbox",
    category="Productivity",
    scope_groups=None,
):
    """Create a complete Installomator policy with script"""

    if scope_groups is None:
        scope_groups = ["All Computers"]

    # Initialize authentication and API client
    auth_manager = AuthenticationManager()
    api_client = JAMFAPIClient(auth_manager, environment=environment)

    # Policy data with Installomator script
    policy_data = {
        "policy": {
            "general": {
                "name": policy_name,
                "enabled": True,
                "trigger": "EVENT",
                "frequency": "Ongoing",
                "retry_attempts": 3,
                "notify_on_each_failed_retry": False,
                "category": {"name": category},
                "description": f"Installomator policy for {app_name}",
            },
            "scope": {
                "all_computers": False,
                "computer_groups": [{"name": group} for group in scope_groups],
                "exclusions": {"computer_groups": []},
            },
            "scripts": [
                {
                    "id": 136,  # Installomator script ID
                    "priority": "Before",
                    "parameter4": app_label,  # Installomator label
                    "parameter5": app_name,  # App name for display
                }
            ],
        }
    }

    print(f"🎯 Creating Installomator Policy: {policy_name}")
    print(f"   App: {app_name}")
    print(f"   Label: {app_label}")
    print(f"   Script ID: 136 (Installomator)")
    print(f"   Environment: {environment}")

    try:
        # Convert to XML for JAMF API
        xml_data = dict_to_xml(policy_data["policy"], "policy")

        # Create policy via API
        response = api_client.api_request(
            "POST", "/JSSResource/policies/id/0", data=xml_data, content_type="xml"
        )

        if response and "policy" in response:
            created_policy = response["policy"]
            print(f"✅ Policy created successfully!")
            print(f"   ID: {created_policy.get('id', 'Unknown')}")
            print(f"   Name: {created_policy.get('name', policy_name)}")
            print(
                f"   Enabled: {created_policy.get('general', {}).get('enabled', 'Unknown')}"
            )
            return True
        else:
            print(f"❌ Failed to create policy")
            return False

    except Exception as e:
        print(f"❌ Error creating policy: {e}")
        return False


def dict_to_xml(data, root_name):
    """Convert dictionary to XML format for JAMF API"""
    xml_parts = [f"<{root_name}>"]

    def dict_to_xml_recursive(obj, parent_key=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            xml_parts.append(f"<{key}>")
                            dict_to_xml_recursive(item)
                            xml_parts.append(f"</{key}>")
                        else:
                            xml_parts.append(f"<{key}>{item}</{key}>")
                elif isinstance(value, dict):
                    xml_parts.append(f"<{key}>")
                    dict_to_xml_recursive(value)
                    xml_parts.append(f"</{key}>")
                else:
                    xml_parts.append(f"<{key}>{value}</{key}>")
        else:
            xml_parts.append(f"<{parent_key}>{obj}</{parent_key}>")

    dict_to_xml_recursive(data)
    xml_parts.append(f"</{root_name}>")

    return "\n".join(xml_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Create Installomator policy with script"
    )
    parser.add_argument("policy_name", help="Name of the policy")
    parser.add_argument("app_label", help="Installomator label")
    parser.add_argument("app_name", help="Name of the app")
    parser.add_argument("--env", default="sandbox", help="Environment (sandbox/prod)")
    parser.add_argument(
        "--category", default="Productivity", help="Category for policy"
    )
    parser.add_argument(
        "--scope-groups",
        nargs="+",
        default=["All Computers"],
        help="Computer groups to scope policy to",
    )

    args = parser.parse_args()

    success = create_installomator_policy(
        args.policy_name,
        args.app_label,
        args.app_name,
        args.env,
        args.category,
        args.scope_groups,
    )

    if success:
        print(f"\n🎉 Successfully created Installomator policy!")
        return 0
    else:
        print(f"\n❌ Failed to create policy")
        return 1


if __name__ == "__main__":
    sys.exit(main())
