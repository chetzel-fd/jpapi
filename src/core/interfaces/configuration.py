#!/usr/bin/env python3
"""
Configuration Interfaces
Defines interfaces for configuration management following SRP and ISP
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConfigurationChange:
    """Configuration change record"""

    timestamp: datetime
    key: str
    old_value: Any
    new_value: Any
    source: str
    user_id: Optional[str] = None


class IConfigurationValidator(ABC):
    """Interface for configuration validation following SRP"""

    @abstractmethod
    def validate(self, key: str, value: Any) -> bool:
        """Validate a configuration value"""
        pass

    @abstractmethod
    def get_error_message(self, key: str, value: Any) -> str:
        """Get validation error message"""
        pass


class IConfigurationManager(ABC):
    """Core configuration management interface following SRP"""

    @abstractmethod
    def get(self, key: str, default: Any = None, tenant: Optional[str] = None) -> Any:
        """Get configuration value"""
        pass

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        tenant: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Set configuration value"""
        pass

    @abstractmethod
    def has(self, key: str, tenant: Optional[str] = None) -> bool:
        """Check if configuration key exists"""
        pass

    @abstractmethod
    def delete(self, key: str, tenant: Optional[str] = None) -> bool:
        """Delete configuration key"""
        pass

    @abstractmethod
    def get_all(self, tenant: Optional[str] = None) -> Dict[str, Any]:
        """Get all configuration values"""
        pass


class IConfigurationLoader(ABC):
    """Interface for loading configuration from various sources"""

    @abstractmethod
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from source"""
        pass

    @abstractmethod
    def save(self, config: Dict[str, Any], destination: str) -> None:
        """Save configuration to destination"""
        pass


class IConfigurationWatcher(ABC):
    """Interface for watching configuration changes"""

    @abstractmethod
    def add_change_callback(
        self, callback: Callable[[ConfigurationChange], None]
    ) -> None:
        """Add callback for configuration changes"""
        pass

    @abstractmethod
    def remove_change_callback(
        self, callback: Callable[[ConfigurationChange], None]
    ) -> None:
        """Remove configuration change callback"""
        pass

    @abstractmethod
    def get_change_history(self, hours: int = 24) -> List[ConfigurationChange]:
        """Get configuration change history"""
        pass
