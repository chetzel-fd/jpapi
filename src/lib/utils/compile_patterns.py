#!/usr/bin/env python3
"""
Pattern Compiler Implementations
Provides different pattern matching strategies
"""

import re
from typing import Dict, Pattern
from src.interfaces.pattern_compiler import IPatternCompiler


class ExactPatternCompiler(IPatternCompiler):
    """Exact string matching compiler"""

    def compile_pattern(self, pattern: str, case_sensitive: bool = False) -> str:
        """Compile pattern for exact matching"""
        return pattern.lower() if not case_sensitive else pattern

    def match(self, pattern: str, value: str, case_sensitive: bool = False) -> bool:
        """Check if value exactly matches pattern"""
        if not case_sensitive:
            value = value.lower()
        return value == pattern

    def clear_cache(self) -> None:
        """No cache to clear for exact matching"""
        pass


class ContainsPatternCompiler(IPatternCompiler):
    """Substring matching compiler"""

    def compile_pattern(self, pattern: str, case_sensitive: bool = False) -> str:
        """Compile pattern for substring matching"""
        return pattern.lower() if not case_sensitive else pattern

    def match(self, pattern: str, value: str, case_sensitive: bool = False) -> bool:
        """Check if value contains pattern"""
        if not case_sensitive:
            value = value.lower()
        return pattern in value

    def clear_cache(self) -> None:
        """No cache to clear for substring matching"""
        pass


class WildcardPatternCompiler(IPatternCompiler):
    """Wildcard pattern matching compiler"""

    def __init__(self):
        """Initialize wildcard compiler"""
        self._cache: Dict[str, Pattern] = {}

    def compile_pattern(self, pattern: str, case_sensitive: bool = False) -> Pattern:
        """Compile wildcard pattern to regex"""
        cache_key = f"{pattern}:{case_sensitive}"
        if cache_key not in self._cache:
            # If no wildcards, use contains matching
            if "*" not in pattern and "?" not in pattern:
                escaped = re.escape(pattern)
                regex = f".*{escaped}.*"
            else:
                # Convert wildcards to regex
                escaped = re.escape(pattern)
                regex = escaped.replace(r"\*", ".*").replace(r"\?", ".")
                regex = f"^{regex}$"

            flags = 0 if case_sensitive else re.IGNORECASE
            self._cache[cache_key] = re.compile(regex, flags)

        return self._cache[cache_key]

    def match(self, pattern: Pattern, value: str, case_sensitive: bool = False) -> bool:
        """Check if value matches wildcard pattern"""
        return bool(pattern.match(value))

    def clear_cache(self) -> None:
        """Clear cached patterns"""
        self._cache.clear()


class RegexPatternCompiler(IPatternCompiler):
    """Regular expression pattern compiler"""

    def __init__(self):
        """Initialize regex compiler"""
        self._cache: Dict[str, Pattern] = {}

    def compile_pattern(self, pattern: str, case_sensitive: bool = False) -> Pattern:
        """Compile regex pattern"""
        cache_key = f"{pattern}:{case_sensitive}"
        if cache_key not in self._cache:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                self._cache[cache_key] = re.compile(pattern, flags)
            except re.error:
                # If regex is invalid, fall back to contains matching
                escaped = re.escape(pattern)
                self._cache[cache_key] = re.compile(
                    f".*{escaped}.*", re.IGNORECASE if not case_sensitive else 0
                )

        return self._cache[cache_key]

    def match(self, pattern: Pattern, value: str, case_sensitive: bool = False) -> bool:
        """Check if value matches regex pattern"""
        return bool(pattern.match(value))

    def clear_cache(self) -> None:
        """Clear cached patterns"""
        self._cache.clear()
