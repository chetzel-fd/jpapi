#!/usr/bin/env python3
"""
Config Storage Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IConfigStorage(ABC):
    """Interface for configuration storage"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get configuration value"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete configuration value"""
        pass

    @abstractmethod
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        pass
