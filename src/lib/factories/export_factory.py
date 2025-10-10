#!/usr/bin/env python3
"""
Export Factory
Creates and manages export manager instances
"""

from typing import Dict, Optional
from pathlib import Path
from src.interfaces import IExportManager
from ..exports.manage_exports import get_instance_prefix


class ExportFactory:
    """Factory for creating export managers"""

    _exporters: Dict[str, callable] = {
        "default": get_instance_prefix,
    }

    @classmethod
    def register_exporter(cls, name: str, exporter_func: callable) -> None:
        """
        Register a new exporter function

        Args:
            name: Name to register the exporter under
            exporter_func: Exporter function to register
        """
        cls._exporters[name] = exporter_func

    @classmethod
    def create_exporter(cls, exporter_type: str = "default") -> Optional[callable]:
        """
        Get an exporter function

        Args:
            exporter_type: Type of exporter to get

        Returns:
            Exporter function or None if type not found
        """
        return cls._exporters.get(exporter_type)

    @classmethod
    def get_available_exporters(cls) -> Dict[str, callable]:
        """
        Get all registered exporter functions

        Returns:
            Dict mapping exporter names to their functions
        """
        return cls._exporters.copy()
