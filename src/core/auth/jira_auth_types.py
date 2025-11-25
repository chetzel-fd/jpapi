#!/usr/bin/env python3
"""
Jira Authentication Types and Interfaces
Defines the core data structures and interfaces for Jira authentication
Similar to JPAPI's login_types.py but adapted for Jira
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class JiraAuthStatus(Enum):
    """Jira authentication status enumeration"""

    NOT_CONFIGURED = "not_configured"
    AUTHENTICATED = "authenticated"
    INVALID = "invalid"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class JiraAuthCredentials:
    """Jira authentication credentials data structure"""

    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    api_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires: Optional[str] = None
    auth_method: str = "basic"  # "basic", "oauth", "api_token"


@dataclass
class JiraAuthResult:
    """Jira authentication result data structure"""

    success: bool
    status: JiraAuthStatus
    message: str
    token: Optional[str] = None
    expires_at: Optional[str] = None
    refresh_token: Optional[str] = None


class JiraAuthInterface(ABC):
    """Unified authentication interface for all Jira auth implementations"""

    def __init__(self, environment: str = "dev"):
        self.environment = environment

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if authentication is properly configured"""
        pass

    @abstractmethod
    def get_token(self) -> JiraAuthResult:
        """Get a valid authentication token"""
        pass

    @abstractmethod
    def refresh_token(self) -> JiraAuthResult:
        """Refresh the current authentication token"""
        pass

    @abstractmethod
    def store_credentials(self, credentials: JiraAuthCredentials) -> bool:
        """Store authentication credentials securely"""
        pass

    @abstractmethod
    def load_credentials(self) -> Optional[JiraAuthCredentials]:
        """Load stored authentication credentials"""
        pass

    @abstractmethod
    def clear_credentials(self) -> bool:
        """Clear stored authentication credentials"""
        pass

    @abstractmethod
    def api_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request"""
        pass

    @abstractmethod
    def get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        pass

    def get_environment(self) -> str:
        """Get current environment"""
        return self.environment

    def validate_token(self, token: str) -> bool:
        """Validate a token (default implementation)"""
        try:
            # Basic validation - override in implementations for specific logic
            return bool(token and len(token) > 10)
        except Exception:
            return False

    def get_auth_method(self) -> str:
        """Get the authentication method being used"""
        credentials = self.load_credentials()
        if credentials:
            return credentials.auth_method
        return "unknown"

