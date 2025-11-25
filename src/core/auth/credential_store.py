#!/usr/bin/env python3
"""
Credential Store for JAMF Authentication
Handles secure storage and retrieval of credentials
Supports macOS Keychain and file-based storage
Extracted from UnifiedJamfAuth for SRP compliance
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Optional

from .login_types import AuthCredentials


class CredentialStore:
    """Handles secure credential storage and retrieval"""

    def __init__(self, environment: str, backend: str = "keychain"):
        """
        Initialize credential store

        Args:
            environment: Environment name (sandbox, production, etc.)
            backend: Storage backend (keychain or file)
        """
        self.environment = environment
        self.backend = backend

        # Handle custom service names for different environments
        env = (environment or "").lower()
        if env in ("dev", "sandbox"):
            self.service_name = "jpapi_sandbox"
        elif env in ("prod", "production"):
            self.service_name = "jpapi_production"
        else:
            self.service_name = f"jpapi_{env}"

        # Initialize backend
        self._init_backend()

    def _init_backend(self):
        """Initialize credential backend with fallback"""
        if self.backend == "keychain" and sys.platform != "darwin":
            self.backend = "file"

    def store_credentials(self, credentials: AuthCredentials) -> bool:
        """
        Store authentication credentials securely

        Args:
            credentials: Credentials to store

        Returns:
            True if successful, False otherwise
        """
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
        """
        Load stored authentication credentials

        Returns:
            AuthCredentials if found, None otherwise
        """
        try:
            if self.backend == "keychain":
                return self._load_keychain()
            elif self.backend == "file":
                return self._load_file()
            else:
                return None
        except Exception:
            return None

    def clear_credentials(self) -> bool:
        """
        Clear stored authentication credentials

        Returns:
            True if successful, False otherwise
        """
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

            # Map environment names to keychain account names
            account_mapping = {
                "dev": "sandbox",
                "prod": "production",
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
            # Map environment names to keychain account names
            account_mapping = {
                "dev": "sandbox",
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
                token=None,
                refresh_token=None,
                token_expires=None,
            )

        except Exception:
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
