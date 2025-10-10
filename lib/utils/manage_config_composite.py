#!/usr/bin/env python3
"""
Composite Configuration Manager
Implements configuration management using multiple managers
"""

from typing import Dict, List, Optional, Type, TypeVar
from ..interfaces.config_manager import IConfigManager, ConfigValue

T = TypeVar("T", bound=ConfigValue)  # Type of configuration value


class CompositeConfigManager(IConfigManager):
    """Composite configuration manager implementation"""

    def __init__(self, managers: List[IConfigManager]):
        """
        Initialize composite configuration manager

        Args:
            managers: List of configuration managers in priority order
        """
        self.managers = managers

    def get_value(
        self, key: str, value_type: Type[T], default: Optional[T] = None
    ) -> Optional[T]:
        """Get configuration value from first manager that has it"""
        for manager in self.managers:
            value = manager.get_value(key, value_type, None)
            if value is not None:
                return value
        return default

    def set_value(self, key: str, value: ConfigValue) -> None:
        """Store configuration value in all managers"""
        for manager in self.managers:
            manager.set_value(key, value)

    def get_section(self, section: str) -> Dict[str, ConfigValue]:
        """Get all configuration values in a section"""
        result = {}
        for manager in reversed(self.managers):
            # Start with lowest priority manager
            result.update(manager.get_section(section))
        return result

    def set_section(self, section: str, values: Dict[str, ConfigValue]) -> None:
        """Set all configuration values in a section"""
        for manager in self.managers:
            manager.set_section(section, values)

    def clear_section(self, section: str) -> None:
        """Clear all configuration values in a section"""
        for manager in self.managers:
            manager.clear_section(section)

    def clear_all(self) -> None:
        """Clear all configuration values"""
        for manager in self.managers:
            manager.clear_all()
