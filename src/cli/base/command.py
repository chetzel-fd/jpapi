#!/usr/bin/env python3
"""
Base Command Class for jpapi CLI
Uses composition with extracted components for SRP compliance
"""

from abc import ABC
from typing import Optional
from argparse import ArgumentParser, Namespace

from core.auth.login_factory import get_best_auth
from resources.config.central_config import central_config
from core.auth.login_types import AuthInterface
from core.logging.command_mixin import LoggingCommandMixin

from .output_formatter import OutputFormatter
from .safety_validator import SafetyValidator
from .pattern_matcher import PatternMatcher, CommandPattern


class BaseCommand(ABC, LoggingCommandMixin):
    """Base class for all CLI commands with composition for SRP compliance"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._auth: Optional[AuthInterface] = None
        self.environment = central_config.environments.default

        # Composed components (SRP)
        self.output_formatter = OutputFormatter()
        self.safety_validator = SafetyValidator()
        self.pattern_matcher = PatternMatcher()

        # Initialize logging mixin
        LoggingCommandMixin.__init__(self)

        # Setup patterns (template method)
        self._setup_patterns()

    def _setup_patterns(self):
        """Override in subclasses to define conversational patterns"""
        pass

    @property
    def auth(self) -> AuthInterface:
        """Get authenticated instance (lazy loading)"""
        if self._auth is None:
            raw_env = getattr(self, "environment", central_config.environments.default)
            environment = central_config.normalize_environment(raw_env)
            self._auth = get_best_auth(environment)
        return self._auth

    # Convenience methods that delegate to pattern_matcher
    def add_conversational_pattern(self, *args, **kwargs):
        """Add a conversational pattern"""
        return self.pattern_matcher.add_conversational_pattern(*args, **kwargs)

    def add_subcommand_config(self, *args, **kwargs):
        """Add subcommand configuration"""
        return self.pattern_matcher.add_subcommand_config(*args, **kwargs)

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Enhanced argument parsing with conversational and traditional support
        """
        # Add common arguments first
        self.setup_common_args(parser)

        # Create subcommands using configuration
        if self.pattern_matcher.has_subcommands():
            subparsers = parser.add_subparsers(
                dest="subcommand", help=f"{self.name.title()} operations"
            )
            self._create_subcommands(subparsers)

        # Support flexible positional arguments for conversational patterns
        if not self.pattern_matcher.has_subcommands():
            parser.add_argument(
                "target",
                nargs="?",
                help=f"What to {self.name} (supports natural language)",
            )
            parser.add_argument("action", nargs="?", help="Action to perform")
            parser.add_argument(
                "terms", nargs="*", help="Additional terms or identifiers"
            )

    def _create_subcommands(self, subparsers):
        """Create subcommands from configuration"""
        for config in self.pattern_matcher.subcommand_configs:
            # Create parser for main command name
            parser = subparsers.add_parser(config.name, help=config.description)

            # Add arguments
            for arg_config in config.arguments:
                self._add_argument_from_config(parser, arg_config)

            # Add common args
            self.setup_common_args(parser)

    def _add_argument_from_config(self, parser: ArgumentParser, arg_config: dict):
        """Add argument from configuration dictionary"""
        name = arg_config.pop("name")
        parser.add_argument(name, **arg_config)

    def execute(self, args: Namespace) -> int:
        """Enhanced execution with conversational pattern matching"""
        if not self.check_auth(args):
            return 1

        try:
            # Try conversational patterns first
            if hasattr(args, "target") and args.target:
                return self._handle_conversational_pattern(args)

            # Fall back to traditional subcommand structure
            if hasattr(args, "subcommand") and args.subcommand:
                return self._handle_subcommand(args)

            # Show help if no pattern matched
            self._show_help()
            return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_conversational_pattern(self, args: Namespace) -> int:
        """Handle conversational command patterns"""
        target, action, terms = self.pattern_matcher.parse_conversational_args(args)
        pattern_string = self.pattern_matcher.build_pattern_string(
            target, action, terms
        )

        # Find matching pattern
        matched_pattern = self.pattern_matcher.find_matching_pattern(
            pattern_string, target, action
        )

        if matched_pattern:
            print(f"🔍 {matched_pattern.description}")
            return self._execute_handler(matched_pattern.handler, args, matched_pattern)
        else:
            # Check if action is a numeric ID - if so, try with just target
            if action and str(action).isdigit():
                # Try to find pattern with just the target (e.g., "scripts")
                target_pattern = self.pattern_matcher.find_matching_pattern(
                    target, target, None
                )
                if target_pattern:
                    print(f"🔍 {target_pattern.description}")
                    return self._execute_handler(
                        target_pattern.handler, args, target_pattern
                    )

            print(f"❌ Could not understand: {pattern_string}")
            self._show_suggestions(pattern_string)
            return 1

    def _execute_handler(
        self, handler_name: str, args: Namespace, pattern: CommandPattern
    ) -> int:
        """Execute the handler method"""
        if hasattr(self, handler_name):
            handler_method = getattr(self, handler_name)
            return handler_method(args, pattern)
        else:
            print(f"❌ Handler method not found: {handler_name}")
            return 1

    def _handle_subcommand(self, args: Namespace) -> int:
        """Handle traditional subcommand structure"""
        subcommand = args.subcommand
        config = self.pattern_matcher.find_subcommand_config(subcommand)

        if not config:
            print(f"❌ Unknown subcommand: {subcommand}")
            return 1

        # Execute the handler method
        if hasattr(self, config.handler_method):
            handler_method = getattr(self, config.handler_method)
            return handler_method(args)
        else:
            print(f"❌ Handler method not found: {config.handler_method}")
            return 1

    def _show_help(self):
        """Show comprehensive help for the command"""
        print(f"📋 {self.description}")
        print()

        if self.pattern_matcher.has_conversational_patterns():
            print("💬 Conversational Commands:")
            for pattern in self.pattern_matcher.conversational_patterns:
                print(f"   jpapi {self.name} {pattern.pattern}")
                if pattern.description:
                    print(f"      {pattern.description}")
                if pattern.aliases:
                    print(f"      Aliases: {', '.join(pattern.aliases)}")
                print()

        if self.pattern_matcher.has_subcommands():
            print("🔧 Traditional Commands:")
            for config in self.pattern_matcher.subcommand_configs:
                print(f"   jpapi {self.name} {config.name}")
                print(f"      {config.description}")
                if config.aliases:
                    print(f"      Aliases: {', '.join(config.aliases)}")
                print()

    def _show_suggestions(self, pattern_string: str):
        """Show suggestions for unrecognized patterns"""
        print("\n💡 Did you mean:")

        suggestions = self.pattern_matcher.get_suggestions(pattern_string)
        for pattern in suggestions:
            print(f"   jpapi {self.name} {pattern.pattern}")

        if not suggestions:
            print("   Try 'jpapi help' for available commands")

    def setup_common_args(self, parser: ArgumentParser) -> None:
        """Add common arguments that all commands might need"""
        parser.add_argument(
            "--format",
            choices=["table", "json", "csv"],
            default="csv",
            help="Output format",
        )
        parser.add_argument("--output", help="Output file path")
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Verbose output"
        )
        parser.add_argument(
            "--filter", help="Filter results (supports wildcards: *, ?)"
        )
        parser.add_argument(
            "--filter-type",
            choices=["wildcard", "regex", "exact", "contains"],
            default="wildcard",
            help="Type of filtering to use",
        )
        parser.add_argument(
            "--status",
            choices=["enabled", "disabled", "all"],
            default="all",
            help="Filter by status (for policies)",
        )

        # Only add dry-run and force if they don't already exist
        existing_actions = [action.dest for action in parser._actions]
        if "dry_run" not in existing_actions:
            parser.add_argument(
                "--dry-run",
                action="store_true",
                help="Show what would be created without actually creating it",
            )
        if "force" not in existing_actions:
            parser.add_argument(
                "--force",
                action="store_true",
                help="Skip production confirmation prompts (use with caution)",
            )

    def check_auth(self, args: Namespace) -> bool:
        """Check if authentication is configured"""
        if hasattr(args, "environment"):
            self.environment = args.environment

        if not self.auth.is_configured():
            print(
                f"❌ Authentication not configured for environment: {self.environment}"
            )
            print(f"   Run: jpapi auth setup {self.environment}")
            return False
        return True

    # Delegate output formatting to OutputFormatter
    def format_output(self, data, format_type: str = "table") -> str:
        """Format output data (delegates to OutputFormatter)"""
        return self.output_formatter.format_output(data, format_type)

    def save_output(self, content: str, output_path: Optional[str] = None) -> None:
        """Save output to file or print (delegates to OutputFormatter)"""
        success, message = self.output_formatter.save_output(content, output_path)
        if message:
            print(message)

    def handle_api_error(self, error: Exception) -> int:
        """Handle API errors consistently"""
        error_msg = str(error)

        if "401" in error_msg or "Authentication" in error_msg:
            print("❌ Authentication failed. Please check your credentials.")
            print("   Run: jpapi auth setup")
            return 1
        elif "403" in error_msg:
            print("❌ Access denied. Check your permissions.")
            return 1
        elif "404" in error_msg:
            print("❌ Resource not found.")
            return 1
        elif "timeout" in error_msg.lower():
            print("❌ Request timed out. Please try again.")
            return 1
        else:
            print(f"❌ API Error: {error_msg}")
            return 1

    # Delegate production safety to SafetyValidator
    def is_production_environment(self) -> bool:
        """Check if current environment is production"""
        return self.safety_validator.is_production_environment(self.environment)

    def require_production_confirmation(
        self,
        operation: str,
        details: str = "",
        changes_summary: str = "",
        args: Optional[Namespace] = None,
    ) -> bool:
        """Require explicit confirmation for production operations"""
        return self.safety_validator.require_production_confirmation(
            self.environment, operation, details, changes_summary, args
        )

    def require_dry_run_confirmation(self, operation: str) -> bool:
        """Suggest dry-run mode for production operations"""
        return self.safety_validator.require_dry_run_confirmation(
            self.environment, operation
        )

    def check_destructive_operation(
        self, operation: str, resource_name: str = ""
    ) -> bool:
        """Check if operation is destructive and requires extra confirmation"""
        return self.safety_validator.check_destructive_operation(
            self.environment, operation, resource_name
        )

    def create_bulk_changes_summary(self, operation_type: str, objects: list) -> str:
        """Create a comprehensive summary for bulk operations"""
        return self.safety_validator.create_bulk_changes_summary(
            operation_type, objects
        )
