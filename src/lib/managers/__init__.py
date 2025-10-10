"""
JAMF Pro API Managers
Implements managers for various JAMF Pro operations
"""

from .computer_manager import ComputerManager
from .mobile_device_manager import MobileDeviceManager

__all__ = [
    "ComputerManager",
    "MobileDeviceManager",
]
