#!/usr/bin/env python3
"""
App Installation Service
Handles application installation via Installomator and custom policies
"""

from typing import Optional, Dict, Any
from core.auth.login_types import AuthInterface


class AppInstallationService:
    """Service for application installation"""
    
    def __init__(self, auth: Optional[AuthInterface] = None):
        self.auth = auth
    
    def install_with_installomator(self, app_name: str, label: str = None, 
                                 category: str = "Productivity") -> bool:
        """Install an application using Installomator"""
        if not label:
            label = app_name.lower().replace(" ", "")
        
        print(f"📱 Installing app with Installomator: {app_name}")
        
        try:
            # Create Installomator policy
            policy_data = self._create_installomator_policy(app_name, label, category)
            
            if not self.auth:
                print("❌ Jamf Pro connection required for policy creation")
                return False
            
            # Convert to XML and deploy
            xml_data = self._dict_to_xml(policy_data, "policy")
            
            response = self.auth.api_request(
                "POST",
                "/JSSResource/policies/id/0",
                data=xml_data,
                content_type="xml"
            )
            
            if response and "policy" in response:
                print(f"✅ Successfully created Installomator policy: {app_name}")
                return True
            else:
                print(f"❌ Failed to create Installomator policy: {app_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating Installomator policy: {e}")
            return False
    
    def _create_installomator_policy(self, app_name: str, label: str, 
                                   category: str) -> Dict[str, Any]:
        """Create Installomator policy data"""
        return {
            "policy": {
                "general": {
                    "name": f"Install {app_name} - Latest Version",
                    "enabled": True,
                    "trigger": "EVENT",
                    "frequency": "Ongoing",
                    "retry_attempts": 3,
                    "notify_on_each_failed_retry": True,
                    "category": {"name": category},
                    "description": f"Installomator policy for {app_name} installation"
                },
                "scope": {
                    "all_computers": True,
                    "all_jss_users": False,
                    "computer_groups": [],
                    "exclusions": {
                        "computer_groups": []
                    }
                },
                "scripts": [
                    {
                        "id": 196,  # Installomator script ID
                        "priority": "Before",
                        "parameter4": label,
                        "parameter5": app_name
                    }
                ],
                "packages": [],
                "maintenance": {
                    "recon": False,
                    "reset_catalog": False,
                    "install_cached_packages": False,
                    "cache_packages": False,
                    "fix_permissions": False,
                    "reboot": False
                },
                "files_processes": {
                    "delete_files": False,
                    "delete_processes": False,
                    "update_ldap": False,
                    "search_by_path": "",
                    "delete_file": False,
                    "locate_file": "",
                    "run_command": ""
                },
                "user_interaction": {
                    "message_start": "",
                    "message_finish": "",
                    "allow_user_to_defer": False,
                    "allow_deferral_until_utc": "",
                    "allow_deferral_for": 0,
                    "maximum_deferral": 0
                }
            }
        }
    
    def _dict_to_xml(self, data: Dict[str, Any], root_name: str) -> str:
        """Convert dictionary to XML format (simplified)"""
        xml_parts = [f"<{root_name}>"]
        
        def dict_to_xml_recursive(obj, indent=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        xml_parts.append(f"{indent}<{key}>")
                        dict_to_xml_recursive(value, indent + "  ")
                        xml_parts.append(f"{indent}</{key}>")
                    else:
                        xml_parts.append(f"{indent}<{key}>{value}</{key}>")
            elif isinstance(obj, list):
                for item in obj:
                    dict_to_xml_recursive(item, indent)
        
        dict_to_xml_recursive(data, "  ")
        xml_parts.append(f"</{root_name}>")
        
        return "\n".join(xml_parts)













