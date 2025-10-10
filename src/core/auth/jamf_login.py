#!/usr/bin/env python3
"""
Enhanced Authentication Manager with Label System
Supports multiple JAMF instances with easy setup and management
"""

import subprocess
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from pathlib import Path
from dataclasses import dataclass

from .interface import AuthCredentials, AuthResult, AuthStatus


@dataclass
class JAMFInstance:
    """Represents a JAMF Pro instance configuration"""
    label: str
    url: str
    client_id: str
    client_secret: str
    environment: str = "production"
    description: str = ""
    created_at: str = ""
    last_used: str = ""


class EnhancedAuthManager:
    """
    Enhanced authentication manager with label system
    Supports multiple JAMF instances with easy setup
    """
    
    def __init__(self):
        self.service_prefix = "jpapi"
        self.instances: Dict[str, JAMFInstance] = {}
        self.current_instance: Optional[str] = None
        self._load_instances()
    
    def _load_instances(self):
        """Load all configured JAMF instances from keychain"""
        try:
            # Get all jpapi-related keychain items
            result = subprocess.run([
                "security", "dump-keychain"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse keychain output to find jpapi instances
                lines = result.stdout.split('\n')
                current_item = {}
                
                for line in lines:
                    if '"svce"<blob>="' in line and 'jpapi' in line:
                        service = line.split('"svce"<blob>="')[1].split('"')[0]
                        if service.startswith(self.service_prefix):
                            # Extract label from service name
                            label = service.replace(f"{self.service_prefix}_", "")
                            if label not in self.instances:
                                self.instances[label] = JAMFInstance(
                                    label=label,
                                    url="",
                                    client_id="",
                                    client_secret="",
                                    environment="production"
                                )
        except Exception as e:
            print(f"Warning: Could not load instances from keychain: {e}")
    
    def list_instances(self) -> List[JAMFInstance]:
        """List all configured JAMF instances"""
        return list(self.instances.values())
    
    def get_instance(self, label: str) -> Optional[JAMFInstance]:
        """Get a specific JAMF instance by label"""
        return self.instances.get(label)
    
    def add_instance(self, label: str, url: str, client_id: str, client_secret: str, 
                    environment: str = "production", description: str = "") -> bool:
        """Add a new JAMF instance"""
        try:
            # Create credentials object
            credentials = {
                "url": url,
                "client_id": client_id,
                "client_secret": client_secret,
                "environment": environment,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            }
            
            # Store in keychain
            service_name = f"{self.service_prefix}_{label}"
            cmd = [
                "security", "add-generic-password",
                "-a", label,
                "-s", service_name,
                "-w", json.dumps(credentials),
                "-U"  # Update if exists
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Update local cache
                self.instances[label] = JAMFInstance(
                    label=label,
                    url=url,
                    client_id=client_id,
                    client_secret=client_secret,
                    environment=environment,
                    description=description,
                    created_at=credentials["created_at"],
                    last_used=credentials["last_used"]
                )
                return True
            else:
                print(f"Failed to store credentials: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error adding instance: {e}")
            return False
    
    def remove_instance(self, label: str) -> bool:
        """Remove a JAMF instance"""
        try:
            service_name = f"{self.service_prefix}_{label}"
            cmd = [
                "security", "delete-generic-password",
                "-a", label,
                "-s", service_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                if label in self.instances:
                    del self.instances[label]
                return True
            else:
                print(f"Failed to remove credentials: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error removing instance: {e}")
            return False
    
    def get_credentials(self, label: str) -> Optional[AuthCredentials]:
        """Get credentials for a specific instance"""
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
                cred_data = json.loads(result.stdout.strip())
                return AuthCredentials(
                    url=cred_data.get("url", ""),
                    client_id=cred_data.get("client_id", ""),
                    client_secret=cred_data.get("client_secret", ""),
                    token=cred_data.get("token"),
                    refresh_token=cred_data.get("refresh_token"),
                    token_expires=cred_data.get("token_expires")
                )
            return None
            
        except Exception as e:
            print(f"Error getting credentials: {e}")
            return None
    
    def set_current_instance(self, label: str) -> bool:
        """Set the current active instance"""
        if label in self.instances:
            self.current_instance = label
            return True
        return False
    
    def get_current_instance(self) -> Optional[str]:
        """Get the current active instance label"""
        return self.current_instance
    
    def test_connection(self, label: str) -> bool:
        """Test connection to a JAMF instance"""
        try:
            credentials = self.get_credentials(label)
            if not credentials:
                return False
            
            # Try to get a token
            from .unified_auth import UnifiedJamfAuth
            auth = UnifiedJamfAuth(environment=label, backend="keychain")
            token_result = auth.get_token()
            return token_result.success
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def migrate_legacy_credentials(self) -> bool:
        """Migrate legacy credentials to new label system"""
        try:
            # Check for jpapi_sandbox (your current setup)
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
                success = self.add_instance(
                    label="sandbox",
                    url=cred_data.get("url", ""),
                    client_id=cred_data.get("client_id", ""),
                    client_secret=cred_data.get("client_secret", ""),
                    environment="sandbox",
                    description="Migrated from legacy jpapi_sandbox"
                )
                
                if success:
                    print("✅ Successfully migrated sandbox credentials to new label system")
                    return True
                else:
                    print("❌ Failed to migrate sandbox credentials")
                    return False
            else:
                print("No legacy credentials found to migrate")
                return False
                
        except Exception as e:
            print(f"Migration failed: {e}")
            return False


# Global instance
auth_manager = EnhancedAuthManager()
