#!/usr/bin/env python3
"""
Factory Provider Interface
Defines the contract for factory providers
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar

from .factory import IFactory

T = TypeVar("T")  # Type of object being created
C = TypeVar("C")  # Type of configuration


class IFactoryProvider(ABC):
    """Interface for factory providers"""

    @abstractmethod
    def register_factory(
        self,
        factory_type: Type[IFactory[T, C]],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a factory type with optional configuration

        Args:
            factory_type: The factory class to register
            config: Optional configuration for the factory
        """
        pass

    @abstractmethod
    def get_factory(self, factory_type: Type[IFactory[T, C]]) -> IFactory[T, C]:
        """
        Get or create a factory instance

        Args:
            factory_type: The factory class to get

        Returns:
            Factory instance

        Raises:
            ValueError: If factory type is not registered
        """
        pass

    @abstractmethod
    def clear_factories(self) -> None:
        """Clear all factory instances"""
        pass
