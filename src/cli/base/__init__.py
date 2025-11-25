"""CLI base classes and utilities"""

from .command import BaseCommand
from .registry import CommandRegistry, registry
from .output_formatter import OutputFormatter
from .safety_validator import SafetyValidator
from .pattern_matcher import PatternMatcher, CommandPattern, SubcommandConfig
from .validators import InputValidators
from .error_handler import APIErrorHandler, ErrorContext, ErrorType

__all__ = [
    "BaseCommand",
    "CommandRegistry",
    "registry",
    "OutputFormatter",
    "SafetyValidator",
    "PatternMatcher",
    "CommandPattern",
    "SubcommandConfig",
    "InputValidators",
    "APIErrorHandler",
    "ErrorContext",
    "ErrorType",
]
