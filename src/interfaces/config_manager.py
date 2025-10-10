#!/usr/bin/env python3
"""
Config Manager Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ConfigValue:
    """Configuration value container"""

    value: Any
    source: str
    timestamp: float


class IConfigManager(ABC):
    """Interface for configuration management"""

    @abstractmethod
    def get(self, key: str) -> Optional[ConfigValue]:
        """Get configuration value"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, source: str = "manual") -> None:
        """Set configuration value"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete configuration value"""
        pass

    @abstractmethod
    def get_all(self) -> Dict[str, ConfigValue]:
        """Get all configuration values"""
        pass
