#!/usr/bin/env python3
"""
JPAPI Credential Update Tool
Simple tool to update JAMF Pro API credentials in keychain
"""

import keyring
import json
import sys
import requests
import base64


def test_credentials(client_id, client_secret, url):
    """Test if credentials work"""
    try:
        token_url = f"{url}/api/oauth/token"
        auth_string = f"{client_id}:{client_secret}"
        auth_header = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "client_credentials"}

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            print(
                f"✅ Credentials work! Token expires in {token_data.get('expires_in', 'unknown')} seconds"
            )
            return True
        else:
            print(f"❌ Credentials failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def update_credentials(environment, client_id, client_secret, url, client_name=None):
    """Update credentials in keychain"""
    try:
        keychain_name = f"jpapi_{environment}"

        # Test credentials first
        print(f"Testing credentials for {environment}...")
        if not test_credentials(client_id, client_secret, url):
            print("❌ Credentials test failed. Not updating keychain.")
            return False

        # Create credentials object
        creds = {
            "url": url.rstrip("/"),
            "client_id": client_id,
            "client_secret": client_secret,
            "client_name": client_name or f"jpapi_{environment}",
            "grant_type": "client_credentials",
            "content_type": "application/x-www-form-urlencoded",
        }

        # Update both common account names
        for account in [
            environment,
            "dev" if environment == "sandbox" else "prod",
            "production" if environment == "production" else "sandbox",
        ]:
            keyring.set_password(keychain_name, account, json.dumps(creds))
            print(f"✅ Updated {keychain_name}/{account}")

        return True

    except Exception as e:
        print(f"❌ Failed to update credentials: {e}")
        return False


def main():
    print("🔑 JPAPI Credential Update Tool")
    print("=" * 40)

    if len(sys.argv) < 3:
        print(
            "Usage: python3 update_credentials.py <environment> <client_id> <client_secret> <url> [client_name]"
        )
        print()
        print("Example:")
        print(
            "  python3 update_credentials.py sandbox YOUR_CLIENT_ID YOUR_CLIENT_SECRET https://your-company.jamfcloud.com"
        )
        print()
        print("Or paste the JSON from JAMF Pro:")
        print(
            '  python3 update_credentials.py sandbox \'{"client_id":"...","client_secret":"...","url":"..."}\''
        )
        return 1

    environment = sys.argv[1]

    # Check if second argument is JSON
    if sys.argv[2].startswith("{"):
        try:
            creds_json = json.loads(sys.argv[2])
            client_id = creds_json["client_id"]
            client_secret = creds_json["client_secret"]
            url = creds_json.get("url", "")
            client_name = creds_json.get("client_name")
        except json.JSONDecodeError:
            print("❌ Invalid JSON format")
            return 1
    else:
        if len(sys.argv) < 5:
            print(
                "❌ Need at least 4 arguments: environment, client_id, client_secret, url"
            )
            return 1
        client_id = sys.argv[2]
        client_secret = sys.argv[3]
        url = sys.argv[4]
        client_name = sys.argv[5] if len(sys.argv) > 5 else None

    print(f"Environment: {environment}")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:20]}...")
    print(f"URL: {url}")
    print()

    if update_credentials(environment, client_id, client_secret, url, client_name):
        print(f"\n🎉 Successfully updated {environment} credentials!")
        print("You can now run: ./bin/jpapi --env sandbox export policies --format csv")
        return 0
    else:
        print(f"\n❌ Failed to update {environment} credentials")
        return 1


if __name__ == "__main__":
    sys.exit(main())
