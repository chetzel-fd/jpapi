#!/usr/bin/env python3
"""
Upload Policies and Profiles to Production
Uploads the exported policies and profiles to production with null scope
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.auth.login_manager import UnifiedJamfAuth


def dict_to_xml(data, root_name):
    """Convert dictionary to XML string for JAMF API"""

    def dict_to_xml_elem(parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    child = ET.SubElement(parent, key)
                    dict_to_xml_elem(child, value)
                else:
                    child = ET.SubElement(parent, key)
                    if value is not None:
                        child.text = str(value)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    dict_to_xml_elem(parent, item)
                else:
                    child = ET.SubElement(parent, "item")
                    if item is not None:
                        child.text = str(item)

    root = ET.Element(root_name)
    dict_to_xml_elem(root, data)
    ET.indent(root, space="  ", level=0)
    return ET.tostring(root, encoding="unicode")


def set_null_scope(data):
    """Set scope to null (no computers) for policies and profiles"""
    if "scope" in data:
        data["scope"] = {
            "all_computers": False,
            "computers": [],
            "computer_groups": [],
            "buildings": [],
            "departments": [],
            "limit_to_users": {"user_groups": []},
            "limitations": {
                "users": [],
                "user_groups": [],
                "network_segments": [],
                "ibeacons": [],
            },
            "exclusions": {
                "computers": [],
                "computer_groups": [],
                "buildings": [],
                "departments": [],
                "users": [],
                "user_groups": [],
                "network_segments": [],
                "ibeacons": [],
            },
        }
    return data


def clean_dependencies(data):
    """Remove or nullify dependencies that might not exist in production"""
    # Remove category references
    if "general" in data and "category" in data["general"]:
        del data["general"]["category"]

    # Remove site references
    if "general" in data and "site" in data["general"]:
        del data["general"]["site"]

    # Remove package references (they won't exist in production)
    if "package_configuration" in data:
        data["package_configuration"]["packages"] = []

    # Remove script references (they won't exist in production)
    if "scripts" in data:
        data["scripts"] = []

    # Remove printer references
    if "printers" in data:
        data["printers"] = []

    # Remove dock item references
    if "dock_items" in data:
        data["dock_items"] = []

    return data


def clean_policy_data(data):
    """Clean policy data for production upload"""
    # Remove ID
    if "id" in data.get("general", {}):
        del data["general"]["id"]

    # Remove category ID, keep only name
    if "category" in data.get("general", {}):
        if (
            isinstance(data["general"]["category"], dict)
            and "id" in data["general"]["category"]
        ):
            category_name = data["general"]["category"].get("name", "Uncategorized")
            data["general"]["category"] = {"name": category_name}

    # Remove site ID
    if "site" in data.get("general", {}):
        data["general"]["site"] = {"id": -1, "name": "NONE"}

    # Remove package references (they don't exist in prod)
    if "package_configuration" in data:
        data["package_configuration"]["packages"] = []

    # Remove script references (they don't exist in prod)
    if "scripts" in data:
        data["scripts"] = []

    # Set null scope
    data = set_null_scope(data)

    return data


def clean_profile_data(data):
    """Clean profile data for production upload"""
    # Remove ID
    if "id" in data.get("general", {}):
        del data["general"]["id"]

    # Remove site ID
    if "site" in data.get("general", {}):
        data["general"]["site"] = {"id": -1, "name": "NONE"}

    # Set null scope
    data = set_null_scope(data)

    return data


def upload_policies(auth):
    """Upload policies to production"""
    print("📋 Uploading Policies to Production...")
    print("=" * 50)

    policies_dir = Path("storage/exports/policies")
    uploaded_count = 0
    failed_count = 0

    for policy_file in policies_dir.glob("*.json"):
        if "TEST" in policy_file.name:
            continue  # Skip test policies

        print(f"\n📄 Processing: {policy_file.name}")

        try:
            with open(policy_file, "r") as f:
                policy_data = json.load(f)

            # Remove ID to create new policy
            if "id" in policy_data.get("general", {}):
                del policy_data["general"]["id"]

            # Add prefix to make name unique
            original_name = policy_data.get("general", {}).get("name", "Unknown Policy")
            policy_data["general"]["name"] = f"PROD - {original_name}"

            # Clean dependencies and set null scope
            policy_data = clean_dependencies(policy_data)
            policy_data = set_null_scope(policy_data)

            # Convert to XML
            xml_data = dict_to_xml(policy_data, "policy")

            # Upload policy
            response = auth.api_request(
                "POST",
                "/JSSResource/policies/id/0",
                data=xml_data,
                content_type="xml",
            )

            if response and "policy" in response:
                created_policy = response["policy"]
                print(f"✅ Policy created successfully!")
                print(f"   ID: {created_policy.get('id', 'Unknown')}")
                print(f"   Name: {created_policy.get('name', 'Unknown')}")
                uploaded_count += 1
            else:
                print(f"❌ Failed to create policy")
                failed_count += 1

        except Exception as e:
            print(f"❌ Error processing {policy_file.name}: {e}")
            failed_count += 1

    print(f"\n📊 Policy Upload Summary:")
    print(f"   ✅ Successfully uploaded: {uploaded_count}")
    print(f"   ❌ Failed: {failed_count}")

    return uploaded_count, failed_count


def upload_profiles(auth):
    """Upload profiles to production"""
    print("\n📱 Uploading macOS Profiles to Production...")
    print("=" * 50)

    profiles_dir = Path("storage/exports/macos-profiles")
    uploaded_count = 0
    failed_count = 0

    for profile_file in profiles_dir.glob("*.json"):
        print(f"\n📄 Processing: {profile_file.name}")

        try:
            with open(profile_file, "r") as f:
                profile_data = json.load(f)

            # Remove ID to create new profile
            if "id" in profile_data.get("general", {}):
                del profile_data["general"]["id"]

            # Add prefix to make name unique
            original_name = profile_data.get("general", {}).get(
                "name", "Unknown Profile"
            )
            profile_data["general"]["name"] = f"PROD - {original_name}"

            # Clean dependencies and set null scope
            profile_data = clean_dependencies(profile_data)
            profile_data = set_null_scope(profile_data)

            # Convert to XML
            xml_data = dict_to_xml(profile_data, "os_x_configuration_profile")

            # Upload profile
            response = auth.api_request(
                "POST",
                "/JSSResource/osxconfigurationprofiles/id/0",
                data=xml_data,
                content_type="xml",
            )

            if response and "os_x_configuration_profile" in response:
                created_profile = response["os_x_configuration_profile"]
                print(f"✅ Profile created successfully!")
                print(f"   ID: {created_profile.get('id', 'Unknown')}")
                print(f"   Name: {created_profile.get('name', 'Unknown')}")
                uploaded_count += 1
            else:
                print(f"❌ Failed to create profile")
                failed_count += 1

        except Exception as e:
            print(f"❌ Error processing {profile_file.name}: {e}")
            failed_count += 1

    print(f"\n📊 Profile Upload Summary:")
    print(f"   ✅ Successfully uploaded: {uploaded_count}")
    print(f"   ❌ Failed: {failed_count}")

    return uploaded_count, failed_count


def main():
    """Main upload function"""
    print("🚀 Uploading Objects to PRODUCTION Environment...")
    print("=" * 60)
    print("⚠️  WARNING: This will create objects in PRODUCTION!")
    print("🔒 All objects will have NULL SCOPE (no computers)")
    print("=" * 60)

    # Confirm production upload
    response = input("\nType 'yes' to proceed with PRODUCTION upload: ").strip().lower()
    if response not in ["yes", "y"]:
        print("❌ Upload cancelled")
        return 1

    try:
        # Initialize auth for production
        auth = UnifiedJamfAuth("prod")

        # Upload policies
        policy_uploaded, policy_failed = upload_policies(auth)

        # Upload profiles
        profile_uploaded, profile_failed = upload_profiles(auth)

        # Final summary
        print(f"\n🎯 Final Summary:")
        print(f"   📋 Policies uploaded: {policy_uploaded}")
        print(f"   📱 Profiles uploaded: {profile_uploaded}")
        print(f"   ❌ Total failures: {policy_failed + profile_failed}")

        if policy_failed + profile_failed == 0:
            print(f"\n✅ All objects uploaded successfully to PRODUCTION!")
        else:
            print(f"\n⚠️  Some objects failed to upload. Check the logs above.")

        return 0

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
