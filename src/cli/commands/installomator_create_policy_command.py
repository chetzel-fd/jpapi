#!/usr/bin/env python3
"""
Create Policy Command for Installomator
Creates actual JAMF policies for Installomator apps
"""

import sys
import json
from pathlib import Path
from typing import Any, List, Optional

from .common_imports import ArgumentParser, BaseCommand, Namespace

# Add addons to path for installomator imports
addons_path = Path(__file__).parent.parent.parent / "addons"
sys.path.insert(0, str(addons_path))

from installomator import InstallomatorFactory, PolicyConfig, PolicyType, TriggerType


class InstallomatorCreatePolicyCommand(BaseCommand):
    """Command to create actual JAMF policies for Installomator apps"""

    def __init__(self):
        super().__init__(
            name="installomator-create-policy",
            description="🚀 Create actual JAMF policies for Installomator apps",
        )
        self._setup_patterns()
        self.factory = InstallomatorFactory()

    def _setup_patterns(self):
        """Setup conversational patterns for creating policies"""
        self.add_conversational_pattern(
            pattern="create policy",
            handler="_create_policy",
            description="Create a JAMF policy for an Installomator app",
            aliases=["create", "make policy", "add policy"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        parser.add_argument(
            "app_label",
            help="Installomator label of the app (e.g., 'adobecreativeclouddesktop')",
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
            "--category", default="Productivity", help="Category for the policy"
        )
        parser.add_argument("--description", help="Description for the policy")
        parser.add_argument(
            "--trigger",
            choices=["EVENT", "ENROLLMENT_COMPLETE"],
            default="EVENT",
            help="Trigger for the policy",
        )
        parser.add_argument(
            "--frequency", default="Ongoing", help="Frequency of the policy"
        )
        parser.add_argument(
            "--retry-attempts", type=int, default=3, help="Number of retry attempts"
        )
        parser.add_argument(
            "--notify-on-failure", action="store_true", help="Notify on policy failure"
        )
        parser.add_argument(
            "--output-file", help="Save policy JSON to file instead of creating in JAMF"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without making changes",
        )

    def execute(self, args: Namespace) -> int:
        """Execute the create policy command"""
        try:
            return self._create_policy(args)
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if getattr(args, "verbose", False):
                import traceback

                traceback.print_exc()
            return 1

    def _create_policy(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Create a policy for the specified app"""
        service = self.factory.create_installomator_service()

        # Find the app by label
        apps = service.list_all_apps()
        target_app = None
        for app in apps:
            if app.label == args.app_label:
                target_app = app
                break

        if not target_app:
            print(f"❌ App with label '{args.app_label}' not found!")
            print("\nAvailable apps:")
            for app in apps:
                print(f"   • {app.app_name} ({app.label})")
            return 1

        print(f"🎯 Creating Policy for {target_app.app_name}")
        print("=" * 50)

        # Map policy type
        policy_type_map = {
            "install": PolicyType.INSTALL,
            "daily_update": PolicyType.DAILY_UPDATE,
            "latest_version": PolicyType.LATEST_VERSION,
        }

        policy_type = policy_type_map[args.policy_type]
        policy_name = args.policy_name or f"Install {target_app.app_name}"

        # Map trigger
        trigger_map = {
            "EVENT": TriggerType.EVENT,
            "ENROLLMENT_COMPLETE": TriggerType.ENROLLMENT,
        }
        trigger = trigger_map[args.trigger]

        # Create policy configuration
        config = PolicyConfig(
            app_name=target_app.app_name,
            label=target_app.label,
            policy_name=policy_name,
            policy_type=policy_type,
            trigger=trigger,
            category=args.category,
            description=args.description
            or f"Installomator policy for {target_app.app_name}",
            scope_groups=args.scope_groups,
            frequency=args.frequency,
            retry_attempts=args.retry_attempts,
            notify_on_failure=args.notify_on_failure,
        )

        print(f"App: {config.app_name}")
        print(f"Label: {config.label}")
        print(f"Policy Name: {config.policy_name}")
        print(f"Policy Type: {config.policy_type.value}")
        print(f"Trigger: {config.trigger.value}")
        print(f"Category: {config.category}")
        print(f"Scope Groups: {config.scope_groups}")
        print(f"Frequency: {config.frequency}")
        print(f"Retry Attempts: {config.retry_attempts}")
        print(f"Notify on Failure: {config.notify_on_failure}")

        if args.dry_run:
            print(f"\n🧪 DRY RUN - Policy would be created with these settings")
            return 0

        # Generate JAMF policy JSON
        jamf_policy = config.to_jamf_policy()

        if args.output_file:
            # Save to file
            with open(args.output_file, "w") as f:
                json.dump(jamf_policy, f, indent=2)
            print(f"\n✅ Policy JSON saved to: {args.output_file}")
            return 0

        # Create the policy (simulation for now)
        print(f"\n🚀 Creating policy...")
        result = service.create_policy(config)

        if result.success:
            print(f"✅ Policy created successfully!")
            print(f"   Policy: {result.policy_name}")
            print(f"   ID: {result.policy_id}")

            # Show the JAMF policy JSON
            print(f"\n📄 JAMF Policy JSON:")
            print(json.dumps(jamf_policy, indent=2))

            if result.warnings:
                print(f"\n⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"   • {warning}")
            return 0
        else:
            print(f"❌ Failed to create policy: {result.error_message}")
            return 1
