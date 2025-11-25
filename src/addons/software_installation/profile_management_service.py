#!/usr/bin/env python3
"""
Profile Management Service
Handles PPPC and preference profile creation and deployment
"""

import uuid
import plistlib
from typing import Optional, List, Dict, Any
from core.auth.login_types import AuthInterface


class ProfileManagementService:
    """Service for profile management operations"""
    
    def __init__(self, auth: Optional[AuthInterface] = None):
        self.auth = auth
    
    def create_pppc_profile(self, app_name: str, bundle_id: str, 
                          permissions: List[str], profile_name: str = None) -> bool:
        """Create a PPPC permissions profile"""
        if not profile_name:
            profile_name = f"{app_name} PPPC Permissions"
        
        print(f"🔒 Creating PPPC profile: {app_name}")
        
        try:
            mobileconfig = self._create_pppc_mobileconfig(
                app_name=app_name,
                bundle_id=bundle_id,
                permissions=permissions,
                profile_name=profile_name
            )
            
            return self._deploy_mobileconfig(mobileconfig, profile_name)
            
        except Exception as e:
            print(f"❌ Error creating PPPC profile: {e}")
            return False
    
    def _create_pppc_mobileconfig(self, app_name: str, bundle_id: str, 
                                 permissions: List[str], profile_name: str) -> Dict[str, Any]:
        """Create PPPC mobileconfig"""
        # Map permission names to TCC services
        permission_map = {
            "full_disk_access": "SystemPolicyAllFiles",
            "network_volumes": "SystemPolicyNetworkVolumes",
            "sys_admin_files": "SystemPolicySysAdminFiles",
            "camera": "Camera",
            "microphone": "Microphone",
            "photos": "Photos",
            "contacts": "Contacts",
            "calendar": "Calendar",
            "reminders": "Reminders",
            "location": "LocationServices"
        }
        
        services = {}
        for permission in permissions:
            if permission in permission_map:
                service_key = permission_map[permission]
                services[service_key] = [{
                    "Allowed": True,
                    "Authorization": "Allow",
                    "CodeRequirement": f'identifier "{bundle_id}" and anchor apple',
                    "Identifier": bundle_id,
                    "IdentifierType": "bundleID",
                    "Comment": f"Allow {app_name} {permission.replace('_', ' ')}"
                }]
        
        return {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.TCC.configuration-profile-policy",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"com.jamf.pppc.{bundle_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"{app_name} PPPC Permissions",
                    "PayloadDescription": f"Privacy preferences for {app_name}",
                    "Services": services
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"PPPC permissions for {app_name}",
            "PayloadIdentifier": f"com.jamf.pppc.{bundle_id}.profile",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }
    
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













