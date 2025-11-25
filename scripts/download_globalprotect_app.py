#!/usr/bin/env python3
"""
Native macOS app version of GlobalProtect downloader.

Uses native macOS dialogs (osascript) for the best user experience.
Can be packaged as a .app bundle for easy distribution.
"""

import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Optional, Tuple
import getpass

try:
    from oktaloginwrapper import OktaLoginWrapper as OLW
    OKTA_WRAPPER_AVAILABLE = True
except ImportError:
    OKTA_WRAPPER_AVAILABLE = False


class KeychainManager:
    """Manage Okta credentials in macOS Keychain."""
    
    SERVICE_NAME = "GlobalProtect_Okta"
    ACCOUNT_NAME = "fanduel_okta"
    SUPER_UPDATE_SERVICE = "Super Update Service"
    
    KEYCHAIN_SEARCH_TERMS = [
        "fanduel.com",
        "okta.com",
        "fanduel",
        "okta",
    ]
    
    @staticmethod
    def generate_username_from_system() -> str:
        """Generate username from system username as firstname.lastname@fanduel.com"""
        try:
            import os
            import pwd
            
            # Get current system username
            system_user = os.getenv('USER') or os.getenv('USERNAME') or os.getlogin()
            
            # Try to get full name from system
            try:
                user_info = pwd.getpwnam(system_user)
                full_name = user_info.pw_gecos.split(',')[0] if user_info.pw_gecos else system_user
            except (KeyError, AttributeError):
                full_name = system_user
            
            # Convert to firstname.lastname format
            # Handle various formats: "First Last", "FirstLast", "first.last", etc.
            if '.' in full_name or '@' in full_name:
                # Already in correct format or has email
                if '@' in full_name:
                    return full_name  # Already an email
                return f"{full_name}@fanduel.com"
            elif ' ' in full_name:
                # "First Last" -> "first.last"
                parts = full_name.split()
                if len(parts) >= 2:
                    return f"{parts[0].lower()}.{parts[-1].lower()}@fanduel.com"
                else:
                    return f"{full_name.lower()}@fanduel.com"
            else:
                # Single word - try to split if camelCase or use as-is
                # For now, just use as firstname.lastname (assuming it's already in that format)
                return f"{full_name.lower()}@fanduel.com"
        except Exception:
            # Fallback to system username
            import os
            system_user = os.getenv('USER') or os.getenv('USERNAME') or 'user'
            return f"{system_user.lower()}@fanduel.com"
    
    @staticmethod
    def find_super_update_service_credentials() -> Optional[Tuple[str, str]]:
        """Find credentials from 'Super Update Service' keychain entry."""
        try:
            # Search for "Super Update Service" in generic passwords
            cmd = [
                "security",
                "find-generic-password",
                "-l", KeychainManager.SUPER_UPDATE_SERVICE,
                "-g"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Extract account (username) from output
                username = None
                for line in result.stdout.split('\n'):
                    if 'acct"' in line or '"acct"' in line or 'account:' in line.lower():
                        # Try to extract account name
                        if 'acct"' in line:
                            parts = line.split('"')
                            if len(parts) >= 2:
                                username = parts[-2]
                        elif 'account:' in line.lower():
                            username = line.split('account:')[-1].strip().strip('"')
                        break
                
                if username:
                    # Get the password
                    cmd_pass = [
                        "security",
                        "find-generic-password",
                        "-l", KeychainManager.SUPER_UPDATE_SERVICE,
                        "-a", username,
                        "-w"
                    ]
                    pass_result = subprocess.run(cmd_pass, capture_output=True, text=True, timeout=5)
                    if pass_result.returncode == 0 and pass_result.stdout.strip():
                        return (username, pass_result.stdout.strip())
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def find_existing_keychain_entry() -> Optional[Tuple[str, str]]:
        """Search for existing keychain entries."""
        try:
            # First, try "Super Update Service" (highest priority)
            super_update_creds = KeychainManager.find_super_update_service_credentials()
            if super_update_creds:
                return super_update_creds
            
            # Try our specific service
            cmd = [
                "security",
                "find-generic-password",
                "-a", KeychainManager.ACCOUNT_NAME,
                "-s", KeychainManager.SERVICE_NAME,
                "-w"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                try:
                    cred_data = json.loads(result.stdout.strip())
                    username = cred_data.get("username")
                    password = cred_data.get("password")
                    if username and password:
                        return (username, password)
                except json.JSONDecodeError:
                    pass
            
            # Try internet passwords
            for term in KeychainManager.KEYCHAIN_SEARCH_TERMS:
                # Get account name
                cmd_account = [
                    "security",
                    "find-internet-password",
                    "-s", term,
                    "-g"
                ]
                account_result = subprocess.run(cmd_account, capture_output=True, text=True, timeout=5)
                if account_result.returncode == 0:
                    username = None
                    for line in account_result.stdout.split('\n'):
                        if 'acct"' in line or '"acct"' in line:
                            parts = line.split('"')
                            if len(parts) >= 2:
                                username = parts[-2]
                                break
                    
                    if username:
                        # Get password
                        cmd_pass = [
                            "security",
                            "find-internet-password",
                            "-s", term,
                            "-a", username,
                            "-w"
                        ]
                        pass_result = subprocess.run(cmd_pass, capture_output=True, text=True, timeout=5)
                        if pass_result.returncode == 0 and pass_result.stdout.strip():
                            return (username, pass_result.stdout.strip())
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_username_from_keychain() -> Optional[str]:
        """Try to extract username from keychain entries."""
        try:
            # First try Super Update Service
            super_update_creds = KeychainManager.find_super_update_service_credentials()
            if super_update_creds:
                return super_update_creds[0]
            
            creds = KeychainManager.find_existing_keychain_entry()
            if creds:
                return creds[0]
            
            # Search for any internet password with email-like account
            for term in KeychainManager.KEYCHAIN_SEARCH_TERMS:
                cmd = [
                    "security",
                    "find-internet-password",
                    "-s", term,
                    "-g"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'acct"' in line or '"acct"' in line:
                            parts = line.split('"')
                            if len(parts) >= 2:
                                username = parts[-2]
                                if '@' in username and 'fanduel.com' in username:
                                    return username
            
            # Fallback to generated username
            return KeychainManager.generate_username_from_system()
        except Exception:
            return KeychainManager.generate_username_from_system()
    
    @staticmethod
    def store_credentials(username: str, password: str) -> bool:
        """Store credentials in macOS Keychain."""
        try:
            cred_data = json.dumps({
                "username": username,
                "password": password
            })
            
            # Delete existing entry
            subprocess.run([
                "security",
                "delete-generic-password",
                "-a", KeychainManager.ACCOUNT_NAME,
                "-s", KeychainManager.SERVICE_NAME
            ], capture_output=True, timeout=5)
            
            # Add new entry
            cmd = [
                "security",
                "add-generic-password",
                "-a", KeychainManager.ACCOUNT_NAME,
                "-s", KeychainManager.SERVICE_NAME,
                "-w", cred_data,
                "-U"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False


class NativeDialog:
    """Native macOS dialog using osascript."""
    
    @staticmethod
    def show_info(title: str, message: str) -> None:
        """Show info dialog."""
        script = f'''
        tell application "System Events"
            display dialog "{message}" buttons {{"OK"}} default button "OK" with title "{title}" with icon note
        end tell
        '''
        subprocess.run(["osascript", "-e", script], capture_output=True)
    
    @staticmethod
    def show_error(title: str, message: str) -> None:
        """Show error dialog."""
        script = f'''
        tell application "System Events"
            display dialog "{message}" buttons {{"OK"}} default button "OK" with title "{title}" with icon stop
        end tell
        '''
        subprocess.run(["osascript", "-e", script], capture_output=True)
    
    @staticmethod
    def show_question(title: str, message: str, buttons: list = None) -> str:
        """Show question dialog, returns button text."""
        if buttons is None:
            buttons = ["Yes", "No"]
        
        buttons_str = "{" + ", ".join([f'"{b}"' for b in buttons]) + "}"
        default_button = f'default button "{buttons[0]}"'
        
        script = f'''
        tell application "System Events"
            set result to display dialog "{message}" buttons {buttons_str} {default_button} with title "{title}"
            return button returned of result
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else buttons[0]
    
    @staticmethod
    def get_text_input(title: str, message: str, default_text: str = "") -> Optional[str]:
        """Get text input from user."""
        # Escape special characters for AppleScript
        default_text = default_text.replace('\\', '\\\\').replace('"', '\\"')
        message = message.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        title = title.replace('\\', '\\\\').replace('"', '\\"')
        
        script = f'''
        try
            display dialog "{message}" default answer "{default_text}" with title "{title}" buttons {{"OK", "Cancel"}} default button "OK"
            set result to text returned of result
            return result
        on error number -128
            return ""
        on error errMsg
            return ""
        end try
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    
    @staticmethod
    def get_password_input(title: str, message: str) -> Optional[str]:
        """Get password input (hidden) from user."""
        import os
        from pathlib import Path
        
        # Try using a shell script wrapper to avoid Python subprocess issues
        script_dir = Path(__file__).parent if '__file__' in globals() else Path('.')
        helper_script = script_dir / "get_password.sh"
        
        if helper_script.exists():
            try:
                # Escape message for shell
                message_escaped = message.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
                title_escaped = title.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
                
                result = subprocess.run(
                    [str(helper_script), message_escaped, title_escaped],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    password = result.stdout.strip()
                    if password:
                        return password
            except Exception:
                pass  # Fall back to direct osascript
        
        # Fallback to direct osascript call
        message_clean = message.replace('\n', ' ').replace('\\', '\\\\').replace('"', '\\"')
        title_clean = title.replace('\\', '\\\\').replace('"', '\\"')
        
        script = f'''try
    set theDialog to display dialog "{message_clean}" default answer "" with title "{title_clean}" buttons {{"OK", "Cancel"}} default button "OK" with hidden answer
    set theAnswer to text returned of theDialog
    return theAnswer
on error number -128
    return ""
on error
    return ""
end try'''
        
        try:
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if "text returned:" in output:
                    password = output.split("text returned:")[-1].strip()
                    if password:
                        return password
                elif output and "button returned" not in output:
                    return output
        except Exception:
            pass
        
        return None


class GlobalProtectDownloader:
    """Main downloader with native macOS integration."""
    
    def __init__(self, okta_instance: str = "fanduel",
                 download_url: str = "https://secure.fanduel.com/global-protect/getmsi.esp?version=none&platform=mac"):
        self.okta_instance = okta_instance
        self.download_url = download_url
        self.username = None
        self.password = None
        self.dialog = NativeDialog()
    
    def get_credentials(self) -> bool:
        """Get credentials from keychain or user input."""
        print("DEBUG: get_credentials() called")
        
        # Try keychain first
        creds = KeychainManager.find_existing_keychain_entry()
        print(f"DEBUG: Keychain creds found: {creds is not None}")
        if creds and creds[0] and creds[1]:
            self.username = creds[0]
            self.password = creds[1]
            print("DEBUG: Using credentials from keychain")
            return True
        
        # Get username - try keychain first, then generate from system
        username = KeychainManager.get_username_from_keychain()
        print(f"DEBUG: Username from keychain: {username}")
        if not username:
            username = KeychainManager.generate_username_from_system()
            print(f"DEBUG: Generated username: {username}")
        
        # If we have username but no password, try to get password from Super Update Service
        if username:
            # Try to get password for this specific username from Super Update Service
            super_update_creds = KeychainManager.find_super_update_service_credentials()
            if super_update_creds and super_update_creds[0] == username:
                self.username = username
                self.password = super_update_creds[1]
                print("DEBUG: Using credentials from Super Update Service")
                return True
        
        # Need to prompt for password (username is auto-filled)
        print(f"DEBUG: About to show password dialog for {username}")
        password = self.dialog.get_password_input(
            "GlobalProtect Downloader",
            f"Enter your Okta password for {username}:"
        )
        print(f"DEBUG: Password dialog returned: {'Yes' if password else 'No/None'}")
        
        if not password:
            print("DEBUG: No password provided")
            return False
        
        self.username = username
        self.password = password
        print(f"DEBUG: Credentials set for {username}")
        return True
    
    def download(self, output_path: Optional[Path] = None) -> bool:
        """Download GlobalProtect.pkg."""
        if not OKTA_WRAPPER_AVAILABLE:
            self.dialog.show_error(
                "Error",
                "oktaloginwrapper is required.\n\nInstall with: pip install oktaloginwrapper"
            )
            return False
        
        if not self.username or not self.password:
            self.dialog.show_error("Error", "Username and password are required")
            return False
        
        if output_path is None:
            output_path = Path.home() / "Downloads" / "GlobalProtect.pkg"
        
        # Show progress dialog
        self.dialog.show_info(
            "GlobalProtect Downloader",
            f"Authenticating as {self.username}...\n\nThis may take a moment."
        )
        
        try:
            # Initialize Okta session
            okta_url = f"https://{self.okta_instance}.okta.com"
            session = OLW.OktaSession(okta_url)
            
            # Authenticate
            session.okta_auth(username=self.username, password=self.password)
            
            # Download
            response = session.session.get(self.download_url, timeout=60, stream=True)
            
            if response.status_code == 200:
                # Handle redirects
                if 'text/html' in response.headers.get('Content-Type', ''):
                    content = response.text
                    if 'GlobalProtect.pkg' in content:
                        match = re.search(r'["\']([^"\']*GlobalProtect\.pkg[^"\']*)["\']', content)
                        if match:
                            pkg_url = match.group(1)
                            if not pkg_url.startswith('http'):
                                pkg_url = f"https://secure.fanduel.com/global-protect/{pkg_url.lstrip('/')}"
                            response = session.session.get(pkg_url, timeout=60, stream=True)
                
                # Save file
                output_path.parent.mkdir(parents=True, exist_ok=True)
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                
                # Store credentials for next time
                KeychainManager.store_credentials(self.username, self.password)
                
                # Show success
                self.dialog.show_info(
                    "Success",
                    f"GlobalProtect downloaded successfully!\n\nLocation: {output_path}\n\nSize: {output_path.stat().st_size:,} bytes"
                )
                
                return True
            else:
                self.dialog.show_error(
                    "Download Failed",
                    f"Failed to download GlobalProtect.\n\nStatus code: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.dialog.show_error(
                "Error",
                f"An error occurred:\n\n{str(e)}"
            )
            return False


def main():
    """Main entry point."""
    try:
        downloader = GlobalProtectDownloader()
        
        print("🔐 GlobalProtect Downloader")
        print("=" * 60)
        print("Checking for credentials...")
        
        if not downloader.get_credentials():
            print("❌ Failed to get credentials")
            return 1
        
        print(f"✅ Got credentials for: {downloader.username}")
        print("Starting download...")
        
        success = downloader.download()
        
        if success:
            print("✅ Download completed successfully!")
        else:
            print("❌ Download failed")
        
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

