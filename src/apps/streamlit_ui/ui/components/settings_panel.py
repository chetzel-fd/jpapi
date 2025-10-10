"""
Settings Panel Component - Single Responsibility Principle
Renders the settings popover with instance information
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from .base import BaseComponent
from ...core.services.environment_service import EnvironmentService
from ...core.services.object_type_service import ObjectTypeService
from ...utils.formatters import DataFormatter


class SettingsPanelComponent(BaseComponent):
    """Settings panel component for settings popover"""

    def __init__(
        self,
        env_service: EnvironmentService,
        object_service: ObjectTypeService,
        component_id: str = "settings_panel",
    ):
        super().__init__(component_id)
        self.env_service = env_service
        self.object_service = object_service
        self.formatter = DataFormatter()

    def render(self) -> None:
        """Render the settings panel component"""
        self._render_settings_panel_css()

        # Check if settings button was clicked
        if self.get_component_state("settings_clicked", False):
            self._render_settings_popover()
            self.set_component_state("settings_clicked", False)

    def _render_settings_panel_css(self) -> None:
        """Render settings panel CSS"""
        st.markdown(
            """
        <style>
        .settings-dropdown {
            position: relative;
            animation: slideDown 0.3s ease-out;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .info-card {
            background-color: #f8f9fa;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
        }
        
        .info-card h4 {
            margin: 0 0 8px 0;
            color: #333333;
            font-size: 16px;
        }
        
        .info-card p {
            margin: 4px 0;
            color: #666666;
            font-size: 14px;
        }
        
        .info-card .label {
            font-weight: bold;
            color: #333333;
        }
        
        .info-card .value {
            color: #666666;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def _render_settings_popover(self) -> None:
        """Render settings popover menu"""
        with st.popover("⚙️ Settings", use_container_width=True):
            st.markdown("### ⚙️ Settings")

            # Instance Information
            self._render_instance_info()

            st.divider()

            # Display Options
            self._render_display_options()

            st.divider()

            # Export Settings
            self._render_export_settings()

    def _render_instance_info(self) -> None:
        """Render instance information cards"""
        st.markdown("**📊 Instance Information**")

        # Environment info
        current_env = self.env_service.get_current()
        env_config = self.env_service.get_environment_config(current_env)

        st.info(
            f"""
        **Environment:** {env_config.get('display_name', current_env.title())}
        **Server:** {env_config.get('server_url', 'Not configured')}
        **Description:** {env_config.get('description', 'No description available')}
        """
        )

        # Object type info
        current_type = self.object_service.get_current()
        type_config = self.object_service.get_object_type_config(current_type)

        st.info(
            f"""
        **Object Type:** {type_config.get('display_name', current_type.title())}
        **Icon:** {type_config.get('icon', '📄')}
        **Description:** {type_config.get('description', 'No description available')}
        **JPAPI Command:** {type_config.get('jpapi_command', current_type)}
        """
        )

        # Data status info
        self._render_data_status_info()

    def _render_data_status_info(self) -> None:
        """Render data status information"""
        cache_key = (
            f"data_{self.object_service.get_current()}_{self.env_service.get_current()}"
        )
        cached_data = st.session_state.get(cache_key)

        if cached_data is not None:
            if hasattr(cached_data, "shape"):
                row_count = len(cached_data)
                col_count = len(cached_data.columns)

                st.success(
                    f"""
                **Data Status:** ✅ Loaded
                **Objects:** {row_count}
                **Columns:** {col_count}
                """
                )

                # Show data summary
                if not cached_data.empty:
                    summary = self.formatter.format_object_summary(cached_data)
                    st.caption(
                        f"🟢 {summary['active']} active • 🔴 {summary['deleted']} deleted • 🧠 {summary['smart']} smart"
                    )
            else:
                st.warning("⚠️ Data format error")
        else:
            st.warning("⚠️ No data loaded")

    def _render_display_options(self) -> None:
        """Render display options"""
        st.markdown("**🎨 Display Options**")

        # View mode
        view_mode = st.selectbox(
            "View Mode",
            options=["grid", "list"],
            index=0 if st.session_state.get("view_mode", "grid") == "grid" else 1,
            key="settings_view_mode",
        )

        if view_mode != st.session_state.get("view_mode", "grid"):
            st.session_state["view_mode"] = view_mode
            st.rerun()

        # Show deleted objects
        show_deleted = st.checkbox(
            "Show Deleted Objects",
            value=st.session_state.get("show_deleted", False),
            key="settings_show_deleted",
        )

        if show_deleted != st.session_state.get("show_deleted", False):
            st.session_state["show_deleted"] = show_deleted
            st.rerun()

        # Sort options
        sort_by = st.selectbox(
            "Sort By",
            options=["Name", "Status", "Modified", "Smart"],
            index=0,
            key="settings_sort_by",
        )

        sort_ascending = st.checkbox(
            "Ascending Order", value=True, key="settings_sort_ascending"
        )

    def _render_export_settings(self) -> None:
        """Render export settings"""
        st.markdown("**📤 Export Settings**")

        # Export format
        export_format = st.selectbox(
            "Default Export Format",
            options=["csv", "json", "xlsx"],
            index=0,
            key="settings_export_format",
        )

        # Max export rows
        max_rows = st.number_input(
            "Maximum Export Rows",
            min_value=100,
            max_value=50000,
            value=10000,
            step=1000,
            key="settings_max_export_rows",
        )

        # Include metadata
        include_metadata = st.checkbox(
            "Include Metadata in Export", value=True, key="settings_include_metadata"
        )

    def set_settings_clicked(self) -> None:
        """Set settings button as clicked"""
        self.set_component_state("settings_clicked", True)

    def get_component_info(self) -> Dict[str, Any]:
        """Get settings panel component information"""
        info = super().get_component_info()
        info.update(
            {
                "settings_clicked": self.get_component_state("settings_clicked", False),
                "current_environment": self.env_service.get_current(),
                "current_object_type": self.object_service.get_current(),
                "view_mode": st.session_state.get("view_mode", "grid"),
                "show_deleted": st.session_state.get("show_deleted", False),
            }
        )
        return info
