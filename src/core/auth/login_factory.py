#!/usr/bin/env python3
"""
Authentication Factory for jpapi
Creates appropriate authentication implementations based on configuration
"""

#!/usr/bin/env python3
"""
🧪 EXPERIMENTAL UI FEATURE - USE AT YOUR OWN RISK

This file contains experimental UI functionality that:
- May be unstable or incomplete
- Requires optional dependencies (install with: pip install jpapi[ui])
- Is not recommended for production use without thorough testing
- May have breaking changes in future versions

If you encounter issues, consider using the core CLI features instead.
"""


import os
import sys
from typing import Dict, Type, Optional
from pathlib import Path

# Using proper package structure via pip install -e .

from .login_types import AuthInterface, AuthStatus
from .login_manager import UnifiedJamfAuth
from .jamf_auth import JamfAuth


class AuthFactory:
    """Factory for creating authentication implementations"""

    _implementations: Dict[str, Type[AuthInterface]] = {
        "jamf": JamfAuth,  # New refactored implementation
        "unified": UnifiedJamfAuth,  # Legacy implementation
        "keychain": JamfAuth,  # Use refactored version for keychain
        "production": JamfAuth,  # Use refactored version for production
        "simple": UnifiedJamfAuth,  # Keep legacy for simple
        "default": JamfAuth,  # Use refactored version as default
    }

    @classmethod
    def create_auth(
        cls, auth_type: str = "default", environment: str = "dev", **kwargs
    ) -> AuthInterface:
        """
        Create authentication implementation

        Args:
            auth_type: Type of authentication ('keychain', 'production', 'simple', 'default')
            environment: Environment name ('dev', 'prod', etc.)
            **kwargs: Additional arguments for auth implementation

        Returns:
            AuthInterface: Configured authentication instance

        Raises:
            ValueError: If auth_type is not supported
        """
        if auth_type not in cls._implementations:
            raise ValueError(
                f"Unsupported auth type: {auth_type}. Available: {list(cls._implementations.keys())}"
            )

        auth_class = cls._implementations[auth_type]
        return auth_class(environment=environment, **kwargs)

    @classmethod
    def get_best_auth(cls, environment: str = "dev") -> AuthInterface:
        """
        Get the best available authentication implementation

        Args:
            environment: Environment name

        Returns:
            AuthInterface: Best available auth implementation
        """
        # Use refactored JamfAuth as default - it's cleaner and SRP-compliant
        try:
            auth = cls.create_auth("jamf", environment)
            if auth.is_configured():
                return auth
        except Exception:
            pass

        # Try keychain auth (uses JamfAuth)
        if sys.platform == "darwin":
            try:
                auth = cls.create_auth("keychain", environment)
                if auth.is_configured():
                    return auth
            except Exception:
                pass

        # Fall back to legacy UnifiedJamfAuth if needed
        try:
            auth = cls.create_auth("unified", environment)
            if auth.is_configured():
                return auth
        except Exception:
            pass

        # Return default (JamfAuth) even if not configured
        return cls.create_auth("default", environment)

    @classmethod
    def register_implementation(cls, name: str, implementation: Type[AuthInterface]):
        """
        Register a new authentication implementation

        Args:
            name: Name for the implementation
            implementation: Auth implementation class
        """
        cls._implementations[name] = implementation

    @classmethod
    def list_implementations(cls) -> list:
        """List available authentication implementations"""
        return list(cls._implementations.keys())


# Convenience function for backward compatibility
def get_auth(environment: str = "dev", auth_type: str = "default") -> AuthInterface:
    """
    Get authentication instance (convenience function)

    Args:
        environment: Environment name
        auth_type: Authentication type

    Returns:
        AuthInterface: Configured authentication instance
    """
    return AuthFactory.create_auth(auth_type, environment)


def get_best_auth(environment: str = "dev") -> AuthInterface:
    """
    Get the best available authentication for the system

    Args:
        environment: Environment name

    Returns:
        AuthInterface: Best available auth implementation
    """
    return AuthFactory.get_best_auth(environment)
