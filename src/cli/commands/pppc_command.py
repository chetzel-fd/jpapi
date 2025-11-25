#!/usr/bin/env python3
"""
PPPC Command - Privacy Preferences Policy Control Scanner
"""

import sys
from pathlib import Path
from typing import Any, List, Optional
from argparse import Namespace

from .common_imports import ArgumentParser, BaseCommand, Namespace

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.pppc_scanner import PPPCScanner, ScanResults

# Try to import ConfigManager, fallback to mock if not available
try:
    from core.config.config_manager import ConfigManager
except ImportError:
    # Mock ConfigManager for standalone usage
    class ConfigManager:
        def __init__(self, environment="sandbox"):
            self.environment = environment


class PPPCCommand(BaseCommand):
    """PPPC Scanner Command"""

    def __init__(self):
        super().__init__("pppc", "Privacy Preferences Policy Control Scanner")

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        subparsers = parser.add_subparsers(dest="pppc_action", help="PPPC actions")

        # Scan command
        scan_parser = subparsers.add_parser(
            "scan", help="Scan applications for PPPC analysis"
        )
        scan_parser.add_argument("--env", default="sandbox", help="Environment to use")
        scan_parser.add_argument(
            "--paths", "-p", action="append", help="Additional paths to scan"
        )
        scan_parser.add_argument("--output", "-o", help="Output directory for reports")
        scan_parser.add_argument(
            "--verbose", "-v", action="store_true", help="Verbose output"
        )
        scan_parser.add_argument(
            "--format",
            default="table",
            choices=["table", "json", "csv"],
            help="Output format",
        )

        # Generate command
        gen_parser = subparsers.add_parser(
            "generate", help="Generate PPPC profile for specific app"
        )
        gen_parser.add_argument("--env", default="sandbox", help="Environment to use")
        gen_parser.add_argument(
            "--app-path", required=True, help="Path to application bundle"
        )
        gen_parser.add_argument("--output", "-o", help="Output path for profile")

        # Analyze command
        analyze_parser = subparsers.add_parser(
            "analyze", help="Analyze existing PPPC profiles"
        )
        analyze_parser.add_argument(
            "--env", default="sandbox", help="Environment to use"
        )
        analyze_parser.add_argument(
            "--profiles-dir", help="Directory containing PPPC profiles"
        )

    def execute(self, args: Namespace) -> int:
        """Execute the PPPC command"""
        if not hasattr(args, "pppc_action") or not args.pppc_action:
            print("❌ Please specify an action: scan, generate, or analyze")
            return 1

        if args.pppc_action == "scan":
            return self._scan_applications(args)
        elif args.pppc_action == "generate":
            return self._generate_profile(args)
        elif args.pppc_action == "analyze":
            return self._analyze_profiles(args)
        else:
            print(f"❌ Unknown action: {args.pppc_action}")
            return 1

    def _scan_applications(self, args: Namespace) -> int:
        """Scan applications for PPPC analysis"""
        try:
            # Initialize scanner
            config_manager = ConfigManager(environment=args.env)
            output_dir = (
                Path(args.output)
                if args.output
                else Path.cwd() / "storage" / "data" / "pppc-profiles"
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            scanner = PPPCScanner(config_manager, str(output_dir))

            print("🔍 Scanning applications for PPPC analysis...")

            # Scan applications
            scan_results = scanner.scan_core_applications(args.paths or [])

            # Generate report
            report_path = (
                output_dir
                / f"pppc_scan_report_{scan_results.scan_timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            )
            scanner.generate_report(scan_results, str(report_path))

            # Generate profiles for non-compliant apps
            profile_count = 0
            for analysis in scan_results.app_analyses:
                if analysis.compliance_status.value in [
                    "NEEDS_IMPROVEMENT",
                    "NON_COMPLIANT",
                ]:
                    profile_path = (
                        output_dir
                        / f"{analysis.app_name.replace(' ', '_')}_pppc.mobileconfig"
                    )
                    if scanner.generate_pppc_profile(analysis, str(profile_path)):
                        profile_count += 1

            # Display results
            self._display_scan_results(scan_results, args.format)

            print(f"\n✅ Scan Complete!")
            print(f"   📊 Report: {report_path}")
            print(f"   📁 Profiles: {profile_count} generated")
            print(f"   📂 Output: {output_dir}")

            return 0

        except Exception as e:
            print(f"❌ Error during scan: {e}")
            return 1

    def _generate_profile(self, args: Namespace) -> int:
        """Generate PPPC profile for specific application"""
        try:
            if not Path(args.app_path).exists():
                print(f"❌ Application not found at {args.app_path}")
                return 1

            # Initialize scanner
            config_manager = ConfigManager(environment=args.env)
            scanner = PPPCScanner(config_manager)

            print(f"🔍 Analyzing application: {args.app_path}")

            # Analyze application
            analysis = scanner._analyze_application(args.app_path)
            if not analysis:
                print(f"❌ Could not analyze application at {args.app_path}")
                return 1

            # Generate profile
            if not args.output:
                args.output = f"{analysis.app_name.replace(' ', '_')}_pppc.mobileconfig"

            if scanner.generate_pppc_profile(analysis, args.output):
                print(f"✅ Generated PPPC profile: {args.output}")
                self._display_app_analysis(analysis)
                return 0
            else:
                print("❌ Failed to generate profile")
                return 1

        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    def _analyze_profiles(self, args: Namespace) -> int:
        """Analyze existing PPPC profiles"""
        try:
            # Initialize scanner
            config_manager = ConfigManager(environment=args.env)
            profiles_dir = args.profiles_dir or str(
                Path.cwd() / "storage" / "data" / "pppc-profiles"
            )
            scanner = PPPCScanner(config_manager, profiles_dir)

            print("🔍 Analyzing existing PPPC profiles...")

            # This would need to be implemented in the scanner
            print("⚠️  Profile analysis not yet implemented")
            return 0

        except Exception as e:
            print(f"❌ Error analyzing profiles: {e}")
            return 1

    def _display_scan_results(self, scan_results: ScanResults, output_format: str):
        """Display scan results"""
        if output_format == "table":
            self._display_scan_results_table(scan_results)
        elif output_format == "json":
            self._display_scan_results_json(scan_results)
        elif output_format == "csv":
            self._display_scan_results_csv(scan_results)

    def _display_scan_results_table(self, scan_results: ScanResults):
        """Display scan results in table format"""
        print(f"\n📊 PPPC Scan Summary")
        print(f"   Total Apps Scanned: {scan_results.total_apps_scanned}")
        print(f"   Compliant Apps: {scan_results.compliant_apps}")
        print(f"   Non-Compliant Apps: {scan_results.non_compliant_apps}")
        print(f"   Scan Duration: {scan_results.scan_duration:.2f}s")

        if scan_results.app_analyses:
            print(f"\n📱 Application Analysis:")
            for analysis in scan_results.app_analyses:
                status_color = (
                    "🟢" if analysis.compliance_status.value == "COMPLIANT" else "🔴"
                )
                print(
                    f"   {status_color} {analysis.app_name} ({analysis.compliance_status.value}) - Risk: {analysis.risk_level}"
                )

    def _display_scan_results_json(self, scan_results: ScanResults):
        """Display scan results in JSON format"""
        import json
        from dataclasses import asdict

        result_dict = {
            "scan_metadata": {
                "timestamp": scan_results.scan_timestamp.isoformat(),
                "total_apps_scanned": scan_results.total_apps_scanned,
                "compliant_apps": scan_results.compliant_apps,
                "non_compliant_apps": scan_results.non_compliant_apps,
                "scan_duration": scan_results.scan_duration,
            },
            "app_analyses": [
                asdict(analysis) for analysis in scan_results.app_analyses
            ],
        }

        print(json.dumps(result_dict, indent=2, default=str))

    def _display_scan_results_csv(self, scan_results: ScanResults):
        """Display scan results in CSV format"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "App Name",
                "Bundle ID",
                "Compliance Status",
                "Risk Level",
                "Missing Permissions Count",
                "Required Permissions",
                "Missing Permissions",
                "Recommendations",
            ]
        )

        # Data
        for analysis in scan_results.app_analyses:
            writer.writerow(
                [
                    analysis.app_name,
                    analysis.bundle_id,
                    analysis.compliance_status.value,
                    analysis.risk_level,
                    len(analysis.missing_permissions),
                    ", ".join(analysis.required_permissions),
                    ", ".join(analysis.missing_permissions),
                    ", ".join(analysis.recommendations),
                ]
            )

        print(output.getvalue())

    def _display_app_analysis(self, analysis):
        """Display analysis for a single application"""
        print(f"\n📱 Analysis for {analysis.app_name}")
        print(f"   Bundle ID: {analysis.bundle_id}")
        print(f"   Compliance: {analysis.compliance_status.value}")
        print(f"   Risk Level: {analysis.risk_level}")

        if analysis.required_permissions:
            print(
                f"   Required Permissions: {', '.join(analysis.required_permissions)}"
            )

        if analysis.missing_permissions:
            print(f"   Missing Permissions: {', '.join(analysis.missing_permissions)}")

        if analysis.recommendations:
            print(f"   Recommendations: {', '.join(analysis.recommendations)}")
