#!/usr/bin/env python3
"""
Create Command for jpapi CLI
Create new JAMF objects (categories, policies, searches, etc.)
"""

from .common_imports import (
    ArgumentParser,
    Namespace,
    Dict,
    Any,
    List,
    Optional,
    BaseCommand,
)
import argparse
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from resources.config.api_endpoints import APIRegistry
from lib.utils.manage_signatures import (
    add_signature_to_name,
    get_user_signature,
    set_user_signature,
)

# SOLID: Import services and handlers
from .create.services.xml_converter import XMLConverterService
from .create.services.profile_converter import ProfileConverterService
from .create.services.criteria_parser import CriteriaParserService
from .create.services.production_checker import ProductionCheckerAdapter
from .create.handlers.handler_registry import create_handler_registry


class CreateCommand(BaseCommand):
    """Create new JAMF objects (categories, policies, searches)"""

    def __init__(self):
        super().__init__(
            name="create",
            description="Create new JAMF objects (categories, policies, searches)",
        )

        # SOLID: Initialize services (SRP, DIP)
        self.xml_converter = XMLConverterService()
        self.profile_converter = ProfileConverterService()
        self.criteria_parser = CriteriaParserService()
        self.production_checker = ProductionCheckerAdapter(self)

        # SOLID: Initialize handler registry (OCP)
        self._handler_registry = None

    def _get_handler_registry(self):
        """Lazy initialization of handler registry"""
        if self._handler_registry is None:
            self._handler_registry = create_handler_registry(
                self.auth, self.xml_converter, self.production_checker
            )
        return self._handler_registry

    def dict_to_xml(self, data: Dict[str, Any], root_name: str) -> str:
        """Convert dictionary to XML string for JAMF API (delegates to service)"""
        return self.xml_converter.dict_to_xml(data, root_name)

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add create command arguments with comprehensive aliases"""
        # Traditional subcommand structure (remove conflicting positional args)
        subparsers = parser.add_subparsers(
            dest="create_object", help="Object type to create"
        )

        # Categories - main command with aliases in help
        category_parser = subparsers.add_parser(
            "category", help="Create new category (also: cat)"
        )
        category_parser.add_argument("name", help="Category name")
        category_parser.add_argument(
            "--priority",
            type=int,
            default=9,
            help="Category priority (1-20, default: 9)",
        )
        self.setup_common_args(category_parser)

        # Hidden aliases for categories
        for alias in ["cat", "cats"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument("name", help="Category name")
            alias_parser.add_argument(
                "--priority", type=int, default=9, help="Category priority (1-20)"
            )
            self.setup_common_args(alias_parser)

        # Policies - main command with aliases in help
        policy_parser = subparsers.add_parser(
            "policy", help="Create new policy (also: pol)"
        )
        policy_parser.add_argument("name", help="Policy name")
        policy_parser.add_argument("--category", help="Policy category")
        policy_parser.add_argument(
            "--enabled", action="store_true", help="Enable policy immediately"
        )
        policy_parser.add_argument(
            "--frequency",
            choices=["Once per computer", "Once per user", "Ongoing"],
            default="Ongoing",
            help="Policy frequency",
        )
        policy_parser.add_argument(
            "--trigger",
            choices=["Startup", "Login", "Logout", "Check-in"],
            default="Check-in",
            help="Policy trigger",
        )
        self.setup_common_args(policy_parser)

        # Hidden aliases for policies
        for alias in ["pol", "policies"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument("name", help="Policy name")
            alias_parser.add_argument("--category", help="Policy category")
            alias_parser.add_argument(
                "--enabled", action="store_true", help="Enable policy immediately"
            )
            alias_parser.add_argument(
                "--frequency",
                choices=["Once per computer", "Once per user", "Ongoing"],
                default="Ongoing",
                help="Policy frequency",
            )
            alias_parser.add_argument(
                "--trigger",
                choices=["Startup", "Login", "Logout", "Check-in"],
                default="Check-in",
                help="Policy trigger",
            )
            self.setup_common_args(alias_parser)

        # Search templates - main command
        search_parser = subparsers.add_parser(
            "search", help="Create search template (also: find)"
        )
        search_parser.add_argument("name", help="Search template name")
        search_parser.add_argument(
            "--type",
            choices=["computer", "mobile"],
            default="computer",
            help="Search type",
        )
        search_parser.add_argument("--criteria", help="Search criteria (JSON format)")
        search_parser.add_argument(
            "--display-fields", help="Display fields (comma-separated)"
        )
        self.setup_common_args(search_parser)

        # Hidden aliases for search
        for alias in ["find", "searches"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument("name", help="Search template name")
            alias_parser.add_argument(
                "--type",
                choices=["computer", "mobile"],
                default="computer",
                help="Search type",
            )
            alias_parser.add_argument(
                "--criteria", help="Search criteria (JSON format)"
            )
            alias_parser.add_argument(
                "--display-fields", help="Display fields (comma-separated)"
            )
            self.setup_common_args(alias_parser)

        # Groups - main command with aliases in help
        group_parser = subparsers.add_parser(
            "group", help="Create new group (also: grp)"
        )
        group_parser.add_argument("name", help="Group name")
        group_parser.add_argument(
            "--type",
            choices=["computer", "mobile"],
            default="computer",
            help="Group type",
        )
        group_parser.add_argument(
            "--smart", action="store_true", help="Create smart group"
        )
        group_parser.add_argument(
            "--criteria", help="Smart group criteria (JSON format)"
        )
        self.setup_common_args(group_parser)

        # Hidden aliases for groups
        for alias in ["grp", "groups"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument("name", help="Group name")
            alias_parser.add_argument(
                "--type",
                choices=["computer", "mobile"],
                default="computer",
                help="Group type",
            )
            alias_parser.add_argument(
                "--smart", action="store_true", help="Create smart group"
            )
            alias_parser.add_argument(
                "--criteria", help="Smart group criteria (JSON format)"
            )
            self.setup_common_args(alias_parser)

        # Smart group - main command with flexible criteria
        smart_group_parser = subparsers.add_parser(
            "smart-group", help="Create smart group with flexible criteria"
        )
        smart_group_parser.add_argument("name", help="Group name")
        smart_group_parser.add_argument(
            "--criteria",
            required=True,
            help='Smart group criteria (e.g., email:"user1,user2", model:"MacBook Pro")',
        )
        smart_group_parser.add_argument(
            "--type",
            choices=["computer", "mobile"],
            default="computer",
            help="Group type",
        )
        smart_group_parser.add_argument(
            "--id",
            type=int,
            help="Update existing group by ID instead of creating new one",
        )
        self.setup_common_args(smart_group_parser)

        # Profiles - main command with aliases in help
        profile_parser = subparsers.add_parser(
            "profile", help="Create new configuration profile (also: prof)"
        )
        profile_parser.add_argument("name", help="Profile name")
        profile_parser.add_argument(
            "--type", choices=["macos", "ios"], default="macos", help="Profile type"
        )
        profile_parser.add_argument("--description", help="Profile description")
        profile_parser.add_argument("--category", help="Profile category")

        # New payload options
        payload_group = profile_parser.add_mutually_exclusive_group()
        payload_group.add_argument(
            "--json-payload", help="JSON file containing profile payload configuration"
        )
        payload_group.add_argument(
            "--mobileconfig-file", help="mobileconfig file to upload as profile payload"
        )

        self.setup_common_args(profile_parser)

        # Hidden aliases for profiles
        for alias in ["prof", "profiles"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument("name", help="Profile name")
            alias_parser.add_argument(
                "--type", choices=["macos", "ios"], default="macos", help="Profile type"
            )
            alias_parser.add_argument("--description", help="Profile description")
            alias_parser.add_argument("--category", help="Profile category")

            # New payload options for aliases
            payload_group = alias_parser.add_mutually_exclusive_group()
            payload_group.add_argument(
                "--json-payload",
                help="JSON file containing profile payload configuration",
            )
            payload_group.add_argument(
                "--mobileconfig-file",
                help="mobileconfig file to upload as profile payload",
            )

            self.setup_common_args(alias_parser)

        # Hidden aliases for smart groups
        for alias in ["smart", "smartgrp"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument("name", help="Group name")
            alias_parser.add_argument(
                "--criteria",
                required=True,
                help='Smart group criteria (e.g., email:"user1,user2", model:"MacBook Pro")',
            )
            alias_parser.add_argument(
                "--type",
                choices=["computer", "mobile"],
                default="computer",
                help="Group type",
            )
            self.setup_common_args(alias_parser)

        # Extension attributes
        ext_attr_parser = subparsers.add_parser(
            "extension-attribute", help="Create extension attribute"
        )
        ext_attr_parser.add_argument(
            "attr_type",
            choices=["computer", "mobile", "user"],
            help="Extension attribute type",
        )
        ext_attr_parser.add_argument("name", help="Attribute name")
        ext_attr_parser.add_argument("--description", help="Attribute description")
        ext_attr_parser.add_argument(
            "--data-type",
            choices=["String", "Integer", "Date", "Boolean"],
            default="String",
            help="Data type",
        )
        ext_attr_parser.add_argument(
            "--input-type",
            choices=["Text Field", "Pop-up Menu", "Script", "LDAP Mapping"],
            default="Text Field",
            help="Input type",
        )
        ext_attr_parser.add_argument(
            "--script-file",
            help="Path to script file (auto-sets input-type to Script)",
        )
        ext_attr_parser.add_argument(
            "--enabled",
            action="store_true",
            default=True,
            help="Enable the attribute",
        )
        ext_attr_parser.add_argument(
            "--inventory-display",
            default="Extension Attributes",
            help="Inventory display section (default: Extension Attributes)",
        )
        self.setup_common_args(ext_attr_parser)

        # Signature configuration
        signature_parser = subparsers.add_parser(
            "signature", help="Configure signature settings"
        )
        signature_parser.add_argument(
            "--set", help='Set the signature to use (e.g., "jdoe")'
        )
        signature_parser.add_argument(
            "--show", action="store_true", help="Show current signature"
        )
        signature_parser.add_argument(
            "--reset", action="store_true", help="Reset to default signature (admin)"
        )
        self.setup_common_args(signature_parser)

    def execute(self, args: Namespace) -> int:
        """Execute the create command"""
        # Set environment on command instance
        if hasattr(args, "env"):
            self.environment = args.env

        # Enhanced production safety warnings
        if self.is_production_environment():
            print("🚨 PRODUCTION ENVIRONMENT DETECTED 🚨")
            print("=" * 60)
            print(f"Environment: {self.environment.upper()}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            print("⚠️  WARNING: You are about to CREATE objects in PRODUCTION!")
            print("   • This will modify live JAMF Pro data")
            print("   • Changes may affect all managed devices")
            print("   • Use --dry-run to test operations safely")
            print("   • Use --force to skip confirmation prompts")
            print("   • Consider testing in DEV environment first")
            print("=" * 60)
            print()

        if not self.check_auth(args):
            return 1

        # Additional production safety check
        if self.is_production_environment() and not getattr(args, "force", False):
            print("🔍 FINAL PRODUCTION SAFETY CHECK")
            print("=" * 50)
            print("You are about to CREATE objects in PRODUCTION environment.")
            print("This will modify live JAMF Pro data that may affect all devices.")
            print()
            print("Before proceeding, confirm:")
            print("1. You have tested this operation in DEV environment")
            print("2. You understand the impact on production systems")
            print("3. You have proper authorization for this change")
            print()

            final_confirm = (
                input(
                    "Do you want to proceed with creating objects in PRODUCTION? (y/N): "
                )
                .strip()
                .lower()
            )
            if final_confirm not in ["y", "yes"]:
                print("❌ Operation cancelled - safety check failed")
                return 1
            print("✅ Final safety check passed")
            print()

        try:
            # Handle subcommand structure
            if not args.create_object:
                print("🛠️ Create New JAMF Objects:")
                print()
                print("💬 Quick Create:")
                print("   jpapi create category 'Software Updates'")
                print("   jpapi create policy 'Install Chrome' --category Software")
                print("   jpapi create group 'Marketing Macs' --smart")
                print(
                    "   jpapi create smart-group 'WhatsApp Exclusions' --criteria 'email:jessica.oldham,emily.shields'"
                )
                print()
                print("🏗️  Traditional Create:")
                print("   jpapi create category 'New Category' --priority 5")
                print(
                    "   jpapi create policy 'Policy Name' --enabled --trigger Startup"
                )
                print("   jpapi create search 'Find iPads' --type mobile")
                print("   jpapi create group 'Smart Group' --smart --criteria '{...}'")
                print()
                print("🔧 Available Objects:")
                print("   Categories: category, cat")
                print("   Policies: policy, pol")
                print("   Profiles: profile, prof")
                print("   Searches: search, find")
                print("   Groups: group, grp")
                print("   Smart Groups: smart-group, smart, smartgrp")
                return 1

            # SOLID: Use handler registry (OCP, Strategy pattern)
            registry = self._get_handler_registry()
            handler = registry.find_handler(args.create_object)

            if handler:
                return handler.create(args)

            # Fallback to legacy handlers for complex operations
            if args.create_object in ["profile", "prof", "profiles"]:
                return self._create_profile(args)
            elif args.create_object in ["search", "find", "searches"]:
                return self._create_search(args)
            elif args.create_object in ["group", "grp", "groups"]:
                return self._create_group(args)
            elif args.create_object in ["smart-group", "smart", "smartgrp"]:
                return self._create_smart_group(args)
            elif args.create_object == "extension-attribute":
                return self._create_extension_attribute(args)
            elif args.create_object == "signature":
                return self._configure_signature(args)
            else:
                print(f"❌ Unknown create object: {args.create_object}")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_conversational_create(self, args: Namespace) -> int:
        """Handle conversational create patterns"""
        target = args.create_target.lower()
        name = args.create_name if args.create_name else None
        terms = args.create_terms if args.create_terms else []

        if not name:
            print(f"❌ Please specify a name for the {target}")
            return 1

        print(f"🛠️ Creating {target}: {name}")

        # Determine create type from target
        if target in ["category", "cat", "cats"]:
            return self._create_category_conversational(name, terms, args)
        elif target in ["policy", "pol", "policies"]:
            return self._create_policy_conversational(name, terms, args)
        elif target in ["search", "find", "searches"]:
            return self._create_search_conversational(name, terms, args)
        elif target in ["group", "grp", "groups"]:
            return self._create_group_conversational(name, terms, args)
        else:
            print(f"❌ Unknown create target: {target}")
            print("   Available: category, policy, search, group")
            return 1

    def _create_category(self, args: Namespace) -> int:
        """Create a new category"""
        try:
            # Production guardrails
            if not args.force and not self.check_destructive_operation(
                "Create Category", args.name
            ):
                return 1

            # Dry-run mode
            if args.dry_run:
                print(f"🔍 DRY-RUN: Would create Category: {args.name}")
                print(f"   Priority: {args.priority}")
                print(
                    "\n✅ Dry-run complete. Use without --dry-run to actually create the category."
                )
                return 0

            # Add signature to name
            signed_name = add_signature_to_name(args.name)
            print(f"📁 Creating Category: {signed_name}")

            # Validate priority
            if args.priority < 1 or args.priority > 20:
                print("❌ Priority must be between 1 and 20")
                return 1

            # Prepare category data
            category_data = {
                "category": {"name": signed_name, "priority": args.priority}
            }

            # Create category via API
            response = self.auth.api_request(
                "POST", "/JSSResource/categories/id/0", data=category_data
            )

            if response and "category" in response:
                created_category = response["category"]
                print(f"✅ Category created successfully!")
                print(f"   ID: {created_category.get('id', 'Unknown')}")
                print(f"   Name: {created_category.get('name', signed_name)}")
                print(f"   Priority: {created_category.get('priority', args.priority)}")
                return 0
            else:
                print("❌ Failed to create category")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _create_policy(self, args: Namespace) -> int:
        """Create a new policy"""
        try:
            # Add signature to name
            signed_name = add_signature_to_name(args.name)

            # Create comprehensive summary for production confirmation
            if self.is_production_environment():
                changes_summary = f"""
