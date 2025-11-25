#!/usr/bin/env python3
"""
Handler Registry - SOLID OCP
Registry pattern for managing create handlers
"""

from typing import Dict, Optional, List
from .base_handler import ICreateHandler
from .category_handler import CategoryCreateHandler
from .policy_handler import PolicyCreateHandler


class HandlerRegistry:
    """Registry for managing create operation handlers"""
    
    def __init__(self):
        """Initialize registry with handlers"""
        self._handlers: Dict[str, ICreateHandler] = {}
        self._handlers_by_type: Dict[str, List[ICreateHandler]] = {}
    
    def register(self, handler: ICreateHandler, object_types: List[str]):
        """
        Register a handler for specific object types
        
        Args:
            handler: The handler instance
            object_types: List of object type strings this handler can handle
        """
        for obj_type in object_types:
            if obj_type not in self._handlers_by_type:
                self._handlers_by_type[obj_type] = []
            self._handlers_by_type[obj_type].append(handler)
            self._handlers[obj_type] = handler
    
    def get_handler(self, object_type: str) -> Optional[ICreateHandler]:
        """
        Get handler for object type
        
        Args:
            object_type: The object type to get handler for
            
        Returns:
            Handler instance or None if not found
        """
        return self._handlers.get(object_type)
    
    def find_handler(self, object_type: str) -> Optional[ICreateHandler]:
        """
        Find handler that can handle the object type
        
        Args:
            object_type: The object type to find handler for
            
        Returns:
            Handler instance or None if not found
        """
        # First try direct lookup
        handler = self.get_handler(object_type)
        if handler:
            return handler
        
        # Then try finding by can_handle
        for handler in self._handlers.values():
            if handler.can_handle(object_type):
                return handler
        
        return None


def create_handler_registry(auth, xml_converter, production_checker=None) -> HandlerRegistry:
    """
    Factory function to create and populate handler registry
    
    Args:
        auth: Authentication interface
        xml_converter: XML converter service
        production_checker: Optional production safety checker
        
    Returns:
        Configured HandlerRegistry instance
    """
    registry = HandlerRegistry()
    
    # Register handlers
    category_handler = CategoryCreateHandler(auth, xml_converter, production_checker)
    registry.register(category_handler, ["category", "cat", "cats"])
    
    policy_handler = PolicyCreateHandler(auth, xml_converter, production_checker)
    registry.register(policy_handler, ["policy", "pol", "policies"])
    
    # TODO: Register other handlers as they are created
    # profile_handler = ProfileCreateHandler(auth, xml_converter, production_checker)
    # registry.register(profile_handler, ["profile", "prof", "profiles"])
    
    return registry









