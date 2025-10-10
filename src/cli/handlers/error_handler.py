#!/usr/bin/env python3
"""
Error Handler
Single Responsibility: Handles all error processing and user feedback
"""

from typing import Dict, Any, Optional
import logging
from enum import Enum


class ErrorType(Enum):
    """Error type enumeration"""

    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    NETWORK = "network"
    VALIDATION = "validation"
    API = "api"
    UNKNOWN = "unknown"


class ErrorHandler:
    """Handles error processing following SRP"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("ErrorHandler")
        self.error_messages = self._setup_error_messages()

    def _setup_error_messages(self) -> Dict[ErrorType, Dict[str, str]]:
        """Setup error message templates"""
        return {
            ErrorType.AUTHENTICATION: {
                "title": "❌ Authentication Error",
                "message": "Authentication failed. Please check your credentials.",
                "suggestion": "Run: jpapi auth setup",
                "exit_code": 1,
            },
            ErrorType.PERMISSION: {
                "title": "❌ Permission Error",
                "message": "Access denied. Check your API permissions.",
                "suggestion": "Contact your administrator for access",
                "exit_code": 2,
            },
            ErrorType.NETWORK: {
                "title": "❌ Network Error",
                "message": "Network connection failed.",
                "suggestion": "Check your network connection and try again",
                "exit_code": 3,
            },
            ErrorType.VALIDATION: {
                "title": "❌ Validation Error",
                "message": "Invalid input or configuration.",
                "suggestion": "Check your command arguments and configuration",
                "exit_code": 4,
            },
            ErrorType.API: {
                "title": "❌ API Error",
                "message": "API request failed.",
                "suggestion": "Check the error details above",
                "exit_code": 5,
            },
            ErrorType.UNKNOWN: {
                "title": "❌ Unknown Error",
                "message": "An unexpected error occurred.",
                "suggestion": "Check the error details and try again",
                "exit_code": 6,
            },
        }

    def handle_error(self, error: Exception, context: Optional[str] = None) -> int:
        """Handle error and return appropriate exit code"""
        error_type = self._classify_error(error)
        error_info = self.error_messages[error_type]

        # Log the error
        self.logger.error(f"Error in {context or 'unknown context'}: {error}")

        # Display user-friendly message
        print(f"{error_info['title']}")
        print(f"   {error_info['message']}")

        if context:
            print(f"   Context: {context}")

        print(f"   💡 {error_info['suggestion']}")

        # Show detailed error if in debug mode
        if self.logger.level <= logging.DEBUG:
            print(f"   Details: {str(error)}")

        return error_info["exit_code"]

    def handle_api_error(self, error: Exception, context: Optional[str] = None) -> int:
        """Handle API-specific errors"""
        error_str = str(error).lower()

        if any(
            keyword in error_str
            for keyword in ["401", "unauthorized", "authentication"]
        ):
            return self.handle_error(error, context or "API Authentication")
        elif any(
            keyword in error_str for keyword in ["403", "forbidden", "permission"]
        ):
            return self.handle_error(error, context or "API Permission")
        elif any(keyword in error_str for keyword in ["404", "not found"]):
            print("❌ Resource not found")
            print("   💡 Check if the resource exists or verify the identifier")
            return 4
        elif any(keyword in error_str for keyword in ["timeout", "connection"]):
            return self.handle_error(error, context or "API Network")
        else:
            return self.handle_error(error, context or "API Request")

    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type based on exception"""
        error_str = str(error).lower()

        if any(
            keyword in error_str
            for keyword in ["auth", "credential", "token", "401", "unauthorized"]
        ):
            return ErrorType.AUTHENTICATION
        elif any(
            keyword in error_str
            for keyword in ["permission", "403", "forbidden", "access"]
        ):
            return ErrorType.PERMISSION
        elif any(
            keyword in error_str
            for keyword in ["network", "connection", "timeout", "dns"]
        ):
            return ErrorType.NETWORK
        elif any(
            keyword in error_str
            for keyword in ["validation", "invalid", "format", "required"]
        ):
            return ErrorType.VALIDATION
        elif any(
            keyword in error_str
            for keyword in ["api", "http", "server", "500", "502", "503"]
        ):
            return ErrorType.API
        else:
            return ErrorType.UNKNOWN

    def create_error_summary(self, errors: list) -> str:
        """Create summary of multiple errors"""
        if not errors:
            return "No errors occurred"

        error_counts = {}
        for error in errors:
            error_type = self._classify_error(error)
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        summary = f"Error Summary: {len(errors)} total errors\n"
        for error_type, count in error_counts.items():
            summary += f"  • {error_type.value.title()}: {count}\n"

        return summary

    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log error with additional context"""
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        self.logger.error(f"Error with context [{context_str}]: {error}")

    def get_error_help(self, error_type: ErrorType) -> str:
        """Get help information for specific error type"""
        error_info = self.error_messages[error_type]
        return f"{error_info['title']}\n{error_info['message']}\n💡 {error_info['suggestion']}"

    def is_recoverable_error(self, error: Exception) -> bool:
        """Check if error is recoverable"""
        error_type = self._classify_error(error)
        return error_type in [ErrorType.NETWORK, ErrorType.API]

    def get_retry_suggestion(self, error: Exception) -> Optional[str]:
        """Get retry suggestion for recoverable errors"""
        if self.is_recoverable_error(error):
            return "This error might be temporary. Try again in a few moments."
        return None