Policy Creation Summary:
  • Name: {signed_name}
  • Enabled: {args.enabled}
  • Frequency: {args.frequency}
  • Trigger: {args.trigger}
  • Category: {getattr(args, 'category', 'None')}
  • Scope: No computers (null scope)
  • Scripts: None
  • Packages: None
  • Impact: Will create a new policy in PRODUCTION
"""

                if not self.require_production_confirmation(
                    "Create Policy", f"Creating policy: {signed_name}", changes_summary
                ):
                    return 1

            print(f"📋 Creating Policy: {signed_name}")

            # Prepare policy data
            policy_data = {
                "policy": {
                    "general": {
                        "name": signed_name,
                        "enabled": args.enabled,
                        "frequency": args.frequency,
                        "trigger_checkin": args.trigger == "Check-in",
                        "trigger_startup": args.trigger == "Startup",
                        "trigger_login": args.trigger == "Login",
                        "trigger_logout": args.trigger == "Logout",
                    },
                    "scope": {
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
                    },
                }
            }

            # Add category if specified
            if args.category:
                policy_data["policy"]["general"]["category"] = {"name": args.category}

            # Create policy via API using XML format
            xml_data = self.dict_to_xml(policy_data["policy"], "policy")
            response = self.auth.api_request(
                "POST", "/JSSResource/policies/id/0", data=xml_data, content_type="xml"
            )

            if response and "policy" in response:
                created_policy = response["policy"]
                print(f"✅ Policy created successfully!")
                print(f"   ID: {created_policy.get('id', 'Unknown')}")
                print(f"   Name: {created_policy.get('name', signed_name)}")
                print(f"   Enabled: {args.enabled}")
                print(f"   Frequency: {args.frequency}")
                print(f"   Trigger: {args.trigger}")
                if args.category:
                    print(f"   Category: {args.category}")
                return 0
            else:
                print("❌ Failed to create policy")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _create_profile(self, args: Namespace) -> int:
        """Create a new configuration profile with JSON payload or mobileconfig upload"""
        try:
            # Add signature to name
            signed_name = add_signature_to_name(args.name)

            # Handle different profile creation methods
            if hasattr(args, "json_payload") and args.json_payload:
                return self._create_profile_from_json(args, signed_name)
            elif hasattr(args, "mobileconfig_file") and args.mobileconfig_file:
                return self._create_profile_from_mobileconfig(args, signed_name)
            else:
                return self._create_empty_profile(args, signed_name)

        except Exception as e:
            return self.handle_api_error(e)

    def _create_empty_profile(self, args: Namespace, signed_name: str) -> int:
        """Create an empty configuration profile"""
        # Create comprehensive summary for production confirmation
        if self.is_production_environment():
            changes_summary = f"""
