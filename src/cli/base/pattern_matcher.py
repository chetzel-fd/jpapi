#!/usr:bin/env python3
"""
Pattern Matcher for Conversational Commands
Handles natural language command pattern matching and parsing
Extracted from BaseCommand for SRP compliance
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from argparse import Namespace


@dataclass
class CommandPattern:
    """Represents a conversational command pattern"""

    pattern: str
    handler: str
    description: str
    aliases: Optional[List[str]] = None
    required_args: Optional[List[str]] = None
    optional_args: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.required_args is None:
            self.required_args = []
        if self.optional_args is None:
            self.optional_args = {}


@dataclass
class SubcommandConfig:
    """Configuration for subcommand creation"""

    name: str
    aliases: List[str]
    description: str
    handler_method: str
    arguments: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self):
        if self.arguments is None:
            self.arguments = []


class PatternMatcher:
    """Handles conversational pattern matching for CLI commands"""

    def __init__(self):
        self.conversational_patterns: List[CommandPattern] = []
        self.subcommand_configs: List[SubcommandConfig] = []

    def add_conversational_pattern(
        self,
        pattern: str,
        handler: str,
        description: str,
        aliases: Optional[List[str]] = None,
        required_args: Optional[List[str]] = None,
        optional_args: Optional[Dict[str, Any]] = None,
    ) -> None:
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
        arguments: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
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

    def find_matching_pattern(
        self, pattern_string: str, target: str, action: str
    ) -> Optional[CommandPattern]:
        """
        Find the best matching conversational pattern

        Args:
            pattern_string: Full pattern string to match
            target: Target noun/object
            action: Action verb

        Returns:
            Matching CommandPattern or None
        """
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

    def find_subcommand_config(self, subcommand: str) -> Optional[SubcommandConfig]:
        """
        Find subcommand configuration by name or alias

        Args:
            subcommand: Subcommand name to find

        Returns:
            Matching SubcommandConfig or None
        """
        for config in self.subcommand_configs:
            if subcommand == config.name or subcommand in config.aliases:
                return config
        return None

    def parse_conversational_args(self, args: Namespace) -> tuple[str, str, List[str]]:
        """
        Parse conversational arguments from Namespace

        Args:
            args: Parsed command arguments

        Returns:
            Tuple of (target, action, terms)
        """
        target = args.target.lower() if hasattr(args, "target") and args.target else ""
        action = args.action.lower() if hasattr(args, "action") and args.action else ""
        terms = args.terms if hasattr(args, "terms") and args.terms else []

        return target, action, terms

    def build_pattern_string(self, target: str, action: str, terms: List[str]) -> str:
        """
        Build pattern string from components

        Args:
            target: Target noun/object
            action: Action verb
            terms: Additional terms

        Returns:
            Full pattern string
        """
        pattern_parts = [target]
        if action:
            pattern_parts.append(action)
        if terms:
            pattern_parts.extend(terms)

        return " ".join(pattern_parts)

    def get_suggestions(self, pattern_string: str) -> List[CommandPattern]:
        """
        Get pattern suggestions based on partial match

        Args:
            pattern_string: Partial pattern to match

        Returns:
            List of suggested patterns
        """
        suggestions = []
        for pattern in self.conversational_patterns:
            if any(word in pattern.pattern for word in pattern_string.split()):
                suggestions.append(pattern)

        return suggestions[:3]  # Return top 3 suggestions

    def has_conversational_patterns(self) -> bool:
        """Check if any conversational patterns are registered"""
        return len(self.conversational_patterns) > 0

    def has_subcommands(self) -> bool:
        """Check if any subcommands are registered"""
        return len(self.subcommand_configs) > 0
