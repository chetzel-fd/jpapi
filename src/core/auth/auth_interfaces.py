#!/usr/bin/env python3
"""
Authentication Interfaces
Defines focused interfaces for JAMF Pro authentication
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class JAMFInstance:
    """Data class for JAMF instance information"""

    label: str
    url: str
    client_id: str
    client_secret: str
    environment: str = "production"
    description: str = ""
    created_at: str = ""
    last_used: str = ""


# Single Responsibility: Instance Management Only
class IInstanceManager(ABC):
    """Interface for managing JAMF instances - SRP compliant"""

    @abstractmethod
    def list_instances(self) -> List[JAMFInstance]:
        """List all configured instances"""
        pass

    @abstractmethod
    def get_instance(self, label: str) -> Optional[JAMFInstance]:
        """Get specific instance by label"""
        pass

    @abstractmethod
    def add_instance(self, instance: JAMFInstance) -> bool:
        """Add new instance"""
        pass

    @abstractmethod
    def remove_instance(self, label: str) -> bool:
        """Remove instance"""
        pass

    @abstractmethod
    def set_current_instance(self, label: str) -> bool:
        """Set current active instance"""
        pass

    @abstractmethod
    def get_current_instance(self) -> Optional[str]:
        """Get current active instance label"""
        pass


# Single Responsibility: Credential Storage Only
class ICredentialStorage(ABC):
    """Interface for credential storage - SRP compliant"""

    @abstractmethod
    def store_credentials(self, label: str, credentials: Dict[str, Any]) -> bool:
        """Store credentials for a label"""
        pass

    @abstractmethod
    def load_credentials(self, label: str) -> Optional[Dict[str, Any]]:
        """Load credentials for a label"""
        pass

    @abstractmethod
    def remove_credentials(self, label: str) -> bool:
        """Remove credentials for a label"""
        pass

    @abstractmethod
    def list_credential_labels(self) -> List[str]:
        """List all stored credential labels"""
        pass


# Single Responsibility: Connection Testing Only
class IConnectionTester(ABC):
    """Interface for testing connections - SRP compliant"""

    @abstractmethod
    def test_connection(self, instance: JAMFInstance) -> bool:
        """Test connection to JAMF instance"""
        pass


# Single Responsibility: Token Management Only
class ITokenManager(ABC):
    """Interface for token management - SRP compliant"""

    @abstractmethod
    def get_token(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Get authentication token"""
        pass

    @abstractmethod
    def refresh_token(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh authentication token"""
        pass

    @abstractmethod
    def is_token_valid(self, token: str, expires_at: str) -> bool:
        """Check if token is valid"""
        pass


# Single Responsibility: API Requests Only
class IAPIClient(ABC):
    """Interface for API requests - SRP compliant"""

    @abstractmethod
    def make_request(
        self, method: str, url: str, headers: Dict[str, str], data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Make HTTP request"""
        pass


# Single Responsibility: Migration Only
class ICredentialMigrator(ABC):
    """Interface for credential migration - SRP compliant"""

    @abstractmethod
    def migrate_legacy_credentials(self) -> bool:
        """Migrate legacy credentials to new system"""
        pass

    @abstractmethod
    def detect_legacy_credentials(self) -> List[str]:
        """Detect available legacy credentials"""
        pass
