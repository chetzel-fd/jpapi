#!/usr/bin/env python3
"""
Cache Types
Common types used by cache implementations
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CacheTier(Enum):
    """Cache storage tiers"""

    MEMORY = "memory"  # Fastest, limited size
    SQLITE = "sqlite"  # Persistent, medium speed
    API = "api"  # Source of truth, slowest


@dataclass
class CacheEntry:
    """Unified cache entry"""

    key: str
    data: Any
    tier: CacheTier
    ttl: int
    created_at: float
    access_count: int = 0
    last_access: float = 0
    priority: int = 1  # 1=low, 5=high


