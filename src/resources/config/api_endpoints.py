#!/usr/bin/env python3
"""
API Endpoint Registry for jpapi
Centralized endpoint definitions and response extraction logic
Single source of truth for all JAMF Pro API endpoints
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Literal, Optional


@dataclass
class APIEndpoint:
    """API endpoint configuration"""

    base_path: str
    version: Literal["classic", "v1", "v2"]
    supports_list: bool = True
    supports_get: bool = True
    supports_create: bool = True
    supports_update: bool = True
    supports_delete: bool = True
    list_response_key: Optional[str] = None
    single_response_key: Optional[str] = None


class ObjectType(Enum):
    """Centralized object type registry"""

    CATEGORIES = "categories"
    PROFILES = "profiles"
    PROFILES_MACOS = "macos-profiles"
    PROFILES_IOS = "ios-profiles"
    SCRIPTS = "scripts"
    POLICIES = "macos-policies"
    DEVICES_MACOS = "macos-devices"
    DEVICES_IOS = "ios-devices"
    PACKAGES = "packages"
    GROUPS_COMPUTER = "computer-groups"
    SEARCHES_COMPUTER_ADVANCED = "computer-advanced-searches"
    SEARCHES_MOBILE_ADVANCED = "mobile-advanced-searches"
    SEARCHES_USER_ADVANCED = "user-advanced-searches"
    # Extension Attributes
    EXTENSION_ATTR_COMPUTER = "computer-extension-attribute"
    EXTENSION_ATTR_MOBILE = "mobile-extension-attribute"
    EXTENSION_ATTR_USER = "user-extension-attribute"
    # User Groups
    USER_GROUP_SMART = "smart-user-group"
    USER_GROUP_STATIC = "static-user-group"


# Centralized endpoint mapping - SINGLE SOURCE OF TRUTH
API_ENDPOINTS: Dict[ObjectType, APIEndpoint] = {
    ObjectType.CATEGORIES: APIEndpoint(
        base_path="/JSSResource/categories",
        version="classic",
        list_response_key="categories.category",
        single_response_key="category",
    ),
    ObjectType.PROFILES: APIEndpoint(
        base_path="/JSSResource/osxconfigurationprofiles",
        version="classic",
        list_response_key="os_x_configuration_profiles.os_x_configuration_profile",
        single_response_key="os_x_configuration_profile",
    ),
    ObjectType.PROFILES_MACOS: APIEndpoint(
        base_path="/JSSResource/osxconfigurationprofiles",
        version="classic",
        list_response_key="os_x_configuration_profiles.os_x_configuration_profile",
        single_response_key="os_x_configuration_profile",
    ),
    ObjectType.PROFILES_IOS: APIEndpoint(
        base_path="/JSSResource/mobiledeviceconfigurationprofiles",
        version="classic",
        list_response_key="mobile_device_configuration_profiles.mobile_device_configuration_profile",
        single_response_key="mobile_device_configuration_profile",
    ),
    ObjectType.SCRIPTS: APIEndpoint(
        base_path="/JSSResource/scripts",
        version="classic",
        list_response_key="scripts.script",
        single_response_key="script",
    ),
    ObjectType.POLICIES: APIEndpoint(
        base_path="/api/v1/policies",
        version="v1",
        list_response_key="results",
        single_response_key=None,  # v1 returns direct object
    ),
    ObjectType.DEVICES_MACOS: APIEndpoint(
        base_path="/JSSResource/computers",
        version="classic",
        list_response_key="computers.computer",
        single_response_key="computer",
    ),
    ObjectType.DEVICES_IOS: APIEndpoint(
        base_path="/JSSResource/mobiledevices",
        version="classic",
        list_response_key="mobile_devices.mobile_device",
        single_response_key="mobile_device",
    ),
    ObjectType.PACKAGES: APIEndpoint(
        base_path="/JSSResource/packages",
        version="classic",
        list_response_key="packages.package",
        single_response_key="package",
    ),
    ObjectType.GROUPS_COMPUTER: APIEndpoint(
        base_path="/JSSResource/computergroups",
        version="classic",
        list_response_key="computer_groups.computer_group",
        single_response_key="computer_group",
    ),
    ObjectType.SEARCHES_COMPUTER_ADVANCED: APIEndpoint(
        base_path="/JSSResource/advancedcomputersearches",
        version="classic",
        list_response_key="advanced_computer_searches.advanced_computer_search",
        single_response_key="advanced_computer_search",
    ),
    ObjectType.SEARCHES_MOBILE_ADVANCED: APIEndpoint(
        base_path="/api/v1/advanced-mobile-device-searches",
        version="v1",
        list_response_key="results",
        single_response_key=None,
    ),
    ObjectType.SEARCHES_USER_ADVANCED: APIEndpoint(
        base_path="/JSSResource/advancedusersearches",
        version="classic",
        list_response_key="advanced_user_searches.advanced_user_search",
        single_response_key="advanced_user_search",
    ),
    # Extension Attributes
    ObjectType.EXTENSION_ATTR_COMPUTER: APIEndpoint(
        base_path="/JSSResource/computerextensionattributes",
        version="classic",
        list_response_key="computer_extension_attributes.computer_extension_attribute",
        single_response_key="computer_extension_attribute",
    ),
    ObjectType.EXTENSION_ATTR_MOBILE: APIEndpoint(
        base_path="/JSSResource/mobiledeviceextensionattributes",
        version="classic",
        list_response_key="mobile_device_extension_attributes.mobile_device_extension_attribute",
        single_response_key="mobile_device_extension_attribute",
    ),
    ObjectType.EXTENSION_ATTR_USER: APIEndpoint(
        base_path="/JSSResource/userextensionattributes",
        version="classic",
        list_response_key="user_extension_attributes.user_extension_attribute",
        single_response_key="user_extension_attribute",
    ),
    # User Groups
    ObjectType.USER_GROUP_SMART: APIEndpoint(
        base_path="/JSSResource/smartusergroups",
        version="classic",
        list_response_key="smart_user_groups.smart_user_group",
        single_response_key="smart_user_group",
    ),
    ObjectType.USER_GROUP_STATIC: APIEndpoint(
        base_path="/JSSResource/staticusergroups",
        version="classic",
        list_response_key="static_user_groups.static_user_group",
        single_response_key="static_user_group",
    ),
}


# String to ObjectType mapping for backward compatibility
OBJECT_TYPE_ALIASES: Dict[str, ObjectType] = {
    "categories": ObjectType.CATEGORIES,
    "profiles": ObjectType.PROFILES,
    "macos-profiles": ObjectType.PROFILES_MACOS,
    "ios-profiles": ObjectType.PROFILES_IOS,
    "scripts": ObjectType.SCRIPTS,
    "macos-policies": ObjectType.POLICIES,
    "macos-devices": ObjectType.DEVICES_MACOS,
    "ios-devices": ObjectType.DEVICES_IOS,
    "packages": ObjectType.PACKAGES,
    "computer-groups": ObjectType.GROUPS_COMPUTER,
    "computer-advanced-searches": ObjectType.SEARCHES_COMPUTER_ADVANCED,
    "mobile-advanced-searches": ObjectType.SEARCHES_MOBILE_ADVANCED,
    "user-advanced-searches": ObjectType.SEARCHES_USER_ADVANCED,
    # Extension Attributes - support both old and new patterns
    "computer": ObjectType.EXTENSION_ATTR_COMPUTER,
    "mobile": ObjectType.EXTENSION_ATTR_MOBILE,
    "user": ObjectType.EXTENSION_ATTR_USER,
    # User Groups
    "smart": ObjectType.USER_GROUP_SMART,
    "static": ObjectType.USER_GROUP_STATIC,
}


class APIRegistry:
    """API endpoint registry with helper methods"""

    @staticmethod
    def get_object_type(type_string: str) -> Optional[ObjectType]:
        """Convert string to ObjectType enum"""
        return OBJECT_TYPE_ALIASES.get(type_string)

    @staticmethod
    def get_list_endpoint(object_type_str: str) -> str:
        """Get list endpoint for object type string"""
        obj_type = OBJECT_TYPE_ALIASES.get(object_type_str)
        if not obj_type:
            raise ValueError(f"Unknown object type: {object_type_str}")

        config = API_ENDPOINTS[obj_type]
        return config.base_path

    @staticmethod
    def get_single_endpoint(object_type_str: str, obj_id: int) -> str:
        """Get single object endpoint"""
        obj_type = OBJECT_TYPE_ALIASES.get(object_type_str)
        if not obj_type:
            raise ValueError(f"Unknown object type: {object_type_str}")

        config = API_ENDPOINTS[obj_type]

        # v1 API uses /{id}, classic uses /id/{id}
        if config.version == "v1":
            return f"{config.base_path}/{obj_id}"
        else:
            return f"{config.base_path}/id/{obj_id}"

    @staticmethod
    def extract_list_response(
        object_type_str: str, response: dict
    ) -> List[Dict[str, Any]]:
        """
        Extract list of objects from nested API response

        Args:
            object_type_str: Object type string
            response: API response dictionary

        Returns:
            List of objects extracted from response
        """
        obj_type = OBJECT_TYPE_ALIASES.get(object_type_str)
        if not obj_type:
            return []

        config = API_ENDPOINTS[obj_type]

        if not config.list_response_key:
            return response if isinstance(response, list) else []

        # Navigate nested keys (e.g., "scripts.script")
        result = response
        for key in config.list_response_key.split("."):
            if isinstance(result, dict):
                result = result.get(key, {})
            else:
                return []

        return result if isinstance(result, list) else []

    @staticmethod
    def extract_single_response(object_type_str: str, response: dict) -> dict:
        """
        Extract single object from API response

        Args:
            object_type_str: Object type string
            response: API response dictionary

        Returns:
            Single object extracted from response
        """
        obj_type = OBJECT_TYPE_ALIASES.get(object_type_str)
        if not obj_type:
            return response

        config = API_ENDPOINTS[obj_type]

        if not config.single_response_key:
            return response

        return response.get(config.single_response_key, response)
