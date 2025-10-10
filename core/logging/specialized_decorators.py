#!/usr/bin/env python3
"""
Specialized Logging Decorators for jpapi
Common patterns for different types of operations
"""

import time
from typing import Optional, Callable, Any, List, Dict
from functools import wraps
from core.logging.command_mixin import get_logging_manager


def log_api_call(endpoint: str, method: str = "GET"):
    """Decorator for API calls with automatic logging"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logging_manager = get_logging_manager()
            logging_manager.log_info(f"Making {method} request to {endpoint}")

            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                duration = time.time() - start_time
                logging_manager.log_success(f"API call completed in {duration:.2f}s")
                return result
            except Exception as e:
                logging_manager.log_error(f"API call failed: {e}")
                raise

        return wrapper

    return decorator


def log_pagination(total_pages: Optional[int] = None):
    """Decorator for paginated operations"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logging_manager = get_logging_manager()
            logging_manager.log_info(f"Starting paginated operation")

            if total_pages:
                logging_manager.log_info(f"Expected {total_pages} pages")

            with logging_manager.progress_tracker(
                total_pages or 100, "Processing pages"
            ) as tracker:
                result = func(self, *args, **kwargs)
                return result

        return wrapper

    return decorator


def log_file_operations(operation_type: str = "file"):
    """Decorator for file operations (download, upload, save)"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logging_manager = get_logging_manager()
            logging_manager.log_info(f"Starting {operation_type} operation")

            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                duration = time.time() - start_time
                logging_manager.log_success(
                    f"{operation_type.title()} operation completed in {duration:.2f}s"
                )
                return result
            except Exception as e:
                logging_manager.log_error(
                    f"{operation_type.title()} operation failed: {e}"
                )
                raise

        return wrapper

    return decorator


def log_data_processing(data_type: str, total_items: Optional[int] = None):
    """Decorator for data processing operations"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logging_manager = get_logging_manager()
            logging_manager.log_info(f"Processing {data_type}")

            if total_items:
                logging_manager.log_info(f"Processing {total_items} {data_type} items")
                with logging_manager.progress_tracker(
                    total_items, f"Processing {data_type}"
                ) as tracker:
                    result = func(self, *args, **kwargs)
                    return result
            else:
                result = func(self, *args, **kwargs)
                return result

        return wrapper

    return decorator


def log_export_operation(export_type: str):
    """Decorator specifically for export operations"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logging_manager = get_logging_manager()
            logging_manager.log_info(f"Starting {export_type} export")

            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                duration = time.time() - start_time
                logging_manager.log_success(
                    f"{export_type} export completed in {duration:.2f}s"
                )
                return result
            except Exception as e:
                logging_manager.log_error(f"{export_type} export failed: {e}")
                raise

        return wrapper

    return decorator


def log_list_operation(object_type: str):
    """Decorator specifically for list operations"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logging_manager = get_logging_manager()
            logging_manager.log_info(f"Listing {object_type}")

            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                duration = time.time() - start_time
                logging_manager.log_success(
                    f"{object_type} listing completed in {duration:.2f}s"
                )
                return result
            except Exception as e:
                logging_manager.log_error(f"{object_type} listing failed: {e}")
                raise

        return wrapper

    return decorator


def log_batch_operation(operation_name: str, batch_size: int = 100):
    """Decorator for batch operations with progress tracking"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logging_manager = get_logging_manager()
            logging_manager.log_info(
                f"Starting {operation_name} in batches of {batch_size}"
            )

            with logging_manager.progress_tracker(
                batch_size, f"Processing {operation_name}"
            ) as tracker:
                result = func(self, *args, **kwargs)
                return result

        return wrapper

    return decorator


def log_streamlit_operation(operation_name: str):
    """Decorator for Streamlit operations with progress bars"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import streamlit as st

            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text(f"🔄 {operation_name}...")
            progress_bar.progress(10)

            try:
                result = func(*args, **kwargs)
                progress_bar.progress(100)
                status_text.text(f"✅ {operation_name} completed!")
                return result
            except Exception as e:
                status_text.text(f"❌ {operation_name} failed: {e}")
                raise

        return wrapper

    return decorator
