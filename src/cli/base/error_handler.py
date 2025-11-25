#!/usr/bin/env python3
"""
Error handling service for jpapi CLI
Centralized error classification and handling for consistent UX
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable


class ErrorType(Enum):
    """Categorized error types"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation"
    NETWORK = "network"
    API_ERROR = "api_error"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context for error handling"""

    operation: str
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    user_message: Optional[str] = None


class APIErrorHandler:
    """Centralized API error handling service"""

    @staticmethod
    def classify_error(error: Exception) -> ErrorType:
        """
        Classify error by type based on error message

        Args:
            error: Exception to classify

        Returns:
            Classified ErrorType
        """
        error_msg = str(error).lower()

        if "401" in error_msg or "unauthorized" in error_msg:
            return ErrorType.AUTHENTICATION
        if "403" in error_msg or "forbidden" in error_msg:
            return ErrorType.AUTHORIZATION
        if "404" in error_msg or "not found" in error_msg:
            return ErrorType.NOT_FOUND
        if "timeout" in error_msg or "timed out" in error_msg:
            return ErrorType.TIMEOUT
        if "429" in error_msg or "rate limit" in error_msg:
            return ErrorType.RATE_LIMIT
        if "connection" in error_msg or "network" in error_msg:
            return ErrorType.NETWORK
        if "invalid" in error_msg or "validation" in error_msg:
            return ErrorType.VALIDATION

        return ErrorType.UNKNOWN

    @staticmethod
    def handle_error(
        error: Exception,
        context: ErrorContext,
        retry_callback: Optional[Callable] = None,
    ) -> int:
        """
        Handle error with appropriate user feedback

        Args:
            error: Exception to handle
            context: Error context for messaging
            retry_callback: Optional callback for retry logic

        Returns:
            Exit code (1 for errors)
        """
        error_type = APIErrorHandler.classify_error(error)

        if error_type == ErrorType.TIMEOUT and retry_callback:
            print(f"⏰ {context.operation} timed out. Retrying...")
            return retry_callback()

        if error_type == ErrorType.RATE_LIMIT:
            print("🚦 Rate limit reached. Please wait and try again.")
            return 1

        if error_type == ErrorType.NOT_FOUND:
            obj_desc = (
                f"{context.object_type} {context.object_id}"
                if context.object_id
                else context.object_type
            )
            print(f"❌ {obj_desc} not found")
            return 1

        if error_type == ErrorType.AUTHENTICATION:
            print("🔒 Authentication failed. Please run: jpapi setup auth")
            return 1

        if error_type == ErrorType.AUTHORIZATION:
            print(
                f"🚫 Permission denied. "
                f"You don't have access to {context.operation}"
            )
            return 1

        if error_type == ErrorType.VALIDATION:
            print(f"❌ Validation error: {error}")
            return 1

        # Default error handling
        if context.user_message:
            print(f"❌ {context.user_message}: {error}")
        else:
            print(f"❌ Error during {context.operation}: {error}")

        return 1
