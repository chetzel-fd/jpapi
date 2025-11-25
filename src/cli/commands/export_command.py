#!/usr/bin/env python3
"""
Export Command for jpapi CLI - DEPRECATED
This command is deprecated. Use 'list' command with --export-mode instead.
Redirects all calls to ListCommand for backward compatibility.
"""

from .common_imports import (
    ArgumentParser,
    Namespace,
    BaseCommand,
)
from .list_command import ListCommand
import sys


class ExportCommand(BaseCommand):
    """DEPRECATED: Export command that redirects to ListCommand

    This command is deprecated as of v2.0. The 'list' command now handles
    all export functionality with the --export-mode flag.

    For backward compatibility, this wrapper remains but will be removed
    in a future version.

    Migration:
        Old: jpapi export policies
        New: jpapi list policies --export-mode

    The 'export' alias for 'list' command provides seamless transition.
    """

    def __init__(self):
        super().__init__(
            name="export", description="📤 Export JAMF data (DEPRECATED - use list)"
        )
        # Create a ListCommand instance to delegate to
        self._list_command = ListCommand()
        # Copy patterns from list command
        self.pattern_matcher = self._list_command.pattern_matcher
        self._deprecation_shown = False

    def _setup_patterns(self):
        """Patterns are inherited from ListCommand"""
        pass

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Delegate argument parsing to ListCommand"""
        self._list_command.add_arguments(parser)

    def _show_deprecation_warning(self):
        """Show deprecation warning once per execution"""
        if not self._deprecation_shown:
            print("⚠️  DEPRECATION WARNING ⚠️")
            print("=" * 60)
            print("The 'export' command is deprecated and will be removed")
            print("in a future version. Please use 'list' command instead.")
            print()
            print("Migration:")
            print("  Old: jpapi export policies")
            print("  New: jpapi list policies --export-mode")
            print()
            print("Note: The 'export' alias for 'list' provides automatic")
            print("export mode, so 'jpapi export policies' still works but")
            print("uses 'list' under the hood.")
            print("=" * 60)
            print()
            self._deprecation_shown = True

    def execute(self, args: Namespace) -> int:
        """Execute export by delegating to ListCommand with deprecation warning"""
        # Show deprecation warning
        self._show_deprecation_warning()

        # Enable export mode for file saving with instance prefix
        args.export_mode = True

        # Default to CSV format for exports if no format specified
        if not hasattr(args, "format") or args.format == "table":
            args.format = "csv"

        # Set auth using protected attribute
        self._list_command._auth = self._auth
        self._list_command.environment = self.environment

        # Delegate to list command
        return self._list_command.execute(args)
