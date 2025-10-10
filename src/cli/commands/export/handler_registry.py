#!/usr/bin/env python3
"""
Export Handler Registry for jpapi CLI
Centralized registry for managing export handlers and their aliases
"""

from typing import Dict, List, Type, Any, Optional
from .export_base import ExportBase


class ExportHandlerRegistry:
    """Centralized registry for export handlers"""

    def __init__(self):
        self._handlers: Dict[str, Type[ExportBase]] = {}
        self._aliases: Dict[str, str] = {}
        self._handler_configs: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        export_type: str,
        handler_class: Type[ExportBase],
        aliases: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a handler for an export type"""
        self._handlers[export_type] = handler_class
        if aliases:
            for alias in aliases:
                if alias in self._aliases:
                    raise ValueError(f"Alias '{alias}' is already registered")
                self._aliases[alias] = export_type
        if config:
            self._handler_configs[export_type] = config

    def get_handler(self, export_type: str, auth, *args, **kwargs) -> ExportBase:
        """Get handler instance for export type"""
        actual_type = self._aliases.get(export_type, export_type)
        handler_class = self._handlers.get(actual_type)

        if not handler_class:
            available_types = list(self._handlers.keys()) + list(self._aliases.keys())
            raise ValueError(
                f"Unknown export type: '{export_type}'. "
                f"Available types: {', '.join(sorted(available_types))}"
            )

        # Get handler-specific configuration
        # TODO: Pass handler-specific configuration to handler
        # handler_config = self._handler_configs.get(actual_type, {})

        # Create handler instance with appropriate arguments
        if actual_type in ["mobile", "computers"]:
            # Device handlers need device_type parameter
            device_type = "mobile" if actual_type == "mobile" else "computers"
            return handler_class(auth, device_type)
        else:
            # Other handlers just need auth
            return handler_class(auth, actual_type)

    def has_handler(self, export_type: str) -> bool:
        """Check if handler exists for export type"""
        actual_type = self._aliases.get(export_type, export_type)
        return actual_type in self._handlers

    def is_alias_conflict(self, alias: str) -> bool:
        """Check if alias conflicts with existing registration"""
        return alias in self._aliases

    def get_available_types(self) -> List[str]:
        """Get list of all available export types"""
        return sorted(list(self._handlers.keys()))

    def get_aliases_for_type(self, export_type: str) -> List[str]:
        """Get all aliases for a specific export type"""
        return [
            alias
            for alias, type_name in self._aliases.items()
            if type_name == export_type
        ]

    def get_handler_info(self, export_type: str) -> Dict[str, Any]:
        """Get information about a handler"""
        actual_type = self._aliases.get(export_type, export_type)
        handler_class = self._handlers.get(actual_type)

        if not handler_class:
            return {}

        return {
            "type": actual_type,
            "handler_class": handler_class.__name__,
            "aliases": self.get_aliases_for_type(actual_type),
            "config": self._handler_configs.get(actual_type, {}),
        }
