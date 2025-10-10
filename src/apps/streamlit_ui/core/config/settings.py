"""
Application Settings - Configuration Management
Centralized configuration for the JPAPI Streamlit UI
"""

from typing import Dict, List, Any


class Settings:
    """Application settings and configuration"""

    # Application metadata
    APP_NAME = "JPAPI Manager"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "JAMF Pro API Management Dashboard"

    # Data directories to search for CSV exports
    CSV_EXPORT_DIRS = [
        "storage/data/csv-exports",
        "data/csv-exports",
        "exports",
        "storage/exports",
    ]

    # Environment configurations
    ENVIRONMENTS = {
        "sandbox": {
            "name": "Sandbox",
            "display_name": "Sandbox Environment",
            "server_url": "your-dev-company.jamfcloud.com",
            "description": "Development and testing environment",
        },
        "production": {
            "name": "Production",
            "display_name": "Production Environment",
            "server_url": "your-prod-company.jamfcloud.com",
            "description": "Live production environment",
        },
    }

    # Object type configurations
    OBJECT_TYPES = {
        "searches": {
            "name": "Advanced Searches",
            "display_name": "Advanced Searches",
            "jpapi_command": "advanced-searches",
            "icon": "🔍",
            "description": "Smart and static computer groups",
            "file_patterns": [
                "{env}-advanced-searches-export-*.csv",
                "*-advanced-searches-export-*.csv",
                "advanced-searches-export-*.csv",
            ],
        },
        "policies": {
            "name": "Policies",
            "display_name": "Policies",
            "jpapi_command": "policies",
            "icon": "📋",
            "description": "Configuration profiles and policies",
            "file_patterns": [
                "{env}-policies-export-*.csv",
                "*-policies-export-*.csv",
                "policies-export-*.csv",
            ],
        },
        "profiles": {
            "name": "Profiles",
            "display_name": "Configuration Profiles",
            "jpapi_command": "profiles",
            "icon": "⚙️",
            "description": "Configuration profiles",
            "file_patterns": [
                "{env}-profiles-export-*.csv",
                "*-profiles-export-*.csv",
                "profiles-export-*.csv",
            ],
        },
        "scripts": {
            "name": "Scripts",
            "display_name": "Scripts",
            "jpapi_command": "scripts",
            "icon": "📜",
            "description": "Shell scripts and scripts",
            "file_patterns": [
                "{env}-scripts-export-*.csv",
                "*-scripts-export-*.csv",
                "scripts-export-*.csv",
            ],
        },
    }

    # UI Configuration
    UI_CONFIG = {
        "page_title": "JPAPI Manager",
        "page_icon": "⚡",
        "layout": "wide",
        "initial_sidebar_state": "expanded",
        "header_height": 60,
        "sidebar_width": 300,
    }

    # Cache Configuration
    CACHE_CONFIG = {
        "enabled": True,
        "prefix": "data_",
        "ttl_seconds": 3600,  # 1 hour
        "max_size_mb": 100,
    }

    # Export Configuration
    EXPORT_CONFIG = {
        "default_format": "csv",
        "supported_formats": ["csv", "json", "xlsx"],
        "max_export_rows": 10000,
    }

    @classmethod
    def get_environment_names(cls) -> List[str]:
        """Get list of environment names"""
        return list(cls.ENVIRONMENTS.keys())

    @classmethod
    def get_object_type_names(cls) -> List[str]:
        """Get list of object type names"""
        return list(cls.OBJECT_TYPES.keys())

    @classmethod
    def get_environment_config(cls, env: str) -> Dict[str, Any]:
        """Get configuration for specific environment"""
        return cls.ENVIRONMENTS.get(env, {})

    @classmethod
    def get_object_type_config(cls, obj_type: str) -> Dict[str, Any]:
        """Get configuration for specific object type"""
        return cls.OBJECT_TYPES.get(obj_type, {})
