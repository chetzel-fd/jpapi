#!/usr/bin/env python3
"""Tests for FilterManager"""

from src.lib.utils.filter_utils import FilterManager, FilterType, FilterField


def test_init():
    """Test initialization"""
    filter_mgr = FilterManager()
    assert filter_mgr.filter_type == FilterType.WILDCARD
    assert filter_mgr.compiled_patterns == {}


def test_wildcard_matching():
    """Test wildcard pattern matching"""
    filter_mgr = FilterManager(FilterType.WILDCARD)
    assert filter_mgr.matches("test123", "test*")
    assert filter_mgr.matches("testing", "test*")
    assert not filter_mgr.matches("other", "test*")


def test_regex_matching():
    """Test regex pattern matching"""
    filter_mgr = FilterManager(FilterType.REGEX)
    assert filter_mgr.matches("test123", r"^test\d+$")
    assert not filter_mgr.matches("testabc", r"^test\d+$")


def test_exact_matching():
    """Test exact pattern matching"""
    filter_mgr = FilterManager(FilterType.EXACT)
    assert filter_mgr.matches("test", "test")
    assert not filter_mgr.matches("test123", "test")


def test_contains_matching():
    """Test contains pattern matching"""
    filter_mgr = FilterManager(FilterType.CONTAINS)
    assert filter_mgr.matches("test123", "test")
    assert filter_mgr.matches("123test456", "test")
    assert not filter_mgr.matches("other", "test")


def test_filter_objects():
    """Test filtering objects"""
    test_objects = [
        {"name": "Test Policy 1", "enabled": True, "category": "Security"},
        {"name": "Another Policy", "enabled": False, "category": "General"},
        {"name": "Test Policy 2", "enabled": True, "category": "Security"},
    ]

    filter_mgr = FilterManager()
    filtered = filter_mgr.filter_objects(test_objects, FilterField.NAME, "Test*")
    assert len(filtered) == 2
    assert all("Test" in obj["name"] for obj in filtered)

    filtered = filter_mgr.filter_objects(test_objects, FilterField.CATEGORY, "Security")
    assert len(filtered) == 2
    assert all(obj["category"] == "Security" for obj in filtered)
