#!/usr/bin/env python3
"""
Software Installation via Jamf Pro Config Profiles
==================================================

This script provides multiple approaches for software installation using Jamf Pro:

1. CONFIG PROFILE APPROACH: Creates configuration profiles that:
   - Force installation of browser extensions
   - Configure application preferences
   - Set up PPPC permissions
   - Deploy managed preferences

2. HYBRID APPROACH: Combines config profiles with:
   - Installomator policies for actual software installation
   - Package deployment policies
   - Custom installation scripts

3. PURE POLICY APPROACH: Uses Jamf Pro policies for direct software installation

Usage:
    python software_install_via_config_profile.py --help
    python software_install_via_config_profile.py install-extension --app Chrome --extension-id abc123
    python software_install_via_config_profile.py install-app --app-name "Slack" --method installomator
    python software_install_via_config_profile.py create-policy --app-name "Zoom" --package-id 123
"""

import sys
import json
import argparse
import uuid
import plistlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add src to path for JPAPI imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from cli.commands.create_command import CreateCommand
    from cli.commands.installomator_command import InstallomatorCommand
    from core.auth import JamfAuth
    JPAPI_AVAILABLE = True
except ImportError:
    JPAPI_AVAILABLE = False
    print("⚠️  JPAPI not available. Some features will be limited.")


