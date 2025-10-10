#!/usr/bin/env python3
"""
Device Manager Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IDeviceManager(ABC):
    """Interface for device management"""

    @abstractmethod
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices"""
        pass

    @abstractmethod
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get specific device by ID"""
        pass

    @abstractmethod
    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new device"""
        pass

    @abstractmethod
    def update_device(
        self, device_id: str, device_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a device"""
        pass

    @abstractmethod
    def delete_device(self, device_id: str) -> bool:
        """Delete a device"""
        pass
