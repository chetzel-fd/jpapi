#!/usr/bin/env python3
"""
Main Dashboard Application - SOLID Compliant
"""
import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dashboard.factory import ManagerFactory
    from dashboard.ui_components_refactored import DashboardUI
except ImportError as e:
    st.error(f"Dashboard modules not found: {e}")
    st.info("Running in demo mode")
    ManagerFactory = None
    DashboardUI = None


class DashboardApp:
    """Main Dashboard Application - SOLID SRP compliance"""

    def __init__(self):
        self.ui = DashboardUI()
        self.factory = ManagerFactory()

    def configure_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="jpapi manager",
            page_icon="🍎",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def initialize_session_state(self):
        """Initialize session state variables"""
        if "deletion_results" not in st.session_state:
            st.session_state.deletion_results = []

    def render_sidebar_controls(self):
        """Render sidebar controls - SOLID SRP"""
        st.sidebar.header("🎛️ Dashboard Controls")

        # Object type selection
        available_types = self.factory.get_available_types()
        object_type = st.sidebar.selectbox(
            "Select Object Type:",
            options=available_types,
            index=0,
            help="Choose which type of JAMF objects to manage",
        )

        st.sidebar.markdown("---")

        # Advanced search filters
        if object_type == "advanced-searches":
            st.sidebar.subheader("🔍 Advanced Search Filters")

            # Search type filter
            search_type = st.sidebar.selectbox(
                "Search Type:",
                options=["All", "Computer", "Mobile", "User"],
                index=0,
                help="Filter by advanced search type",
            )

            # Status filter
            status_filter = st.sidebar.selectbox(
                "Status:",
                options=["All", "Static", "Smart"],
                index=0,
                help="Filter by search status",
            )

            # Name search
            name_search = st.sidebar.text_input(
                "Search by name:",
                placeholder="Enter search term...",
                help="Filter searches by name",
            )

            # Store filters in session state
            st.session_state.search_filters = {
                "search_type": search_type,
                "status_filter": status_filter,
                "name_search": name_search,
            }

            st.sidebar.markdown("---")

        return object_type

    def create_manager(self, object_type: str):
        """Create appropriate manager - SOLID DIP"""
        try:
            return self.factory.create_manager(object_type)
        except ValueError as e:
            st.error(f"Error creating manager: {e}")
            return None

    def load_data(self, manager):
        """Load data using manager - SOLID DIP"""
        if not manager:
            return None

        # Load data
        df = manager.load_data()

        # Apply filters if available
        if (
            hasattr(st.session_state, "search_filters")
            and st.session_state.search_filters
        ):
            df = self.apply_filters(df)

        return df

    def apply_filters(self, df):
        """Apply sidebar filters to the dataframe"""
        filters = st.session_state.search_filters

        # Filter by search type based on name patterns
        if filters["search_type"] != "All":
            if filters["search_type"] == "Computer":
                computer_keywords = [
                    "mac",
                    "macbook",
                    "computer",
                    "laptop",
                    "desktop",
                    "imac",
                ]
                df = df[
                    df["Name"].str.contains(
                        "|".join(computer_keywords), case=False, na=False
                    )
                ]
            elif filters["search_type"] == "Mobile":
                mobile_keywords = [
                    "iphone",
                    "ipad",
                    "mobile",
                    "device",
                    "ios",
                    "android",
                ]
                df = df[
                    df["Name"].str.contains(
                        "|".join(mobile_keywords), case=False, na=False
                    )
                ]
            elif filters["search_type"] == "User":
                user_keywords = ["user", "people", "person", "staff", "employee"]
                df = df[
                    df["Name"].str.contains(
                        "|".join(user_keywords), case=False, na=False
                    )
                ]

        # Filter by status (using Smart column)
        if filters["status_filter"] != "All":
            if filters["status_filter"] == "Smart":
                df = df[df["Smart"] == True]
            elif filters["status_filter"] == "Static":
                df = df[df["Smart"] == False]

        # Filter by name search
        if filters["name_search"]:
            search_term = filters["name_search"].lower()
            df = df[df["Name"].str.contains(search_term, case=False, na=False)]

        return df

    def render_refresh_controls(self, manager):
        """Render refresh controls - SOLID SRP"""
        if st.sidebar.button("🔄 Refresh from JAMF", type="primary"):
            with st.spinner("Refreshing from JAMF Pro..."):
                success, message = manager.refresh_data()
                if success:
                    st.success(message)
                    st.rerun()
                    # Add JavaScript to scroll to top after refresh
                    st.markdown(
                        """
                        <script>
                        window.parent.scrollTo(0, 0);
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.error(message)

    def run(self):
        """Main application runner - SOLID SRP"""
        # Configure page
        self.configure_page()

        # Initialize session state
        self.initialize_session_state()

        # Render custom CSS
        self.ui.render_custom_css()

        # Render sidebar controls
        object_type = self.render_sidebar_controls()

        # Create manager
        manager = self.create_manager(object_type)
        if not manager:
            return

        # Load data
        df = self.load_data(manager)
        if df is None or df.empty:
            st.error("❌ No data found")
            return

        # Render header
        self.ui.render_header(
            f"jpapi manager",
            f"elegant {object_type.replace('-', ' ')} management",
        )

        # Render refresh controls
        self.render_refresh_controls(manager)
        st.sidebar.markdown("---")

        # Render stats
        self.ui.render_stats(df)
        st.markdown("---")

        # Render selection interface (now includes grid layout and sorting)
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