class SoftwareInstaller:
    """Main class for software installation via config profiles"""
    
    def __init__(self, environment: str = "sandbox"):
        self.environment = environment
        self.auth = None
        self.create_cmd = None
        
        if JPAPI_AVAILABLE:
            try:
                self.auth = JamfAuth(environment=environment)
                self.create_cmd = CreateCommand()
                print(f"✅ Connected to Jamf Pro ({environment})")
            except Exception as e:
                print(f"⚠️  Could not connect to Jamf Pro: {e}")
                print("   Will create profiles locally only")
    
    def install_browser_extension(self, app: str, extension_id: str, 
                                extension_url: str = None, 
                                profile_name: str = None) -> bool:
        """
        Install a browser extension via config profile
        
        Args:
            app: Browser app (Chrome, Firefox, Safari, Edge)
            extension_id: Extension ID
            extension_url: Extension manifest URL (optional)
            profile_name: Custom profile name (optional)
        """
        print(f"🌐 Installing {app} extension: {extension_id}")
        
        if app.lower() == "chrome":
            return self._install_chrome_extension(extension_id, extension_url, profile_name)
        elif app.lower() == "firefox":
            return self._install_firefox_extension(extension_id, extension_url, profile_name)
        elif app.lower() == "safari":
            return self._install_safari_extension(extension_id, profile_name)
        elif app.lower() == "edge":
            return self._install_edge_extension(extension_id, extension_url, profile_name)
        else:
            print(f"❌ Unsupported browser: {app}")
            return False
    
    def _install_chrome_extension(self, extension_id: str, extension_url: str = None, 
                                profile_name: str = None) -> bool:
        """Install Chrome extension via managed preferences"""
        
        if not profile_name:
            profile_name = f"Chrome Extension - {extension_id[:8]}"
        
        # Create mobileconfig for Chrome extension
        mobileconfig = {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"com.google.Chrome.extension.{extension_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"Chrome Extension - {extension_id}",
                    "PayloadDescription": f"Forces installation of extension {extension_id}",
                    "PayloadContent": {
                        "com.google.Chrome": {
                            "Forced": [
                                {
                                    "mcx_preference_settings": {
                                        "ExtensionInstallForcelist": [
                                            f"{extension_id};{extension_url}" if extension_url 
                                            else extension_id
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"Configuration profile for Chrome extension {extension_id}",
            "PayloadIdentifier": f"com.jamf.chrome.extension.{extension_id}",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }
        
        return self._deploy_mobileconfig(mobileconfig, profile_name)
    
    def _install_firefox_extension(self, extension_id: str, extension_url: str = None, 
                                 profile_name: str = None) -> bool:
        """Install Firefox extension via managed preferences"""
        
        if not profile_name:
            profile_name = f"Firefox Extension - {extension_id[:8]}"
        
        mobileconfig = {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"org.mozilla.firefox.extension.{extension_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"Firefox Extension - {extension_id}",
                    "PayloadDescription": f"Forces installation of Firefox extension {extension_id}",
                    "PayloadContent": {
                        "org.mozilla.firefox": {
                            "Forced": [
                                {
                                    "mcx_preference_settings": {
                                        "extensions.webextensions.remote": True,
                                        "extensions.install.requireBuiltInCerts": False,
                                        "extensions.autoDisableScopes": 0
                                    }
                                }
                            ]
                        }
                    }
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"Configuration profile for Firefox extension {extension_id}",
            "PayloadIdentifier": f"com.jamf.firefox.extension.{extension_id}",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }
        
        return self._deploy_mobileconfig(mobileconfig, profile_name)
    
    def _install_safari_extension(self, extension_id: str, profile_name: str = None) -> bool:
        """Install Safari extension via managed preferences"""
        
        if not profile_name:
            profile_name = f"Safari Extension - {extension_id[:8]}"
        
        mobileconfig = {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"com.apple.Safari.extension.{extension_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"Safari Extension - {extension_id}",
                    "PayloadDescription": f"Forces installation of Safari extension {extension_id}",
                    "PayloadContent": {
                        "com.apple.Safari": {
                            "Forced": [
                                {
                                    "mcx_preference_settings": {
                                        "SafariExtensionsEnabled": True,
                                        "SafariExtensionsUpdateCheckEnabled": True
                                    }
                                }
                            ]
                        }
                    }
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"Configuration profile for Safari extension {extension_id}",
            "PayloadIdentifier": f"com.jamf.safari.extension.{extension_id}",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }
        
        return self._deploy_mobileconfig(mobileconfig, profile_name)
    
    def _install_edge_extension(self, extension_id: str, extension_url: str = None, 
                              profile_name: str = None) -> bool:
        """Install Microsoft Edge extension via managed preferences"""
        
        if not profile_name:
            profile_name = f"Edge Extension - {extension_id[:8]}"
        
        mobileconfig = {
            "PayloadContent": [
                {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadVersion": 1,
                    "PayloadIdentifier": f"com.microsoft.edgemac.extension.{extension_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadEnabled": True,
                    "PayloadDisplayName": f"Edge Extension - {extension_id}",
                    "PayloadDescription": f"Forces installation of Edge extension {extension_id}",
                    "PayloadContent": {
                        "com.microsoft.edgemac": {
                            "Forced": [
                                {
                                    "mcx_preference_settings": {
                                        "ExtensionInstallForcelist": [
                                            f"{extension_id};{extension_url}" if extension_url 
                                            else extension_id
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            ],
            "PayloadDisplayName": profile_name,
            "PayloadDescription": f"Configuration profile for Edge extension {extension_id}",
            "PayloadIdentifier": f"com.jamf.edge.extension.{extension_id}",
            "PayloadOrganization": "JAMF Pro",
            "PayloadType": "Configuration",
            "PayloadUUID": str(uuid.uuid4()),
            "PayloadVersion": 1
        }
        
        return self._deploy_mobileconfig(mobileconfig, profile_name)
    
    def install_app_with_installomator(self, app_name: str, label: str = None, 
                                     profile_name: str = None) -> bool:
        """
        Install an application using Installomator with supporting config profiles
        
        Args:
            app_name: Name of the application
            label: Installomator label (if different from app_name)
            profile_name: Custom profile name (optional)
        """
        print(f"📱 Installing app with Installomator: {app_name}")
        
        if not JPAPI_AVAILABLE:
            print("❌ Installomator integration requires JPAPI")
            return False
        
        try:
            # Use existing Installomator command
            installomator_cmd = InstallomatorCommand()
            
            # Create a mock args object
            class MockArgs:
                def __init__(self):
                    self.app_name = app_name
                    self.label = label or app_name.lower().replace(" ", "")
                    self.env = self.environment
                    self.scope_groups = ["All Computers"]
                    self.description = f"Installomator policy for {app_name}"
                    self.category = "Productivity"
                    self.trigger = "EVENT"
                    self.frequency = "Ongoing"
                    self.retry_attempts = 3
                    self.notify_on_failure = True
                    self.create_profiles = True
                    self.upload_to_jamf = True
            
            args = MockArgs()
            
            # Run the installomator command
            result = installomator_cmd.run(args)
            
            if result == 0:
                print(f"✅ Successfully created Installomator policy for {app_name}")
                return True
            else:
                print(f"❌ Failed to create Installomator policy for {app_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating Installomator policy: {e}")
            return False
    
    def create_software_policy(self, app_name: str, package_id: int = None, 
                             script_id: int = None, policy_name: str = None) -> bool:
        """
        Create a Jamf Pro policy for software installation
        
        Args:
            app_name: Name of the application
            package_id: Jamf Pro package ID (optional)
            script_id: Jamf Pro script ID (optional)
            policy_name: Custom policy name (optional)
        """
        print(f"📦 Creating software installation policy: {app_name}")
        
        if not self.auth:
            print("❌ Jamf Pro connection required for policy creation")
            return False
        
        if not policy_name:
            policy_name = f"Install {app_name}"
        
        # Create policy data
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
        
        try:
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
    
    def create_pppc_profile(self, app_name: str, bundle_id: str, 
                          permissions: List[str], profile_name: str = None) -> bool:
        """
        Create a PPPC (Privacy Preferences Policy Control) profile for an app
        
        Args:
            app_name: Name of the application
            bundle_id: Bundle identifier
            permissions: List of permissions to grant
            profile_name: Custom profile name (optional)
        """
        print(f"🔒 Creating PPPC profile for: {app_name}")
        
        if not profile_name:
            profile_name = f"{app_name} PPPC Permissions"
        
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
        
        mobileconfig = {
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
        
        return self._deploy_mobileconfig(mobileconfig, profile_name)
    
    def _deploy_mobileconfig(self, mobileconfig: Dict[str, Any], profile_name: str) -> bool:
        """Deploy a mobileconfig to Jamf Pro or save locally"""
        
        try:
            if self.auth and self.create_cmd:
                # Deploy to Jamf Pro
                print(f"🚀 Deploying profile to Jamf Pro: {profile_name}")
                
                # Convert mobileconfig to XML format
                payloads_xml = self.create_cmd._convert_mobileconfig_to_xml(mobileconfig)
                
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
                            "all_computers": True,
                            "all_jss_users": False
                        }
                    }
                }
                
                # Convert to XML
                xml_data = self._dict_to_xml(profile_data, "os_x_configuration_profile")
                
                # Create profile in Jamf Pro
                response = self.auth.api_request(
                    "POST",
                    "/JSSResource/osxconfigurationprofiles/id/0",
                    data=xml_data,
                    content_type="xml"
                )
                
                if response and "os_x_configuration_profile" in response:
                    print(f"✅ Profile deployed successfully: {profile_name}")
                    return True
                else:
                    print(f"❌ Failed to deploy profile: {profile_name}")
                    return False
            else:
                # Save locally
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
            print(f"❌ Error deploying profile: {e}")
            return False
    
    def _dict_to_xml(self, data: Dict[str, Any], root_name: str) -> str:
        """Convert dictionary to XML format (simplified)"""
        # This is a simplified XML conversion
        # In production, you'd want to use a proper XML library
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


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Software Installation via Jamf Pro Config Profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install Chrome extension
  python software_install_via_config_profile.py install-extension --app Chrome --extension-id abc123def456

  # Install app with Installomator
  python software_install_via_config_profile.py install-app --app-name "Slack" --method installomator

  # Create software installation policy
  python software_install_via_config_profile.py create-policy --app-name "Zoom" --package-id 123

  # Create PPPC permissions profile
  python software_install_via_config_profile.py create-pppc --app-name "Chrome" --bundle-id com.google.Chrome --permissions full_disk_access,camera,microphone
        """
    )
    
    parser.add_argument("--environment", "-e", 
                       choices=["sandbox", "production"], 
                       default="sandbox",
                       help="Jamf Pro environment (default: sandbox)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install extension command
    ext_parser = subparsers.add_parser("install-extension", help="Install browser extension")
    ext_parser.add_argument("--app", required=True, 
                           choices=["Chrome", "Firefox", "Safari", "Edge"],
                           help="Browser application")
    ext_parser.add_argument("--extension-id", required=True, 
                           help="Extension ID")
    ext_parser.add_argument("--extension-url", 
                           help="Extension manifest URL")
    ext_parser.add_argument("--profile-name", 
                           help="Custom profile name")
    
    # Install app command
    app_parser = subparsers.add_parser("install-app", help="Install application")
    app_parser.add_argument("--app-name", required=True, 
                           help="Application name")
    app_parser.add_argument("--method", 
                           choices=["installomator", "policy", "package"],
                           default="installomator",
                           help="Installation method")
    app_parser.add_argument("--label", 
                           help="Installomator label")
    app_parser.add_argument("--package-id", type=int,
                           help="Jamf Pro package ID")
    app_parser.add_argument("--script-id", type=int,
                           help="Jamf Pro script ID")
    
    # Create policy command
    policy_parser = subparsers.add_parser("create-policy", help="Create software installation policy")
    policy_parser.add_argument("--app-name", required=True, 
                              help="Application name")
    policy_parser.add_argument("--package-id", type=int,
                              help="Jamf Pro package ID")
    policy_parser.add_argument("--script-id", type=int,
                              help="Jamf Pro script ID")
    policy_parser.add_argument("--policy-name", 
                              help="Custom policy name")
    
    # Create PPPC command
    pppc_parser = subparsers.add_parser("create-pppc", help="Create PPPC permissions profile")
    pppc_parser.add_argument("--app-name", required=True, 
                            help="Application name")
    pppc_parser.add_argument("--bundle-id", required=True, 
                            help="Bundle identifier")
    pppc_parser.add_argument("--permissions", required=True, 
                            help="Comma-separated list of permissions")
    pppc_parser.add_argument("--profile-name", 
                            help="Custom profile name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize installer
    installer = SoftwareInstaller(environment=args.environment)
    
    try:
        if args.command == "install-extension":
            permissions = args.permissions.split(",") if hasattr(args, 'permissions') else []
            success = installer.install_browser_extension(
                app=args.app,
                extension_id=args.extension_id,
                extension_url=args.extension_url,
                profile_name=args.profile_name
            )
            
        elif args.command == "install-app":
            if args.method == "installomator":
                success = installer.install_app_with_installomator(
                    app_name=args.app_name,
                    label=args.label,
                    profile_name=args.profile_name
                )
            elif args.method == "policy":
                success = installer.create_software_policy(
                    app_name=args.app_name,
                    package_id=args.package_id,
                    script_id=args.script_id,
                    policy_name=args.policy_name
                )
            else:
                print(f"❌ Unsupported method: {args.method}")
                success = False
                
        elif args.command == "create-policy":
            success = installer.create_software_policy(
                app_name=args.app_name,
                package_id=args.package_id,
                script_id=args.script_id,
                policy_name=args.policy_name
            )
            
        elif args.command == "create-pppc":
            permissions = args.permissions.split(",")
            success = installer.create_pppc_profile(
                app_name=args.app_name,
                bundle_id=args.bundle_id,
                permissions=permissions,
                profile_name=args.profile_name
            )
        
        else:
            print(f"❌ Unknown command: {args.command}")
            success = False
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())













