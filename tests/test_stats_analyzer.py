#!/usr/bin/env python3
"""Tests for StatsAnalyzer"""

from src.lib.utils.stats_analyzer import StatsAnalyzer


def test_init():
    """Test initialization"""
    analyzer = StatsAnalyzer()
    assert analyzer._stats_cache == {}
    assert analyzer._object_cache == {}
    assert analyzer._cache_timestamps == {}
    assert analyzer._stats_ttl == 300
    assert analyzer._objects_ttl == 1800
    assert analyzer._max_objects_per_type == 1000


def test_get_fast_stats_no_auth():
    """Test getting stats without auth"""
    analyzer = StatsAnalyzer()
    stats = analyzer.get_fast_stats()
    assert stats["source"] == "mock"
    assert stats["policies"] == 45
    assert stats["profiles"] == 23
    assert stats["scripts"] == 18
    assert stats["packages"] == 67
    assert stats["groups"] == 12
    assert stats["categories"] == 8
    assert "timestamp" in stats


def test_get_fast_objects_no_auth():
    """Test getting objects without auth"""
    analyzer = StatsAnalyzer()
    result = analyzer.get_fast_objects("policies", 5)
    assert result["source"] == "mock"
    assert len(result["objects"]) == 5
    assert result["count"] == 5
    assert result["total_available"] == 5
    assert not result["limited"]
    assert "timestamp" in result


def test_cache_invalidation():
    """Test cache invalidation"""
    analyzer = StatsAnalyzer()
    stats = analyzer.get_fast_stats()
    assert not stats["cache_hit"]

    # Second call should hit cache
    stats = analyzer.get_fast_stats()
    assert stats["cache_hit"]
