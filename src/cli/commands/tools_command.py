#!/usr/bin/env python3
"""
Tools Command for jpapi CLI
Utilities for cache management and health checks (unique tools only)
"""

from argparse import ArgumentParser, Namespace
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
import shutil
import psutil
import time
import json

# Using proper package structure via pip install -e .

from base.command import BaseCommand


class ToolsCommand(BaseCommand):
    """JAMF Pro utilities (cache management, health checks)"""

    def __init__(self):
        super().__init__(
            name="tools",
            description="JAMF Pro utilities (cache management, health checks)",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add tools command arguments"""
        subparsers = parser.add_subparsers(dest="tool_type", help="Available tools")

        # Cache management tools
        cache_parser = subparsers.add_parser("cache", help="💾 Cache management tools")
        cache_subparsers = cache_parser.add_subparsers(
            dest="cache_action", help="Cache actions"
        )

        cache_clear_parser = cache_subparsers.add_parser(
            "clear", help="Clear all caches"
        )
        cache_clear_parser.add_argument(
            "--type",
            choices=["memory", "file", "all"],
            default="all",
            help="Type of cache to clear",
        )

        cache_stats_parser = cache_subparsers.add_parser(
            "stats", help="Show cache statistics"
        )
        self.setup_common_args(cache_stats_parser)

        # Health check tools
        health_parser = subparsers.add_parser("health", help="🏥 Health check tools")
        health_subparsers = health_parser.add_subparsers(
            dest="health_action", help="Health check actions"
        )

        health_system_parser = health_subparsers.add_parser(
            "system", help="Check system health"
        )
        self.setup_common_args(health_system_parser)

        health_api_parser = health_subparsers.add_parser(
            "api", help="Check API connectivity"
        )
        health_api_parser.add_argument(
            "--timeout", type=int, default=30, help="Connection timeout in seconds"
        )
        self.setup_common_args(health_api_parser)

    def execute(self, args: Namespace) -> int:
        """Execute the tools command"""
        try:
            if not args.tool_type:
                print("🔧 Available JAMF Pro Tools:")
                print()
                print("💾 Cache Management:")
                print("   jpapi tools cache clear            # Clear all caches")
                print("   jpapi tools cache clear --type file # Clear file caches only")
                print("   jpapi tools cache stats            # Show cache statistics")
                print()
                print("🏥 Health Checks:")
                print("   jpapi tools health system          # Check system health")
                print("   jpapi tools health api             # Check API connectivity")
                print()
                print("ℹ️  Note: API matrix, role management, and dashboard tools")
                print("   are available as separate web interfaces in src/components/")
                return 1

            # Route to appropriate handler
            if args.tool_type == "cache":
                return self._handle_cache_tools(args)
            elif args.tool_type == "health":
                return self._handle_health_tools(args)
            else:
                print(f"❌ Unknown tool type: {args.tool_type}")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_cache_tools(self, args: Namespace) -> int:
        """Handle cache management tools"""
        if not hasattr(args, "cache_action") or not args.cache_action:
            print("💾 Available Cache Tools:")
            print("   jpapi tools cache clear            # Clear all caches")
            print("   jpapi tools cache stats            # Show cache statistics")
            return 1

        if args.cache_action == "clear":
            return self._clear_cache(args)
        elif args.cache_action == "stats":
            return self._show_cache_stats(args)
        else:
            print(f"❌ Unknown cache action: {args.cache_action}")
            return 1

    def _clear_cache(self, args: Namespace) -> int:
        """Clear caches"""
        try:
            print(f"🧹 Clearing {args.type} cache(s)...")

            cleared_items = 0
            cleared_size = 0

            # Define cache directories
            cache_dirs = [
                Path("tmp/cache"),
                Path("src/cache"),
                Path("cache"),
                (
                    Path(".jpapi/cache")
                    if Path.home().joinpath(".jpapi/cache").exists()
                    else None
                ),
            ]

            # Remove None entries
            cache_dirs = [d for d in cache_dirs if d is not None]

            if args.type in ["file", "all"]:
                print("   🗂️  Clearing file caches...")
                for cache_dir in cache_dirs:
                    if cache_dir.exists():
                        for cache_file in cache_dir.rglob("*"):
                            if cache_file.is_file():
                                try:
                                    file_size = cache_file.stat().st_size
                                    cache_file.unlink()
                                    cleared_items += 1
                                    cleared_size += file_size
                                except Exception as e:
                                    print(
                                        f"      ⚠️  Could not remove {cache_file}: {e}"
                                    )

                print(
                    f"      ✅ Cleared {cleared_items} files ({cleared_size / 1024:.1f} KB)"
                )

            if args.type in ["memory", "all"]:
                print("   🧠 Clearing memory caches...")
                # Clear Python __pycache__ directories
                pycache_cleared = 0
                for pycache_dir in Path(".").rglob("__pycache__"):
                    try:
                        shutil.rmtree(pycache_dir)
                        pycache_cleared += 1
                    except Exception as e:
                        print(f"      ⚠️  Could not remove {pycache_dir}: {e}")

                print(f"      ✅ Cleared {pycache_cleared} __pycache__ directories")

            print(f"\n✅ Cache clearing complete!")
            return 0

        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
            return 1

    def _show_cache_stats(self, args: Namespace) -> int:
        """Show cache statistics"""
        try:
            print("📊 Cache Statistics")
            print("=" * 50)

            # Analyze cache directories
            cache_dirs = [
                ("tmp/cache", Path("tmp/cache")),
                ("src/cache", Path("src/cache")),
                ("cache", Path("cache")),
                ("user cache", Path.home() / ".jpapi/cache"),
            ]

            total_files = 0
            total_size = 0
            cache_stats = []

            for name, cache_dir in cache_dirs:
                if cache_dir.exists():
                    files = list(cache_dir.rglob("*"))
                    file_count = len([f for f in files if f.is_file()])
                    dir_size = sum(f.stat().st_size for f in files if f.is_file())

                    cache_stats.append(
                        {
                            "Directory": name,
                            "Files": file_count,
                            "Size (KB)": f"{dir_size / 1024:.1f}",
                            "Path": str(cache_dir),
                        }
                    )

                    total_files += file_count
                    total_size += dir_size
                else:
                    cache_stats.append(
                        {
                            "Directory": name,
                            "Files": 0,
                            "Size (KB)": "0.0",
                            "Path": f"{cache_dir} (not found)",
                        }
                    )

            # Output cache stats
            if cache_stats:
                output = self.format_output(cache_stats, args.format)
                self.save_output(output, args.output)

            print(f"\n📈 Summary:")
            print(f"   Total Files: {total_files}")
            print(
                f"   Total Size: {total_size / 1024:.1f} KB ({total_size / (1024*1024):.2f} MB)"
            )

            # Check __pycache__ directories
            pycache_dirs = list(Path(".").rglob("__pycache__"))
            if pycache_dirs:
                print(f"   Python Cache: {len(pycache_dirs)} __pycache__ directories")

            return 0

        except Exception as e:
            print(f"❌ Error getting cache stats: {e}")
            return 1

    def _handle_health_tools(self, args: Namespace) -> int:
        """Handle health check tools"""
        if not hasattr(args, "health_action") or not args.health_action:
            print("🏥 Available Health Check Tools:")
            print("   jpapi tools health system          # Check system health")
            print("   jpapi tools health api             # Check API connectivity")
            return 1

        if args.health_action == "system":
            return self._check_system_health(args)
        elif args.health_action == "api":
            return self._check_api_health(args)
        else:
            print(f"❌ Unknown health action: {args.health_action}")
            return 1

    def _check_system_health(self, args: Namespace) -> int:
        """Check system health"""
        try:
            print("🏥 System Health Check")
            print("=" * 50)

            health_data = []
            overall_status = "Healthy"

            # Check Python version
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            python_ok = sys.version_info >= (3, 8)
            health_data.append(
                {
                    "Component": "Python Version",
                    "Status": "✅ OK" if python_ok else "❌ FAIL",
                    "Value": python_version,
                    "Details": (
                        "Requires Python 3.8+" if not python_ok else "Compatible"
                    ),
                }
            )
            if not python_ok:
                overall_status = "Issues Found"

            # Check disk space
            disk_usage = psutil.disk_usage(".")
            free_gb = disk_usage.free / (1024**3)
            disk_ok = free_gb > 1.0  # At least 1GB free
            health_data.append(
                {
                    "Component": "Disk Space",
                    "Status": "✅ OK" if disk_ok else "⚠️  LOW",
                    "Value": f"{free_gb:.1f} GB free",
                    "Details": "Sufficient space" if disk_ok else "Low disk space",
                }
            )
            if not disk_ok:
                overall_status = "Warnings"

            # Check memory
            memory = psutil.virtual_memory()
            memory_ok = memory.available > (
                512 * 1024 * 1024
            )  # At least 512MB available
            health_data.append(
                {
                    "Component": "Memory",
                    "Status": "✅ OK" if memory_ok else "⚠️  LOW",
                    "Value": f"{memory.available / (1024**2):.0f} MB available",
                    "Details": (
                        "Sufficient memory" if memory_ok else "Low available memory"
                    ),
                }
            )
            if not memory_ok:
                overall_status = "Warnings"

            # Check dependencies
            required_modules = ["requests", "urllib3", "json", "argparse"]
            missing_modules = []

            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_modules.append(module)

            deps_ok = len(missing_modules) == 0
            health_data.append(
                {
                    "Component": "Dependencies",
                    "Status": "✅ OK" if deps_ok else "❌ FAIL",
                    "Value": f"{len(required_modules) - len(missing_modules)}/{len(required_modules)} modules",
                    "Details": (
                        "All dependencies available"
                        if deps_ok
                        else f'Missing: {", ".join(missing_modules)}'
                    ),
                }
            )
            if not deps_ok:
                overall_status = "Issues Found"

            # Check jpapi files
            core_files = [
                Path("jpapi"),
                Path("utilities/jpapi_core_modular"),
                Path("src/core/auth/unified_auth.py"),
                Path("src/cli/main.py"),
            ]

            missing_files = [f for f in core_files if not f.exists()]
            files_ok = len(missing_files) == 0
            health_data.append(
                {
                    "Component": "Core Files",
                    "Status": "✅ OK" if files_ok else "❌ FAIL",
                    "Value": f"{len(core_files) - len(missing_files)}/{len(core_files)} files",
                    "Details": (
                        "All core files present"
                        if files_ok
                        else f'Missing: {", ".join(str(f) for f in missing_files)}'
                    ),
                }
            )
            if not files_ok:
                overall_status = "Issues Found"

            # Output results
            output = self.format_output(health_data, args.format)
            self.save_output(output, args.output)

            print(f"\n🎯 Overall Status: {overall_status}")

            if overall_status == "Issues Found":
                return 1
            elif overall_status == "Warnings":
                return 0  # Warnings but still functional
            else:
                return 0

        except Exception as e:
            print(f"❌ Error checking system health: {e}")
            return 1

    def _check_api_health(self, args: Namespace) -> int:
        """Check API connectivity and health"""
        if not self.check_auth(args):
            return 1

        try:
            print("🌐 API Health Check")
            print("=" * 50)

            health_data = []
            start_time = time.time()

            # Test basic connectivity
            try:
                auth_info = self.auth.get_auth_info()
                auth_time = time.time() - start_time

                health_data.append(
                    {
                        "Endpoint": "Authentication",
                        "Status": "✅ OK",
                        "Response Time": f"{auth_time:.3f}s",
                        "Details": f"Connected as: {auth_info.get('account', {}).get('username', 'Unknown')}",
                    }
                )
            except Exception as e:
                health_data.append(
                    {
                        "Endpoint": "Authentication",
                        "Status": "❌ FAIL",
                        "Response Time": "N/A",
                        "Details": str(e),
                    }
                )

            # Test key endpoints
            test_endpoints = [
                ("/JSSResource/categories", "Categories"),
                ("/JSSResource/policies", "Policies"),
                ("/JSSResource/mobiledevices", "Mobile Devices"),
                ("/JSSResource/computers", "Computers"),
            ]

            for endpoint, name in test_endpoints:
                try:
                    start_time = time.time()
                    response = self.auth.api_request("GET", endpoint)
                    response_time = time.time() - start_time

                    # Check if response has expected structure
                    if isinstance(response, dict) and len(response) > 0:
                        status = "✅ OK"
                        details = f"Response received ({len(str(response))} chars)"
                    else:
                        status = "⚠️  EMPTY"
                        details = "Empty response"

                    health_data.append(
                        {
                            "Endpoint": name,
                            "Status": status,
                            "Response Time": f"{response_time:.3f}s",
                            "Details": details,
                        }
                    )

                except Exception as e:
                    health_data.append(
                        {
                            "Endpoint": name,
                            "Status": "❌ FAIL",
                            "Response Time": "N/A",
                            "Details": str(e),
                        }
                    )

            # Output results
            output = self.format_output(health_data, args.format)
            self.save_output(output, args.output)

            # Determine overall API health
            failed_tests = [item for item in health_data if "❌ FAIL" in item["Status"]]
            warning_tests = [item for item in health_data if "⚠️" in item["Status"]]

            if failed_tests:
                print(f"\n❌ API Health: Issues Found ({len(failed_tests)} failures)")
                return 1
            elif warning_tests:
                print(f"\n⚠️  API Health: Warnings ({len(warning_tests)} warnings)")
                return 0
            else:
                print(f"\n✅ API Health: All systems operational")
                return 0

        except Exception as e:
            print(f"❌ Error checking API health: {e}")
            return 1
