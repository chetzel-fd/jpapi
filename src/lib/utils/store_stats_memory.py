#!/usr/bin/env python3
"""
Memory Stats Storage
Implements in-memory storage for stats and object lists
"""

from typing import Dict, Any, Optional
from src.interfaces.stats_storage import IStatsStorage


class MemoryStatsStorage(IStatsStorage):
    """In-memory stats storage implementation"""

    def __init__(self):
        """Initialize memory storage"""
        self._stats_cache: Dict[str, Any] = {}
        self._object_cache: Dict[str, Any] = {}

    def get_stats(self, key: str) -> Optional[Dict[str, Any]]:
        """Get stats from memory storage"""
        return self._stats_cache.get(key)

    def store_stats(self, key: str, stats: Dict[str, Any]) -> None:
        """Store stats in memory storage"""
        self._stats_cache[key] = stats.copy()

    def get_objects(self, key: str) -> Optional[Dict[str, Any]]:
        """Get object list from memory storage"""
        return self._object_cache.get(key)

    def store_objects(self, key: str, objects: Dict[str, Any]) -> None:
        """Store object list in memory storage"""
        self._object_cache[key] = objects.copy()

    def clear(self) -> None:
        """Clear all stored data"""
        self._stats_cache.clear()
        self._object_cache.clear()



