#!/usr/bin/env python3
"""
Add App Command for Installomator
Allows easy addition of new apps to the Installomator service
"""

import sys
from pathlib import Path
from typing import Any, List, Optional

from .common_imports import ArgumentParser, BaseCommand, Namespace

# Add addons to path for installomator imports
addons_path = Path(__file__).parent.parent.parent / "addons"
sys.path.insert(0, str(addons_path))

from installomator import InstallomatorFactory, PolicyConfig, PolicyType, TriggerType
from installomator.profile_generator import InstallomatorProfileGenerator


class InstallomatorAddAppCommand(BaseCommand):
    """Command to add new apps to Installomator and create policies"""

    def __init__(self):
        super().__init__(
            name="installomator-add-app",
            description="➕ Add new app to Installomator and create policy",
        )
        self._setup_patterns()
        self.factory = InstallomatorFactory()
        self.profile_generator = InstallomatorProfileGenerator()

    def _setup_patterns(self):
        """Setup conversational patterns for adding apps"""
        self.add_conversational_pattern(
            pattern="add app",
            handler="_add_app",
            description="Add a new app to Installomator",
            aliases=["add", "new app", "create app"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
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
        parser.add_argument(
            "--policy-name",
            help="Name for the policy (defaults to 'Install {app_name}')",
        )
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
        parser.add_argument(
            "--create-policy",
            action="store_true",
            help="Create the policy immediately after adding the app",
        )
        parser.add_argument(
            "--output-file", help="Save policy JSON to file when creating policy"
        )
        parser.add_argument(
            "--generate-profiles",
            action="store_true",
            help="Generate configuration profiles (PPPC, preferences) for the app",
        )
        parser.add_argument(
            "--profile-output-dir", help="Output directory for generated profiles"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def execute(self, args: Namespace) -> int:
        """Execute the add app command"""
        try:
            return self._add_app(args)
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if getattr(args, "verbose", False):
                import traceback

                traceback.print_exc()
            return 1

    def _add_app(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Add a new app to Installomator"""
        app_name = args.app_name
        label = args.label
        description = args.description or f"{app_name} application"
        category = args.category
        policy_name = args.policy_name or f"Install {app_name}"

        print(f"🎯 Adding App to Installomator")
        print("=" * 50)
        print(f"App Name: {app_name}")
        print(f"Label: {label}")
        print(f"Description: {description}")
        print(f"Category: {category}")
        print(f"Policy Name: {policy_name}")

        if args.dry_run:
            print("\n🧪 DRY RUN - No changes will be made")
            return 0

        # Add app to the service
        service = self.factory.create_installomator_service()

        # Check if app already exists
        existing_apps = service.search_apps(app_name.lower())
        for app in existing_apps:
            if app.label == label:
                print(f"\n⚠️  App with label '{label}' already exists!")
                return 1

        # Add the new app to the apps cache
        from addons.installomator.installomator_service import AppInfo

        new_app = AppInfo(
            app_name=app_name, label=label, description=description, category=category
        )

        # This is a temporary addition - in a real implementation,
        # this would be persisted to a database or config file
        service.apps_cache.append(new_app)

        print(f"\n✅ App '{app_name}' added successfully!")
        print(f"   Label: {label}")
        print(f"   Category: {category}")

        if args.create_policy:
            print(f"\n🚀 Creating policy...")
            policy_result = self._create_policy_for_app(args, new_app, service)
            if policy_result != 0:
                return policy_result

        if args.generate_profiles:
            print(f"\n🔧 Generating configuration profiles...")
            profile_result = self._generate_profiles_for_app(args, new_app)
            if profile_result != 0:
                return profile_result

        return 0

    def _create_policy_for_app(self, args: Namespace, app, service) -> int:
        """Create a policy for the specified app"""
        policy_type_map = {
            "install": PolicyType.INSTALL,
            "daily_update": PolicyType.DAILY_UPDATE,
            "latest_version": PolicyType.LATEST_VERSION,
        }

        policy_type = policy_type_map[args.policy_type]
        policy_name = args.policy_name or f"Install {app.app_name}"

        config = PolicyConfig(
            app_name=app.app_name,
            label=app.label,
            policy_name=policy_name,
            policy_type=policy_type,
            trigger=TriggerType.EVENT,
            category=args.category,
            description=f"Installomator policy for {app.app_name}",
            scope_groups=args.scope_groups,
            frequency="Ongoing",
            retry_attempts=3,
            notify_on_failure=True,
        )

        # Generate JAMF policy JSON
        jamf_policy = config.to_jamf_policy()

        if args.output_file:
            # Save to file
            import json

            with open(args.output_file, "w") as f:
                json.dump(jamf_policy, f, indent=2)
            print(f"✅ Policy JSON saved to: {args.output_file}")
            return 0

        result = service.create_policy(config)

        if result.success:
            print(f"✅ Policy created successfully!")
            print(f"   Policy: {result.policy_name}")
            print(f"   ID: {result.policy_id}")
            if result.warnings:
                print(f"\n⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"   • {warning}")
            return 0
        else:
            print(f"❌ Failed to create policy: {result.error_message}")
            return 1

    def _generate_profiles_for_app(self, args: Namespace, app) -> int:
        """Generate configuration profiles for the specified app"""
        try:
            # Check if app has profile mapping
            app_info = self.profile_generator.get_app_profile_info(app.label)

            if not app_info:
                print(f"⚠️  No profile mapping found for {app.app_name} ({app.label})")
                print(
                    "   Profiles will not be generated. Use --generate-profiles to force generation."
                )
                return 0

            # Generate profiles
            results = self.profile_generator.generate_profiles_for_app(
                app.label, args.profile_output_dir
            )

            print(f"✅ Generated {len(results['generated_profiles'])} profiles:")
            for profile in results["generated_profiles"]:
                print(f"   • {profile['type']}: {profile['name']}")
                print(f"     File: {profile['file']}")

            print(f"📂 Profile output: {results['output_directory']}")
            return 0

        except Exception as e:
            print(f"❌ Error generating profiles: {e}")
            return 1
