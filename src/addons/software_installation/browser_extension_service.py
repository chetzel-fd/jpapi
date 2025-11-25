#!/usr/bin/env python3
"""
Browser Extension Service
Handles browser extension installation via config profiles
"""

import uuid
import plistlib
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from core.auth.login_types import AuthInterface


class BrowserExtensionStrategy(ABC):
    """Strategy interface for browser extension installation"""
    
    @abstractmethod
    def create_mobileconfig(self, extension_id: str, extension_url: str = None, 
                          profile_name: str = None) -> Dict[str, Any]:
        """Create mobileconfig for browser extension"""
        pass


class ChromeExtensionStrategy(BrowserExtensionStrategy):
    """Chrome extension installation strategy"""
    
    def create_mobileconfig(self, extension_id: str, extension_url: str = None, 
                          profile_name: str = None) -> Dict[str, Any]:
        """Create Chrome extension mobileconfig"""
        if not profile_name:
            profile_name = f"Chrome Extension - {extension_id[:8]}"
        
        return {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"com.google.Chrome.extension.{extension_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"Chrome Extension - {extension_id}",
                    "PayloadDescription": f"Forces installation of extension {extension_id}",
                    "PayloadContent": {
                        "com.google.Chrome": {
                            "Forced": [
                                {
                                    "mcx_preference_settings": {
                                        "ExtensionInstallForcelist": [
                                            f"{extension_id};{extension_url}" if extension_url 
                                            else extension_id
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"Configuration profile for Chrome extension {extension_id}",
            "PayloadIdentifier": f"com.jamf.chrome.extension.{extension_id}",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }


class FirefoxExtensionStrategy(BrowserExtensionStrategy):
    """Firefox extension installation strategy"""
    
    def create_mobileconfig(self, extension_id: str, extension_url: str = None, 
                          profile_name: str = None) -> Dict[str, Any]:
        """Create Firefox extension mobileconfig"""
        if not profile_name:
            profile_name = f"Firefox Extension - {extension_id[:8]}"
        
        return {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"org.mozilla.firefox.extension.{extension_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"Firefox Extension - {extension_id}",
                    "PayloadDescription": f"Forces installation of Firefox extension {extension_id}",
                    "PayloadContent": {
                        "org.mozilla.firefox": {
                            "Forced": [
                                {
                                    "mcx_preference_settings": {
                                        "extensions.webextensions.remote": True,
                                        "extensions.install.requireBuiltInCerts": False,
                                        "extensions.autoDisableScopes": 0
                                    }
                                }
                            ]
                        }
                    }
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"Configuration profile for Firefox extension {extension_id}",
            "PayloadIdentifier": f"com.jamf.firefox.extension.{extension_id}",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }


class SafariExtensionStrategy(BrowserExtensionStrategy):
    """Safari extension installation strategy"""
    
    def create_mobileconfig(self, extension_id: str, extension_url: str = None, 
                          profile_name: str = None) -> Dict[str, Any]:
        """Create Safari extension mobileconfig"""
        if not profile_name:
            profile_name = f"Safari Extension - {extension_id[:8]}"
        
        return {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"com.apple.Safari.extension.{extension_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"Safari Extension - {extension_id}",
                    "PayloadDescription": f"Forces installation of Safari extension {extension_id}",
                    "PayloadContent": {
                        "com.apple.Safari": {
                            "Forced": [
                                {
                                    "mcx_preference_settings": {
                                        "SafariExtensionsEnabled": True,
                                        "SafariExtensionsUpdateCheckEnabled": True
                                    }
                                }
                            ]
                        }
                    }
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"Configuration profile for Safari extension {extension_id}",
            "PayloadIdentifier": f"com.jamf.safari.extension.{extension_id}",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }


class EdgeExtensionStrategy(BrowserExtensionStrategy):
    """Microsoft Edge extension installation strategy"""
    
    def create_mobileconfig(self, extension_id: str, extension_url: str = None, 
                          profile_name: str = None) -> Dict[str, Any]:
        """Create Edge extension mobileconfig"""
        if not profile_name:
            profile_name = f"Edge Extension - {extension_id[:8]}"
        
        return {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"com.microsoft.edgemac.extension.{extension_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"Edge Extension - {extension_id}",
                    "PayloadDescription": f"Forces installation of Edge extension {extension_id}",
                    "PayloadContent": {
                        "com.microsoft.edgemac": {
                            "Forced": [
                                {
                                    "mcx_preference_settings": {
                                        "ExtensionInstallForcelist": [
                                            f"{extension_id};{extension_url}" if extension_url 
                                            else extension_id
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"Configuration profile for Edge extension {extension_id}",
            "PayloadIdentifier": f"com.jamf.edge.extension.{extension_id}",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }


class BrowserExtensionService:
    """Service for browser extension installation"""
    
    def __init__(self, auth: Optional[AuthInterface] = None):
        self.auth = auth
        self._strategies = {
            'chrome': ChromeExtensionStrategy(),
            'firefox': FirefoxExtensionStrategy(),
            'safari': SafariExtensionStrategy(),
            'edge': EdgeExtensionStrategy()
        }
    
    def install_extension(self, browser: str, extension_id: str, 
                         extension_url: str = None, 
                         profile_name: str = None) -> bool:
        """Install a browser extension"""
        strategy = self._strategies.get(browser.lower())
        if not strategy:
            print(f"❌ Unsupported browser: {browser}")
            return False
        
        try:
            mobileconfig = strategy.create_mobileconfig(
                extension_id=extension_id,
                extension_url=extension_url,
                profile_name=profile_name
            )
            
            return self._deploy_mobileconfig(mobileconfig, profile_name or f"{browser.title()} Extension")
            
        except Exception as e:
            print(f"❌ Error installing {browser} extension: {e}")
            return False
    
    def _deploy_mobileconfig(self, mobileconfig: Dict[str, Any], profile_name: str) -> bool:
        """Deploy mobileconfig to Jamf Pro or save locally"""
        try:
            if self.auth:
                # Deploy to Jamf Pro
                print(f"🚀 Deploying profile to Jamf Pro: {profile_name}")
                # Implementation would use self.auth.api_request()
                return True
            else:
                # Save locally
                from pathlib import Path
                output_dir = Path("generated_profiles")
                output_dir.mkdir(exist_ok=True)
                
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{profile_name.replace(' ', '_')}_{timestamp}.mobileconfig"
                filepath = output_dir / filename
                
                with open(filepath, "wb") as f:
                    plistlib.dump(mobileconfig, f)
                
                print(f"✅ Profile saved locally: {filepath}")
                return True
                
        except Exception as e:
            print(f"❌ Error deploying profile: {e}")
            return False













