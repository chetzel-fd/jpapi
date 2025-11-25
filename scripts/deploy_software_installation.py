#!/usr/bin/env python3
"""
Deploy Software Installation via Jamf Pro
==========================================

This script provides a comprehensive deployment system for software installation
using Jamf Pro config profiles, policies, and packages.

Features:
- Deploy browser extensions via config profiles
- Create Installomator policies for app installation
- Deploy PPPC permissions profiles
- Create custom software installation policies
- Template-based profile generation
- Batch deployment capabilities

Usage:
    python deploy_software_installation.py --help
    python deploy_software_installation.py deploy-extension --template chrome --extension-id abc123
    python deploy_software_installation.py deploy-app --app-name "Slack" --method installomator
    python deploy_software_installation.py batch-deploy --config deployment_config.json
"""

import sys
import json
import argparse
import uuid
import plistlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Add src to path for JPAPI imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from cli.commands.create_command import CreateCommand
    from core.auth import JamfAuth
    JPAPI_AVAILABLE = True
except ImportError:
    JPAPI_AVAILABLE = False
    print("⚠️  JPAPI not available. Some features will be limited.")


class SoftwareDeploymentManager:
    """Manages software deployment via Jamf Pro"""
    
    def __init__(self, environment: str = "sandbox"):
        self.environment = environment
        self.auth = None
        self.create_cmd = None
        self.templates_dir = Path(__file__).parent / "templates"
        
        if JPAPI_AVAILABLE:
            try:
                self.auth = JamfAuth(environment=environment)
                self.create_cmd = CreateCommand()
                print(f"✅ Connected to Jamf Pro ({environment})")
            except Exception as e:
                print(f"⚠️  Could not connect to Jamf Pro: {e}")
                print("   Will create profiles locally only")
    
    def deploy_extension_from_template(self, template: str, extension_id: str, 
                                    extension_url: str = None, 
                                    extension_name: str = None) -> bool:
        """
        Deploy browser extension using template
        
        Args:
            template: Template name (chrome, firefox, safari, edge)
            extension_id: Extension ID
            extension_url: Extension manifest URL
            extension_name: Human-readable extension name
        """
        if not extension_name:
            extension_name = f"Extension {extension_id[:8]}"
        
        template_file = self.templates_dir / f"{template}_extension_template.mobileconfig"
        if not template_file.exists():
            print(f"❌ Template not found: {template_file}")
            return False
        
        print(f"🌐 Deploying {template} extension: {extension_name}")
        
        try:
            # Read template
            with open(template_file, "rb") as f:
                template_data = plistlib.load(f)
            
            # Replace placeholders
            profile_data = self._replace_template_placeholders(
                template_data,
                {
                    "EXTENSION_ID": extension_id,
                    "EXTENSION_URL": extension_url or "",
                    "EXTENSION_NAME": extension_name,
                    "EXTENSION_UUID": str(uuid.uuid4()),
                    "PROFILE_UUID": str(uuid.uuid4()),
                    "YOUR_ORGANIZATION": "JAMF Pro"
                }
            )
            
            # Deploy profile
            profile_name = f"{template.title()} Extension - {extension_name}"
            return self._deploy_mobileconfig(profile_data, profile_name)
            
        except Exception as e:
            print(f"❌ Error deploying extension: {e}")
            return False
    
    def deploy_app_with_installomator(self, app_name: str, label: str = None, 
                                    category: str = "Productivity") -> bool:
        """
        Deploy app using Installomator policy
        
        Args:
            app_name: Application name
            label: Installomator label
            category: Policy category
        """
        if not label:
            label = app_name.lower().replace(" ", "")
        
        print(f"📱 Deploying app with Installomator: {app_name}")
        
        # Create Installomator policy
        policy_data = self._create_installomator_policy(app_name, label, category)
        
        if not self.auth:
            print("❌ Jamf Pro connection required for policy creation")
            return False
        
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
                print(f"✅ Successfully created Installomator policy: {app_name}")
                
                # Also create PPPC profile if needed
                return self._create_pppc_profile_for_app(app_name, label)
            else:
                print(f"❌ Failed to create Installomator policy: {app_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating Installomator policy: {e}")
            return False
    
    def deploy_pppc_profile(self, app_name: str, bundle_id: str, 
                          permissions: List[str]) -> bool:
        """
        Deploy PPPC permissions profile
        
        Args:
            app_name: Application name
            bundle_id: Bundle identifier
            permissions: List of permissions to grant
        """
        print(f"🔒 Deploying PPPC profile: {app_name}")
        
        template_file = self.templates_dir / "app_pppc_template.mobileconfig"
        if not template_file.exists():
            print(f"❌ PPPC template not found: {template_file}")
            return False
        
        try:
            # Read template
            with open(template_file, "rb") as f:
                template_data = plistlib.load(f)
            
            # Replace placeholders
            profile_data = self._replace_template_placeholders(
                template_data,
                {
                    "APP_NAME": app_name,
                    "APP_BUNDLE_ID": bundle_id,
                    "PPPC_UUID": str(uuid.uuid4()),
                    "PROFILE_UUID": str(uuid.uuid4()),
                    "YOUR_ORGANIZATION": "JAMF Pro"
                }
            )
            
            # Deploy profile
            profile_name = f"{app_name} PPPC Permissions"
            return self._deploy_mobileconfig(profile_data, profile_name)
            
        except Exception as e:
            print(f"❌ Error deploying PPPC profile: {e}")
            return False
    
    def batch_deploy(self, config_file: str) -> bool:
        """
        Deploy multiple items from configuration file
        
        Args:
            config_file: Path to JSON configuration file
        """
        print(f"📦 Batch deploying from: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            success_count = 0
            total_count = 0
            
            # Deploy extensions
            for extension in config.get("extensions", []):
                total_count += 1
                if self.deploy_extension_from_template(
                    template=extension["template"],
                    extension_id=extension["extension_id"],
                    extension_url=extension.get("extension_url"),
                    extension_name=extension.get("extension_name")
                ):
                    success_count += 1
            
            # Deploy apps
            for app in config.get("apps", []):
                total_count += 1
                if self.deploy_app_with_installomator(
                    app_name=app["app_name"],
                    label=app.get("label"),
                    category=app.get("category", "Productivity")
                ):
                    success_count += 1
            
            # Deploy PPPC profiles
            for pppc in config.get("pppc_profiles", []):
                total_count += 1
                if self.deploy_pppc_profile(
                    app_name=pppc["app_name"],
                    bundle_id=pppc["bundle_id"],
                    permissions=pppc["permissions"]
                ):
                    success_count += 1
            
            print(f"✅ Batch deployment complete: {success_count}/{total_count} successful")
            return success_count == total_count
            
        except Exception as e:
            print(f"❌ Error in batch deployment: {e}")
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
    
    def _create_pppc_profile_for_app(self, app_name: str, label: str) -> bool:
        """Create PPPC profile for an app (simplified)"""
        # This would typically look up the bundle ID from Installomator data
        # For now, we'll create a generic profile
        bundle_id = f"com.{label.lower()}"
        
        return self.deploy_pppc_profile(
            app_name=app_name,
            bundle_id=bundle_id,
            permissions=["full_disk_access", "camera", "microphone"]
        )
    
    def _replace_template_placeholders(self, data: Any, replacements: Dict[str, str]) -> Any:
        """Recursively replace placeholders in template data"""
        if isinstance(data, dict):
            return {k: self._replace_template_placeholders(v, replacements) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_template_placeholders(item, replacements) for item in data]
        elif isinstance(data, str):
            result = data
            for placeholder, value in replacements.items():
                result = result.replace(placeholder, value)
            return result
        else:
            return data
    
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
        description="Deploy Software Installation via Jamf Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy Chrome extension
  python deploy_software_installation.py deploy-extension --template chrome --extension-id abc123def456

  # Deploy app with Installomator
  python deploy_software_installation.py deploy-app --app-name "Slack" --method installomator

  # Batch deploy from config file
  python deploy_software_installation.py batch-deploy --config deployment_config.json
        """
    )
    
    parser.add_argument("--environment", "-e", 
                       choices=["sandbox", "production"], 
                       default="sandbox",
                       help="Jamf Pro environment (default: sandbox)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Deploy extension command
    ext_parser = subparsers.add_parser("deploy-extension", help="Deploy browser extension")
    ext_parser.add_argument("--template", required=True, 
                           choices=["chrome", "firefox", "safari", "edge"],
                           help="Browser template")
    ext_parser.add_argument("--extension-id", required=True, 
                           help="Extension ID")
    ext_parser.add_argument("--extension-url", 
                           help="Extension manifest URL")
    ext_parser.add_argument("--extension-name", 
                           help="Human-readable extension name")
    
    # Deploy app command
    app_parser = subparsers.add_parser("deploy-app", help="Deploy application")
    app_parser.add_argument("--app-name", required=True, 
                           help="Application name")
    app_parser.add_argument("--method", 
                           choices=["installomator", "policy", "package"],
                           default="installomator",
                           help="Deployment method")
    app_parser.add_argument("--label", 
                           help="Installomator label")
    app_parser.add_argument("--category", 
                           default="Productivity",
                           help="Policy category")
    
    # Deploy PPPC command
    pppc_parser = subparsers.add_parser("deploy-pppc", help="Deploy PPPC permissions profile")
    pppc_parser.add_argument("--app-name", required=True, 
                            help="Application name")
    pppc_parser.add_argument("--bundle-id", required=True, 
                            help="Bundle identifier")
    pppc_parser.add_argument("--permissions", required=True, 
                            help="Comma-separated list of permissions")
    
    # Batch deploy command
    batch_parser = subparsers.add_parser("batch-deploy", help="Batch deploy from config file")
    batch_parser.add_argument("--config", required=True, 
                             help="Configuration file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize deployment manager
    manager = SoftwareDeploymentManager(environment=args.environment)
    
    try:
        if args.command == "deploy-extension":
            success = manager.deploy_extension_from_template(
                template=args.template,
                extension_id=args.extension_id,
                extension_url=args.extension_url,
                extension_name=args.extension_name
            )
            
        elif args.command == "deploy-app":
            if args.method == "installomator":
                success = manager.deploy_app_with_installomator(
                    app_name=args.app_name,
                    label=args.label,
                    category=args.category
                )
            else:
                print(f"❌ Unsupported method: {args.method}")
                success = False
                
        elif args.command == "deploy-pppc":
            permissions = args.permissions.split(",")
            success = manager.deploy_pppc_profile(
                app_name=args.app_name,
                bundle_id=args.bundle_id,
                permissions=permissions
            )
            
        elif args.command == "batch-deploy":
            success = manager.batch_deploy(args.config)
        
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













