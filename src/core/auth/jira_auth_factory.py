#!/usr/bin/env python3
"""
Jira Authentication Factory
Creates Jira authentication instances similar to JPAPI's auth factory
"""

from typing import Dict, Type
from .jira_auth import JiraAuth
from .jira_auth_types import JiraAuthInterface


class JiraAuthFactory:
    """Factory for creating Jira authentication instances"""

    _implementations: Dict[str, Type[JiraAuthInterface]] = {
        "default": JiraAuth,
        "jira": JiraAuth,
    }

    @classmethod
    def create_auth(
        cls,
        environment: str = "dev",
        auth_type: str = "default",
        backend: str = "keychain",
    ) -> JiraAuthInterface:
        """
        Create a Jira authentication instance

        Args:
            environment: Environment name (dev, staging, prod)
            auth_type: Authentication type (default, jira)
            backend: Storage backend (keychain, file)

        Returns:
            JiraAuthInterface instance
        """
        if auth_type not in cls._implementations:
            raise ValueError(
                f"Unknown auth type: {auth_type}. Available types: {list(cls._implementations.keys())}"
            )

        auth_class = cls._implementations[auth_type]
        return auth_class(environment=environment, backend=backend)

    @classmethod
    def register_auth_type(cls, name: str, auth_class: Type[JiraAuthInterface]):
        """
        Register a new authentication type

        Args:
            name: Name of the auth type
            auth_class: Authentication class to register
        """
        cls._implementations[name] = auth_class

    @classmethod
    def get_available_types(cls) -> list:
        """Get list of available authentication types"""
        return list(cls._implementations.keys())


def get_jira_auth(
    environment: str = "dev", auth_type: str = "default", backend: str = "keychain"
) -> JiraAuthInterface:
    """
    Convenience function to get a Jira authentication instance

    Args:
        environment: Environment name (dev, staging, prod)
        auth_type: Authentication type (default, jira)
        backend: Storage backend (keychain, file)

    Returns:
        JiraAuthInterface instance
    """
    return JiraAuthFactory.create_auth(environment, auth_type, backend)

