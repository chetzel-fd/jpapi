#!/usr/bin/env python3
"""
Base Command Class for jpapi CLI
Provides common functionality for all CLI commands
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, Callable
from argparse import ArgumentParser, Namespace
from pathlib import Path
import getpass
import re
from dataclasses import dataclass

# Using proper package structure via pip install -e .

from core.auth.login_factory import get_best_auth
from core.auth.login_types import AuthInterface
from core.checks.check_manager import SafetyManager
from core.logging.command_mixin import LoggingCommandMixin
from src.lib.utils import create_filter, FilterField


@dataclass
class CommandPattern:
    """Represents a conversational command pattern"""

    pattern: str
    handler: str
    description: str
    aliases: List[str] = None
    required_args: List[str] = None
    optional_args: Dict[str, Any] = None


@dataclass
class SubcommandConfig:
    """Configuration for subcommand creation"""

    name: str
    aliases: List[str]
    description: str
    handler_method: str
    arguments: List[Dict[str, Any]] = None


class BaseCommand(ABC, LoggingCommandMixin):
    """Base class for all CLI commands with logging capabilities"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._auth: Optional[AuthInterface] = None
        self.environment = "dev"  # Default environment
        self.safety_manager = SafetyManager()
        # Initialize logging mixin
        LoggingCommandMixin.__init__(self)

        # Configuration-driven patterns
        self.conversational_patterns: List[CommandPattern] = []
        self.subcommand_configs: List[SubcommandConfig] = []
        self._setup_patterns()

    def _setup_patterns(self):
        """Override in subclasses to define conversational patterns"""
        pass

    def add_conversational_pattern(
        self,
        pattern: str,
        handler: str,
        description: str,
        aliases: List[str] = None,
        required_args: List[str] = None,
        optional_args: Dict[str, Any] = None,
    ):
        """Add a conversational pattern"""
        self.conversational_patterns.append(
            CommandPattern(
                pattern=pattern,
                handler=handler,
                description=description,
                aliases=aliases or [],
                required_args=required_args or [],
                optional_args=optional_args or {},
            )
        )

    def add_subcommand_config(
        self,
        name: str,
        aliases: List[str],
        description: str,
        handler_method: str,
        arguments: List[Dict[str, Any]] = None,
    ):
        """Add subcommand configuration"""
        self.subcommand_configs.append(
            SubcommandConfig(
                name=name,
                aliases=aliases,
                description=description,
                handler_method=handler_method,
                arguments=arguments or [],
            )
        )

    @property
    def auth(self) -> AuthInterface:
        """Get authenticated instance (lazy loading)"""
        if self._auth is None:
            environment = getattr(self, "environment", "dev")
            self._auth = get_best_auth(environment)
        return self._auth

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Enhanced argument parsing with both conversational and traditional support"""
        # Add common arguments first
        self.setup_common_args(parser)

        # Create subcommands using configuration
        if self.subcommand_configs:
            subparsers = parser.add_subparsers(
                dest="subcommand", help=f"{self.name.title()} operations"
            )
            self._create_subcommands(subparsers)

        # Support flexible positional arguments for conversational patterns (only if no subcommands)
        if not self.subcommand_configs:
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
        for config in self.subcommand_configs:
            # Create parser for main command name
            parser = subparsers.add_parser(config.name, help=config.description)

            # Add arguments
            for arg_config in config.arguments:
                self._add_argument_from_config(parser, arg_config)

            # Add common args
            self.setup_common_args(parser)

    def _add_argument_from_config(
        self, parser: ArgumentParser, arg_config: Dict[str, Any]
    ):
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
        target = args.target.lower()
        action = args.action.lower() if args.action else ""
        terms = args.terms if args.terms else []

        # Build pattern string
        pattern_parts = [target]
        if action:
            pattern_parts.append(action)
        if terms:
            pattern_parts.extend(terms)

        pattern_string = " ".join(pattern_parts)

        # Find matching pattern
        matched_pattern = self._find_matching_pattern(pattern_string, target, action)

        if matched_pattern:
            print(f"🔍 {matched_pattern.description}")
            return self._execute_handler(matched_pattern.handler, args, matched_pattern)
        else:
            print(f"❌ Could not understand: {pattern_string}")
            self._show_suggestions(pattern_string)
            return 1

    def _find_matching_pattern(
        self, pattern_string: str, target: str, action: str
    ) -> Optional[CommandPattern]:
        """Find the best matching conversational pattern"""
        # Try exact match first
        for pattern in self.conversational_patterns:
            if pattern_string == pattern.pattern:
                return pattern

        # Try partial matches - check if all words in pattern_string are in pattern
        for pattern in self.conversational_patterns:
            pattern_words = pattern.pattern.split()
            input_words = pattern_string.split()

            # Check if all input words are in pattern words (more specific matching)
            if all(word in pattern_words for word in input_words):
                return pattern

            # Also check aliases
            if target in pattern.aliases:
                return pattern

        # Try action-based matching
        if action:
            for pattern in self.conversational_patterns:
                if action in pattern.pattern.split():
                    return pattern

        return None

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

        # Find the config for this subcommand
        config = None
        for cfg in self.subcommand_configs:
            if subcommand == cfg.name or subcommand in cfg.aliases:
                config = cfg
                break

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

        if self.conversational_patterns:
            print("💬 Conversational Commands:")
            for pattern in self.conversational_patterns:
                print(f"   jpapi {self.name} {pattern.pattern}")
                if pattern.description:
                    print(f"      {pattern.description}")
                if pattern.aliases:
                    print(f"      Aliases: {', '.join(pattern.aliases)}")
                print()

        if self.subcommand_configs:
            print("🔧 Traditional Commands:")
            for config in self.subcommand_configs:
                print(f"   jpapi {self.name} {config.name}")
                print(f"      {config.description}")
                if config.aliases:
                    print(f"      Aliases: {', '.join(config.aliases)}")
                print()

    def _show_suggestions(self, pattern_string: str):
        """Show suggestions for unrecognized patterns"""
        print("\n💡 Did you mean:")

        # Find similar patterns
        similar_patterns = []
        for pattern in self.conversational_patterns:
            if any(word in pattern.pattern for word in pattern_string.split()):
                similar_patterns.append(pattern)

        for pattern in similar_patterns[:3]:  # Show top 3 suggestions
            print(f"   jpapi {self.name} {pattern.pattern}")

        if not similar_patterns:
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

    def format_output(self, data: Any, format_type: str = "table") -> str:
        """Format output data"""
        if format_type == "json":
            import json

            return json.dumps(data, indent=2)
        elif format_type == "csv":
            return self._format_csv(data)
        else:
            return self._format_table(data)

    def _format_table(self, data: Any) -> str:
        """Format data as table"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Simple table formatting
            headers = list(data[0].keys())
            rows = []

            # Header
            header_row = " | ".join(f"{h:15}" for h in headers)
            separator = "-" * len(header_row)
            rows.append(header_row)
            rows.append(separator)

            # Data rows
            for item in data:
                row = " | ".join(f"{str(item.get(h, '')):15}" for h in headers)
                rows.append(row)

            return "\n".join(rows)
        else:
            return str(data)

    def _format_csv(self, data: Any) -> str:
        """Format data as CSV"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        else:
            return str(data)

    def save_output(self, content: str, output_path: Optional[str] = None) -> None:
        """Save output to file or print to stdout"""
        if output_path:
            try:
                # Ensure directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(content)
                print(f"✅ Output saved to: {output_path}")
            except Exception as e:
                print(f"❌ Failed to save output: {e}")
                print(content)
        else:
            print(content)

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

    # Production Guardrails
    def is_production_environment(self) -> bool:
        """Check if current environment is production"""
        return self.safety_manager.is_production_environment(self.environment)

    def require_production_confirmation(
        self,
        operation: str,
        details: str = "",
        changes_summary: str = "",
        args: Namespace = None,
    ) -> bool:
        """Require explicit confirmation for production operations with comprehensive summary"""
        if not self.is_production_environment():
            return True

        # Check for force flag
        if args and getattr(args, "force", False):
            print("🔒 Force flag detected - skipping production confirmation")
            return True

        print("🚨 PRODUCTION ENVIRONMENT DETECTED 🚨")
        print("=" * 60)
        print(f"Operation: {operation}")
        if details:
            print(f"Details: {details}")
        print(f"Environment: {self.environment}")
        print(f"Timestamp: {self._get_timestamp()}")
        print("=" * 60)

        # Show comprehensive changes summary
        if changes_summary:
            print("\n📋 CHANGES SUMMARY:")
            print("-" * 40)
            print(changes_summary)
            print("-" * 40)

        print("\n⚠️  This will modify PRODUCTION data.")
        print("💡 Use --dry-run to test operations safely")
        print("🔒 Use --force to skip this confirmation")
        print()

        # Enhanced confirmation
        print("🔐 SAFETY CONFIRMATION REQUIRED")
        print("=" * 40)
        response = (
            input("Do you want to proceed with this PRODUCTION operation? (y/N): ")
            .strip()
            .lower()
        )

        if response not in ["y", "yes"]:
            print("❌ Operation cancelled")
            return False

        # Additional confirmation for high-risk operations
        safety_word = (
            input("Are you absolutely sure you want to proceed? (y/N): ")
            .strip()
            .lower()
        )
        if safety_word not in ["y", "yes"]:
            print("❌ Operation cancelled - second confirmation failed")
            return False

        print("✅ Production operation confirmed. Proceeding...")
        return True

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def create_bulk_changes_summary(self, operation_type: str, objects: list) -> str:
        """Create a comprehensive summary for bulk operations"""
        summary = f"\n{operation_type} Summary:\n"
        summary += f"  • Total Objects: {len(objects)}\n"

        # Group by type
        by_type = {}
        for obj in objects:
            obj_type = obj.get("type", "Unknown")
            if obj_type not in by_type:
                by_type[obj_type] = []
            by_type[obj_type].append(obj)

        for obj_type, items in by_type.items():
            summary += f"\n  {obj_type.upper()} ({len(items)} items):\n"
            for item in items[:5]:  # Show first 5 items
                name = item.get("name", "Unknown")
                summary += f"    • {name}\n"
            if len(items) > 5:
                summary += f"    • ... and {len(items) - 5} more\n"

        summary += f"\n  Impact: Will {operation_type.lower()} {len(objects)} objects in PRODUCTION"
        return summary

    def require_dry_run_confirmation(self, operation: str) -> bool:
        """Suggest dry-run mode for production operations"""
        if not self.is_production_environment():
            return True

        print("🔍 DRY-RUN MODE RECOMMENDED")
        print("=" * 40)
        print(f"Operation: {operation}")
        print(f"Environment: {self.environment}")
        print()
        print("💡 Consider using --dry-run to test first:")
        print(f"   jpapi {self.name} --dry-run ...")
        print()

        response = (
            input("Continue without dry-run? (type 'yes' to proceed): ").strip().lower()
        )
        return response == "yes"

    def check_destructive_operation(
        self, operation: str, resource_name: str = ""
    ) -> bool:
        """Check if operation is destructive and requires extra confirmation"""
        if not self.safety_manager.should_require_confirmation(
            self.environment, operation
        ):
            return True

        return self.require_production_confirmation(
            f"Destructive Operation: {operation}",
            f"Resource: {resource_name}" if resource_name else "",
        )
