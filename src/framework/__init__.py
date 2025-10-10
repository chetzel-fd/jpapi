#!/usr/bin/env python3
"""
JPAPI Framework - Core application framework
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class AppMetadata:
    """Application metadata"""

    id: str
    name: str
    description: str
    version: str
    category: str
    icon: str
    entry_point: callable
    permissions: list
    multi_tenant: bool = False
    real_time: bool = False


@dataclass
class TenantConfig:
    """Tenant configuration"""

    id: str
    name: str
    config: Dict[str, Any]


class JPAPIApplication:
    """Base application class"""

    def __init__(self, framework=None, tenant=None):
        self.framework = framework
        self.tenant = tenant
        self.logger = self._get_logger()

    def _get_logger(self):
        """Get logger instance"""
        import logging

        return logging.getLogger(self.__class__.__name__)

    def get_metadata(self) -> AppMetadata:
        """Get application metadata - must be implemented by subclasses"""
        raise NotImplementedError

    def initialize(self) -> bool:
        """Initialize application - must be implemented by subclasses"""
        raise NotImplementedError

    def launch(self, **kwargs) -> Any:
        """Launch application - must be implemented by subclasses"""
        raise NotImplementedError


def create_framework():
    """Create framework instance"""
    return type("Framework", (), {"tenants": {}, "apps": {}, "logger": None})()
