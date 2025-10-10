#!/usr/bin/env python3
"""
Installomator Policy Configuration
Defines policy types and configurations for Installomator integration
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class PolicyType(Enum):
    """Types of Installomator policies"""

    INSTALL = "install"
    UPDATE = "update"
    DAILY_UPDATE = "daily_update"
    LATEST_VERSION = "latest_version"


class TriggerType(Enum):
    """Types of policy triggers"""

    EVENT = "EVENT"
    STARTUP = "STARTUP"
    LOGIN = "LOGIN"
    CHECKIN = "CHECKIN"
    ENROLLMENT = "ENROLLMENT_COMPLETE"


@dataclass
class PolicyConfig:
    """Configuration for an Installomator policy"""

    app_name: str
    label: str
    policy_name: str
    policy_type: PolicyType
    trigger: TriggerType
    category: str = "IT"
    description: str = ""
    scope_groups: List[str] = None
    exclusions: List[str] = None
    frequency: str = "Ongoing"
    retry_attempts: int = -1
    notify_on_failure: bool = False

    def __post_init__(self):
        if self.scope_groups is None:
            self.scope_groups = []
        if self.exclusions is None:
            self.exclusions = []

    def to_jamf_policy(self) -> Dict[str, Any]:
        """Convert to JAMF policy format"""
        return {
            "general": {
                "name": self.policy_name,
                "enabled": True,
                "trigger": self.trigger.value,
                "frequency": self.frequency,
                "retry_attempts": self.retry_attempts,
                "notify_on_each_failed_retry": self.notify_on_failure,
                "category": {"name": self.category},
                "description": self.description,
            },
            "scope": {
                "all_computers": len(self.scope_groups) == 0,
                "computer_groups": [{"name": group} for group in self.scope_groups],
                "exclusions": {
                    "computer_groups": [{"name": group} for group in self.exclusions]
                },
            },
            "scripts": [
                {
                    "id": 196,  # Installomator script ID
                    "priority": "Before",
                    "parameter4": self.label,
                    "parameter5": self.app_name,
                }
            ],
        }
