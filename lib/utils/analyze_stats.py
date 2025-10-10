#!/usr/bin/env python3
"""
SIMPLE STATS ENGINE
Fast object counting and basic statistics for immediate dashboard feedback
Provides instant results while full relationship analysis runs in background
"""
import time
import threading
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StatsAnalyzer:
    """
    Lightweight statistics engine for immediate dashboard feedback

    Features:
    - Ultra-fast object counts (< 100ms response time)
    - Cached results with smart invalidation
    - Background refresh without blocking UI
    - Fallback to mock data when JAMF is unavailable
    - Memory-efficient storage
    """

    def __init__(
        self,
        jamf_client=None,
        stats_storage=None,
        stats_ttl: int = 300,  # 5 minutes for stats
        objects_ttl: int = 1800,  # 30 minutes for object lists
        max_objects_per_type: int = 1000,  # Limit for memory efficiency
    ):
        """
        Initialize StatsAnalyzer with optional dependencies

        Args:
            jamf_client: Optional JAMF API client implementation
            stats_storage: Optional stats storage implementation
            stats_ttl: Time-to-live for stats cache in seconds
            objects_ttl: Time-to-live for objects cache in seconds
            max_objects_per_type: Maximum number of objects to store per type
        """
        from .store_stats_memory import MemoryStatsStorage

        # Initialize dependencies
        self.auth = jamf_client
        self._storage = stats_storage or MemoryStatsStorage()

        # Cache configuration
        self._stats_ttl = stats_ttl
        self._objects_ttl = objects_ttl
        self._max_objects_per_type = max_objects_per_type
        self._cache_timestamps: Dict[str, float] = {}

        # Background refresh
        self._refresh_lock = threading.Lock()
        self._refresh_thread = None
        self._stop_refresh = False

        # Performance tracking
        self._request_count = 0
        self._cache_hits = 0
        self._api_calls = 0

        logger.info("🚀 Simple Stats Engine initialized")
        logger.info(f"   ⚡ Stats TTL: {self._stats_ttl}s")
        logger.info(f"   📦 Objects TTL: {self._objects_ttl}s")

    def get_fast_stats(self) -> Dict[str, Any]:
        """Get object counts as fast as possible"""
        self._request_count += 1

        # Check cache first
        cache_key = "fast_stats"
        cached_stats = self._storage.get_stats(cache_key)
        if cached_stats and self._is_cache_valid(cache_key, self._stats_ttl):
            self._cache_hits += 1
            stats = cached_stats.copy()
            stats["cache_hit"] = True
            stats["response_time_ms"] = 0  # Cached response
            return stats

        start_time = time.time()

        # Try to get fresh data
        try:
            stats = self._fetch_fresh_stats()

            # Cache the result
            self._storage.store_stats(cache_key, stats)
            self._cache_timestamps[cache_key] = time.time()

            # Start background refresh if not already running
            self._start_background_refresh()

        except Exception as e:
            logger.warning(f"Failed to fetch fresh stats: {e}")

            # Try to return stale cache data
            if cached_stats:
                stats = cached_stats.copy()
                stats["cache_hit"] = True
                stats["stale"] = True
                stats["error"] = str(e)
                return stats

            # Fallback to mock data
            stats = self._get_mock_stats()
            stats["error"] = str(e)

        response_time = (time.time() - start_time) * 1000
        stats["response_time_ms"] = round(response_time, 2)
        stats["cache_hit"] = False

        return stats

    def get_fast_objects(self, object_type: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get object list as fast as possible

        Args:
            object_type: Object type to fetch
            limit: Max objects to return
        """
        self._request_count += 1

        # Limit for memory efficiency
        limit = min(limit, self._max_objects_per_type)

        # Check cache first
        cache_key = f"objects_{object_type}_{limit}"
        cached_objects = self._storage.get_objects(cache_key)
        if cached_objects and self._is_cache_valid(cache_key, self._objects_ttl):
            self._cache_hits += 1
            result = cached_objects.copy()
            result["cache_hit"] = True
            result["response_time_ms"] = 0
            return result

        start_time = time.time()

        try:
            result = self._fetch_fresh_objects(object_type, limit)

            # Cache the result
            self._storage.store_objects(cache_key, result)
            self._cache_timestamps[cache_key] = time.time()

        except Exception as e:
            logger.warning(f"Failed to fetch {object_type}: {e}")

            # Try stale cache
            if cached_objects:
                result = cached_objects.copy()
                result["cache_hit"] = True
                result["stale"] = True
                result["error"] = str(e)
                return result

            # Fallback to mock data
            result = self._get_mock_objects(object_type, limit)
            result["error"] = str(e)

        response_time = (time.time() - start_time) * 1000
        result["response_time_ms"] = round(response_time, 2)
        result["cache_hit"] = False

        return result

    def _fetch_fresh_stats(self) -> Dict[str, Any]:
        """Fetch fresh statistics from JAMF API"""
        if not self.auth:
            return self._get_mock_stats()

        self._api_calls += 1

        stats = {
            "policies": 0,
            "profiles": 0,
            "scripts": 0,
            "packages": 0,
            "groups": 0,
            "categories": 0,
            "timestamp": datetime.now().isoformat(),
            "source": "live",
        }

        # Fast count endpoints - just get the list length
        endpoints = {
            "policies": "/JSSResource/policies",
            "profiles": "/JSSResource/osxconfigurationprofiles",  # noqa
            "scripts": "/JSSResource/scripts",
            "packages": "/JSSResource/packages",
            "groups": "/JSSResource/computergroups",
            "categories": "/JSSResource/categories",
        }

        for object_type, endpoint in endpoints.items():
            try:
                response = self.auth.make_api_call(endpoint)
                if response and isinstance(response, dict):
                    # Handle different response formats
                    if object_type in response:
                        items = response[object_type]
                        stats[object_type] = (
                            len(items) if isinstance(items, list) else 0
                        )
                    else:
                        # Some endpoints return direct lists
                        stats[object_type] = (
                            len(response) if isinstance(response, list) else 0
                        )

            except Exception as e:
                logger.warning(f"Failed to count {object_type}: {e}")
                # Keep the 0 value for failed counts

        return stats

    def _fetch_fresh_objects(self, object_type: str, limit: int) -> Dict[str, Any]:
        """Fetch fresh object list from JAMF API"""
        if not self.auth:
            return self._get_mock_objects(object_type, limit)

        self._api_calls += 1

        # API endpoints for each type
        endpoint_map = {
            "policies": "/JSSResource/policies",
            "profiles": "/JSSResource/osxconfigurationprofiles",  # noqa
            "scripts": "/JSSResource/scripts",
            "packages": "/JSSResource/packages",
            "groups": "/JSSResource/computergroups",
            "categories": "/JSSResource/categories",
        }

        endpoint = endpoint_map.get(object_type)
        if not endpoint:
            raise ValueError(f"Unknown object type: {object_type}")

        response = self.auth.make_api_call(endpoint)
        if not response:
            raise ValueError("No response from API")

        # Extract objects
        objects = []
        if object_type in response:
            raw_objects = response[object_type]
        elif isinstance(response, list):
            raw_objects = response
        else:
            raw_objects = []

        # Normalize and limit objects
        for obj in raw_objects[:limit]:
            if isinstance(obj, dict):
                objects.append(
                    {
                        "id": obj.get("id", "unknown"),
                        "name": obj.get("name", "Unknown"),
                        "description": obj.get("description", "")[
                            :100
                        ],  # Truncate for memory
                    }
                )

        return {
            "objects": objects,
            "count": len(objects),
            "total_available": len(raw_objects),
            "limited": len(objects) < len(raw_objects),
            "source": "live",
            "timestamp": datetime.now().isoformat(),
        }

    def _get_mock_stats(self) -> Dict[str, Any]:
        """Get mock statistics for testing/fallback"""
        return {
            "policies": 45,
            "profiles": 23,
            "scripts": 18,
            "packages": 67,
            "groups": 12,
            "categories": 8,
            "timestamp": datetime.now().isoformat(),
            "source": "mock",
        }

    def _get_mock_objects(self, object_type: str, limit: int) -> Dict[str, Any]:
        """Get mock objects for testing/fallback"""
        objects = []
        for i in range(min(limit, 10)):  # Max 10 mock objects
            objects.append(
                {
                    "id": i + 1,
                    "name": f"Mock {object_type.title()} {i + 1}",
                    "description": f"Mock {object_type} for testing purposes",
                }
            )

        return {
            "objects": objects,
            "count": len(objects),
            "total_available": len(objects),
            "limited": False,
            "source": "mock",
            "timestamp": datetime.now().isoformat(),
        }

    def _is_cache_valid(self, cache_key: str, ttl: int) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache_timestamps:
            return False

        age = time.time() - self._cache_timestamps[cache_key]
        return age < ttl

    def _start_background_refresh(self):
        """Start background cache refresh if not already running"""
        with self._refresh_lock:
            if self._refresh_thread and self._refresh_thread.is_alive():
                return  # Already running

            self._stop_refresh = False
            self._refresh_thread = threading.Thread(target=self._background_refresh)
            self._refresh_thread.daemon = True
            self._refresh_thread.start()

    def _background_refresh(self):
        """Background thread to refresh cache periodically"""
        logger.info("🔄 Starting background cache refresh")

        while not self._stop_refresh:
            try:
                time.sleep(60)  # Check every minute

                if self._stop_refresh:
                    break

                # Refresh stats if they're getting stale
                stats_age = time.time() - self._cache_timestamps.get("fast_stats", 0)
                if stats_age > self._stats_ttl * 0.8:  # Refresh at 80% of TTL
                    try:
                        fresh_stats = self._fetch_fresh_stats()
                        self._stats_cache["fast_stats"] = fresh_stats
                        self._cache_timestamps["fast_stats"] = time.time()
                        logger.debug("🔄 Background stats refresh completed")
                    except Exception as e:
                        logger.warning(f"Background stats refresh failed: {e}")

                # Clean up old cache entries
                self._cleanup_old_cache()

            except Exception as e:
                logger.error(f"Background refresh error: {e}")

        logger.info("🛑 Background cache refresh stopped")

    def _cleanup_old_cache(self):
        """Remove old cache entries to prevent memory bloat"""
        current_time = time.time()
        # Keep for 2x TTL
        max_age = max(self._stats_ttl, self._objects_ttl) * 2

        old_keys = []
        for key, timestamp in self._cache_timestamps.items():
            if current_time - timestamp > max_age:
                old_keys.append(key)

        for key in old_keys:
            self._cache_timestamps.pop(key, None)

        if old_keys:
            logger.debug(f"🧹 Cleaned up {len(old_keys)} old cache entries")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total_requests = self._request_count
        cache_hit_rate = (
            (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "total_requests": total_requests,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "api_calls": self._api_calls,
            "background_refresh_active": self._refresh_thread
            and self._refresh_thread.is_alive(),
        }

    def clear_cache(self):
        """Clear all cached data"""
        with self._refresh_lock:
            self._storage.clear()
            self._cache_timestamps.clear()
            logger.info("🧹 Simple stats cache cleared")

    def stop(self):
        """Stop background processes"""
        self._stop_refresh = True
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)
        logger.info("🛑 Simple stats engine stopped")
