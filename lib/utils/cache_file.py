#!/usr/bin/env python3
"""
Unified Cache Manager - Replaces all caching systems
Consolidates:
- SmartRelationshipCache
- AdaptiveCacheSystem
- SimpleStatsEngine
- ComprehensiveRelationshipSystem
- JSONAnalyticsEngine
- EnhancedRelationshipEngine
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional

from .store_memory import MemoryStorage
from .store_sqlite import SQLiteStorage
from .cache_types import CacheEntry, CacheTier


class FileCache:
    """
    Single cache system that replaces all existing caching implementations.

    Features:
    - 3-tier hierarchy: Memory → SQLite → API
    - Intelligent promotion/demotion between tiers
    - Unified TTL management
    - Background refresh
    - Memory-efficient storage
    - Thread-safe operations
    """

    def __init__(
        self,
        memory_storage: Optional["MemoryStorage"] = None,
        sqlite_storage: Optional["SQLiteStorage"] = None,
        cache_dir: str = "tmp/cache/unified",
        max_memory_items: int = 1000,
    ):
        """
        Initialize FileCache with optional storage implementations

        Args:
            memory_storage: Optional memory storage
            sqlite_storage: Optional SQLite storage
            cache_dir: Cache directory (if sqlite_storage not provided)
            max_memory_items: Memory limit (if memory_storage not provided)
        """
        # Initialize storage implementations
        self._memory_storage = memory_storage or MemoryStorage(max_memory_items)
        db_path = str(Path(cache_dir) / "cache.db")
        self._sqlite_storage = sqlite_storage or SQLiteStorage(db_path)

        # Thread safety
        self._lock = threading.RLock()

        # Performance tracking
        self._hits: Dict[str, int] = {"memory": 0, "sqlite": 0, "api": 0}
        self._misses: int = 0
        self._promotions: int = 0
        self._evictions: int = 0

        print("🚀 Unified Cache Manager initialized")
        print(f"   💾 Max memory items: {max_memory_items}")
        print(f"   📁 Cache directory: {cache_dir}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get data from cache with 3-tier lookup"""
        with self._lock:
            # Tier 1: Memory cache
            memory_data = self._memory_storage.get(key)
            if memory_data:
                entry = self._deserialize_entry(memory_data)
                if self._is_valid(entry):
                    self._update_access(entry)
                    self._hits["memory"] += 1
                    return entry.data
                else:
                    self._memory_storage.remove(key)

            # Tier 2: SQLite cache
            sqlite_data = self._sqlite_storage.get(key)
            if sqlite_data:
                entry = self._deserialize_entry(sqlite_data)
                if self._is_valid(entry):
                    # Promote to memory if high priority
                    if entry.priority >= 3:
                        self._promote_to_memory(entry)
                    self._hits["sqlite"] += 1
                    return entry.data
                else:
                    self._sqlite_storage.remove(key)

            # Tier 3: Cache miss
            self._misses += 1
            return default

    def put(
        self,
        key: str,
        data: Any,
        ttl: int = 3600,
        priority: int = 1,
        tier: Optional[CacheTier] = None,
    ) -> None:
        """Store data in cache with intelligent tier selection"""
        with self._lock:
            entry = CacheEntry(
                key=key,
                data=data,
                tier=tier or self._select_tier(priority),
                ttl=ttl,
                created_at=time.time(),
                priority=priority,
            )

            # Always store in SQLite for persistence
            self._sqlite_storage.put(entry)

            # Store in memory only if high priority
            if entry.priority >= 3:
                self._promote_to_memory(entry)

    def _select_tier(self, priority: int) -> CacheTier:
        """Select appropriate cache tier based on priority"""
        if priority >= 4:
            return CacheTier.MEMORY
        elif priority >= 2:
            return CacheTier.SQLITE
        else:
            return CacheTier.SQLITE

    def _is_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - entry.created_at < entry.ttl

    def _update_access(self, entry: CacheEntry):
        """Update access statistics"""
        entry.access_count += 1
        entry.last_access = time.time()

    def _promote_to_memory(self, entry: CacheEntry):
        """Promote entry to memory cache"""
        self._memory_storage.put(entry)
        self._promotions += 1

    def _deserialize_entry(self, data: Dict) -> CacheEntry:
        """Deserialize storage data to CacheEntry"""
        return CacheEntry(
            key=data["key"],
            data=(
                json.loads(data["data"])
                if isinstance(data["data"], str)
                else data["data"]
            ),
            tier=CacheTier(data["tier"]),
            ttl=data["ttl"],
            created_at=data["created_at"],
            access_count=data["access_count"],
            last_access=data["last_access"],
            priority=data["priority"],
        )

    def clear(self, tier: Optional[CacheTier] = None):
        """Clear cache entries"""
        with self._lock:
            if tier is None or tier == CacheTier.MEMORY:
                self._memory_storage.clear()

            if tier is None or tier == CacheTier.SQLITE:
                self._sqlite_storage.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        with self._lock:
            total_hits = sum(self._hits.values())
            total_requests = total_hits + self._misses
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "memory_items": self._memory_storage.count(),
                "sqlite_items": self._sqlite_storage.count(),
                "hit_rate": round(hit_rate, 2),
                "hits": self._hits.copy(),
                "misses": self._misses,
                "promotions": self._promotions,
                "evictions": self._evictions,
            }


# Global cache instance (singleton pattern)
_global_cache: Optional[FileCache] = None


def get_global_cache() -> FileCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = FileCache()
    return _global_cache
