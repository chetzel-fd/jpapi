#!/usr/bin/env python3
"""
Policy Management Service
Handles software installation policy creation and deployment
"""

from typing import Optional, Dict, Any
from core.auth.login_types import AuthInterface


class PolicyManagementService:
    """Service for policy management operations"""
    
    def __init__(self, auth: Optional[AuthInterface] = None):
        self.auth = auth
    
    def create_policy(self, app_name: str, package_id: int = None, 
                     script_id: int = None, policy_name: str = None) -> bool:
        """Create a software installation policy"""
        if not policy_name:
            policy_name = f"Install {app_name}"
        
        print(f"📦 Creating software installation policy: {app_name}")
        
        if not self.auth:
            print("❌ Jamf Pro connection required for policy creation")
            return False
        
        try:
            policy_data = self._create_policy_data(
                app_name=app_name,
                package_id=package_id,
                script_id=script_id,
                policy_name=policy_name
            )
            
            # Convert to XML
            xml_data = self._dict_to_xml(policy_data, "policy")
            
            # Create policy in Jamf Pro
            response = self.auth.api_request(
                "POST",
                "/JSSResource/policies/id/0",
                data=xml_data,
                content_type="xml"
            )
            
            if response and "policy" in response:
                print(f"✅ Successfully created policy: {policy_name}")
                return True
            else:
                print(f"❌ Failed to create policy: {policy_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating policy: {e}")
            return False
    
    def _create_policy_data(self, app_name: str, package_id: int = None, 
                          script_id: int = None, policy_name: str = None) -> Dict[str, Any]:
        """Create policy data structure"""
        policy_data = {
            "policy": {
                "general": {
                    "name": policy_name,
                    "enabled": True,
                    "trigger": "EVENT",
                    "frequency": "Ongoing",
                    "retry_attempts": 3,
                    "notify_on_each_failed_retry": True,
                    "category": {"name": "Software Installation"},
                    "description": f"Installation policy for {app_name}"
                },
                "scope": {
                    "all_computers": True,
                    "all_jss_users": False
                },
                "scripts": [],
                "packages": []
            }
        }
        
        # Add package if provided
        if package_id:
            policy_data["policy"]["packages"].append({
                "id": package_id,
                "action": "Install"
            })
        
        # Add script if provided
        if script_id:
            policy_data["policy"]["scripts"].append({
                "id": script_id,
                "priority": "Before"
            })
        
        return policy_data
    
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













