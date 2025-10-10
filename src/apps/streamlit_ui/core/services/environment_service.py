"""
Environment Service - Single Responsibility Principle
Manages environment selection and configuration
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from ..config.settings import Settings
from ..config.constants import DEFAULT_ENVIRONMENT


class EnvironmentService:
    """Environment management service"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session_key = "current_environment"
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize session state for environment"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = DEFAULT_ENVIRONMENT

    def get_current(self) -> str:
        """Get current environment"""
        return st.session_state.get(self.session_key, DEFAULT_ENVIRONMENT)

    def set_current(self, environment: str) -> None:
        """Set current environment"""
        if self.validate(environment):
            st.session_state[self.session_key] = environment

    def get_available_environments(self) -> List[str]:
        """Get list of available environments"""
        return self.settings.get_environment_names()

    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for specific environment"""
        return self.settings.get_environment_config(environment)

    def get_server_url(self, environment: str) -> str:
        """Get server URL for environment"""
        config = self.get_environment_config(environment)
        return config.get("server_url", "")

    def get_display_name(self, environment: str) -> str:
        """Get display name for environment"""
        config = self.get_environment_config(environment)
        return config.get("display_name", environment.title())

    def validate(self, environment: str) -> bool:
        """Validate environment"""
        return environment in self.get_available_environments()

    def get_environment_info(self, environment: str) -> Dict[str, Any]:
        """Get comprehensive environment information"""
        config = self.get_environment_config(environment)
        return {
            "name": environment,
            "display_name": config.get("display_name", environment.title()),
            "server_url": config.get("server_url", ""),
            "description": config.get("description", ""),
            "is_current": environment == self.get_current(),
        }

    def switch_environment(self, new_environment: str) -> bool:
        """Switch to new environment and clear related cache"""
        if self.validate(new_environment):
            old_environment = self.get_current()
            self.set_current(new_environment)

            # Clear cache for old environment
            if old_environment != new_environment:
                self._clear_environment_cache(old_environment)

            return True
        return False

    def _clear_environment_cache(self, environment: str) -> None:
        """Clear cache for specific environment"""
        # This will be handled by the cache manager
        # when we integrate with it
        pass
