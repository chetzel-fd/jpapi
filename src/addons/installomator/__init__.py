#!/usr/bin/env python3
"""
Installomator Addon for jpapi
Simplified Installomator integration that works with existing JAMF API
"""

from .installomator_service import InstallomatorService
from .installomator_factory import InstallomatorFactory
from .policy_config import PolicyConfig, PolicyType, TriggerType

__all__ = [
    "InstallomatorService",
    "InstallomatorFactory",
    "PolicyConfig",
    "PolicyType",
    "TriggerType",
]
