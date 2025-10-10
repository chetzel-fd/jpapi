#!/usr/bin/env python3
"""
Pattern Command Interface
Handles conversational patterns and subcommands following ISP
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from argparse import ArgumentParser, Namespace

from .command_pattern import CommandPattern
from .subcommand_config import SubcommandConfig


class PatternCommandInterface(ABC):
    """Interface for pattern and subcommand operations"""

    @abstractmethod
    def add_conversational_pattern(
        self,
        pattern: str,
        handler: str,
        description: str,
        aliases: List[str] = None,
        required_args: List[str] = None,
        optional_args: Dict[str, Any] = None,
    ) -> None:
        """Add a conversational pattern"""
        pass

    @abstractmethod
    def add_subcommand_config(
        self,
        name: str,
        aliases: List[str],
        description: str,
        handler_method: str,
        arguments: List[Dict[str, Any]] = None,
    ) -> None:
        """Add subcommand configuration"""
        pass

    @abstractmethod
    def _handle_conversational_pattern(self, args: Namespace) -> int:
        """Handle conversational pattern execution"""
        pass

    @abstractmethod
    def _handle_subcommand(self, args: Namespace) -> int:
        """Handle subcommand execution"""
        pass

    @abstractmethod
    def _find_matching_pattern(self, pattern_string: str) -> Optional[CommandPattern]:
        """Find matching conversational pattern"""
        pass
