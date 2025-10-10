#!/usr/bin/env python3
"""
Labeled Authentication System
Works with the enhanced auth manager to support multiple JAMF instances
"""

import subprocess
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .interface import AuthCredentials, AuthResult, AuthStatus
from .enhanced_auth_manager import auth_manager


class LabeledJamfAuth:
    """
    JAMF authentication that works with the label system
    Supports multiple JAMF instances with easy switching
    """
    
    def __init__(self, label: str = "sandbox", backend: str = "keychain"):
        self.label = label
        self.backend = backend
        self.manager = auth_manager
        
        # Ensure the instance exists
        if label not in [i.label for i in self.manager.list_instances()]:
            print(f"⚠️  Warning: Instance '{label}' not found in configured instances")
            print("Available instances:", [i.label for i in self.manager.list_instances()])
    
    def is_configured(self) -> bool:
        """Check if authentication is properly configured"""
        try:
            credentials = self.manager.get_credentials(self.label)
            if not credentials:
                return False
            
            required = ["url", "client_id", "client_secret"]
            return all(getattr(credentials, key, None) for key in required)
        except Exception:
            return False
    
    def get_token(self) -> AuthResult:
        """Get a valid authentication token"""
        try:
            credentials = self.manager.get_credentials(self.label)
            if not credentials:
                return AuthResult(
                    success=False,
                    status=AuthStatus.NOT_CONFIGURED,
                    message=f"Authentication not configured for '{self.label}'. Run server setup tool.",
                )
            
            # Check if we have a valid cached token
            if credentials.token and not self._is_token_expired(credentials.token_expires):
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
            credentials = self.manager.get_credentials(self.label)
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
            import urllib.request
            import urllib.parse
            import base64
            
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
            
            # Update credentials in keychain
            self._update_credentials(credentials, access_token, new_refresh_token or credentials.refresh_token, expires_at)
            
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
            import urllib.request
            import urllib.parse
            
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
            
            # Update credentials in keychain
            self._update_credentials(credentials, access_token, refresh_token, expires_at)
            
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
    
    def _update_credentials(self, credentials: AuthCredentials, token: str, refresh_token: str, expires_at: str):
        """Update credentials in keychain"""
        try:
            # Create updated credentials
            updated_creds = {
                "url": credentials.url,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "token": token,
                "refresh_token": refresh_token,
                "token_expires": expires_at,
                "environment": getattr(credentials, 'environment', 'production'),
                "last_used": datetime.now().isoformat()
            }
            
            # Store in keychain
            service_name = f"jpapi_{self.label}"
            cmd = [
                "security", "add-generic-password",
                "-a", self.label,
                "-s", service_name,
                "-w", json.dumps(updated_creds),
                "-U"  # Update if exists
            ]
            
            subprocess.run(cmd, capture_output=True, text=True)
            
        except Exception as e:
            print(f"Warning: Could not update credentials: {e}")
    
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
                expires_dt = datetime.fromisoformat(expires_timestamp.replace("Z", "+00:00"))
                # Add 5 minute buffer
                buffer_time = expires_dt - timedelta(minutes=5)
                return datetime.now() > buffer_time
        except Exception:
            return True
    
    def api_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                   content_type: str = "json") -> Dict[str, Any]:
        """Make authenticated API request"""
        # Get valid token
        token_result = self.get_token()
        if not token_result.success:
            raise Exception(f"Authentication failed: {token_result.message}")
        
        # Prepare request
        credentials = self.manager.get_credentials(self.label)
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
        
        import urllib.request
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
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {"raw_response": response_text}
                else:
                    return {}
        except urllib.error.HTTPError as e:
            error_text = e.read().decode("utf-8") if e.fp else str(e)
            raise Exception(f"API request failed ({e.code}): {error_text}")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        try:
            # Try to get current auth info from API
            auth_info = self.api_request("GET", "/api/v1/auth/current")
            return auth_info
        except Exception as e:
            # Return basic info if API call fails
            credentials = self.manager.get_credentials(self.label)
            return {
                "label": self.label,
                "configured": self.is_configured(),
                "url": credentials.url if credentials else None,
                "error": str(e),
            }
    
    def load_credentials(self) -> Optional[AuthCredentials]:
        """Load stored authentication credentials"""
        return self.manager.get_credentials(self.label)
    
    def store_credentials(self, credentials: AuthCredentials) -> bool:
        """Store authentication credentials (delegates to manager)"""
        return self.manager.add_instance(
            label=self.label,
            url=credentials.url,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret
        )
    
    def clear_credentials(self) -> bool:
        """Clear stored authentication credentials"""
        return self.manager.remove_instance(self.label)
