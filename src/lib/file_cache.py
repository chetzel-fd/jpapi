#!/usr/bin/env python3
"""
JAMF File Cache
Saves JAMF data to files to avoid repeated API calls
"""

import json
import sqlite3
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class StorageType(Enum):
    """Where to store the data"""

    MEMORY = "memory"  # Fastest but temporary
    SQLITE = "sqlite"  # Saved to database
    API = "api"  # Get from JAMF API


@dataclass
class CachedFile:
    """A saved file"""

    name: str
    data: Any
    storage: StorageType
    expires_in: int
    priority: int = 1  # 1=low, 5=high
    last_used: float = time.time()
    last_updated: float = time.time()


class FileCache:
    """
    Saves JAMF data to avoid repeated API calls

    Features:
    - Saves data in memory for speed
    - Backs up to database for persistence
    - Falls back to API when needed
    - Cleans up old unused data
    """

    def __init__(self, cache_dir: str = "tmp/cache/files"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Setup storage
        self._memory_cache: Dict[str, Any] = {}
        self._db_path = self.cache_dir / "cache.db"
        self._setup_database()

        # Settings
        self._max_memory_items = 1000
        self._cleanup_interval = 3600  # 1 hour
        self._default_ttl = 86400  # 24 hours

        # Start cleanup
        self._start_cleanup_thread()

    def save(
        self,
        key: str,
        data: Any,
        expires_in: int = None,
        priority: int = 1,
        storage: StorageType = StorageType.MEMORY,
    ) -> None:
        """
        Save data to cache

        Args:
            key: Name to save under
            data: Data to save
            expires_in: Seconds until expired (default 24 hours)
            priority: Importance (1-5, higher = keep longer)
            storage: Where to save (memory, database, or API)
        """
        expires_in = expires_in or self._default_ttl

        entry = CachedFile(
            name=key,
            data=data,
            storage=storage,
            expires_in=expires_in,
            priority=max(1, min(priority, 5)),
            last_used=time.time(),
            last_updated=time.time(),
        )

        # Save to memory
        if storage == StorageType.MEMORY:
            self._memory_cache[key] = entry

            # Clean memory if too full
            if len(self._memory_cache) > self._max_memory_items:
                self._clean_memory_cache()

        # Save to database
        elif storage == StorageType.SQLITE:
            self._save_to_db(entry)

    def get(self, key: str, default: Any = None, max_age: int = None) -> Any:
        """
        Get data from cache

        Args:
            key: Name to look up
            default: What to return if not found
            max_age: Maximum age in seconds

        Returns:
            The data if found and not expired, else default
        """
        # Try memory first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if not self._is_expired(entry, max_age):
                entry.last_used = time.time()
                return entry.data

        # Try database next
        db_entry = self._get_from_db(key)
        if db_entry and not self._is_expired(db_entry, max_age):
            # Cache in memory for next time
            self._memory_cache[key] = db_entry
            return db_entry.data

        return default

    def delete(self, key: str) -> None:
        """Delete from all storage"""
        if key in self._memory_cache:
            del self._memory_cache[key]

        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))

    def clear(self) -> None:
        """Clear all storage"""
        self._memory_cache.clear()

        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM cache")

    def _setup_database(self) -> None:
        """Create database tables"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data TEXT,
                    storage TEXT,
                    expires_in INTEGER,
                    priority INTEGER,
                    last_used REAL,
                    last_updated REAL
                )
            """
            )

    def _save_to_db(self, entry: CachedFile) -> None:
        """Save entry to database"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache
                (key, data, storage, expires_in, priority, last_used, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.name,
                    json.dumps(entry.data),
                    entry.storage.value,
                    entry.expires_in,
                    entry.priority,
                    entry.last_used,
                    entry.last_updated,
                ),
            )

    def _get_from_db(self, key: str) -> Optional[CachedFile]:
        """Get entry from database"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute("SELECT * FROM cache WHERE key = ?", (key,))
            row = cursor.fetchone()

            if row:
                return CachedFile(
                    name=row[0],
                    data=json.loads(row[1]),
                    storage=StorageType(row[2]),
                    expires_in=row[3],
                    priority=row[4],
                    last_used=row[5],
                    last_updated=row[6],
                )

        return None

    def _is_expired(self, entry: CachedFile, max_age: Optional[int] = None) -> bool:
        """Check if entry is expired"""
        now = time.time()
        age = now - entry.last_updated

        # Check custom max age
        if max_age and age > max_age:
            return True

        # Check entry TTL
        return age > entry.expires_in

    def _clean_memory_cache(self) -> None:
        """Clean old items from memory"""
        if len(self._memory_cache) <= self._max_memory_items:
            return

        # Sort by priority and last used
        sorted_entries = sorted(
            self._memory_cache.items(), key=lambda x: (x[1].priority, x[1].last_used)
        )

        # Remove oldest, lowest priority items
        to_remove = len(self._memory_cache) - self._max_memory_items
        for key, _ in sorted_entries[:to_remove]:
            del self._memory_cache[key]

    def _start_cleanup_thread(self) -> None:
        """Start background cleanup"""

        def cleanup():
            while True:
                try:
                    self._clean_memory_cache()
                    time.sleep(self._cleanup_interval)
                except Exception as e:
                    print(f"Cache cleanup error: {e}")
                    time.sleep(300)  # Wait 5 min on error

        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
