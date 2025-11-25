#!/usr/bin/env python3
"""
Unified JAMF Authentication Implementation
Single, clean implementation that replaces all existing auth modules
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
import subprocess
import urllib.request
import urllib.error
import urllib.parse
import json
import base64
import time
import sys
import getpass
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from pathlib import Path

from .login_types import AuthInterface, AuthCredentials, AuthResult, AuthStatus


class UnifiedJamfAuth(AuthInterface):
    """
    Unified JAMF authentication implementation
    Combines the best features from existing auth modules into one clean implementation
    """

    def __init__(self, environment: str = "sandbox", backend: str = "keychain"):
        super().__init__(environment)
        self.backend = backend
        # Handle custom service names for different environments (with back-compat aliases)
        env = (environment or "").lower()
        if env in ("dev", "sandbox"):
            self.service_name = "jpapi_sandbox"
        elif env in ("prod", "production"):
            self.service_name = "jpapi_production"  # Custom production service name
        else:
            self.service_name = f"jpapi_{env}"

        # Environment URLs - configure via jpapi setup or environment variables
        self.environment_urls = {
            "sandbox": os.environ.get("JPAPI_SANDBOX_URL", ""),
            "prod": os.environ.get("JPAPI_PROD_URL", ""),
            "production": os.environ.get("JPAPI_PROD_URL", ""),
        }

        # Cache
        self._credentials_cache = {}
        self._token_cache = None
        self._token_expires = None

        # Initialize backend
        self._init_backend()

    def _init_backend(self):
        """Initialize credential backend with fallback"""
        if self.backend == "keychain" and sys.platform != "darwin":
            print(
                "⚠️  Keychain not available on this platform, falling back to file storage"
            )
            self.backend = "file"

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
        try:
            credentials = self.load_credentials()
            if not credentials:
                return AuthResult(
                    success=False,
                    status=AuthStatus.NOT_CONFIGURED,
                    message="Authentication not configured. Run setup first.",
                )

            # Check if we have a valid cached token
            if credentials.token and not self._is_token_expired(
                credentials.token_expires
            ):
                return AuthResult(
                    success=True,
                    status=AuthStatus.AUTHENTICATED,
                    token=credentials.token,
                    message="Using cached valid token",
                    expires_at=credentials.token_expires,
                )

            # Try refresh first if we have a refresh token
            if credentials.refresh_token:
                refresh_result = self._refresh_token_internal(credentials)
                if refresh_result.success:
                    return refresh_result

            # Get new token
            return self._request_new_token(credentials)

        except Exception as e:
            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message=f"Failed to get token: {str(e)}",
            )

    def refresh_token(self) -> AuthResult:
        """Refresh the current authentication token"""
        try:
            credentials = self.load_credentials()
            if not credentials or not credentials.refresh_token:
                return self.get_token()  # Fall back to new token

            return self._refresh_token_internal(credentials)

        except Exception as e:
            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message=f"Failed to refresh token: {str(e)}",
            )

    def _refresh_token_internal(self, credentials: AuthCredentials) -> AuthResult:
        """Internal token refresh implementation"""
        try:
            # Prepare refresh request
            refresh_url = f"{credentials.url}/api/oauth/token"
            refresh_data = {
                "grant_type": "refresh_token",
                "refresh_token": credentials.refresh_token,
            }

            # Create request
            data = urllib.parse.urlencode(refresh_data).encode("utf-8")
            request = urllib.request.Request(refresh_url, data=data, method="POST")

            # Add authorization header
            auth_string = f"{credentials.client_id}:{credentials.client_secret}"
            auth_bytes = base64.b64encode(auth_string.encode("utf-8")).decode("ascii")
            request.add_header("Authorization", f"Basic {auth_bytes}")
            request.add_header("Content-Type", "application/x-www-form-urlencoded")

            # Make request
            with urllib.request.urlopen(request, timeout=30) as response:
                response_data = json.loads(response.read().decode("utf-8"))

            # Extract tokens
            access_token = response_data.get("access_token")
            new_refresh_token = response_data.get("refresh_token")
            expires_in = response_data.get("expires_in", 3600)

            if not access_token:
                return AuthResult(
                    success=False,
                    status=AuthStatus.INVALID,
                    message="No access token in refresh response",
                )

            # Calculate expiry
            expires_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat()

            # Update credentials
            updated_credentials = AuthCredentials(
                url=credentials.url,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                token=access_token,
                refresh_token=new_refresh_token or credentials.refresh_token,
                token_expires=expires_at,
            )

            # Store updated credentials
            self.store_credentials(updated_credentials)

            return AuthResult(
                success=True,
                status=AuthStatus.AUTHENTICATED,
                token=access_token,
                message="Token refreshed successfully",
                expires_at=expires_at,
            )

        except Exception as e:
            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message=f"Token refresh failed: {str(e)}",
            )

    def _request_new_token(self, credentials: AuthCredentials) -> AuthResult:
        """Request a new OAuth token"""
        try:
            # Prepare token request
            token_url = f"{credentials.url}/api/oauth/token"
            token_data = {
                "grant_type": "client_credentials",
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
            }

            # Create request
            data = urllib.parse.urlencode(token_data).encode("utf-8")
            request = urllib.request.Request(token_url, data=data, method="POST")
            request.add_header("Content-Type", "application/x-www-form-urlencoded")

            # Make request
            with urllib.request.urlopen(request, timeout=30) as response:
                response_data = json.loads(response.read().decode("utf-8"))

            # Extract tokens
            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")
            expires_in = response_data.get("expires_in", 3600)

            if not access_token:
                return AuthResult(
                    success=False,
                    status=AuthStatus.INVALID,
                    message="No access token in response",
                )

            # Calculate expiry (store as Unix timestamp for consistency with keychain)
            expires_at = str(int(time.time()) + expires_in)

            # Update credentials
            updated_credentials = AuthCredentials(
                url=credentials.url,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                token=access_token,
                refresh_token=refresh_token,
                token_expires=expires_at,
            )

            # Store updated credentials
            self.store_credentials(updated_credentials)

            return AuthResult(
                success=True,
                status=AuthStatus.AUTHENTICATED,
                token=access_token,
                message="New token obtained successfully",
                expires_at=expires_at,
            )

        except Exception as e:
            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message=f"Failed to get new token: {str(e)}",
            )

    def _is_token_expired(self, expires_timestamp: Optional[str]) -> bool:
        """Check if token is expired"""
        if not expires_timestamp:
            return True

        try:
            # Handle both Unix timestamp and ISO format
            if expires_timestamp.isdigit():
                # Unix timestamp
                expires_time = int(expires_timestamp)
                current_time = int(time.time())
                # Add 5 minute buffer (300 seconds)
                return current_time > (expires_time - 300)
            else:
                # ISO format
                expires_dt = datetime.fromisoformat(
                    expires_timestamp.replace("Z", "+00:00")
                )
                # Add 5 minute buffer
                buffer_time = expires_dt - timedelta(minutes=5)
                return datetime.now() > buffer_time
        except Exception:
            return True

    def store_credentials(self, credentials: AuthCredentials) -> bool:
        """Store authentication credentials securely"""
        try:
            if self.backend == "keychain":
                return self._store_keychain(credentials)
            elif self.backend == "file":
                return self._store_file(credentials)
            else:
                return False
        except Exception:
            return False

    def load_credentials(self) -> Optional[AuthCredentials]:
        """Load stored authentication credentials"""
        try:
            if self.backend == "keychain":
                return self._load_keychain()
            elif self.backend == "file":
                return self._load_file()
            else:
                return None
        except Exception as e:
            print(f"Debug: load_credentials failed: {e}")
            import traceback

            traceback.print_exc()
            return None

    def clear_credentials(self) -> bool:
        """Clear stored authentication credentials"""
        try:
            if self.backend == "keychain":
                return self._clear_keychain()
            elif self.backend == "file":
                return self._clear_file()
            else:
                return False
        except Exception:
            return False

    def _store_keychain(self, credentials: AuthCredentials) -> bool:
        """Store credentials in macOS keychain"""
        try:
            # Store as JSON in keychain
            cred_data = {
                "url": credentials.url,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expires": credentials.token_expires,
            }

            cred_json = json.dumps(cred_data)

            # Use security command to store in keychain
            # Handle custom account names for different environments
            # Map environment names to keychain account names
            account_mapping = {
                "dev": "sandbox",  # alias: dev -> sandbox
                "prod": "production",  # alias: prod -> production
                "sandbox": "sandbox",
                "production": "production",
            }
            account_name = account_mapping.get(self.environment, self.environment)

            cmd = [
                "security",
                "add-generic-password",
                "-a",
                account_name,
                "-s",
                self.service_name,
                "-w",
                cred_json,
                "-U",  # Update if exists
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception:
            return False

    def _load_keychain(self) -> Optional[AuthCredentials]:
        """Load credentials from macOS keychain"""
        try:
            # Load as JSON blob from keychain
            # Handle custom account names for different environments
            # Map environment names to keychain account names
            account_mapping = {
                "dev": "sandbox",  # alias: dev -> sandbox
                "sandbox": "sandbox",
                "prod": "prod",
                "production": "production",
            }
            account_name = account_mapping.get(self.environment, self.environment)

            cmd = [
                "security",
                "find-generic-password",
                "-a",
                account_name,
                "-s",
                self.service_name,
                "-w",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                cred_data = json.loads(result.stdout.strip())
                return AuthCredentials(
                    url=cred_data.get("url", ""),
                    client_id=cred_data.get("client_id", ""),
                    client_secret=cred_data.get("client_secret", ""),
                    token=cred_data.get("token"),
                    refresh_token=cred_data.get("refresh_token"),
                    token_expires=cred_data.get("token_expires"),
                )

            # Fallback to individual fields (old format)
            url = self._get_keychain_field("jamf_url")
            client_id = self._get_keychain_field("client_id")
            client_secret = self._get_keychain_field("client_secret")

            if not all([url, client_id, client_secret]):
                return None

            return AuthCredentials(
                url=url,
                client_id=client_id,
                client_secret=client_secret,
                token=None,  # Will be fetched when needed
                refresh_token=None,
                token_expires=None,
            )

        except Exception as e:
            return None

    def _get_keychain_field(self, account: str) -> Optional[str]:
        """Get a specific field from keychain"""
        try:
            cmd = [
                "security",
                "find-generic-password",
                "-a",
                account,
                "-s",
                self.service_name,
                "-w",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return None
            return result.stdout.strip()
        except Exception:
            return None

    def _clear_keychain(self) -> bool:
        """Clear credentials from macOS keychain"""
        try:
            cmd = [
                "security",
                "delete-generic-password",
                "-a",
                self.environment,
                "-s",
                self.service_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception:
            return False

    def _store_file(self, credentials: AuthCredentials) -> bool:
        """Store credentials in file (fallback)"""
        try:
            config_dir = Path.home() / ".jpapi"
            config_dir.mkdir(exist_ok=True)

            cred_file = config_dir / f"credentials_{self.environment}.json"

            cred_data = {
                "url": credentials.url,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expires": credentials.token_expires,
            }

            with open(cred_file, "w") as f:
                json.dump(cred_data, f, indent=2)

            # Set restrictive permissions
            cred_file.chmod(0o600)

            return True

        except Exception:
            return False

    def _load_file(self) -> Optional[AuthCredentials]:
        """Load credentials from file (fallback)"""
        try:
            config_dir = Path.home() / ".jpapi"
            cred_file = config_dir / f"credentials_{self.environment}.json"

            if not cred_file.exists():
                return None

            with open(cred_file, "r") as f:
                cred_data = json.load(f)

            return AuthCredentials(
                url=cred_data.get("url", ""),
                client_id=cred_data.get("client_id", ""),
                client_secret=cred_data.get("client_secret", ""),
                token=cred_data.get("token"),
                refresh_token=cred_data.get("refresh_token"),
                token_expires=cred_data.get("token_expires"),
            )

        except Exception:
            return None

    def _clear_file(self) -> bool:
        """Clear credentials from file (fallback)"""
        try:
            config_dir = Path.home() / ".jpapi"
            cred_file = config_dir / f"credentials_{self.environment}.json"

            if cred_file.exists():
                cred_file.unlink()

            return True

        except Exception:
            return False

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
                    # Try to parse as JSON first, fall back to raw text for XML responses
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
