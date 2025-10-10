#!/usr/bin/env python3
"""
Composite Configuration Storage
Implements configuration storage using multiple storage backends
"""

from typing import List, Optional
from src.interfaces.config_storage import IConfigStorage


class CompositeConfigStorage(IConfigStorage):
    """Composite configuration storage implementation"""

    def __init__(self, storages: List[IConfigStorage]):
        """
        Initialize composite storage

        Args:
            storages: List of storage implementations in priority order
        """
        self.storages = storages

    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value from first storage that has it"""
        for storage in self.storages:
            value = storage.get_config(key)
            if value is not None:
                return value
        return None

    def set_config(self, key: str, value: str) -> None:
        """Store configuration value in all storages"""
        for storage in self.storages:
            storage.set_config(key, value)

    def get(self, key: str) -> Optional[str]:
        """Get value from first storage that has it"""
        return self.get_config(key)

    def set(self, key: str, value: str) -> None:
        """Set value in all storages"""
        self.set_config(key, value)

    def delete(self, key: str) -> None:
        """Delete value from all storages"""
        for storage in self.storages:
            storage.delete(key)

    def get_all(self) -> dict:
        """Get all configuration values from all storages"""
        result = {}
        for storage in self.storages:
            storage_all = storage.get_all()
            result.update(storage_all)
        return result
