#!/usr/bin/env python3
"""
Token Manager for JAMF Authentication
Handles OAuth token lifecycle: acquisition, refresh, and expiration
Extracted from UnifiedJamfAuth for SRP compliance
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .login_types import AuthCredentials, AuthResult, AuthStatus


class TokenManager:
    """Manages OAuth token lifecycle for JAMF authentication"""

    def get_token(self, credentials: AuthCredentials) -> AuthResult:
        """
        Get a valid authentication token

        Args:
            credentials: Authentication credentials

        Returns:
            AuthResult with token or error
        """
        try:
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
                refresh_result = self.refresh_token(credentials)
                if refresh_result.success:
                    return refresh_result

            # Get new token
            return self.request_new_token(credentials)

        except Exception as e:
            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message=f"Failed to get token: {str(e)}",
            )

    def refresh_token(self, credentials: AuthCredentials) -> AuthResult:
        """
        Refresh the current authentication token

        Args:
            credentials: Authentication credentials with refresh token

        Returns:
            AuthResult with new token or error
        """
        if not credentials.refresh_token:
            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message="No refresh token available",
            )

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
            import base64

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

            return AuthResult(
                success=True,
                status=AuthStatus.AUTHENTICATED,
                token=access_token,
                refresh_token=new_refresh_token or credentials.refresh_token,
                message="Token refreshed successfully",
                expires_at=expires_at,
            )

        except Exception as e:
            return AuthResult(
                success=False,
                status=AuthStatus.INVALID,
                message=f"Token refresh failed: {str(e)}",
            )

    def request_new_token(self, credentials: AuthCredentials) -> AuthResult:
        """
        Request a new OAuth token

        Args:
            credentials: Authentication credentials

        Returns:
            AuthResult with new token or error
        """
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

            # Calculate expiry (store as Unix timestamp for consistency)
            expires_at = str(int(time.time()) + expires_in)

            return AuthResult(
                success=True,
                status=AuthStatus.AUTHENTICATED,
                token=access_token,
                refresh_token=refresh_token,
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
        """
        Check if token is expired

        Args:
            expires_timestamp: Expiration timestamp (Unix or ISO format)

        Returns:
            True if expired, False otherwise
        """
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
