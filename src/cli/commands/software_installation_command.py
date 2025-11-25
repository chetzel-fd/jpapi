#!/usr/bin/env python3
"""
Software Installation Command for jpapi CLI
Integrates the SOLID-compliant software installation addon with the main jpapi CLI
"""

import sys
import json
from pathlib import Path
from typing import Any, List, Optional

from .common_imports import ArgumentParser, BaseCommand, Namespace

# Add addons to path for software installation imports
addons_path = Path(__file__).parent.parent.parent / "addons"
sys.path.insert(0, str(addons_path))

from software_installation import SoftwareInstallationFactory


class SoftwareInstallationCommand(BaseCommand):
    """Software installation command using jpapi's CLI architecture"""

    def __init__(self):
        super().__init__(
            name="software-install",
            description="📦 Software installation via config profiles, policies, and packages",
        )
        self._setup_patterns()
        self.factory = SoftwareInstallationFactory()

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")
        
        # Install extension command
        ext_parser = subparsers.add_parser("extension", help="Install browser extension")
        ext_parser.add_argument("--browser", required=True, 
                               choices=["chrome", "firefox", "safari", "edge"],
                               help="Browser application")
        ext_parser.add_argument("--extension-id", required=True, 
                               help="Extension ID")
        ext_parser.add_argument("--extension-url", 
                               help="Extension manifest URL")
        ext_parser.add_argument("--profile-name", 
                               help="Custom profile name")
        
        # Install app command
        app_parser = subparsers.add_parser("app", help="Install application")
        app_parser.add_argument("--app-name", required=True, 
                               help="Application name")
        app_parser.add_argument("--method", 
                               choices=["installomator", "policy", "package"],
                               default="installomator",
                               help="Installation method")
        app_parser.add_argument("--label", 
                               help="Installomator label")
        app_parser.add_argument("--category", 
                               default="Productivity",
                               help="Policy category")
        
        # Create policy command
        policy_parser = subparsers.add_parser("policy", help="Create software installation policy")
        policy_parser.add_argument("--app-name", required=True, 
                                  help="Application name")
        policy_parser.add_argument("--package-id", type=int,
                                  help="Jamf Pro package ID")
        policy_parser.add_argument("--script-id", type=int,
                                  help="Jamf Pro script ID")
        policy_parser.add_argument("--policy-name", 
                                  help="Custom policy name")
        
        # Create PPPC command
        pppc_parser = subparsers.add_parser("pppc", help="Create PPPC permissions profile")
        pppc_parser.add_argument("--app-name", required=True, 
                                help="Application name")
        pppc_parser.add_argument("--bundle-id", required=True, 
                                help="Bundle identifier")
        pppc_parser.add_argument("--permissions", required=True, 
                                help="Comma-separated list of permissions")
        pppc_parser.add_argument("--profile-name", 
                                help="Custom profile name")
        
        # Batch deploy command
        batch_parser = subparsers.add_parser("batch", help="Batch deploy from config file")
        batch_parser.add_argument("--config", required=True, 
                                 help="Configuration file path")
        
        # Script to profile command
        script_parser = subparsers.add_parser("script-to-profile", 
                                             help="Download script from Jamf Pro and create config profile")
        script_parser.add_argument("--script-id", type=int, required=True,
                                  help="Jamf Pro script ID to download")
        script_parser.add_argument("--profile-name",
                                  help="Custom profile name (default: script name)")
        script_parser.add_argument("--description",
                                  help="Profile description")
        script_parser.add_argument("--no-deploy", action="store_true",
                                  help="Don't deploy to Jamf Pro, just save locally")
        script_parser.add_argument("--no-execute", action="store_true",
                                  help="Don't auto-execute script, just install the file")
        script_parser.add_argument("--execution-trigger",
                                  choices=["once", "always"],
                                  default="once",
                                  help="Execution trigger: 'once' (run once) or 'always' (run on boot/login)")
        script_parser.add_argument("--env", 
                                  choices=["sandbox", "production"],
                                  help="Environment for deployment (overrides default)")
        script_parser.add_argument("--download-env",
                                  choices=["sandbox", "production"],
                                  help="Environment to download script from (default: same as --env)")
        script_parser.add_argument("--deploy-env",
                                  choices=["sandbox", "production"],
                                  help="Environment to deploy profile to (default: same as --env)")
        
        # CrowdStrike installation command
        cs_parser = subparsers.add_parser("crowdstrike", 
                                         help="Create CrowdStrike Falcon installation config profile")
        cs_parser.add_argument("--policy-event",
                               default="crowdstrikefalcon",
                               help="Policy event name to trigger (default: crowdstrikefalcon)")
        cs_parser.add_argument("--direct-install", action="store_true",
                               help="Use direct installation instead of policy trigger (less scalable)")
        cs_parser.add_argument("--customer-id",
                               help="CrowdStrike Customer ID (CID) - required if --direct-install")
        cs_parser.add_argument("--package-name",
                               default="FalconSensorMacOS.MaverickGyr-1124.pkg",
                               help="CrowdStrike package name (only for --direct-install)")
        cs_parser.add_argument("--package-id", type=int,
                               help="CrowdStrike package ID (only for --direct-install)")
        cs_parser.add_argument("--script-id", type=int,
                               help="Use existing installation script ID (e.g., 50) and enhance it")
        cs_parser.add_argument("--profile-name",
                               help="Custom profile name")
        cs_parser.add_argument("--no-deploy", action="store_true",
                               help="Don't deploy to Jamf Pro, just save locally")
        cs_parser.add_argument("--env", 
                               choices=["sandbox", "production"],
                               help="Environment for deployment (overrides default)")
        cs_parser.add_argument("--download-env",
                               choices=["sandbox", "production"],
                               help="Environment to download script from (default: same as --env)")
        cs_parser.add_argument("--deploy-env",
                               choices=["sandbox", "production"],
                               help="Environment to deploy profile to (default: same as --env)")

    def _setup_patterns(self):
        """Setup conversational patterns"""
        self.pattern_matcher.add_conversational_pattern(
            pattern="install extension",
            handler=self._handle_extension_install,
            description="Install a browser extension"
        )
        self.pattern_matcher.add_conversational_pattern(
            pattern="install app",
            handler=self._handle_app_install,
            description="Install an application"
        )
        self.pattern_matcher.add_conversational_pattern(
            pattern="create policy",
            handler=self._handle_policy_create,
            description="Create a software installation policy"
        )
        self.pattern_matcher.add_conversational_pattern(
            pattern="create pppc",
            handler=self._handle_pppc_create,
            description="Create a PPPC permissions profile"
        )

    def execute(self, args: Namespace) -> int:
        """Execute the software installation command"""
        if not self.check_auth(args):
            return 1
        
        return self.run(args)
    
    def run(self, args: Namespace) -> int:
        """Run the software installation command"""
        try:
            # Initialize factory with auth
            self.factory.auth = self.auth
            
            if args.subcommand == "extension":
                return self._handle_extension_install(args)
            elif args.subcommand == "app":
                return self._handle_app_install(args)
            elif args.subcommand == "policy":
                return self._handle_policy_create(args)
            elif args.subcommand == "pppc":
                return self._handle_pppc_create(args)
            elif args.subcommand == "batch":
                return self._handle_batch_deploy(args)
            elif args.subcommand == "script-to-profile":
                return self._handle_script_to_profile(args)
            elif args.subcommand == "crowdstrike":
                return self._handle_crowdstrike_install(args)
            else:
                print("❌ No subcommand specified. Use --help for available options.")
                return 1
                
        except Exception as e:
            self.logger.error(f"Software installation command failed: {e}")
            return 1

    def _handle_extension_install(self, args: Namespace) -> int:
        """Handle browser extension installation"""
        try:
            service = self.factory.create_software_installation_service()
            
            success = service.install_browser_extension(
                browser=args.browser,
                extension_id=args.extension_id,
                extension_url=args.extension_url,
                profile_name=args.profile_name
            )
            
            if success:
                print(f"✅ Successfully installed {args.browser} extension: {args.extension_id}")
                return 0
            else:
                print(f"❌ Failed to install {args.browser} extension: {args.extension_id}")
                return 1
                
        except Exception as e:
            print(f"❌ Error installing extension: {e}")
            return 1

    def _handle_app_install(self, args: Namespace) -> int:
        """Handle application installation"""
        try:
            service = self.factory.create_software_installation_service()
            
            if args.method == "installomator":
                success = service.install_app_with_installomator(
                    app_name=args.app_name,
                    label=args.label,
                    category=args.category
                )
            else:
                print(f"❌ Unsupported method: {args.method}")
                return 1
            
            if success:
                print(f"✅ Successfully installed app: {args.app_name}")
                return 0
            else:
                print(f"❌ Failed to install app: {args.app_name}")
                return 1
                
        except Exception as e:
            print(f"❌ Error installing app: {e}")
            return 1

    def _handle_policy_create(self, args: Namespace) -> int:
        """Handle policy creation"""
        try:
            service = self.factory.create_software_installation_service()
            
            success = service.create_software_policy(
                app_name=args.app_name,
                package_id=args.package_id,
                script_id=args.script_id,
                policy_name=args.policy_name
            )
            
            if success:
                print(f"✅ Successfully created policy: {args.app_name}")
                return 0
            else:
                print(f"❌ Failed to create policy: {args.app_name}")
                return 1
                
        except Exception as e:
            print(f"❌ Error creating policy: {e}")
            return 1

    def _handle_pppc_create(self, args: Namespace) -> int:
        """Handle PPPC profile creation"""
        try:
            service = self.factory.create_software_installation_service()
            
            permissions = args.permissions.split(",")
            success = service.create_pppc_profile(
                app_name=args.app_name,
                bundle_id=args.bundle_id,
                permissions=permissions,
                profile_name=args.profile_name
            )
            
            if success:
                print(f"✅ Successfully created PPPC profile: {args.app_name}")
                return 0
            else:
                print(f"❌ Failed to create PPPC profile: {args.app_name}")
                return 1
                
        except Exception as e:
            print(f"❌ Error creating PPPC profile: {e}")
            return 1

    def _handle_batch_deploy(self, args: Namespace) -> int:
        """Handle batch deployment"""
        try:
            # Load configuration file
            with open(args.config, 'r') as f:
                config = json.load(f)
            
            service = self.factory.create_software_installation_service()
            
            success = service.batch_deploy(config)
            
            if success:
                print("✅ Successfully completed batch deployment")
                return 0
            else:
                print("❌ Batch deployment completed with errors")
                return 1
                
        except Exception as e:
            print(f"❌ Error in batch deployment: {e}")
            return 1

    def _handle_script_to_profile(self, args: Namespace) -> int:
        """Handle script-to-profile conversion with cross-environment support"""
        try:
            from core.auth.login_factory import get_best_auth
            
            # Determine environments
            download_env = args.download_env or args.env or self.environment
            deploy_env = args.deploy_env or args.env or self.environment
            
            print(f"📥 Download Environment: {download_env}")
            print(f"🚀 Deploy Environment: {deploy_env}")
            
            # Download script from source environment
            print(f"\n📥 Step 1: Downloading script {args.script_id} from {download_env}...")
            
            # Create temporary auth for download
            from core.auth.login_types import AuthInterface
            download_auth = get_best_auth(environment=download_env)
            download_service = self.factory.create_software_installation_service()
            download_service.script_service.auth = download_auth
            
            # Download script
            script_data = download_service.script_service.download_script(args.script_id)
            if not script_data:
                print(f"❌ Failed to download script {args.script_id} from {download_env}")
                return 1
            
            print(f"✅ Successfully downloaded: {script_data.get('name', 'Unknown')}")
            
            # Create profile from downloaded script
            print(f"\n📦 Step 2: Creating config profile...")
            
            mobileconfig = download_service.script_service.create_script_profile(
                script_data=script_data,
                profile_name=args.profile_name,
                description=args.description or f"Script {args.script_id} from {download_env}",
                auto_execute=not args.no_execute,
                execution_trigger=args.execution_trigger
            )
            
            if not mobileconfig:
                print(f"❌ Failed to create profile from script")
                return 1
            
            print(f"✅ Profile created successfully")
            
            # Deploy to target environment (if not --no-deploy)
            if not args.no_deploy:
                print(f"\n🚀 Step 3: Deploying profile to {deploy_env}...")
                
                # Create deploy auth
                deploy_auth = get_best_auth(environment=deploy_env)
                deploy_service = self.factory.create_software_installation_service()
                deploy_service.script_service.auth = deploy_auth
                
                profile_name = args.profile_name or f"{script_data.get('name', 'Unknown Script')} Script Profile"
                success = deploy_service.script_service._deploy_mobileconfig(
                    mobileconfig, 
                    profile_name,
                    environment=deploy_env
                )
            else:
                print(f"\n💾 Saving profile locally...")
                profile_name = args.profile_name or f"{script_data.get('name', 'Unknown Script')} Script Profile"
                success = download_service.script_service._save_mobileconfig_locally(mobileconfig, profile_name)
            
            if success:
                if args.no_deploy:
                    print(f"✅ Successfully created profile locally")
                    print(f"   Downloaded from: {download_env}")
                    print(f"   Ready to deploy to: {deploy_env}")
                else:
                    print(f"✅ Successfully downloaded from {download_env} and deployed to {deploy_env}")
                return 0
            else:
                print(f"❌ Failed to deploy profile")
                return 1
                
        except Exception as e:
            print(f"❌ Error creating script profile: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def _handle_crowdstrike_install(self, args: Namespace) -> int:
        """Handle CrowdStrike installation profile creation with cross-environment support"""
        try:
            from core.auth.login_factory import get_best_auth
            
            # Determine environments
            download_env = args.download_env or args.env or self.environment
            deploy_env = args.deploy_env or args.env or self.environment
            
            print(f"📥 Download Environment: {download_env}")
            print(f"🚀 Deploy Environment: {deploy_env}")
            
            # Validate arguments
            if args.direct_install and not args.customer_id:
                print("❌ --customer-id is required when using --direct-install")
                return 1
            
            # If script-id provided, download and enhance existing script
            if args.script_id:
                print(f"\n📥 Step 1: Downloading script {args.script_id} from {download_env}...")
                
                # Create download auth
                download_auth = get_best_auth(environment=download_env)
                
                # Import CrowdStrike service (addons_path already added at top)
                from software_installation import CrowdStrikeInstallerService
                
                download_cs_service = CrowdStrikeInstallerService(auth=download_auth)
                
                # Download script and create profile
                mobileconfig = download_cs_service.download_script_and_create_profile(
                    script_id=args.script_id,
                    customer_id=args.customer_id,
                    package_name=args.package_name,
                    profile_name=args.profile_name
                )
                
                if not mobileconfig:
                    print(f"❌ Failed to create profile from script {args.script_id}")
                    return 1
                
                print(f"✅ Profile created successfully")
                
                # Deploy or save
                if not args.no_deploy:
                    print(f"\n🚀 Step 2: Deploying profile to {deploy_env}...")
                    
                    # Create deploy auth
                    deploy_auth = get_best_auth(environment=deploy_env)
                    deploy_cs_service = CrowdStrikeInstallerService(auth=deploy_auth)
                    
                    success = deploy_cs_service.script_service._deploy_mobileconfig(
                        mobileconfig,
                        args.profile_name or "CrowdStrike Falcon - Pre-Login Installation",
                        environment=deploy_env
                    )
                else:
                    print(f"\n💾 Saving profile locally...")
                    success = download_cs_service.script_service._save_mobileconfig_locally(
                        mobileconfig,
                        args.profile_name or "CrowdStrike Falcon - Pre-Login Installation"
                    )
            else:
                # Create new installation profile (prefer policy trigger approach)
                use_policy = not args.direct_install
                
                # Create auth for the environment we're deploying to
                deploy_auth = get_best_auth(environment=deploy_env)
                from software_installation import CrowdStrikeInstallerService
                cs_service = CrowdStrikeInstallerService(auth=deploy_auth)
                
                if use_policy:
                    print(f"✅ Using RECOMMENDED approach: Policy trigger (event: {args.policy_event})")
                    print(f"   Profile will call existing Jamf policy instead of embedding installation logic")
                    print(f"   More scalable and maintainable!")
                else:
                    print(f"⚠️  Using direct installation approach (less scalable)")
                    print(f"   Consider using --policy-event instead for better maintainability")
                
                success = cs_service.deploy_crowdstrike_profile(
                    policy_event=args.policy_event,
                    use_policy=use_policy,
                    customer_id=args.customer_id,
                    package_name=args.package_name,
                    package_id=args.package_id,
                    deploy=not args.no_deploy,
                    profile_name=args.profile_name
                )
            
            if success:
                if args.no_deploy:
                    print(f"✅ Successfully created CrowdStrike installation profile locally")
                    print(f"   Profile will install CrowdStrike during enrollment (pre-login)")
                    if args.script_id:
                        print(f"   Downloaded from: {download_env}")
                        print(f"   Ready to deploy to: {deploy_env}")
                else:
                    print(f"✅ Successfully created and deployed CrowdStrike installation profile")
                    print(f"   Profile will install CrowdStrike during enrollment (pre-login)")
                    if args.script_id:
                        print(f"   Downloaded from: {download_env}")
                        print(f"   Deployed to: {deploy_env}")
                    if args.package_name:
                        print(f"   Package: {args.package_name}")
                    if args.customer_id:
                        print(f"   Customer ID: {args.customer_id}")
                return 0
            else:
                print(f"❌ Failed to create CrowdStrike installation profile")
                return 1
                
        except Exception as e:
            print(f"❌ Error creating CrowdStrike profile: {e}")
            import traceback
            traceback.print_exc()
            return 1
