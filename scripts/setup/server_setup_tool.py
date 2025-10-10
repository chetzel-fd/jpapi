#!/usr/bin/env python3
"""
JPAPI Server Setup Tool
Easy tool to add new JAMF Pro servers to jpapi
"""

import sys
import json
import getpass
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.auth.jamf_login import auth_manager


class ServerSetupTool:
    """Interactive tool for setting up new JAMF Pro servers"""
    
    def __init__(self):
        self.manager = auth_manager
    
    def run(self):
        """Run the server setup tool"""
        print("🚀 JPAPI Server Setup Tool")
        print("=" * 50)
        print("This tool helps you add new JAMF Pro servers to jpapi")
        print()
        
        # Show current instances
        self._show_current_instances()
        
        # Main menu
        while True:
            print("\n📋 What would you like to do?")
            print("1. Add a new JAMF Pro server")
            print("2. List current servers")
            print("3. Test connection to a server")
            print("4. Remove a server")
            print("5. Set default server")
            print("6. Migrate legacy credentials")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                self._add_new_server()
            elif choice == "2":
                self._list_servers()
            elif choice == "3":
                self._test_connection()
            elif choice == "4":
                self._remove_server()
            elif choice == "5":
                self._set_default_server()
            elif choice == "6":
                self._migrate_legacy()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _show_current_instances(self):
        """Show current configured instances"""
        instances = self.manager.list_instances()
        if instances:
            print("📊 Current JAMF Pro servers:")
            for instance in instances:
                status = "🟢" if self.manager.test_connection(instance.label) else "🔴"
                print(f"   {status} {instance.label} - {instance.url}")
        else:
            print("📊 No JAMF Pro servers configured yet")
    
    def _add_new_server(self):
        """Add a new JAMF Pro server"""
        print("\n➕ Adding New JAMF Pro Server")
        print("-" * 30)
        
        # Get server details
        label = input("Server label (e.g., 'prod', 'staging', 'dev'): ").strip()
        if not label:
            print("❌ Label is required")
            return
        
        if label in [i.label for i in self.manager.list_instances()]:
            print(f"❌ Server '{label}' already exists")
            return
        
        url = input("JAMF Pro URL (e.g., https://your-company.jamfcloud.com): ").strip()
        if not url:
            print("❌ URL is required")
            return
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        client_id = input("OAuth Client ID: ").strip()
        if not client_id:
            print("❌ Client ID is required")
            return
        
        client_secret = getpass.getpass("OAuth Client Secret: ").strip()
        if not client_secret:
            print("❌ Client Secret is required")
            return
        
        environment = input("Environment (production/sandbox/staging) [production]: ").strip() or "production"
        description = input("Description (optional): ").strip()
        
        # Confirm details
        print(f"\n📋 Server Details:")
        print(f"   Label: {label}")
        print(f"   URL: {url}")
        print(f"   Client ID: {client_id[:10]}...")
        print(f"   Environment: {environment}")
        print(f"   Description: {description}")
        
        confirm = input("\nAdd this server? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Cancelled")
            return
        
        # Add the server
        print("\n🔄 Adding server...")
        success = self.manager.add_instance(
            label=label,
            url=url,
            client_id=client_id,
            client_secret=client_secret,
            environment=environment,
            description=description
        )
        
        if success:
            print(f"✅ Successfully added server '{label}'")
            
            # Test connection
            print("🧪 Testing connection...")
            if self.manager.test_connection(label):
                print(f"✅ Connection to '{label}' successful!")
            else:
                print(f"⚠️  Connection test failed. Please check your credentials.")
        else:
            print(f"❌ Failed to add server '{label}'")
    
    def _list_servers(self):
        """List all configured servers"""
        print("\n📊 Configured JAMF Pro Servers")
        print("-" * 40)
        
        instances = self.manager.list_instances()
        if not instances:
            print("No servers configured")
            return
        
        for instance in instances:
            status = "🟢 Connected" if self.manager.test_connection(instance.label) else "🔴 Disconnected"
            print(f"\n🏷️  {instance.label}")
            print(f"   URL: {instance.url}")
            print(f"   Environment: {instance.environment}")
            print(f"   Status: {status}")
            if instance.description:
                print(f"   Description: {instance.description}")
            if instance.created_at:
                print(f"   Created: {instance.created_at}")
    
    def _test_connection(self):
        """Test connection to a server"""
        instances = self.manager.list_instances()
        if not instances:
            print("❌ No servers configured")
            return
        
        print("\n🧪 Test Server Connection")
        print("-" * 30)
        
        print("Available servers:")
        for i, instance in enumerate(instances, 1):
            print(f"   {i}. {instance.label} - {instance.url}")
        
        try:
            choice = int(input("\nSelect server (number): ")) - 1
            if 0 <= choice < len(instances):
                instance = instances[choice]
                print(f"\n🔄 Testing connection to {instance.label}...")
                
                if self.manager.test_connection(instance.label):
                    print(f"✅ Connection to '{instance.label}' successful!")
                else:
                    print(f"❌ Connection to '{instance.label}' failed!")
                    print("   Please check your credentials and network connection")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    def _remove_server(self):
        """Remove a server"""
        instances = self.manager.list_instances()
        if not instances:
            print("❌ No servers configured")
            return
        
        print("\n🗑️  Remove Server")
        print("-" * 20)
        
        print("Available servers:")
        for i, instance in enumerate(instances, 1):
            print(f"   {i}. {instance.label} - {instance.url}")
        
        try:
            choice = int(input("\nSelect server to remove (number): ")) - 1
            if 0 <= choice < len(instances):
                instance = instances[choice]
                confirm = input(f"\nRemove server '{instance.label}'? (y/N): ").strip().lower()
                
                if confirm == 'y':
                    if self.manager.remove_instance(instance.label):
                        print(f"✅ Successfully removed server '{instance.label}'")
                    else:
                        print(f"❌ Failed to remove server '{instance.label}'")
                else:
                    print("❌ Cancelled")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    def _set_default_server(self):
        """Set the default server"""
        instances = self.manager.list_instances()
        if not instances:
            print("❌ No servers configured")
            return
        
        print("\n⭐ Set Default Server")
        print("-" * 25)
        
        print("Available servers:")
        for i, instance in enumerate(instances, 1):
            current = " (current)" if instance.label == self.manager.get_current_instance() else ""
            print(f"   {i}. {instance.label} - {instance.url}{current}")
        
        try:
            choice = int(input("\nSelect default server (number): ")) - 1
            if 0 <= choice < len(instances):
                instance = instances[choice]
                if self.manager.set_current_instance(instance.label):
                    print(f"✅ Set '{instance.label}' as default server")
                else:
                    print(f"❌ Failed to set '{instance.label}' as default")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    def _migrate_legacy(self):
        """Migrate legacy credentials"""
        print("\n🔄 Migrate Legacy Credentials")
        print("-" * 35)
        print("This will migrate your existing jpapi_sandbox credentials")
        print("to the new label system.")
        
        confirm = input("\nProceed with migration? (y/N): ").strip().lower()
        if confirm == 'y':
            if self.manager.migrate_legacy_credentials():
                print("✅ Migration completed successfully!")
            else:
                print("❌ Migration failed")
        else:
            print("❌ Migration cancelled")


def main():
    """Main entry point"""
    tool = ServerSetupTool()
    tool.run()


if __name__ == "__main__":
    main()
