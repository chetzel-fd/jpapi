#!/usr/bin/env python3
"""
Main CLI Runner for jpapi
Clean modular architecture with SOLID principles
"""
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# No sys.path hacks - proper package imports with pure src/ layout
from cli.base import registry
from cli.commands import (
    ListCommand,
    ExportCommand,
    SearchCommand,
    ToolsCommand,
    DevicesCommand,
    CreateCommand,
    MoveCommand,
    InfoCommand,
    ExperimentalCommand,
    ScriptsCommand,
    UpdateCommand,
    InstallomatorCommand,
    PPPCCommand,
    ManifestCommand,
)
from cli.commands.setup_command import SetupCommand
from cli.commands.backup_command import BackupCommand
from cli.commands.advanced_searches_command import AdvancedSearchesCommand
from cli.commands.extension_attributes_command import ExtensionAttributesCommand
from cli.commands.mobile_apps_command import MobileAppsCommand
from cli.commands.packages_command import PackagesCommand
from cli.commands.delete_command import DeleteCommand
from cli.commands.profiles_scoped_command import ProfilesScopedCommand
from cli.commands.safety_command import SafetyCommand
from cli.commands.roles_command import RolesCommand


class JPAPIDevCLI:
    """Main CLI application with modular command architecture"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent

        # Register commands
        self._register_commands()

    def _register_commands(self):
        """Register all available commands"""
        # Register list command with aliases
        registry.register(ListCommand, aliases=["ls", "show"])

        # Register export command with aliases
        registry.register(ExportCommand, aliases=["exp", "export-data", "dump"])

        # Register search command with aliases
        registry.register(SearchCommand, aliases=["find", "query"])

        # Register tools command with aliases
        registry.register(ToolsCommand, aliases=["tool", "util", "utils"])

        # Register devices command with aliases
        registry.register(DevicesCommand, aliases=["device", "dev"])

        # Register create command with aliases
        registry.register(CreateCommand, aliases=["add", "new"])

        # Register delete command with aliases
        registry.register(DeleteCommand, aliases=["del", "remove", "rm"])

        # Register move command with aliases
        registry.register(MoveCommand, aliases=["mv", "transfer"])

        # Register info command with aliases
        registry.register(InfoCommand, aliases=["help", "about"])

        # Register experimental command with aliases
        registry.register(ExperimentalCommand, aliases=["exp", "beta"])

        # Register scripts command with aliases
        registry.register(ScriptsCommand, aliases=["script", "download-scripts"])

        # Register backup command with aliases
        registry.register(BackupCommand, aliases=["backup-data", "backup-all"])

        # Register update command with aliases
        registry.register(UpdateCommand, aliases=["sync", "apply"])

        # Register list profiles scoped command with aliases
        registry.register(
            ProfilesScopedCommand,
            aliases=["list-scoped", "scoped-profiles", "profiles-scoped"],
        )

        # Register safety command with aliases
        registry.register(SafetyCommand, aliases=["guard", "guardrails", "prod-safety"])

        # Register roles command with aliases
        registry.register(RolesCommand, aliases=["role", "permissions", "access"])

        # Register new Phase 1 commands
        registry.register(
            AdvancedSearchesCommand, aliases=["advanced-search", "searches"]
        )
        registry.register(
            ExtensionAttributesCommand,
            aliases=["extension-attributes", "ext-attributes", "attributes"],
        )
        registry.register(
            MobileAppsCommand, aliases=["mobile-apps", "mobileapps", "apps"]
        )

        # Register Phase 2 commands
        registry.register(PackagesCommand, aliases=["package", "pkg", "packages"])

        # Register Installomator command with aliases
        registry.register(
            InstallomatorCommand, aliases=["installomator", "installer", "apps"]
        )

        # Register PPPC command with aliases
        registry.register(
            PPPCCommand, aliases=["pppc", "privacy", "tcc", "pppc-scanner"]
        )

        # Register Manifest command with aliases
        registry.register(
            ManifestCommand, aliases=["manifest", "manifests", "profiles-manifest"]
        )

        # Register setup command with aliases
        registry.register(SetupCommand, aliases=["configure", "config", "init"])

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser"""
        parser = argparse.ArgumentParser(
            prog="jpapi",
            description="📱 JAMF Pro API Development CLI - Modular Architecture",
            epilog='Use "jpapi <command> --help" for more information on a specific command.',
        )

        # Global arguments
        parser.add_argument(
            "--env", default="dev", help="JAMF environment (dev, prod, etc.)"
        )
        parser.add_argument(
            "--experimental", action="store_true", help="Enable experimental features"
        )
        parser.add_argument(
            "--version", action="version", version="jpapi 2.0.0 (modular)"
        )

        # Add subparsers for commands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Register only main commands in help
        for command_name in registry.list_commands():
            command_class = registry.get_command(command_name)
            command_instance = command_class()

            # Show aliases in the help text
            aliases = [
                alias
                for alias, cmd in registry.list_aliases().items()
                if cmd == command_name
            ]
            help_text = command_instance.description
            if aliases:
                help_text += f" (aliases: {', '.join(aliases[:3])}{'...' if len(aliases) > 3 else ''})"

            # Create subparser for main command
            command_parser = subparsers.add_parser(command_name, help=help_text)

            # Add command-specific arguments
            command_instance.add_arguments(command_parser)

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI application"""
        # Handle alias resolution before parsing
        if args is None:
            args = sys.argv[1:]  # Get command line args if none provided

        if args and len(args) > 0:
            first_arg = args[0]
            if first_arg in registry.list_aliases():
                # Replace alias with actual command
                actual_command = registry.list_aliases()[first_arg]
                args = [actual_command] + args[1:]

        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        # Show help if no command specified
        if not parsed_args.command:
            parser.print_help()
            return 0

        try:
            # Get command class and create instance
            command_class = registry.get_command(parsed_args.command)
            command_instance = command_class()

            # Set environment on command instance
            if hasattr(parsed_args, "env"):
                command_instance.environment = parsed_args.env

            # Execute command
            return command_instance.execute(parsed_args)

        except ValueError as e:
            print(f"❌ {e}")

            # Suggest similar commands
            available_commands = registry.list_commands()
            aliases = registry.list_aliases()

            print(f"\nAvailable commands: {', '.join(available_commands)}")
            if aliases:
                print(
                    f"Command aliases: {', '.join(f'{alias}→{cmd}' for alias, cmd in aliases.items())}"
                )

            return 1
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if "--debug" in sys.argv:
                import traceback

                traceback.print_exc()
            return 1


def main():
    """Main entry point"""
    cli = JPAPIDevCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
