#!/usr/bin/env python3
"""
CLI Command: JPAPI Integration
Manage integration between analytics system and jpapi
"""
import sys
import json
from pathlib import Path
from typing import List, Optional

# Using proper package structure via pip install -e .

from cli.base.command import BaseCommand
from framework.analytics.json_engine import JSONAnalyticsEngine
from framework.analytics.jpapi_integration import JPAPIDevIntegration
from core.auth.login_manager import UnifiedJamfAuth


class IntegrationCommand(BaseCommand):
    """JPAPI integration management command"""

    def get_name(self) -> str:
        return "jpapi-integration"

    def get_description(self) -> str:
        return "Manage integration between analytics system and jpapi"

    def add_arguments(self, parser):
        """Add command arguments"""
        subparsers = parser.add_subparsers(dest="action", help="Integration actions")

        # Status command
        status_parser = subparsers.add_parser("status", help="Show integration status")
        status_parser.add_argument("--json", action="store_true", help="Output as JSON")

        # Sync command
        sync_parser = subparsers.add_parser(
            "sync", help="Sync analytics with jpapi exports"
        )
        sync_parser.add_argument(
            "--types",
            nargs="+",
            choices=["policies", "groups", "profiles", "devices"],
            help="Object types to sync (default: all)",
        )

        # Cache command
        cache_parser = subparsers.add_parser("cache", help="Manage caches")
        cache_parser.add_argument(
            "cache_action",
            choices=["clear", "status", "sync"],
            help="Cache action to perform",
        )

        # Launch command
        launch_parser = subparsers.add_parser("launch", help="Launch integrated system")
        launch_parser.add_argument(
            "--analytics-only",
            action="store_true",
            help="Launch only analytics components",
        )
        launch_parser.add_argument(
            "--jpapi-gui",
            choices=["dash", "streamlit"],
            help="Also launch jpapi GUI interface",
        )

        # Test command
        test_parser = subparsers.add_parser(
            "test", help="Test integration connectivity"
        )

    def execute(self, args):
        """Execute integration command"""
        try:
            if not args.action:
                print("❌ No action specified. Use --help for available actions.")
                return False

            # Initialize components
            print("🔗 Initializing JPAPI integration...")

            # Initialize analytics engine
            analytics = JSONAnalyticsEngine(
                framework=None,
                export_dir="tmp/exports",
                cache_dir="tmp/cache/analytics",
            )

            # Get integration instance
            integration = analytics.jpapi_integration

            # Execute action
            if args.action == "status":
                return self._handle_status(integration, args)
            elif args.action == "sync":
                return self._handle_sync(integration, args)
            elif args.action == "cache":
                return self._handle_cache(integration, args)
            elif args.action == "launch":
                return self._handle_launch(integration, args)
            elif args.action == "test":
                return self._handle_test(integration, args)
            else:
                print(f"❌ Unknown action: {args.action}")
                return False

        except Exception as e:
            print(f"❌ Integration error: {e}")
            return False

    def _handle_status(self, integration, args):
        """Handle status command"""
        print("📊 Getting integration status...")

        status = integration.get_integration_status()

        if args.json:
            print(json.dumps(status, indent=2))
            return True

        # Pretty print status
        print("\n🔗 JPAPI INTEGRATION STATUS")
        print("=" * 40)

        # JPAPI status
        jpapi_status = status["jpapi"]
        jpapi_health = jpapi_status.get("status", "unknown")

        if jpapi_health == "healthy":
            print("📱 JPAPI: ✅ Healthy")
        elif jpapi_health == "error":
            print("📱 JPAPI: ❌ Error")
            print(f"   Error: {jpapi_status.get('error', 'Unknown')}")
        else:
            print("📱 JPAPI: ⚠️ Unavailable")

        # Analytics status
        analytics_status = status["analytics"]
        print(
            f"📊 Analytics Engine: {'✅' if analytics_status['engine_available'] else '❌'}"
        )
        print(f"   Cache Directory: {analytics_status['cache_directory']}")
        print(f"   Export Directory: {analytics_status['export_directory']}")

        # Integration status
        integration_info = status["integration"]
        jpapi_exists = integration_info["jpapi_exists"]
        print(f"🔗 Integration: {'✅' if jpapi_exists else '❌'}")
        print(f"   JPAPI Path: {integration_info['jpapi_path']}")
        print(f"   Path Exists: {'✅' if jpapi_exists else '❌'}")

        return True

    def _handle_sync(self, integration, args):
        """Handle sync command"""
        print("🔄 Syncing analytics with jpapi exports...")

        sync_results = integration.sync_with_jpapi_exports()

        print("\n📊 SYNC RESULTS")
        print("=" * 20)

        for object_type, result in sync_results.items():
            status = result.get("status", "unknown")

            if status == "success":
                print(f"✅ {object_type}: Success")
                print(f"   File: {result.get('file', 'N/A')}")
            elif status == "warning":
                print(f"⚠️ {object_type}: Warning")
                print(f"   Error: {result.get('error', 'Unknown')[:100]}")
            elif status == "timeout":
                print(f"⏰ {object_type}: Timeout")
            else:
                print(f"❌ {object_type}: Error")
                print(f"   Error: {result.get('error', 'Unknown')}")

        return True

    def _handle_cache(self, integration, args):
        """Handle cache command"""
        action = args.cache_action
        print(f"💾 Cache management: {action}")

        results = integration.cache_management_bridge(action)

        print(f"\n💾 CACHE {action.upper()} RESULTS")
        print("=" * 30)

        for cache_type, result in results.items():
            if isinstance(result, str):
                if "error" in result:
                    print(f"❌ {cache_type}: {result}")
                elif "warning" in result:
                    print(f"⚠️ {cache_type}: {result}")
                else:
                    print(f"✅ {cache_type}: {result}")
            else:
                print(f"📊 {cache_type}: {result}")

        return True

    def _handle_launch(self, integration, args):
        """Handle launch command"""
        print("🚀 Launching integrated system...")

        # Create and show launcher path
        launcher_path = integration.create_integrated_launcher()

        print(f"📝 Created launcher script: {launcher_path}")
        print("")
        print("🎯 TO LAUNCH THE INTEGRATED SYSTEM:")
        print(f"   {launcher_path}")
        print("")
        print("📊 This will start:")
        print("   • Analytics Backend (port 8901)")
        print("   • Analytics Frontend (port 8902)")
        print("   • JPAPI integration endpoints")

        if args.jpapi_gui:
            print(f"   • JPAPI {args.jpapi_gui} interface")
            success = integration.launch_jpapi_gui(args.jpapi_gui)
            if success:
                print(f"✅ JPAPI {args.jpapi_gui} launched")
            else:
                print(f"❌ Failed to launch JPAPI {args.jpapi_gui}")

        return True

    def _handle_test(self, integration, args):
        """Handle test command"""
        print("🧪 Testing integration connectivity...")

        # Test jpapi availability
        jpapi_status = integration.get_jpapi_status()

        print("\n🧪 INTEGRATION TESTS")
        print("=" * 25)

        # Test 1: JPAPI executable
        jpapi_path = integration.jpapi_path
        if jpapi_path.exists():
            print("✅ JPAPI executable found")
        else:
            print("❌ JPAPI executable not found")
            print(f"   Expected path: {jpapi_path}")

        # Test 2: JPAPI status
        if jpapi_status["status"] == "healthy":
            print("✅ JPAPI status check passed")
        else:
            print("❌ JPAPI status check failed")
            print(f"   Status: {jpapi_status['status']}")
            if "error" in jpapi_status:
                print(f"   Error: {jpapi_status['error']}")

        # Test 3: Analytics engine
        if integration.analytics_engine:
            print("✅ Analytics engine available")
        else:
            print("❌ Analytics engine not available")

        # Test 4: Cache directories
        cache_dir = integration.cache_dir
        export_dir = integration.export_dir

        if cache_dir.exists():
            print("✅ Cache directory exists")
        else:
            print("⚠️ Cache directory missing (will be created)")

        if export_dir.exists():
            print("✅ Export directory exists")
        else:
            print("⚠️ Export directory missing (will be created)")

        print("")
        print(
            "🎯 INTEGRATION READY!"
            if jpapi_status["status"] == "healthy"
            else "⚠️ Integration has issues"
        )

        return True


# Register command
def register_command():
    """Register the jpapi integration command"""
    return JPAPIDevIntegrationCommand()
