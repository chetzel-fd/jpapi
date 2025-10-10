#!/usr/bin/env python3
"""
Stats Storage Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IStatsStorage(ABC):
    """Interface for statistics storage"""

    @abstractmethod
    def store(self, key: str, stats: Dict[str, Any]) -> None:
        """Store statistics"""
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get statistics"""
        pass

    @abstractmethod
    def list_keys(self) -> List[str]:
        """List all stored statistics keys"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all statistics"""
        pass
