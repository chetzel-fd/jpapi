#!/usr/bin/env python3
"""
Output Command Interface
Handles output formatting and saving operations following ISP
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class OutputCommandInterface(ABC):
    """Interface for output-related command operations"""

    @abstractmethod
    def format_output(self, data: Any, format_type: str = "table") -> str:
        """Format data for output"""
        pass

    @abstractmethod
    def save_output(self, content: str, output_path: Optional[str] = None) -> None:
        """Save output to file"""
        pass

    @abstractmethod
    def _format_table(self, data: Any) -> str:
        """Format data as table"""
        pass

    @abstractmethod
    def _format_csv(self, data: Any) -> str:
        """Format data as CSV"""
        pass
