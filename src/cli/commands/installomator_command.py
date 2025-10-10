#!/usr/bin/env python3
"""
Installomator Command for jpapi CLI
Integrates the SOLID-compliant installomator addon with the main jpapi CLI
"""

import sys
from pathlib import Path
from typing import Any, List, Optional

from .common_imports import ArgumentParser, BaseCommand, Namespace

# Add addons to path for installomator imports
addons_path = Path(__file__).parent.parent.parent / "addons"
sys.path.insert(0, str(addons_path))

from installomator import InstallomatorFactory, PolicyConfig, PolicyType, TriggerType


class InstallomatorCommand(BaseCommand):
    """Installomator command using jpapi's CLI architecture"""

    def __init__(self):
        super().__init__(
            name="installomator",
            description="📱 Installomator policy management with SOLID architecture",
        )
        self._setup_patterns()
        self.factory = InstallomatorFactory()

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
