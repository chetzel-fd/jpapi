#!/usr/bin/env python3
"""
JAMF Authentication - Refactored with SRP compliance
Uses composition with TokenManager and CredentialStore
"""

import os
import urllib.request
import urllib.error
import json
import getpass
from typing import Dict, Optional, Any

from .login_types import AuthInterface, AuthCredentials, AuthResult, AuthStatus
from .token_manager import TokenManager
from .credential_store import CredentialStore


class JamfAuth(AuthInterface):
    """JAMF authentication using composition for SRP compliance"""

    def __init__(self, environment: str = "sandbox", backend: str = "keychain"):
        super().__init__(environment)
        self.backend = backend

        # Composed components (SRP)
        self.token_manager = TokenManager()
        self.credential_store = CredentialStore(environment, backend)

        # Environment URLs - configure via jpapi setup or environment variables
        self.environment_urls = {
            "sandbox": os.environ.get("JPAPI_SANDBOX_URL", ""),
            "prod": os.environ.get("JPAPI_PROD_URL", ""),
            "production": os.environ.get("JPAPI_PROD_URL", ""),
        }

    def is_configured(self) -> bool:
        """Check if authentication is properly configured"""
        try:
            credentials = self.load_credentials()
            if not credentials:
                return False

            required = ["url", "client_id", "client_secret"]
            return all(getattr(credentials, key, None) for key in required)
        except Exception:
            return False

    def get_token(self) -> AuthResult:
        """Get a valid authentication token"""
        credentials = self.load_credentials()
        if not credentials:
            return AuthResult(
                success=False,
                status=AuthStatus.NOT_CONFIGURED,
                message="Authentication not configured. Run setup first.",
            )

        # Delegate token management to TokenManager
        token_result = self.token_manager.get_token(credentials)

        # Update stored credentials if token was refreshed
        if token_result.success and token_result.token:
            updated_creds = AuthCredentials(
                url=credentials.url,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                token=token_result.token,
                refresh_token=token_result.refresh_token or credentials.refresh_token,
                token_expires=token_result.expires_at,
            )
            self.store_credentials(updated_creds)

        return token_result

    def refresh_token(self) -> AuthResult:
        """Refresh the current authentication token"""
        credentials = self.load_credentials()
        if not credentials:
            return AuthResult(
                success=False,
                status=AuthStatus.NOT_CONFIGURED,
                message="No credentials available",
            )

        # Delegate to TokenManager
        refresh_result = self.token_manager.refresh_token(credentials)

        # Update stored credentials if successful
        if refresh_result.success:
            updated_creds = AuthCredentials(
                url=credentials.url,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                token=refresh_result.token,
                refresh_token=(
                    refresh_result.refresh_token or credentials.refresh_token
                ),
                token_expires=refresh_result.expires_at,
            )
            self.store_credentials(updated_creds)

        return refresh_result

    def store_credentials(self, credentials: AuthCredentials) -> bool:
        """Store authentication credentials securely"""
        return self.credential_store.store_credentials(credentials)

    def load_credentials(self) -> Optional[AuthCredentials]:
        """Load stored authentication credentials"""
        return self.credential_store.load_credentials()

    def clear_credentials(self) -> bool:
        """Clear stored authentication credentials"""
        return self.credential_store.clear_credentials()

    def api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        content_type: str = "json",
    ) -> Dict[str, Any]:
        """Make authenticated API request"""
        # Get valid token
        token_result = self.get_token()
        if not token_result.success:
            raise Exception(f"Authentication failed: {token_result.message}")

        # Prepare request
        credentials = self.load_credentials()
        if not credentials:
            raise Exception("No credentials available")

        url = f"{credentials.url}{endpoint}"

        # Create request
        request_data = None
        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            if content_type == "xml":
                request_data = data.encode("utf-8")
            else:
                request_data = json.dumps(data).encode("utf-8")

        request = urllib.request.Request(url, data=request_data, method=method.upper())
        request.add_header("Authorization", f"Bearer {token_result.token}")
        request.add_header("Accept", "application/json")

        if request_data:
            if content_type == "xml":
                request.add_header("Content-Type", "application/xml")
            else:
                request.add_header("Content-Type", "application/json")

        # Make request
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                response_text = response.read().decode("utf-8")
                if response_text:
                    # Try to parse as JSON first
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        # Return raw response for XML or other non-JSON responses
                        return {"raw_response": response_text}
                else:
                    return {}
        except urllib.error.HTTPError as e:
            error_text = e.read().decode("utf-8") if e.fp else str(e)
            raise Exception(f"API request failed ({e.code}): {error_text}")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

    def api_request_xml(
        self, method: str, endpoint: str, xml_data: str
    ) -> Dict[str, Any]:
        """Make authenticated API request with XML data"""
        return self.api_request(method, endpoint, xml_data, content_type="xml")

    def get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        try:
            # Try to get current auth info from API
            auth_info = self.api_request("GET", "/api/v1/auth/current")
            return auth_info
        except Exception as e:
            # Return basic info if API call fails
            credentials = self.load_credentials()
            return {
                "environment": self.environment,
                "configured": self.is_configured(),
                "backend": self.backend,
                "url": credentials.url if credentials else None,
                "error": str(e),
            }

    def setup_interactive(self) -> bool:
        """Interactive setup for credentials"""
        print(f"🔧 Setting up JAMF authentication for environment: {self.environment}")
        print()

        # Get URL
        default_url = self.environment_urls.get(self.environment, "")
        if default_url:
            url = input(f"JAMF URL [{default_url}]: ").strip() or default_url
        else:
            url = input("JAMF URL: ").strip()

        if not url:
            print("❌ URL is required")
            return False

        # Get client credentials
        client_id = input("Client ID: ").strip()
        if not client_id:
            print("❌ Client ID is required")
            return False

        client_secret = getpass.getpass("Client Secret: ").strip()
        if not client_secret:
            print("❌ Client Secret is required")
            return False

        # Create credentials
        credentials = AuthCredentials(
            url=url, client_id=client_id, client_secret=client_secret
        )

        # Test credentials by getting a token
        print("\n🔄 Testing credentials...")

        # Temporarily store credentials
        if not self.store_credentials(credentials):
            print("❌ Failed to store credentials")
            return False

        # Test token retrieval
        token_result = self.get_token()
        if not token_result.success:
            print(f"❌ Authentication test failed: {token_result.message}")
            self.clear_credentials()
            return False

        print("✅ Authentication setup successful!")
        return True
