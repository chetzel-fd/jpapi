#!/usr/bin/env python3
"""
Simple JPAPI Authentication Setup
User-friendly setup for first-time users
"""

import json
import os
import sys
from pathlib import Path


def main():
    print("🔐 JPAPI Authentication Setup")
    print("=" * 40)
    print("Let's get you connected to JAMF Pro!")
    print()

    # Get JAMF Pro URL
    print("1. JAMF Pro Server URL")
    print(
        "   Enter your JAMF Pro server URL (e.g., https://your-company.jamfcloud.com)"
    )
    jamf_url = input("   URL: ").strip()

    if not jamf_url:
        print("❌ URL is required!")
        return 1

    if not jamf_url.startswith(("http://", "https://")):
        jamf_url = "https://" + jamf_url

    print()
    print("2. Authentication Method")
    print("   Choose how you want to authenticate:")
    print("   1) OAuth (recommended for production)")
    print("   2) Basic Authentication (username/password)")

    while True:
        choice = input("   Enter 1 or 2: ").strip()
        if choice in ["1", "2"]:
            break
        print("   Please enter 1 or 2")

    auth_config = {
        "jamf_url": jamf_url,
        "prefer_oauth": choice == "1",
        "fallback_to_basic": True,
        "auto_refresh_tokens": True,
        "token_cache_duration": 3600,
    }

    if choice == "1":
        print()
        print("3. OAuth Credentials")
        print("   You'll need to create an OAuth client in JAMF Pro:")
        print("   - Go to Settings > Global Management > API Roles & Clients")
        print("   - Create a new client with 'Full Access' scope")
        print("   - JAMF will show you a JSON response")
        print()
        print("   💡 TIP: You can paste the entire JSON from JAMF!")
        print()

        paste_choice = (
            input("   Paste entire JSON or enter separately? (json/manual) [json]: ")
            .strip()
            .lower()
            or "json"
        )

        if paste_choice in ["json", "j"]:
            print()
            print("   Paste the JSON from JAMF:")
            print('   Example: {"client_id":"abc-123","client_secret":"xyz-789",...}')
            print()
            json_input = input("   JSON: ").strip()

            try:
                creds = json.loads(json_input)
                client_id = creds.get("client_id", "")
                client_secret = creds.get("client_secret", "")

                if client_id and client_secret:
                    print(f"   ✅ Parsed: Client ID = {client_id[:20]}...")
                else:
                    print("   ⚠️  Could not find client_id or client_secret in JSON")
                    print("   Please enter them manually:")
                    client_id = input("   Client ID: ").strip()
                    client_secret = input("   Client Secret: ").strip()
            except json.JSONDecodeError as e:
                print(f"   ⚠️  Invalid JSON: {e}")
                print("   Please enter credentials manually:")
                client_id = input("   Client ID: ").strip()
                client_secret = input("   Client Secret: ").strip()
        else:
            client_id = input("   Client ID: ").strip()
            client_secret = input("   Client Secret: ").strip()

        if not client_id or not client_secret:
            print("❌ Both Client ID and Client Secret are required!")
            return 1

        auth_config.update(
            {
                "auth_method": "oauth",
                "oauth_client_id": client_id,
                "oauth_client_secret": client_secret,
                "oauth_redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "basic_username": "",
                "basic_password": "",
            }
        )

    else:
        print()
        print("3. Basic Authentication")
        print("   Enter your JAMF Pro username and password")

        username = input("   Username: ").strip()
        password = input("   Password: ").strip()

        if not username or not password:
            print("❌ Both username and password are required!")
            return 1

        auth_config.update(
            {
                "auth_method": "basic",
                "basic_username": username,
                "basic_password": password,
                "oauth_client_id": "",
                "oauth_client_secret": "",
                "oauth_redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            }
        )

    # Save configuration
    config_path = Path("resources/config/authentication.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(auth_config, f, indent=2)

    print()
    print("✅ Authentication configured successfully!")
    print(f"   Configuration saved to: {config_path}")
    print()

    # Test the configuration
    print("4. Testing Connection")
    print("   Testing your JAMF Pro connection...")

    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from core.auth.login_manager import UnifiedJamfAuth

        auth = UnifiedJamfAuth(environment="dev")
        token_result = auth.get_token()

        if hasattr(token_result, "success") and token_result.success:
            print("   ✅ Connection successful!")
            print("   🎉 You're ready to use JPAPI!")
        else:
            print("   ⚠️  Connection test failed, but configuration was saved.")
            print("   You can try running the export command to test again.")

    except Exception as e:
        print(f"   ⚠️  Could not test connection: {e}")
        print("   Configuration was saved - you can try the export command.")

    print()
    print("🚀 Next Steps:")
    print("   1. Try: python3 jpapi_main.py export 'advanced searches' --format csv")
    print("   2. Or: python3 jpapi_main.py list policies")
    print("   3. Run: python3 jpapi_main.py --help for more commands")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
