#!/usr/bin/env python3
"""
Rich Logger Implementation
Follows Single Responsibility Principle (SRP)
"""

import time
from typing import Optional
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from core.interfaces.logging import LoggingInterface, ProgressInterface, ProgressTracker


class RichProgressTracker(ProgressTracker):
    """Rich-based progress tracker"""

    def __init__(self, console: Console, total: int, description: str):
        self.console = console
        self.total = total
        self.description = description
        self.progress = None
        self.task = None

    def __enter__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        )
        self.task = self.progress.add_task(self.description, total=self.total)
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()

    def update(self, advance: int = 1, description: Optional[str] = None) -> None:
        if self.progress and self.task is not None:
            if description:
                self.progress.update(self.task, description=description)
            self.progress.advance(self.task, advance)


class RichLogger(LoggingInterface, ProgressInterface):
    """Rich-based logger implementation - follows SRP"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self._current_operation = None
        self._start_time = None

    def log_info(self, message: str, context: Optional[str] = None) -> None:
        """Log informational message"""
        prefix = f"[{context}] " if context else ""
        self.console.print(f"ℹ️ {prefix}{message}")

    def log_success(self, message: str, context: Optional[str] = None) -> None:
        """Log success message"""
        prefix = f"[{context}] " if context else ""
        self.console.print(f"✅ {prefix}{message}")

    def log_warning(self, message: str, context: Optional[str] = None) -> None:
        """Log warning message"""
        prefix = f"[{context}] " if context else ""
        self.console.print(f"⚠️ {prefix}{message}")

    def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[str] = None,
    ) -> None:
        """Log error message"""
        prefix = f"[{context}] " if context else ""
        if error:
            self.console.print(f"❌ {prefix}{message}: {error}")
        else:
            self.console.print(f"❌ {prefix}{message}")

    def log_operation_start(
        self, operation: str, total_items: Optional[int] = None
    ) -> None:
        """Log operation start"""
        self._current_operation = operation
        self._start_time = time.time()
        if total_items:
            self.console.print(f"🚀 Starting {operation} ({total_items} items)...")
        else:
            self.console.print(f"🚀 Starting {operation}...")

    def log_operation_end(
        self, operation: str, items_processed: int, duration: float
    ) -> None:
        """Log operation end"""
        self.console.print(
            f"✅ Completed {operation} - {items_processed} items in {duration:.2f}s"
        )
        self._current_operation = None
        self._start_time = None

    def log_progress(
        self, current: int, total: int, item: str, operation: str = "Processing"
    ) -> None:
        """Log progress update"""
        progress_pct = (current / total) * 100 if total > 0 else 0
        self.console.print(
            f"🔄 {operation} {item} ({current}/{total} - {progress_pct:.1f}%)"
        )

    def start_progress(self, total: int, description: str) -> RichProgressTracker:
        """Start progress tracking"""
        return RichProgressTracker(self.console, total, description)

    def update_progress(
        self, advance: int = 1, description: Optional[str] = None
    ) -> None:
        """Update progress - not used in this implementation"""
        pass

    def complete_progress(self) -> None:
        """Complete progress tracking - not used in this implementation"""
        pass
