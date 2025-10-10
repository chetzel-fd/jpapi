"""
Object Type Service - Single Responsibility Principle
Manages object type selection and configuration
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from ..config.settings import Settings
from ..config.constants import DEFAULT_OBJECT_TYPE


class ObjectTypeService:
    """Object type management service"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session_key = "current_object_type"
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize session state for object type"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = DEFAULT_OBJECT_TYPE

    def get_current(self) -> str:
        """Get current object type"""
        return st.session_state.get(self.session_key, DEFAULT_OBJECT_TYPE)

    def set_current(self, object_type: str) -> None:
        """Set current object type"""
        if self.validate(object_type):
            st.session_state[self.session_key] = object_type

    def get_available_object_types(self) -> List[str]:
        """Get list of available object types"""
        return self.settings.get_object_type_names()

    def get_object_type_config(self, object_type: str) -> Dict[str, Any]:
        """Get configuration for specific object type"""
        return self.settings.get_object_type_config(object_type)

    def get_display_name(self, object_type: str) -> str:
        """Get display name for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("display_name", object_type.title())

    def get_icon(self, object_type: str) -> str:
        """Get icon for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("icon", "📄")

    def get_description(self, object_type: str) -> str:
        """Get description for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("description", "")

    def get_jpapi_command(self, object_type: str) -> str:
        """Get JPAPI command for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("jpapi_command", object_type)

    def get_file_patterns(self, object_type: str) -> List[str]:
        """Get file patterns for object type"""
        config = self.get_object_type_config(object_type)
        return config.get("file_patterns", [])

    def validate(self, object_type: str) -> bool:
        """Validate object type"""
        return object_type in self.get_available_object_types()

    def get_object_type_info(self, object_type: str) -> Dict[str, Any]:
        """Get comprehensive object type information"""
        config = self.get_object_type_config(object_type)
        return {
            "name": object_type,
            "display_name": config.get("display_name", object_type.title()),
            "icon": config.get("icon", "📄"),
            "description": config.get("description", ""),
            "jpapi_command": config.get("jpapi_command", object_type),
            "file_patterns": config.get("file_patterns", []),
            "is_current": object_type == self.get_current(),
        }

    def switch_object_type(self, new_object_type: str) -> bool:
        """Switch to new object type and clear related cache"""
        if self.validate(new_object_type):
            old_object_type = self.get_current()
            self.set_current(new_object_type)

            # Clear cache for old object type
            if old_object_type != new_object_type:
                self._clear_object_type_cache(old_object_type)

            return True
        return False

    def _clear_object_type_cache(self, object_type: str) -> None:
        """Clear cache for specific object type"""
        # This will be handled by the cache manager
        # when we integrate with it
        pass

    def get_object_types_for_dropdown(self) -> List[tuple]:
        """Get object types formatted for Streamlit dropdown"""
        return [
            (f"{self.get_icon(obj_type)} {self.get_display_name(obj_type)}", obj_type)
            for obj_type in self.get_available_object_types()
        ]
