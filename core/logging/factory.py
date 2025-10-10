#!/usr/bin/env python3
"""
Logging Factory for jpapi
Follows existing factory pattern from auth system
"""

import os
from typing import Dict, Type, Optional
from core.interfaces.logging import LoggingInterface
from .rich_logger import RichLogger
from .simple_logger import SimpleLogger


class LoggingFactory:
    """Factory for creating logging implementations - follows existing pattern"""

    _implementations: Dict[str, Type[LoggingInterface]] = {
        "rich": RichLogger,
        "simple": SimpleLogger,
        "default": RichLogger,  # Default to Rich for better UX
    }

    @classmethod
    def create_logger(cls, logger_type: str = "default", **kwargs) -> LoggingInterface:
        """
        Create logging implementation

        Args:
            logger_type: Type of logger ('rich', 'simple', 'default')
            **kwargs: Additional arguments for logger implementation

        Returns:
            LoggingInterface: Configured logger instance

        Raises:
            ValueError: If logger_type is not supported
        """
        if logger_type not in cls._implementations:
            raise ValueError(
                f"Unsupported logger type: {logger_type}. "
                f"Available: {list(cls._implementations.keys())}"
            )

        logger_class = cls._implementations[logger_type]
        return logger_class(**kwargs)

    @classmethod
    def get_best_logger(cls, **kwargs) -> LoggingInterface:
        """
        Get the best available logging implementation for the current system

        Args:
            **kwargs: Additional arguments for logger implementation

        Returns:
            LoggingInterface: Best available logger implementation
        """
        # Try Rich first (better UX)
        try:
            return cls.create_logger("rich", **kwargs)
        except Exception:
            pass

        # Fall back to simple logger
        return cls.create_logger("simple", **kwargs)

    @classmethod
    def register_implementation(cls, name: str, implementation: Type[LoggingInterface]):
        """
        Register a new logging implementation

        Args:
            name: Name for the implementation
            implementation: Logger implementation class
        """
        cls._implementations[name] = implementation

    @classmethod
    def list_implementations(cls) -> list:
        """List available logging implementations"""
        return list(cls._implementations.keys())


# Convenience functions following existing pattern
def get_logger(logger_type: str = "default", **kwargs) -> LoggingInterface:
    """
    Get logger instance (convenience function)

    Args:
        logger_type: Logger type
        **kwargs: Additional arguments

    Returns:
        LoggingInterface: Configured logger instance
    """
    return LoggingFactory.create_logger(logger_type, **kwargs)


def get_best_logger(**kwargs) -> LoggingInterface:
    """
    Get the best available logger for the system

    Args:
        **kwargs: Additional arguments

    Returns:
        LoggingInterface: Best available logger implementation
    """
    return LoggingFactory.get_best_logger(**kwargs)
