#!/usr/bin/env python3
"""
Dependency Injection Container
Manages factory instances and dependencies
"""

from typing import Dict, TypeVar, Any, Optional
from interfaces.factory import IFactory

T = TypeVar("T")  # Type of object being created


class Container:
    """Dependency injection container"""

    def __init__(self):
        """Initialize container"""
        self._factories: Dict[str, IFactory] = {}
        self._singletons: Dict[str, Any] = {}
        self._configs: Dict[str, Any] = {}

    def register_factory(self, name: str, factory: IFactory) -> None:
        """
        Register a factory

        Args:
            name: Name to register the factory under
            factory: The factory instance to register
        """
        self._factories[name] = factory

    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register a singleton instance

        Args:
            name: Name to register the singleton under
            instance: The singleton instance
        """
        self._singletons[name] = instance

    def register_config(self, name: str, config: Any) -> None:
        """
        Register configuration

        Args:
            name: Name to register the config under
            config: The configuration data
        """
        self._configs[name] = config

    def get_factory(self, name: str) -> Optional[IFactory]:
        """
        Get a registered factory

        Args:
            name: Name of the factory to get

        Returns:
            The factory instance or None if not found
        """
        return self._factories.get(name)

    def get_singleton(self, name: str) -> Optional[Any]:
        """
        Get a registered singleton

        Args:
            name: Name of the singleton to get

        Returns:
            The singleton instance or None if not found
        """
        return self._singletons.get(name)

    def get_config(self, name: str) -> Optional[Any]:
        """
        Get registered configuration

        Args:
            name: Name of the config to get

        Returns:
            The configuration data or None if not found
        """
        return self._configs.get(name)

    def create(
        self, factory_name: str, object_name: str, config: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Create an object using a registered factory

        Args:
            factory_name: Name of the factory to use
            object_name: Name of the object type to create
            config: Optional configuration to pass to the factory

        Returns:
            The created object or None if factory not found

        Raises:
            ValueError: If the factory or object type is not found
            ConfigurationError: If the configuration is invalid
        """
        factory = self.get_factory(factory_name)
        if not factory:
            raise ValueError(f"Factory not found: {factory_name}")

        # Merge with registered config if available
        if config is None and factory_name in self._configs:
            config = self._configs[factory_name]

        return factory.create(object_name, config)


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance"""
    global _container
    if _container is None:
        _container = Container()
    return _container
