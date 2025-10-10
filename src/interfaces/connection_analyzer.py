#!/usr/bin/env python3
"""
Connection Analyzer Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IConnectionAnalyzer(ABC):
    """Interface for connection analysis"""

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze connections in data"""
        pass

    @abstractmethod
    def get_connections(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all connections from data"""
        pass

    @abstractmethod
    def find_relationships(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find relationships in data"""
        pass
