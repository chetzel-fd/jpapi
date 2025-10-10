#!/usr/bin/env python3
"""
Authentication Interfaces
Defines interfaces for authentication following SRP and ISP
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class AuthStatus(Enum):
    """Authentication status enumeration"""

    AUTHENTICATED = "authenticated"
    NOT_CONFIGURED = "not_configured"
    INVALID = "invalid"
    EXPIRED = "expired"
    REFRESHING = "refreshing"


@dataclass
class AuthCredentials:
    """Authentication credentials data structure"""

    url: str
    client_id: str
    client_secret: str
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires: Optional[str] = None
    environment: str = "dev"


@dataclass
class AuthResult:
    """Authentication result data structure"""

    success: bool
    status: AuthStatus
    token: Optional[str] = None
    message: str = ""
    expires_at: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None


@dataclass
class SessionInfo:
    """Session information data structure"""

    session_id: str
    user_id: str
    tenant_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    expires_at: Optional[datetime] = None


class IAuthCredentials(ABC):
    """Interface for managing authentication credentials"""

    @abstractmethod
    def load_credentials(self, environment: str = "dev") -> Optional[AuthCredentials]:
        """Load stored credentials"""
        pass

    @abstractmethod
    def store_credentials(self, credentials: AuthCredentials) -> bool:
        """Store credentials securely"""
        pass

    @abstractmethod
    def clear_credentials(self, environment: str = "dev") -> bool:
        """Clear stored credentials"""
        pass

    @abstractmethod
    def is_configured(self, environment: str = "dev") -> bool:
        """Check if credentials are configured"""
        pass


class IAuthProvider(ABC):
    """Interface for authentication providers following SRP"""

    @abstractmethod
    def authenticate(self, credentials: AuthCredentials) -> AuthResult:
        """Authenticate with credentials"""
        pass

    @abstractmethod
    def refresh_token(
        self, refresh_token: str, credentials: AuthCredentials
    ) -> AuthResult:
        """Refresh authentication token"""
        pass

    @abstractmethod
    def validate_token(self, token: str) -> AuthResult:
        """Validate existing token"""
        pass

    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """Revoke authentication token"""
        pass


class IAuthManager(ABC):
    """Interface for authentication management following SRP"""

    @abstractmethod
    def get_auth_provider(self, provider_type: str) -> IAuthProvider:
        """Get authentication provider by type"""
        pass

    @abstractmethod
    def create_session(
        self, user_id: str, tenant_id: Optional[str] = None
    ) -> SessionInfo:
        """Create user session"""
        pass

    @abstractmethod
    def validate_session(self, session_id: str) -> Optional[SessionInfo]:
        """Validate session"""
        pass

    @abstractmethod
    def refresh_session(self, session_id: str) -> Optional[SessionInfo]:
        """Refresh session"""
        pass

    @abstractmethod
    def destroy_session(self, session_id: str) -> bool:
        """Destroy session"""
        pass

    @abstractmethod
    def get_active_sessions(self, user_id: Optional[str] = None) -> List[SessionInfo]:
        """Get active sessions"""
        pass


class IAPIAuthenticator(ABC):
    """Interface for API authentication following ISP"""

    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        pass

    @abstractmethod
    def make_authenticated_request(self, method: str, url: str, **kwargs) -> Any:
        """Make authenticated API request"""
        pass
