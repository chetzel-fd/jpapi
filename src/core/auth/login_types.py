#!/usr/bin/env python3
"""
Unified Authentication Interface for jpapi
Provides a consistent interface for all authentication implementations
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


from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class AuthStatus(Enum):
    """Authentication status enumeration"""
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    INVALID = "invalid"
    NOT_CONFIGURED = "not_configured"

@dataclass
class AuthCredentials:
    """Authentication credentials container"""
    url: str
    client_id: str
    client_secret: str
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires: Optional[str] = None

@dataclass
class AuthResult:
    """Authentication operation result"""
    success: bool
    status: AuthStatus
    token: Optional[str] = None
    message: Optional[str] = None
    expires_at: Optional[str] = None

class AuthInterface(ABC):
    """Unified authentication interface for all JAMF auth implementations"""
    
    def __init__(self, environment: str = 'dev'):
        self.environment = environment
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if authentication is properly configured"""
        pass
    
    @abstractmethod
    def get_token(self) -> AuthResult:
        """Get a valid authentication token"""
        pass
    
    @abstractmethod
    def refresh_token(self) -> AuthResult:
        """Refresh the current authentication token"""
        pass
    
    @abstractmethod
    def store_credentials(self, credentials: AuthCredentials) -> bool:
        """Store authentication credentials securely"""
        pass
    
    @abstractmethod
    def load_credentials(self) -> Optional[AuthCredentials]:
        """Load stored authentication credentials"""
        pass
    
    @abstractmethod
    def clear_credentials(self) -> bool:
        """Clear stored authentication credentials"""
        pass
    
    @abstractmethod
    def api_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
