#!/usr/bin/env python3
"""
Cache Factory
Creates and manages cache manager instances
"""

from typing import Dict, Type, Optional
from pathlib import Path
from src.interfaces import ICacheManager
from ..utils import FileCache


class CacheFactory:
    """Factory for creating cache managers"""

    _cache_types: Dict[str, Type[ICacheManager]] = {
        "file": FileCache,
    }

    @classmethod
    def register_cache_type(cls, name: str, cache_class: Type[ICacheManager]) -> None:
        """
        Register a new cache type
        
        Args:
            name: Name to register the cache under
            cache_class: The cache class to register
        """
        if not issubclass(cache_class, ICacheManager):
            raise ValueError(f"{cache_class.__name__} must implement ICacheManager")
        cls._cache_types[name] = cache_class

    @classmethod
    def create_cache(cls, cache_type: str = "file", **kwargs) -> ICacheManager:
        """
        Create a cache manager instance
        
        Args:
            cache_type: Type of cache to create
            **kwargs: Additional arguments to pass to the cache constructor
            
        Returns:
            An instance of the requested cache manager
            
        Raises:
            ValueError: If the requested cache type is not registered
        """
        if cache_type not in cls._cache_types:
            raise ValueError(f"Unknown cache type: {cache_type}")
        return cls._cache_types[cache_type](**kwargs)

    @classmethod
    def get_available_cache_types(cls) -> Dict[str, Type[ICacheManager]]:
        """
        Get all registered cache types
        
        Returns:
            Dict mapping cache type names to their classes
        """
        return cls._cache_types.copy()

    @classmethod
    def create_layered_cache(cls, layers: Dict[str, Dict]) -> ICacheManager:
        """
        Create a layered cache with multiple cache types
        
        Args:
            layers: Dict mapping cache types to their constructor arguments,
                   ordered from fastest to slowest
            
        Returns:
            A layered cache manager instance
            
        Example:
            layers = {
                "memory": {"max_size": 1000},
                "file": {"cache_dir": "/tmp/cache"}
            }
        """
        from ..utils.layered_cache import LayeredCache

        instances = []
        for cache_type, args in layers.items():
            instances.append(cls.create_cache(cache_type, **args))
        return LayeredCache(instances)

    @classmethod
    def create_distributed_cache(cls, nodes: Dict[str, Dict]) -> ICacheManager:
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
        """
        from ..utils.distributed_cache import DistributedCache

        instances = {}
        for node_name, config in nodes.items():
            cache_type = config.pop("type", "file")
            instances[node_name] = cls.create_cache(cache_type, **config)
        return DistributedCache(instances)
