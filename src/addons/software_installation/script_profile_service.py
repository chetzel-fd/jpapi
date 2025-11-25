#!/usr/bin/env python3
"""
Script Profile Service
Converts Jamf Pro scripts into config profiles with script payloads
"""

import uuid
import base64
import plistlib
from typing import Optional, Dict, Any
from core.auth.login_types import AuthInterface


class ScriptProfileService:
    """Service for converting scripts to config profiles"""
    
    def __init__(self, auth: Optional[AuthInterface] = None):
        self.auth = auth
    
    def download_script(self, script_id: int) -> Optional[Dict[str, Any]]:
        """Download a script from Jamf Pro"""
        if not self.auth:
            print("❌ Jamf Pro connection required for script download")
            return None
        
        try:
            print(f"📥 Downloading script {script_id} from Jamf Pro...")
            
            response = self.auth.api_request(
                "GET",
                f"/JSSResource/scripts/id/{script_id}"
            )
            
            if 'script' in response:
                script_data = response['script']
                print(f"✅ Successfully downloaded script: {script_data.get('name', 'Unknown')}")
                return script_data
            else:
                print(f"❌ Script {script_id} not found")
                return None
                
        except Exception as e:
            print(f"❌ Error downloading script {script_id}: {e}")
            return None
    
    def create_script_profile(self, script_data: Dict[str, Any], 
                            profile_name: str = None,
                            description: str = None,
                            auto_execute: bool = True,
                            execution_trigger: str = "once") -> Dict[str, Any]:
        """
        Create a config profile from script data that installs and executes the script
        
        Args:
            script_data: Script data from Jamf Pro
            profile_name: Custom profile name
            description: Profile description
            auto_execute: If True, creates LaunchDaemon to execute script automatically
            execution_trigger: "once" (run once) or "always" (run on every boot/login)
        """
        
        script_name = script_data.get('name', 'Unknown Script')
        script_id = script_data.get('id', 'unknown')
        script_content = script_data.get('script_contents', '')
        
        if not profile_name:
            profile_name = f"{script_name} Script Profile"
        
        if not description:
            description = f"Config profile for script: {script_name}"
        
        # Sanitize script name for file paths
        safe_script_name = script_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        safe_script_name = ''.join(c for c in safe_script_name if c.isalnum() or c in ('_', '-'))
        
        # Determine script extension from content or default to .sh
        script_extension = ".sh"
        shebang = ""
        if script_content.startswith("#!/"):
            first_line = script_content.split('\n')[0]
            shebang = first_line + "\n"
            if "python" in first_line.lower():
                script_extension = ".py"
            elif "ruby" in first_line.lower():
                script_extension = ".rb"
            elif "perl" in first_line.lower():
                script_extension = ".pl"
        
        # Script will be installed here
        script_path = f"/usr/local/bin/{safe_script_name}{script_extension}"
        
        # Create file payload that installs the script
        script_encoded = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
        
        file_payload = {
            "PayloadType": "com.apple.system.extension.file",
            "PayloadVersion": 1,
            "PayloadIdentifier": f"com.jamf.script.file.{script_id}",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadEnabled": True,
            "PayloadDisplayName": f"{script_name} Script File",
            "PayloadDescription": f"Installs script file: {script_name}",
            "PayloadContent": {
                "FilePath": script_path,
                "Payload": script_encoded
            }
        }
        
        payloads = [file_payload]
        
        # Create LaunchDaemon payload to execute the script
        if auto_execute:
            launchd_payloads = self._create_launchd_payload(
                script_id=script_id,
                script_name=script_name,
                script_path=script_path,
                execution_trigger=execution_trigger
            )
            payloads.extend(launchd_payloads)
        
        # Create full mobileconfig
        mobileconfig = {
            "PayloadContent": payloads,
            "PayloadDisplayName": profile_name,
            "PayloadDescription": description,
            "PayloadIdentifier": f"com.jamf.script.{script_id}.profile",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }
        
        return mobileconfig
    
    def _create_launchd_payload(self, script_id: int, script_name: str, 
                              script_path: str, execution_trigger: str = "once") -> Dict[str, Any]:
        """
        Create a LaunchDaemon payload that executes the script
        
        Args:
            script_id: Script ID
            script_name: Script name
            script_path: Path where script is installed
            execution_trigger: "once" or "always"
        """
        safe_script_name = script_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        safe_script_name = ''.join(c for c in safe_script_name if c.isalnum() or c in ('_', '-'))
        
        plist_label = f"com.jamf.script.{script_id}.{safe_script_name}"
        
        # Create LaunchDaemon plist content
        if execution_trigger == "once":
            # Run once after profile installation
            plist_content = {
                "Label": plist_label,
                "ProgramArguments": ["/bin/bash", script_path],
                "RunAtLoad": True,
                "StartInterval": 0,
                "StandardOutPath": f"/var/log/{safe_script_name}.log",
                "StandardErrorPath": f"/var/log/{safe_script_name}.error.log"
            }
        else:  # "always"
            # Run on every boot/login
            plist_content = {
                "Label": plist_label,
                "ProgramArguments": ["/bin/bash", script_path],
                "RunAtLoad": True,
                "StandardOutPath": f"/var/log/{safe_script_name}.log",
                "StandardErrorPath": f"/var/log/{safe_script_name}.error.log"
            }
        
        # Encode plist as base64
        import plistlib
        plist_bytes = plistlib.dumps(plist_content)
        plist_encoded = base64.b64encode(plist_bytes).decode('utf-8')
        
        # LaunchDaemon path
        launchd_path = f"/Library/LaunchDaemons/{plist_label}.plist"
        
        # Create LaunchDaemon file payload
        launchd_file_payload = {
            "PayloadType": "com.apple.system.extension.file",
            "PayloadVersion": 1,
            "PayloadIdentifier": f"com.jamf.script.launchd.{script_id}",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadEnabled": True,
            "PayloadDisplayName": f"{script_name} LaunchDaemon",
            "PayloadDescription": f"LaunchDaemon to execute {script_name}",
            "PayloadContent": {
                "FilePath": launchd_path,
                "Payload": plist_encoded
            }
        }
        
        # Create LaunchDaemon control payload (loads the daemon)
        # Note: This requires proper MDM framework support
        launchd_control_payload = {
            "PayloadType": "com.apple.system.extension.launchd",
            "PayloadVersion": 1,
            "PayloadIdentifier": f"com.jamf.script.launchd.control.{script_id}",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadEnabled": True,
            "PayloadDisplayName": f"{script_name} LaunchDaemon Control",
            "PayloadDescription": f"Control LaunchDaemon for {script_name}",
            "PayloadContent": {
                "LaunchDaemon": {
                    "Label": plist_label,
                    "FilePath": launchd_path
                }
            }
        }
        
        # For now, we'll use a simpler approach: create a wrapper script that
        # makes the script executable and runs it, then loads it as a LaunchDaemon
        # Actually, let's use a different approach - embed the execution in a script that runs at install
        
        # Create an execution script that runs the main script
        execution_script = f"""#!/bin/bash
# Auto-generated execution wrapper for {script_name}
# Script ID: {script_id}

# Make script executable
chmod +x "{script_path}"

# Execute the script
"{script_path}"

# If this is a one-time execution, we can remove this LaunchDaemon
if [ "$(echo "{execution_trigger}")" = "once" ]; then
    launchctl unload "{launchd_path}" 2>/dev/null || true
    rm -f "{launchd_path}"
fi
"""
        
        execution_script_encoded = base64.b64encode(execution_script.encode('utf-8')).decode('utf-8')
        execution_script_path = f"/usr/local/bin/{safe_script_name}_executor.sh"
        
        # Create execution script file payload
        execution_payload = {
            "PayloadType": "com.apple.system.extension.file",
            "PayloadVersion": 1,
            "PayloadIdentifier": f"com.jamf.script.executor.{script_id}",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadEnabled": True,
            "PayloadDisplayName": f"{script_name} Executor",
            "PayloadDescription": f"Execution wrapper for {script_name}",
            "PayloadContent": {
                "FilePath": execution_script_path,
                "Payload": execution_script_encoded
            }
        }
        
        # Update LaunchDaemon to run the executor script
        plist_content_executor = {
            "Label": plist_label,
            "ProgramArguments": ["/bin/bash", execution_script_path],
            "RunAtLoad": True,
            "StandardOutPath": f"/var/log/{safe_script_name}.log",
            "StandardErrorPath": f"/var/log/{safe_script_name}.error.log"
        }
        
        plist_bytes_executor = plistlib.dumps(plist_content_executor)
        plist_encoded_executor = base64.b64encode(plist_bytes_executor).decode('utf-8')
        
        launchd_file_payload["PayloadContent"]["Payload"] = plist_encoded_executor
        
        # Return both payloads: executor script and LaunchDaemon plist
        return [execution_payload, launchd_file_payload]
    
    def download_and_create_profile(self, script_id: int, 
                                  profile_name: str = None,
                                  description: str = None) -> Optional[Dict[str, Any]]:
        """Download script and create config profile in one step"""
        
        # Download script
        script_data = self.download_script(script_id)
        if not script_data:
            return None
        
        # Create profile
        profile = self.create_script_profile(
            script_data=script_data,
            profile_name=profile_name,
            description=description
        )
        
        return profile
    
    def deploy_script_profile(self, script_id: int, 
                            profile_name: str = None,
                            description: str = None,
                            deploy: bool = True,
                            create_policy: bool = False,
                            auto_execute: bool = True,
                            execution_trigger: str = "once") -> bool:
        """
        Download script, create profile/policy, and optionally deploy to Jamf Pro
        
        Note: macOS config profiles cannot execute scripts directly.
        This creates a Jamf Pro policy that runs the script, which is the standard approach.
        Optionally also creates a file payload profile to install the script file.
        """
        
        try:
            # Download script
            script_data = self.download_script(script_id)
            if not script_data:
                return False
            
            script_name = script_data.get('name', f'Script {script_id}')
            
            success = True
            
            # Create and deploy policy (standard way to run scripts in Jamf)
            if create_policy and deploy:
                policy_success = self._create_script_policy(script_id, script_data, profile_name)
                success = success and policy_success
            
            # Create config profile with file payload and execution (installs and executes script)
            mobileconfig = self.create_script_profile(
                script_data=script_data,
                profile_name=profile_name or f"{script_name} Script Profile",
                description=description or f"Installs and executes script: {script_name}",
                auto_execute=auto_execute,
                execution_trigger=execution_trigger
            )
            
            if deploy:
                # Get environment from auth if available
                env = getattr(self.auth, 'environment', None) if self.auth else None
                profile_success = self._deploy_mobileconfig(
                    mobileconfig, 
                    profile_name or f"{script_name} Script Profile",
                    environment=env
                )
                success = success and profile_success
            else:
                profile_success = self._save_mobileconfig_locally(
                    mobileconfig,
                    profile_name or f"{script_name} Script Profile"
                )
                success = success and profile_success
            
            return success
                
        except Exception as e:
            print(f"❌ Error creating script profile: {e}")
            return False
    
    def _create_script_policy(self, script_id: int, script_data: Dict[str, Any], 
                            policy_name: str = None) -> bool:
        """Create a Jamf Pro policy that runs the script"""
        try:
            script_name = script_data.get('name', f'Script {script_id}')
            
            if not policy_name:
                policy_name = f"Run {script_name}"
            
            print(f"📦 Creating policy to run script: {script_name}")
            
            policy_data = {
                "policy": {
                    "general": {
                        "name": policy_name,
                        "enabled": True,
                        "trigger": "EVENT",
                        "frequency": "Ongoing",
                        "retry_attempts": 3,
                        "notify_on_each_failed_retry": False,
                        "category": {"name": "Script Execution"},
                        "description": f"Policy to execute script: {script_name}"
                    },
                    "scope": {
                        "all_computers": True,
                        "all_jss_users": False
                    },
                    "scripts": [
                        {
                            "id": script_id,
                            "priority": "Before"
                        }
                    ],
                    "packages": []
                }
            }
            
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
            print(f"❌ Error creating script policy: {e}")
            return False
    
    def _deploy_mobileconfig(self, mobileconfig: Dict[str, Any], profile_name: str, 
                            environment: str = None) -> bool:
        """
        Deploy mobileconfig to Jamf Pro with SAFE DEFAULTS
        
        SAFETY MEASURES:
        - Scope: NO computers by default (all_computers: False)
        - Requires manual scoping after creation
        - Requires confirmation for production environments
        """
        try:
            if not self.auth:
                print("⚠️  No Jamf Pro connection, saving locally instead")
                return self._save_mobileconfig_locally(mobileconfig, profile_name)
            
            # Determine environment for confirmation
            if not environment:
                # Try to get environment from auth if available
                env = getattr(self.auth, 'environment', 'sandbox')
            else:
                env = environment
            
            # Verify payloads exist
            payload_count = len(mobileconfig.get("PayloadContent", []))
            if payload_count == 0:
                print("⚠️  WARNING: Profile has no payloads - will be blank!")
                print("   Proceeding anyway, but profile will need payloads added manually")
            
            # Show deployment summary
            print(f"\n📋 Profile Deployment Summary:")
            print(f"   Name: {profile_name}")
            print(f"   Description: {mobileconfig.get('PayloadDescription', 'None')}")
            print(f"   Payloads: {payload_count}")
            print(f"   Scope: NO computers (null scope) - SAFE DEFAULT")
            print(f"   Environment: {env}")
            print(f"   Risk Level: {'HIGH' if env == 'production' else 'MEDIUM'}")
            print(f"   ⚠️  Profile will be created with NO SCOPE")
            print(f"   ⚠️  You must manually scope it after creation\n")
            
            # Require confirmation ONLY for production (dev/sandbox: no confirmation)
            if env == "production":
                print("🚨 PRODUCTION ENVIRONMENT DETECTED 🚨")
                print("=" * 60)
                response = input("Type 'yes' to confirm deployment to PRODUCTION: ")
                if response.lower() != "yes":
                    print("❌ Deployment cancelled")
                    return False
            # No confirmation needed for dev/sandbox (automated workflows)
            
            print(f"\n🚀 Deploying profile to Jamf Pro: {profile_name}")
            
            # Use CreateCommand methods for XML conversion (leverages existing tested code)
            from cli.commands.create_command import CreateCommand
            create_cmd = CreateCommand()
            
            # Convert mobileconfig to XML format using CreateCommand method
            # CreateCommand uses the full mobileconfig structure - Jamf Pro extracts PayloadContent internally
            payloads_xml = create_cmd._convert_mobileconfig_to_xml(mobileconfig)
            
            # Verify PayloadContent exists
            payload_count = len(mobileconfig.get("PayloadContent", []))
            if payload_count == 0:
                print("⚠️  WARNING: Mobileconfig has no PayloadContent - profile will be blank!")
            else:
                print(f"✅ Mobileconfig contains {payload_count} payloads")
            
            # SAFE SCOPE: all_computers = False (null scope, like CreateCommand)
            profile_data = {
                "os_x_configuration_profile": {
                    "general": {
                        "name": profile_name,
                        "description": mobileconfig.get("PayloadDescription", ""),
                        "distribution_method": "Install Automatically",
                        "user_removable": False,
                        "level": "System",
                        "redeploy_on_update": "Newly Assigned",
                        "payloads": payloads_xml
                    },
                    "scope": {
                        "all_computers": False,  # SAFE DEFAULT - null scope
                        "computers": [],
                        "computer_groups": [],
                        "buildings": [],
                        "departments": [],
                        "limitations": {
                            "users": [],
                            "user_groups": [],
                            "network_limitations": {
                                "minimum_network_connection": "No Minimum",
                                "any_ip_address": True,
                                "network_segments": [],
                            },
                        },
                        "exclusions": {
                            "computers": [],
                            "computer_groups": [],
                            "buildings": [],
                            "departments": [],
                            "users": [],
                            "user_groups": [],
                        },
                    }
                }
            }
            
            # Extract inner profile data and convert to XML (like CreateCommand does)
            profile_key = list(profile_data.keys())[0]
            inner_profile_data = profile_data[profile_key]
            xml_data = create_cmd.dict_to_xml(inner_profile_data, profile_key)
            
            # Create profile in Jamf Pro
            try:
                response = self.auth.api_request(
                    "POST",
                    "/JSSResource/osxconfigurationprofiles/id/0",
                    data=xml_data,
                    content_type="xml"
                )
                
                # Check for success - response can be dict with os_x_configuration_profile key
                # or raw_response with XML containing <os_x_configuration_profile><id>
                success = False
                if isinstance(response, dict):
                    if "os_x_configuration_profile" in response or "mobile_device_configuration_profile" in response:
                        success = True
                    elif "raw_response" in response:
                        raw = response["raw_response"]
                        if "<os_x_configuration_profile>" in raw or "<mobile_device_configuration_profile>" in raw:
                            if "<id>" in raw:
                                success = True
                
                if success:
                    # Extract profile ID if available
                    profile_id = None
                    if isinstance(response, dict) and "raw_response" in response:
                        import re
                        match = re.search(r'<id>(\d+)</id>', response["raw_response"])
                        if match:
                            profile_id = match.group(1)
                    
                    if profile_id:
                        print(f"✅ Profile deployed successfully: {profile_name} (ID: {profile_id})")
                        print(f"")
                        print(f"⚠️  IMPORTANT: Profile has NO SCOPE (not deployed to any computers)")
                        print(f"   You must manually scope this profile in Jamf Pro before it will deploy")
                        print(f"   View profile: Configuration Profiles > ID {profile_id}")
                    else:
                        print(f"✅ Profile deployed successfully: {profile_name}")
                        print(f"⚠️  IMPORTANT: Profile has NO SCOPE - manually scope it in Jamf Pro")
                    return True
                else:
                    print(f"❌ Failed to deploy profile: {profile_name}")
                    if response:
                        print(f"   Response: {response}")
                    return False
            except Exception as api_error:
                print(f"❌ API error deploying profile: {api_error}")
                return False
                
        except Exception as e:
            print(f"❌ Error deploying profile: {e}")
            return False
    
    def _save_mobileconfig_locally(self, mobileconfig: Dict[str, Any], profile_name: str) -> bool:
        """Save mobileconfig locally"""
        try:
            from pathlib import Path
            from datetime import datetime
            
            output_dir = Path("generated_profiles")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{profile_name.replace(' ', '_')}_{timestamp}.mobileconfig"
            filepath = output_dir / filename
            
            with open(filepath, "wb") as f:
                plistlib.dump(mobileconfig, f)
            
            print(f"✅ Profile saved locally: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving profile: {e}")
            return False
    
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
