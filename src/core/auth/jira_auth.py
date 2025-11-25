#!/usr/bin/env python3
"""
Jira Authentication - Mirrors JPAPI auth flow
Uses composition with TokenManager and CredentialStore for Jira
"""

import os
import urllib.request
import urllib.error
import urllib.parse
import json
import getpass
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .login_types import AuthInterface, AuthCredentials, AuthResult, AuthStatus


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
    token: Optional[str] = None
    token_expires: Optional[str] = None
    auth_method: str = "api_token"  # "basic", "api_token"


@dataclass
class JiraAuthResult:
    """Jira authentication result data structure"""

    success: bool
    status: JiraAuthStatus
    message: str
    token: Optional[str] = None
    expires_at: Optional[str] = None


class JiraAuth(AuthInterface):
    """Jira authentication using composition for SRP compliance"""

    def __init__(self, environment: str = "dev", backend: str = "keychain"):
        super().__init__(environment)
        self.backend = backend

        # Environment URLs - configure via environment variables or setup
        self.environment_urls = {
            "dev": os.environ.get("JIRA_DEV_URL", ""),
            "staging": os.environ.get("JIRA_STAGING_URL", ""),
            "prod": os.environ.get("JIRA_PROD_URL", ""),
            "production": os.environ.get("JIRA_PROD_URL", ""),
        }

        # Cache
        self._credentials_cache = {}
        self._token_cache = None
        self._token_expires = None

        # Initialize backend
        self._init_backend()

    def _init_backend(self):
        """Initialize credential backend with fallback"""
        import sys

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

            required = ["url", "username"]
            if credentials.auth_method == "api_token":
                required.append("api_token")
            elif credentials.auth_method == "basic":
                required.append("password")

            return all(getattr(credentials, key, None) for key in required)
        except Exception:
            return False

    def get_token(self) -> AuthResult:
        """Get a valid authentication token (for Jira, this is usually the API token)"""
        try:
            credentials = self.load_credentials()
            if not credentials:
                return AuthResult(
                    success=False,
                    status=AuthStatus.NOT_CONFIGURED,
                    message="Authentication not configured. Run setup first.",
                )

            # For Jira, we typically use API tokens or basic auth
            if credentials.auth_method == "api_token":
                return AuthResult(
                    success=True,
                    status=AuthStatus.AUTHENTICATED,
                    token=credentials.api_token,
                    message="Using API token authentication",
                )
            elif credentials.auth_method == "basic":
                # For basic auth, we encode username:password
                auth_string = f"{credentials.username}:{credentials.password}"
                encoded_auth = base64.b64encode(auth_string.encode()).decode()
                return AuthResult(
                    success=True,
                    status=AuthStatus.AUTHENTICATED,
                    token=encoded_auth,
                    message="Using basic authentication",
                )

            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message="Invalid authentication method",
            )

        except Exception as e:
            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message=f"Failed to get token: {str(e)}",
            )

    def refresh_token(self) -> AuthResult:
        """Refresh the current authentication token (Jira doesn't typically use refresh tokens)"""
        # For Jira, we usually just return the current token
        return self.get_token()

    def store_credentials(self, credentials: AuthCredentials) -> bool:
        """Store authentication credentials securely"""
        try:
            # Convert AuthCredentials to JiraAuthCredentials
            jira_creds = JiraAuthCredentials(
                url=credentials.url,
                username=credentials.client_id,  # Map client_id to username
                password=credentials.client_secret,  # Map client_secret to password
                api_token=credentials.token,  # Map token to api_token
                auth_method="api_token" if credentials.token else "basic",
            )

            return self._store_credentials_internal(jira_creds)
        except Exception:
            return False

    def load_credentials(self) -> Optional[JiraAuthCredentials]:
        """Load stored authentication credentials"""
        try:
            return self._load_credentials_internal()
        except Exception:
            return None

    def clear_credentials(self) -> bool:
        """Clear stored authentication credentials"""
        try:
            return self._clear_credentials_internal()
        except Exception:
            return False

    def api_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request to Jira"""
        try:
            auth_result = self.get_token()
            if not auth_result.success:
                raise Exception(f"Authentication failed: {auth_result.message}")

            credentials = self.load_credentials()
            if not credentials:
                raise Exception("No credentials available")

            # Build full URL
            if endpoint.startswith("http"):
                url = endpoint
            else:
                base_url = credentials.url.rstrip("/")
                endpoint = endpoint.lstrip("/")
                url = f"{base_url}/rest/api/3/{endpoint}"

            # Prepare request
            if data:
                data_json = json.dumps(data).encode("utf-8")
                request = urllib.request.Request(url, data=data_json, method=method)
                request.add_header("Content-Type", "application/json")
            else:
                request = urllib.request.Request(url, method=method)

            # Add authentication header
            if credentials.auth_method == "api_token":
                auth_string = f"{credentials.username}:{credentials.api_token}"
                encoded_auth = base64.b64encode(auth_string.encode()).decode()
                request.add_header("Authorization", f"Basic {encoded_auth}")
            elif credentials.auth_method == "basic":
                request.add_header("Authorization", f"Basic {auth_result.token}")

            # Add standard Jira headers
            request.add_header("Accept", "application/json")

            # Make request
            with urllib.request.urlopen(request, timeout=30) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                return response_data

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else "No error details"
            raise Exception(f"HTTP {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

    def get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        credentials = self.load_credentials()
        if not credentials:
            return {"configured": False, "message": "Not configured"}

        return {
            "configured": True,
            "url": credentials.url,
            "username": credentials.username,
            "auth_method": credentials.auth_method,
            "environment": self.environment,
        }

    def _store_credentials_internal(self, credentials: JiraAuthCredentials) -> bool:
        """Store Jira credentials securely"""
        try:
            if self.backend == "keychain":
                return self._store_keychain(credentials)
            elif self.backend == "file":
                return self._store_file(credentials)
            else:
                return False
        except Exception:
            return False

    def _load_credentials_internal(self) -> Optional[JiraAuthCredentials]:
        """Load Jira credentials"""
        try:
            if self.backend == "keychain":
                return self._load_keychain()
            elif self.backend == "file":
                return self._load_file()
            else:
                return None
        except Exception:
            return None

    def _clear_credentials_internal(self) -> bool:
        """Clear Jira credentials"""
        try:
            if self.backend == "keychain":
                return self._clear_keychain()
            elif self.backend == "file":
                return self._clear_file()
            else:
                return False
        except Exception:
            return False

    def _store_keychain(self, credentials: JiraAuthCredentials) -> bool:
        """Store Jira credentials in macOS keychain"""
        try:
            import subprocess

            # Store as JSON in keychain
            cred_data = {
                "url": credentials.url,
                "username": credentials.username,
                "password": credentials.password,
                "api_token": credentials.api_token,
                "auth_method": credentials.auth_method,
            }

            cred_json = json.dumps(cred_data)

            # Service name for keychain
            service_name = f"jira_toolkit_{self.environment}"

            cmd = [
                "security",
                "add-generic-password",
                "-a",
                self.environment,
                "-s",
                service_name,
                "-w",
                cred_json,
                "-U",  # Update if exists
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception:
            return False

    def _load_keychain(self) -> Optional[JiraAuthCredentials]:
        """Load Jira credentials from macOS keychain"""
        try:
            import subprocess

            service_name = f"jira_toolkit_{self.environment}"

            cmd = [
                "security",
                "find-generic-password",
                "-a",
                self.environment,
                "-s",
                service_name,
                "-w",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                cred_data = json.loads(result.stdout.strip())
                return JiraAuthCredentials(
                    url=cred_data.get("url", ""),
                    username=cred_data.get("username"),
                    password=cred_data.get("password"),
                    api_token=cred_data.get("api_token"),
                    auth_method=cred_data.get("auth_method", "api_token"),
                )
            return None

        except Exception:
            return None

    def _clear_keychain(self) -> bool:
        """Clear Jira credentials from macOS keychain"""
        try:
            import subprocess

            service_name = f"jira_toolkit_{self.environment}"

            cmd = [
                "security",
                "delete-generic-password",
                "-a",
                self.environment,
                "-s",
                service_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception:
            return False

    def _store_file(self, credentials: JiraAuthCredentials) -> bool:
        """Store Jira credentials in file (fallback)"""
        try:
            from pathlib import Path

            config_dir = Path.home() / ".jira_toolkit"
            config_dir.mkdir(exist_ok=True)

            cred_file = config_dir / f"credentials_{self.environment}.json"

            cred_data = {
                "url": credentials.url,
                "username": credentials.username,
                "password": credentials.password,
                "api_token": credentials.api_token,
                "auth_method": credentials.auth_method,
            }

            with open(cred_file, "w") as f:
                json.dump(cred_data, f, indent=2)

            # Set restrictive permissions
            cred_file.chmod(0o600)

            return True

        except Exception:
            return False

    def _load_file(self) -> Optional[JiraAuthCredentials]:
        """Load Jira credentials from file (fallback)"""
        try:
            from pathlib import Path

            config_dir = Path.home() / ".jira_toolkit"
            cred_file = config_dir / f"credentials_{self.environment}.json"

            if not cred_file.exists():
                return None

            with open(cred_file, "r") as f:
                cred_data = json.load(f)

            return JiraAuthCredentials(
                url=cred_data.get("url", ""),
                username=cred_data.get("username"),
                password=cred_data.get("password"),
                api_token=cred_data.get("api_token"),
                auth_method=cred_data.get("auth_method", "api_token"),
            )

        except Exception:
            return None

    def _clear_file(self) -> bool:
        """Clear Jira credentials from file (fallback)"""
        try:
            from pathlib import Path

            config_dir = Path.home() / ".jira_toolkit"
            cred_file = config_dir / f"credentials_{self.environment}.json"

            if cred_file.exists():
                cred_file.unlink()

            return True

        except Exception:
            return False

