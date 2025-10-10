#!/usr/bin/env python3
"""
Auth Command Interface
Handles authentication-related operations following ISP
"""

from abc import ABC, abstractmethod
from typing import Optional
from argparse import Namespace

from core.auth.login_types import AuthInterface


class AuthCommandInterface(ABC):
    """Interface for authentication-related command operations"""

    @abstractmethod
    def auth(self) -> AuthInterface:
        """Get authentication interface"""
        pass

    @abstractmethod
    def check_auth(self, args: Namespace) -> bool:
        """Check if authentication is valid"""
        pass

    @abstractmethod
    def is_production_environment(self) -> bool:
        """Check if running in production environment"""
        pass

    @abstractmethod
    def require_production_confirmation(self, operation: str) -> bool:
        """Require confirmation for production operations"""
        pass
