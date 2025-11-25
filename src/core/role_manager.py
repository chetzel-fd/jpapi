#!/usr/bin/env python3
"""
JAMF Pro Role Manager for jpapi CLI
Integrates with existing jpapi authentication system
"""

import sys
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

# Import jpapi auth system
from .auth.login_manager import UnifiedJamfAuth
from .auth.login_types import AuthResult, AuthStatus


class APIRole(Enum):
    """API Roles for jpapi CLI operations"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class RolePermission:
    """Individual permission within a role"""

    resource: str  # e.g., "devices", "policies", "scripts"
    operation: str  # e.g., "list", "export", "create"
    endpoint: str  # JAMF API endpoint
    description: str


@dataclass
class APIRoleConfig:
    """Complete API role configuration"""

    role: APIRole
    display_name: str
    description: str
    permissions: List[RolePermission]
    cli_commands: List[str]
    color: str  # For UI display


class JAMFRoleManager:
    """Manages JAMF Pro API roles for jpapi CLI"""

    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.auth = UnifiedJamfAuth(environment=environment)

        # Role definitions
        self.role_configs = {
            APIRole.READ: APIRoleConfig(
                role=APIRole.READ,
                display_name="🔵 Read-Only Access",
                description="View and export data without modification rights",
                color="🔵",
                cli_commands=["list", "search", "info", "export", "status"],
                permissions=[
                    RolePermission(
                        "devices",
                        "list",
                        "/JSSResource/mobiledevices",
                        "List mobile devices",
                    ),
                    RolePermission(
                        "devices", "list", "/JSSResource/computers", "List computers"
                    ),
                    RolePermission(
                        "devices",
                        "export",
                        "/JSSResource/mobiledevices",
                        "Export device data",
                    ),
                    RolePermission(
                        "policies", "list", "/JSSResource/policies", "List policies"
                    ),
                    RolePermission(
                        "scripts", "list", "/JSSResource/scripts", "List scripts"
                    ),
                    RolePermission(
                        "groups",
                        "list",
                        "/JSSResource/mobiledevicegroups",
                        "List device groups",
                    ),
                    RolePermission(
                        "profiles",
                        "list",
                        "/JSSResource/osxconfigurationprofiles",
                        "List profiles",
                    ),
                    RolePermission(
                        "extension_attributes",
                        "list",
                        "/JSSResource/computerextensionattributes",
                        "List extension attributes",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "list",
                        "/JSSResource/advancedcomputersearches",
                        "List advanced computer searches",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "list",
                        "/JSSResource/advancedmobiledevicesearches",
                        "List advanced mobile device searches",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "list",
                        "/JSSResource/advancedusersearches",
                        "List advanced user searches",
                    ),
                ],
            ),
            APIRole.CREATE: APIRoleConfig(
                role=APIRole.CREATE,
                display_name="🟢 Create Access",
                description="Create new JAMF objects and configurations",
                color="🟢",
                cli_commands=["create", "add"],
                permissions=[
                    RolePermission(
                        "devices",
                        "create",
                        "/JSSResource/mobiledevices",
                        "Add mobile devices",
                    ),
                    RolePermission(
                        "policies", "create", "/JSSResource/policies", "Create policies"
                    ),
                    RolePermission(
                        "scripts", "create", "/JSSResource/scripts", "Create scripts"
                    ),
                    RolePermission(
                        "groups",
                        "create",
                        "/JSSResource/mobiledevicegroups",
                        "Create groups",
                    ),
                    RolePermission(
                        "profiles",
                        "create",
                        "/JSSResource/osxconfigurationprofiles",
                        "Create profiles",
                    ),
                    RolePermission(
                        "extension_attributes",
                        "create",
                        "/JSSResource/computerextensionattributes",
                        "Create extension attributes",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "create",
                        "/JSSResource/advancedcomputersearches",
                        "Create advanced computer searches",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "create",
                        "/JSSResource/advancedmobiledevicesearches",
                        "Create advanced mobile device searches",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "create",
                        "/JSSResource/advancedusersearches",
                        "Create advanced user searches",
                    ),
                ],
            ),
            APIRole.UPDATE: APIRoleConfig(
                role=APIRole.UPDATE,
                display_name="🟡 Update Access",
                description="Modify existing objects and configurations",
                color="🟡",
                cli_commands=["update", "move", "modify"],
                permissions=[
                    RolePermission(
                        "devices",
                        "update",
                        "/JSSResource/mobiledevices",
                        "Update device settings",
                    ),
                    RolePermission(
                        "policies", "update", "/JSSResource/policies", "Modify policies"
                    ),
                    RolePermission(
                        "scripts", "update", "/JSSResource/scripts", "Update scripts"
                    ),
                    RolePermission(
                        "groups",
                        "update",
                        "/JSSResource/mobiledevicegroups",
                        "Modify groups",
                    ),
                    RolePermission(
                        "profiles",
                        "update",
                        "/JSSResource/osxconfigurationprofiles",
                        "Update profiles",
                    ),
                    RolePermission(
                        "extension_attributes",
                        "update",
                        "/JSSResource/computerextensionattributes",
                        "Update extension attributes",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "update",
                        "/JSSResource/advancedcomputersearches",
                        "Update advanced computer searches",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "update",
                        "/JSSResource/advancedmobiledevicesearches",
                        "Update advanced mobile device searches",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "update",
                        "/JSSResource/advancedusersearches",
                        "Update advanced user searches",
                    ),
                ],
            ),
            APIRole.DELETE: APIRoleConfig(
                role=APIRole.DELETE,
                display_name="🔴 Delete Access",
                description="Remove objects and configurations (HIGH RISK)",
                color="🔴",
                cli_commands=["delete", "remove", "destroy"],
                permissions=[
                    RolePermission(
                        "devices",
                        "delete",
                        "/JSSResource/mobiledevices",
                        "Remove devices",
                    ),
                    RolePermission(
                        "policies", "delete", "/JSSResource/policies", "Delete policies"
                    ),
                    RolePermission(
                        "scripts", "delete", "/JSSResource/scripts", "Remove scripts"
                    ),
                    RolePermission(
                        "groups",
                        "delete",
                        "/JSSResource/mobiledevicegroups",
                        "Delete groups",
                    ),
                    RolePermission(
                        "profiles",
                        "delete",
                        "/JSSResource/osxconfigurationprofiles",
                        "Remove profiles",
                    ),
                    RolePermission(
                        "extension_attributes",
                        "delete",
                        "/JSSResource/computerextensionattributes",
                        "Delete extension attributes",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "delete",
                        "/JSSResource/advancedcomputersearches",
                        "Delete advanced computer searches",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "delete",
                        "/JSSResource/advancedmobiledevicesearches",
                        "Delete advanced mobile device searches",
                    ),
                    RolePermission(
                        "advanced_searches",
                        "delete",
                        "/JSSResource/advancedusersearches",
                        "Delete advanced user searches",
                    ),
                ],
            ),
        }

    def is_authenticated(self) -> bool:
        """Check if we can authenticate with JAMF Pro"""
        try:
            token_result = self.auth.get_token()
            return token_result.success
        except Exception:
            return False

    def create_role(self, role: APIRole) -> bool:
        """Create a single role in JAMF Pro"""
        if not self.is_authenticated():
            print(f"❌ Authentication failed. Run: jpapi auth setup {self.environment}")
            return False

        config = self.role_configs[role]
        role_name = f"jpapi-{role.value}"

        # Map permissions to JAMF Pro privileges
        privileges = self._map_permissions_to_privileges(config.permissions)

        role_data = {
            "displayName": f"jpapi-{role.value}",
            "privileges": privileges,
        }

        try:
            # Use correct JAMF Pro API for role creation
            # Try different endpoint structure
            response = self.auth.api_request("POST", "/api/v1/api-roles", role_data)

            if response and "id" in response:
                print(f"✅ Created role: {config.display_name}")
                return True
            else:
                print(f"⚠️  Role may already exist: {config.display_name}")
                return True

        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                print(f"⚠️  Role already exists: {config.display_name}")
                return True
            else:
                print(f"❌ Failed to create role {config.display_name}: {e}")
                return False

    def update_role(self, role: APIRole) -> bool:
        """Update an existing role in JAMF Pro"""
        if not self.is_authenticated():
            print(f"❌ Authentication failed. Run: jpapi auth setup {self.environment}")
            return False

        config = self.role_configs[role]
        role_name = f"jpapi-{role.value}"

        # First, find the existing role
        existing_roles = self.list_existing_roles()
        role_to_update = None

        for existing_role in existing_roles:
            if existing_role.get("displayName") == role_name:
                role_to_update = existing_role
                break

        if not role_to_update:
            print(f"❌ Role {role_name} not found. Use create_role() instead.")
            return False

        # Map permissions to JAMF Pro privileges
        privileges = self._map_permissions_to_privileges(config.permissions)

        role_data = {
            "displayName": f"jpapi-{role.value}",
            "privileges": privileges,
        }

        try:
            # Update the role using the role ID
            role_id = role_to_update.get("id")
            response = self.auth.api_request(
                "PUT", f"/api/v1/api-roles/{role_id}", role_data
            )

            if response:
                print(f"✅ Updated role: {config.display_name}")
                return True
            else:
                print(f"❌ Failed to update role: {config.display_name}")
                return False

        except Exception as e:
            print(f"❌ Failed to update role {config.display_name}: {e}")
            return False

    def update_all_roles(self) -> Dict[APIRole, bool]:
        """Update all 4 jpapi roles"""
        print(f"🔄 Updating jpapi roles in JAMF Pro ({self.environment})...")
        print("=" * 60)

        results = {}
        for role in APIRole:
            results[role] = self.update_role(role)

        success_count = sum(1 for success in results.values() if success)
        print(f"\n🎉 Role update complete!")
        print(f"✅ Successfully updated {success_count}/4 roles")

        return results

    def create_all_roles(self) -> Dict[APIRole, bool]:
        """Create all 4 jpapi roles"""
        print(f"🚀 Creating jpapi roles in JAMF Pro ({self.environment})...")
        print("=" * 60)

        results = {}
        for role in APIRole:
            results[role] = self.create_role(role)

        success_count = sum(1 for success in results.values() if success)
        print(f"\n🎉 Role creation complete!")
        print(f"✅ Successfully created/verified {success_count}/4 roles")

        return results

    def list_existing_roles(self) -> List[Dict[str, Any]]:
        """List existing jpapi roles in JAMF Pro"""
        try:
            response = self.auth.api_request("GET", "/api/v1/api-roles")
            if response and "results" in response:
                jpapi_roles = [
                    role
                    for role in response["results"]
                    if role.get("displayName", "").startswith("jpapi-")
                ]
                return jpapi_roles
            return []
        except Exception as e:
            print(f"❌ Error listing roles: {e}")
            return []

    def _map_permissions_to_privileges(
        self, permissions: List[RolePermission]
    ) -> List[str]:
        """Map our permission model to JAMF Pro privileges"""
        privilege_map = {
            "devices": {
                "list": ["Read Mobile Devices", "Read Computers"],
                "export": ["Read Mobile Devices", "Read Computers"],
                "create": ["Create Mobile Devices", "Create Computers"],
                "update": ["Update Mobile Devices", "Update Computers"],
                "delete": ["Delete Mobile Devices", "Delete Computers"],
            },
            "policies": {
                "list": ["Read Policies"],
                "create": ["Create Policies"],
                "update": ["Update Policies"],
                "delete": ["Delete Policies"],
            },
            "scripts": {
                "list": ["Read Scripts"],
                "create": ["Create Scripts"],
                "update": ["Update Scripts"],
                "delete": ["Delete Scripts"],
            },
            "groups": {
                "list": [
                    "Read Smart Mobile Device Groups",
                    "Read Static Mobile Device Groups",
                    "Read Smart Computer Groups",
                    "Read Static Computer Groups",
                ],
                "create": [
                    "Create Smart Mobile Device Groups",
                    "Create Static Mobile Device Groups",
                    "Create Smart Computer Groups",
                    "Create Static Computer Groups",
                ],
                "update": [
                    "Update Smart Mobile Device Groups",
                    "Update Static Mobile Device Groups",
                    "Update Smart Computer Groups",
                    "Update Static Computer Groups",
                ],
                "delete": [
                    "Delete Smart Mobile Device Groups",
                    "Delete Static Mobile Device Groups",
                    "Delete Smart Computer Groups",
                    "Delete Static Computer Groups",
                ],
            },
            "profiles": {
                "list": [
                    "Read iOS Configuration Profiles",
                    "Read macOS Configuration Profiles",
                ],
                "create": [
                    "Create iOS Configuration Profiles",
                    "Create macOS Configuration Profiles",
                ],
                "update": [
                    "Update iOS Configuration Profiles",
                    "Update macOS Configuration Profiles",
                ],
                "delete": [
                    "Delete iOS Configuration Profiles",
                    "Delete macOS Configuration Profiles",
                ],
            },
            "advanced_searches": {
                "list": [
                    "Read Advanced Computer Searches",
                    "Read Advanced Mobile Device Searches",
                    "Read Advanced User Searches",
                ],
                "create": [
                    "Create Advanced Computer Searches",
                    "Create Advanced Mobile Device Searches",
                    "Create Advanced User Searches",
                ],
                "update": [
                    "Update Advanced Computer Searches",
                    "Update Advanced Mobile Device Searches",
                    "Update Advanced User Searches",
                ],
                "delete": [
                    "Delete Advanced Computer Searches",
                    "Delete Advanced Mobile Device Searches",
                    "Delete Advanced User Searches",
                ],
            },
            "extension_attributes": {
                "list": [
                    "Read Computer Extension Attributes",
                    "Read Mobile Device Extension Attributes",
                    "Read User Extension Attributes",
                ],
                "create": [
                    "Create Computer Extension Attributes",
                    "Create Mobile Device Extension Attributes",
                    "Create User Extension Attributes",
                ],
                "update": [
                    "Update Computer Extension Attributes",
                    "Update Mobile Device Extension Attributes",
                    "Update User Extension Attributes",
                ],
                "delete": [
                    "Delete Computer Extension Attributes",
                    "Delete Mobile Device Extension Attributes",
                    "Delete User Extension Attributes",
                ],
            },
            "user_groups": {
                "list": [
                    "Read Smart User Groups",
                    "Read Static User Groups",
                ],
                "create": [
                    "Create Smart User Groups",
                    "Create Static User Groups",
                ],
                "update": [
                    "Update Smart User Groups",
                    "Update Static User Groups",
                ],
                "delete": [
                    "Delete Smart User Groups",
                    "Delete Static User Groups",
                ],
            },
            "mobile_apps": {
                "list": [
                    "Read Mobile Device Applications",
                ],
                "create": [
                    "Create Mobile Device Applications",
                ],
                "update": [
                    "Update Mobile Device Applications",
                ],
                "delete": [
                    "Delete Mobile Device Applications",
                ],
            },
            "packages": {
                "list": ["Read Packages"],
                "create": ["Create Packages"],
                "update": ["Update Packages"],
                "delete": ["Delete Packages"],
            },
        }

        privileges = set()
        for perm in permissions:
            if (
                perm.resource in privilege_map
                and perm.operation in privilege_map[perm.resource]
            ):
                privileges.update(privilege_map[perm.resource][perm.operation])

        # Always include read privileges for basic access
        privileges.update(
            [
                "Read Mobile Devices",
                "Read Computers",
                "Read Policies",
                "Read Scripts",
                "Read Smart Mobile Device Groups",
                "Read Static Mobile Device Groups",
                "Read Smart Computer Groups",
                "Read Static Computer Groups",
                "Read iOS Configuration Profiles",
                "Read macOS Configuration Profiles",
                "Read Packages",
                "Read Categories",
                "Read Accounts",
                "Read Sites",
                "Read Buildings",
                "Read Departments",
                # New Phase 1 privileges
                "Read Advanced Computer Searches",
                "Read Advanced Mobile Device Searches",
                "Read Advanced User Searches",
                "Read Computer Extension Attributes",
                "Read Mobile Device Extension Attributes",
                "Read User Extension Attributes",
                "Read Smart User Groups",
                "Read Static User Groups",
                "Read Mobile Device Applications",
                # Phase 2 privileges
                "Read Distribution Points",
            ]
        )

        return sorted(list(privileges))

    def get_role_info(self) -> Dict[str, Any]:
        """Get information about available roles"""
        return {
            "environment": self.environment,
            "authenticated": self.is_authenticated(),
            "roles": {
                role.value: {
                    "display_name": config.display_name,
                    "description": config.description,
                    "cli_commands": config.cli_commands,
                    "permissions": len(config.permissions),
                }
                for role, config in self.role_configs.items()
            },
        }


def create_roles_interactive(environment: str = "dev") -> bool:
    """Interactive role creation with user confirmation"""
    manager = JAMFRoleManager(environment)

    print(f"🔧 JAMF Pro Role Manager for jpapi CLI")
    print(f"Environment: {environment}")
    print("=" * 50)
    print()

    # Check authentication
    if not manager.is_authenticated():
        print(f"❌ Not authenticated with JAMF Pro ({environment})")
        print(f"Run: jpapi auth setup {environment}")
        return False

    print("✅ Authenticated with JAMF Pro")
    print()

    # Show available roles
    print("📋 Available jpapi roles:")
    for role, config in manager.role_configs.items():
        print(f"  {config.color} {config.display_name}")
        print(f"     {config.description}")
        print(f"     Commands: {', '.join(config.cli_commands)}")
        print()

    # Confirm creation
    confirm = input("Create all 4 jpapi roles? (y/n): ").lower().strip()
    if confirm not in ["y", "yes"]:
        print("❌ Role creation cancelled")
        return False

    # Create roles
    results = manager.create_all_roles()

    # Show results
    print("\n📋 Creation Results:")
    for role, success in results.items():
        config = manager.role_configs[role]
        status = "✅" if success else "❌"
        print(f"  {status} {config.display_name}")

    # List existing roles
    print("\n📋 Existing jpapi roles in JAMF Pro:")
    existing_roles = manager.list_existing_roles()
    if existing_roles:
        for role in existing_roles:
            print(
                f"  • {role.get('displayName', 'Unknown')} (ID: {role.get('id', 'Unknown')})"
            )
    else:
        print("  No jpapi roles found")

    return all(results.values())


if __name__ == "__main__":
    """Command line interface for role management"""
    import argparse

    parser = argparse.ArgumentParser(description="JAMF Pro Role Manager for jpapi CLI")
    parser.add_argument(
        "--env", default="sandbox", help="Environment (sandbox/production)"
    )
    parser.add_argument("--create", action="store_true", help="Create all roles")
    parser.add_argument("--list", action="store_true", help="List existing roles")
    parser.add_argument("--info", action="store_true", help="Show role information")

    args = parser.parse_args()

    manager = JAMFRoleManager(args.env)

    if args.create:
        create_roles_interactive(args.env)
    elif args.list:
        roles = manager.list_existing_roles()
        print(f"📋 Existing jpapi roles in {args.env}:")
        for role in roles:
            print(
                f"  • {role.get('displayName', 'Unknown')} (ID: {role.get('id', 'Unknown')})"
            )
    elif args.info:
        info = manager.get_role_info()
        print(f"🔧 Role Manager Info ({args.env}):")
        print(f"  Authenticated: {info['authenticated']}")
        print(f"  Available roles: {len(info['roles'])}")
        for role_name, role_info in info["roles"].items():
            print(
                f"    • {role_info['display_name']} ({len(role_info['cli_commands'])} commands)"
            )
    else:
        create_roles_interactive(args.env)
