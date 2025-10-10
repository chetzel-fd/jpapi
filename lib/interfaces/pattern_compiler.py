#!/usr/bin/env python3
"""
Pattern Compiler Interface
Defines the contract for pattern compilation implementations
"""

from abc import ABC, abstractmethod
from typing import Any


class IPatternCompiler(ABC):
    """Interface for pattern compilation implementations"""

    @abstractmethod
    def compile_pattern(self, pattern: str, case_sensitive: bool = False) -> Any:
        """
        Compile a pattern for matching

        Args:
            pattern: The pattern to compile
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            Compiled pattern object
        """
        pass

    @abstractmethod
    def match(self, pattern: Any, value: str, case_sensitive: bool = False) -> bool:
        """
        Check if a value matches a compiled pattern

        Args:
            pattern: The compiled pattern to match against
            value: The value to check
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            True if value matches pattern
        """
        pass

    @abstractmethod
    def clear_cache(self) -> None:
        """Clear any cached patterns"""
        pass
