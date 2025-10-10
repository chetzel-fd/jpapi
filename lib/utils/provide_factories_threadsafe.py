#!/usr/bin/env python3
"""
Thread-safe Factory Provider
Implements lazy loading of factory instances with thread safety
"""

import threading
from typing import Any, Dict, Optional, Type, TypeVar, cast
from ..interfaces.factory import IFactory
from ..interfaces.factory_provider import IFactoryProvider

T = TypeVar("T")  # Type of object being created
C = TypeVar("C")  # Type of configuration


class ThreadSafeFactoryProvider(IFactoryProvider):
    """Thread-safe factory provider implementation"""

    def __init__(self):
        """Initialize factory provider"""
        self._factory_configs: Dict[Type[IFactory[Any, Any]], Dict[str, Any]] = {}
        self._factory_instances: Dict[Type[IFactory[Any, Any]], IFactory[Any, Any]] = {}
        self._lock = threading.RLock()

    def register_factory(
        self,
        factory_type: Type[IFactory[T, C]],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a factory type with optional configuration"""
        with self._lock:
            self._factory_configs[factory_type] = config or {}

    def get_factory(self, factory_type: Type[IFactory[T, C]]) -> IFactory[T, C]:
        """Get or create a factory instance"""
        with self._lock:
            if factory_type not in self._factory_configs:
                raise ValueError(
                    f"Factory type not registered: {factory_type.__name__}"
                )

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
        with self._lock:
            self._factory_instances.clear()
