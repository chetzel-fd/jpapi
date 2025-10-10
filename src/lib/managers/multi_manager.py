#!/usr/bin/env python3
"""
Multi-Device Manager
Manages multiple device types through a single interface
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from interfaces import IDeviceManager


class MultiDeviceManager(IDeviceManager):
    """Manages multiple device types"""

    def __init__(self, managers: Dict[str, IDeviceManager]):
        """
        Initialize with device type managers
        
        Args:
            managers: Dict mapping device types to their managers
        """
        self._managers = managers
        self._default_type = next(iter(managers.keys()))

    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Get device info using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].get_device_info(device_id)

    def get_device_policies(self, device_id: str) -> List[Dict[str, Any]]:
        """Get device policies using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].get_device_policies(device_id)

    def get_device_profiles(self, device_id: str) -> List[Dict[str, Any]]:
        """Get device profiles using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].get_device_profiles(device_id)

    def get_device_groups(self, device_id: str) -> List[Dict[str, Any]]:
        """Get device groups using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].get_device_groups(device_id)

    def update_device_inventory(self, device_id: str) -> bool:
        """Update device inventory using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].update_device_inventory(device_id)

    def send_command(self, device_id: str, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send command using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].send_command(device_id, command, params)

    def get_command_status(self, device_id: str, command_uuid: str) -> Dict[str, Any]:
        """Get command status using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].get_command_status(device_id, command_uuid)

    def get_device_logs(self, device_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get device logs using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].get_device_logs(device_id, start_date, end_date)

    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status using appropriate manager"""
        device_type = self._detect_device_type(device_id)
        return self._managers[device_type].get_device_status(device_id)

    def _detect_device_type(self, device_id: str) -> str:
        """
        Detect device type from ID
        
        Args:
            device_id: The device ID to check
            
        Returns:
            Device type string
            
        Note:
            This is a simple implementation. In practice, you might want to:
            1. Cache device type lookups
            2. Query the API to determine device type
            3. Use a more sophisticated detection method
        """
        # Try each manager to find device
        for device_type, manager in self._managers.items():
            try:
                if manager.get_device_info(device_id):
                    return device_type
            except:
                continue

        # Fall back to default type
        return self._default_type
