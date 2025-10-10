#!/usr/bin/env python3
"""
File-based Configuration Manager
Implements configuration management using JSON files
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, cast
from interfaces.config_manager import IConfigManager, ConfigValue

T = TypeVar("T", bound=ConfigValue)  # Type of configuration value


class FileConfigManager(IConfigManager):
    """File-based configuration manager implementation"""

    def __init__(self, config_dir: str = "~/.jpapi/config"):
        """
        Initialize file-based configuration manager

        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_value(
        self, key: str, value_type: Type[T], default: Optional[T] = None
    ) -> Optional[T]:
        """Get configuration value from file"""
        section, key_name = self._split_key(key)
        config = self._load_section(section)
        value = config.get(key_name)

        if value is None:
            return default

        try:
            # Handle special cases
            if value_type == bool and isinstance(value, str):
                return cast(T, value.lower() in ("true", "yes", "1", "on"))
            elif value_type == dict and isinstance(value, str):
                return cast(T, json.loads(value))
            elif value_type == list and isinstance(value, str):
                return cast(T, json.loads(value))
            return cast(T, value_type(value))
        except (ValueError, TypeError):
            return default

    def set_value(self, key: str, value: ConfigValue) -> None:
        """Store configuration value in file"""
        section, key_name = self._split_key(key)
        config = self._load_section(section)
        config[key_name] = value
        self._save_section(section, config)

    def get_section(self, section: str) -> Dict[str, ConfigValue]:
        """Get all configuration values in a section"""
        return self._load_section(section)

    def set_section(self, section: str, values: Dict[str, ConfigValue]) -> None:
        """Set all configuration values in a section"""
        self._save_section(section, values)

    def clear_section(self, section: str) -> None:
        """Clear all configuration values in a section"""
        config_file = self.config_dir / f"{section}.json"
        if config_file.exists():
            config_file.unlink()

    def clear_all(self) -> None:
        """Clear all configuration values"""
        for config_file in self.config_dir.glob("*.json"):
            config_file.unlink()

    def _split_key(self, key: str) -> tuple[str, str]:
        """Split key into section and key name"""
        parts = key.split(".", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return "default", key

    def _load_section(self, section: str) -> Dict[str, Any]:
        """Load configuration section from file"""
        config_file = self.config_dir / f"{section}.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_section(self, section: str, config: Dict[str, Any]) -> None:
        """Save configuration section to file"""
        config_file = self.config_dir / f"{section}.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
