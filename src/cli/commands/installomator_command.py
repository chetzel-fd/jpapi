#!/usr/bin/env python3
"""
Installomator Command for jpapi CLI
Integrates the SOLID-compliant installomator addon with the main jpapi CLI
"""

import sys
import re
from pathlib import Path
from typing import Any, List, Optional

from .common_imports import ArgumentParser, BaseCommand, Namespace

# Add addons to path for installomator imports
addons_path = Path(__file__).parent.parent.parent / "addons"
sys.path.insert(0, str(addons_path))

from installomator import InstallomatorFactory, PolicyConfig, PolicyType, TriggerType
from installomator.profile_generator import InstallomatorProfileGenerator
from .create_command import CreateCommand


class InstallomatorCommand(BaseCommand):
    """Installomator command using jpapi's CLI architecture"""

    def __init__(self):
        super().__init__(
            name="installomator",
            description="📱 Installomator policy management with SOLID architecture",
        )
        self._setup_patterns()
        self.factory = InstallomatorFactory()

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        parser.add_argument(
            "label",
            nargs="?",
            help="Installomator label to create setup for (e.g., 'adobecreativeclouddesktop')",
        )
        parser.add_argument(
            "--env", default="prod", help="Environment to use (dev/prod/sandbox)"
        )
        parser.add_argument(
            "--mock", action="store_true", help="Use mock components for testing"
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose output"
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip confirmation prompt (non-interactive mode)",
        )

    def _setup_patterns(self):
        """Setup conversational patterns for Installomator commands"""

        self.add_conversational_pattern(
            pattern="list apps",
            handler="_list_apps",
            description="List all available Installomator apps",
            aliases=["apps", "list", "show apps", "available apps"],
        )

        self.add_conversational_pattern(
            pattern="search apps",
            handler="_search_apps",
            description="Search for Installomator apps",
            aliases=["search", "find apps", "find", "lookup"],
        )

        self.add_conversational_pattern(
            pattern="create policy",
            handler="_create_policy",
            description="Create Installomator policy",
            aliases=["create", "make policy", "add policy", "new policy"],
        )

        self.add_conversational_pattern(
            pattern="create latest",
            handler="_create_latest",
            description="Create latest version policy",
            aliases=["latest", "latest version", "install latest"],
        )

        self.add_conversational_pattern(
            pattern="create daily",
            handler="_create_daily",
            description="Create daily update policy",
            aliases=["daily", "update daily", "daily update"],
        )

        self.add_conversational_pattern(
            pattern="create batch",
            handler="_create_batch",
            description="Create multiple policies from batch file",
            aliases=["batch", "bulk create", "mass create"],
        )

        self.add_conversational_pattern(
            pattern="interactive",
            handler="_interactive_mode",
            description="Run interactive policy creation",
            aliases=["interactive", "guided", "wizard", "setup"],
        )

    def execute(self, args: Namespace) -> int:
        """Execute the installomator command using conversational patterns"""
        try:
            # Create service with appropriate configuration
            environment = getattr(args, "env", "prod")
            use_mock = getattr(args, "mock", False)

            service = self.factory.create_installomator_service(
                environment=environment, use_mock_components=use_mock
            )

            if use_mock:
                print("🧪 Using mock components for testing")

            # Check if a label was provided as a positional argument
            if hasattr(args, "label") and args.label:
                return self._create_installomator_setup(args, service)

            # Use the base class conversational pattern handling
            return super().execute(args)

        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if getattr(args, "verbose", False):
                import traceback

                traceback.print_exc()
            return 1

    def _create_installomator_setup(self, args: Namespace, service) -> int:
        """Create complete Installomator setup: 2 policies + 3 profiles with real payloads"""
        label = args.label

        print(f"🎯 Creating Complete Installomator Setup for: {label}")
        print("=" * 60)

        # Step 1: Grep labels from Installomator labels text file
        print(f"🔍 Searching for label: {label}")
        app_info = self._find_app_by_label(label)

        if not app_info:
            print(f"❌ Label '{label}' not found in Installomator labels")
            return 1

        print(f"✅ Found app: {app_info['name']}")
        print(f"   Description: {app_info.get('description', 'N/A')}")

        # Step 2: Verify prompt
        print(f"\n📋 Setup will create:")
        print(f"   • 2 Policies: Latest Version + Daily Update")
        print(f"   • 3 Profiles: PPPC + Preferences + Combined")
        print(f"   • App: {app_info['name']} ({label})")

        if not getattr(args, "yes", False):
            confirm = input(f"\n❓ Continue with setup? [y/N]: ").strip().lower()
            if confirm not in ["y", "yes"]:
                print("❌ Setup cancelled by user")
                return 1
        else:
            print(f"\n✅ Non-interactive mode: Proceeding with setup...")

        # Step 3: Create policies with real payloads
        print(f"\n🚀 Creating policies in JAMF Pro...")
        policy_results = self._create_policies_with_payloads(
            args, service, app_info, label
        )

        # Step 4: Create profiles with real payloads
        print(f"\n🔧 Creating configuration profiles in JAMF Pro...")
        profile_results = self._create_profiles_with_payloads(args, app_info, label)

        # Summary
        if policy_results and profile_results:
            print(f"\n🎉 Complete setup created successfully!")
            print(f"   ✅ 2 Policies created with Installomator scripts")
            print(f"   ✅ 3 Configuration profiles created with payloads")
            return 0
        else:
            print(f"\n❌ Setup completed with errors")
            return 1

    def _find_app_by_label(self, label: str) -> Optional[dict]:
        """Find app info by grepping Installomator labels"""
        # This would normally grep from the actual Installomator labels file
        # For now, we'll use our cached apps
        service = self.factory.create_installomator_service()
        apps = service.search_apps(label)

        for app in apps:
            if app.label == label:
                return {
                    "name": app.app_name,
                    "label": app.label,
                    "description": app.description,
                    "category": app.category,
                }
        return None

    def _create_policies_with_payloads(self, args, service, app_info, label):
        """Create 2 policies with real Installomator script payloads"""
        try:
            # Create Latest Version policy with unique name
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            latest_config = PolicyConfig(
                app_name=app_info["name"],
                label=label,
                policy_name=f"{app_info['name']} Install Latest Version - {timestamp}",
                policy_type=PolicyType.LATEST_VERSION,
                trigger=TriggerType.EVENT,
                category="Productivity",
                description=f"Installomator policy for {app_info['name']} - Latest Version",
                scope_groups=["All Computers"],
                frequency="Ongoing",
                retry_attempts=3,
                notify_on_failure=True,
            )

            # Create Daily Update policy with unique name
            daily_config = PolicyConfig(
                app_name=app_info["name"],
                label=label,
                policy_name=f"{app_info['name']} Daily Update - {timestamp}",
                policy_type=PolicyType.DAILY_UPDATE,
                trigger=TriggerType.EVENT,
                category="Productivity",
                description=f"Installomator policy for {app_info['name']} - Daily Update",
                scope_groups=["All Computers"],
                frequency="Ongoing",
                retry_attempts=3,
                notify_on_failure=True,
            )

            # Create policies in JAMF Pro
            latest_result = self._create_policy_in_jamf(args, latest_config)
            daily_result = self._create_policy_in_jamf(args, daily_config)

            if latest_result and daily_result:
                print(f"   ✅ Latest Version Policy: {latest_config.policy_name}")
                print(f"   ✅ Daily Update Policy: {daily_config.policy_name}")
                return True
            else:
                print(f"   ❌ Failed to create policies")
                return False

        except Exception as e:
            print(f"   ❌ Error creating policies: {e}")
            return False

    def _create_policy_in_jamf(self, args, config):
        """Create a single policy in JAMF Pro with real payload"""
        try:
            # Generate JAMF policy JSON
            jamf_policy = config.to_jamf_policy()

            # Create the full policy structure with scripts
            policy_data = {
                "policy": {
                    "general": {
                        "name": config.policy_name,
                        "enabled": True,
                        "frequency": config.frequency,
                        "trigger_checkin": False,
                        "trigger_startup": False,
                        "trigger_login": False,
                        "trigger_logout": False,
                        "trigger_other": (
                            "EVENT" if config.trigger.value == "EVENT" else None
                        ),
                        "category": {"name": config.category},
                        "description": config.description,
                    },
                    "scope": {
                        "all_computers": len(config.scope_groups) == 0,
                        "computers": [],
                        "computer_groups": [
                            {"name": group} for group in config.scope_groups
                        ],
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
                            "computer_groups": [
                                {"name": group} for group in config.exclusions
                            ],
                            "buildings": [],
                            "departments": [],
                            "users": [],
                            "user_groups": [],
                            "network_segments": [],
                            "ibeacons": [],
                        },
                    },
                    "scripts": {
                        "script": [
                            {
                                "id": 196,
                                "priority": "Before",
                                "parameter4": config.label,
                                "parameter5": config.app_name,
                            }
                        ]
                    },
                }
            }

            # Create command instance to use its dict_to_xml method
            create_cmd = CreateCommand()

            # Convert to XML for JAMF API
            xml_data = create_cmd.dict_to_xml(policy_data["policy"], "policy")

            # Create policy via API using the base command's auth
            response = self.auth.api_request(
                "POST", "/JSSResource/policies/id/0", data=xml_data, content_type="xml"
            )

            # Parse the raw_response if needed
            if response and "raw_response" in response:
                import xml.etree.ElementTree as ET

                root = ET.fromstring(response["raw_response"])
                policy_id = (
                    root.find(".//id").text
                    if root.find(".//id") is not None
                    else "Unknown"
                )
                print(f"     ✅ Created policy: {config.policy_name}")
                print(f"     📤 Policy ID: {policy_id}")
                return True
            elif response and "policy" in response:
                created_policy = response["policy"]
                print(f"     ✅ Created policy: {config.policy_name}")
                print(f"     📤 Policy ID: {created_policy.get('id', 'Unknown')}")
                return True
            else:
                print(f"     ❌ Policy creation failed - no policy in response")
                return False

        except Exception as e:
            print(f"   ❌ Error creating policy {config.policy_name}: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _create_profiles_with_payloads(self, args, app_info, label):
        """Create 3 configuration profiles with real payloads"""
        try:
            profile_generator = InstallomatorProfileGenerator()

            # Generate profiles
            profile_results = profile_generator.generate_profiles_for_app(label)

            if not profile_results or not profile_results.get("generated_profiles"):
                print(f"   ❌ No profiles generated for {label}")
                return False

            # Upload each profile to JAMF Pro
            success_count = 0
            for profile in profile_results["generated_profiles"]:
                if self._upload_profile_to_jamf(args, profile, app_info["name"], label):
                    success_count += 1
                    print(f"   ✅ {profile['type']} Profile: {profile['name']}")
                else:
                    print(f"   ❌ Failed to upload {profile['type']} Profile")

            return success_count > 0

        except Exception as e:
            print(f"   ❌ Error creating profiles: {e}")
            return False

    def _upload_profile_to_jamf(self, args, profile, app_name, label):
        """Upload a single profile to JAMF Pro with real payload"""
        try:
            import plistlib
            import base64
            from pathlib import Path

            # Read the mobileconfig content (our files are in JSON format)
            mobileconfig_path = Path(profile["file"])
            import json

            with open(mobileconfig_path, "r") as f:
                mobileconfig_data = json.load(f)

            # Create profile name with unique timestamp
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            profile_name = f"{profile['name']} - {timestamp}"

            # Create the full profile structure with payload
            profile_root = (
                "os_x_configuration_profile"
                if args.env != "ios"
                else "mobile_device_configuration_profile"
            )

            # Create command instance to use its methods
            create_cmd = CreateCommand()

            # Convert mobileconfig JSON to XML format using the proper method
            payloads_xml = create_cmd._convert_mobileconfig_to_xml(mobileconfig_data)

            profile_data = {
                profile_root: {
                    "general": {
                        "name": profile_name,
                        "description": f"{profile['type']} profile for {app_name}",
                        "distribution_method": "Install Automatically",
                        "user_removable": False,
                        "level": "System",
                        "redeploy_on_update": "Newly Assigned",
                        "payloads": payloads_xml,
                    },
                    "scope": {
                        "all_computers": False,
                        "computers": [],
                        "computer_groups": [],
                        "buildings": [],
                        "departments": [],
                        "limitations": {
                            "users": [],
                            "user_groups": [],
                            "network_limitations": {
                                "minimum_network_connection": "No Minimum",
                                "any_ip_address": True,
                                "network_segments": [],
                            },
                        },
                        "exclusions": {
                            "computers": [],
                            "computer_groups": [],
                            "buildings": [],
                            "departments": [],
                            "users": [],
                            "user_groups": [],
                        },
                    },
                }
            }

            # Convert to XML for JAMF API
            xml_data = create_cmd.dict_to_xml(profile_data[profile_root], profile_root)

            # Create profile via API
            endpoint = (
                "/JSSResource/osxconfigurationprofiles/id/0"
                if args.env != "ios"
                else "/JSSResource/mobiledeviceconfigurationprofiles/id/0"
            )
            response = self.auth.api_request(
                "POST", endpoint, data=xml_data, content_type="xml"
            )

            # Parse the raw_response if needed
            if response and "raw_response" in response:
                import xml.etree.ElementTree as ET

                root = ET.fromstring(response["raw_response"])
                profile_id = (
                    root.find(".//id").text
                    if root.find(".//id") is not None
                    else "Unknown"
                )
                print(f"     ✅ Created {profile['type']} profile: {profile_name}")
                print(f"     📤 Profile ID: {profile_id}")
                return True
            elif response and profile_root in response:
                created_profile = response[profile_root]
                print(f"     ✅ Created {profile['type']} profile: {profile_name}")
                print(f"     📤 Profile ID: {created_profile.get('id', 'Unknown')}")
                return True
            else:
                print(
                    f"     ❌ Failed to create {profile['type']} profile with payload"
                )
                return False

        except Exception as e:
            print(f"     ❌ Error uploading profile: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _convert_mobileconfig_payloads(self, mobileconfig_data):
        """Convert mobileconfig PayloadContent to JAMF XML format"""
        import plistlib

        # Ensure we have the proper mobileconfig structure
        if not isinstance(mobileconfig_data, dict):
            raise ValueError("mobileconfig_data must be a dictionary")

        # Convert the entire mobileconfig to plist XML format
        plist_str = plistlib.dumps(mobileconfig_data, fmt=plistlib.FMT_XML).decode(
            "utf-8"
        )
        return plist_str

    def _dict_to_xml(self, data, root_name):
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

    def _list_apps(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Handle list apps command"""
        service = self.factory.create_installomator_service(
            environment=getattr(args, "env", "prod"),
            use_mock_components=getattr(args, "mock", False),
        )

        apps = service.list_all_apps()
        if not apps:
            print("❌ No apps available")
            return 1

        print(f"📱 Available Installomator Apps ({len(apps)} total):")
        print("=" * 80)

        # Group by first letter
        grouped = {}
        for app in apps:
            first_letter = app.app_name[0].upper()
            if first_letter not in grouped:
                grouped[first_letter] = []
            grouped[first_letter].append(app)

        for letter in sorted(grouped.keys()):
            print(f"\n{letter}:")
            for app in sorted(grouped[letter], key=lambda x: x.app_name):
                print(f"   {app.app_name:<40} -> {app.label}")

        return 0

    def _search_apps(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Handle search apps command"""
        service = self.factory.create_installomator_service(
            environment=getattr(args, "env", "prod"),
            use_mock_components=getattr(args, "mock", False),
        )

        search_term = " ".join(args.terms) if args.terms else ""
        if not search_term:
            print("❌ Please provide search terms")
            return 1

        apps = service.search_apps(search_term)
        if not apps:
            print(f"❌ No apps found matching '{search_term}'")
            return 1

        print(f"🔍 Found {len(apps)} apps matching '{search_term}':")
        print("=" * 80)
        for app in apps:
            print(f"   {app.app_name:<40} -> {app.label}")

        return 0

    def _create_batch(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Handle batch create command"""
        service = self.factory.create_installomator_service(
            environment=getattr(args, "env", "prod"),
            use_mock_components=getattr(args, "mock", False),
        )

        batch_file = args.terms[0] if args.terms else ""
        if not batch_file:
            print("❌ Please provide batch file path")
            return 1

        if not Path(batch_file).exists():
            print(f"❌ Batch file not found: {batch_file}")
            return 1

        # Load batch configurations
        batch_processor = service.batch_processor
        configs = batch_processor.load_batch_from_file(batch_file)

        if not configs:
            print("❌ No valid configurations found in batch file")
            return 1

        print(f"🚀 Creating {len(configs)} policies from batch file...")

        # Create policies
        results = service.create_batch_policies(configs)

        # Display results
        service.interactive_ui.display_results(results)

        # Return appropriate exit code
        failed_count = sum(1 for r in results if not r.success)
        return 1 if failed_count > 0 else 0

    def _interactive_mode(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Handle interactive mode"""
        service = self.factory.create_installomator_service(
            environment=getattr(args, "env", "prod"),
            use_mock_components=getattr(args, "mock", False),
        )

        print("🎯 Interactive Mode - Follow the prompts to create your policy")
        result = service.create_policy_interactive()
        if result.success:
            print("\n✅ Policy created successfully!")
            print(f"   Policy: {result.policy_name}")
            print(f"   ID: {result.policy_id}")
            if result.warnings:
                print("\n⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"   • {warning}")
            return 0
        else:
            print("\n❌ Failed to create policy")
            print(f"   Error: {result.error_message}")
            return 1

    def _create_policy(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Handle create policy command"""
        service = self.factory.create_installomator_service(
            environment=getattr(args, "env", "prod"),
            use_mock_components=getattr(args, "mock", False),
        )

        # For conversational patterns, we'll use interactive mode
        print("🎯 Creating policy - Follow the prompts")
        result = service.create_policy_interactive()
        if result.success:
            print("\n✅ Policy created successfully!")
            print(f"   Policy: {result.policy_name}")
            print(f"   ID: {result.policy_id}")
            if result.warnings:
                print("\n⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"   • {warning}")
            return 0
        else:
            print("\n❌ Failed to create policy")
            print(f"   Error: {result.error_message}")
            return 1

    def _create_latest(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Handle create latest version policy"""
        return self._create_policy(args, pattern)

    def _create_daily(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Handle create daily update policy"""
        return self._create_policy(args, pattern)
