"""
URL utilities for generating JAMF Pro GUI links
"""

from typing import Dict, Optional


def get_jamf_gui_url(object_type: str, object_id: str, base_url: str) -> str:
    """
    Generate JAMF Pro GUI URL for a specific object

    Args:
        object_type: Type of object (policies, profiles, scripts, etc.)
        object_id: ID of the object
        base_url: Base JAMF Pro URL (e.g., https://company.jamfcloud.com)

    Returns:
        Complete URL to the object in JAMF Pro GUI
    """
    # Remove trailing slash from base_url if present
    base_url = base_url.rstrip("/")

    # Map object types to their GUI paths
    gui_paths = {
        "policies": "policies.html",
        "profiles": "osXConfigurationProfiles.html",
        "macos-profiles": "osXConfigurationProfiles.html",
        "ios-profiles": "osXConfigurationProfiles.html",
        "scripts": "scripts.html",
        "packages": "packages.html",
        "groups": "computerGroups.html",
        "computer-groups": "computerGroups.html",
        "categories": "categories.html",
        "mobile-devices": "mobileDevices.html",
        "mobile_devices": "mobileDevices.html",
        "computers": "computers.html",
        "computer_devices": "computers.html",
        "advanced-searches": "advancedComputerSearches.html",
        "extension-attributes": "computerExtensionAttributes.html",
        "user-groups": "userGroups.html",
        "mobile-apps": "mobileDeviceApplications.html",
    }

    # Get the GUI path for the object type
    gui_path = gui_paths.get(object_type.lower())

    if not gui_path:
        # Fallback: try to construct from object_type
        gui_path = f"{object_type.lower().replace('_', '').replace('-', '')}.html"

    # Construct the full URL
    return f"{base_url}/{gui_path}?id={object_id}"


def create_hyperlink(text: str, url: str) -> str:
    """
    Create an Excel-compatible hyperlink formula

    Args:
        text: Display text for the hyperlink
        url: URL to link to

    Returns:
        Excel hyperlink formula string
    """
    return f'=HYPERLINK("{url}","{text}")'


def get_base_url_from_environment(environment: str) -> str:
    """
    Get the base JAMF Pro URL for the given environment

    Args:
        environment: Environment name (dev, prod, etc.)

    Returns:
        Base JAMF Pro URL
    """
    # Default URLs - these should match the configuration
    default_urls = {
        "dev": "https://your-dev-company.jamfcloud.com",
        "prod": "https://your-prod-company.jamfcloud.com",
    }

    return default_urls.get(environment, default_urls["dev"])


def create_jamf_hyperlink(
    object_type: str, object_id: str, environment: str = "dev"
) -> str:
    """
    Create a complete JAMF Pro GUI hyperlink for an object

    Args:
        object_type: Type of object
        object_id: ID of the object
        environment: JAMF Pro environment

    Returns:
        Excel hyperlink formula string
    """
    base_url = get_base_url_from_environment(environment)
    gui_url = get_jamf_gui_url(object_type, object_id, base_url)
    return create_hyperlink(str(object_id), gui_url)