Profile Creation Summary:
  • Name: {signed_name}
  • Type: {args.type.upper()}
  • Description: {getattr(args, 'description', 'None')}
  • Scope: No computers (null scope) - SAFE DEFAULT
  • Payload: Empty (no configuration) - SAFE DEFAULT
  • Impact: Will create a new profile in PRODUCTION
  • Risk Level: LOW (empty profile, no scope)
  • Recovery: Profile can be deleted if needed
"""

            if not self.require_production_confirmation(
                "Create Profile",
                f"Creating {args.type} profile: {signed_name}",
                changes_summary,
                args,
            ):
                return 1

        print(f"📱 Creating Empty Profile: {signed_name}")

        # Prepare profile data
        profile_data = {
            (
                "os_x_configuration_profile"
                if args.type == "macos"
                else "mobile_device_configuration_profile"
            ): {
                "general": {
                    "name": signed_name,
                    "description": args.description
                    or f"Configuration profile created by jpapi",
                }
            }
        }

        # Add category if specified
        if args.category:
            profile_data[list(profile_data.keys())[0]]["general"]["category"] = {
                "name": args.category
            }

        # Determine endpoint
        endpoint = (
            "/JSSResource/osxconfigurationprofiles/id/0"
            if args.type == "macos"
            else "/JSSResource/mobiledeviceconfigurationprofiles/id/0"
        )

        # Create profile via API using XML format
        # Extract the inner profile data to avoid double nesting
        profile_key = list(profile_data.keys())[0]
        inner_profile_data = profile_data[profile_key]
        xml_data = self.dict_to_xml(inner_profile_data, profile_key)

        # Debug output removed for production

        response = self.auth.api_request(
            "POST", endpoint, data=xml_data, content_type="xml"
        )

        if response:
            print(f"✅ Empty profile created successfully!")
            print(f"   Name: {signed_name}")
            print(f"   Type: {args.type}")
            if args.description:
                print(f"   Description: {args.description}")
            if args.category:
                print(f"   Category: {args.category}")
            return 0
        else:
            print("❌ Failed to create profile")
            return 1

    def _create_profile_from_json(self, args: Namespace, signed_name: str) -> int:
        """Create a profile from JSON payload"""
        try:
            import json
            import base64

            print(f"📱 Creating Profile from JSON: {signed_name}")

            # Load JSON payload
            with open(args.json_payload, "r") as f:
                payload_data = json.load(f)

            # Create comprehensive summary for production confirmation
            if self.is_production_environment():
                changes_summary = f"""
