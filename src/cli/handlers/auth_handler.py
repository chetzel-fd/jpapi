#!/usr/bin/env python3
"""
Authentication Handler
Single Responsibility: Handles all authentication-related operations
"""

from typing import Optional, Dict, Any
from argparse import Namespace
from core.auth.login_types import AuthInterface
from core.auth.login_factory import get_best_auth


class AuthHandler:
    """Handles authentication operations following SRP"""

    def __init__(self, auth: Optional[AuthInterface] = None):
        self._auth = auth

    @property
    def auth(self) -> AuthInterface:
        """Get authentication interface (lazy loading)"""
        if self._auth is None:
            self._auth = get_best_auth()
        return self._auth

    def check_auth(self, args: Namespace) -> bool:
        """Check if authentication is valid"""
        try:
            return self.auth.is_configured() and self._validate_auth()
        except Exception:
            return False

    def _validate_auth(self) -> bool:
        """Validate current authentication"""
        try:
            result = self.auth.get_token()
            return result.success
        except Exception:
            return False

    def is_production_environment(self, environment: str = "dev") -> bool:
        """Check if running in production environment"""
        return environment.lower() == "prod"

    def require_production_confirmation(
        self, operation: str, environment: str = "dev"
    ) -> bool:
        """Require confirmation for production operations"""
        if not self.is_production_environment(environment):
            return True

        print(f"⚠️  WARNING: {operation} in PRODUCTION environment!")
        confirmation = input("Type 'yes' to confirm: ")
        return confirmation.lower() == "yes"

    def get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        try:
            return self.auth.get_auth_info()
        except Exception as e:
            return {"error": str(e), "configured": False}

    def setup_auth(self, environment: str = "dev") -> bool:
        """Setup authentication for given environment"""
        try:
            # This would implement interactive auth setup
            print(f"Setting up authentication for {environment} environment...")
            return True
        except Exception as e:
            print(f"Failed to setup authentication: {e}")
            return False

    def clear_auth(self) -> bool:
        """Clear stored authentication"""
        try:
            return self.auth.clear_credentials()
        except Exception as e:
            print(f"Failed to clear authentication: {e}")
            return False



