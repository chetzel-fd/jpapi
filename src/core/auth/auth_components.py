#!/usr/bin/env python3
"""
Authentication Components
Modular authentication implementations for JAMF Pro
"""

import subprocess
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any

from .auth_interfaces import (
    IInstanceManager, ICredentialStorage, IConnectionTester, 
    ITokenManager, IAPIClient, ICredentialMigrator, JAMFInstance
)


# Single Responsibility: Keychain Storage Operations Only
class KeychainCredentialStorage(ICredentialStorage):
    """Handles credential storage in macOS keychain - SRP compliant"""
    
    def __init__(self, service_prefix: str = "jpapi"):
        self.service_prefix = service_prefix
    
    def store_credentials(self, label: str, credentials: Dict[str, Any]) -> bool:
        """Store credentials in keychain"""
        try:
            service_name = f"{self.service_prefix}_{label}"
            cmd = [
                "security", "add-generic-password",
                "-a", label,
                "-s", service_name,
                "-w", json.dumps(credentials),
                "-U"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def load_credentials(self, label: str) -> Optional[Dict[str, Any]]:
        """Load credentials from keychain"""
        try:
            service_name = f"{self.service_prefix}_{label}"
            cmd = [
                "security", "find-generic-password",
                "-a", label,
                "-s", service_name,
                "-w"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            return None
        except Exception:
            return None
    
    def remove_credentials(self, label: str) -> bool:
        """Remove credentials from keychain"""
        try:
            service_name = f"{self.service_prefix}_{label}"
            cmd = [
                "security", "delete-generic-password",
                "-a", label,
                "-s", service_name
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def list_credential_labels(self) -> List[str]:
        """List all stored credential labels"""
        try:
            result = subprocess.run(["security", "dump-keychain"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                labels = []
                lines = result.stdout.split('\n')
                for line in lines:
                    if f'"{self.service_prefix}_' in line:
                        service = line.split(f'"{self.service_prefix}_')[1].split('"')[0]
                        labels.append(service)
                return labels
            return []
        except Exception:
            return []


# Single Responsibility: Instance Management Only
class InstanceManager(IInstanceManager):
    """Manages JAMF instances - SRP compliant"""
    
    def __init__(self, storage: ICredentialStorage):
        self.storage = storage
        self.current_instance: Optional[str] = None
    
    def list_instances(self) -> List[JAMFInstance]:
        """List all configured instances"""
        instances = []
        for label in self.storage.list_credential_labels():
            creds = self.storage.load_credentials(label)
            if creds:
                instances.append(JAMFInstance(
                    label=label,
                    url=creds.get("url", ""),
                    client_id=creds.get("client_id", ""),
                    client_secret=creds.get("client_secret", ""),
                    environment=creds.get("environment", "production"),
                    description=creds.get("description", ""),
                    created_at=creds.get("created_at", ""),
                    last_used=creds.get("last_used", "")
                ))
        return instances
    
    def get_instance(self, label: str) -> Optional[JAMFInstance]:
        """Get specific instance by label"""
        creds = self.storage.load_credentials(label)
        if creds:
            return JAMFInstance(
                label=label,
                url=creds.get("url", ""),
                client_id=creds.get("client_id", ""),
                client_secret=creds.get("client_secret", ""),
                environment=creds.get("environment", "production"),
                description=creds.get("description", ""),
                created_at=creds.get("created_at", ""),
                last_used=creds.get("last_used", "")
            )
        return None
    
    def add_instance(self, instance: JAMFInstance) -> bool:
        """Add new instance"""
        credentials = {
            "url": instance.url,
            "client_id": instance.client_id,
            "client_secret": instance.client_secret,
            "environment": instance.environment,
            "description": instance.description,
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        }
        return self.storage.store_credentials(instance.label, credentials)
    
    def remove_instance(self, label: str) -> bool:
        """Remove instance"""
        return self.storage.remove_credentials(label)
    
    def set_current_instance(self, label: str) -> bool:
        """Set current active instance"""
        if self.get_instance(label):
            self.current_instance = label
            return True
        return False
    
    def get_current_instance(self) -> Optional[str]:
        """Get current active instance label"""
        return self.current_instance


# Single Responsibility: Connection Testing Only
class JAMFConnectionTester(IConnectionTester):
    """Tests connections to JAMF instances - SRP compliant"""
    
    def __init__(self, token_manager: ITokenManager):
        self.token_manager = token_manager
    
    def test_connection(self, instance: JAMFInstance) -> bool:
        """Test connection to JAMF instance"""
        try:
            credentials = {
                "url": instance.url,
                "client_id": instance.client_id,
                "client_secret": instance.client_secret
            }
            result = self.token_manager.get_token(credentials)
            return result.get("success", False)
        except Exception:
            return False


# Single Responsibility: Token Management Only
class OAuthTokenManager(ITokenManager):
    """Manages OAuth tokens - SRP compliant"""
    
    def get_token(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Get authentication token"""
        try:
            token_url = f"{credentials['url']}/api/oauth/token"
            token_data = {
                "grant_type": "client_credentials",
                "client_id": credentials["client_id"],
                "client_secret": credentials["client_secret"],
            }
            
            data = urllib.parse.urlencode(token_data).encode("utf-8")
            request = urllib.request.Request(token_url, data=data, method="POST")
            request.add_header("Content-Type", "application/x-www-form-urlencoded")
            
            with urllib.request.urlopen(request, timeout=30) as response:
                response_data = json.loads(response.read().decode("utf-8"))
            
            access_token = response_data.get("access_token")
            if access_token:
                return {
                    "success": True,
                    "token": access_token,
                    "expires_in": response_data.get("expires_in", 3600),
                    "refresh_token": response_data.get("refresh_token")
                }
            else:
                return {"success": False, "error": "No access token in response"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def refresh_token(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh authentication token"""
        try:
            refresh_url = f"{credentials['url']}/api/oauth/token"
            refresh_data = {
                "grant_type": "refresh_token",
                "refresh_token": credentials.get("refresh_token"),
            }
            
            data = urllib.parse.urlencode(refresh_data).encode("utf-8")
            request = urllib.request.Request(refresh_url, data=data, method="POST")
            
            auth_string = f"{credentials['client_id']}:{credentials['client_secret']}"
            auth_bytes = base64.b64encode(auth_string.encode("utf-8")).decode("ascii")
            request.add_header("Authorization", f"Basic {auth_bytes}")
            request.add_header("Content-Type", "application/x-www-form-urlencoded")
            
            with urllib.request.urlopen(request, timeout=30) as response:
                response_data = json.loads(response.read().decode("utf-8"))
            
            access_token = response_data.get("access_token")
            if access_token:
                return {
                    "success": True,
                    "token": access_token,
                    "expires_in": response_data.get("expires_in", 3600),
                    "refresh_token": response_data.get("refresh_token")
                }
            else:
                return {"success": False, "error": "No access token in refresh response"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_token_valid(self, token: str, expires_at: str) -> bool:
        """Check if token is valid"""
        try:
            if not expires_at:
                return False
            
            if expires_at.isdigit():
                expires_time = int(expires_at)
                current_time = int(time.time())
                return current_time < (expires_time - 300)  # 5 minute buffer
            else:
                expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                buffer_time = expires_dt - timedelta(minutes=5)
                return datetime.now() < buffer_time
        except Exception:
            return False


# Single Responsibility: API Requests Only
class HTTPAPIClient(IAPIClient):
    """Makes HTTP API requests - SRP compliant"""
    
    def make_request(self, method: str, url: str, headers: Dict[str, str], 
                    data: Optional[Any] = None) -> Dict[str, Any]:
        """Make HTTP request"""
        try:
            request_data = None
            if data and method.upper() in ["POST", "PUT", "PATCH"]:
                if isinstance(data, str):
                    request_data = data.encode("utf-8")
                else:
                    request_data = json.dumps(data).encode("utf-8")
            
            request = urllib.request.Request(url, data=request_data, method=method.upper())
            for key, value in headers.items():
                request.add_header(key, value)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                response_text = response.read().decode("utf-8")
                if response_text:
                    try:
                        return {"success": True, "data": json.loads(response_text)}
                    except json.JSONDecodeError:
                        return {"success": True, "data": {"raw_response": response_text}}
                else:
                    return {"success": True, "data": {}}
                    
        except urllib.error.HTTPError as e:
            error_text = e.read().decode("utf-8") if e.fp else str(e)
            return {"success": False, "error": f"HTTP {e.code}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Single Responsibility: Migration Only
class LegacyCredentialMigrator(ICredentialMigrator):
    """Migrates legacy credentials - SRP compliant"""
    
    def __init__(self, storage: ICredentialStorage):
        self.storage = storage
    
    def migrate_legacy_credentials(self) -> bool:
        """Migrate legacy credentials to new system"""
        try:
            # Check for jpapi_sandbox
            cmd = [
                "security", "find-generic-password",
                "-a", "sandbox",
                "-s", "jpapi_sandbox",
                "-w"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                cred_data = json.loads(result.stdout.strip())
                
                # Migrate to new system
                credentials = {
                    "url": cred_data.get("url", ""),
                    "client_id": cred_data.get("client_id", ""),
                    "client_secret": cred_data.get("client_secret", ""),
                    "environment": "sandbox",
                    "description": "Migrated from legacy jpapi_sandbox",
                    "created_at": datetime.now().isoformat(),
                    "last_used": datetime.now().isoformat()
                }
                
                return self.storage.store_credentials("sandbox", credentials)
            return False
            
        except Exception:
            return False
    
    def detect_legacy_credentials(self) -> List[str]:
        """Detect available legacy credentials"""
        try:
            result = subprocess.run(["security", "dump-keychain"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                legacy_labels = []
                lines = result.stdout.split('\n')
                for line in lines:
                    if '"svce"<blob>="jpapi' in line and 'sandbox' in line:
                        legacy_labels.append("sandbox")
                return legacy_labels
            return []
        except Exception:
            return []
