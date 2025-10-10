#!/usr/bin/env python3
"""
Configuration Manager Interface
Defines the contract for configuration management
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Type, TypeVar, Union

T = TypeVar("T")  # Type of configuration value
ConfigValue = Union[str, int, float, bool, dict, list]  # Supported value types


class IConfigManager(ABC):
    """Interface for configuration management"""

    @abstractmethod
    def get_value(
        self, key: str, value_type: Type[T], default: Optional[T] = None
    ) -> Optional[T]:
        """
        Get configuration value with type checking

        Args:
            key: Configuration key
            value_type: Expected type of value
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        pass

    @abstractmethod
    def set_value(self, key: str, value: ConfigValue) -> None:
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Value to store
        """
        pass

    @abstractmethod
    def get_section(self, section: str) -> Dict[str, ConfigValue]:
        """
        Get all configuration values in a section

        Args:
            section: Configuration section name

        Returns:
            Dictionary of configuration values
        """
        pass

    @abstractmethod
    def set_section(self, section: str, values: Dict[str, ConfigValue]) -> None:
        """
        Set all configuration values in a section

        Args:
            section: Configuration section name
            values: Dictionary of values to store
        """
        pass

    @abstractmethod
    def clear_section(self, section: str) -> None:
        """
        Clear all configuration values in a section

        Args:
            section: Configuration section name
        """
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Clear all configuration values"""
        pass
