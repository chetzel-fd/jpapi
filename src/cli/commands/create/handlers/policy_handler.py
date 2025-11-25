#!/usr/bin/env python3
"""
Policy Create Handler - SOLID SRP
Handles policy creation operations
"""

from argparse import Namespace
from .base_handler import BaseCreateHandler


class PolicyCreateHandler(BaseCreateHandler):
    """Handler for creating policies"""
    
    def can_handle(self, object_type: str) -> bool:
        """Check if this handler can handle the given object type"""
        return object_type in ["policy", "pol", "policies"]
    
    def create(self, args: Namespace) -> int:
        """Create a new policy"""
        try:
            # Add signature to name
            signed_name = self.apply_signature(args.name)
            
            # Create comprehensive summary for production confirmation
            if self.production_checker and self.production_checker.is_production_environment():
                changes_summary = f"""
Policy Creation Summary:
  • Name: {signed_name}
  • Enabled: {getattr(args, 'enabled', False)}
  • Frequency: {getattr(args, 'frequency', 'Ongoing')}
  • Trigger: {getattr(args, 'trigger', 'Check-in')}
  • Category: {getattr(args, 'category', 'None')}
  • Scope: No computers (null scope)
  • Scripts: None
  • Packages: None
  • Impact: Will create a new policy in PRODUCTION
"""
                
                if not self.production_checker.require_production_confirmation(
                    "Create Policy", f"Creating policy: {signed_name}", changes_summary, args
                ):
                    return 1
            
            print(f"📋 Creating Policy: {signed_name}")
            
            # Prepare policy data
            enabled = getattr(args, "enabled", False)
            frequency = getattr(args, "frequency", "Ongoing")
            trigger = getattr(args, "trigger", "Check-in")
            
            policy_data = {
                "policy": {
                    "general": {
                        "name": signed_name,
                        "enabled": enabled,
                        "frequency": frequency,
                        "trigger_checkin": trigger == "Check-in",
                        "trigger_startup": trigger == "Startup",
                        "trigger_login": trigger == "Login",
                        "trigger_logout": trigger == "Logout",
                    },
                    "scope": {
                        "all_computers": False,
                        "computers": [],
                        "computer_groups": [],
                        "buildings": [],
                        "departments": [],
                        "limit_to_users": {"user_groups": []},
                        "limitations": {
                            "users": [],
                            "user_groups": [],
                            "network_segments": [],
                            "ibeacons": [],
                        },
                        "exclusions": {
                            "computers": [],
                            "computer_groups": [],
                            "buildings": [],
                            "departments": [],
                            "users": [],
                            "user_groups": [],
                            "network_segments": [],
                            "ibeacons": [],
                        },
                    },
                }
            }
            
            # Add category if specified
            if hasattr(args, "category") and args.category:
                policy_data["policy"]["general"]["category"] = {"name": args.category}
            
            # Create policy via API using XML format
            xml_data = self.xml_converter.dict_to_xml(policy_data["policy"], "policy")
            response = self.auth.api_request(
                "POST", "/JSSResource/policies/id/0", data=xml_data, content_type="xml"
            )
            
            if response and "policy" in response:
                created_policy = response["policy"]
                print(f"✅ Policy created successfully!")
                print(f"   ID: {created_policy.get('id', 'Unknown')}")
                print(f"   Name: {created_policy.get('name', signed_name)}")
                print(f"   Enabled: {enabled}")
                print(f"   Frequency: {frequency}")
                print(f"   Trigger: {trigger}")
                if hasattr(args, "category") and args.category:
                    print(f"   Category: {args.category}")
                return 0
            else:
                print("❌ Failed to create policy")
                return 1
                
        except Exception as e:
            return self.handle_api_error(e)

