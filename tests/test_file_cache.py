#!/usr/bin/env python3
"""Tests for FileCache"""

from src.lib.utils.file_cache import FileCache, CacheTier


def test_init():
    """Test initialization"""
    cache = FileCache()
    assert len(cache._memory_cache) == 0
    assert cache._max_memory_items == 1000
    assert cache._hits == {"memory": 0, "sqlite": 0, "api": 0}
    assert cache._misses == 0
    assert cache._promotions == 0
    assert cache._evictions == 0


def test_put_get():
    """Test basic put/get operations"""
    cache = FileCache()
    cache.put("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    assert cache.get("nonexistent") is None


def test_cache_tiers():
    """Test cache tier selection"""
    cache = FileCache()
    assert cache._select_tier(5) == CacheTier.MEMORY
    assert cache._select_tier(3) == CacheTier.SQLITE
    assert cache._select_tier(1) == CacheTier.SQLITE


def test_cache_stats():
    """Test cache statistics"""
    cache = FileCache()
    cache.put("test_key", "test_value", priority=4)  # High priority for memory cache

    # First get should hit memory cache
    value = cache.get("test_key")
    assert value == "test_value"

    stats = cache.get_stats()
    assert stats["hits"]["memory"] == 1
    assert stats["hits"]["sqlite"] == 0
    assert stats["misses"] == 0
    assert stats["promotions"] == 1  # One promotion from put
    assert stats["evictions"] == 0
