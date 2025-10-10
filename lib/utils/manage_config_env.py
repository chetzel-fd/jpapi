#!/usr/bin/env python3
"""
Environment-based Configuration Manager
Implements configuration management using environment variables
"""

import os
import json
from typing import Dict, Optional, Type, TypeVar, cast
from ..interfaces.config_manager import IConfigManager, ConfigValue

T = TypeVar("T", bound=ConfigValue)  # Type of configuration value


class EnvConfigManager(IConfigManager):
    """Environment-based configuration manager implementation"""

    def __init__(self, prefix: str = "JAPIDEV_"):
        """
        Initialize environment-based configuration manager

        Args:
            prefix: Prefix for environment variables
        """
        self.prefix = prefix

    def get_value(
        self, key: str, value_type: Type[T], default: Optional[T] = None
    ) -> Optional[T]:
        """Get configuration value from environment"""
        env_key = self._make_env_key(key)
        value = os.getenv(env_key)

        if value is None:
            return default

        try:
            # Handle special cases
            if value_type == bool:
                return cast(T, value.lower() in ("true", "yes", "1", "on"))
            elif value_type == dict:
                return cast(T, json.loads(value))
            elif value_type == list:
                return cast(T, json.loads(value))
            if value_type == str:
                return cast(T, value)
            elif value_type == int:
                return cast(T, int(value))
            elif value_type == float:
                return cast(T, float(value))
            else:
                raise ValueError(f"Unsupported type: {value_type}")
        except (ValueError, TypeError, json.JSONDecodeError):
            return default

    def set_value(self, key: str, value: ConfigValue) -> None:
        """Store configuration value in environment"""
        env_key = self._make_env_key(key)
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        os.environ[env_key] = str(value)

    def get_section(self, section: str) -> Dict[str, ConfigValue]:
        """Get all configuration values in a section"""
        prefix = f"{self.prefix}{section.upper()}_"
        result = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                name = key[len(prefix) :].lower()
                try:
                    # Try to parse as JSON
                    result[name] = json.loads(value)
                except json.JSONDecodeError:
                    result[name] = value
        return result

    def set_section(self, section: str, values: Dict[str, ConfigValue]) -> None:
        """Set all configuration values in a section"""
        for key, value in values.items():
            full_key = f"{section}.{key}"
            self.set_value(full_key, value)

    def clear_section(self, section: str) -> None:
        """Clear all configuration values in a section"""
        prefix = f"{self.prefix}{section.upper()}_"
        for key in list(os.environ.keys()):
            if key.startswith(prefix):
                del os.environ[key]

    def clear_all(self) -> None:
        """Clear all configuration values"""
        for key in list(os.environ.keys()):
            if key.startswith(self.prefix):
                del os.environ[key]

    def _make_env_key(self, key: str) -> str:
        """Convert configuration key to environment variable name"""
        section, key_name = self._split_key(key)
        return f"{self.prefix}{section.upper()}_{key_name.upper()}"

    def _split_key(self, key: str) -> tuple[str, str]:
        """Split key into section and key name"""
        parts = key.split(".", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return "default", key
