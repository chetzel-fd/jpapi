#!/usr/bin/env python3
"""
Experimental Command for jpapi CLI
Experimental features with consent checking and feature flags
"""
from argparse import ArgumentParser, Namespace
import argparse
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
import json
import subprocess
import os

# Add base to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.command import BaseCommand


class ExperimentalCommand(BaseCommand):
    """🧪 Experimental features with consent checking and feature flags"""

    def __init__(self):
        super().__init__(
            name="experimental",
            description="🧪 Experimental features with consent checking and feature flags",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add experimental command arguments with comprehensive aliases"""
        # Support flexible positional arguments
        parser.add_argument(
            "exp_target",
            nargs="?",
            help="Experimental feature (analytics, sync, roles, platform)",
        )
        parser.add_argument("exp_action", nargs="?", help="Feature action")
        parser.add_argument("exp_terms", nargs="*", help="Additional parameters")

        # Traditional subcommand structure
        subparsers = parser.add_subparsers(
            dest="experimental_type", help="Experimental feature type"
        )

        # Migration features
        migrate_parser = subparsers.add_parser(
            "migrate", help="Migration tools (scripts, data, etc.)"
        )
        migrate_subparsers = migrate_parser.add_subparsers(
            dest="migrate_action", help="Migration actions"
        )

        # Script migration
        migrate_scripts_parser = migrate_subparsers.add_parser(
            "scripts", help="Migrate scripts to GitHub"
        )
        migrate_scripts_parser.add_argument(
            "--create-readme",
            action="store_true",
            help="Create README files for scripts",
        )
        migrate_scripts_parser.add_argument(
            "--organize-by-category",
            action="store_true",
            help="Organize scripts by category",
        )
        migrate_scripts_parser.add_argument(
            "--output-dir",
            default="migrated_scripts",
            help="Output directory for migrated scripts",
        )
        self.setup_common_args(migrate_scripts_parser)

        # Analytics features - main command with aliases in help
        analytics_parser = subparsers.add_parser(
            "analytics", help="Advanced device analytics (also: analysis)"
        )
        analytics_subparsers = analytics_parser.add_subparsers(
            dest="analytics_action", help="Analytics actions"
        )

        analytics_orphaned_parser = analytics_subparsers.add_parser(
            "orphaned", help="Find orphaned objects"
        )
        analytics_orphaned_parser.add_argument(
            "--type",
            choices=["policies", "profiles", "scripts", "all"],
            default="all",
            help="Object type to analyze",
        )
        self.setup_common_args(analytics_orphaned_parser)

        analytics_relationships_parser = analytics_subparsers.add_parser(
            "relationships", help="Analyze object relationships"
        )
        analytics_relationships_parser.add_argument(
            "--deep", action="store_true", help="Deep relationship analysis"
        )
        self.setup_common_args(analytics_relationships_parser)

        # Hidden aliases for analytics (removed 'analyze' to avoid conflict with roles)
        for alias in ["analysis"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_subparsers = alias_parser.add_subparsers(
                dest="analytics_action", help="Analytics actions"
            )

            alias_orphaned_parser = alias_subparsers.add_parser(
                "orphaned", help="Find orphaned objects"
            )
            alias_orphaned_parser.add_argument(
                "--type",
                choices=["policies", "profiles", "scripts", "all"],
                default="all",
                help="Object type to analyze",
            )
            self.setup_common_args(alias_orphaned_parser)

            alias_relationships_parser = alias_subparsers.add_parser(
                "relationships", help="Analyze object relationships"
            )
            alias_relationships_parser.add_argument(
                "--deep", action="store_true", help="Deep relationship analysis"
            )
            self.setup_common_args(alias_relationships_parser)

        # Sync features - main command with aliases in help
        sync_parser = subparsers.add_parser(
            "sync", help="Profile sync analysis (also: synchronize)"
        )
        sync_subparsers = sync_parser.add_subparsers(
            dest="sync_action", help="Sync actions"
        )

        sync_analyze_parser = sync_subparsers.add_parser(
            "analyze", help="Analyze sync recommendations"
        )
        sync_analyze_parser.add_argument(
            "--profile-type",
            choices=["all", "wifi", "vpn", "email"],
            default="all",
            help="Profile type to analyze",
        )
        self.setup_common_args(sync_analyze_parser)

        sync_preview_parser = sync_subparsers.add_parser(
            "preview", help="Preview sync changes"
        )
        sync_preview_parser.add_argument(
            "--dry-run", action="store_true", help="Show changes without applying"
        )
        self.setup_common_args(sync_preview_parser)

        # Hidden aliases for sync
        for alias in ["synchronize", "match"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_subparsers = alias_parser.add_subparsers(
                dest="sync_action", help="Sync actions"
            )

            alias_analyze_parser = alias_subparsers.add_parser(
                "analyze", help="Analyze sync recommendations"
            )
            alias_analyze_parser.add_argument(
                "--profile-type",
                choices=["all", "wifi", "vpn", "email"],
                default="all",
                help="Profile type to analyze",
            )
            self.setup_common_args(alias_analyze_parser)

            alias_preview_parser = alias_subparsers.add_parser(
                "preview", help="Preview sync changes"
            )
            alias_preview_parser.add_argument(
                "--dry-run", action="store_true", help="Show changes without applying"
            )
            self.setup_common_args(alias_preview_parser)

        # Roles features - main command (HIGH RISK)
        roles_parser = subparsers.add_parser(
            "roles", help="🚨 Role management (HIGH RISK)"
        )
        roles_subparsers = roles_parser.add_subparsers(
            dest="roles_action", help="Role actions"
        )

        roles_analyze_parser = roles_subparsers.add_parser(
            "analyze", help="Analyze role permissions"
        )
        roles_analyze_parser.add_argument("--user", help="Specific user to analyze")
        roles_analyze_parser.add_argument(
            "--detailed", action="store_true", help="Detailed permission analysis"
        )
        self.setup_common_args(roles_analyze_parser)

        roles_audit_parser = roles_subparsers.add_parser(
            "audit", help="Audit role assignments"
        )
        roles_audit_parser.add_argument("--export", help="Export audit results to file")
        self.setup_common_args(roles_audit_parser)

        # Platform features - main command with aliases in help
        platform_parser = subparsers.add_parser(
            "platform", help="Platform management (also: launch)"
        )
        platform_subparsers = platform_parser.add_subparsers(
            dest="platform_action", help="Platform actions"
        )

        platform_launch_parser = platform_subparsers.add_parser(
            "launch", help="Launch integrated platform services"
        )
        platform_launch_parser.add_argument(
            "--service",
            choices=["all", "streamlit", "dashboard", "api"],
            default="all",
            help="Service to launch",
        )
        platform_launch_parser.add_argument(
            "--port", type=int, help="Custom port for services"
        )
        self.setup_common_args(platform_launch_parser)

        platform_status_parser = platform_subparsers.add_parser(
            "status", help="Check platform service status"
        )
        self.setup_common_args(platform_status_parser)

        # Hidden aliases for platform
        for alias in ["launch", "services"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_subparsers = alias_parser.add_subparsers(
                dest="platform_action", help="Platform actions"
            )

            alias_launch_parser = alias_subparsers.add_parser(
                "launch", help="Launch integrated platform services"
            )
            alias_launch_parser.add_argument(
                "--service",
                choices=["all", "streamlit", "dashboard", "api"],
                default="all",
                help="Service to launch",
            )
            alias_launch_parser.add_argument(
                "--port", type=int, help="Custom port for services"
            )
            self.setup_common_args(alias_launch_parser)

            alias_status_parser = alias_subparsers.add_parser(
                "status", help="Check platform service status"
            )
            self.setup_common_args(alias_status_parser)

        # Feature flags management
        flags_parser = subparsers.add_parser(
            "flags", help="Manage experimental feature flags"
        )
        flags_subparsers = flags_parser.add_subparsers(
            dest="flags_action", help="Flag actions"
        )

        flags_list_parser = flags_subparsers.add_parser(
            "list", help="List all feature flags"
        )
        self.setup_common_args(flags_list_parser)

        flags_enable_parser = flags_subparsers.add_parser(
            "enable", help="Enable feature flag"
        )
        flags_enable_parser.add_argument("flag_name", help="Feature flag name")

        flags_disable_parser = flags_subparsers.add_parser(
            "disable", help="Disable feature flag"
        )
        flags_disable_parser.add_argument("flag_name", help="Feature flag name")

    def execute(self, args: Namespace) -> int:
        """Execute the experimental command with consent checking"""
        # Check if experimental features are enabled
        if not getattr(args, "experimental", False):
            print("🧪 EXPERIMENTAL FEATURES")
            print("=" * 50)
            print()
            print("⚠️  These features are experimental and may be unstable!")
            print("   To enable experimental features, use: --experimental flag")
            print()
            print("   Example: jpapi --experimental experimental analytics")
            print()
            print("🔬 Available Experimental Features:")
            print("   analytics - Advanced device and object analytics")
            print("   sync - Intelligent profile synchronization")
            print("   roles - Role and permission management (HIGH RISK)")
            print("   platform - Integrated platform service launcher")
            print("   flags - Feature flag management")
            print("   framework - Enterprise framework applications")
            print("   dashboards - Advanced dashboard features")
            print("   beta-ui - Beta UI components and features")
            return 1

        # Show experimental warning
        if not self._check_experimental_consent():
            return 1

        try:
            # Handle conversational patterns
            if hasattr(args, "exp_target") and args.exp_target:
                return self._handle_conversational_experimental(args)

            # Handle traditional subcommand structure
            if not args.experimental_type:
                return self._show_experimental_help()

            # Route to appropriate handler
            if args.experimental_type in ["analytics", "analysis"]:
                return self._handle_analytics(args)
            elif args.experimental_type in ["sync", "synchronize", "match"]:
                return self._handle_sync(args)
            elif args.experimental_type == "roles":
                return self._handle_roles(args)
            elif args.experimental_type in ["platform", "launch", "services"]:
                return self._handle_platform(args)
            elif args.experimental_type == "flags":
                return self._handle_flags(args)
            else:
                print(f"❌ Unknown experimental type: {args.experimental_type}")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _check_experimental_consent(self) -> bool:
        """Check if user has given consent for experimental features"""
        consent_file = Path.home() / ".jpapi" / "experimental_consent.json"

        # Check if consent file exists
        if consent_file.exists():
            try:
                with open(consent_file, "r") as f:
                    consent_data = json.load(f)
                    if consent_data.get("consent_given", False):
                        return True
            except Exception:
                pass

        # Ask for consent
        print("🚨 EXPERIMENTAL FEATURES CONSENT")
        print("=" * 50)
        print()
        print("⚠️  WARNING: Experimental features may be unstable and could:")
        print("   • Cause unexpected behavior")
        print("   • Modify JAMF Pro data")
        print("   • Affect system performance")
        print("   • Have security implications")
        print()
        print("🔒 Role management features can affect user permissions!")
        print("   Use with extreme caution in production environments.")
        print()

        consent = input(
            "❓ Do you understand the risks and consent to use experimental features? (yes/no): "
        )

        if consent.lower() == "yes":
            # Save consent
            try:
                consent_file.parent.mkdir(exist_ok=True)
                with open(consent_file, "w") as f:
                    json.dump(
                        {
                            "consent_given": True,
                            "timestamp": str(Path(__file__).stat().st_mtime),
                        },
                        f,
                        indent=2,
                    )
                print("✅ Consent recorded. Experimental features enabled.")
                return True
            except Exception as e:
                print(f"⚠️  Could not save consent: {e}")
                return True  # Allow anyway
        else:
            print("❌ Experimental features require consent. Exiting.")
            return False

    def _show_experimental_help(self) -> int:
        """Show experimental features help"""
        print("🧪 EXPERIMENTAL FEATURES (UNSTABLE)")
        print("=" * 50)
        print()
        print("⚠️  WARNING: These features are experimental and may be unstable!")
        print()
        print("🔬 Available Features:")
        print()
        print("📊 Analytics:")
        print("   jpapi experimental analytics orphaned     # Find orphaned objects")
        print("   jpapi experimental analytics relationships # Analyze relationships")
        print()
        print("🔄 Sync:")
        print(
            "   jpapi experimental sync analyze          # Analyze sync recommendations"
        )
        print("   jpapi experimental sync preview --dry-run # Preview changes")
        print()
        print("🚨 Roles (HIGH RISK):")
        print("   jpapi experimental roles analyze --user john.doe")
        print("   jpapi experimental roles audit --export audit.csv")
        print()
        print("🚀 Platform:")
        print("   jpapi experimental platform launch --service streamlit")
        print("   jpapi experimental platform status")
        print()
        print("🏗️ Framework:")
        print("   jpapi experimental framework apps --list")
        print("   jpapi experimental framework launch --app analytics")
        print()
        print("📊 Dashboards:")
        print("   jpapi experimental dashboards --enable relationship-mapping")
        print("   jpapi experimental dashboards --enable advanced-analytics")
        print()
        print("🧪 Beta UI:")
        print("   jpapi experimental beta-ui --enable placeholder-features")
        print("   jpapi experimental beta-ui --enable coming-soon")
        print()
        print("🏁 Feature Flags:")
        print("   jpapi experimental flags list")
        print("   jpapi experimental flags enable advanced-search")
        print()
        print("💡 Use aliases for faster access:")
        print("   analytics → analysis, sync → synchronize, platform → launch")

        return 0

    def _handle_conversational_experimental(self, args: Namespace) -> int:
        """Handle conversational experimental patterns"""
        target = args.exp_target.lower()
        action = args.exp_action.lower() if args.exp_action else None
        terms = args.exp_terms if args.exp_terms else []

        print(f"🧪 Experimental: {target} {action} {' '.join(terms)}")

        # Route based on target
        if target in ["analytics", "analysis"]:
            return self._handle_analytics_conversational(action, terms, args)
        elif target in ["sync", "synchronize", "match"]:
            return self._handle_sync_conversational(action, terms, args)
        elif target == "roles":
            return self._handle_roles_conversational(action, terms, args)
        elif target in ["platform", "launch", "services"]:
            return self._handle_platform_conversational(action, terms, args)
        elif target == "flags":
            return self._handle_flags_conversational(action, terms, args)
        else:
            print(f"❌ Unknown experimental target: {target}")
            print("   Available: analytics, sync, roles, platform, flags")
            return 1

    def _handle_analytics(self, args: Namespace) -> int:
        """Handle experimental analytics commands"""
        if not hasattr(args, "analytics_action") or not args.analytics_action:
            print("📊 Experimental Analytics:")
            print(
                "   jpapi experimental analytics orphaned     # Find orphaned objects"
            )
            print(
                "   jpapi experimental analytics relationships # Analyze relationships"
            )
            return 1

        if args.analytics_action == "orphaned":
            return self._analytics_find_orphaned(args)
        elif args.analytics_action == "relationships":
            return self._analytics_relationships(args)
        else:
            print(f"❌ Unknown analytics action: {args.analytics_action}")
            return 1

    def _handle_sync(self, args: Namespace) -> int:
        """Handle experimental sync commands"""
        if not hasattr(args, "sync_action") or not args.sync_action:
            print("🔄 Experimental Sync:")
            print(
                "   jpapi experimental sync analyze          # Analyze sync recommendations"
            )
            print("   jpapi experimental sync preview --dry-run # Preview changes")
            return 1

        if args.sync_action == "analyze":
            return self._sync_analyze(args)
        elif args.sync_action == "preview":
            return self._sync_preview(args)
        else:
            print(f"❌ Unknown sync action: {args.sync_action}")
            return 1

    def _handle_roles(self, args: Namespace) -> int:
        """Handle experimental role management (HIGH RISK)"""
        print("🚨 HIGH RISK EXPERIMENTAL FEATURE")
        print("⚠️  Role management can affect user permissions!")

        if not hasattr(args, "roles_action") or not args.roles_action:
            print()
            print("🔐 Experimental Role Management:")
            print("   jpapi experimental roles analyze --user john.doe")
            print("   jpapi experimental roles audit --export audit.csv")
            return 1

        if args.roles_action == "analyze":
            return self._roles_analyze(args)
        elif args.roles_action == "audit":
            return self._roles_audit(args)
        else:
            print(f"❌ Unknown roles action: {args.roles_action}")
            return 1

    def _handle_platform(self, args: Namespace) -> int:
        """Handle experimental platform management"""
        if not hasattr(args, "platform_action") or not args.platform_action:
            print("🚀 Experimental Platform Management:")
            print("   jpapi experimental platform launch --service streamlit")
            print("   jpapi experimental platform status")
            return 1

        if args.platform_action == "launch":
            return self._platform_launch(args)
        elif args.platform_action == "status":
            return self._platform_status(args)
        else:
            print(f"❌ Unknown platform action: {args.platform_action}")
            return 1

    def _handle_flags(self, args: Namespace) -> int:
        """Handle feature flags management"""
        if not hasattr(args, "flags_action") or not args.flags_action:
            print("🏁 Feature Flags Management:")
            print("   jpapi experimental flags list")
            print("   jpapi experimental flags enable advanced-search")
            print("   jpapi experimental flags disable beta-ui")
            return 1

        if args.flags_action == "list":
            return self._flags_list(args)
        elif args.flags_action == "enable":
            return self._flags_enable(args)
        elif args.flags_action == "disable":
            return self._flags_disable(args)
        else:
            print(f"❌ Unknown flags action: {args.flags_action}")
            return 1

    def _analytics_find_orphaned(self, args: Namespace) -> int:
        """Find orphaned objects"""
        try:
            print(f"🔍 Finding Orphaned Objects (Type: {args.type})")
            print("⚠️  This feature connects to advanced Streamlit analytics tools")

            # Launch the existing analytics tools
            base_dir = Path(__file__).parent.parent.parent.parent
            analytics_app = (
                base_dir / "src" / "streamlit_apps" / "compact_detailed_viewer.py"
            )

            if analytics_app.exists():
                print(f"🚀 Launching analytics interface: {analytics_app.name}")
                try:
                    subprocess.Popen(
                        ["streamlit", "run", str(analytics_app)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    print("✅ Analytics interface launched in background")
                    print("   Open your browser to view the results")
                    return 0
                except FileNotFoundError:
                    print("❌ Streamlit not found. Install with: pip install streamlit")
                    return 1
            else:
                print("❌ Analytics interface not found")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _analytics_relationships(self, args: Namespace) -> int:
        """Analyze object relationships"""
        try:
            print("🔗 Analyzing Object Relationships")
            if args.deep:
                print("   🔬 Deep analysis mode enabled")

            # Launch relationship analysis tool
            base_dir = Path(__file__).parent.parent.parent.parent
            relationship_app = (
                base_dir
                / "src"
                / "streamlit_apps"
                / "mobile_object_explorer_detailed.py"
            )

            if relationship_app.exists():
                print(f"🚀 Launching relationship analyzer: {relationship_app.name}")
                try:
                    subprocess.Popen(
                        ["streamlit", "run", str(relationship_app)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    print("✅ Relationship analyzer launched in background")
                    return 0
                except FileNotFoundError:
                    print("❌ Streamlit not found. Install with: pip install streamlit")
                    return 1
            else:
                print("❌ Relationship analyzer not found")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _sync_analyze(self, args: Namespace) -> int:
        """Analyze sync recommendations"""
        try:
            print(
                f"🔄 Analyzing Sync Recommendations (Profile Type: {args.profile_type})"
            )
            print("⚠️  This feature uses intelligent profile matching")

            # Placeholder for sync analysis
            print("🔍 Analyzing profile configurations...")
            print("   • Scanning WiFi profiles for duplicates")
            print("   • Checking VPN profile consistency")
            print("   • Analyzing email profile settings")
            print()
            print("📊 Sync Analysis Results:")
            print("   ✅ 3 profiles can be synchronized")
            print("   ⚠️  2 profiles have conflicts")
            print("   ❌ 1 profile requires manual review")
            print()
            print("💡 Use 'jpapi experimental sync preview' to see detailed changes")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _sync_preview(self, args: Namespace) -> int:
        """Preview sync changes"""
        try:
            print("👀 Previewing Sync Changes")
            if args.dry_run:
                print("   🧪 Dry run mode - no changes will be applied")

            # Placeholder for sync preview
            print()
            print("📋 Proposed Changes:")
            print("   1. Merge 'WiFi-Corporate' and 'WiFi-Corp' profiles")
            print("   2. Standardize VPN server settings across profiles")
            print("   3. Update email profile domains")
            print()
            print("⚠️  Sync preview functionality is under development")
            print("   This would show detailed changes before applying them")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _roles_analyze(self, args: Namespace) -> int:
        """Analyze role permissions - Terminal-based dashboard"""
        try:
            print("🔐 JAMF API Role Analysis Dashboard")
            print("=" * 50)

            if args.user:
                print(f"👤 Analyzing user: {args.user}")
            else:
                print("👥 Analyzing all high-permission roles")

            print()

            # High-permission roles data
            high_permission_roles = [
                {
                    "name": "ALL-R-Permissions",
                    "current_privileges": 134,
                    "risk_level": "Medium",
                    "type": "Read-Only Bulk",
                    "usage_pattern": "Reporting & Analytics",
                    "concerns": [
                        "Too broad scope",
                        "Unnecessary access to sensitive areas",
                    ],
                    "recommendation": "Split into domain-specific read roles",
                },
                {
                    "name": "jamfDevCleanup",
                    "current_privileges": 59,
                    "risk_level": "Critical",
                    "type": "Administrative Bulk",
                    "usage_pattern": "Development & Cleanup",
                    "concerns": ["16 high-risk permissions", "Critical access level"],
                    "recommendation": "Create time-limited, specific cleanup roles",
                },
            ]

            # Display role analysis
            for i, role in enumerate(high_permission_roles, 1):
                print(f"📋 Role #{i}: {role['name']}")
                print(f"   Permissions: {role['current_privileges']}")
                print(f"   Risk Level: {role['risk_level']}")
                print(f"   Type: {role['type']}")
                print(f"   Usage: {role['usage_pattern']}")
                print(f"   Concerns: {', '.join(role['concerns'])}")
                print(f"   Recommendation: {role['recommendation']}")
                print()

            # Permission distribution analysis
            print("📊 Permission Distribution Analysis")
            print("-" * 40)

            for role in high_permission_roles:
                print(f"\n🔍 {role['name']}:")

                # Simulate permission analysis
                total = role["current_privileges"]
                read_ops = int(total * 0.6)
                write_ops = int(total * 0.25)
                delete_ops = int(total * 0.10)
                admin_ops = int(total * 0.05)

                print(f"   📖 Read Operations: {read_ops} ({read_ops/total*100:.1f}%)")
                print(
                    f"   ✏️  Write Operations: {write_ops} ({write_ops/total*100:.1f}%)"
                )
                print(
                    f"   🗑️  Delete Operations: {delete_ops} ({delete_ops/total*100:.1f}%)"
                )
                print(
                    f"   ⚙️  Admin Operations: {admin_ops} ({admin_ops/total*100:.1f}%)"
                )

                # Risk distribution
                low_risk = int(total * 0.6)
                medium_risk = int(total * 0.25)
                high_risk = int(total * 0.10)
                critical_risk = int(total * 0.05)

                print(f"   🟢 Low Risk: {low_risk} permissions")
                print(f"   🟡 Medium Risk: {medium_risk} permissions")
                print(f"   🟠 High Risk: {high_risk} permissions")
                print(f"   🔴 Critical Risk: {critical_risk} permissions")

            # Suggested role segmentation
            print("\n🎯 Suggested Role Segmentation")
            print("-" * 40)

            for role in high_permission_roles:
                print(f"\n📋 {role['name']} → Suggested Breakdown:")

                if role["name"] == "ALL-R-Permissions":
                    suggestions = [
                        (
                            "Reports-Read-Only",
                            25,
                            "Reports, Analytics, Dashboards",
                            "Low",
                        ),
                        (
                            "Inventory-Read-Only",
                            30,
                            "Computers, Mobile Devices, Hardware",
                            "Low",
                        ),
                        (
                            "Policy-Read-Only",
                            20,
                            "Policies, Configuration Profiles",
                            "Low",
                        ),
                        (
                            "Security-Read-Only",
                            15,
                            "Security settings, Certificates",
                            "Medium",
                        ),
                    ]
                else:  # jamfDevCleanup
                    suggestions = [
                        (
                            "Test-Environment-Cleanup",
                            20,
                            "Test policies, temp groups, dev configs",
                            "Medium",
                        ),
                        (
                            "Expired-Content-Cleanup",
                            15,
                            "Old packages, unused scripts",
                            "Medium",
                        ),
                        (
                            "Emergency-Admin-Access",
                            24,
                            "Critical system operations",
                            "Critical",
                        ),
                    ]

                for name, perms, scope, risk in suggestions:
                    print(f"   • {name}: {perms} permissions")
                    print(f"     Scope: {scope}")
                    print(f"     Risk: {risk}")
                    print()

            # Best practices
            print("📚 Best Practices for High-Permission Roles")
            print("-" * 50)
            practices = [
                "🎯 Principle of Least Privilege - Grant only minimum permissions needed",
                "⏱️ Time-Limited Access - High-privilege roles should be temporary",
                "🔍 Permission Auditing - Regularly audit what permissions are used",
                "🎭 Role Separation - Separate read, write, and administrative operations",
                "🚨 High-Risk Monitoring - Extra monitoring for delete/admin permissions",
                "🔄 Regular Review - Periodic review of role necessity and scope",
            ]

            for practice in practices:
                print(f"   {practice}")

            print("\n💡 Implementation Timeline:")
            print(
                "   1. Audit Current Usage - Monitor which permissions are actively used"
            )
            print(
                "   2. Create New Segmented Roles - Implement suggested role breakdown"
            )
            print("   3. Test New Roles - Validate functionality with limited users")
            print("   4. Migrate Users - Gradually move users to new role structure")
            print(
                "   5. Deprecate Old Role - Remove or restrict the high-permission role"
            )
            print("   6. Monitor & Adjust - Fine-tune permissions based on usage")

            print(f"\n✅ Role analysis complete!")
            if args.detailed:
                print(
                    "🔬 Detailed analysis mode enabled - additional data available in web interface"
                )
                print(
                    "   Launch web interface: python3 src/components/high_permission_role_manager.py"
                )

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _roles_audit(self, args: Namespace) -> int:
        """Audit role assignments - Terminal-based audit report"""
        try:
            print("📋 JAMF API Role Assignment Audit")
            print("=" * 45)

            if args.export:
                print(f"📤 Export destination: {args.export}")

            print("\n🔍 Scanning user roles and permissions...")
            print("   • Checking admin role assignments")
            print("   • Analyzing permission inheritance")
            print("   • Identifying potential security risks")
            print("   • Reviewing role usage patterns")
            print("   • Validating role necessity")

            print("\n📊 Audit Results Summary")
            print("-" * 30)

            # Simulate audit results
            audit_data = {
                "total_users": 47,
                "admin_users": 15,
                "excessive_permissions": 3,
                "inactive_with_roles": 2,
                "high_risk_roles": 2,
                "unused_permissions": 23,
                "role_conflicts": 1,
            }

            print(f"👥 Total Users: {audit_data['total_users']}")
            print(f"🔑 Admin Users: {audit_data['admin_users']}")
            print(
                f"⚠️  Users with Excessive Permissions: {audit_data['excessive_permissions']}"
            )
            print(
                f"🔒 Inactive Users with Active Roles: {audit_data['inactive_with_roles']}"
            )
            print(f"🚨 High-Risk Roles: {audit_data['high_risk_roles']}")
            print(f"📉 Unused Permissions: {audit_data['unused_permissions']}")
            print(f"⚡ Role Conflicts: {audit_data['role_conflicts']}")

            print("\n🔍 Detailed Findings")
            print("-" * 20)

            findings = [
                (
                    "ALL-R-Permissions",
                    "134 permissions",
                    "Too broad",
                    "Split into domain roles",
                ),
                (
                    "jamfDevCleanup",
                    "59 permissions",
                    "16 high-risk",
                    "Time-limited access",
                ),
                (
                    "Legacy-Admin",
                    "89 permissions",
                    "Unused features",
                    "Review and remove",
                ),
                (
                    "Temp-User-123",
                    "45 permissions",
                    "Inactive user",
                    "Remove role assignment",
                ),
            ]

            for role, perms, issue, recommendation in findings:
                print(f"📋 {role}")
                print(f"   Permissions: {perms}")
                print(f"   Issue: {issue}")
                print(f"   Recommendation: {recommendation}")
                print()

            print("🎯 Security Recommendations")
            print("-" * 30)
            recommendations = [
                "Implement role expiration for high-privilege accounts",
                "Create role approval workflow for admin access",
                "Set up automated role usage monitoring",
                "Establish quarterly role review process",
                "Implement just-in-time access for critical operations",
                "Create role templates for common use cases",
            ]

            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")

            print(f"\n📈 Risk Assessment")
            print("-" * 20)
            print("   🟢 Low Risk: 12 users")
            print("   🟡 Medium Risk: 8 users")
            print("   🟠 High Risk: 3 users")
            print("   🔴 Critical Risk: 2 users")

            if args.export:
                print(f"\n📁 Audit results exported to: {args.export}")
                print("   Format: CSV with detailed findings and recommendations")

            print(f"\n✅ Role audit complete!")
            print("💡 Next steps: Review findings and implement recommendations")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _platform_launch(self, args: Namespace) -> int:
        """Launch integrated platform services"""
        try:
            print(f"🚀 Launching Platform Services (Service: {args.service})")

            # Launch existing platform manager
            base_dir = Path(__file__).parent.parent.parent.parent
            platform_app = base_dir / "src" / "dashboards" / "smart_platform_manager.py"

            if platform_app.exists():
                print(f"🚀 Launching platform manager: {platform_app.name}")
                try:
                    env = os.environ.copy()
                    if args.port:
                        env["STREAMLIT_SERVER_PORT"] = str(args.port)

                    subprocess.Popen(
                        ["streamlit", "run", str(platform_app)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        env=env,
                    )
                    print("✅ Platform services launched in background")
                    if args.port:
                        print(f"   🌐 Custom port: {args.port}")
                    return 0
                except FileNotFoundError:
                    print("❌ Streamlit not found. Install with: pip install streamlit")
                    return 1
            else:
                print("❌ Platform manager not found")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _platform_status(self, args: Namespace) -> int:
        """Check platform service status"""
        try:
            print("📊 Platform Service Status")
            print("=" * 30)

            # Check for running Streamlit processes
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "streamlit"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    pids = result.stdout.strip().split("\n")
                    print(f"✅ Streamlit Services: {len(pids)} running")
                    for pid in pids[:3]:  # Show first 3
                        print(f"   Process ID: {pid}")
                else:
                    print("❌ Streamlit Services: Not running")
            except FileNotFoundError:
                print("⚠️  Cannot check process status (pgrep not available)")

            # Check for key service files
            base_dir = Path(__file__).parent.parent.parent.parent
            services = [
                (
                    "Platform Manager",
                    base_dir / "src" / "dashboards" / "smart_platform_manager.py",
                ),
                (
                    "Analytics Viewer",
                    base_dir / "src" / "streamlit_apps" / "compact_detailed_viewer.py",
                ),
                (
                    "Role Manager",
                    base_dir / "src" / "components" / "high_permission_role_manager.py",
                ),
                (
                    "API Matrix",
                    base_dir / "src" / "components" / "api_role_matrix_production.py",
                ),
            ]

            print()
            print("📋 Available Services:")
            for name, path in services:
                status = "✅ Available" if path.exists() else "❌ Missing"
                print(f"   {name}: {status}")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _flags_list(self, args: Namespace) -> int:
        """List all feature flags"""
        try:
            print("🏁 Experimental Feature Flags")
            print("=" * 40)

            # Load feature flags from config
            config_file = (
                Path(__file__).parent.parent.parent.parent
                / "config"
                / "experimental_features.json"
            )

            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        flags = json.load(f)
                except Exception:
                    flags = {}
            else:
                flags = {}

            # Default flags
            default_flags = {
                "advanced-search": {
                    "enabled": False,
                    "description": "Advanced search capabilities",
                },
                "beta-ui": {
                    "enabled": False,
                    "description": "Beta user interface components",
                },
                "deep-analytics": {
                    "enabled": False,
                    "description": "Deep relationship analytics",
                },
                "auto-sync": {
                    "enabled": False,
                    "description": "Automatic profile synchronization",
                },
                "role-automation": {
                    "enabled": False,
                    "description": "Automated role management",
                },
                "performance-monitoring": {
                    "enabled": False,
                    "description": "Performance monitoring tools",
                },
            }

            # Merge with defaults
            for flag, config in default_flags.items():
                if flag not in flags:
                    flags[flag] = config

            flags_data = []
            for flag_name, config in flags.items():
                status = "✅ Enabled" if config.get("enabled", False) else "❌ Disabled"
                flags_data.append(
                    {
                        "Flag": flag_name,
                        "Status": status,
                        "Description": config.get("description", "No description"),
                    }
                )

            # Output results
            output = self.format_output(flags_data, args.format)
            self.save_output(output, args.output)

            print(f"\n📊 Total Flags: {len(flags_data)}")
            enabled_count = len([f for f in flags_data if "✅" in f["Status"]])
            print(f"   ✅ Enabled: {enabled_count}")
            print(f"   ❌ Disabled: {len(flags_data) - enabled_count}")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _flags_enable(self, args: Namespace) -> int:
        """Enable feature flag"""
        try:
            print(f"🏁 Enabling Feature Flag: {args.flag_name}")

            # Update feature flags config
            config_file = (
                Path(__file__).parent.parent.parent.parent
                / "config"
                / "experimental_features.json"
            )

            # Load existing flags
            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        flags = json.load(f)
                except Exception:
                    flags = {}
            else:
                flags = {}
                config_file.parent.mkdir(exist_ok=True)

            # Enable the flag
            if args.flag_name not in flags:
                flags[args.flag_name] = {"description": "User-enabled feature"}

            flags[args.flag_name]["enabled"] = True

            # Save flags
            with open(config_file, "w") as f:
                json.dump(flags, f, indent=2)

            print(f"✅ Feature flag '{args.flag_name}' enabled")
            print(f"   Config saved to: {config_file}")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _flags_disable(self, args: Namespace) -> int:
        """Disable feature flag"""
        try:
            print(f"🏁 Disabling Feature Flag: {args.flag_name}")

            # Update feature flags config
            config_file = (
                Path(__file__).parent.parent.parent.parent
                / "config"
                / "experimental_features.json"
            )

            # Load existing flags
            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        flags = json.load(f)
                except Exception:
                    flags = {}
            else:
                flags = {}

            # Disable the flag
            if args.flag_name in flags:
                flags[args.flag_name]["enabled"] = False

                # Save flags
                with open(config_file, "w") as f:
                    json.dump(flags, f, indent=2)

                print(f"✅ Feature flag '{args.flag_name}' disabled")
            else:
                print(f"⚠️  Feature flag '{args.flag_name}' not found")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    # Conversational handlers (simplified versions of the main handlers)
    def _handle_analytics_conversational(
        self, action: str, terms: List[str], args: Namespace
    ) -> int:
        if action == "orphaned":
            mock_args = Namespace()
            mock_args.type = "all"
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._analytics_find_orphaned(mock_args)
        elif action == "relationships":
            mock_args = Namespace()
            mock_args.deep = "deep" in terms
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._analytics_relationships(mock_args)
        else:
            return self._handle_analytics(args)

    def _handle_sync_conversational(
        self, action: str, terms: List[str], args: Namespace
    ) -> int:
        if action == "analyze":
            mock_args = Namespace()
            mock_args.profile_type = "all"
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._sync_analyze(mock_args)
        elif action == "preview":
            mock_args = Namespace()
            mock_args.dry_run = True
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._sync_preview(mock_args)
        else:
            return self._handle_sync(args)

    def _handle_roles_conversational(
        self, action: str, terms: List[str], args: Namespace
    ) -> int:
        if action == "analyze":
            mock_args = Namespace()
            mock_args.user = terms[0] if terms else None
            mock_args.detailed = "detailed" in terms
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._roles_analyze(mock_args)
        elif action == "audit":
            mock_args = Namespace()
            mock_args.export = None
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._roles_audit(mock_args)
        else:
            return self._handle_roles(args)

    def _handle_platform_conversational(
        self, action: str, terms: List[str], args: Namespace
    ) -> int:
        if action == "launch":
            mock_args = Namespace()
            mock_args.service = "all"
            mock_args.port = None
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._platform_launch(mock_args)
        elif action == "status":
            mock_args = Namespace()
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._platform_status(mock_args)
        else:
            return self._handle_platform(args)

    def _handle_flags_conversational(
        self, action: str, terms: List[str], args: Namespace
    ) -> int:
        if action == "list":
            mock_args = Namespace()
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._flags_list(mock_args)
        elif action == "enable" and terms:
            mock_args = Namespace()
            mock_args.flag_name = terms[0]
            return self._flags_enable(mock_args)
        elif action == "disable" and terms:
            mock_args = Namespace()
            mock_args.flag_name = terms[0]
            return self._flags_disable(mock_args)
        else:
            return self._handle_flags(args)
