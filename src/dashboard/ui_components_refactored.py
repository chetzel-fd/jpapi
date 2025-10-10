"""
UI Components - SOLID SRP compliance
Refactored into focused, single-responsibility classes
"""

import streamlit as st
from typing import List, Dict, Any
import pandas as pd
import os


class CSSRenderer:
    """Handles CSS rendering - SOLID SRP"""

    @staticmethod
    def render_custom_css():
        """Render enhanced custom CSS"""
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Hide Streamlit branding */
            #MainMenu {visibility: hidden;}
            .stDeployButton {display: none;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            .main > div {
                padding-top: 1rem;
                max-width: none !important;
            }
            
            /* Clean dark theme */
            .stApp {
                background: #0a0a0a;
                color: #ffffff;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            }
            
            /* Better stats buttons */
            .stats-container {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 24px;
                backdrop-filter: blur(20px);
            }
            
            .stats-button {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .stats-button:hover {
                background: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
            }
            
            .stats-number {
                font-size: 2rem;
                font-weight: 700;
                color: #ffffff;
                margin: 0;
            }
            
            .stats-label {
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.7);
                margin: 4px 0 0 0;
                font-weight: 500;
            }
            
            /* Enhanced object cards */
            .object-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 24px;
                margin: 12px 0;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                backdrop-filter: blur(20px);
                min-height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            
            .object-card:hover {
                background: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            .object-card.selected {
                background: rgba(255, 193, 7, 0.15);
                border-color: #ffc107;
                box-shadow: 0 0 0 1px rgba(255, 193, 7, 0.3);
            }
            
            .object-card.deleted {
                background: rgba(220, 53, 69, 0.15);
                border-color: #dc3545;
                box-shadow: 0 0 0 1px rgba(220, 53, 69, 0.3);
            }
            
            .object-title {
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 8px;
                line-height: 1.3;
            }
            
            .object-details {
                font-size: 15px;
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 12px;
            }
            
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .status-active {
                background: rgba(34, 197, 94, 0.2);
                color: #22c55e;
                border: 1px solid rgba(34, 197, 94, 0.3);
            }
            
            .status-selected {
                background: rgba(255, 193, 7, 0.2);
                color: #ffc107;
                border: 1px solid rgba(255, 193, 7, 0.3);
            }
            
            .status-deleted {
                background: rgba(220, 53, 69, 0.2);
                color: #dc3545;
                border: 1px solid rgba(220, 53, 69, 0.3);
            }
            
            /* Selection buttons */
            .stButton > button {
                width: 100%;
                height: 32px;
                border-radius: 16px;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            
            .stButton > button[type="primary"] {
                background: #ffc107;
                color: #000;
                border-color: #ffc107;
            }
            
            .stButton > button[type="primary"]:hover {
                background: #ffb300;
                border-color: #ffb300;
                transform: scale(1.05);
            }
            
            .stButton > button[type="secondary"] {
                background: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.7);
                border-color: rgba(255, 255, 255, 0.3);
            }
            
            .stButton > button[type="secondary"]:hover {
                background: rgba(255, 255, 255, 0.2);
                color: #fff;
                border-color: rgba(255, 255, 255, 0.5);
                transform: scale(1.05);
            }
            
            /* Sidebar styling */
            .css-1d391kg {
                background: rgba(0, 0, 0, 0.8);
            }
            
            .css-1d391kg .css-1v0mbdj {
                color: #ffffff;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


class HeaderRenderer:
    """Handles header rendering - SOLID SRP"""

    @staticmethod
    def render_header(title: str, subtitle: str):
        """Render dashboard header with enhanced styling"""
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0; color: #ffffff;">🍎 {title}</h1>
                <p style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.7); margin: 0.5rem 0 0 0;">{subtitle}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


class StatsRenderer:
    """Handles statistics rendering - SOLID SRP"""

    @staticmethod
    def render_stats(df: pd.DataFrame):
        """Render enhanced statistics cards"""
        # Initialize session state for selection tracking
        if "selected_objects" not in st.session_state:
            st.session_state.selected_objects = set()
        if "deleted_objects" not in st.session_state:
            st.session_state.deleted_objects = set()

        selected_count = len(st.session_state.selected_objects)
        deleted_count = len(st.session_state.deleted_objects)
        active_count = len(df) - deleted_count

        st.markdown(
            f"""
            <div class="stats-container">
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
                    <div class="stats-button" style="border-left: 4px solid #007bff;">
                        <div class="stats-number">{len(df)}</div>
                        <div class="stats-label">Total</div>
                    </div>
                    <div class="stats-button" style="border-left: 4px solid #28a745;">
                        <div class="stats-number">{selected_count}</div>
                        <div class="stats-label">Selected</div>
                    </div>
                    <div class="stats-button" style="border-left: 4px solid #dc3545;">
                        <div class="stats-number">{deleted_count}</div>
                        <div class="stats-label">Deleted</div>
                    </div>
                    <div class="stats-button" style="border-left: 4px solid #ffc107;">
                        <div class="stats-number">{active_count}</div>
                        <div class="stats-label">Active</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


class DataProcessor:
    """Handles data processing - SOLID SRP"""

    @staticmethod
    def shorten_name(name: str, max_length: int = 40) -> str:
        """Shorten long names for better display"""
        if len(name) <= max_length:
            return name
        return name[: max_length - 3] + "..."


class SortingController:
    """Handles sorting functionality - SOLID SRP"""

    @staticmethod
    def render_sorting_controls(df: pd.DataFrame) -> pd.DataFrame:
        """Render sorting controls and return sorted dataframe"""
        with st.sidebar:
            st.markdown("### 🔧 Controls")
            sort_options = {
                "Name (A-Z)": "Name",
                "Name (Z-A)": "Name_desc",
                "ID (Low-High)": "ID",
                "ID (High-Low)": "ID_desc",
                "Type": "Type",
            }
            sort_by = st.selectbox("Sort by:", list(sort_options.keys()), index=0)

            # Apply sorting with column existence checks
            if sort_by == "Name (A-Z)":
                if "Name" in df.columns:
                    df = df.sort_values("Name")
                elif "name" in df.columns:
                    df = df.sort_values("name")
            elif sort_by == "Name (Z-A)":
                if "Name" in df.columns:
                    df = df.sort_values("Name", ascending=False)
                elif "name" in df.columns:
                    df = df.sort_values("name", ascending=False)
            elif sort_by == "ID (Low-High)":
                if "ID" in df.columns:
                    df = df.sort_values("ID")
                elif "id" in df.columns:
                    df = df.sort_values("id")
            elif sort_by == "ID (High-Low)":
                if "ID" in df.columns:
                    df = df.sort_values("ID", ascending=False)
                elif "id" in df.columns:
                    df = df.sort_values("id", ascending=False)
            elif sort_by == "Type":
                if "Type" in df.columns:
                    df = df.sort_values("Type")
                elif "type" in df.columns:
                    df = df.sort_values("type")

        return df


class GridRenderer:
    """Handles grid rendering - SOLID SRP"""

    @staticmethod
    def render_object_grid(df: pd.DataFrame, manager):
        """Render the object grid with selection functionality"""
        st.markdown("### 📋 Objects")
        st.markdown("Use the toggle switches to select objects for deletion")

        # Create 3-column grid for better layout
        cols_per_row = 3
        for i in range(0, len(df), cols_per_row):
            cols = st.columns(cols_per_row)

            for j, col in enumerate(cols):
                if i + j < len(df):
                    row = df.iloc[i + j]
                    object_id = str(row["ID"])
                    object_name = row["ShortName"]
                    full_name = row.get("Name", row.get("name", "Unknown"))
                    object_type = row.get("Type", row.get("type", "Unknown"))
                    is_selected = object_id in st.session_state.selected_objects
                    is_deleted = object_id in st.session_state.deleted_objects

                    with col:
                        # Get search type for color coding based on name patterns
                        search_name = row.get("Name", row.get("name", "")).lower()
                        search_type = row.get(
                            "Type", row.get("type", "Unknown")
                        ).lower()

                        # Determine color based on search name patterns
                        if any(
                            keyword in search_name
                            for keyword in [
                                "mac",
                                "macbook",
                                "computer",
                                "laptop",
                                "desktop",
                                "imac",
                            ]
                        ):
                            type_color = "#007bff"  # Blue for computer
                        elif any(
                            keyword in search_name
                            for keyword in [
                                "iphone",
                                "ipad",
                                "mobile",
                                "device",
                                "ios",
                                "android",
                            ]
                        ):
                            type_color = "#28a745"  # Green for mobile
                        elif any(
                            keyword in search_name
                            for keyword in [
                                "user",
                                "people",
                                "person",
                                "staff",
                                "employee",
                            ]
                        ):
                            type_color = "#ffc107"  # Yellow for user
                        else:
                            type_color = "#6c757d"  # Gray for unknown

                        # Card styling
                        card_class = "object-card"
                        if is_deleted:
                            card_class += " deleted"
                        elif is_selected:
                            card_class += " selected"

                        # Status badge
                        if is_deleted:
                            status_badge = '<span class="status-badge status-deleted">🗑️ Deleted</span>'
                        elif is_selected:
                            status_badge = '<span class="status-badge status-selected">⚠️ Selected</span>'
                        else:
                            status_badge = '<span class="status-badge status-active">✅ Active</span>'

                        # Render card content with color coding
                        st.markdown(
                            f"""
                            <div class="{card_class}" title="{full_name}" style="border-left: 4px solid {type_color};">
                                <div>
                                    <div class="object-title">{object_name}</div>
                                    <div class="object-details">ID: {object_id} • {object_type}</div>
                                    {status_badge}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Selection button
                        button_text = "✓" if is_selected else "○"
                        button_type = "primary" if is_selected else "secondary"

                        if st.button(
                            button_text,
                            key=f"select_{object_id}",
                            help=f"Toggle selection for {full_name}",
                            type=button_type,
                            use_container_width=True,
                        ):
                            if is_selected:
                                st.session_state.selected_objects.discard(object_id)
                            else:
                                st.session_state.selected_objects.add(object_id)
                            st.rerun()


class ActionController:
    """Handles action buttons - SOLID SRP"""

    @staticmethod
    def render_action_buttons():
        """Render action buttons"""
        st.markdown("---")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            if st.button(
                "🗑️ Delete Selected",
                type="primary",
                use_container_width=True,
                key="delete_selected_btn",
            ):
                if st.session_state.selected_objects:
                    st.session_state.deleted_objects.update(
                        st.session_state.selected_objects
                    )
                    st.session_state.selected_objects.clear()
                    st.rerun()
                else:
                    st.warning("No items selected")

        with col2:
            if st.button("🔄 Clear All", use_container_width=True, key="clear_all_btn"):
                st.session_state.selected_objects.clear()
                st.session_state.deleted_objects.clear()
                st.rerun()

        with col3:
            if st.button(
                "🔄 Refresh Data",
                type="secondary",
                use_container_width=True,
                key="refresh_data_btn",
            ):
                st.rerun()

        with col4:
            # Show count of items marked for deletion
            if st.session_state.deleted_objects:
                st.markdown(
                    f"""
                    <div style="background: rgba(220, 53, 69, 0.1); border: 1px solid #dc3545; border-radius: 8px; padding: 12px; margin: 8px 0;">
                        <strong>⚠️ {len(st.session_state.deleted_objects)} items marked for deletion</strong><br>
                        Use the deletion interface below to confirm.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Status info
        st.info(
            f"**{len(st.session_state.selected_objects)}** selected • **{len(st.session_state.deleted_objects)}** deleted"
        )


class DashboardUI:
    """Main Dashboard UI Coordinator - SOLID SRP compliance"""

    def __init__(self):
        self.css_renderer = CSSRenderer()
        self.header_renderer = HeaderRenderer()
        self.stats_renderer = StatsRenderer()
        self.data_processor = DataProcessor()
        self.sorting_controller = SortingController()
        self.grid_renderer = GridRenderer()
        self.action_controller = ActionController()

    def render_custom_css(self):
        """Render custom CSS"""
        self.css_renderer.render_custom_css()

    def render_header(self, title: str, subtitle: str):
        """Render dashboard header"""
        self.header_renderer.render_header(title, subtitle)

    def render_stats(self, df: pd.DataFrame):
        """Render statistics"""
        self.stats_renderer.render_stats(df)

    def render_selection_interface(self, df: pd.DataFrame, manager) -> List[str]:
        """Render enhanced grid-based selection interface"""
        # Apply sorting
        df = self.sorting_controller.render_sorting_controls(df)

        # Add shortened names
        name_col = "Name" if "Name" in df.columns else "name"
        df["ShortName"] = df[name_col].apply(self.data_processor.shorten_name)

        # Render grid
        self.grid_renderer.render_object_grid(df, manager)

        # Render action buttons
        self.action_controller.render_action_buttons()

        # Return selected items for compatibility
        selected_items = []
        for object_id in st.session_state.selected_objects:
            try:
                row = df[df["ID"] == int(object_id)].iloc[0]
                selected_items.append(manager.get_display_name(row))
            except (IndexError, ValueError):
                continue

        return selected_items

    @staticmethod
    def _perform_real_deletion(deleted_object_ids: set):
        """Perform real deletion of objects from JAMF Pro"""
        if not deleted_object_ids:
            return

        # Create progress container
        progress_container = st.container()
        status_container = st.container()

        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

        with status_container:
            deleted_count = 0
            failed_count = 0
            results = []

            # Get the current dataframe to find object details
            try:
                import sys

                sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
                from dashboard.providers import CSVDataProvider
                from dashboard.managers import AdvancedSearchManager
                from dashboard.providers import JAMFAuthProvider

                # Create manager for deletion
                data_provider = CSVDataProvider()
                auth_provider = JAMFAuthProvider()
                manager = AdvancedSearchManager(data_provider, auth_provider)

                # Load current data
                df = manager.load_data()

                # Process each deleted object
                for i, object_id in enumerate(deleted_object_ids, 1):
                    try:
                        # Find the object in the dataframe
                        object_row = df[df["ID"] == int(object_id)]
                        if object_row.empty:
                            failed_count += 1
                            results.append(f"❌ Object ID {object_id} not found")
                            continue

                        object_name = object_row.iloc[0].get(
                            "Name", object_row.iloc[0].get("name", "Unknown")
                        )
                        object_type = manager.get_object_type(int(object_id), df)

                        # Update progress
                        progress = i / len(deleted_object_ids)
                        progress_bar.progress(progress)
                        status_text.text(
                            f"Deleting {object_name}... ({i}/{len(deleted_object_ids)})"
                        )

                        # Perform deletion
                        success, message = manager.delete_object(
                            int(object_id), object_name, object_type
                        )

                        if success:
                            deleted_count += 1
                            results.append(f"✅ {object_name} (ID: {object_id})")
                        else:
                            failed_count += 1
                            results.append(
                                f"❌ {object_name} (ID: {object_id}): {message}"
                            )

                    except Exception as e:
                        failed_count += 1
                        results.append(f"❌ Error deleting ID {object_id}: {str(e)}")

                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()

                # Store results in session state
                st.session_state.deletion_results = results
                st.session_state.deleted_objects.clear()  # Clear after deletion

                # Show results
                if deleted_count > 0:
                    st.markdown(
                        f"""
                        <div class="success-box">
                            <strong>✅ Deletion Complete!</strong><br>
                            Successfully deleted: {deleted_count} objects<br>
                            Failed: {failed_count} objects
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Refresh data from JAMF Pro
                    with st.spinner("Refreshing data..."):
                        success, message = manager.refresh_data()
                        if success:
                            st.success("Data refreshed successfully")
                            st.balloons()
                        else:
                            st.warning("Deletion successful but refresh failed")

                    # Force rerun to show updated data and scroll to top
                    st.rerun()
                    # Add JavaScript to scroll to top
                    st.markdown(
                        """
                        <script>
                        window.parent.scrollTo(0, 0);
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <div class="error-box">
                            <strong>Deletion Failed!</strong><br>
                            No objects were successfully deleted.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            except Exception as e:
                st.error(f"Error during deletion process: {str(e)}")

    def render_deletion_interface(self, df: pd.DataFrame, manager):
        """Render streamlined deletion interface"""
        # Check if there are items marked for deletion
        if not st.session_state.get("deleted_objects", set()):
            return

        deleted_objects = st.session_state.deleted_objects
        st.markdown("---")
        st.markdown("### 🗑️ Deletion Confirmation")

        # Show items marked for deletion
        st.markdown(f"**{len(deleted_objects)} items marked for deletion:**")

        # Get the actual object names from the dataframe
        for object_id in deleted_objects:
            object_row = df[df["ID"] == int(object_id)]
            if not object_row.empty:
                object_name = object_row.iloc[0].get(
                    "Name", object_row.iloc[0].get("name", "Unknown")
                )
                st.write(f"• {object_name} (ID: {object_id})")

        # Warning message
        st.markdown(
            """
        <div class="warning-box">
            <strong>⚠️ WARNING: This will permanently delete the selected items from JAMF Pro!</strong><br>
            This action cannot be undone. Make sure you have backups if needed.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Single confirmation with two buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "🗑️ DELETE FROM JAMF PRO",
                type="primary",
                use_container_width=True,
                key="delete_confirm_btn",
            ):
                self._perform_deletion(deleted_objects, df, manager)

        with col2:
            if st.button(
                "❌ CANCEL",
                type="secondary",
                use_container_width=True,
                key="delete_cancel_btn",
            ):
                st.session_state.selected_objects.clear()
                st.session_state.deleted_objects.clear()
                st.rerun()

    def _perform_deletion(self, deleted_object_ids: set, df: pd.DataFrame, manager):
        """Perform the actual deletion"""
        # Create progress container
        progress_container = st.container()
        status_container = st.container()

        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

        with status_container:
            deleted_count = 0
            failed_count = 0
            results = []

            # Process each deleted object
            for i, object_id in enumerate(deleted_object_ids, 1):
                try:
                    # Find the object in the dataframe
                    object_row = df[df["ID"] == int(object_id)]
                    if object_row.empty:
                        failed_count += 1
                        results.append(f"❌ Object ID {object_id} not found")
                        continue

                    object_name = object_row.iloc[0].get(
                        "Name", object_row.iloc[0].get("name", "Unknown")
                    )
                    object_type = manager.get_object_type(int(object_id), df)

                    # Update progress
                    progress = i / len(deleted_object_ids)
                    progress_bar.progress(progress)
                    status_text.text(
                        f"Deleting {object_name}... ({i}/{len(deleted_object_ids)})"
                    )

                    # Perform deletion
                    success, message = manager.delete_object(
                        int(object_id), object_name, object_type
                    )

                    if success:
                        deleted_count += 1
                        results.append(f"✅ {object_name} (ID: {object_id})")
                    else:
                        failed_count += 1
                        results.append(f"❌ {object_name} (ID: {object_id}): {message}")

                except Exception as e:
                    failed_count += 1
                    results.append(f"❌ Error deleting ID {object_id}: {str(e)}")

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            # Store results in session state
            st.session_state.deletion_results = results
            st.session_state.deleted_objects.clear()  # Clear after deletion

            # Show results
            if deleted_count > 0:
                st.markdown(
                    f"""
                    <div class="success-box">
                        <strong>✅ Deletion Complete!</strong><br>
                        Successfully deleted: {deleted_count} objects<br>
                        Failed: {failed_count} objects
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Refresh data from JAMF Pro
                with st.spinner("Refreshing data..."):
                    success, message = manager.refresh_data()
                    if success:
                        st.success("Data refreshed successfully")
                        st.balloons()
                    else:
                        st.warning("Deletion successful but refresh failed")

                # Force rerun to show updated data and scroll to top
                st.rerun()
                # Add JavaScript to scroll to top
                st.markdown(
                    """
                    <script>
                    window.parent.scrollTo(0, 0);
                    </script>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="error-box">
                        <strong>Deletion Failed!</strong><br>
                        No objects were successfully deleted.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
