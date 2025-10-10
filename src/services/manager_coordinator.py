#!/usr/bin/env python3
"""
Manager Coordinator - SOLID SRP compliance
Handles manager creation and coordination
"""
from typing import Optional, List
from abc import ABC, abstractmethod


class ManagerCoordinatorInterface(ABC):
    """Interface for manager coordination - SOLID DIP"""

    @abstractmethod
    def create_manager(self, object_type: str):
        """Create manager for object type"""
        pass

    @abstractmethod
    def get_available_types(self) -> List[str]:
        """Get available object types"""
        pass


class ManagerCoordinator(ManagerCoordinatorInterface):
    """Manager coordinator implementation - SOLID SRP"""

    def __init__(self, factory):
        self.factory = factory
        self.managers = {}

    def create_manager(self, object_type: str):
        """Create manager for object type - SOLID DIP"""
        if not self.factory:
            return None

        try:
            # Create manager using factory
            manager = self.factory.create_manager(object_type)

            # Store manager for potential reuse
            self.managers[object_type] = manager

            return manager
        except Exception as e:
            print(f"Error creating manager for {object_type}: {e}")
            return None

    def get_available_types(self) -> List[str]:
        """Get available object types - SOLID DIP"""
        if not self.factory:
            return ["demo-type"]

        try:
            return self.factory.get_available_types()
        except Exception as e:
            print(f"Error getting available types: {e}")
            return ["demo-type"]

    def get_manager(self, object_type: str):
        """Get existing manager for object type"""
        return self.managers.get(object_type)

    def clear_managers(self):
        """Clear all managers"""
        self.managers.clear()
