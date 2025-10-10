#!/usr/bin/env python3
"""
Logging Interface for jpapi
Follows Interface Segregation Principle (ISP)
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict


class LoggingInterface(ABC):
    """Interface for logging operations - follows ISP"""

    @abstractmethod
    def log_info(self, message: str, context: Optional[str] = None) -> None:
        """Log informational message"""
        pass

    @abstractmethod
    def log_success(self, message: str, context: Optional[str] = None) -> None:
        """Log success message"""
        pass

    @abstractmethod
    def log_warning(self, message: str, context: Optional[str] = None) -> None:
        """Log warning message"""
        pass

    @abstractmethod
    def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[str] = None,
    ) -> None:
        """Log error message"""
        pass

    @abstractmethod
    def log_operation_start(
        self, operation: str, total_items: Optional[int] = None
    ) -> None:
        """Log operation start"""
        pass

    @abstractmethod
    def log_operation_end(
        self, operation: str, items_processed: int, duration: float
    ) -> None:
        """Log operation end"""
        pass

    @abstractmethod
    def log_progress(
        self, current: int, total: int, item: str, operation: str = "Processing"
    ) -> None:
        """Log progress update"""
        pass


class ProgressInterface(ABC):
    """Interface for progress tracking - follows ISP"""

    @abstractmethod
    def start_progress(self, total: int, description: str) -> "ProgressTracker":
        """Start progress tracking"""
        pass

    @abstractmethod
    def update_progress(
        self, advance: int = 1, description: Optional[str] = None
    ) -> None:
        """Update progress"""
        pass

    @abstractmethod
    def complete_progress(self) -> None:
        """Complete progress tracking"""
        pass


class ProgressTracker(ABC):
    """Abstract progress tracker"""

    @abstractmethod
    def __enter__(self):
        """Context manager entry"""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass

    @abstractmethod
    def update(self, advance: int = 1, description: Optional[str] = None) -> None:
        """Update progress"""
        pass
