#!/usr/bin/env python3
"""
Cache Storage Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ICacheStorage(ABC):
    """Interface for cache storage"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache"""
        pass
