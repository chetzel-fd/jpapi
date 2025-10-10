"""
Header Component - Single Responsibility Principle
Renders the main application header with title and action buttons
"""

import streamlit as st
from typing import Dict, Any, Optional
from .base import BaseComponent
from ..styles.theme import ThemeManager


class HeaderComponent(BaseComponent):
    """Header component for the main application"""

    def __init__(self, component_id: str = "header"):
        super().__init__(component_id)
        self.theme = ThemeManager()

    def render(self) -> None:
        """Render the header component"""
        self._render_header_css()

        # Main header layout
        header_col1, header_col2 = st.columns([3, 1])

        with header_col1:
            self._render_title()

        with header_col2:
            self._render_action_buttons()

    def _render_header_css(self) -> None:
        """Render header-specific CSS"""
        st.markdown(
            """
        <style>
        .header-buttons {
            display: flex;
            gap: 8px;
            align-items: center;
            justify-content: flex-end;
        }
        
        .header-buttons .stButton > button {
            width: 36px;
            height: 36px;
            min-width: 36px;
            padding: 0;
            border-radius: 8px;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #e1e5e9;
            background-color: #ffffff;
            color: #333333;
            transition: all 0.2s ease;
        }
        
        .header-buttons .stButton > button:hover {
            background-color: #f8f9fa;
            border-color: #007bff;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header-title {
            font-size: 28px;
            font-weight: bold;
            color: #333333;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def _render_title(self) -> None:
        """Render the application title"""
        st.markdown(
            """
        <div class="header-title">
            ⚡ JPAPI Manager
        </div>
        """,
            unsafe_allow_html=True,
        )

    def _render_action_buttons(self) -> None:
        """Render action buttons"""
        st.markdown('<div class="header-buttons">', unsafe_allow_html=True)

        # Actions button (⚡)
        if st.button("⚡", key="header_actions", help="Actions"):
            self._handle_actions_click()

        # Notifications button (🔔)
        if st.button("🔔", key="header_notifications", help="Notifications"):
            self._handle_notifications_click()

        # Refresh button (🔄)
        if st.button("🔄", key="header_refresh", help="Refresh Data"):
            self._handle_refresh_click()

        # Settings button (⚙️)
        if st.button("⚙️", key="header_settings", help="Settings"):
            self._handle_settings_click()

        st.markdown("</div>", unsafe_allow_html=True)

    def _handle_actions_click(self) -> None:
        """Handle actions button click"""
        self.set_component_state("actions_clicked", True)

    def _handle_notifications_click(self) -> None:
        """Handle notifications button click"""
        self.set_component_state("notifications_clicked", True)

    def _handle_refresh_click(self) -> None:
        """Handle refresh button click"""
        self.set_component_state("refresh_clicked", True)
        # Clear all data cache
        for key in st.session_state.keys():
            if key.startswith("data_"):
                del st.session_state[key]
        st.rerun()

    def _handle_settings_click(self) -> None:
        """Handle settings button click"""
        self.set_component_state("settings_clicked", True)

    def get_clicked_action(self) -> Optional[str]:
        """Get which action was clicked"""
        if self.get_component_state("actions_clicked"):
            self.set_component_state("actions_clicked", False)
            return "actions"
        elif self.get_component_state("notifications_clicked"):
            self.set_component_state("notifications_clicked", False)
            return "notifications"
        elif self.get_component_state("refresh_clicked"):
            self.set_component_state("refresh_clicked", False)
            return "refresh"
        elif self.get_component_state("settings_clicked"):
            self.set_component_state("settings_clicked", False)
            return "settings"
        return None

    def render_instance_info(
        self, environment: str, object_type: str, server_url: str
    ) -> None:
        """Render instance information in sidebar"""
        st.sidebar.markdown("### 📊 Instance Info")

        # Environment info
        st.sidebar.info(f"**Environment:** {environment.title()}")

        # Object type info
        st.sidebar.info(f"**Object Type:** {object_type.title()}")

        # Server URL info
        if server_url:
            st.sidebar.info(f"**Server:** {server_url}")

    def get_component_info(self) -> Dict[str, Any]:
        """Get header component information"""
        info = super().get_component_info()
        info.update(
            {
                "actions_clicked": self.get_component_state("actions_clicked", False),
                "notifications_clicked": self.get_component_state(
                    "notifications_clicked", False
                ),
                "refresh_clicked": self.get_component_state("refresh_clicked", False),
                "settings_clicked": self.get_component_state("settings_clicked", False),
            }
        )
        return info
