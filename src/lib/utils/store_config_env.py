#!/usr/bin/env python3
"""
Environment-based Configuration Storage
Implements configuration storage using environment variables
"""

import os
from typing import Optional
from interfaces.config_storage import IConfigStorage


class EnvConfigStorage(IConfigStorage):
    """Environment-based configuration storage implementation"""

    def __init__(self, prefix: str = "JAPIDEV_"):
        """
        Initialize environment storage

        Args:
            prefix: Prefix for environment variables
        """
        self.prefix = prefix

    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value from environment"""
        env_key = f"{self.prefix}{key.upper()}"
        value = os.getenv(env_key)
        return value.strip() if value else None

    def set_config(self, key: str, value: str) -> None:
        """Store configuration value in environment"""
        env_key = f"{self.prefix}{key.upper()}"
        os.environ[env_key] = value.strip()

    def get(self, key: str) -> Optional[str]:
        """Get value from environment"""
        return self.get_config(key)

    def set(self, key: str, value: str) -> None:
        """Set value in environment"""
        self.set_config(key, value)

    def delete(self, key: str) -> None:
        """Delete value from environment"""
        env_key = f"{self.prefix}{key.upper()}"
        if env_key in os.environ:
            del os.environ[env_key]

    def get_all(self) -> dict:
        """Get all configuration values"""
        result = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix) :].lower()
                result[config_key] = value
        return result
