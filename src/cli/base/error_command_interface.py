#!/usr/bin/env python3
"""
Error Command Interface
Handles error handling operations following ISP
"""

from abc import ABC, abstractmethod


class ErrorCommandInterface(ABC):
    """Interface for error handling operations"""

    @abstractmethod
    def handle_api_error(self, error: Exception) -> int:
        """Handle API errors and return appropriate exit code"""
        pass
