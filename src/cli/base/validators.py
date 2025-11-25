#!/usr/bin/env python3
"""
Input validation service for jpapi CLI
Centralized validation logic for consistent security and error handling
"""
from typing import Any


class InputValidators:
    """Centralized input validation service"""

    @staticmethod
    def validate_id(value: Any, min_val: int = 1, max_val: int = 999999) -> int:
        """
        Validate and return object ID

        Args:
            value: Input value to validate
            min_val: Minimum valid ID
            max_val: Maximum valid ID

        Returns:
            Validated integer ID

        Raises:
            ValueError: If value is not numeric or out of range
        """
        if not str(value).isdigit():
            raise ValueError(f"ID must be numeric, got: {value}")

        id_val = int(value)
        if not (min_val <= id_val <= max_val):
            raise ValueError(
                f"ID must be between {min_val} and {max_val}, got: {id_val}"
            )

        return id_val

    @staticmethod
    def is_numeric(value: Any) -> bool:
        """Check if value is numeric"""
        return str(value).isdigit()

    @staticmethod
    def validate_filter_pattern(pattern: str) -> str:
        """
        Validate filter pattern

        Args:
            pattern: Filter pattern to validate

        Returns:
            Validated pattern

        Raises:
            ValueError: If pattern is invalid
        """
        if not pattern or not isinstance(pattern, str):
            raise ValueError("Filter pattern must be a non-empty string")

        return pattern.strip()
