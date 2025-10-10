"""
Dashboard Page - Single Responsibility Principle
Main dashboard page that orchestrates all components
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from ..components.header import HeaderComponent
from ..components.controls import ControlsComponent
from ..components.object_card import ObjectCardComponent
from ..components.action_menu import ActionMenuComponent
from ..components.settings_panel import SettingsPanelComponent
from ...core.data.csv_loader import CSVLoader
from ...core.data.cache_manager import CacheManager
from ...core.data.validators import CSVDataValidator
from ...core.services.environment_service import EnvironmentService
from ...core.services.object_type_service import ObjectTypeService
from ...core.services.jpapi_integration import JPAPIIntegrationService
from ...core.services.export_service import ExportService
from ...core.config.settings import Settings
from ...core.config.paths import Paths
from ...utils.session_manager import SessionManager
from ...utils.formatters import DataFormatter
from ...utils.helpers import HelperFunctions


class Dashboard:
    """Main dashboard page class"""

    def __init__(self):
        # Initialize configuration
        self.settings = Settings()
        self.paths = Paths()

        # Initialize services
        self.env_service = EnvironmentService(self.settings)
        self.object_service = ObjectTypeService(self.settings)
        self.jpapi_service = JPAPIIntegrationService(self.paths.project_root)
        self.export_service = ExportService()

        # Initialize data layer
        self.validator = CSVDataValidator()
        self.cache_manager = CacheManager()
        self.data_loader = CSVLoader(self.validator, self.settings)

        # Initialize utilities
        self.session_manager = SessionManager()
        self.formatter = DataFormatter()
        self.helpers = HelperFunctions()

        # Initialize components
        self.header = HeaderComponent()
        self.controls = ControlsComponent(self.env_service, self.object_service)
        self.object_cards = ObjectCardComponent()
        self.action_menu = ActionMenuComponent(self.jpapi_service, self.export_service)
        self.settings_panel = SettingsPanelComponent(
            self.env_service, self.object_service
        )

    def render(self) -> None:
        """Render the main dashboard"""
        # Set page configuration
        self._configure_page()

        # Render header
        self.header.render()

        # Handle header button clicks
        clicked_action = self.header.get_clicked_action()
        if clicked_action == "actions":
            self.action_menu.set_actions_clicked()
        elif clicked_action == "settings":
            self.settings_panel.set_settings_clicked()

        # Render controls
        self.controls.render()

        # Load and display data
        self._load_and_display_data()

        # Render action menu and settings panel
        self.action_menu.render()
        self.settings_panel.render()

        # Render instance info in sidebar
        self._render_sidebar_info()

    def _configure_page(self) -> None:
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=self.settings.UI_CONFIG["page_title"],
            page_icon=self.settings.UI_CONFIG["page_icon"],
            layout=self.settings.UI_CONFIG["layout"],
            initial_sidebar_state=self.settings.UI_CONFIG["initial_sidebar_state"],
        )

    def _load_and_display_data(self) -> None:
        """Load and display data based on current selections"""
        current_env = self.env_service.get_current()
        current_type = self.object_service.get_current()

        # Create cache key
        cache_key = f"data_{current_type}_{current_env}"

        # Check if data is cached
        cached_data = self.cache_manager.get(cache_key)

        if cached_data is None:
            # Load data
            with st.spinner(f"Loading {current_type} data from {current_env}..."):
                data = self.data_loader.load(current_type, current_env)

                # Cache the data
                self.cache_manager.set(cache_key, data)
                cached_data = data

        # Display data
        if not cached_data.empty:
            self._display_data(cached_data)
        else:
            st.warning("⚠️ No data available")
            st.info(
                "Click 'Gather Data' in the Actions menu to load data from JAMF Pro"
            )

    def _display_data(self, data: pd.DataFrame) -> None:
        """Display data using object cards"""
        # Get display options
        view_mode = st.session_state.get("view_mode", "grid")
        show_deleted = st.session_state.get("show_deleted", False)

        # Filter data
        filtered_data = self._filter_data(data, show_deleted)

        if filtered_data.empty:
            st.info("No objects match the current filters")
            return

        # Sort data
        sort_by = st.session_state.get("sort_by", "Name")
        sort_ascending = st.session_state.get("sort_ascending", True)
        sorted_data = self.helpers.sort_dataframe(
            filtered_data, sort_by, sort_ascending
        )

        # Display data
        if view_mode == "grid":
            self.object_cards.render_object_grid(sorted_data)
        else:
            self.object_cards.render_object_list(sorted_data)

        # Display summary
        self._display_data_summary(sorted_data)

    def _filter_data(self, data: pd.DataFrame, show_deleted: bool) -> pd.DataFrame:
        """Filter data based on current settings"""
        if data.empty:
            return data

        # Filter out deleted objects if not showing deleted
        if not show_deleted and "Status" in data.columns:
            return data[data["Status"] != "Deleted"]

        return data

    def _display_data_summary(self, data: pd.DataFrame) -> None:
        """Display data summary"""
        if data.empty:
            return

        # Get summary statistics
        summary = self.formatter.format_object_summary(data)

        # Display summary in columns
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total", summary["total"])

        with col2:
            st.metric("Active", summary["active"])

        with col3:
            st.metric("Deleted", summary["deleted"])

        with col4:
            st.metric("Smart", summary["smart"])

        with col5:
            st.metric("Static", summary["static"])

    def _render_sidebar_info(self) -> None:
        """Render instance information in sidebar"""
        current_env = self.env_service.get_current()
        current_type = self.object_service.get_current()

        # Get server URL
        server_url = self.env_service.get_server_url(current_env)

        # Render instance info
        self.header.render_instance_info(current_env, current_type, server_url)

        # Render selection info
        selected_count = self.object_cards.get_selection_count()
        if selected_count > 0:
            st.sidebar.success(f"✅ {selected_count} objects selected")

        # Render data info
        cache_key = f"data_{current_type}_{current_env}"
        cached_data = st.session_state.get(cache_key)

        if cached_data is not None and hasattr(cached_data, "shape"):
            st.sidebar.info(f"📊 {len(cached_data)} objects loaded")

    def get_dashboard_info(self) -> Dict[str, Any]:
        """Get comprehensive dashboard information"""
        return {
            "environment": self.env_service.get_current(),
            "object_type": self.object_service.get_current(),
            "view_mode": st.session_state.get("view_mode", "grid"),
            "show_deleted": st.session_state.get("show_deleted", False),
            "selected_count": self.object_cards.get_selection_count(),
            "data_loaded": st.session_state.get("data_loaded", False),
            "components": {
                "header": self.header.get_component_info(),
                "controls": self.controls.get_component_info(),
                "object_cards": self.object_cards.get_component_info(),
                "action_menu": self.action_menu.get_component_info(),
                "settings_panel": self.settings_panel.get_component_info(),
            },
        }
