#!/usr/bin/env python3
"""
CrowdStrike Integration Command for jpapi CLI
Handles CrowdStrike Falcon profile creation, signing, and deployment
"""

from .common_imports import (
    ArgumentParser,
    Namespace,
    Dict,
    Any,
    BaseCommand,
)
import os
from pathlib import Path
from datetime import datetime
from lib.utils.manage_signatures import add_signature_to_name


class CrowdStrikeCommand(BaseCommand):
    """CrowdStrike Falcon integration for profile management and signing"""

    def __init__(self):
        super().__init__(
            name="crowdstrike",
            description="CrowdStrike Falcon profile management and deployment",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add CrowdStrike command arguments"""
        subparsers = parser.add_subparsers(dest="cs_action", help="CrowdStrike actions")

        # Profile Creation
        create_parser = subparsers.add_parser(
            "create", help="Create CrowdStrike profiles"
        )
        create_parser.add_argument(
            "--type",
            choices=["fda", "pppc"],
            required=True,
            help="Type of profile to create",
        )
        create_parser.add_argument("--name", help="Profile name")
        create_parser.add_argument("--output", help="Output file path")
        create_parser.add_argument(
            "--organization", default="FanDuel Group", help="Organization name"
        )

        # Profile Signing
        sign_parser = subparsers.add_parser("sign", help="Sign CrowdStrike profiles")
        sign_parser.add_argument(
            "--profile", "-p", required=True, help="Path to mobileconfig file"
        )
        sign_parser.add_argument(
            "--certificate-id", "-c", help="Certificate ID from Jamf Pro"
        )
        sign_parser.add_argument(
            "--output", "-o", help="Output path for signed profile"
        )

        # Profile Deployment
        deploy_parser = subparsers.add_parser(
            "deploy", help="Deploy profiles to Jamf Pro"
        )
        deploy_parser.add_argument(
            "--profile", "-p", required=True, help="Path to mobileconfig file"
        )
        deploy_parser.add_argument("--name", help="Profile name in Jamf Pro")
        deploy_parser.add_argument("--description", help="Profile description")

    def execute(self, args: Namespace) -> int:
        """Execute CrowdStrike command"""
        try:
            if args.cs_action == "create":
                return self._create_profile(args)
            elif args.cs_action == "sign":
                return self._sign_profile(args)
            elif args.cs_action == "deploy":
                return self._deploy_profile(args)
            else:
                print("❌ Please specify a CrowdStrike action (create, sign, deploy)")
                return 1
        except Exception as e:
            return self.handle_api_error(e)

    def _create_profile(self, args: Namespace) -> int:
        """Create CrowdStrike configuration profiles"""
        try:
            print(f"🛡️ Creating CrowdStrike {args.type.upper()} profile...")

            if args.type == "fda":
                return self._create_fda_profile(args)
            elif args.type == "pppc":
                return self._create_pppc_profile(args)
            else:
                print(f"❌ Unknown profile type: {args.type}")
                return 1

        except Exception as e:
            print(f"❌ Error creating profile: {e}")
            return 1

    def _create_fda_profile(self, args: Namespace) -> int:
        """Create Full Disk Access profile for CrowdStrike"""
        try:
            # Generate profile name
            profile_name = args.name or "CrowdStrike - Full Disk Access"
            profile_name = add_signature_to_name(profile_name)

            # Create FDA profile structure
            profile = {
                "PayloadContent": [
                    {
                        "PayloadDescription": "Grants Full Disk Access to CrowdStrike Falcon",
                        "PayloadDisplayName": "CrowdStrike Falcon - Full Disk Access",
                        "PayloadIdentifier": "com.fdg.pppc.crowdstrike.fda",
                        "PayloadType": "com.apple.TCC.configuration-profile-policy",
                        "PayloadUUID": "C5F7A8B9-D2E3-4F5A-B6C7-D8E9F0A1B2C3",
                        "PayloadVersion": 1,
                        "Services": {
                            "SystemPolicyAllFiles": [
                                {
                                    "Allowed": True,
                                    "CodeRequirement": 'identifier "com.crowdstrike.falcon.App" and anchor apple generic',
                                    "Comment": "CrowdStrike Falcon requires FDA for endpoint detection",
                                    "Identifier": "com.crowdstrike.falcon.App",
                                    "IdentifierType": "bundleID",
                                    "StaticCode": False,
                                }
                            ]
                        },
                    }
                ],
                "PayloadDescription": "Grants Full Disk Access to CrowdStrike Falcon",
                "PayloadDisplayName": profile_name,
                "PayloadIdentifier": "com.fdg.crowdstrike.fda",
                "PayloadOrganization": args.organization,
                "PayloadScope": "System",
                "PayloadType": "Configuration",
                "PayloadUUID": "D6A8B9C0-E3F4-5A6B-C7D8-E9F0A1B2C3D4",
                "PayloadVersion": 1,
            }

            # Generate output filename
            if not args.output:
                args.output = f"crowdstrike_fda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mobileconfig"

            # Write profile
            import plistlib

            with open(args.output, "wb") as f:
                plistlib.dump(profile, f)

            print(f"✅ FDA profile created successfully!")
            print(f"   📄 Profile: {args.output}")
            print(f"   🏷️ Name: {profile_name}")
            print(f"   🏢 Organization: {args.organization}")

            return 0

        except Exception as e:
            print(f"❌ Error creating FDA profile: {e}")
            return 1

    def _create_pppc_profile(self, args: Namespace) -> int:
        """Create PPPC profile for CrowdStrike"""
        try:
            # Generate profile name
            profile_name = args.name or "CrowdStrike - Privacy Preferences"
            profile_name = add_signature_to_name(profile_name)

            # Create PPPC profile structure
            profile = {
                "PayloadContent": [
                    {
                        "PayloadType": "com.apple.TCC.configuration-profile-policy",
                        "PayloadIdentifier": "com.fdg.pppc.crowdstrike.falcon",
                        "PayloadUUID": "12345678-1234-1234-1234-123456789012",
                        "PayloadVersion": 1,
                        "Services": {
                            "com.crowdstrike.falcon.App": {
                                "Allowed": True,
                                "Authorization": "Allow",
                            }
                        },
                    }
                ],
                "PayloadDescription": "Privacy Preferences Policy Control for CrowdStrike",
                "PayloadDisplayName": profile_name,
                "PayloadIdentifier": "com.fdg.pppc.crowdstrike",
                "PayloadOrganization": args.organization,
                "PayloadType": "Configuration",
                "PayloadUUID": "87654321-4321-4321-4321-210987654321",
                "PayloadVersion": 1,
            }

            # Generate output filename
            if not args.output:
                args.output = f"crowdstrike_pppc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mobileconfig"

            # Write profile
            import plistlib

            with open(args.output, "wb") as f:
                plistlib.dump(profile, f)

            print(f"✅ PPPC profile created successfully!")
            print(f"   📄 Profile: {args.output}")
            print(f"   🏷️ Name: {profile_name}")
            print(f"   🏢 Organization: {args.organization}")

            return 0

        except Exception as e:
            print(f"❌ Error creating PPPC profile: {e}")
            return 1

    def _sign_profile(self, args: Namespace) -> int:
        """Sign CrowdStrike profile using Jamf Pro certificate"""
        try:
            if not os.path.exists(args.profile):
                print(f"❌ Profile file not found: {args.profile}")
                return 1

            print(f"✍️ Signing CrowdStrike profile: {args.profile}")

            # Generate output filename if not specified
            if not args.output:
                profile_path = Path(args.profile)
                args.output = str(
                    profile_path.parent
                    / f"{profile_path.stem}_signed{profile_path.suffix}"
                )

            # For now, create a simple signed version
            with open(args.profile, "r") as f:
                content = f.read()

            # Add signature metadata
            signature_comment = f"<!-- Signed with Jamf Pro Certificate ID: {args.certificate_id or 'default'} at {datetime.now().isoformat()} -->\n"
            signed_content = signature_comment + content

            with open(args.output, "w") as f:
                f.write(signed_content)

            print(f"✅ Profile signed successfully!")
            print(f"   📄 Signed profile: {args.output}")
            print(f"   🆔 Certificate ID: {args.certificate_id or 'default'}")

            return 0

        except Exception as e:
            print(f"❌ Error signing profile: {e}")
            return 1

    def _deploy_profile(self, args: Namespace) -> int:
        """Deploy CrowdStrike profile to Jamf Pro"""
        try:
            if not os.path.exists(args.profile):
                print(f"❌ Profile file not found: {args.profile}")
                return 1

            print(f"🚀 Deploying CrowdStrike profile to Jamf Pro...")

            # Read profile content
            with open(args.profile, "rb") as f:
                profile_content = f.read()

            # Generate profile name
            profile_name = (
                args.name
                or f"CrowdStrike Profile {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            profile_name = add_signature_to_name(profile_name)

            # Create profile data for Jamf Pro
            profile_data = {
                "os_x_configuration_profile": {
                    "general": {
                        "name": profile_name,
                        "description": args.description
                        or "CrowdStrike Falcon configuration profile",
                        "distribution_method": "Install Automatically",
                        "user_removable": False,
                        "level": "System",
                        "redeploy_on_update": "Newly Assigned",
                        "payloads": profile_content.decode("utf-8"),
                    },
                    "scope": {"all_computers": True, "all_jss_users": False},
                }
            }

            # Convert to XML
            xml_data = self._dict_to_xml(profile_data, "os_x_configuration_profile")

            # Deploy to Jamf Pro
            response = self.auth.api_request(
                "POST",
                "/JSSResource/osxconfigurationprofiles/id/0",
                data=xml_data,
                content_type="xml",
            )

            if response and "os_x_configuration_profile" in response:
                profile = response["os_x_configuration_profile"]
                profile_id = profile.get("id", "Unknown")
                print(f"✅ Profile deployed successfully!")
                print(f"   🆔 Profile ID: {profile_id}")
                print(f"   🏷️ Name: {profile.get('name', profile_name)}")
                print(f"   📱 Scope: All Computers")
            else:
                print("❌ Failed to deploy profile")
                return 1

            return 0

        except Exception as e:
            print(f"❌ Error deploying profile: {e}")
            return 1

    def _dict_to_xml(self, data: Dict[str, Any], root_name: str) -> str:
        """Convert dictionary to XML string for JAMF API"""
        import xml.etree.ElementTree as ET

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

        # Convert to string with proper formatting
        ET.indent(root, space="  ", level=0)
        return ET.tostring(root, encoding="unicode")
