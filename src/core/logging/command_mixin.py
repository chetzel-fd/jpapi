#!/usr/bin/env python3
"""
Logging Command Mixin for jpapi
Extends existing BaseCommand with logging capabilities
"""

from typing import Optional, Any, Callable
from functools import wraps
from contextlib import contextmanager

from core.logging.logging_manager import get_logging_manager, LoggingManager


class LoggingCommandMixin:
    """Mixin to add logging capabilities to commands - follows existing patterns"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logging_manager: LoggingManager = get_logging_manager()

    def log_info(self, message: str, context: Optional[str] = None) -> None:
        """Log informational message"""
        self.logging_manager.log_info(message, context)

    def log_success(self, message: str, context: Optional[str] = None) -> None:
        """Log success message"""
        self.logging_manager.log_success(message, context)

    def log_warning(self, message: str, context: Optional[str] = None) -> None:
        """Log warning message"""
        self.logging_manager.log_warning(message, context)

    def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[str] = None,
    ) -> None:
        """Log error message"""
        self.logging_manager.log_error(message, error, context)

    def log_operation_start(
        self, operation: str, total_items: Optional[int] = None
    ) -> None:
        """Log operation start"""
        self.logging_manager.log_operation_start(operation, total_items)

    def log_operation_end(
        self, operation: str, items_processed: int, duration: float
    ) -> None:
        """Log operation end"""
        self.logging_manager.log_operation_end(operation, items_processed, duration)

    def log_progress(
        self, current: int, total: int, item: str, operation: str = "Processing"
    ) -> None:
        """Log progress update"""
        self.logging_manager.log_progress(current, total, item, operation)

    @contextmanager
    def progress_tracker(self, total: int, description: str):
        """Context manager for progress tracking"""
        with self.logging_manager.progress_tracker(total, description) as tracker:
            yield tracker

    def with_operation_logging(
        self, operation_name: str, total_items: Optional[int] = None
    ):
        """Decorator for automatic operation logging"""
        return self.logging_manager.with_operation_logging(operation_name, total_items)

    def with_progress(self, total: int, description: str):
        """Decorator for progress tracking"""
        return self.logging_manager.with_progress(total, description)


# Convenience decorators for use in commands
def log_operation(operation_name: str, total_items: Optional[int] = None):
    """Decorator to add operation logging to methods"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, "logging_manager"):
                return self.logging_manager.with_operation_logging(
                    operation_name, total_items
                )(func)(self, *args, **kwargs)
            else:
                # Fallback for commands without mixin
                logging_manager = get_logging_manager()
                return logging_manager.with_operation_logging(
                    operation_name, total_items
                )(func)(self, *args, **kwargs)

        return wrapper

    return decorator


def with_progress(total: int, description: str):
    """Decorator to add progress tracking to methods"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, "logging_manager"):
                return self.logging_manager.with_progress(total, description)(func)(
                    self, *args, **kwargs
                )
            else:
                # Fallback for commands without mixin
                logging_manager = get_logging_manager()
                return logging_manager.with_progress(total, description)(func)(
                    self, *args, **kwargs
                )

        return wrapper

    return decorator
