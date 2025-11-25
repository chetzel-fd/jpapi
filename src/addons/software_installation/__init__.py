#!/usr/bin/env python3
"""
Software Installation Addon for jpapi
Provides software installation via config profiles, policies, and packages
"""

from .software_installation_service import SoftwareInstallationService
from .software_installation_factory import SoftwareInstallationFactory
from .browser_extension_service import BrowserExtensionService
from .app_installation_service import AppInstallationService
from .profile_management_service import ProfileManagementService
from .policy_management_service import PolicyManagementService
from .script_profile_service import ScriptProfileService
from .crowdstrike_installer_service import CrowdStrikeInstallerService

__all__ = [
    "SoftwareInstallationService",
    "SoftwareInstallationFactory", 
    "BrowserExtensionService",
    "AppInstallationService",
    "ProfileManagementService",
    "PolicyManagementService",
    "ScriptProfileService",
    "CrowdStrikeInstallerService",
]
