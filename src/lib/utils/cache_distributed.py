#!/usr/bin/env python3
"""
Distributed Cache
Implements a distributed caching system across multiple nodes
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
from src.interfaces import ICacheManager


class DistributedCache(ICacheManager):
    """Distributed caching system"""

    def __init__(self, nodes: Dict[str, ICacheManager]):
        """
        Initialize with node cache managers
        
        Args:
            nodes: Dict mapping node names to their cache managers
        """
        self._nodes = nodes
        self._node_names = sorted(nodes.keys())

    def get(self, key: str) -> Optional[Any]:
        """Get value from appropriate node"""
        node = self._get_node_for_key(key)
        return self._nodes[node].get(key)

    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """Set value in appropriate node"""
        node = self._get_node_for_key(key)
        return self._nodes[node].set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete value from appropriate node"""
        node = self._get_node_for_key(key)
        return self._nodes[node].delete(key)

    def exists(self, key: str) -> bool:
        """Check if key exists in appropriate node"""
        node = self._get_node_for_key(key)
        return self._nodes[node].exists(key)

    def get_ttl(self, key: str) -> Optional[timedelta]:
        """Get TTL from appropriate node"""
        node = self._get_node_for_key(key)
        return self._nodes[node].get_ttl(key)

    def set_ttl(self, key: str, ttl: timedelta) -> bool:
        """Set TTL in appropriate node"""
        node = self._get_node_for_key(key)
        return self._nodes[node].set_ttl(key, ttl)

    def clear(self) -> bool:
        """Clear all nodes"""
        success = True
        for node in self._nodes.values():
            if not node.clear():
                success = False
        return success

    def get_stats(self) -> Dict[str, Any]:
        """Get combined cache statistics"""
        stats = {
            "nodes": len(self._nodes),
            "total_size": 0,
            "total_entries": 0,
            "total_hits": 0,
            "total_misses": 0,
            "node_stats": {}
        }

        for node_name, node in self._nodes.items():
            node_stats = node.get_stats()
            stats["total_size"] += node_stats.get("size", 0)
            stats["total_entries"] += node_stats.get("entries", 0)
            stats["total_hits"] += node_stats.get("hits", 0)
            stats["total_misses"] += node_stats.get("misses", 0)
            stats["node_stats"][node_name] = node_stats

        if stats["total_hits"] + stats["total_misses"] > 0:
            stats["overall_hit_rate"] = (
                stats["total_hits"] /
                (stats["total_hits"] + stats["total_misses"])
            )
        else:
            stats["overall_hit_rate"] = 0

        return stats

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get keys from all nodes matching pattern"""
        keys = set()
        for node in self._nodes.values():
            keys.update(node.get_keys(pattern))
        return sorted(list(keys))

    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from appropriate nodes"""
        # Group keys by node
        node_keys: Dict[str, List[str]] = {}
        for key in keys:
            node = self._get_node_for_key(key)
            if node not in node_keys:
                node_keys[node] = []
            node_keys[node].append(key)

        # Get values from each node
        results = {}
        for node_name, node_keys_list in node_keys.items():
            node_results = self._nodes[node_name].get_multiple(node_keys_list)
            results.update(node_results)

        return results

    def set_multiple(self, items: Dict[str, Any], ttl: Optional[timedelta] = None) -> bool:
        """Set multiple values in appropriate nodes"""
        # Group items by node
        node_items: Dict[str, Dict[str, Any]] = {}
        for key, value in items.items():
            node = self._get_node_for_key(key)
            if node not in node_items:
                node_items[node] = {}
            node_items[node][key] = value

        # Set values in each node
        success = True
        for node_name, node_items_dict in node_items.items():
            if not self._nodes[node_name].set_multiple(node_items_dict, ttl):
                success = False

        return success

    def delete_multiple(self, keys: List[str]) -> bool:
        """Delete multiple values from appropriate nodes"""
        # Group keys by node
        node_keys: Dict[str, List[str]] = {}
        for key in keys:
            node = self._get_node_for_key(key)
            if node not in node_keys:
                node_keys[node] = []
            node_keys[node].append(key)

        # Delete values from each node
        success = True
        for node_name, node_keys_list in node_keys.items():
            if not self._nodes[node_name].delete_multiple(node_keys_list):
                success = False

        return success

    def _get_node_for_key(self, key: str) -> str:
        """
        Determine which node should handle a key
        
        Args:
            key: The cache key
            
        Returns:
            Name of the node that should handle this key
        """
        # Use consistent hashing to determine node
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        node_index = hash_value % len(self._nodes)
        return self._node_names[node_index]
