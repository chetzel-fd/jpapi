#!/usr/bin/env python3
"""
Factory Provider Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IFactoryProvider(ABC):
    """Interface for factory provider"""

    @abstractmethod
    def get_factory(self, factory_type: str) -> Any:
        """Get factory by type"""
        pass

    @abstractmethod
    def list_factories(self) -> List[str]:
        """List available factory types"""
        pass

    @abstractmethod
    def register_factory(self, factory_type: str, factory: Any) -> None:
        """Register a factory"""
        pass
