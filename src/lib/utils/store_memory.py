#!/usr/bin/env python3
"""
Memory Cache Storage
Implements in-memory cache storage with LRU eviction
"""

from typing import Dict, Optional
from interfaces.cache_storage import ICacheStorage
from .cache_types import CacheEntry


class MemoryStorage(ICacheStorage):
    """In-memory cache storage implementation"""

    def __init__(self, max_items: int = 1000):
        """
        Initialize memory storage

        Args:
            max_items: Maximum number of items to store in memory
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._max_items = max_items

    def get(self, key: str) -> Optional[Dict]:
        """Get entry from memory storage"""
        entry = self._cache.get(key)
        if entry:
            return {
                "key": entry.key,
                "data": entry.data,
                "tier": entry.tier.value,
                "ttl": entry.ttl,
                "created_at": entry.created_at,
                "access_count": entry.access_count,
                "last_access": entry.last_access,
                "priority": entry.priority,
            }
        return None

    def put(self, entry: CacheEntry) -> None:
        """Store entry in memory storage"""
        if len(self._cache) >= self._max_items:
            self._evict_lru()
        self._cache[entry.key] = entry

    def remove(self, key: str) -> None:
        """Remove entry from memory storage"""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all entries from memory storage"""
        self._cache.clear()

    def count(self) -> int:
        """Get count of entries in memory storage"""
        return len(self._cache)

    def _evict_lru(self) -> None:
        """Evict least recently used item from memory"""
        if not self._cache:
            return

        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_access)
        del self._cache[lru_key]
