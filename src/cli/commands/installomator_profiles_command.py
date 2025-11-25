#!/usr/bin/env python3
"""
Installomator Profiles Command
Generates configuration profiles (PPPC, preferences) for Installomator apps
"""

import sys
from pathlib import Path
from typing import Any, List, Optional

from .common_imports import ArgumentParser, BaseCommand, Namespace

# Add addons to path for installomator imports
addons_path = Path(__file__).parent.parent.parent / "addons"
sys.path.insert(0, str(addons_path))

from installomator import InstallomatorFactory
from installomator.profile_generator import InstallomatorProfileGenerator


class InstallomatorProfilesCommand(BaseCommand):
    """Command to generate configuration profiles for Installomator apps"""

    def __init__(self):
        super().__init__(
            name="installomator-profiles",
            description="🔧 Generate configuration profiles for Installomator apps",
        )
        self._setup_patterns()
        self.factory = InstallomatorFactory()
        self.profile_generator = InstallomatorProfileGenerator()

    def _setup_patterns(self):
        """Setup conversational patterns for profile generation"""
        self.add_conversational_pattern(
            pattern="generate profiles",
            handler="_generate_profiles",
            description="Generate configuration profiles for an app",
            aliases=["generate", "create profiles", "make profiles"],
        )
        self.add_conversational_pattern(
            pattern="list supported",
            handler="_list_supported",
            description="List apps with profile support",
            aliases=["supported", "list apps", "available"],
        )
        self.add_conversational_pattern(
            pattern="generate all",
            handler="_generate_all",
            description="Generate profiles for all supported apps",
            aliases=["all", "bulk generate", "mass generate"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        subparsers = parser.add_subparsers(
            dest="profile_action", help="Profile generation actions"
        )

        # Generate profiles command
        generate_parser = subparsers.add_parser(
            "generate", help="Generate profiles for a specific app"
        )
        generate_parser.add_argument(
            "app_label",
            help="Installomator label of the app (e.g., 'adobecreativeclouddesktop')",
        )
        generate_parser.add_argument(
            "--output-dir", help="Output directory for generated profiles"
        )
        generate_parser.add_argument(
            "--pppc-only", action="store_true", help="Generate only PPPC profile"
        )
        generate_parser.add_argument(
            "--preferences-only",
            action="store_true",
            help="Generate only preferences profile",
        )
        generate_parser.add_argument(
            "--combined-only",
            action="store_true",
            help="Generate only combined profile",
        )

        # List supported apps command
        list_parser = subparsers.add_parser(
            "list", help="List apps with profile support"
        )
        list_parser.add_argument(
            "--format",
            choices=["table", "json", "csv"],
            default="table",
            help="Output format",
        )

        # Generate all profiles command
        all_parser = subparsers.add_parser(
            "all", help="Generate profiles for all supported apps"
        )
        all_parser.add_argument(
            "--output-dir", help="Output directory for generated profiles"
        )
        all_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be generated without creating files",
        )

    def execute(self, args: Namespace) -> int:
        """Execute the profiles command"""
        try:
            if not hasattr(args, "profile_action") or not args.profile_action:
                print("❌ Please specify an action: generate, list, or all")
                return 1

            if args.profile_action == "generate":
                return self._generate_profiles(args)
            elif args.profile_action == "list":
                return self._list_supported(args)
            elif args.profile_action == "all":
                return self._generate_all(args)
            else:
                print(f"❌ Unknown action: {args.profile_action}")
                return 1

        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if getattr(args, "verbose", False):
                import traceback

                traceback.print_exc()
            return 1

    def _generate_profiles(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Generate profiles for a specific app"""
        app_info = self.profile_generator.get_app_profile_info(args.app_label)

        if not app_info:
            print(f"❌ No profile mapping found for app: {args.app_label}")
            print("\nSupported apps:")
            for app in self.profile_generator.list_supported_apps():
                print(f"   • {app.app_name} ({app.label})")
            return 1

        print(f"🔧 Generating profiles for {app_info.app_name}")
        print("=" * 60)
        print(f"App: {app_info.app_name}")
        print(f"Label: {app_info.label}")
        print(f"Bundle ID: {app_info.bundle_id}")
        print(f"Category: {app_info.category}")
        print(f"Requires PPPC: {app_info.requires_pppc}")
        print(f"Requires Preferences: {app_info.requires_preferences}")

        if app_info.requires_pppc:
            print(f"PPPC Permissions: {', '.join(app_info.pppc_permissions)}")
        if app_info.requires_preferences:
            print(f"Preference Domains: {', '.join(app_info.preference_domains)}")

        try:
            # Generate profiles
            results = self.profile_generator.generate_profiles_for_app(
                args.app_label, args.output_dir
            )

            print(f"\n✅ Generated {len(results['generated_profiles'])} profiles:")
            for profile in results["generated_profiles"]:
                print(f"   • {profile['type']}: {profile['name']}")
                print(f"     File: {profile['file']}")

            print(f"\n📂 Output directory: {results['output_directory']}")
            return 0

        except Exception as e:
            print(f"❌ Error generating profiles: {e}")
            return 1

    def _list_supported(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List apps with profile support"""
        apps = self.profile_generator.list_supported_apps()

        if not apps:
            print("❌ No apps with profile support found")
            return 1

        print(f"📋 Apps with Profile Support ({len(apps)} total)")
        print("=" * 80)

        if args.format == "table":
            self._display_supported_table(apps)
        elif args.format == "json":
            self._display_supported_json(apps)
        elif args.format == "csv":
            self._display_supported_csv(apps)

        return 0

    def _generate_all(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Generate profiles for all supported apps"""
        if args.dry_run:
            print("🧪 DRY RUN - Would generate profiles for:")
            for app in self.profile_generator.list_supported_apps():
                print(f"   • {app.app_name} ({app.label})")
            return 0

        print("🔧 Generating profiles for all supported apps...")
        print("=" * 60)

        try:
            results = self.profile_generator.generate_all_profiles(args.output_dir)

            print(
                f"✅ Generated profiles for {len(results['generated_profiles'])} apps"
            )
            print(f"📂 Output directory: {results['output_directory']}")

            # Show summary
            total_profiles = sum(
                len(app["generated_profiles"]) for app in results["generated_profiles"]
            )
            print(f"📊 Total profiles created: {total_profiles}")

            return 0

        except Exception as e:
            print(f"❌ Error generating all profiles: {e}")
            return 1

    def _display_supported_table(self, apps: List):
        """Display supported apps in table format"""
        print(
            f"{'App Name':<30} {'Label':<25} {'Bundle ID':<35} {'PPPC':<6} {'Prefs':<6}"
        )
        print("-" * 105)

        for app in apps:
            pppc = "Yes" if app.requires_pppc else "No"
            prefs = "Yes" if app.requires_preferences else "No"
            print(
                f"{app.app_name[:29]:<30} {app.label[:24]:<25} {app.bundle_id[:34]:<35} {pppc:<6} {prefs:<6}"
            )

    def _display_supported_json(self, apps: List):
        """Display supported apps in JSON format"""
        import json
        from dataclasses import asdict

        result_dict = {
            "supported_apps": [asdict(app) for app in apps],
            "total_count": len(apps),
        }

        print(json.dumps(result_dict, indent=2, default=str))

    def _display_supported_csv(self, apps: List):
        """Display supported apps in CSV format"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "App Name",
                "Label",
                "Bundle ID",
                "Category",
                "Requires PPPC",
                "Requires Preferences",
                "PPPC Permissions",
                "Preference Domains",
            ]
        )

        # Data
        for app in apps:
            writer.writerow(
                [
                    app.app_name,
                    app.label,
                    app.bundle_id,
                    app.category,
                    app.requires_pppc,
                    app.requires_preferences,
                    "; ".join(app.pppc_permissions),
                    "; ".join(app.preference_domains),
                ]
            )

        print(output.getvalue())
