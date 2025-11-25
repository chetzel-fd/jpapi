#!/usr/bin/env python3
"""
Software Installation Service
Main service that coordinates software installation operations
"""

from typing import Optional, List, Dict, Any
from .browser_extension_service import BrowserExtensionService
from .app_installation_service import AppInstallationService
from .profile_management_service import ProfileManagementService
from .policy_management_service import PolicyManagementService
from .script_profile_service import ScriptProfileService


class SoftwareInstallationService:
    """Main service for software installation operations"""
    
    def __init__(self, 
                 browser_service: BrowserExtensionService,
                 app_service: AppInstallationService,
                 profile_service: ProfileManagementService,
                 policy_service: PolicyManagementService,
                 script_service: ScriptProfileService):
        self.browser_service = browser_service
        self.app_service = app_service
        self.profile_service = profile_service
        self.policy_service = policy_service
        self.script_service = script_service
    
    def install_browser_extension(self, browser: str, extension_id: str, 
                                extension_url: str = None, 
                                profile_name: str = None) -> bool:
        """Install a browser extension"""
        return self.browser_service.install_extension(
            browser=browser,
            extension_id=extension_id,
            extension_url=extension_url,
            profile_name=profile_name
        )
    
    def install_app_with_installomator(self, app_name: str, label: str = None, 
                                     category: str = "Productivity") -> bool:
        """Install an application using Installomator"""
        return self.app_service.install_with_installomator(
            app_name=app_name,
            label=label,
            category=category
        )
    
    def create_software_policy(self, app_name: str, package_id: int = None, 
                             script_id: int = None, policy_name: str = None) -> bool:
        """Create a software installation policy"""
        return self.policy_service.create_policy(
            app_name=app_name,
            package_id=package_id,
            script_id=script_id,
            policy_name=policy_name
        )
    
    def create_pppc_profile(self, app_name: str, bundle_id: str, 
                          permissions: List[str], profile_name: str = None) -> bool:
        """Create a PPPC permissions profile"""
        return self.profile_service.create_pppc_profile(
            app_name=app_name,
            bundle_id=bundle_id,
            permissions=permissions,
            profile_name=profile_name
        )
    
    def download_script_and_create_profile(self, script_id: int, 
                                         profile_name: str = None,
                                         description: str = None,
                                         deploy: bool = True,
                                         auto_execute: bool = True,
                                         execution_trigger: str = "once") -> bool:
        """Download a script from Jamf Pro and create a config profile"""
        return self.script_service.deploy_script_profile(
            script_id=script_id,
            profile_name=profile_name,
            description=description,
            deploy=deploy,
            auto_execute=auto_execute,
            execution_trigger=execution_trigger
        )
    
    def batch_deploy(self, config: Dict[str, Any]) -> bool:
        """Deploy multiple items from configuration"""
        success_count = 0
        total_count = 0
        
        # Deploy extensions
        for extension in config.get("extensions", []):
            total_count += 1
            if self.install_browser_extension(
                browser=extension["browser"],
                extension_id=extension["extension_id"],
                extension_url=extension.get("extension_url"),
                profile_name=extension.get("profile_name")
            ):
                success_count += 1
        
        # Deploy apps
        for app in config.get("apps", []):
            total_count += 1
            if self.install_app_with_installomator(
                app_name=app["app_name"],
                label=app.get("label"),
                category=app.get("category", "Productivity")
            ):
                success_count += 1
        
        # Deploy PPPC profiles
        for pppc in config.get("pppc_profiles", []):
            total_count += 1
            if self.create_pppc_profile(
                app_name=pppc["app_name"],
                bundle_id=pppc["bundle_id"],
                permissions=pppc["permissions"],
                profile_name=pppc.get("profile_name")
            ):
                success_count += 1
        
        return success_count == total_count
