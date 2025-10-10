"""
Controls Component - Single Responsibility Principle
Renders environment and object type controls
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from .base import BaseComponent
from ...core.services.environment_service import EnvironmentService
from ...core.services.object_type_service import ObjectTypeService
from ...utils.formatters import DataFormatter


class ControlsComponent(BaseComponent):
    """Controls component for environment and object type selection"""

    def __init__(
        self,
        env_service: EnvironmentService,
        object_service: ObjectTypeService,
        component_id: str = "controls",
    ):
        super().__init__(component_id)
        self.env_service = env_service
        self.object_service = object_service
        self.formatter = DataFormatter()

    def render(self) -> None:
        """Render the controls component"""
        self._render_controls_css()

        # Controls layout
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            self._render_environment_selector()

        with col2:
            self._render_object_type_selector()

        with col3:
            self._render_data_info()

    def _render_controls_css(self) -> None:
        """Render controls-specific CSS"""
        st.markdown(
            """
        <style>
        .controls-container {
            margin-bottom: 16px;
        }
        
        .control-label {
            font-size: 14px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 4px;
        }
        
        .data-info {
            background-color: #f8f9fa;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
        }
        
        .data-info h4 {
            margin: 0 0 8px 0;
            color: #333333;
            font-size: 16px;
        }
        
        .data-info p {
            margin: 4px 0;
            color: #666666;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def _render_environment_selector(self) -> None:
        """Render environment selector"""
        st.markdown(
            '<div class="control-label">Environment</div>', unsafe_allow_html=True
        )

        current_env = self.env_service.get_current()
        available_envs = self.env_service.get_available_environments()

        # Create environment options with display names
        env_options = [
            (f"🌍 {self.env_service.get_display_name(env)}", env)
            for env in available_envs
        ]

        selected_env = st.selectbox(
            "Select Environment",
            options=[opt[1] for opt in env_options],
            format_func=lambda x: next(opt[0] for opt in env_options if opt[1] == x),
            key="env_selector",
            help="Choose the JAMF Pro environment",
        )

        # Handle environment change
        if selected_env != current_env:
            self.env_service.set_current(selected_env)
            self._clear_data_cache()
            st.rerun()

    def _render_object_type_selector(self) -> None:
        """Render object type selector"""
        st.markdown(
            '<div class="control-label">Object Type</div>', unsafe_allow_html=True
        )

        current_type = self.object_service.get_current()
        available_types = self.object_service.get_available_object_types()

        # Create object type options with icons and display names
        type_options = [
            (
                f"{self.object_service.get_icon(obj_type)} {self.object_service.get_display_name(obj_type)}",
                obj_type,
            )
            for obj_type in available_types
        ]

        selected_type = st.selectbox(
            "Select Object Type",
            options=[opt[1] for opt in type_options],
            format_func=lambda x: next(opt[0] for opt in type_options if opt[1] == x),
            key="type_selector",
            help="Choose the type of objects to view",
        )

        # Handle object type change
        if selected_type != current_type:
            self.object_service.set_current(selected_type)
            self._clear_data_cache()
            st.rerun()

    def _render_data_info(self) -> None:
        """Render data information panel"""
        st.markdown(
            """
        <div class="data-info">
            <h4>📊 Data Status</h4>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Get cached data info
        cache_key = (
            f"data_{self.object_service.get_current()}_{self.env_service.get_current()}"
        )
        cached_data = st.session_state.get(cache_key)

        if cached_data is not None:
            # Data is loaded
            if hasattr(cached_data, "shape"):
                row_count = len(cached_data)
                col_count = len(cached_data.columns)

                st.success(f"✅ **{row_count}** objects loaded")
                st.caption(
                    f"📋 {col_count} columns • Environment: {self.env_service.get_current().title()}"
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
            # No data loaded
            st.warning("⚠️ No data loaded")
            st.caption("Click 'Gather Data' to load objects")

    def _clear_data_cache(self) -> None:
        """Clear data cache when switching environments or object types"""
        # Clear all data cache
        for key in st.session_state.keys():
            if key.startswith("data_"):
                del st.session_state[key]

    def get_current_selections(self) -> Dict[str, str]:
        """Get current environment and object type selections"""
        return {
            "environment": self.env_service.get_current(),
            "object_type": self.object_service.get_current(),
        }

    def get_environment_info(self) -> Dict[str, Any]:
        """Get current environment information"""
        current_env = self.env_service.get_current()
        return self.env_service.get_environment_info(current_env)

    def get_object_type_info(self) -> Dict[str, Any]:
        """Get current object type information"""
        current_type = self.object_service.get_current()
        return self.object_service.get_object_type_info(current_type)

    def get_component_info(self) -> Dict[str, Any]:
        """Get controls component information"""
        info = super().get_component_info()
        info.update(
            {
                "current_environment": self.env_service.get_current(),
                "current_object_type": self.object_service.get_current(),
                "available_environments": self.env_service.get_available_environments(),
                "available_object_types": self.object_service.get_available_object_types(),
            }
        )
        return info
