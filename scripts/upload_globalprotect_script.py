#!/usr/bin/env python3
"""
Upload GlobalProtect Download Script to Jamf Pro Production
Uses jpapi authentication to upload the script to Jamf Pro
"""

import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from argparse import Namespace

# Add src to path (like other scripts do)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli.base.command import BaseCommand
from cli.commands.create.services.xml_converter import XMLConverterService


def upload_script_to_jamf(script_path: Path, script_name: str = None, 
                          category: str = "No Category Assigned",
                          info: str = "", notes: str = "",
                          priority: str = "Before",
                          environment: str = "production") -> bool:
    """
    Upload a script file to Jamf Pro
    
    Args:
        script_path: Path to the script file
        script_name: Name for the script in Jamf Pro (defaults to filename)
        category: Script category
        info: Script info/description
        notes: Script notes
        priority: Script priority (Before, After, At Reboot)
        environment: Environment (production or sandbox)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read script file
        if not script_path.exists():
            print(f"❌ Script file not found: {script_path}")
            return False
        
        with open(script_path, 'r') as f:
            script_contents = f.read()
        
        # Use filename as name if not provided
        if not script_name:
            script_name = script_path.stem.replace('_', ' ').title()
        
        print(f"📤 Uploading script to Jamf Pro ({environment})...")
        print(f"   Name: {script_name}")
        print(f"   File: {script_path.name}")
        print(f"   Size: {len(script_contents)} bytes")
        print(f"   Category: {category}")
        
        # Initialize authentication using BaseCommand
        cmd = BaseCommand(name="upload-script", description="Upload script to Jamf Pro")
        cmd.environment = environment
        
        # Check authentication
        mock_args = Namespace(env=environment)
        if not cmd.check_auth(mock_args):
            print(f"❌ Failed to authenticate to {environment}")
            return False
        
        auth = cmd.auth
        
        # Build script data structure (inner dict only, root tag added by converter)
        script_data = {
            "name": script_name,
            "category": category,
            "info": info or f"GlobalProtect VPN client downloader and installer",
            "notes": notes or "Downloads and installs GlobalProtect VPN client from Okta-authenticated endpoint",
            "priority": priority,
            "parameter4": {
                "name": "Text Field",
                "value": ""
            },
            "parameter5": {
                "name": "Text Field",
                "value": ""
            },
            "parameter6": {
                "name": "Text Field",
                "value": ""
            },
            "parameter7": {
                "name": "Text Field",
                "value": ""
            },
            "parameter8": {
                "name": "Text Field",
                "value": ""
            },
            "parameter9": {
                "name": "Text Field",
                "value": ""
            },
            "parameter10": {
                "name": "Text Field",
                "value": ""
            },
            "parameter11": {
                "name": "Text Field",
                "value": ""
            },
            "os_requirements": "",
            "script_contents": script_contents
        }
        
        # Convert to XML using the proper converter service
        xml_converter = XMLConverterService()
        xml_data = xml_converter.dict_to_xml(script_data, "script")
        
        # Check if script already exists
        print(f"\n🔍 Checking if script already exists...")
        try:
            scripts_response = auth.api_request("GET", "/JSSResource/scripts")
            existing_script_id = None
            
            # Handle different response structures
            scripts_list = []
            if isinstance(scripts_response, list):
                scripts_list = scripts_response
            elif isinstance(scripts_response, dict):
                if "scripts" in scripts_response:
                    script_data = scripts_response["scripts"]
                    if isinstance(script_data, dict) and "script" in script_data:
                        scripts_list = script_data["script"]
                        if not isinstance(scripts_list, list):
                            scripts_list = [scripts_list]
                    elif isinstance(script_data, list):
                        scripts_list = script_data
            
            for script in scripts_list:
                if isinstance(script, dict) and script.get("name") == script_name:
                    existing_script_id = script.get("id")
                    break
            
            if existing_script_id:
                print(f"   ⚠️  Script '{script_name}' already exists (ID: {existing_script_id})")
                print(f"   🔄 Updating existing script...")
                
                # Update existing script
                response = auth.api_request(
                    "PUT",
                    f"/JSSResource/scripts/id/{existing_script_id}",
                    data=xml_data,
                    content_type="xml"
                )
                script_id = existing_script_id
                action = "updated"
            else:
                # Create new script
                print(f"   ✅ Script name is unique, creating new script...")
                print(f"\n🚀 Creating script in Jamf Pro...")
                try:
                    response = auth.api_request(
                        "POST",
                        "/JSSResource/scripts/id/0",
                        data=xml_data,
                        content_type="xml"
                    )
                    action = "created"
                    
                    # Extract script ID from response
                    script_id = None
                    if response:
                        if isinstance(response, dict) and "script" in response:
                            created_script = response["script"]
                            script_id = created_script.get("id")
                        elif isinstance(response, dict) and "raw_response" in response:
                            # Parse raw XML response
                            try:
                                root = ET.fromstring(response["raw_response"])
                                id_elem = root.find("id")
                                if id_elem is not None:
                                    script_id = id_elem.text
                            except:
                                pass
                except Exception as create_error:
                    # If creation fails with duplicate error, try to find and update
                    error_str = str(create_error)
                    if "Duplicate name" in error_str or "409" in error_str:
                        print(f"   ⚠️  Script with this name already exists, searching for it...")
                        # Search by name to find the ID
                        for script in scripts_list:
                            if isinstance(script, dict) and script.get("name") == script_name:
                                existing_script_id = script.get("id")
                                print(f"   🔄 Found existing script (ID: {existing_script_id}), updating...")
                                response = auth.api_request(
                                    "PUT",
                                    f"/JSSResource/scripts/id/{existing_script_id}",
                                    data=xml_data,
                                    content_type="xml"
                                )
                                script_id = existing_script_id
                                action = "updated"
                                break
                        else:
                            raise create_error
                    else:
                        raise create_error
                
        except Exception as check_error:
            # If check fails, try to create anyway and handle duplicate
            error_str = str(check_error)
            if "Duplicate name" in error_str or "409" in error_str:
                print(f"   ⚠️  Script already exists, attempting to find and update...")
                # Try to get the script list and find by name
                try:
                    scripts_response = auth.api_request("GET", "/JSSResource/scripts")
                    scripts_list = []
                    if isinstance(scripts_response, list):
                        scripts_list = scripts_response
                    elif isinstance(scripts_response, dict) and "scripts" in scripts_response:
                        script_data = scripts_response["scripts"]
                        if isinstance(script_data, dict) and "script" in script_data:
                            scripts_list = script_data["script"]
                            if not isinstance(scripts_list, list):
                                scripts_list = [scripts_list]
                    
                    for script in scripts_list:
                        if isinstance(script, dict) and script.get("name") == script_name:
                            existing_script_id = script.get("id")
                            print(f"   🔄 Found existing script (ID: {existing_script_id}), updating...")
                            response = auth.api_request(
                                "PUT",
                                f"/JSSResource/scripts/id/{existing_script_id}",
                                data=xml_data,
                                content_type="xml"
                            )
                            script_id = existing_script_id
                            action = "updated"
                            break
                    else:
                        raise check_error
                except:
                    raise check_error
            else:
                print(f"   ⚠️  Could not check for existing script: {check_error}")
                print(f"   🚀 Attempting to create script...")
                response = auth.api_request(
                    "POST",
                    "/JSSResource/scripts/id/0",
                    data=xml_data,
                    content_type="xml"
                )
                action = "created"
                script_id = None
        
        # Handle response
        if script_id or (response and not isinstance(response, Exception)):
            if not script_id:
                # Try to extract ID from response
                if isinstance(response, dict) and "script" in response:
                    script_id = response["script"].get("id")
                elif isinstance(response, dict) and "raw_response" in response:
                    try:
                        root = ET.fromstring(response["raw_response"])
                        id_elem = root.find("id")
                        if id_elem is not None:
                            script_id = id_elem.text
                    except:
                        pass
            
            if script_id:
                print(f"\n✅ Script {action} successfully!")
                print(f"   ID: {script_id}")
                print(f"   Name: {script_name}")
                print(f"   Category: {category}")
                print(f"\n📋 Next Steps:")
                print(f"   1. Review the script in Jamf Pro: Scripts > {script_name}")
                print(f"   2. Create a policy to run this script")
                print(f"   3. Test the script in a pilot group")
                return True
        
        # If we get here, something went wrong
        print(f"❌ Failed to {action} script")
        if response:
            print(f"   Response: {response}")
        return False
            
    except Exception as e:
        print(f"❌ Error uploading script: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Upload GlobalProtect download script to Jamf Pro production"
    )
    parser.add_argument(
        "--script-path",
        type=Path,
        default=Path(__file__).parent / "download_globalprotect.sh",
        help="Path to script file (default: scripts/download_globalprotect.sh)"
    )
    parser.add_argument(
        "--name",
        default="GlobalProtect Downloader and Installer",
        help="Script name in Jamf Pro"
    )
    parser.add_argument(
        "--category",
        default="No Category Assigned",
        help="Script category (default: No Category Assigned)"
    )
    parser.add_argument(
        "--info",
        default="Downloads and installs GlobalProtect VPN client from Okta-authenticated endpoint",
        help="Script info/description"
    )
    parser.add_argument(
        "--notes",
        default="Automated GlobalProtect installer with Okta authentication. Handles credential management via Keychain and automatic installation.",
        help="Script notes"
    )
    parser.add_argument(
        "--priority",
        default="Before",
        choices=["Before", "After", "At Reboot"],
        help="Script priority (default: Before)"
    )
    parser.add_argument(
        "--env",
        default="production",
        choices=["production", "sandbox"],
        help="Environment (default: production)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually uploading"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt (use with caution)"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN - Would upload script with:")
        print(f"   Name: {args.name}")
        print(f"   Category: {args.category}")
        print(f"   File: {args.script_path}")
        print(f"   Environment: {args.env}")
        return 0
    
    # Check production safety
    if args.env == "production" and not args.yes:
        response = input(f"\n⚠️  You are about to upload to PRODUCTION. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Upload cancelled")
            return 1
    
    success = upload_script_to_jamf(
        script_path=args.script_path,
        script_name=args.name,
        category=args.category,
        info=args.info,
        notes=args.notes,
        priority=args.priority,
        environment=args.env
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