Profile Creation Summary:
  • Name: {signed_name}
  • Type: {args.type.upper()}
  • Description: {getattr(args, 'description', 'None')}
  • Scope: No computers (null scope) - SAFE DEFAULT
  • Payload: JSON configuration from {args.json_payload}
  • Impact: Will create a new profile in PRODUCTION
  • Risk Level: MEDIUM (contains configuration payload)
  • Recovery: Profile can be deleted if needed
  • Validation: Review payload content before deployment
"""

                if not self.require_production_confirmation(
                    "Create Profile from JSON",
                    f"Creating {args.type} profile: {signed_name}",
                    changes_summary,
                    args,
                ):
                    return 1

            # Prepare profile data with JSON payload
            profile_data = {
                (
                    "os_x_configuration_profile"
                    if args.type == "macos"
                    else "mobile_device_configuration_profile"
                ): {
                    "general": {
                        "name": signed_name,
                        "description": args.description
                        or f"Configuration profile created by jpapi",
                        "distribution_method": "Install Automatically",
                        "user_removable": False,
                        "level": "System",
                        "redeploy_on_update": "Newly Assigned",
                        "payloads": self._convert_json_to_mobileconfig_xml(
                            payload_data
                        ),
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

            # Add category if specified
            if args.category:
                profile_data[list(profile_data.keys())[0]]["general"]["category"] = {
                    "name": args.category
                }

            # Determine endpoint
            endpoint = (
                "/JSSResource/osxconfigurationprofiles/id/0"
                if args.type == "macos"
                else "/JSSResource/mobiledeviceconfigurationprofiles/id/0"
            )

            # Create profile via API using XML format
            xml_data = self.dict_to_xml(profile_data, list(profile_data.keys())[0])
            response = self.auth.api_request(
                "POST", endpoint, data=xml_data, content_type="xml"
            )

            if response:
                print(f"✅ Profile created successfully from JSON!")
                print(f"   Name: {signed_name}")
                print(f"   Type: {args.type}")
                print(f"   Payload: {args.json_payload}")
                return 0
            else:
                print("❌ Failed to create profile from JSON")
                return 1

        except Exception as e:
            print(f"❌ Error creating profile from JSON: {e}")
            return 1

    def _create_profile_from_mobileconfig(
        self, args: Namespace, signed_name: str
    ) -> int:
        """Create a profile from mobileconfig file"""
        try:
            import plistlib
            import base64
            from pathlib import Path

            print(f"📱 Creating Profile from mobileconfig: {signed_name}")

            # Validate mobileconfig file exists
            mobileconfig_path = Path(args.mobileconfig_file)
            if not mobileconfig_path.exists():
                print(f"❌ mobileconfig file not found: {args.mobileconfig_file}")
                return 1

            # Load mobileconfig file
            with open(mobileconfig_path, "rb") as f:
                mobileconfig_data = plistlib.load(f)

            # Create comprehensive summary for production confirmation
            if self.is_production_environment():
                changes_summary = f"""
Profile Creation Summary:
  • Name: {signed_name}
  • Type: {args.type.upper()}
  • Description: {getattr(args, 'description', 'None')}
  • Scope: No computers (null scope) - SAFE DEFAULT
  • Payload: mobileconfig file {args.mobileconfig_file}
  • Impact: Will create a new profile in PRODUCTION
  • Risk Level: MEDIUM (contains configuration payload)
  • Recovery: Profile can be deleted if needed
  • Validation: Review mobileconfig content before deployment
