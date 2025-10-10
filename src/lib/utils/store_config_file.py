#!/usr/bin/env python3
"""
File-based Configuration Storage
Implements configuration storage using JSON files
"""

import json
from pathlib import Path
from typing import Optional
from interfaces.config_storage import IConfigStorage


class FileConfigStorage(IConfigStorage):
    """File-based configuration storage implementation"""

    def __init__(self, config_dir: str = "~/.jpapi"):
        """
        Initialize file storage

        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value from file"""
        config_file = self.config_dir / f"{key}.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    return config.get(key)
            except (json.JSONDecodeError, KeyError, IOError):
                pass
        return None

    def set_config(self, key: str, value: str) -> None:
        """Store configuration value in file"""
        config_file = self.config_dir / f"{key}.json"
        config = {key: value.strip()}
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

    def get(self, key: str) -> Optional[str]:
        """Get value from file"""
        return self.get_config(key)

    def set(self, key: str, value: str) -> None:
        """Set value in file"""
        self.set_config(key, value)

    def delete(self, key: str) -> None:
        """Delete value from file"""
        config_file = self.config_dir / f"{key}.json"
        if config_file.exists():
            config_file.unlink()

    def get_all(self) -> dict:
        """Get all configuration values"""
        result = {}
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    result.update(config)
            except (json.JSONDecodeError, IOError):
                pass
        return result
