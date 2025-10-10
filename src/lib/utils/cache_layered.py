#!/usr/bin/env python3
"""
Layered Cache
Implements a multi-layer caching system
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from src.interfaces import ICacheManager


class LayeredCache(ICacheManager):
    """Multi-layer caching system"""

    def __init__(self, layers: List[ICacheManager]):
        """
        Initialize with ordered list of cache layers
        
        Args:
            layers: List of cache managers, ordered from fastest to slowest
        """
        self._layers = layers

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, trying each layer"""
        value = None
        found_in_layer = -1

        # Try to get from each layer
        for i, layer in enumerate(self._layers):
            value = layer.get(key)
            if value is not None:
                found_in_layer = i
                break

        # If found in a slower layer, populate faster layers
        if found_in_layer > 0:
            ttl = self._layers[found_in_layer].get_ttl(key)
            for i in range(found_in_layer):
                self._layers[i].set(key, value, ttl)

        return value

    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """Set value in all cache layers"""
        success = True
        for layer in self._layers:
            if not layer.set(key, value, ttl):
                success = False
        return success

    def delete(self, key: str) -> bool:
        """Delete value from all cache layers"""
        success = True
        for layer in self._layers:
            if not layer.delete(key):
                success = False
        return success

    def exists(self, key: str) -> bool:
        """Check if key exists in any cache layer"""
        for layer in self._layers:
            if layer.exists(key):
                return True
        return False

    def get_ttl(self, key: str) -> Optional[timedelta]:
        """Get TTL from first layer that has the key"""
        for layer in self._layers:
            ttl = layer.get_ttl(key)
            if ttl is not None:
                return ttl
        return None

    def set_ttl(self, key: str, ttl: timedelta) -> bool:
        """Set TTL in all cache layers"""
        success = True
        for layer in self._layers:
            if not layer.set_ttl(key, ttl):
                success = False
        return success

    def clear(self) -> bool:
        """Clear all cache layers"""
        success = True
        for layer in self._layers:
            if not layer.clear():
                success = False
        return success

    def get_stats(self) -> Dict[str, Any]:
        """Get combined cache statistics"""
        stats = {
            "layers": len(self._layers),
            "total_size": 0,
            "total_entries": 0,
            "total_hits": 0,
            "total_misses": 0,
            "layer_stats": []
        }

        for i, layer in enumerate(self._layers):
            layer_stats = layer.get_stats()
            stats["total_size"] += layer_stats.get("size", 0)
            stats["total_entries"] += layer_stats.get("entries", 0)
            stats["total_hits"] += layer_stats.get("hits", 0)
            stats["total_misses"] += layer_stats.get("misses", 0)
            stats["layer_stats"].append({
                "layer": i,
                "stats": layer_stats
            })

        if stats["total_hits"] + stats["total_misses"] > 0:
            stats["overall_hit_rate"] = (
                stats["total_hits"] /
                (stats["total_hits"] + stats["total_misses"])
            )
        else:
            stats["overall_hit_rate"] = 0

        return stats

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get unique keys from all layers matching pattern"""
        keys = set()
        for layer in self._layers:
            keys.update(layer.get_keys(pattern))
        return sorted(list(keys))

    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values, trying each layer"""
        results = {}
        remaining_keys = set(keys)

        # Try each layer
        for i, layer in enumerate(self._layers):
            if not remaining_keys:
                break

            layer_results = layer.get_multiple(list(remaining_keys))
            
            # Update results and populate faster layers
            for key, value in layer_results.items():
                if value is not None:
                    results[key] = value
                    remaining_keys.remove(key)
                    
                    # Populate faster layers
                    if i > 0:
                        ttl = layer.get_ttl(key)
                        for j in range(i):
                            self._layers[j].set(key, value, ttl)

        return results

    def set_multiple(self, items: Dict[str, Any], ttl: Optional[timedelta] = None) -> bool:
        """Set multiple values in all layers"""
        success = True
        for layer in self._layers:
            if not layer.set_multiple(items, ttl):
                success = False
        return success

    def delete_multiple(self, keys: List[str]) -> bool:
        """Delete multiple values from all layers"""
        success = True
        for layer in self._layers:
            if not layer.delete_multiple(keys):
                success = False
        return success
