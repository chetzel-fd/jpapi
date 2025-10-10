#!/usr/bin/env python3
"""
Factory Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ConfigurationError(Exception):
    """Configuration error"""

    pass


class IFactory(ABC):
    """Interface for factory pattern"""

    @abstractmethod
    def create(self, config: Dict[str, Any]) -> Any:
        """Create instance from configuration"""
        pass

    @abstractmethod
    def can_create(self, config: Dict[str, Any]) -> bool:
        """Check if factory can create instance from config"""
        pass
