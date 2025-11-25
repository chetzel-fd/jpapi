#!/usr/bin/env python3
"""
Software Installation Factory
Creates and configures software installation services following SOLID principles
"""

from typing import Optional
from core.auth.login_types import AuthInterface
from .software_installation_service import SoftwareInstallationService
from .browser_extension_service import BrowserExtensionService
from .app_installation_service import AppInstallationService
from .profile_management_service import ProfileManagementService
from .policy_management_service import PolicyManagementService
from .script_profile_service import ScriptProfileService


class SoftwareInstallationFactory:
    """Factory for creating software installation services"""
    
    def __init__(self, auth: Optional[AuthInterface] = None):
        self.auth = auth
    
    def create_software_installation_service(self) -> SoftwareInstallationService:
        """Create the main software installation service"""
        return SoftwareInstallationService(
            browser_service=self.create_browser_extension_service(),
            app_service=self.create_app_installation_service(),
            profile_service=self.create_profile_management_service(),
            policy_service=self.create_policy_management_service(),
            script_service=self.create_script_profile_service()
        )
    
    def create_browser_extension_service(self) -> BrowserExtensionService:
        """Create browser extension service"""
        return BrowserExtensionService(auth=self.auth)
    
    def create_app_installation_service(self) -> AppInstallationService:
        """Create app installation service"""
        return AppInstallationService(auth=self.auth)
    
    def create_profile_management_service(self) -> ProfileManagementService:
        """Create profile management service"""
        return ProfileManagementService(auth=self.auth)
    
    def create_policy_management_service(self) -> PolicyManagementService:
        """Create policy management service"""
        return PolicyManagementService(auth=self.auth)
    
    def create_script_profile_service(self) -> ScriptProfileService:
        """Create script profile service"""
        return ScriptProfileService(auth=self.auth)