"""

                if not self.require_production_confirmation(
                    "Create Profile from mobileconfig",
                    f"Creating {args.type} profile: {signed_name}",
                    changes_summary,
                    args,
                ):
                    return 1

            # Prepare profile data with mobileconfig payload
            profile_data = {
                (
                    "os_x_configuration_profile"
                    if args.type == "macos"
                    else "mobile_device_configuration_profile"
                ): {
                    "general": {
                        "name": signed_name,
                        "description": args.description
                        or mobileconfig_data.get(
                            "PayloadDescription",
                            "Configuration profile created by jpapi",
                        ),
                        "distribution_method": "Install Automatically",
                        "user_removable": False,
                        "level": "System",
                        "redeploy_on_update": "Newly Assigned",
                        "payloads": self._convert_mobileconfig_to_xml(
                            mobileconfig_data
                        ),
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

            # Add category if specified
            if args.category:
                profile_data[list(profile_data.keys())[0]]["general"]["category"] = {
                    "name": args.category
                }

            # Determine endpoint
            endpoint = (
                "/JSSResource/osxconfigurationprofiles/id/0"
                if args.type == "macos"
                else "/JSSResource/mobiledeviceconfigurationprofiles/id/0"
            )

            # Create profile via API using XML format
            # Extract the inner profile data to avoid double nesting
            profile_key = list(profile_data.keys())[0]
            inner_profile_data = profile_data[profile_key]
            xml_data = self.dict_to_xml(inner_profile_data, profile_key)

            # Debug output removed for production

            response = self.auth.api_request(
                "POST", endpoint, data=xml_data, content_type="xml"
            )

            if response:
                print(f"✅ Profile created successfully from mobileconfig!")
                print(f"   Name: {signed_name}")
                print(f"   Type: {args.type}")
                print(f"   File: {args.mobileconfig_file}")
                return 0
            else:
                print("❌ Failed to create profile from mobileconfig")
                return 1

        except Exception as e:
            print(f"❌ Error creating profile from mobileconfig: {e}")
            return 1

    def _convert_mobileconfig_to_xml(self, mobileconfig_data: dict) -> str:
        """Convert mobileconfig data to XML-escaped string (delegates to service)"""
        return self.profile_converter.mobileconfig_to_xml(mobileconfig_data)

    def _convert_json_to_mobileconfig_xml(self, json_data: dict) -> str:
        """Convert JSON data to mobileconfig XML format (delegates to service)"""
        return self.profile_converter.json_to_mobileconfig_xml(json_data)

    def _create_search(self, args: Namespace) -> int:
        """Create a new search template"""
        try:
            # Add signature to name
            signed_name = add_signature_to_name(args.name)
            print(f"🔍 Creating Search Template: {signed_name}")

            # Prepare search data
            search_data = {
                (
                    "advanced_computer_search"
                    if args.type == "computer"
                    else "advanced_mobile_device_search"
                ): {"name": signed_name}
            }

            # Add criteria if provided
            if args.criteria:
                try:
                    criteria_json = json.loads(args.criteria)
                    search_data[list(search_data.keys())[0]]["criteria"] = criteria_json
                except json.JSONDecodeError:
                    print("❌ Invalid JSON format for criteria")
                    return 1

            # Add display fields if provided
            if args.display_fields:
                fields = [field.strip() for field in args.display_fields.split(",")]
                search_data[list(search_data.keys())[0]]["display_fields"] = fields

            # Determine endpoint
            endpoint = (
                "/JSSResource/advancedcomputersearches/id/0"
                if args.type == "computer"
                else "/JSSResource/advancedmobiledevicesearches/id/0"
            )

            # Create search via API
            response = self.auth.api_request("POST", endpoint, data=search_data)

            if response:
                print(f"✅ Search template created successfully!")
                print(f"   Name: {signed_name}")
                print(f"   Type: {args.type}")
                if args.criteria:
                    print(f"   Criteria: Custom JSON")
                if args.display_fields:
                    print(f"   Display Fields: {args.display_fields}")
                return 0
            else:
                print("❌ Failed to create search template")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _create_group(self, args: Namespace) -> int:
        """Create a new group"""
        try:
            # Add signature to name
            signed_name = add_signature_to_name(args.name)
            print(f"👥 Creating Group: {signed_name}")

            # Prepare group data
            group_data = {
                (
                    "computer_group"
                    if args.type == "computer"
                    else "mobile_device_group"
                ): {"name": signed_name, "is_smart": args.smart}
            }

            # Add criteria for smart groups
            if args.smart and args.criteria:
                try:
                    criteria_json = json.loads(args.criteria)
                    group_data[list(group_data.keys())[0]]["criteria"] = criteria_json
                except json.JSONDecodeError:
                    print("❌ Invalid JSON format for criteria")
                    return 1

            # Determine endpoint
            endpoint = (
                "/JSSResource/computergroups/id/0"
                if args.type == "computer"
                else "/JSSResource/mobiledevicegroups/id/0"
            )

            # Convert group data to XML format for Classic API
            xml_data = self._convert_group_data_to_xml(group_data, args.type)

            # Create group via API using XML format
            response = self.auth.api_request_xml("POST", endpoint, xml_data)

            if response:
                print(f"✅ Group created successfully!")
                print(f"   Name: {signed_name}")
                print(f"   Type: {args.type}")
                print(f"   Smart Group: {args.smart}")
                if args.smart and args.criteria:
                    print(f"   Criteria: Custom JSON")
                return 0
            else:
                print("❌ Failed to create group")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _create_smart_group(self, args: Namespace) -> int:
        """Create a smart group with flexible criteria"""
        try:
            # Production guardrails
            if not args.force and not self.check_destructive_operation(
                "Create Smart Group", args.name
            ):
                return 1

            # Dry-run mode
            if args.dry_run:
                # Add signature to name for dry-run display
                signed_name = add_signature_to_name(args.name)
                print(f"🔍 DRY-RUN: Would create Smart Group: {signed_name}")
                print(f"   Type: {args.type}")
                print(f"   Criteria: {args.criteria}")

                # Parse criteria and show what would be created
                criteria_list = self._parse_criteria(args.criteria)
                if criteria_list:
                    print("   Parsed criteria:")
                    for i, criterion in enumerate(criteria_list):
                        print(f"     {i+1}. {criterion['type']}: {criterion['value']}")

                # Show XML that would be sent
                xml_data = self._create_smart_group_xml_from_criteria(
                    signed_name, criteria_list, args.type
                )
                print("\n   XML that would be sent:")
                print("   " + "\n   ".join(xml_data.split("\n")))

                print(
                    "\n✅ Dry-run complete. Use without --dry-run to actually create the group."
                )
                return 0

            # Add signature to name
            signed_name = add_signature_to_name(args.name)
            print(f"👥 Creating Smart Group: {signed_name}")

            # Parse criteria
            criteria_list = self._parse_criteria(args.criteria)
            if not criteria_list:
                print("❌ No valid criteria provided")
                return 1

            # Check if updating existing group
            is_update = hasattr(args, "id") and args.id is not None

            # If updating, get existing group to preserve name and other fields
            if is_update:
                # Get existing group data using JSON API (more reliable)
                existing_endpoint = (
                    f"/JSSResource/computergroups/id/{args.id}"
                    if args.type == "computer"
                    else f"/JSSResource/mobiledevicegroups/id/{args.id}"
                )
                existing_response = self.auth.api_request("GET", existing_endpoint)

                if not existing_response:
                    print(f"❌ Group with ID {args.id} not found")
                    return 1

                # Extract existing name from response
                group_key = (
                    "computer_group"
                    if args.type == "computer"
                    else "mobile_device_group"
                )
                if group_key in existing_response:
                    existing_group = existing_response[group_key]
                    if "name" in existing_group:
                        signed_name = existing_group["name"]

                print(f"🔄 Updating Smart Group (ID: {args.id}): {signed_name}")

            # Create XML structure for smart group
            xml_data = self._create_smart_group_xml_from_criteria(
                signed_name, criteria_list, args.type
            )

            # Determine endpoint
            if is_update:
                endpoint = (
                    f"/JSSResource/computergroups/id/{args.id}"
                    if args.type == "computer"
                    else f"/JSSResource/mobiledevicegroups/id/{args.id}"
                )
                method = "PUT"
            else:
                endpoint = (
                    "/JSSResource/computergroups/id/0"
                    if args.type == "computer"
                    else "/JSSResource/mobiledevicegroups/id/0"
                )
                method = "POST"

            # Create or update group via API using XML
            response = self.auth.api_request_xml(method, endpoint, xml_data)

            if response and "raw_response" in response:
                # Parse the XML response to get group ID
                import xml.etree.ElementTree as ET

                try:
                    root = ET.fromstring(response["raw_response"])
                    group_id = root.find("id")
                    if group_id is not None:
                        group_id_text = group_id.text

                        action = "updated" if is_update else "created"
                        print(f"✅ Smart group {action} successfully!")
                        print(f"   Name: {signed_name}")
                        print(f"   Type: {args.type}")
                        print(f"   Group ID: {group_id_text}")
                        print(f"   Criteria: {args.criteria}")
                        print(
                            f"   Member Count: Will be calculated based on criteria matching"
                        )

                        return 0
                    else:
                        print("❌ Group created but could not parse group ID")
                        return 1
                except ET.ParseError as e:
                    print(f"❌ Failed to parse group creation response: {e}")
                    return 1
            else:
                print("❌ Failed to create smart group")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _get_group_details(
        self, group_id: str, group_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get group details including member count"""
        try:
            # Determine endpoint based on group type - use the correct JAMF API format
            if group_type == "computer":
                endpoint = f"/JSSResource/computergroups/id/{group_id}"
            else:
                endpoint = f"/JSSResource/mobiledevicegroups/id/{group_id}"

            # Get group details using XML API
            response = self.auth.api_request_xml("GET", endpoint, "")

            if response:
                # Extract member count from response
                if group_type == "computer":
                    computers = response.get("computer_group", {}).get("computers", [])
                    if isinstance(computers, list):
                        member_count = len(computers)
                    else:
                        member_count = 0
                else:
                    mobile_devices = response.get("mobile_device_group", {}).get(
                        "mobile_devices", []
                    )
                    if isinstance(mobile_devices, list):
                        member_count = len(mobile_devices)
                    else:
                        member_count = 0

                return {
                    "member_count": member_count,
                    "group_name": response.get(
                        (
                            "computer_group"
                            if group_type == "computer"
                            else "mobile_device_group"
                        ),
                        {},
                    ).get("name", "Unknown"),
                }

            return None

        except Exception as e:
            print(f"⚠️ Could not fetch group details: {e}")
            return None

    def _convert_group_data_to_xml(
        self, group_data: Dict[str, Any], group_type: str
    ) -> str:
        """Convert group data to XML format for Classic API"""
        import xml.etree.ElementTree as ET

        # Create root element
        if group_type == "computer":
            root = ET.Element("computer_group")
        else:
            root = ET.Element("mobile_device_group")

        # Add basic group information
        group_info = list(group_data.values())[0]

        name_elem = ET.SubElement(root, "name")
        name_elem.text = group_info.get("name", "")

        is_smart_elem = ET.SubElement(root, "is_smart")
        is_smart_elem.text = str(group_info.get("is_smart", False)).lower()

        # Add criteria if present
        if "criteria" in group_info and group_info["criteria"]:
            criteria_elem = ET.SubElement(root, "criteria")
            for criterion in group_info["criteria"]:
                criterion_elem = ET.SubElement(criteria_elem, "criterion")

                name_elem = ET.SubElement(criterion_elem, "name")
                name_elem.text = criterion.get("name", "")

                operator_elem = ET.SubElement(criterion_elem, "operator")
                operator_elem.text = criterion.get("operator", "")

                value_elem = ET.SubElement(criterion_elem, "value")
                value_elem.text = criterion.get("value", "")

        # Convert to XML string
        return ET.tostring(root, encoding="unicode")

    def _parse_criteria(self, criteria_input: str) -> List[Dict[str, str]]:
        """Parse criteria string (delegates to service)"""
        return self.criteria_parser.parse_criteria(criteria_input)

    def _create_smart_group_xml_from_criteria(
        self, name: str, criteria_list: List[Dict[str, str]], group_type: str
    ) -> str:
        """Create XML structure for smart group from criteria list"""
        # Escape XML special characters
        name_escaped = (
            name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

        # Determine the root element based on group type
        root_element = (
            "computer_group" if group_type == "computer" else "mobile_device_group"
        )

        # Build criteria XML
        criteria_xml = ""
        current_priority = 0

        for i, criterion in enumerate(criteria_list):
            criterion_type = criterion["type"]
            criterion_value = criterion["value"]

            # Handle different criterion types
            if criterion_type == "email":
                # Parse email addresses and create separate criteria for each
                emails = self._parse_email_addresses(criterion_value)
                if emails:
                    for j, email in enumerate(emails):
                        # Add @fanduel.com if not already present
                        if "@" not in email:
                            full_email = f"{email}@fanduel.com"
                        else:
                            full_email = email

                        # Use 'or' for subsequent email criteria
                        and_or = "or" if j > 0 else "and"

                        criterion_xml = f"""    <criterion>
      <name>Email Address</name>
      <priority>{current_priority}</priority>
      <and_or>{and_or}</and_or>
      <search_type>like</search_type>
      <value>{full_email}</value>
      <opening_paren>false</opening_paren>
      <closing_paren>false</closing_paren>
    </criterion>"""
                        criteria_xml += criterion_xml + "\n"
                        current_priority += 1
            elif criterion_type == "model":
                # Model criteria
                criterion_xml = f"""    <criterion>
      <name>Model</name>
      <priority>{current_priority}</priority>
      <and_or>and</and_or>
      <search_type>is</search_type>
      <value>{criterion_value}</value>
      <opening_paren>false</opening_paren>
      <closing_paren>false</closing_paren>
    </criterion>"""
                criteria_xml += criterion_xml + "\n"
                current_priority += 1
            elif criterion_type == "os_version":
                # OS version criteria
                criterion_xml = f"""    <criterion>
      <name>Operating System Version</name>
      <priority>{current_priority}</priority>
      <and_or>and</and_or>
      <search_type>is</search_type>
      <value>{criterion_value}</value>
      <opening_paren>false</opening_paren>
      <closing_paren>false</closing_paren>
    </criterion>"""
                criteria_xml += criterion_xml + "\n"
                current_priority += 1
            elif criterion_type == "job_title":
                # Parse job titles and create separate criteria for each with OR logic
                job_titles = self._parse_job_titles(criterion_value)
                if job_titles:
                    for j, job_title in enumerate(job_titles):
                        # Use 'or' for subsequent job title criteria
                        and_or = "or" if j > 0 else "and"

                        # Determine search type: use "like" for wildcard patterns, "is" for exact matches
                        search_type = (
                            "like" if "*" in job_title or "?" in job_title else "is"
                        )

                        # Escape XML special characters in job title value
                        job_title_escaped = (
                            job_title.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                            .replace('"', "&quot;")
                            .replace("'", "&apos;")
                        )

                        # Use "Position" as the field name for job title in computer groups
                        field_name = "Position"

                        criterion_xml = f"""    <criterion>
      <name>{field_name}</name>
      <priority>{current_priority}</priority>
      <and_or>{and_or}</and_or>
      <search_type>{search_type}</search_type>
      <value>{job_title_escaped}</value>
      <opening_paren>false</opening_paren>
      <closing_paren>false</closing_paren>
    </criterion>"""
                        criteria_xml += criterion_xml + "\n"
                        current_priority += 1
            else:
                # Generic criteria
                criterion_xml = f"""    <criterion>
      <name>{criterion_type.title()}</name>
      <priority>{current_priority}</priority>
      <and_or>and</and_or>
      <search_type>is</search_type>
      <value>{criterion_value}</value>
      <opening_paren>false</opening_paren>
      <closing_paren>false</closing_paren>
    </criterion>"""
                criteria_xml += criterion_xml + "\n"
                current_priority += 1

        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<{root_element}>
  <name>{name_escaped}</name>
  <is_smart>true</is_smart>
  <site>
    <id>-1</id>
    <name>NONE</name>
  </site>
  <criteria>
{criteria_xml}  </criteria>
  <computers/>
</{root_element}>"""

        return xml_template

    def _parse_email_addresses(self, emails_input: str) -> List[str]:
        """Parse email addresses (delegates to service)"""
        return self.criteria_parser.parse_email_addresses(emails_input)

    def _parse_job_titles(self, job_titles_input: str) -> List[str]:
        """Parse job titles (delegates to service)"""
        return self.criteria_parser.parse_job_titles(job_titles_input)

    def _create_email_regex_pattern(self, emails: List[str], domain: str) -> str:
        """Create regex pattern for email matching"""
        # Extract usernames from emails
        usernames = []
        for email in emails:
            if "@" in email:
                # Full email address - extract username
                username = email.split("@")[0]
            else:
                # Username only
                username = email

            # Escape special regex characters
            username = username.replace(".", r"\.")
            usernames.append(username)

        if not usernames:
            return ""

        # Create regex pattern: ^(user1|user2|user3)@domain\.com$
        escaped_domain = domain.replace(".", r"\.")
        pattern = f"^({'|'.join(usernames)})@{escaped_domain}$"
        return pattern

    def _create_category_conversational(
        self, name: str, terms: List[str], args: Namespace
    ) -> int:
        """Create category using conversational terms"""
        # Parse priority from terms
        priority = 9  # default
        for term in terms:
            if term.isdigit():
                priority = int(term)
                break

        # Create mock args
        mock_args = Namespace()
        mock_args.name = name
        mock_args.priority = priority
        mock_args.format = getattr(args, "format", "table")
        mock_args.output = getattr(args, "output", None)
        mock_args.force = getattr(args, "force", False)
        mock_args.dry_run = getattr(args, "dry_run", False)

        return self._create_category(mock_args)

    def _create_policy_conversational(
        self, name: str, terms: List[str], args: Namespace
    ) -> int:
        """Create policy using conversational terms"""
        # Parse terms for policy attributes
        category = None
        enabled = False
        frequency = "Ongoing"
        trigger = "Check-in"

        terms_text = " ".join(terms).lower()

        # Look for category
        if "category" in terms_text:
            # Find the word after 'category'
            words = terms_text.split()
            try:
                cat_index = words.index("category")
                if cat_index + 1 < len(words):
                    category = words[cat_index + 1].title()
            except ValueError:
                pass

        # Look for enabled
        if "enabled" in terms_text or "enable" in terms_text:
            enabled = True

        # Look for frequency
        if "once" in terms_text:
            frequency = "Once per computer"
        elif "ongoing" in terms_text:
            frequency = "Ongoing"

        # Look for trigger
        if "startup" in terms_text:
            trigger = "Startup"
        elif "login" in terms_text:
            trigger = "Login"
        elif "logout" in terms_text:
            trigger = "Logout"

        # Create mock args
        mock_args = Namespace()
        mock_args.name = name
        mock_args.category = category
        mock_args.enabled = enabled
        mock_args.frequency = frequency
        mock_args.trigger = trigger
        mock_args.format = getattr(args, "format", "table")
        mock_args.output = getattr(args, "output", None)
        mock_args.force = getattr(args, "force", False)
        mock_args.dry_run = getattr(args, "dry_run", False)

        return self._create_policy(mock_args)

    def _create_search_conversational(
        self, name: str, terms: List[str], args: Namespace
    ) -> int:
        """Create search using conversational terms"""
        # Parse terms for search attributes
        search_type = "computer"  # default

        terms_text = " ".join(terms).lower()

        # Determine search type
        if any(word in terms_text for word in ["mobile", "ios", "ipad", "iphone"]):
            search_type = "mobile"

        # Create mock args
        mock_args = Namespace()
        mock_args.name = name
        mock_args.type = search_type
        mock_args.criteria = None
        mock_args.display_fields = None
        mock_args.format = getattr(args, "format", "table")
        mock_args.output = getattr(args, "output", None)
        mock_args.force = getattr(args, "force", False)
        mock_args.dry_run = getattr(args, "dry_run", False)

        return self._create_search(mock_args)

    def _create_group_conversational(
        self, name: str, terms: List[str], args: Namespace
    ) -> int:
        """Create group using conversational terms"""
        # Parse terms for group attributes
        group_type = "computer"  # default
        smart = False

        terms_text = " ".join(terms).lower()

        # Determine group type
        if any(word in terms_text for word in ["mobile", "ios", "ipad", "iphone"]):
            group_type = "mobile"

        # Determine if smart group
        if "smart" in terms_text:
            smart = True

        # Create mock args
        mock_args = Namespace()
        mock_args.name = name
        mock_args.type = group_type
        mock_args.smart = smart
        mock_args.criteria = None
        mock_args.format = getattr(args, "format", "table")
        mock_args.output = getattr(args, "output", None)
        mock_args.force = getattr(args, "force", False)
        mock_args.dry_run = getattr(args, "dry_run", False)

        return self._create_group(mock_args)

    def _create_extension_attribute(self, args: Namespace) -> int:
        """Create extension attribute with optional script support"""
        try:
            print(f"🔧 Creating {args.attr_type} extension attribute")
            print(f"   Name: {args.name}")

            # Map attribute type to API endpoint
            endpoint_mapping = {
                "computer": "/JSSResource/computerextensionattributes/id/0",
                "mobile": ("/JSSResource/mobiledeviceextensionattributes/id/0"),
                "user": "/JSSResource/userextensionattributes/id/0",
            }

            endpoint = endpoint_mapping.get(args.attr_type)
            if not endpoint:
                print(f"❌ Unknown attribute type: {args.attr_type}")
                return 1

            # Handle script file if provided
            script_contents = None
            input_type = getattr(args, "input_type", "Text Field")

            if hasattr(args, "script_file") and args.script_file:
                from pathlib import Path

                script_path = Path(args.script_file).expanduser()

                if not script_path.exists():
                    print(f"❌ Script file not found: {script_path}")
                    return 1

                print(f"   Script: {script_path.name}")

                try:
                    with open(script_path, "r") as f:
                        script_contents = f.read()
                    input_type = "Script"  # Auto-set to Script type
                    print(f"   Script loaded: {len(script_contents)} bytes")
                except Exception as e:
                    print(f"❌ Failed to read script file: {e}")
                    return 1

            # Build input_type structure
            input_type_data = {"type": input_type}

            # Add script if provided
            if script_contents:
                input_type_data["script"] = script_contents

            # Build extension attribute data
            attr_data = {
                "name": args.name,
                "description": getattr(args, "description", ""),
                "data_type": getattr(args, "data_type", "String"),
                "input_type": input_type_data,
                "enabled": getattr(args, "enabled", True),
                "inventory_display": getattr(
                    args, "inventory_display", "Extension Attributes"
                ),
                "recon_display": getattr(
                    args, "inventory_display", "Extension Attributes"
                ),
            }

            # Convert to XML for Classic API
            import xml.etree.ElementTree as ET

            # Build XML structure based on type
            if args.attr_type == "computer":
                root = ET.Element("computer_extension_attribute")
            elif args.attr_type == "mobile":
                root = ET.Element("mobile_device_extension_attribute")
            else:
                root = ET.Element("user_extension_attribute")

            # Add fields
            ET.SubElement(root, "name").text = attr_data["name"]
            ET.SubElement(root, "description").text = attr_data.get("description", "")
            ET.SubElement(root, "data_type").text = attr_data["data_type"]
            ET.SubElement(root, "enabled").text = str(attr_data["enabled"]).lower()
            ET.SubElement(root, "inventory_display").text = attr_data[
                "inventory_display"
            ]
            ET.SubElement(root, "recon_display").text = attr_data["recon_display"]

            # Add input_type
            input_type_elem = ET.SubElement(root, "input_type")
            ET.SubElement(input_type_elem, "type").text = input_type_data["type"]
            if "script" in input_type_data:
                # Required for script type
                ET.SubElement(input_type_elem, "platform").text = "Mac"
                ET.SubElement(input_type_elem, "script").text = input_type_data[
                    "script"
                ]

            # Convert to XML string
            xml_payload = ET.tostring(root, encoding="unicode", method="xml")

            # Make API request with XML
            print(f"   Endpoint: {endpoint}")
            response = self.auth.api_request(
                "POST", endpoint, data=xml_payload, content_type="xml"
            )

            if response:
                print("✅ Extension attribute created successfully!")
                # Extract ID from response
                ea_id = None
                if (
                    args.attr_type == "computer"
                    and "computer_extension_attribute" in response
                ):
                    ea_id = response["computer_extension_attribute"].get("id")
                elif (
                    args.attr_type == "mobile"
                    and "mobile_device_extension_attribute" in response
                ):
                    ea_id = response["mobile_device_extension_attribute"].get("id")
                elif (
                    args.attr_type == "user" and "user_extension_attribute" in response
                ):
                    ea_id = response["user_extension_attribute"].get("id")
                else:
                    ea_id = response.get("id")

                if ea_id:
                    print(f"   ID: {ea_id}")
                return 0
            else:
                print("❌ Failed to create: No response from API")
                return 1

        except Exception as e:
            print(f"❌ Failed to create extension attribute: {e}")
            import traceback

            traceback.print_exc()
            return 1

    def _configure_signature(self, args: Namespace) -> int:
        """Configure signature settings"""
        try:
            if args.show:
                current_signature = get_user_signature()
                print(f"📝 Current signature: '{current_signature}'")
                print(f"   Example: 'My Policy - {current_signature} 2025.09.12'")
                return 0

            elif args.set:
                if not args.set.strip():
                    print("❌ Signature cannot be empty")
                    return 1

                set_user_signature(args.set)
                print(f"✅ Signature set to: '{args.set}'")
                print(
                    f"   New objects will be named like: 'My Policy - {args.set} 2025.09.12'"
                )
                return 0

            elif args.reset:
                set_user_signature("admin")
                print("✅ Signature reset to default: 'admin'")
                print(
                    "   New objects will be named like: 'My Policy - admin 2025.09.12'"
                )
                return 0

            else:
                print("🔧 Signature Configuration:")
                print()
                print("Usage:")
                print(
                    "   jpapi create signature --show                    # Show current signature"
                )
                print(
                    "   jpapi create signature --set 'jdoe'              # Set signature to 'jdoe'"
                )
                print(
                    "   jpapi create signature --reset                   # Reset to default 'admin'"
                )
                print()
                print("Environment variable:")
                print(
                    "   export JAPIDEV_SIGNATURE='jdoe'                     # Override with env var"
                )
                print()
                print("Configuration file:")
                print(
                    "   ~/.jpapi/signature.json                         # Persistent config"
                )
                return 1

        except Exception as e:
            print(f"❌ Error configuring signature: {e}")
            return 1
