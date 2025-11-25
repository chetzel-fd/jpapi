#!/usr/bin/env python3
"""
Jira Authentication Setup Script
Mirrors JPAPI's setup_auth.py but for Jira authentication
"""

import sys
import os
import getpass
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.auth.jira_auth import JiraAuth, JiraAuthCredentials


def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🔧 Jira Toolkit Authentication Setup")
    print("=" * 60)
    print()


def get_environment():
    """Get environment selection"""
    print("📋 Select Environment:")
    print("1) Development")
    print("2) Staging")
    print("3) Production")
    print()

    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice == "1":
            return "dev"
        elif choice == "2":
            return "staging"
        elif choice == "3":
            return "prod"
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


def get_jira_url():
    """Get Jira URL"""
    print()
    print("🌐 Jira Server Configuration:")
    print("Enter your Jira server URL (e.g., https://yourcompany.atlassian.net)")

    while True:
        url = input("Jira URL: ").strip()
        if not url:
            print("❌ URL cannot be empty.")
            continue

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        return url


def get_auth_method():
    """Get authentication method"""
    print()
    print("🔐 Authentication Method:")
    print("1) API Token (Recommended)")
    print("2) Username/Password (Basic Auth)")
    print()

    while True:
        choice = input("Enter choice (1-2): ").strip()
        if choice == "1":
            return "api_token"
        elif choice == "2":
            return "basic"
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")


def get_credentials(auth_method):
    """Get authentication credentials"""
    print()
    print("👤 Authentication Credentials:")

    username = input("Username/Email: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return None

    if auth_method == "api_token":
        print()
        print("🔑 API Token:")
        print("To get your API token:")
        print("1. Go to https://id.atlassian.com/manage-profile/security/api-tokens")
        print("2. Click 'Create API token'")
        print("3. Give it a label (e.g., 'Jira Toolkit')")
        print("4. Copy the generated token")
        print()

        api_token = getpass.getpass("API Token: ").strip()
        if not api_token:
            print("❌ API token cannot be empty.")
            return None

        return {
            "username": username,
            "api_token": api_token,
            "auth_method": "api_token",
        }

    else:  # basic auth
        password = getpass.getpass("Password: ").strip()
        if not password:
            print("❌ Password cannot be empty.")
            return None

        return {"username": username, "password": password, "auth_method": "basic"}


def test_connection(auth, credentials):
    """Test the Jira connection"""
    print()
    print("🧪 Testing Connection...")

    try:
        # Store credentials temporarily for testing
        temp_creds = JiraAuthCredentials(
            url=credentials["url"],
            username=credentials["username"],
            password=credentials.get("password"),
            api_token=credentials.get("api_token"),
            auth_method=credentials["auth_method"],
        )

        # Test API call
        result = auth.api_request("GET", "myself")

        if result and "accountId" in result:
            print("✅ Connection successful!")
            print(f"   Logged in as: {result.get('displayName', 'Unknown')}")
            print(f"   Account ID: {result.get('accountId', 'Unknown')}")
            return True
        else:
            print("❌ Connection failed: Invalid response")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def save_credentials(auth, credentials):
    """Save credentials securely"""
    print()
    print("💾 Saving Credentials...")

    try:
        # Convert to AuthCredentials format for compatibility
        from core.auth.login_types import AuthCredentials

        auth_creds = AuthCredentials(
            url=credentials["url"],
            client_id=credentials["username"],  # Map username to client_id
            client_secret=credentials.get("password")
            or credentials.get("api_token"),  # Map to client_secret
            token=credentials.get("api_token"),  # Map api_token to token
        )

        success = auth.store_credentials(auth_creds)

        if success:
            print("✅ Credentials saved securely!")
            return True
        else:
            print("❌ Failed to save credentials.")
            return False

    except Exception as e:
        print(f"❌ Error saving credentials: {str(e)}")
        return False


def main():
    """Main setup function"""
    print_banner()

    try:
        # Get environment
        environment = get_environment()

        # Initialize auth
        auth = JiraAuth(environment=environment, backend="keychain")

        # Get Jira URL
        jira_url = get_jira_url()

        # Get authentication method
        auth_method = get_auth_method()

        # Get credentials
        cred_data = get_credentials(auth_method)
        if not cred_data:
            print("❌ Setup cancelled.")
            return 1

        # Add URL to credentials
        cred_data["url"] = jira_url

        # Test connection
        if not test_connection(auth, cred_data):
            print()
            print("❌ Setup failed. Please check your credentials and try again.")
            return 1

        # Save credentials
        if not save_credentials(auth, cred_data):
            print()
            print("❌ Setup failed. Could not save credentials.")
            return 1

        # Success
        print()
        print("🎉 Setup Complete!")
        print()
        print("Your Jira authentication is now configured.")
        print(f"Environment: {environment}")
        print(f"Jira URL: {jira_url}")
        print(f"Auth Method: {auth_method}")
        print()
        print("You can now use the Jira toolkit with this configuration.")

        return 0

    except KeyboardInterrupt:
        print()
        print("❌ Setup cancelled by user.")
        return 1
    except Exception as e:
        print()
        print(f"❌ Setup failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

