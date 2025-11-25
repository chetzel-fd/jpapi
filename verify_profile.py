#!/usr/bin/env python3
"""Quick script to verify profile exists and show details"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.auth.login_factory import get_best_auth

def verify_profile(profile_id: int, env: str = "sandbox"):
    """Verify profile exists and show details"""
    auth = get_best_auth(environment=env)
    
    print(f"🔍 Checking Profile ID {profile_id} in {env}...")
    
    try:
        response = auth.api_request(
            "GET",
            f"/JSSResource/osxconfigurationprofiles/id/{profile_id}"
        )
        
        if response and "os_x_configuration_profile" in response:
            profile = response["os_x_configuration_profile"]
            general = profile.get("general", {})
            
            print(f"\n✅ Profile Found!")
            print(f"   ID: {profile_id}")
            print(f"   Name: {general.get('name', 'N/A')}")
            print(f"   Description: {general.get('description', 'N/A')}")
            print(f"   Distribution Method: {general.get('distribution_method', 'N/A')}")
            print(f"   Level: {general.get('level', 'N/A')}")
            print(f"   Created: {general.get('site', {}).get('id', 'N/A')}")
            
            # Check scope
            scope = profile.get("scope", {})
            if scope.get("all_computers"):
                print(f"   Scope: All Computers")
            else:
                print(f"   Scope: Limited")
            
            # Count payloads
            payloads = general.get("payloads", [])
            if isinstance(payloads, str):
                # It's XML-escaped string
                payload_count = payloads.count("<dict>")
            else:
                payload_count = len(payloads) if isinstance(payloads, list) else 1
            
            print(f"   Payloads: {payload_count}")
            print(f"\n🌐 View in Jamf Pro:")
            print(f"   https://{auth.server}/osXConfigurationProfiles.html?id={profile_id}")
            
            return True
        else:
            print(f"❌ Profile {profile_id} not found or invalid response")
            return False
            
    except Exception as e:
        print(f"❌ Error checking profile: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify config profile exists")
    parser.add_argument("--profile-id", type=int, required=True, help="Profile ID to check")
    parser.add_argument("--env", default="sandbox", choices=["sandbox", "production"], help="Environment")
    
    args = parser.parse_args()
    verify_profile(args.profile_id, args.env)
