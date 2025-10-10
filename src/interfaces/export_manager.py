#!/usr/bin/env python3
"""
Export Manager Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IExportManager(ABC):
    """Interface for export management"""

    @abstractmethod
    def export_data(self, data: List[Dict[str, Any]], format: str) -> str:
        """Export data in specified format"""
        pass

    @abstractmethod
    def get_export_formats(self) -> List[str]:
        """Get available export formats"""
        pass

    @abstractmethod
    def validate_export_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate data for export"""
        pass
