#!/usr/bin/env python3
"""
CLI Command: Configuration Management
Manage JPAPI centralized configuration system
"""
import json
import sys
from pathlib import Path
from typing import List, Optional
from argparse import Namespace

# Using proper package structure via pip install -e .

from cli.base.command import BaseCommand

try:
    from config.central_config import central_config, get_port, get_timeout, get_path
    from config.central_config import (
        ServerPorts,
        Environments,
        OutputFormats,
        Paths,
        Timeouts,
        Version,
        Logging,
        Users,
        Authentication,
        ExperimentalFeatures,
        AddonConfiguration,
        CacheConfiguration,
        ExportConfiguration,
        APIConfiguration,
    )
except ImportError:
    central_config = None


class ConfigCommand(BaseCommand):
    """Configuration management command"""

    def __init__(self):
        super().__init__("config", "Manage JPAPI centralized configuration system")

    def get_name(self) -> str:
        return "config"

    def get_description(self) -> str:
        return "Manage JPAPI centralized configuration system"

    def add_arguments(self, parser):
        """Add command arguments"""
        subparsers = parser.add_subparsers(dest="action", help="Configuration actions")

        # Show command
        show_parser = subparsers.add_parser("show", help="Show current configuration")
        show_parser.add_argument(
            "--section", help="Show specific section (ports, paths, timeouts, etc.)"
        )
        show_parser.add_argument(
            "--format",
            choices=["table", "json", "yaml"],
            default="table",
            help="Output format",
        )

        # Set command
        set_parser = subparsers.add_parser("set", help="Set configuration value")
        set_parser.add_argument(
            "section", help="Configuration section (ports, paths, timeouts, etc.)"
        )
        set_parser.add_argument("key", help="Configuration key")
        set_parser.add_argument("value", help="New value")

        # Get command
        get_parser = subparsers.add_parser("get", help="Get configuration value")
        get_parser.add_argument("section", help="Configuration section")
        get_parser.add_argument("key", help="Configuration key")

        # Reset command
        reset_parser = subparsers.add_parser(
            "reset", help="Reset configuration to defaults"
        )
        reset_parser.add_argument("--section", help="Reset specific section only")
        reset_parser.add_argument(
            "--confirm", action="store_true", help="Skip confirmation prompt"
        )

        # Export command
        export_parser = subparsers.add_parser(
            "export", help="Export configuration to file"
        )
        export_parser.add_argument("output_file", help="Output file path")
        export_parser.add_argument(
            "--format", choices=["json", "yaml"], default="json", help="Export format"
        )

        # Import command
        import_parser = subparsers.add_parser(
            "import", help="Import configuration from file"
        )
        import_parser.add_argument("input_file", help="Input file path")
        import_parser.add_argument(
            "--confirm", action="store_true", help="Skip confirmation prompt"
        )

        # Validate command
        validate_parser = subparsers.add_parser(
            "validate", help="Validate configuration"
        )
        validate_parser.add_argument(
            "--fix", action="store_true", help="Attempt to fix validation issues"
        )

        # GUI command
        gui_parser = subparsers.add_parser("gui", help="Launch configuration GUI")
        gui_parser.add_argument(
            "--background", action="store_true", help="Run GUI in background"
        )

    def execute(self, args: Namespace) -> int:
        """Execute the config command"""
        if not central_config:
            print("❌ Centralized configuration system not available")
            print("   Please ensure the configuration system is properly installed")
            return 1

        try:
            if not args.action:
                self._show_help()
                return 1

            if args.action == "show":
                return self._handle_show(args)
            elif args.action == "set":
                return self._handle_set(args)
            elif args.action == "get":
                return self._handle_get(args)
            elif args.action == "reset":
                return self._handle_reset(args)
            elif args.action == "export":
                return self._handle_export(args)
            elif args.action == "import":
                return self._handle_import(args)
            elif args.action == "validate":
                return self._handle_validate(args)
            elif args.action == "gui":
                return self._handle_gui(args)
            else:
                print(f"❌ Unknown action: {args.action}")
                return 1

        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    def _show_help(self):
        """Show help information"""
        print("🔧 JPAPI Configuration Management")
        print()
        print("Available actions:")
        print("  show     - Show current configuration")
        print("  set      - Set configuration value")
        print("  get      - Get configuration value")
        print("  reset    - Reset to defaults")
        print("  export   - Export configuration")
        print("  import   - Import configuration")
        print("  validate - Validate configuration")
        print("  gui      - Launch configuration GUI")
        print()
        print("Examples:")
        print("  jpapi config show")
        print("  jpapi config set ports backend_fast 8600")
        print("  jpapi config get timeouts api_timeout")
        print("  jpapi config reset --section ports")
        print("  jpapi config export config_backup.json")
        print("  jpapi config gui")

    def _handle_show(self, args: Namespace) -> int:
        """Handle show command"""
        if args.section:
            # Show specific section
            section_data = self._get_section_data(args.section)
            if section_data is None:
                print(f"❌ Unknown section: {args.section}")
                return 1

            if args.format == "json":
                print(json.dumps(section_data, indent=2))
            elif args.format == "yaml":
                import yaml

                print(yaml.dump(section_data, default_flow_style=False))
            else:
                self._print_section_table(args.section, section_data)
        else:
            # Show all sections
            sections = [
                "ports",
                "environments",
                "formats",
                "paths",
                "timeouts",
                "version",
                "logging",
                "users",
                "authentication",
                "experimental",
                "addons",
                "cache",
                "export",
                "api",
            ]
            for section in sections:
                print(f"\n📋 {section.upper()}:")
                section_data = self._get_section_data(section)
                if section_data:
                    if args.format == "json":
                        print(json.dumps(section_data, indent=2))
                    elif args.format == "yaml":
                        import yaml

                        print(yaml.dump(section_data, default_flow_style=False))
                    else:
                        self._print_section_table(section, section_data)

        return 0

    def _handle_set(self, args: Namespace) -> int:
        """Handle set command"""
        try:
            # Convert value to appropriate type
            value = self._convert_value(args.value)

            # Update configuration
            central_config.update_config(args.section, args.key, value)

            print(f"✅ Set {args.section}.{args.key} = {value}")
            return 0
        except Exception as e:
            print(f"❌ Failed to set {args.section}.{args.key}: {e}")
            return 1

    def _handle_get(self, args: Namespace) -> int:
        """Handle get command"""
        try:
            section_data = self._get_section_data(args.section)
            if section_data is None:
                print(f"❌ Unknown section: {args.section}")
                return 1

            if args.key not in section_data:
                print(f"❌ Key {args.key} not found in section {args.section}")
                return 1

            value = section_data[args.key]
            print(f"{args.section}.{args.key} = {value}")
            return 0
        except Exception as e:
            print(f"❌ Failed to get {args.section}.{args.key}: {e}")
            return 1

    def _handle_reset(self, args: Namespace) -> int:
        """Handle reset command"""
        if not args.confirm:
            if (
                not input("Are you sure you want to reset configuration? (y/N): ")
                .lower()
                .startswith("y")
            ):
                print("Reset cancelled")
                return 0

        try:
            if args.section:
                # Reset specific section
                self._reset_section(args.section)
                print(f"✅ Reset section {args.section} to defaults")
            else:
                # Reset all sections
                central_config.reset_to_defaults()
                print("✅ Reset all configuration to defaults")
            return 0
        except Exception as e:
            print(f"❌ Failed to reset configuration: {e}")
            return 1

    def _handle_export(self, args: Namespace) -> int:
        """Handle export command"""
        try:
            central_config.export_config(args.output_file)
            print(f"✅ Configuration exported to {args.output_file}")
            return 0
        except Exception as e:
            print(f"❌ Failed to export configuration: {e}")
            return 1

    def _handle_import(self, args: Namespace) -> int:
        """Handle import command"""
        if not args.confirm:
            if (
                not input("Are you sure you want to import configuration? (y/N): ")
                .lower()
                .startswith("y")
            ):
                print("Import cancelled")
                return 0

        try:
            central_config.import_config(args.input_file)
            print(f"✅ Configuration imported from {args.input_file}")
            return 0
        except Exception as e:
            print(f"❌ Failed to import configuration: {e}")
            return 1

    def _handle_validate(self, args: Namespace) -> int:
        """Handle validate command"""
        try:
            issues = self._validate_configuration()
            if not issues:
                print("✅ Configuration is valid")
                return 0
            else:
                print("❌ Configuration validation issues found:")
                for issue in issues:
                    print(f"  - {issue}")

                if args.fix:
                    print("\n🔧 Attempting to fix issues...")
                    self._fix_configuration_issues(issues)
                    print("✅ Issues fixed")

                return 1
        except Exception as e:
            print(f"❌ Failed to validate configuration: {e}")
            return 1

    def _handle_gui(self, args: Namespace) -> int:
        """Handle GUI command"""
        try:
            import subprocess

            gui_script = (
                Path(__file__).parent.parent.parent.parent / "gui" / "launch_gui.py"
            )

            if not gui_script.exists():
                print("❌ GUI script not found")
                return 1

            if args.background:
                # Run in background
                subprocess.Popen([sys.executable, str(gui_script)])
                print("✅ GUI launched in background")
            else:
                # Run in foreground
                subprocess.run([sys.executable, str(gui_script)])

            return 0
        except Exception as e:
            print(f"❌ Failed to launch GUI: {e}")
            return 1

    def _get_section_data(self, section: str) -> Optional[dict]:
        """Get data for a specific section"""
        if section == "ports":
            return {
                "backend_fast": central_config.ports.backend_fast,
                "backend_enhanced": central_config.ports.backend_enhanced,
                "redis": central_config.ports.redis,
                "dashboard": central_config.ports.dashboard,
                "api_docs": central_config.ports.api_docs,
            }
        elif section == "environments":
            return {
                "default": central_config.environments.default,
                "available": central_config.environments.available,
                "aliases": central_config.environments.aliases,
            }
        elif section == "formats":
            return {
                "data_formats": central_config.formats.data_formats,
                "status_options": central_config.formats.status_options,
                "filter_types": central_config.formats.filter_types,
                "default_format": central_config.formats.default_format,
            }
        elif section == "paths":
            return {
                "cache_dir": central_config.paths.cache_dir,
                "config_dir": central_config.paths.config_dir,
                "data_dir": central_config.paths.data_dir,
                "logs_dir": central_config.paths.logs_dir,
                "temp_dir": central_config.paths.temp_dir,
            }
        elif section == "timeouts":
            return {
                "api_timeout": central_config.timeouts.api_timeout,
                "cache_timeout": central_config.timeouts.cache_timeout,
                "operation_timeout": central_config.timeouts.operation_timeout,
                "connection_timeout": central_config.timeouts.connection_timeout,
                "retry_timeout": central_config.timeouts.retry_timeout,
                "bash_operation_timeout": central_config.timeouts.bash_operation_timeout,
                "python_operation_timeout": central_config.timeouts.python_operation_timeout,
            }
        elif section == "version":
            return {
                "version": central_config.version.version,
                "build": central_config.version.build,
                "architecture": central_config.version.architecture,
                "api_version": central_config.version.api_version,
            }
        elif section == "logging":
            return {
                "default_level": central_config.logging.default_level,
                "available_levels": central_config.logging.available_levels,
                "component_levels": central_config.logging.component_levels,
            }
        elif section == "users":
            return {
                "default_signature": central_config.users.default_signature,
                "available_users": central_config.users.available_users,
                "user_roles": central_config.users.user_roles,
            }
        elif section == "authentication":
            return {
                "jamf_url": central_config.authentication.jamf_url,
                "auth_method": central_config.authentication.auth_method,
                "oauth_client_id": central_config.authentication.oauth_client_id,
                "oauth_client_secret": (
                    "***" if central_config.authentication.oauth_client_secret else ""
                ),
                "oauth_redirect_uri": central_config.authentication.oauth_redirect_uri,
                "basic_username": central_config.authentication.basic_username,
                "basic_password": (
                    "***" if central_config.authentication.basic_password else ""
                ),
                "prefer_oauth": central_config.authentication.prefer_oauth,
                "fallback_to_basic": central_config.authentication.fallback_to_basic,
                "auto_refresh_tokens": central_config.authentication.auto_refresh_tokens,
                "token_cache_duration": central_config.authentication.token_cache_duration,
            }
        elif section == "experimental":
            return {
                "enable_dashboards": central_config.experimental.enable_dashboards,
                "enable_real_time_dashboard": central_config.experimental.enable_real_time_dashboard,
                "enable_analytics_dashboard": central_config.experimental.enable_analytics_dashboard,
                "enable_computer_groups_dashboard": central_config.experimental.enable_computer_groups_dashboard,
                "enable_mobile_devices_dashboard": central_config.experimental.enable_mobile_devices_dashboard,
                "enable_advanced_relationships": central_config.experimental.enable_advanced_relationships,
                "enable_pppc_scanner": central_config.experimental.enable_pppc_scanner,
                "enable_profile_manifests": central_config.experimental.enable_profile_manifests,
                "enable_installomator": central_config.experimental.enable_installomator,
                "enable_debug_mode": central_config.experimental.enable_debug_mode,
                "enable_verbose_logging": central_config.experimental.enable_verbose_logging,
                "enable_performance_metrics": central_config.experimental.enable_performance_metrics,
            }
        elif section == "addons":
            return {
                "installomator_enabled": central_config.addons.installomator_enabled,
                "installomator_repo_url": central_config.addons.installomator_repo_url,
                "installomator_script_path": central_config.addons.installomator_script_path,
                "installomator_timeout": central_config.addons.installomator_timeout,
                "pppc_scanner_enabled": central_config.addons.pppc_scanner_enabled,
                "pppc_scanner_output_dir": central_config.addons.pppc_scanner_output_dir,
                "pppc_scanner_include_system": central_config.addons.pppc_scanner_include_system,
                "pppc_scanner_include_user": central_config.addons.pppc_scanner_include_user,
                "profile_manifests_enabled": central_config.addons.profile_manifests_enabled,
                "profile_manifests_output_dir": central_config.addons.profile_manifests_output_dir,
                "profile_manifests_include_metadata": central_config.addons.profile_manifests_include_metadata,
                "profile_manifests_auto_update": central_config.addons.profile_manifests_auto_update,
            }
        elif section == "cache":
            return {
                "cache_enabled": central_config.cache.cache_enabled,
                "cache_duration": central_config.cache.cache_duration,
                "cache_max_size": central_config.cache.cache_max_size,
                "cache_cleanup_interval": central_config.cache.cache_cleanup_interval,
                "api_cache_ttl": central_config.cache.api_cache_ttl,
                "relationship_cache_ttl": central_config.cache.relationship_cache_ttl,
                "object_detail_cache_ttl": central_config.cache.object_detail_cache_ttl,
                "cache_storage_type": central_config.cache.cache_storage_type,
                "cache_redis_url": central_config.cache.cache_redis_url,
            }
        elif section == "export":
            return {
                "default_export_directory": central_config.export.default_export_directory,
                "default_export_format": central_config.export.default_export_format,
                "include_metadata": central_config.export.include_metadata,
                "include_timestamps": central_config.export.include_timestamps,
                "available_formats": central_config.export.available_formats,
                "export_compression": central_config.export.export_compression,
                "export_encryption": central_config.export.export_encryption,
                "auto_create_directories": central_config.export.auto_create_directories,
                "overwrite_existing": central_config.export.overwrite_existing,
                "export_batch_size": central_config.export.export_batch_size,
            }
        elif section == "api":
            return {
                "max_retries": central_config.api.max_retries,
                "retry_delay": central_config.api.retry_delay,
                "request_timeout": central_config.api.request_timeout,
                "connection_pool_size": central_config.api.connection_pool_size,
                "rate_limit_enabled": central_config.api.rate_limit_enabled,
                "rate_limit_requests_per_minute": central_config.api.rate_limit_requests_per_minute,
                "rate_limit_burst_size": central_config.api.rate_limit_burst_size,
                "auto_retry_failed_requests": central_config.api.auto_retry_failed_requests,
                "cache_api_responses": central_config.api.cache_api_responses,
                "follow_redirects": central_config.api.follow_redirects,
                "verify_ssl": central_config.api.verify_ssl,
            }
        return None

    def _print_section_table(self, section: str, data: dict):
        """Print section data as a table"""
        print(f"{'Key':<25} {'Value':<30}")
        print("-" * 55)
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                value = str(value)
            print(f"{key:<25} {str(value):<30}")

    def _convert_value(self, value: str):
        """Convert string value to appropriate type"""
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Try boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Return as string
        return value

    def _reset_section(self, section: str):
        """Reset a specific section to defaults"""
        if section == "ports":
            central_config.ports = ServerPorts()
        elif section == "environments":
            central_config.environments = Environments()
        elif section == "formats":
            central_config.formats = OutputFormats()
        elif section == "paths":
            central_config.paths = Paths()
        elif section == "timeouts":
            central_config.timeouts = Timeouts()
        elif section == "version":
            central_config.version = Version()
        elif section == "logging":
            central_config.logging = Logging()
        elif section == "users":
            central_config.users = Users()
        elif section == "authentication":
            central_config.authentication = Authentication()
        elif section == "experimental":
            central_config.experimental = ExperimentalFeatures()
        elif section == "addons":
            central_config.addons = AddonConfiguration()
        elif section == "cache":
            central_config.cache = CacheConfiguration()
        elif section == "export":
            central_config.export = ExportConfiguration()
        elif section == "api":
            central_config.api = APIConfiguration()

        central_config._save_config(f"{section}.json", getattr(central_config, section))

    def _validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []

        # Validate ports
        for port_name, port_value in [
            ("backend_fast", central_config.ports.backend_fast),
            ("backend_enhanced", central_config.ports.backend_enhanced),
            ("redis", central_config.ports.redis),
            ("dashboard", central_config.ports.dashboard),
            ("api_docs", central_config.ports.api_docs),
        ]:
            if not isinstance(port_value, int) or port_value < 1 or port_value > 65535:
                issues.append(f"Invalid port for {port_name}: {port_value}")

        # Validate timeouts
        for timeout_name, timeout_value in [
            ("api_timeout", central_config.timeouts.api_timeout),
            ("cache_timeout", central_config.timeouts.cache_timeout),
            ("operation_timeout", central_config.timeouts.operation_timeout),
        ]:
            if not isinstance(timeout_value, int) or timeout_value < 1:
                issues.append(f"Invalid timeout for {timeout_name}: {timeout_value}")

        # Validate log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if central_config.logging.default_level not in valid_levels:
            issues.append(
                f"Invalid default log level: {central_config.logging.default_level}"
            )

        return issues

    def _fix_configuration_issues(self, issues: List[str]):
        """Attempt to fix configuration issues"""
        # This is a placeholder for fixing common issues
        # In a real implementation, you would add logic to fix specific issues
        print("🔧 Fixing configuration issues...")
        # Add specific fix logic here based on the issues found
