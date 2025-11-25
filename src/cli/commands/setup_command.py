#!/usr/bin/env python3
"""
Setup Command for jpapi CLI
Handles authentication setup and configuration
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from .common_imports import (
    ArgumentParser,
    Namespace,
    BaseCommand,
    Optional,
    Any,
)


class SetupCommand(BaseCommand):
    """Setup command for authentication and configuration"""

    def __init__(self):
        super().__init__(
            name="setup", description="🔐 Set up JPAPI authentication and configuration"
        )
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup conversational patterns for natural language commands"""

        # Main setup patterns
        self.add_conversational_pattern(
            pattern="auth",
            handler="_setup_auth",
            description="Set up authentication",
            aliases=["authentication", "login", "configure"],
        )

        self.add_conversational_pattern(
            pattern="oauth",
            handler="_setup_oauth",
            description="Set up OAuth authentication",
            aliases=["oauth2", "token"],
        )

        self.add_conversational_pattern(
            pattern="basic",
            handler="_setup_basic",
            description="Set up basic authentication",
            aliases=["username", "password", "basic-auth"],
        )

        self.add_conversational_pattern(
            pattern="test",
            handler="_test_connection",
            description="Test current authentication",
            aliases=["test-auth", "verify", "check"],
        )

        self.add_conversational_pattern(
            pattern="list",
            handler="_list_credentials",
            description="List available credentials in keychain",
            aliases=["list-credentials", "show", "credentials"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add setup-specific arguments"""
        super().add_arguments(parser)

        parser.add_argument(
            "--url",
            help="JAMF Pro server URL",
        )

        parser.add_argument(
            "--client-id",
            help="OAuth client ID",
        )

        parser.add_argument(
            "--client-secret",
            help="OAuth client secret",
        )

        parser.add_argument(
            "--username",
            help="Basic auth username",
        )

        parser.add_argument(
            "--password",
            help="Basic auth password",
        )

        parser.add_argument(
            "--method",
            choices=["oauth", "basic"],
            help="Authentication method to use",
        )

        parser.add_argument(
            "--save-to-keychain",
            action="store_true",
            help="Save credentials to macOS Keychain after setup",
        )

        parser.add_argument(
            "--list-credentials",
            action="store_true",
            help="List available credentials in keychain",
        )

    def _setup_auth(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Interactive authentication setup"""
        return self._interactive_setup(args)

    def _setup_oauth(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Set up OAuth authentication"""
        return self._setup_oauth_auth(args)

    def _setup_basic(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Set up basic authentication"""
        return self._setup_basic_auth(args)

    def _test_connection(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Test current authentication"""
        return self._test_auth_connection(args)

    def execute(self, args: Namespace) -> int:
        """Execute setup command with direct argument handling"""
        # Check for direct command line arguments first
        if hasattr(args, "list_credentials") and args.list_credentials:
            return self._list_credentials(args)

        # Fall back to base command execution
        return super().execute(args)

    def _list_credentials(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List available credentials in keychain"""
        print("🔑 Available Credentials in Keychain")
        print("=" * 50)
        print()

        existing_creds = self._detect_keychain_credentials()

        if not existing_creds:
            print("❌ No JPAPI credentials found in keychain")
            print()
            print("To save credentials to keychain, run:")
            print("  jpapi setup --save-to-keychain")
            return 1

        for idx, (label, info) in enumerate(existing_creds.items(), 1):
            print(f"{idx}. {label}")
            print(f"   URL: {info.get('url', 'N/A')}")
            if info.get("client_id"):
                print("   Method: OAuth")
                print(f"   Client ID: {info['client_id'][:20]}...")
            elif info.get("username"):
                print("   Method: Basic Auth")
                print(f"   Username: {info['username']}")
            print()

        print(f"✅ Found {len(existing_creds)} credential(s)")
        return 0

    def _interactive_setup(self, args: Namespace) -> int:
        """Run the interactive setup process with keychain detection"""
        try:
            # Show welcome message and guidance
            print("🔐 JPAPI Setup - Authentication Configuration")
            print("=" * 60)
            print()
            print("This wizard will help you configure JPAPI to connect to your JAMF Pro server.")
            print()
            print("What you'll need:")
            print("  • Your JAMF Pro server URL (e.g., company.jamfcloud.com)")
            print("  • OAuth credentials (recommended) OR Basic Auth credentials")
            print()
            print("Getting OAuth Credentials:")
            print("  1. Log into JAMF Pro")
            print("  2. Go to: Settings → System Settings → API Roles and Clients")
            print("  3. Click 'New' to create an API Client")
            print("  4. Copy the JSON response (contains client_id and client_secret)")
            print()
            print("✨ Tip: JPAPI auto-detects existing credentials in your macOS Keychain!")
            print()
            print("-" * 60)
            print()
            
            # Check for existing keychain credentials
            existing_creds = self._detect_keychain_credentials()

            if existing_creds:
                print("\n✨ Found existing credentials in keychain!")
                print()
                for idx, (label, info) in enumerate(existing_creds.items(), 1):
                    print(f"{idx}. {label}")
                    print(f"   URL: {info.get('url', 'N/A')}")
                    if info.get("client_id"):
                        print("   Method: OAuth")
                        print(f"   Client ID: {info['client_id'][:20]}...")
                    elif info.get("username"):
                        print("   Method: Basic Auth")
                        print(f"   Username: {info['username']}")
                    print()

                choice = (
                    input(
                        f"Use existing credentials? (1-{len(existing_creds)}/new/cancel): "
                    )
                    .strip()
                    .lower()
                )

                if choice == "cancel":
                    print("❌ Setup cancelled")
                    return 0
                elif choice != "new" and choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(existing_creds):
                        selected_label = list(existing_creds.keys())[idx]
                        return self._use_existing_credentials(
                            selected_label, existing_creds[selected_label]
                        )

                # User chose 'new' - let setup_auth.py handle the rest
                print()

            # Import and run the setup script
            setup_script_path = (
                Path(__file__).parent.parent.parent.parent
                / "scripts"
                / "setup"
                / "setup_auth.py"
            )

            if not setup_script_path.exists():
                print("❌ Setup script not found. Please run: python3 setup_auth.py")
                return 1

            # Execute the setup script
            result = subprocess.run(
                [sys.executable, str(setup_script_path)],
                capture_output=False,
                text=True,
            )
            
            # If setup was successful, offer PATH guidance
            if result.returncode == 0:
                self._offer_path_guidance()
            
            return result.returncode

        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return 1

    def _save_to_keychain(
        self, label: str, url: str, client_id: str, client_secret: str, auth_type: str
    ) -> bool:
        """Save credentials to macOS Keychain"""
        try:
            print(f"\n💾 Saving to keychain...")

            # Create service name for this credential set
            service_name = f"jpapi-{label}"
            account_name = f"{auth_type}@{url}"

            # For OAuth, save client_id as account and client_secret as password
            # Create a combined string with all info
            password_data = json.dumps(
                {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "url": url,
                    "auth_type": auth_type,
                }
            )

            # Check if entry exists
            check_cmd = [
                "security",
                "find-generic-password",
                "-s",
                service_name,
                "-a",
                account_name,
            ]

            existing = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
            )

            if existing.returncode == 0:
                # Update existing entry
                delete_cmd = [
                    "security",
                    "delete-generic-password",
                    "-s",
                    service_name,
                    "-a",
                    account_name,
                ]
                subprocess.run(delete_cmd, capture_output=True)

            # Add to keychain
            add_cmd = [
                "security",
                "add-generic-password",
                "-s",
                service_name,
                "-a",
                account_name,
                "-w",
                password_data,
                "-U",  # Update if exists
            ]

            result = subprocess.run(add_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✅ Saved to keychain as '{label}'")
                print(f"   Service: {service_name}")
                return True
            else:
                print(f"   ⚠️  Failed to save to keychain: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ⚠️  Could not save to keychain: {e}")
            return False

    def _save_to_unified_keychain(
        self, label: str, url: str, client_id: str, client_secret: str
    ) -> bool:
        """Save credentials to keychain in UnifiedJamfAuth format"""
        try:
            print(f"\n💾 Saving to keychain (UnifiedJamfAuth format)...")

            # Map label to service name and account name
            # UnifiedJamfAuth expects:
            # - service: jpapi_sandbox or jpapi_production
            # - account: sandbox or production (or dev/prod)
            service_mapping = {
                "dev": ("jpapi_sandbox", "sandbox"),
                "sandbox": ("jpapi_sandbox", "sandbox"),
                "prod": ("jpapi_production", "prod"),
                "production": ("jpapi_production", "prod"),
            }

            service_name, account_name = service_mapping.get(
                label.lower(), (f"jpapi_{label}", label)
            )

            # Create credential data as JSON (format expected by UnifiedJamfAuth)
            cred_data = json.dumps(
                {
                    "url": url,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "token": None,
                    "refresh_token": None,
                    "token_expires": None,
                }
            )

            # Delete existing entry if it exists
            delete_cmd = [
                "security",
                "delete-generic-password",
                "-s",
                service_name,
                "-a",
                account_name,
            ]
            subprocess.run(delete_cmd, capture_output=True, text=True)

            # Add new entry
            add_cmd = [
                "security",
                "add-generic-password",
                "-a",
                account_name,
                "-s",
                service_name,
                "-w",
                cred_data,
                "-U",  # Update if exists
            ]

            result = subprocess.run(add_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✅ Saved to keychain!")
                print(f"      Service: {service_name}")
                print(f"      Account: {account_name}")
                return True
            else:
                print(f"   ⚠️  Failed to save: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ⚠️  Could not save to keychain: {e}")
            return False

    def _detect_keychain_credentials(self) -> Dict[str, Dict[str, Any]]:
        """Detect existing JPAPI credentials in keychain"""
        credentials = {}

        try:
            # Known jpapi service and account combinations
            jpapi_entries = [
                ("jpapi_sandbox", "sandbox"),
                ("jpapi_production", "production"),
                ("jpapi_dev", "dev"),
                ("jpapi_prod", "prod"),
            ]

            for service, account in jpapi_entries:
                try:
                    # Try to load credentials directly
                    creds = self._load_keychain_entry(service, account)
                    if creds:
                        # Use friendly label
                        if "sandbox" in service.lower():
                            label = "sandbox"
                        elif "production" in service.lower():
                            label = "production"
                        elif "dev" in service.lower():
                            label = "dev"
                        elif "prod" in service.lower():
                            label = "prod"
                        else:
                            label = service.replace("jpapi_", "")

                        credentials[label] = creds
                except Exception:
                    # Skip this service if it fails
                    continue

            return credentials

        except Exception as e:
            # Silently fail - keychain detection is optional
            return {}

    def _load_keychain_entry(
        self, service: str, account: str
    ) -> Optional[Dict[str, Any]]:
        """Load a specific keychain entry"""
        try:
            result = subprocess.run(
                [
                    "security",
                    "find-generic-password",
                    "-s",
                    service,
                    "-a",
                    account,
                    "-w",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                creds_json = result.stdout.strip()
                if creds_json:
                    try:
                        return json.loads(creds_json)
                    except json.JSONDecodeError:
                        # Not JSON, might be old format - return basic info
                        return {"service": service, "account": account}

            return None

        except Exception:
            return None

    def _use_existing_credentials(self, label: str, credentials: Dict[str, Any]) -> int:
        """Use existing credentials from keychain"""
        try:
            print(f"\n✅ Using existing credentials for '{label}'")

            # Ask if they want to update or use as-is
            print("\nWhat would you like to do?")
            print("  1) Use these credentials as-is")
            print("  2) Update with new credentials (paste JSON)")
            print("  3) Cancel")

            choice = input("\nChoice (1-3): ").strip()

            if choice == "2":
                # Update credentials
                print("\n🔑 Update OAuth Credentials")
                print("   Paste the JSON from JAMF:")
                print('   (Example: {"client_id":"...","client_secret":"..."})')
                json_input = input("   JSON: ").strip()

                try:
                    new_creds = json.loads(json_input)
                    client_id = new_creds.get("client_id", "")
                    client_secret = new_creds.get("client_secret", "")

                    if not client_id or not client_secret:
                        print("   ⚠️  JSON doesn't contain client_id or client_secret")
                        return 1

                    # Update credentials in keychain
                    url = credentials.get("url", "")
                    print(f"\n   Updating credentials for: {url}")
                    self._save_to_unified_keychain(label, url, client_id, client_secret)

                    # Update local credentials dict
                    credentials["client_id"] = client_id
                    credentials["client_secret"] = client_secret

                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Invalid JSON format: {e}")
                    return 1
            elif choice == "3":
                print("   Cancelled")
                return 0

            # Save to the standard location
            config_path = Path("resources/config/authentication.json")
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare auth config
            auth_config = {
                "jamf_url": credentials.get("url", ""),
                "auth_method": "oauth" if credentials.get("client_id") else "basic",
                "oauth_client_id": credentials.get("client_id", ""),
                "oauth_client_secret": credentials.get("client_secret", ""),
                "oauth_redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "basic_username": credentials.get("username", ""),
                "basic_password": credentials.get("password", ""),
                "prefer_oauth": True,
                "fallback_to_basic": True,
                "auto_refresh_tokens": True,
                "token_cache_duration": 3600,
            }

            with open(config_path, "w") as f:
                json.dump(auth_config, f, indent=2)

            print(f"✅ Configuration saved to: {config_path}")

            # Test connection
            print("\n🧪 Testing connection...")
            return self._test_auth_connection(args=Namespace())

        except Exception as e:
            print(f"❌ Failed to use existing credentials: {e}")
            return 1

    def _setup_oauth_auth(self, args: Namespace) -> int:
        """Set up OAuth authentication with provided arguments"""
        try:
            # Get label (optional, defaults to 'dev')
            print("\n🏷️  Label")
            print(
                "   Give this credential set a name (e.g., sandbox, production, staging)"
            )
            label = input("   Label (default: sandbox): ").strip() or "sandbox"

            # Get URL
            print("\n🌐 JAMF Server URL")
            jamf_url = args.url
            if not jamf_url:
                jamf_url = input("   URL: ").strip()

            if not jamf_url:
                print("❌ URL is required!")
                return 1

            if not jamf_url.startswith(("http://", "https://")):
                jamf_url = "https://" + jamf_url

            # Get OAuth credentials - support JSON paste OR individual fields
            print("\n🔑 OAuth Credentials")
            print("   You can either:")
            print("   1) Paste the entire JSON from JAMF (recommended)")
            print("   2) Enter Client ID and Secret separately")
            print()

            client_id = args.client_id
            client_secret = args.client_secret

            if not client_id or not client_secret:
                choice = (
                    input("   Paste JSON or enter separately? (json/manual): ")
                    .strip()
                    .lower()
                )

                if choice in ["json", "j", ""]:
                    print("\n   Paste the JSON from JAMF:")
                    print('   (Example: {"client_id":"...","client_secret":"..."})')
                    json_input = input("   JSON: ").strip()

                    # Try to parse the JSON
                    try:
                        import json

                        creds = json.loads(json_input)
                        client_id = creds.get("client_id", "")
                        client_secret = creds.get("client_secret", "")

                        if not client_id or not client_secret:
                            print(
                                "   ⚠️  JSON doesn't contain client_id or client_secret"
                            )
                            print("   Falling back to manual entry...")
                            client_id = input("   Client ID: ").strip()
                            client_secret = input("   Client Secret: ").strip()
                    except json.JSONDecodeError:
                        print("   ⚠️  Invalid JSON format")
                        print("   Falling back to manual entry...")
                        client_id = input("   Client ID: ").strip()
                        client_secret = input("   Client Secret: ").strip()
                else:
                    client_id = input("   Client ID: ").strip()
                    client_secret = input("   Client Secret: ").strip()

            if not client_id or not client_secret:
                print("❌ Both Client ID and Client Secret are required!")
                return 1

            # Create auth config
            auth_config = {
                "label": label,
                "jamf_url": jamf_url,
                "auth_method": "oauth",
                "oauth_client_id": client_id,
                "oauth_client_secret": client_secret,
                "oauth_redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "basic_username": "",
                "basic_password": "",
                "prefer_oauth": True,
                "fallback_to_basic": True,
                "auto_refresh_tokens": True,
                "token_cache_duration": 3600,
            }

            # Save configuration
            config_path = Path("resources/config/authentication.json")
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w") as f:
                json.dump(auth_config, f, indent=2)

            print(f"\n✅ OAuth authentication configured successfully!")
            print(f"   Label: {label}")
            print(f"   URL: {jamf_url}")
            print(f"   Configuration saved to: {config_path}")

            # Save to keychain for UnifiedJamfAuth compatibility
            self._save_to_unified_keychain(label, jamf_url, client_id, client_secret)

            # Test connection
            result = self._test_auth_connection(args)
            
            # Offer PATH guidance if setup was successful
            if result == 0:
                self._offer_path_guidance()
            
            return result

        except Exception as e:
            print(f"❌ OAuth setup failed: {e}")
            return 1

    def _setup_basic_auth(self, args: Namespace) -> int:
        """Set up basic authentication with provided arguments"""
        try:
            # Get URL
            jamf_url = args.url
            if not jamf_url:
                jamf_url = input("Enter JAMF Pro URL: ").strip()

            if not jamf_url:
                print("❌ URL is required!")
                return 1

            if not jamf_url.startswith(("http://", "https://")):
                jamf_url = "https://" + jamf_url

            # Get basic auth credentials
            username = args.username
            if not username:
                username = input("Enter username: ").strip()

            password = args.password
            if not password:
                password = input("Enter password: ").strip()

            if not username or not password:
                print("❌ Both username and password are required!")
                return 1

            # Create auth config
            auth_config = {
                "jamf_url": jamf_url,
                "auth_method": "basic",
                "basic_username": username,
                "basic_password": password,
                "oauth_client_id": "",
                "oauth_client_secret": "",
                "oauth_redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "prefer_oauth": False,
                "fallback_to_basic": True,
                "auto_refresh_tokens": False,
                "token_cache_duration": 3600,
            }

            # Save configuration
            config_path = Path("resources/config/authentication.json")
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w") as f:
                json.dump(auth_config, f, indent=2)

            print("✅ Basic authentication configured successfully!")
            print(f"   Configuration saved to: {config_path}")

            # Test connection
            result = self._test_auth_connection(args)
            
            # Offer PATH guidance if setup was successful
            if result == 0:
                self._offer_path_guidance()
            
            return result

        except Exception as e:
            print(f"❌ Basic auth setup failed: {e}")
            return 1

    def _test_auth_connection(self, args: Namespace) -> int:
        """Test the current authentication configuration"""
        try:
            print("🔍 Testing authentication...")

            # Check if config exists
            config_path = Path("resources/config/authentication.json")
            if not config_path.exists():
                print("❌ No authentication configuration found!")
                print("   Run: jpapi setup auth")
                return 1

            # Load config
            with open(config_path, "r") as f:
                config = json.load(f)

            print(f"   Server: {config.get('jamf_url', 'Not set')}")
            print(f"   Method: {config.get('auth_method', 'Not set')}")

            # Test authentication
            from core.auth.login_manager import UnifiedJamfAuth

            auth = UnifiedJamfAuth(environment=getattr(self, "environment", "sandbox"))
            token_result = auth.get_token()

            if hasattr(token_result, "success") and token_result.success:
                print("   ✅ Authentication successful!")
                print("   🎉 You're ready to use JPAPI!")
                return 0
            else:
                print("   ❌ Authentication failed!")
                print("   💡 Check your credentials and try: jpapi setup auth")
                return 1

        except Exception as e:
            print(f"   ❌ Authentication test failed: {e}")
            print("   💡 Try running: jpapi setup auth")
            return 1

    def _offer_path_guidance(self) -> None:
        """Offer optional PATH configuration guidance if jpapi is not in PATH"""
        try:
            # Check if jpapi command is available in PATH
            result = subprocess.run(
                ["which", "jpapi"],
                capture_output=True,
                text=True,
            )
            
            # Also check if symlink exists
            home_dir = os.path.expanduser("~")
            symlink_path = f"{home_dir}/.local/bin/jpapi"
            symlink_exists = os.path.exists(symlink_path) or os.path.islink(symlink_path)
            
            if result.returncode == 0:
                # jpapi is in PATH, no guidance needed
                return
            
            # If symlink doesn't exist, don't offer PATH guidance
            if not symlink_exists:
                return
            
            # jpapi is not in PATH, offer guidance
            print("\n" + "=" * 60)
            print("📝 Optional: Add jpapi to your PATH")
            print("=" * 60)
            print()
            print("The 'jpapi' command is not in your PATH.")
            print("You can use it in one of these ways:")
            print()
            print("Option 1: Use the full path")
            print("  /Users/{}/.jpapi/venv/bin/jpapi <command>".format(os.getenv("USER", "user")))
            print()
            print("Option 2: Add to PATH (recommended)")
            print("  Add this line to your ~/.zshrc or ~/.bashrc:")
            print('  export PATH="$HOME/.local/bin:$PATH"')
            print()
            print("  Then reload your shell:")
            print("  source ~/.zshrc  # or source ~/.bashrc")
            print()
            print("Option 3: Create an alias")
            print("  Add this to your ~/.zshrc or ~/.bashrc:")
            print('  alias jpapi="/Users/{}/.jpapi/venv/bin/jpapi"'.format(os.getenv("USER", "user")))
            print()
            
            # Try to detect the installation path
            home_dir = os.path.expanduser("~")
            jpapi_path = f"{home_dir}/.jpapi/venv/bin/jpapi"
            if os.path.exists(jpapi_path):
                print(f"  Your jpapi installation: {jpapi_path}")
                print()
            
            response = input("Would you like to add jpapi to your PATH now? (y/N): ").strip().lower()
            
            if response in ["y", "yes"]:
                self._add_to_path()
            else:
                print("  ✅ You can add it later using the instructions above.")
                print()
        
        except Exception:
            # Silently fail - this is optional guidance
            pass

    def _add_to_path(self) -> None:
        """Add jpapi to user's PATH"""
        try:
            home_dir = os.path.expanduser("~")
            shell = os.getenv("SHELL", "")
            
            # Determine which config file to use
            if "zsh" in shell:
                config_file = f"{home_dir}/.zshrc"
            else:
                config_file = f"{home_dir}/.bashrc"
            
            # Check if already added
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    content = f.read()
                    if '.local/bin' in content:
                        print(f"  ✅ PATH already configured in {config_file}")
                        print(f"  Run: source {config_file}")
                        return
            
            # Add PATH export
            path_line = 'export PATH="$HOME/.local/bin:$PATH"\n'
            
            try:
                with open(config_file, "a") as f:
                    f.write("\n# JPAPI - Add to PATH\n")
                    f.write(path_line)
                
                print(f"  ✅ Added to {config_file}")
                print(f"  Run: source {config_file}")
                print("  Or restart your terminal")
                
            except PermissionError:
                print(f"  ⚠️  Cannot write to {config_file} (permission denied)")
                print(f"  Please manually add this line to {config_file}:")
                print(f"  {path_line.strip()}")
            except Exception as e:
                print(f"  ⚠️  Could not update {config_file}: {e}")
                print(f"  Please manually add this line to {config_file}:")
                print(f"  {path_line.strip()}")
        
        except Exception as e:
            print(f"  ⚠️  Could not add to PATH: {e}")
            print("  Please use Option 1 (full path) or manually configure PATH")
