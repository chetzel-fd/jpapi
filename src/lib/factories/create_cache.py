#!/usr/bin/env python3
"""
Cache Factory
Creates and manages cache manager instances
"""

from typing import Dict, Type, Optional, Any
from src.interfaces import ICacheManager
from src.interfaces.factory import IFactory, ConfigurationError
from ..utils import FileCache


class CacheFactory(IFactory[ICacheManager, Dict[str, Any]]):
    """Factory for creating cache managers"""

    def __init__(self):
        """Initialize with default cache types"""
        self._cache_types: Dict[str, Type[ICacheManager]] = {
            "file": FileCache,
        }

    def register(self, name: str, implementation: Type[ICacheManager]) -> None:
        """
        Register a new cache type

        Args:
            name: Name to register the cache under
            implementation: The cache class to register

        Raises:
            ValueError: If the implementation doesn't implement ICacheManager
        """
        if not issubclass(implementation, ICacheManager):
            raise ValueError(f"{implementation.__name__} must implement ICacheManager")
        self._cache_types[name] = implementation

    def create(
        self, name: str, config: Optional[Dict[str, Any]] = None
    ) -> ICacheManager:
        """
        Create a cache manager instance

        Args:
            name: Type of cache to create
            config: Optional configuration for the cache instance

        Returns:
            An instance of the requested cache manager

        Raises:
            ValueError: If the requested cache type is not registered
            ConfigurationError: If the provided configuration is invalid
        """
        if name not in self._cache_types:
            raise ValueError(f"Unknown cache type: {name}")

        try:
            return self._cache_types[name](**(config or {}))
        except (TypeError, ValueError) as e:
            raise ConfigurationError(f"Invalid configuration for {name} cache: {e}")

    def get_available_types(self) -> Dict[str, Type[ICacheManager]]:
        """
        Get all registered cache types

        Returns:
            Dict mapping cache type names to their classes
        """
        return self._cache_types.copy()

    def create_layered_cache(self, layers: Dict[str, Dict[str, Any]]) -> ICacheManager:
        """
        Create a layered cache with multiple cache types

        Args:
            layers: Dict mapping cache types to their configurations,
                   ordered from fastest to slowest

        Returns:
            A layered cache manager instance

        Example:
            layers = {
                "memory": {"max_size": 1000},
                "file": {"cache_dir": "/tmp/cache"}
            }

        Raises:
            ConfigurationError: If any layer configuration is invalid
        """
        from ..utils.cache_layered import LayeredCache

        instances = []
        for cache_type, config in layers.items():
            try:
                instances.append(self.create(cache_type, config))
            except (ValueError, ConfigurationError) as e:
                raise ConfigurationError(f"Failed to create {cache_type} layer: {e}")
        return LayeredCache(instances)

    def create_distributed_cache(
        self, nodes: Dict[str, Dict[str, Any]]
    ) -> ICacheManager:
        """
        Create a distributed cache across multiple nodes

        Args:
            nodes: Dict mapping node names to their cache configurations

        Returns:
            A distributed cache manager instance

        Example:
            nodes = {
                "node1": {"type": "file", "cache_dir": "/cache1"},
                "node2": {"type": "file", "cache_dir": "/cache2"}
            }

        Raises:
            ConfigurationError: If any node configuration is invalid
        """
        from ..utils.cache_distributed import DistributedCache

        instances = {}
        for node_name, config in nodes.items():
            try:
                cache_type = config.pop("type", "file")
                instances[node_name] = self.create(cache_type, config)
            except (ValueError, ConfigurationError) as e:
                raise ConfigurationError(
                    f"Failed to create cache for node {node_name}: {e}"
                )
        return DistributedCache(instances)
