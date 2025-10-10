#!/usr/bin/env python3
"""
Logging Manager for jpapi
Follows Single Responsibility Principle (SRP)
"""

import time
from typing import Optional, Any, Callable
from functools import wraps
from contextlib import contextmanager

from core.interfaces.logging import LoggingInterface, ProgressTracker
from .factory import get_best_logger


class LoggingManager:
    """Manages logging operations - follows SRP"""

    def __init__(self, logger: Optional[LoggingInterface] = None):
        self.logger = logger or get_best_logger()

    def log_info(self, message: str, context: Optional[str] = None) -> None:
        """Log informational message"""
        self.logger.log_info(message, context)

    def log_success(self, message: str, context: Optional[str] = None) -> None:
        """Log success message"""
        self.logger.log_success(message, context)

    def log_warning(self, message: str, context: Optional[str] = None) -> None:
        """Log warning message"""
        self.logger.log_warning(message, context)

    def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[str] = None,
    ) -> None:
        """Log error message"""
        self.logger.log_error(message, error, context)

    def log_operation_start(
        self, operation: str, total_items: Optional[int] = None
    ) -> None:
        """Log operation start"""
        self.logger.log_operation_start(operation, total_items)

    def log_operation_end(
        self, operation: str, items_processed: int, duration: float
    ) -> None:
        """Log operation end"""
        self.logger.log_operation_end(operation, items_processed, duration)

    def log_progress(
        self, current: int, total: int, item: str, operation: str = "Processing"
    ) -> None:
        """Log progress update"""
        self.logger.log_progress(current, total, item, operation)

    @contextmanager
    def progress_tracker(self, total: int, description: str):
        """Context manager for progress tracking"""
        tracker = self.logger.start_progress(total, description)
        try:
            yield tracker
        finally:
            pass  # Progress tracker handles its own cleanup

    def with_operation_logging(
        self, operation_name: str, total_items: Optional[int] = None
    ):
        """Decorator for automatic operation logging"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                self.log_operation_start(operation_name, total_items)

                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time

                    # Try to determine items processed from result
                    items_processed = 0
                    if hasattr(result, "__len__"):
                        items_processed = len(result)
                    elif isinstance(result, (list, tuple)):
                        items_processed = len(result)

                    self.log_operation_end(operation_name, items_processed, duration)
                    return result
                except Exception as e:
                    self.log_error(f"Error in {operation_name}", e, operation_name)
                    raise

            return wrapper

        return decorator

    def with_progress(self, total: int, description: str):
        """Decorator for progress tracking"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.progress_tracker(total, description) as tracker:
                    # If function yields items, track them
                    if hasattr(func(*args, **kwargs), "__iter__"):
                        for i, item in enumerate(func(*args, **kwargs)):
                            tracker.update(description=f"Processing: {item}")
                            yield item
                    else:
                        return func(*args, **kwargs)

            return wrapper

        return decorator


# Global instance for convenience
_logging_manager = None


def get_logging_manager() -> LoggingManager:
    """Get global logging manager instance"""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager
