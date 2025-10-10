#!/usr/bin/env python3
"""
Central Configuration System for JPAPI
Provides unified configuration management across all components
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging


@dataclass
class ServerPorts:
    """Server port configuration"""

    backend_fast: int = 8600
    backend_enhanced: int = 8900
    redis: int = 6379
    dashboard: int = 5000
    api_docs: int = 8080


@dataclass
class Environments:
    """Environment configuration"""

    default: str = "dev"
    available: List[str] = None
    aliases: Dict[str, str] = None

    def __post_init__(self):
        if self.available is None:
            self.available = ["dev", "staging", "prod", "test"]
        if self.aliases is None:
            self.aliases = {
                "development": "dev",
                "production": "prod",
                "testing": "test",
            }


@dataclass
class OutputFormats:
    """Output format configuration"""

    data_formats: List[str] = None
    status_options: List[str] = None
    filter_types: List[str] = None
    default_format: str = "csv"

    def __post_init__(self):
        if self.data_formats is None:
            self.data_formats = ["table", "json", "csv", "yaml"]
        if self.status_options is None:
            self.status_options = ["enabled", "disabled", "all"]
        if self.filter_types is None:
            self.filter_types = ["wildcard", "regex", "exact", "contains"]


@dataclass
class Paths:
    """Path configuration"""

    cache_dir: str = "~/.jpapi/cache"
    config_dir: str = "~/.jpapi"
    data_dir: str = "~/.jpapi/data"
    logs_dir: str = "~/.jpapi/logs"
    temp_dir: str = "~/.jpapi/temp"


@dataclass
class Timeouts:
    """Timeout configuration"""

    api_timeout: int = 30
    cache_timeout: int = 300
    operation_timeout: int = 300
    connection_timeout: int = 10
    retry_timeout: int = 5
    bash_operation_timeout: int = 30
    python_operation_timeout: int = 300


@dataclass
class Version:
    """Version configuration"""

    version: str = "2.0.0"
    build: str = "modular"
    architecture: str = "hybrid bash/Python"
    api_version: str = "1.0.0"


@dataclass
class Logging:
    """Logging configuration"""

    default_level: str = "INFO"
    available_levels: List[str] = None
    component_levels: Dict[str, str] = None

    def __post_init__(self):
        if self.available_levels is None:
            self.available_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.component_levels is None:
            self.component_levels = {
                "api": "INFO",
                "cache": "WARNING",
                "auth": "ERROR",
                "gui": "INFO",
            }


@dataclass
class Users:
    """User configuration"""

    default_signature: str = "chetzel"
    available_users: List[str] = None
    user_roles: Dict[str, str] = None

    def __post_init__(self):
        if self.available_users is None:
            self.available_users = ["chetzel", "jdoe", "admin"]
        if self.user_roles is None:
            self.user_roles = {"chetzel": "admin", "jdoe": "user", "admin": "admin"}


@dataclass
class Authentication:
    """JAMF authentication configuration"""

    # Required JAMF server URL
    jamf_url: str = ""

    # Authentication methods (OAuth preferred, Basic Auth fallback)
    auth_method: str = "oauth"  # "oauth" or "basic"

    # OAuth configuration
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob"

    # Basic Auth configuration (fallback)
    basic_username: str = ""
    basic_password: str = ""

    # Authentication preferences
    prefer_oauth: bool = True
    fallback_to_basic: bool = True
    auto_refresh_tokens: bool = True
    token_cache_duration: int = 3600  # 1 hour


@dataclass
class ExperimentalFeatures:
    """Experimental features configuration"""

    # Dashboard features
    enable_dashboards: bool = False
    enable_real_time_dashboard: bool = False
    enable_analytics_dashboard: bool = False
    enable_computer_groups_dashboard: bool = False
    enable_mobile_devices_dashboard: bool = False

    # Advanced features
    enable_advanced_relationships: bool = False
    enable_pppc_scanner: bool = False
    enable_profile_manifests: bool = False
    enable_installomator: bool = False

    # Framework features (experimental)
    enable_framework_apps: bool = False
    enable_enterprise_dashboard: bool = False
    enable_analytics_framework: bool = False
    enable_multi_tenant: bool = False
    enable_fastapi_backend: bool = False
    enable_dash_frontend: bool = False

    # Incomplete Streamlit features
    enable_relationship_mapping: bool = False
    enable_advanced_analytics: bool = False
    enable_report_generation: bool = False
    enable_export_analysis: bool = False
    enable_object_manager_v5: bool = False
    enable_interactive_visualizations: bool = False

    # Beta/placeholder features
    enable_placeholder_features: bool = False
    enable_coming_soon_features: bool = False
    enable_beta_ui_components: bool = False

    # Development features
    enable_debug_mode: bool = False
    enable_verbose_logging: bool = False
    enable_performance_metrics: bool = False


@dataclass
class AddonConfiguration:
    """Addon configuration settings"""

    # Installomator settings
    installomator_enabled: bool = True
    installomator_repo_url: str = "https://github.com/Installomator/Installomator"
    installomator_script_path: str = "addons/installomator/installomator.sh"
    installomator_timeout: int = 300

    # PPPC Scanner settings
    pppc_scanner_enabled: bool = True
    pppc_scanner_output_dir: str = "storage/data/pppc-enterprise-profiles"
    pppc_scanner_include_system: bool = True
    pppc_scanner_include_user: bool = True

    # Profile Manifests settings
    profile_manifests_enabled: bool = True
    profile_manifests_output_dir: str = "storage/data/manifest-data"
    profile_manifests_include_metadata: bool = True
    profile_manifests_auto_update: bool = True


@dataclass
class CacheConfiguration:
    """Cache configuration settings"""

    # Cache settings
    cache_enabled: bool = True
    cache_duration: int = 300  # 5 minutes
    cache_max_size: int = 1000  # Maximum cached items
    cache_cleanup_interval: int = 3600  # 1 hour

    # Cache TTL settings
    api_cache_ttl: int = 300
    relationship_cache_ttl: int = 7200  # 2 hours
    object_detail_cache_ttl: int = 1800  # 30 minutes

    # Cache storage
    cache_storage_type: str = "memory"  # "memory" or "redis"
    cache_redis_url: str = "redis://localhost:6379"


@dataclass
class ExportConfiguration:
    """Export configuration settings"""

    # Default export settings
    default_export_directory: str = "storage/exports"
    default_export_format: str = "csv"
    include_metadata: bool = True
    include_timestamps: bool = True

    # Export formats
    available_formats: List[str] = None
    export_compression: bool = False
    export_encryption: bool = False

    # Export behavior
    auto_create_directories: bool = True
    overwrite_existing: bool = False
    export_batch_size: int = 1000

    def __post_init__(self):
        if self.available_formats is None:
            self.available_formats = ["csv", "json", "xlsx", "xml", "yaml"]


@dataclass
class APIConfiguration:
    """API behavior configuration"""

    # Request settings
    max_retries: int = 3
    retry_delay: int = 1
    request_timeout: int = 30
    connection_pool_size: int = 10

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10

    # API behavior
    auto_retry_failed_requests: bool = True
    cache_api_responses: bool = True
    follow_redirects: bool = True
    verify_ssl: bool = True


class CentralConfig:
    """Central configuration manager for JPAPI"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or os.path.join(os.path.dirname(__file__)))
        self.config_dir.mkdir(exist_ok=True)

        # Initialize configuration objects
        self.ports = ServerPorts()
        self.environments = Environments()
        self.formats = OutputFormats()
        self.paths = Paths()
        self.timeouts = Timeouts()
        self.version = Version()
        self.logging = Logging()
        self.users = Users()
        self.authentication = Authentication()
        self.experimental = ExperimentalFeatures()
        self.addons = AddonConfiguration()
        self.cache = CacheConfiguration()
        self.export = ExportConfiguration()
        self.api = APIConfiguration()

        # Load configurations
        self._load_all_configs()

    def _load_all_configs(self):
        """Load all configuration files"""
        config_files = {
            "server_ports.json": self.ports,
            "environments.json": self.environments,
            "output_formats.json": self.formats,
            "paths.json": self.paths,
            "timeouts.json": self.timeouts,
            "version.json": self.version,
            "logging.json": self.logging,
            "users.json": self.users,
            "authentication.json": self.authentication,
            "experimental_features.json": self.experimental,
            "addon_configuration.json": self.addons,
            "cache_configuration.json": self.cache,
            "export_configuration.json": self.export,
            "api_configuration.json": self.api,
        }

        for filename, config_obj in config_files.items():
            self._load_config(filename, config_obj)

    def _load_config(self, filename: str, config_obj):
        """Load a specific configuration file"""
        config_path = self.config_dir / filename

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    # Update the dataclass with loaded data
                    for key, value in data.items():
                        if hasattr(config_obj, key):
                            setattr(config_obj, key, value)
            except Exception as e:
                logging.warning(f"Could not load {filename}: {e}")
        else:
            # Create default config file
            self._save_config(filename, config_obj)

    def _save_config(self, filename: str, config_obj):
        """Save a configuration file"""
        config_path = self.config_dir / filename

        try:
            with open(config_path, "w") as f:
                json.dump(asdict(config_obj), f, indent=2)
        except Exception as e:
            logging.error(f"Could not save {filename}: {e}")

    def save_all_configs(self):
        """Save all configuration files"""
        config_files = {
            "server_ports.json": self.ports,
            "environments.json": self.environments,
            "output_formats.json": self.formats,
            "paths.json": self.paths,
            "timeouts.json": self.timeouts,
            "version.json": self.version,
            "logging.json": self.logging,
            "users.json": self.users,
            "authentication.json": self.authentication,
            "experimental_features.json": self.experimental,
            "addon_configuration.json": self.addons,
            "cache_configuration.json": self.cache,
            "export_configuration.json": self.export,
            "api_configuration.json": self.api,
        }

        for filename, config_obj in config_files.items():
            self._save_config(filename, config_obj)

    def get_port(self, service: str) -> int:
        """Get port for a service"""
        return getattr(self.ports, service, 8080)

    def get_timeout(self, timeout_type: str) -> int:
        """Get timeout value"""
        return getattr(self.timeouts, timeout_type, 30)

    def get_path(self, path_type: str) -> str:
        """Get expanded path"""
        path = getattr(self.paths, path_type, "~/.jpapi")
        return os.path.expanduser(path)

    def get_format_options(self, format_type: str) -> List[str]:
        """Get format options"""
        if format_type == "data":
            return self.formats.data_formats
        elif format_type == "status":
            return self.formats.status_options
        elif format_type == "filter":
            return self.formats.filter_types
        return []

    def get_log_level(self, component: str = None) -> str:
        """Get log level for component or default"""
        if component and component in self.logging.component_levels:
            return self.logging.component_levels[component]
        return self.logging.default_level

    def is_valid_environment(self, env: str) -> bool:
        """Check if environment is valid"""
        return env in self.environments.available

    def get_environment_alias(self, alias: str) -> str:
        """Get environment from alias"""
        return self.environments.aliases.get(alias, alias)

    def get_user_role(self, user: str) -> str:
        """Get user role"""
        return self.users.user_roles.get(user, "user")

    def is_experimental_enabled(self, feature: str) -> bool:
        """Check if experimental feature is enabled"""
        return getattr(self.experimental, feature, False)

    def is_addon_enabled(self, addon: str) -> bool:
        """Check if addon is enabled"""
        return getattr(self.addons, f"{addon}_enabled", False)

    def get_cache_ttl(self, cache_type: str) -> int:
        """Get cache TTL for specific cache type"""
        return getattr(self.cache, f"{cache_type}_ttl", self.cache.cache_duration)

    def get_export_directory(self) -> str:
        """Get default export directory"""
        return os.path.expanduser(self.export.default_export_directory)

    def get_auth_method(self) -> str:
        """Get preferred authentication method"""
        return self.authentication.auth_method

    def get_jamf_url(self) -> str:
        """Get JAMF server URL"""
        return self.authentication.jamf_url

    def is_oauth_configured(self) -> bool:
        """Check if OAuth is properly configured"""
        return (
            self.authentication.oauth_client_id
            and self.authentication.oauth_client_secret
            and self.authentication.jamf_url
        )

    def is_basic_auth_configured(self) -> bool:
        """Check if Basic Auth is properly configured"""
        return (
            self.authentication.basic_username
            and self.authentication.basic_password
            and self.authentication.jamf_url
        )

    def update_config(self, section: str, key: str, value: Any):
        """Update a configuration value"""
        config_obj = getattr(self, section, None)
        if config_obj and hasattr(config_obj, key):
            setattr(config_obj, key, value)
            # Save the updated config
            filename = f"{section}.json"
            self._save_config(filename, config_obj)

    def reset_to_defaults(self):
        """Reset all configurations to defaults"""
        self.ports = ServerPorts()
        self.environments = Environments()
        self.formats = OutputFormats()
        self.paths = Paths()
        self.timeouts = Timeouts()
        self.version = Version()
        self.logging = Logging()
        self.users = Users()
        self.authentication = Authentication()
        self.experimental = ExperimentalFeatures()
        self.addons = AddonConfiguration()
        self.cache = CacheConfiguration()
        self.export = ExportConfiguration()
        self.api = APIConfiguration()
        self.save_all_configs()

    def export_config(self, output_file: str):
        """Export all configuration to a file"""
        config_data = {
            "server_ports": asdict(self.ports),
            "environments": asdict(self.environments),
            "output_formats": asdict(self.formats),
            "paths": asdict(self.paths),
            "timeouts": asdict(self.timeouts),
            "version": asdict(self.version),
            "logging": asdict(self.logging),
            "users": asdict(self.users),
            "authentication": asdict(self.authentication),
            "experimental_features": asdict(self.experimental),
            "addon_configuration": asdict(self.addons),
            "cache_configuration": asdict(self.cache),
            "export_configuration": asdict(self.export),
            "api_configuration": asdict(self.api),
        }

        with open(output_file, "w") as f:
            json.dump(config_data, f, indent=2)

    def import_config(self, input_file: str):
        """Import configuration from a file"""
        with open(input_file, "r") as f:
            config_data = json.load(f)

        for section, data in config_data.items():
            config_obj = getattr(self, section, None)
            if config_obj:
                for key, value in data.items():
                    if hasattr(config_obj, key):
                        setattr(config_obj, key, value)

        self.save_all_configs()


# Global instance
central_config = CentralConfig()


# Convenience functions
def get_port(service: str) -> int:
    """Get port for a service"""
    return central_config.get_port(service)


def get_timeout(timeout_type: str) -> int:
    """Get timeout value"""
    return central_config.get_timeout(timeout_type)


def get_path(path_type: str) -> str:
    """Get expanded path"""
    return central_config.get_path(path_type)


def get_format_options(format_type: str) -> List[str]:
    """Get format options"""
    return central_config.get_format_options(format_type)


def get_log_level(component: str = None) -> str:
    """Get log level for component or default"""
    return central_config.get_log_level(component)
