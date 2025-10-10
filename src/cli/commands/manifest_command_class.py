#!/usr/bin/env python3
"""
Manifest Command - Profile Manifests Manager
"""

import sys
from pathlib import Path
from typing import Any, List, Optional
from argparse import Namespace

from .common_imports import ArgumentParser, BaseCommand, Namespace

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.tools.profile_manifests import (
    ProfileManifestManager,
    ManifestResult,
    ManifestInfo,
)

# Try to import ConfigManager, fallback to mock if not available
try:
    from src.core.config.config_manager import ConfigManager
except ImportError:
    # Mock ConfigManager for standalone usage
    class ConfigManager:
        def __init__(self, environment="dev"):
            self.environment = environment


class ManifestCommand(BaseCommand):
    """Profile Manifests Command"""

    def __init__(self):
        super().__init__("manifest", "Profile Manifests Management")

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        subparsers = parser.add_subparsers(
            dest="manifest_action", help="Manifest actions"
        )

        # Update command
        update_parser = subparsers.add_parser(
            "update", help="Update profile manifests from remote sources"
        )
        update_parser.add_argument("--env", default="dev", help="Environment to use")
        update_parser.add_argument(
            "--output", "-o", help="Output directory for manifest data"
        )
        update_parser.add_argument(
            "--types", "-t", action="append", help="Manifest types to update"
        )
        update_parser.add_argument(
            "--verbose", "-v", action="store_true", help="Verbose output"
        )

        # Search command
        search_parser = subparsers.add_parser(
            "search", help="Search for profile manifests"
        )
        search_parser.add_argument("--env", default="dev", help="Environment to use")
        search_parser.add_argument(
            "--search", "-s", required=True, help="Search term for manifests"
        )
        search_parser.add_argument(
            "--types", "-t", action="append", help="Manifest types to search"
        )
        search_parser.add_argument(
            "--format",
            default="table",
            choices=["table", "json", "csv"],
            help="Output format",
        )

        # Details command
        details_parser = subparsers.add_parser(
            "details", help="Get detailed information about a specific manifest"
        )
        details_parser.add_argument("--env", default="dev", help="Environment to use")
        details_parser.add_argument(
            "--bundle-id", required=True, help="Bundle ID to get details for"
        )

        # Report command
        report_parser = subparsers.add_parser(
            "report", help="Generate a comprehensive manifest report"
        )
        report_parser.add_argument("--env", default="dev", help="Environment to use")
        report_parser.add_argument("--output", "-o", help="Output path for the report")

    def execute(self, args: Namespace) -> int:
        """Execute the manifest command"""
        if not hasattr(args, "manifest_action") or not args.manifest_action:
            print("❌ Please specify an action: update, search, details, or report")
            return 1

        if args.manifest_action == "update":
            return self._update_manifests(args)
        elif args.manifest_action == "search":
            return self._search_manifests(args)
        elif args.manifest_action == "details":
            return self._get_manifest_details(args)
        elif args.manifest_action == "report":
            return self._generate_report(args)
        else:
            print(f"❌ Unknown action: {args.manifest_action}")
            return 1

    def _update_manifests(self, args: Namespace) -> int:
        """Update profile manifests from remote sources"""
        try:
            # Initialize manifest manager
            config_manager = ConfigManager(environment=args.env)
            output_dir = (
                Path(args.output)
                if args.output
                else Path.cwd() / "storage" / "data" / "manifest-data"
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            manager = ProfileManifestManager(config_manager, str(output_dir))

            print("🔄 Updating profile manifests...")

            # Update manifests
            manifest_types = args.types if args.types else None
            result = manager.update_manifests(manifest_types)

            if result.success:
                print(f"✅ Manifests updated successfully!")
                print(f"   📊 Total Manifests: {result.manifest_count}")
                print(f"   🔄 Updated: {result.updated_count}")
                print(f"   📂 Output: {output_dir}")
                return 0
            else:
                print(f"❌ Error: {result.error_message}")
                return 1

        except Exception as e:
            print(f"❌ Error updating manifests: {e}")
            return 1

    def _search_manifests(self, args: Namespace) -> int:
        """Search for profile manifests"""
        try:
            # Initialize manifest manager
            config_manager = ConfigManager(environment=args.env)
            manager = ProfileManifestManager(config_manager)

            print(f"🔍 Searching for manifests: '{args.search}'")

            # Search manifests
            manifest_types = args.types if args.types else None
            results = manager.search_manifests(args.search, manifest_types)

            if not results:
                print(f"⚠️  No manifests found for '{args.search}'")
                return 0

            # Display results
            self._display_search_results(results, args.format)
            return 0

        except Exception as e:
            print(f"❌ Error searching manifests: {e}")
            return 1

    def _get_manifest_details(self, args: Namespace) -> int:
        """Get detailed information about a specific manifest"""
        try:
            # Initialize manifest manager
            config_manager = ConfigManager(environment=args.env)
            manager = ProfileManifestManager(config_manager)

            print(f"🔍 Getting details for bundle ID: {args.bundle_id}")

            # Get manifest details
            details = manager.get_manifest_details(args.bundle_id)

            if not details:
                print(f"⚠️  No manifest found for bundle ID: {args.bundle_id}")
                return 0

            # Display details
            self._display_manifest_details(args.bundle_id, details)
            return 0

        except Exception as e:
            print(f"❌ Error getting manifest details: {e}")
            return 1

    def _generate_report(self, args: Namespace) -> int:
        """Generate a comprehensive manifest report"""
        try:
            # Initialize manifest manager
            config_manager = ConfigManager(environment=args.env)
            manager = ProfileManifestManager(config_manager)

            if not args.output:
                args.output = f"manifest_report_{args.env}.json"

            print(f"📊 Generating manifest report...")

            if manager.generate_manifest_report(args.output):
                print(f"✅ Manifest report generated: {args.output}")
                return 0
            else:
                print("❌ Error generating manifest report")
                return 1

        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return 1

    def _display_search_results(self, results: List[ManifestInfo], output_format: str):
        """Display search results"""
        if output_format == "table":
            self._display_search_results_table(results)
        elif output_format == "json":
            self._display_search_results_json(results)
        elif output_format == "csv":
            self._display_search_results_csv(results)

    def _display_search_results_table(self, results: List[ManifestInfo]):
        """Display search results in table format"""
        print(f"\n📋 Found {len(results)} Manifests")
        print(
            f"{'App Name':<30} {'Bundle ID':<40} {'Category':<15} {'Version':<10} {'Enterprise':<10}"
        )
        print("-" * 105)

        for manifest in results:
            enterprise = "Yes" if manifest.is_enterprise else "No"
            print(
                f"{manifest.app_name[:29]:<30} {manifest.bundle_id[:39]:<40} {manifest.category:<15} {manifest.version:<10} {enterprise:<10}"
            )

    def _display_search_results_json(self, results: List[ManifestInfo]):
        """Display search results in JSON format"""
        import json
        from dataclasses import asdict

        result_dict = {
            "search_results": [asdict(manifest) for manifest in results],
            "total_count": len(results),
        }

        print(json.dumps(result_dict, indent=2, default=str))

    def _display_search_results_csv(self, results: List[ManifestInfo]):
        """Display search results in CSV format"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "App Name",
                "Bundle ID",
                "Description",
                "Payload Type",
                "Version",
                "Last Updated",
                "Manifest URL",
                "Is Enterprise",
                "Requires Code Requirement",
                "Requires Bundle ID",
                "Category",
            ]
        )

        # Data
        for manifest in results:
            writer.writerow(
                [
                    manifest.app_name,
                    manifest.bundle_id,
                    manifest.description,
                    manifest.payload_type,
                    manifest.version,
                    manifest.last_updated.isoformat(),
                    manifest.manifest_url,
                    manifest.is_enterprise,
                    manifest.requires_code_requirement,
                    manifest.requires_bundle_id,
                    manifest.category,
                ]
            )

        print(output.getvalue())

    def _display_manifest_details(self, bundle_id: str, details: dict):
        """Display detailed manifest information"""
        print(f"\n📋 Manifest Details for {bundle_id}")
        import json

        print(json.dumps(details, indent=2, default=str))
