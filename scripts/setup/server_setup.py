#!/usr/bin/env python3
"""
Server Setup Tool
Professional tool for adding new JAMF Pro servers to jpapi
"""

import sys
import json
import getpass
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def add_server(label, url, client_id, client_secret, environment="production"):
    """Add a new JAMF Pro server to keychain"""
    try:
        # Create credentials object
        credentials = {
            "url": url,
            "client_id": client_id,
            "client_secret": client_secret,
            "environment": environment,
            "created_at": str(int(time.time())),
            "last_used": str(int(time.time())),
        }

        # Store in keychain
        service_name = f"jpapi_{label}"
        cmd = [
            "security",
            "add-generic-password",
            "-a",
            label,
            "-s",
            service_name,
            "-w",
            json.dumps(credentials),
            "-U",  # Update if exists
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Successfully added server '{label}'")
            return True
        else:
            print(f"❌ Failed to add server: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error adding server: {e}")
        return False


def list_servers():
    """List all configured servers"""
    try:
        result = subprocess.run(
            ["security", "dump-keychain"], capture_output=True, text=True
        )
        if result.returncode == 0:
            servers = []
            lines = result.stdout.split("\n")
            for line in lines:
                if '"svce"<blob>="jpapi_' in line:
                    service = line.split('"svce"<blob>="jpapi_')[1].split('"')[0]
                    servers.append(service)
            return servers
        return []
    except Exception:
        return []


def test_connection(label):
    """Test connection to a server"""
    try:
        from core.auth.login_manager import UnifiedJamfAuth

        auth = UnifiedJamfAuth(environment=label, backend="keychain")

        if auth.is_configured():
            token_result = auth.get_token()
            if token_result.success:
                print(f"✅ Connection to '{label}' successful!")
                return True
            else:
                print(f"❌ Connection failed: {token_result.message}")
                return False
        else:
            print(f"❌ Server '{label}' not configured")
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False


def main():
    """Main setup tool"""
    print("🚀 JPAPI Server Setup")
    print("=" * 35)

    # Show current servers
    servers = list_servers()
    if servers:
        print(f"\n📊 Current servers: {', '.join(servers)}")
    else:
        print("\n📊 No servers configured yet")

    print("\nWhat would you like to do?")
    print("1. Add a new server")
    print("2. Test existing server")
    print("3. List all servers")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        print("\n➕ Adding New Server")
        print("-" * 20)

        label = input("Server label (e.g., 'prod', 'staging'): ").strip()
        if not label:
            print("❌ Label is required")
            return

        url = input("JAMF Pro URL: ").strip()
        if not url:
            print("❌ URL is required")
            return

        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        client_id = input("OAuth Client ID: ").strip()
        if not client_id:
            print("❌ Client ID is required")
            return

        client_secret = getpass.getpass("OAuth Client Secret: ").strip()
        if not client_secret:
            print("❌ Client Secret is required")
            return

        environment = (
            input("Environment (production/sandbox/staging) [production]: ").strip()
            or "production"
        )

        # Add the server
        if add_server(label, url, client_id, client_secret, environment):
            # Test connection
            print(f"\n🧪 Testing connection...")
            test_connection(label)

    elif choice == "2":
        servers = list_servers()
        if not servers:
            print("❌ No servers configured")
            return

        print(f"\nAvailable servers: {', '.join(servers)}")
        label = input("Enter server label to test: ").strip()
        if label in servers:
            test_connection(label)
        else:
            print(f"❌ Server '{label}' not found")

    elif choice == "3":
        servers = list_servers()
        if servers:
            print(f"\n📊 Configured servers: {', '.join(servers)}")
        else:
            print("\n📊 No servers configured")

    elif choice == "4":
        print("👋 Goodbye!")

    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    import time

    main()
