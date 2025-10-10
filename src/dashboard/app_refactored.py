#!/usr/bin/env python3
"""
Main Dashboard Application - SOLID Refactored
Now properly separated into focused, single-responsibility components
"""
import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dashboard.factory import ManagerFactory
    from dashboard.ui_components_refactored import DashboardUI
    from services import DataService, FilterService, ManagerCoordinator
    from controllers import DashboardController
except ImportError as e:
    st.error(f"Dashboard modules not found: {e}")
    st.info("Running in demo mode")
    ManagerFactory = None
    DashboardUI = None


class DashboardApp:
    """Main Dashboard Application - SOLID SRP compliance"""

    def __init__(self):
        # Initialize services - SOLID DIP
        self.data_service = DataService()
        self.filter_service = FilterService()
        self.manager_coordinator = ManagerCoordinator(ManagerFactory())

        # Initialize controller - SOLID DIP
        self.controller = DashboardController(
            self.data_service, self.filter_service, self.manager_coordinator
        )

        # Initialize UI
        self.ui = DashboardUI() if DashboardUI else None

    def configure_page(self):
        """Configure Streamlit page settings - SOLID SRP"""
        st.set_page_config(
            page_title="jpapi manager",
            page_icon="🍎",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def initialize_session_state(self):
        """Initialize session state variables - SOLID SRP"""
        if "deletion_results" not in st.session_state:
            st.session_state.deletion_results = []
        if "search_filters" not in st.session_state:
            st.session_state.search_filters = {
                "search_type": "All",
                "status_filter": "All",
                "name_search": "",
            }

    def render_sidebar_controls(self):
        """Render sidebar controls - SOLID SRP"""
        st.sidebar.header("🎛️ Dashboard Controls")

        # Object type selection - SOLID DIP
        available_types = self.controller.get_available_types()
        object_type = st.sidebar.selectbox(
            "Select Object Type:", options=available_types, index=0
        )

        # Search filters - SOLID DIP
        self._render_search_filters()

        return object_type

    def _render_search_filters(self):
        """Render search filters - SOLID SRP"""
        st.sidebar.markdown("### 🔍 Search Filters")

        # Search type filter
        search_types = self.filter_service.get_available_search_types()
        search_type = st.sidebar.selectbox(
            "Search Type:", options=search_types, index=0
        )

        # Status filter
        status_filters = self.filter_service.get_available_status_filters()
        status_filter = st.sidebar.selectbox(
            "Status Filter:", options=status_filters, index=0
        )

        # Name search
        name_search = st.sidebar.text_input("Name Search:", value="")

        # Update session state
        st.session_state.search_filters = {
            "search_type": search_type,
            "status_filter": status_filter,
            "name_search": name_search,
        }

    def render_refresh_controls(self, object_type: str):
        """Render refresh controls - SOLID SRP"""
        if st.sidebar.button("🔄 Refresh from JAMF", type="primary"):
            with st.spinner("Refreshing from JAMF Pro..."):
                success, message = self.controller.refresh_data(object_type)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    def run(self):
        """Main application runner - SOLID SRP"""
        # Configure page
        self.configure_page()

        # Initialize session state
        self.initialize_session_state()

        # Render custom CSS
        if self.ui:
            self.ui.render_custom_css()

        # Render sidebar controls
        object_type = self.render_sidebar_controls()

        # Load and filter data - SOLID DIP
        df = self.controller.load_and_filter_data(
            object_type, st.session_state.search_filters
        )

        if df is None or df.empty:
            st.error("❌ No data found")
            return

        # Render header
        if self.ui:
            self.ui.render_header(
                f"jpapi manager",
                f"elegant {object_type.replace('-', ' ')} management",
            )

        # Render refresh controls
        self.render_refresh_controls(object_type)
        st.sidebar.markdown("---")

        # Render stats
        if self.ui:
            self.ui.render_stats(df)
        st.markdown("---")

        # Render selection interface
        if self.ui:
            manager = self.controller.get_manager(object_type)
            selected_items = self.ui.render_selection_interface(df, manager)

            # Render deletion interface
            self.ui.render_deletion_interface(df, manager)

        # Show clean status message
        if not st.session_state.get("deletion_results", []):
            st.info("👆 Select items from the grid above to delete them")


def main():
    """Entry point for the dashboard application"""
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()
