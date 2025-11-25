#!/usr/bin/env python3
"""
Jira Credential Store
Handles secure storage and retrieval of Jira credentials
Supports macOS Keychain and file-based storage
Adapted from JPAPI's credential_store.py for Jira
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Optional

from .jira_auth_types import JiraAuthCredentials


class JiraCredentialStore:
    """Handles secure Jira credential storage and retrieval"""

    def __init__(self, environment: str, backend: str = "keychain"):
        """
        Initialize Jira credential store

        Args:
            environment: Environment name (dev, staging, production, etc.)
            backend: Storage backend (keychain or file)
        """
        self.environment = environment
        self.backend = backend

        # Handle custom service names for different environments
        env = (environment or "").lower()
        if env in ("dev", "development"):
            self.service_name = "jira_toolkit_dev"
        elif env in ("staging", "test"):
            self.service_name = "jira_toolkit_staging"
        elif env in ("prod", "production"):
            self.service_name = "jira_toolkit_production"
        else:
            self.service_name = f"jira_toolkit_{env}"

        # Initialize backend
        self._init_backend()

    def _init_backend(self):
        """Initialize credential backend with fallback"""
        if self.backend == "keychain" and sys.platform != "darwin":
            self.backend = "file"

    def store_credentials(self, credentials: JiraAuthCredentials) -> bool:
        """
        Store Jira authentication credentials securely

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

    def load_credentials(self) -> Optional[JiraAuthCredentials]:
        """
        Load stored Jira authentication credentials

        Returns:
            JiraAuthCredentials if found, None otherwise
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
        Clear stored Jira authentication credentials

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

    def _store_keychain(self, credentials: JiraAuthCredentials) -> bool:
        """Store Jira credentials in macOS keychain"""
        try:
            # Store as JSON in keychain
            cred_data = {
                "url": credentials.url,
                "username": credentials.username,
                "password": credentials.password,
                "api_token": credentials.api_token,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expires": credentials.token_expires,
                "auth_method": credentials.auth_method,
            }

            cred_json = json.dumps(cred_data)

            # Map environment names to keychain account names
            account_mapping = {
                "dev": "development",
                "development": "development",
                "staging": "staging",
                "test": "staging",
                "prod": "production",
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

    def _load_keychain(self) -> Optional[JiraAuthCredentials]:
        """Load Jira credentials from macOS keychain"""
        try:
            # Map environment names to keychain account names
            account_mapping = {
                "dev": "development",
                "development": "development",
                "staging": "staging",
                "test": "staging",
                "prod": "production",
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
                return JiraAuthCredentials(
                    url=cred_data.get("url", ""),
                    username=cred_data.get("username"),
                    password=cred_data.get("password"),
                    api_token=cred_data.get("api_token"),
                    client_id=cred_data.get("client_id"),
                    client_secret=cred_data.get("client_secret"),
                    token=cred_data.get("token"),
                    refresh_token=cred_data.get("refresh_token"),
                    token_expires=cred_data.get("token_expires"),
                    auth_method=cred_data.get("auth_method", "basic"),
                )

            # Fallback to individual fields (old format)
            url = self._get_keychain_field("jira_url")
            username = self._get_keychain_field("jira_username")
            api_token = self._get_keychain_field("jira_api_token")

            if not all([url, username]):
                return None

            return JiraAuthCredentials(
                url=url,
                username=username,
                api_token=api_token,
                auth_method="api_token" if api_token else "basic",
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
        """Clear Jira credentials from macOS keychain"""
        try:
            # Map environment names to keychain account names
            account_mapping = {
                "dev": "development",
                "development": "development",
                "staging": "staging",
                "test": "staging",
                "prod": "production",
                "production": "production",
            }
            account_name = account_mapping.get(self.environment, self.environment)

            cmd = [
                "security",
                "delete-generic-password",
                "-a",
                account_name,
                "-s",
                self.service_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception:
            return False

    def _store_file(self, credentials: JiraAuthCredentials) -> bool:
        """Store Jira credentials in file (fallback)"""
        try:
            config_dir = Path.home() / ".jira_toolkit"
            config_dir.mkdir(exist_ok=True)

            cred_file = config_dir / f"credentials_{self.environment}.json"

            cred_data = {
                "url": credentials.url,
                "username": credentials.username,
                "password": credentials.password,
                "api_token": credentials.api_token,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expires": credentials.token_expires,
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
                client_id=cred_data.get("client_id"),
                client_secret=cred_data.get("client_secret"),
                token=cred_data.get("token"),
                refresh_token=cred_data.get("refresh_token"),
                token_expires=cred_data.get("token_expires"),
                auth_method=cred_data.get("auth_method", "basic"),
            )

        except Exception:
            return None

    def _clear_file(self) -> bool:
        """Clear Jira credentials from file (fallback)"""
        try:
            config_dir = Path.home() / ".jira_toolkit"
            cred_file = config_dir / f"credentials_{self.environment}.json"

            if cred_file.exists():
                cred_file.unlink()

            return True

        except Exception:
            return False

