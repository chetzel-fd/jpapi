#!/usr/bin/env python3
"""
Simple Logger Implementation
Follows Single Responsibility Principle (SRP)
"""

import time
from typing import Optional
from core.interfaces.logging import LoggingInterface, ProgressInterface, ProgressTracker


class SimpleProgressTracker(ProgressTracker):
    """Simple progress tracker"""

    def __init__(self, total: int, description: str):
        self.total = total
        self.description = description
        self.current = 0

    def __enter__(self):
        print(f"🔄 {self.description} (0/{self.total})")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"✅ {self.description} completed")

    def update(self, advance: int = 1, description: Optional[str] = None) -> None:
        self.current += advance
        progress_pct = (self.current / self.total) * 100 if self.total > 0 else 0
        item_desc = f" - {description}" if description else ""
        print(
            f"🔄 {self.description} ({self.current}/{self.total} - {progress_pct:.1f}%){item_desc}"
        )


class SimpleLogger(LoggingInterface, ProgressInterface):
    """Simple logger implementation - follows SRP"""

    def __init__(self):
        self._current_operation = None
        self._start_time = None

    def log_info(self, message: str, context: Optional[str] = None) -> None:
        """Log informational message"""
        prefix = f"[{context}] " if context else ""
        print(f"ℹ️ {prefix}{message}")

    def log_success(self, message: str, context: Optional[str] = None) -> None:
        """Log success message"""
        prefix = f"[{context}] " if context else ""
        print(f"✅ {prefix}{message}")

    def log_warning(self, message: str, context: Optional[str] = None) -> None:
        """Log warning message"""
        prefix = f"[{context}] " if context else ""
        print(f"⚠️ {prefix}{message}")

    def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[str] = None,
    ) -> None:
        """Log error message"""
        prefix = f"[{context}] " if context else ""
        if error:
            print(f"❌ {prefix}{message}: {error}")
        else:
            print(f"❌ {prefix}{message}")

    def log_operation_start(
        self, operation: str, total_items: Optional[int] = None
    ) -> None:
        """Log operation start"""
        self._current_operation = operation
        self._start_time = time.time()
        if total_items:
            print(f"🚀 Starting {operation} ({total_items} items)...")
        else:
            print(f"🚀 Starting {operation}...")

    def log_operation_end(
        self, operation: str, items_processed: int, duration: float
    ) -> None:
        """Log operation end"""
        print(f"✅ Completed {operation} - {items_processed} items in {duration:.2f}s")
        self._current_operation = None
        self._start_time = None

    def log_progress(
        self, current: int, total: int, item: str, operation: str = "Processing"
    ) -> None:
        """Log progress update"""
        progress_pct = (current / total) * 100 if total > 0 else 0
        print(f"🔄 {operation} {item} ({current}/{total} - {progress_pct:.1f}%)")

    def start_progress(self, total: int, description: str) -> SimpleProgressTracker:
        """Start progress tracking"""
        return SimpleProgressTracker(total, description)

    def update_progress(
        self, advance: int = 1, description: Optional[str] = None
    ) -> None:
        """Update progress - not used in this implementation"""
        pass

    def complete_progress(self) -> None:
        """Complete progress tracking - not used in this implementation"""
        pass
