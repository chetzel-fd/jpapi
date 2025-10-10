#!/usr/bin/env python3
"""
Singleton Factory Provider
Implements lazy loading of factory instances with singleton pattern
"""

from typing import Any, Dict, Optional, Type, TypeVar, cast
from ..interfaces.factory import IFactory
from ..interfaces.factory_provider import IFactoryProvider

T = TypeVar("T")  # Type of object being created
C = TypeVar("C")  # Type of configuration


class SingletonFactoryProvider(IFactoryProvider):
    """Singleton factory provider implementation"""

    _instance = None

    def __new__(cls):
        """Create or return singleton instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize factory provider (only once)"""
        if not self._initialized:
            self._factory_configs: Dict[Type[IFactory[Any, Any]], Dict[str, Any]] = {}
            self._factory_instances: Dict[
                Type[IFactory[Any, Any]], IFactory[Any, Any]
            ] = {}
            self._initialized = True

    def register_factory(
        self,
        factory_type: Type[IFactory[T, C]],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a factory type with optional configuration"""
        self._factory_configs[factory_type] = config or {}

    def get_factory(self, factory_type: Type[IFactory[T, C]]) -> IFactory[T, C]:
        """Get or create a factory instance"""
        if factory_type not in self._factory_configs:
            raise ValueError(f"Factory type not registered: {factory_type.__name__}")

        if factory_type not in self._factory_instances:
            # Create new instance with configuration
            config = self._factory_configs[factory_type]
            instance = factory_type()
            for key, value in config.items():
                setattr(instance, key, value)
            self._factory_instances[factory_type] = instance

        return cast(IFactory[T, C], self._factory_instances[factory_type])

    def clear_factories(self) -> None:
        """Clear all factory instances"""
        self._factory_instances.clear()
