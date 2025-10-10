#!/usr/bin/env python3
"""
Manager Factory
Creates and manages device manager instances
"""

from typing import Dict, Type, Optional
from src.interfaces import IDeviceManager
from ..managers import ComputerManager, MobileDeviceManager


class ManagerFactory:
    """Factory for creating device managers"""

    _managers: Dict[str, Type[IDeviceManager]] = {
        "computer": ComputerManager,
        "mobile": MobileDeviceManager,
    }

    @classmethod
    def register_manager(cls, name: str, manager_class: Type[IDeviceManager]) -> None:
        """
        Register a new manager type
        
        Args:
            name: Name to register the manager under
            manager_class: The manager class to register
        """
        if not issubclass(manager_class, IDeviceManager):
            raise ValueError(f"{manager_class.__name__} must implement IDeviceManager")
        cls._managers[name] = manager_class

    @classmethod
    def create_manager(cls, device_type: str, **kwargs) -> IDeviceManager:
        """
        Create a device manager instance
        
        Args:
            device_type: Type of device manager to create ("computer" or "mobile")
            **kwargs: Additional arguments to pass to the manager constructor
            
        Returns:
            An instance of the requested manager
            
        Raises:
            ValueError: If the requested manager type is not registered
        """
        if device_type not in cls._managers:
            raise ValueError(f"Unknown device type: {device_type}")
        return cls._managers[device_type](**kwargs)

    @classmethod
    def get_available_managers(cls) -> Dict[str, Type[IDeviceManager]]:
        """
        Get all registered manager types
        
        Returns:
            Dict mapping manager names to their classes
        """
        return cls._managers.copy()

    @classmethod
    def create_multi_manager(cls, managers: Dict[str, Dict]) -> IDeviceManager:
        """
        Create a manager that can handle multiple device types
        
        Args:
            managers: Dict mapping device types to their constructor arguments
            
        Returns:
            A multi-device manager instance
            
        Example:
            managers = {
                "computer": {"api_version": "v2"},
                "mobile": {"include_apps": True}
            }
        """
        from ..managers.multi_manager import MultiDeviceManager

        instances = {}
        for device_type, args in managers.items():
            instances[device_type] = cls.create_manager(device_type, **args)
        return MultiDeviceManager(instances)
