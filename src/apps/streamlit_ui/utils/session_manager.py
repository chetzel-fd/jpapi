"""
Session Manager - Session State Management
Centralized session state management for the JPAPI Streamlit UI
"""

import streamlit as st
from typing import Any, Dict, List, Optional
from core.config.constants import DEFAULT_ENVIRONMENT, DEFAULT_OBJECT_TYPE


class SessionManager:
    """Session state management utility"""

    def __init__(self):
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize default session state values"""
        defaults = {
            "current_environment": DEFAULT_ENVIRONMENT,
            "current_object_type": DEFAULT_OBJECT_TYPE,
            "data_loaded": False,
            "last_refresh": None,
            "selected_objects": [],
            "view_mode": "grid",
            "show_deleted": False,
            "sort_by": "Name",
            "sort_ascending": True,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get session state value"""
        return st.session_state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set session state value"""
        st.session_state[key] = value

    def clear(self, pattern: Optional[str] = None) -> None:
        """Clear session state by pattern"""
        if pattern is None:
            # Clear all data-related keys
            keys_to_remove = [
                key
                for key in st.session_state.keys()
                if key.startswith("data_") or key.startswith("cache_")
            ]
            for key in keys_to_remove:
                del st.session_state[key]
        else:
            # Clear specific pattern
            keys_to_remove = [key for key in st.session_state.keys() if pattern in key]
            for key in keys_to_remove:
                del st.session_state[key]

    def reset_to_defaults(self) -> None:
        """Reset session state to defaults"""
        self.clear()
        self._initialize_session_state()

    def get_environment(self) -> str:
        """Get current environment"""
        return self.get("current_environment", DEFAULT_ENVIRONMENT)

    def set_environment(self, environment: str) -> None:
        """Set current environment"""
        self.set("current_environment", environment)
        # Clear data cache when switching environments
        self.clear("data_")

    def get_object_type(self) -> str:
        """Get current object type"""
        return self.get("current_object_type", DEFAULT_OBJECT_TYPE)

    def set_object_type(self, object_type: str) -> None:
        """Set current object type"""
        self.set("current_object_type", object_type)
        # Clear data cache when switching object types
        self.clear("data_")

    def get_selected_objects(self) -> List[str]:
        """Get list of selected objects"""
        return self.get("selected_objects", [])

    def set_selected_objects(self, objects: List[str]) -> None:
        """Set selected objects"""
        self.set("selected_objects", objects)

    def add_selected_object(self, object_id: str) -> None:
        """Add object to selection"""
        selected = self.get_selected_objects()
        if object_id not in selected:
            selected.append(object_id)
            self.set_selected_objects(selected)

    def remove_selected_object(self, object_id: str) -> None:
        """Remove object from selection"""
        selected = self.get_selected_objects()
        if object_id in selected:
            selected.remove(object_id)
            self.set_selected_objects(selected)

    def clear_selection(self) -> None:
        """Clear all selected objects"""
        self.set_selected_objects([])

    def is_object_selected(self, object_id: str) -> bool:
        """Check if object is selected"""
        return object_id in self.get_selected_objects()

    def get_view_mode(self) -> str:
        """Get current view mode"""
        return self.get("view_mode", "grid")

    def set_view_mode(self, mode: str) -> None:
        """Set view mode"""
        self.set("view_mode", mode)

    def get_show_deleted(self) -> bool:
        """Get show deleted setting"""
        return self.get("show_deleted", False)

    def set_show_deleted(self, show: bool) -> None:
        """Set show deleted setting"""
        self.set("show_deleted", show)

    def get_sort_settings(self) -> Dict[str, Any]:
        """Get sort settings"""
        return {
            "sort_by": self.get("sort_by", "Name"),
            "sort_ascending": self.get("sort_ascending", True),
        }

    def set_sort_settings(self, sort_by: str, ascending: bool = True) -> None:
        """Set sort settings"""
        self.set("sort_by", sort_by)
        self.set("sort_ascending", ascending)

    def get_session_info(self) -> Dict[str, Any]:
        """Get comprehensive session information"""
        return {
            "environment": self.get_environment(),
            "object_type": self.get_object_type(),
            "selected_count": len(self.get_selected_objects()),
            "view_mode": self.get_view_mode(),
            "show_deleted": self.get_show_deleted(),
            "sort_settings": self.get_sort_settings(),
            "data_loaded": self.get("data_loaded", False),
            "last_refresh": self.get("last_refresh"),
        }
