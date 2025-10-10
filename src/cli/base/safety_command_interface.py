#!/usr/bin/env python3
"""
Safety Command Interface
Handles safety and confirmation operations following ISP
"""

from abc import ABC, abstractmethod
from typing import List


class SafetyCommandInterface(ABC):
    """Interface for safety-related command operations"""

    @abstractmethod
    def require_dry_run_confirmation(self, operation: str) -> bool:
        """Require confirmation for dry run operations"""
        pass

    @abstractmethod
    def check_destructive_operation(self, operation: str, objects: List[str]) -> bool:
        """Check if operation is destructive and require confirmation"""
        pass

    @abstractmethod
    def create_bulk_changes_summary(self, operation_type: str, objects: list) -> str:
        """Create summary of bulk changes"""
        pass
