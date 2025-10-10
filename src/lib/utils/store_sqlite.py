#!/usr/bin/env python3
"""
SQLite Cache Storage
Implements persistent cache storage using SQLite
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional
from src.interfaces.cache_storage import ICacheStorage
from .cache_types import CacheEntry


class SQLiteStorage(ICacheStorage):
    """SQLite-based cache storage implementation"""

    def __init__(self, db_path: str):
        """
        Initialize SQLite storage

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries
                (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    ttl INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_access REAL NOT NULL,
                    priority INTEGER DEFAULT 1
                )
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_created_at ON cache_entries(created_at)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_last_access ON cache_entries(last_access)
            """
            )

    def get(self, key: str) -> Optional[Dict]:
        """
        Get entry from SQLite storage

        Args:
            key: The key to retrieve

        Returns:
            Dict containing entry data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM cache_entries WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return {
                    "key": row[0],
                    "data": row[1],
                    "tier": row[2],
                    "ttl": row[3],
                    "created_at": row[4],
                    "access_count": row[5],
                    "last_access": row[6],
                    "priority": row[7],
                }
        return None

    def put(self, entry: CacheEntry) -> None:
        """Store entry in SQLite storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache_entries
                (
                    key, data, tier, ttl, created_at,
                    access_count, last_access, priority
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry.key,
                    json.dumps(entry.data),
                    entry.tier.value,
                    entry.ttl,
                    entry.created_at,
                    entry.access_count,
                    entry.last_access,
                    entry.priority,
                ),
            )

    def remove(self, key: str) -> None:
        """Remove entry from SQLite storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))

    def clear(self) -> None:
        """Clear all entries from SQLite storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache_entries")

    def count(self) -> int:
        """Get count of entries in SQLite storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
            return cursor.fetchone()[0]
