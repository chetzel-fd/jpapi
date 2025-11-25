#!/usr/bin/env python3
"""
Info Command for jpapi CLI
System information, help, and environment details
"""
from argparse import ArgumentParser, Namespace
import argparse
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
import platform
import subprocess
import os

# Using proper package structure via pip install -e .

from base.command import BaseCommand


class InfoCommand(BaseCommand):
    """ℹ️ System information, help, and environment details"""

    def __init__(self):
        super().__init__(
            name="info",
            description="ℹ️ System information, help, and environment details",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add info command arguments with comprehensive aliases"""
        # Support flexible positional arguments
        parser.add_argument(
            "info_target",
            nargs="?",
            help="What info to show (env, interfaces, examples, system)",
        )
        parser.add_argument("info_terms", nargs="*", help="Additional parameters")

        # Traditional subcommand structure
        subparsers = parser.add_subparsers(dest="info_type", help="Information to show")

        # Environment info - main command with aliases in help
        env_parser = subparsers.add_parser(
            "env", help="Environment information (also: environment)"
        )
        self.setup_common_args(env_parser)

        # Hidden aliases for env
        for alias in ["environment", "config"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            self.setup_common_args(alias_parser)

        # Interfaces info - main command with aliases in help
        interfaces_parser = subparsers.add_parser(
            "interfaces", help="Available web interfaces (also: ui, web)"
        )
        self.setup_common_args(interfaces_parser)

        # Hidden aliases for interfaces
        for alias in ["ui", "web", "dashboard", "dashboards"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            self.setup_common_args(alias_parser)

        # Examples info - main command with aliases in help
        examples_parser = subparsers.add_parser(
            "examples", help="CLI usage examples (also: help, usage)"
        )
        examples_parser.add_argument(
            "--command", help="Show examples for specific command"
        )
        self.setup_common_args(examples_parser)

        # Hidden aliases for examples
        for alias in ["help", "usage", "demo"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument(
                "--command", help="Show examples for specific command"
            )
            self.setup_common_args(alias_parser)

        # System info - main command with aliases in help
        system_parser = subparsers.add_parser(
            "system", help="System health and diagnostics (also: health, diag)"
        )
        system_parser.add_argument(
            "--detailed", action="store_true", help="Show detailed system information"
        )
        self.setup_common_args(system_parser)

        # Hidden aliases for system
        for alias in ["health", "diag", "diagnostics", "status"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument(
                "--detailed",
                action="store_true",
                help="Show detailed system information",
            )
            self.setup_common_args(alias_parser)

        # Version info - main command
        version_parser = subparsers.add_parser(
            "version", help="Version information (also: ver)"
        )
        self.setup_common_args(version_parser)

        # Hidden aliases for version
        for alias in ["ver", "about"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            self.setup_common_args(alias_parser)

    def execute(self, args: Namespace) -> int:
        """Execute the info command with flexible parsing"""
        try:
            # Handle conversational patterns
            if hasattr(args, "info_target") and args.info_target:
                return self._handle_conversational_info(args)

            # Handle traditional subcommand structure
            if not args.info_type:
                print("ℹ️ jpapi Information & Help System:")
                print()
                print("💬 Quick Info:")
                print("   jpapi info env                    # Environment details")
                print("   jpapi info interfaces             # Available web UIs")
                print("   jpapi info examples               # CLI usage examples")
                print("   jpapi info system                 # System health")
                print()
                print("🏗️  Traditional Info:")
                print("   jpapi info env --format json     # Environment as JSON")
                print("   jpapi info examples --command search  # Search examples")
                print("   jpapi info system --detailed     # Detailed diagnostics")
                print()
                print("📋 Available Information:")
                print("   env - Environment configuration and status")
                print("   interfaces - Web dashboards and tools")
                print("   examples - CLI usage examples and help")
                print("   system - System health and diagnostics")
                print("   version - Version and build information")
                return 1

            # Route to appropriate handler
            if args.info_type in ["env", "environment", "config"]:
                return self._show_env_info(args)
            elif args.info_type in [
                "interfaces",
                "ui",
                "web",
                "dashboard",
                "dashboards",
            ]:
                return self._show_interfaces_info(args)
            elif args.info_type in ["examples", "help", "usage", "demo"]:
                return self._show_examples_info(args)
            elif args.info_type in [
                "system",
                "health",
                "diag",
                "diagnostics",
                "status",
            ]:
                return self._show_system_info(args)
            elif args.info_type in ["version", "ver", "about"]:
                return self._show_version_info(args)
            else:
                print(f"❌ Unknown info type: {args.info_type}")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_conversational_info(self, args: Namespace) -> int:
        """Handle conversational info patterns"""
        target = args.info_target.lower()
        terms = args.info_terms if args.info_terms else []

        print(f"ℹ️ Getting info about: {target}")

        # Route based on target
        if target in ["env", "environment", "config"]:
            return self._show_env_info(args)
        elif target in ["interfaces", "ui", "web", "dashboard", "dashboards"]:
            return self._show_interfaces_info(args)
        elif target in ["examples", "help", "usage", "demo"]:
            # Check if specific command requested
            command = terms[0] if terms else None
            mock_args = Namespace()
            mock_args.command = command
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._show_examples_info(mock_args)
        elif target in ["system", "health", "diag", "diagnostics", "status"]:
            mock_args = Namespace()
            mock_args.detailed = "detailed" in terms
            mock_args.format = getattr(args, "format", "table")
            mock_args.output = getattr(args, "output", None)
            return self._show_system_info(mock_args)
        elif target in ["version", "ver", "about"]:
            return self._show_version_info(args)
        else:
            print(f"❌ Unknown info target: {target}")
            print("   Available: env, interfaces, examples, system, version")
            return 1

    def _show_env_info(self, args: Namespace) -> int:
        """Show environment information"""
        try:
            print("🌍 Environment Information")
            print("=" * 50)

            # Get environment from args or default
            environment = getattr(args, "env", "sandbox")

            # Base directory
            base_dir = Path(__file__).parent.parent.parent.parent

            env_data = []

            # Basic environment info
            env_data.append(
                {
                    "Property": "Active Environment",
                    "Value": environment,
                    "Description": "Current JAMF environment",
                }
            )

            env_data.append(
                {
                    "Property": "Base Directory",
                    "Value": str(base_dir),
                    "Description": "jpapi installation directory",
                }
            )

            env_data.append(
                {
                    "Property": "Python Version",
                    "Value": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "Description": "Python interpreter version",
                }
            )

            env_data.append(
                {
                    "Property": "Platform",
                    "Value": platform.system(),
                    "Description": "Operating system",
                }
            )

            # Check authentication status
            if hasattr(self, "auth") and self.auth:
                try:
                    auth_info = self.auth.get_auth_info()
                    auth_status = (
                        "✅ Configured"
                        if auth_info.get("configured", False)
                        else "❌ Not Configured"
                    )
                    server_url = auth_info.get("server_url", "Not set")
                except Exception:
                    auth_status = "❌ Error"
                    server_url = "Unknown"
            else:
                auth_status = "❌ Not Available"
                server_url = "Not available"

            env_data.append(
                {
                    "Property": "Authentication",
                    "Value": auth_status,
                    "Description": f"JAMF Pro connection status",
                }
            )

            env_data.append(
                {
                    "Property": "JAMF Server",
                    "Value": server_url,
                    "Description": "JAMF Pro server URL",
                }
            )

            # Check for key files
            key_files = [
                ("Main CLI", base_dir / "jpapi"),
                ("Python CLI", base_dir / "utilities" / "jpapi_core_modular"),
                ("Auth Module", base_dir / "src" / "core" / "auth" / "unified_auth.py"),
                ("Config", base_dir / "config" / "experimental_features.json"),
            ]

            for name, file_path in key_files:
                status = "✅ Found" if file_path.exists() else "❌ Missing"
                env_data.append(
                    {
                        "Property": name,
                        "Value": status,
                        "Description": f"Core file: {file_path.name}",
                    }
                )

            # Output results
            output = self.format_output(env_data, args.format)
            self.save_output(output, args.output)

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _show_interfaces_info(self, args: Namespace) -> int:
        """Show available web interfaces"""
        try:
            print("🚀 Available JAMF Pro Web Interfaces")
            print("=" * 50)

            # Base directory for finding interfaces
            base_dir = Path(__file__).parent.parent.parent.parent

            interfaces_data = []

            # Streamlit apps
            streamlit_dir = base_dir / "src" / "streamlit_apps"
            if streamlit_dir.exists():
                streamlit_apps = list(streamlit_dir.glob("*.py"))
                for app in streamlit_apps:
                    interfaces_data.append(
                        {
                            "Type": "Streamlit App",
                            "Name": app.stem.replace("_", " ").title(),
                            "File": app.name,
                            "Command": f"streamlit run {app}",
                            "Description": "Interactive web dashboard",
                        }
                    )

            # Dashboard components
            dashboard_dir = base_dir / "src" / "dashboards"
            if dashboard_dir.exists():
                dashboard_apps = list(dashboard_dir.glob("*.py"))
                for app in dashboard_apps:
                    interfaces_data.append(
                        {
                            "Type": "Dashboard",
                            "Name": app.stem.replace("_", " ").title(),
                            "File": app.name,
                            "Command": f"python3 {app}",
                            "Description": "Specialized dashboard component",
                        }
                    )

            # Web interfaces
            web_dir = base_dir / "web"
            if web_dir.exists():
                html_files = list(web_dir.glob("*.html"))
                for html_file in html_files:
                    interfaces_data.append(
                        {
                            "Type": "Web Interface",
                            "Name": html_file.stem.replace("_", " ").title(),
                            "File": html_file.name,
                            "Command": f"open {html_file}",
                            "Description": "Static web interface",
                        }
                    )

            if not interfaces_data:
                print("❌ No web interfaces found")
                return 1

            # Output results
            output = self.format_output(interfaces_data, args.format)
            self.save_output(output, args.output)

            print(f"\n📊 Found {len(interfaces_data)} available interfaces")
            print("\n💡 Quick Launch Tips:")
            print("   • Use 'jpapi launch' command for easy interface launching")
            print("   • Streamlit apps provide interactive dashboards")
            print("   • Dashboard components offer specialized views")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _show_examples_info(self, args: Namespace) -> int:
        """Show CLI usage examples"""
        try:
            command_filter = getattr(args, "command", None)

            if command_filter:
                print(f"💡 jpapi Examples: {command_filter}")
                print("=" * 50)
                return self._show_command_examples(command_filter)
            else:
                print("💡 jpapi CLI Usage Examples")
                print("=" * 50)

            examples_data = []

            # General examples
            general_examples = [
                {
                    "Category": "Authentication",
                    "Command": "jpapi auth setup dev",
                    "Description": "Set up authentication for dev environment",
                    "Usage": "Basic setup",
                },
                {
                    "Category": "Quick Lists",
                    "Command": "jpapi list computers",
                    "Description": "List all computers",
                    "Usage": "Fast overview",
                },
                {
                    "Category": "Quick Lists",
                    "Command": "jpapi ls mobile --filter iPad",
                    "Description": "List iPads using alias",
                    "Usage": "Filtered results",
                },
                {
                    "Category": "Export Data",
                    "Command": "jpapi export policies --format csv",
                    "Description": "Export policies to CSV (default format)",
                    "Usage": "Data analysis",
                },
                {
                    "Category": "Export Data",
                    "Command": "jpapi exp comp --detailed",
                    "Description": "Export detailed computer info using alias",
                    "Usage": "Comprehensive export",
                },
                {
                    "Category": "Search",
                    "Command": 'jpapi search computers criteria --name "MacBook*"',
                    "Description": "Search computers by name pattern",
                    "Usage": "Targeted search",
                },
                {
                    "Category": "Search",
                    "Command": "jpapi find ipad --supervised true",
                    "Description": "Find supervised iPads using alias",
                    "Usage": "Quick filtering",
                },
                {
                    "Category": "Device Management",
                    "Command": "jpapi devices comp info MacBook-123",
                    "Description": "Get detailed computer information",
                    "Usage": "Device details",
                },
                {
                    "Category": "Device Management",
                    "Command": "jpapi dev mobile update iPad-456",
                    "Description": "Update mobile device inventory using alias",
                    "Usage": "Inventory refresh",
                },
                {
                    "Category": "Bulk Operations",
                    "Command": "jpapi move disabled policies",
                    "Description": "Move all disabled policies to Archive",
                    "Usage": "Cleanup operations",
                },
                {
                    "Category": "Creation",
                    "Command": 'jpapi create category "Software Updates"',
                    "Description": "Create a new category",
                    "Usage": "Object creation",
                },
                {
                    "Category": "Tools",
                    "Command": "jpapi tools cache clear",
                    "Description": "Clear all caches",
                    "Usage": "Maintenance",
                },
                {
                    "Category": "Tools",
                    "Command": "jpapi tools health api",
                    "Description": "Check API connectivity",
                    "Usage": "Diagnostics",
                },
            ]

            examples_data.extend(general_examples)

            # Output results
            output = self.format_output(examples_data, args.format)
            self.save_output(output, args.output)

            print(f"\n🎯 Pro Tips:")
            print("   • Use aliases for faster typing (ls, exp, find, dev)")
            print("   • Mix conversational and traditional syntax")
            print("   • Add --help to any command for detailed options")
            print("   • Use --format json for scripting")
            print("   • Use --output file.csv to save results")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _show_command_examples(self, command: str) -> int:
        """Show examples for a specific command"""
        command_examples = {
            "list": [
                "jpapi list computers",
                "jpapi ls mobile --filter iPad",
                "jpapi list categories --format json",
                "jpapi list policies --status enabled",
            ],
            "export": [
                "jpapi export policies --format csv",
                "jpapi exp comp --detailed --output computers.csv",
                "jpapi export mobile --format json",
                "jpapi export categories",
            ],
            "search": [
                'jpapi search computers criteria --name "MacBook*"',
                "jpapi find mobile --model iPad --supervised true",
                'jpapi search computers query "name:MacBook AND department:IT"',
                'jpapi search mobile criteria --os-version ">=15.0"',
            ],
            "devices": [
                "jpapi devices comp info MacBook-123",
                "jpapi dev mobile update iPad-456 --force",
                "jpapi devices computer command restart MacBook-789",
                'jpapi devices ipad lost enable iPad-101 --message "Contact IT"',
            ],
            "create": [
                'jpapi create category "Software Updates"',
                'jpapi create policy "Install Chrome" --category Software --enabled',
                'jpapi create group "Marketing Macs" --smart',
                'jpapi create search "Find iPads" --type mobile',
            ],
            "move": [
                "jpapi move disabled policies",
                'jpapi move policies "*Chrome*" --to-category Software',
                'jpapi move devices "MacBook*" --to-group "IT Department"',
                'jpapi move profiles "WiFi*" --to-category Network',
            ],
            "tools": [
                "jpapi tools cache clear",
                "jpapi tools cache stats --format json",
                "jpapi tools health system",
                "jpapi tools health api --timeout 60",
            ],
        }

        examples = command_examples.get(command.lower(), [])

        if not examples:
            print(f"❌ No examples available for command: {command}")
            return 1

        print(f"Examples for '{command}' command:")
        print()
        for i, example in enumerate(examples, 1):
            print(f"{i:2}. {example}")

        print(f"\n💡 Use 'jpapi {command} --help' for detailed options")

        return 0

    def _show_system_info(self, args: Namespace) -> int:
        """Show system health and diagnostics"""
        try:
            print("🏥 System Health & Diagnostics")
            print("=" * 50)

            system_data = []

            # Python environment
            system_data.append(
                {
                    "Component": "Python Version",
                    "Status": "✅ OK" if sys.version_info >= (3, 8) else "⚠️ OLD",
                    "Value": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "Details": (
                        "Compatible"
                        if sys.version_info >= (3, 8)
                        else "Requires Python 3.8+"
                    ),
                }
            )

            # Platform info
            system_data.append(
                {
                    "Component": "Operating System",
                    "Status": "✅ OK",
                    "Value": f"{platform.system()} {platform.release()}",
                    "Details": platform.platform(),
                }
            )

            # Disk space
            try:
                import shutil

                total, used, free = shutil.disk_usage(".")
                free_gb = free / (1024**3)
                disk_status = "✅ OK" if free_gb > 1.0 else "⚠️ LOW"
                system_data.append(
                    {
                        "Component": "Disk Space",
                        "Status": disk_status,
                        "Value": f"{free_gb:.1f} GB free",
                        "Details": f"Total: {total/(1024**3):.1f} GB",
                    }
                )
            except Exception:
                system_data.append(
                    {
                        "Component": "Disk Space",
                        "Status": "❌ ERROR",
                        "Value": "Unknown",
                        "Details": "Could not check disk space",
                    }
                )

            # Memory
            try:
                import psutil

                memory = psutil.virtual_memory()
                memory_status = (
                    "✅ OK" if memory.available > (512 * 1024 * 1024) else "⚠️ LOW"
                )
                system_data.append(
                    {
                        "Component": "Memory",
                        "Status": memory_status,
                        "Value": f"{memory.available / (1024**2):.0f} MB available",
                        "Details": f"Total: {memory.total / (1024**3):.1f} GB",
                    }
                )
            except ImportError:
                system_data.append(
                    {
                        "Component": "Memory",
                        "Status": "⚠️ N/A",
                        "Value": "psutil not available",
                        "Details": "Install psutil for memory monitoring",
                    }
                )

            # Dependencies
            required_modules = ["requests", "urllib3", "json", "argparse", "pathlib"]
            missing_modules = []

            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_modules.append(module)

            deps_status = "✅ OK" if len(missing_modules) == 0 else "❌ MISSING"
            system_data.append(
                {
                    "Component": "Dependencies",
                    "Status": deps_status,
                    "Value": f"{len(required_modules) - len(missing_modules)}/{len(required_modules)} modules",
                    "Details": (
                        "All available"
                        if not missing_modules
                        else f'Missing: {", ".join(missing_modules)}'
                    ),
                }
            )

            # Core files
            base_dir = Path(__file__).parent.parent.parent.parent
            core_files = [
                base_dir / "jpapi",
                base_dir / "utilities" / "jpapi_core_modular",
                base_dir / "src" / "core" / "auth" / "unified_auth.py",
                base_dir / "src" / "cli" / "main.py",
            ]

            missing_files = [f for f in core_files if not f.exists()]
            files_status = "✅ OK" if len(missing_files) == 0 else "❌ MISSING"
            system_data.append(
                {
                    "Component": "Core Files",
                    "Status": files_status,
                    "Value": f"{len(core_files) - len(missing_files)}/{len(core_files)} files",
                    "Details": (
                        "All present"
                        if not missing_files
                        else f"Missing: {len(missing_files)} files"
                    ),
                }
            )

            # Authentication
            auth_status = "❌ N/A"
            auth_details = "Authentication not available"

            if hasattr(self, "auth") and self.auth:
                try:
                    if self.auth.is_configured():
                        auth_status = "✅ OK"
                        auth_details = "Authentication configured"
                    else:
                        auth_status = "⚠️ NOT CONFIGURED"
                        auth_details = "Run: jpapi auth setup"
                except Exception:
                    auth_status = "❌ ERROR"
                    auth_details = "Authentication error"

            system_data.append(
                {
                    "Component": "Authentication",
                    "Status": auth_status,
                    "Value": "JAMF Pro API",
                    "Details": auth_details,
                }
            )

            # Detailed info if requested
            if getattr(args, "detailed", False):
                # Add more detailed system information
                try:
                    # CPU info
                    import psutil

                    cpu_count = psutil.cpu_count()
                    cpu_percent = psutil.cpu_percent(interval=1)
                    system_data.append(
                        {
                            "Component": "CPU Usage",
                            "Status": "✅ OK" if cpu_percent < 80 else "⚠️ HIGH",
                            "Value": f"{cpu_percent:.1f}%",
                            "Details": f"{cpu_count} cores",
                        }
                    )
                except ImportError:
                    pass

                # Network connectivity
                try:
                    import urllib.request

                    urllib.request.urlopen("https://www.google.com", timeout=5)
                    system_data.append(
                        {
                            "Component": "Network",
                            "Status": "✅ OK",
                            "Value": "Connected",
                            "Details": "Internet connectivity available",
                        }
                    )
                except Exception:
                    system_data.append(
                        {
                            "Component": "Network",
                            "Status": "⚠️ LIMITED",
                            "Value": "Limited",
                            "Details": "Internet connectivity issues",
                        }
                    )

            # Output results
            output = self.format_output(system_data, args.format)
            self.save_output(output, args.output)

            # Overall health summary
            error_count = len([item for item in system_data if "❌" in item["Status"]])
            warning_count = len([item for item in system_data if "⚠️" in item["Status"]])

            print(f"\n🎯 Overall System Health:")
            if error_count > 0:
                print(
                    f"   ❌ Issues Found: {error_count} errors, {warning_count} warnings"
                )
            elif warning_count > 0:
                print(f"   ⚠️ Warnings: {warning_count} items need attention")
            else:
                print(f"   ✅ All Systems Operational")

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _show_version_info(self, args: Namespace) -> int:
        """Show version and build information"""
        try:
            print("📋 jpapi Version Information")
            print("=" * 50)

            version_data = []

            # Version info
            version_data.append(
                {
                    "Component": "jpapi Version",
                    "Value": "2.0.0 (Modular)",
                    "Description": "Current toolkit version",
                }
            )

            version_data.append(
                {
                    "Component": "Architecture",
                    "Value": "Hybrid CLI (Bash + Python)",
                    "Description": "Fast operations in Bash, complex in Python",
                }
            )

            version_data.append(
                {
                    "Component": "Python Version",
                    "Value": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "Description": "Python interpreter version",
                }
            )

            # Build info
            base_dir = Path(__file__).parent.parent.parent.parent

            version_data.append(
                {
                    "Component": "Installation Path",
                    "Value": str(base_dir),
                    "Description": "Toolkit installation directory",
                }
            )

            # Count components
            command_count = len(
                list((base_dir / "src" / "cli" / "commands").glob("*_command.py"))
            )
            streamlit_count = len(
                list((base_dir / "src" / "streamlit_apps").glob("*.py"))
            )
            dashboard_count = len(list((base_dir / "src" / "dashboards").glob("*.py")))

            version_data.append(
                {
                    "Component": "CLI Commands",
                    "Value": str(command_count),
                    "Description": "Available CLI commands",
                }
            )

            version_data.append(
                {
                    "Component": "Streamlit Apps",
                    "Value": str(streamlit_count),
                    "Description": "Interactive web dashboards",
                }
            )

            version_data.append(
                {
                    "Component": "Dashboard Components",
                    "Value": str(dashboard_count),
                    "Description": "Specialized dashboard tools",
                }
            )

            # Features
            features = [
                "Modular CLI Architecture",
                "Comprehensive Alias System",
                "Conversational Command Patterns",
                "Unified Authentication",
                "Multi-tier Caching",
                "Web Dashboard Integration",
                "Export to Multiple Formats",
                "Advanced Search Capabilities",
                "Bulk Operations Support",
                "Health Monitoring",
            ]

            version_data.append(
                {
                    "Component": "Key Features",
                    "Value": f"{len(features)} features",
                    "Description": ", ".join(features[:3]) + "...",
                }
            )

            # Output results
            output = self.format_output(version_data, args.format)
            self.save_output(output, args.output)

            print(f"\n🚀 jpapi - JAMF Pro API Development Toolkit")
            print(f"   A comprehensive, modular toolkit for JAMF Pro management")
            print(f"   Combining CLI efficiency with web dashboard power")

            return 0

        except Exception as e:
            return self.handle_api_error(e)
