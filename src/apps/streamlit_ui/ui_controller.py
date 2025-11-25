#!/usr/bin/env python3
"""
UI Controller Implementation - SOLID Principles
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure local directory is first in path
_current_dir = Path(__file__).parent
_project_src = _current_dir.parent.parent
for p in [str(_current_dir), str(_project_src)]:
    while p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(_current_dir))
sys.path.insert(1, str(_project_src))

# Explicitly load local interfaces to avoid conflicts with project-level interfaces
import importlib.util
import os

_interfaces_path = os.path.join(str(_current_dir), "interfaces.py")
_spec = importlib.util.spec_from_file_location("streamlit_interfaces", _interfaces_path)
_interfaces = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_interfaces)
UIController = _interfaces.UIController
DataLoader = _interfaces.DataLoader
DataExporter = _interfaces.DataExporter
ObjectSelector = _interfaces.ObjectSelector
ObjectDeleter = _interfaces.ObjectDeleter
NotificationManager = _interfaces.NotificationManager

from ui_utils import normalize_environment


class JPAPIManagerController(UIController):
    """Main UI Controller for JPAPI Manager"""

    def __init__(
        self,
        data_loader: DataLoader,
        data_exporter: DataExporter,
        object_selector: ObjectSelector,
        object_deleter: ObjectDeleter,
        notification_manager: NotificationManager,
    ):
        self.data_loader = data_loader
        self.data_exporter = data_exporter
        self.object_selector = object_selector
        self.object_deleter = object_deleter
        self.notification_manager = notification_manager

        # Initialize session state
        self._initialize_session_state()

        # Inject Apple-like SVG sprite/styles once per session
        self._inject_svg_sprite_once()

    def _initialize_session_state(self):
        """Initialize session state variables"""
        if "current_environment" not in st.session_state:
            st.session_state.current_environment = "sandbox"
        if "current_object_type" not in st.session_state:
            st.session_state.current_object_type = "searches"
        # Don't initialize show_delete_confirmation - let it persist
        if "show_selected_only" not in st.session_state:
            st.session_state.show_selected_only = False
        if "deleted_count" not in st.session_state:
            st.session_state.deleted_count = 0
        if "deleted_objects_history" not in st.session_state:
            st.session_state.deleted_objects_history = []
        if "show_deleted_review" not in st.session_state:
            st.session_state.show_deleted_review = False
        if "name_filter" not in st.session_state:
            st.session_state.name_filter = ""
        if "sort_by" not in st.session_state:
            st.session_state.sort_by = "Name"
        if "sort_ascending" not in st.session_state:
            st.session_state.sort_ascending = True

    def render_header(self) -> None:
        """Render the application header"""
        # Map environment names to display names
        env_display = {"sandbox": "sbox", "production": "prod"}.get(
            st.session_state.current_environment, st.session_state.current_environment
        )

        object_type_display = (
            str(st.session_state.current_object_type).title()
            if st.session_state.get("current_object_type")
            else "N/A"
        )

        st.markdown(
            """
        <div class="elegant-header">
            <div class="header-content">
                <div class="header-main" style="display:flex; flex-direction:column; gap:8px;">
                    <h1 class="header-title" style="font-size:32px; font-weight:700; margin:0; text-align:left;">jpapi manager</h1>
                    <div class="header-subtitle">
                        <span class="label">env:</span>
                        <span class="value">{environment}</span>
                        <span class="bullet">•</span>
                        <span class="value">{server_name}</span>
                        <a href="{server_url}" target="_blank" class="url-link">(url)</a>
                        <span class="bullet">•</span>
                        <span class="label">obj:</span>
                        <span class="value">{object_type}</span>
                    </div>
                </div>
            </div>
        </div>
        """.format(
                environment=env_display,
                server_name=os.environ.get("JPAPI_SERVER_NAME", "jamf-server"),
                server_url=os.environ.get("JPAPI_SERVER_URL", "#"),
                object_type=object_type_display,
            ),
            unsafe_allow_html=True,
        )

    def render_data_grid(self, data: pd.DataFrame) -> None:
        """Render the data grid"""
        if data.empty:
            st.warning("No data available")
            return

        # Apply name filter if set
        original_count = len(data)
        if st.session_state.get("name_filter", "").strip():
            name_filter = st.session_state.name_filter.strip()
            data = data[
                data["Name"].astype(str).str.contains(name_filter, case=False, na=False)
            ]

        # Apply sorting
        if st.session_state.get("sort_by", "Name") in data.columns:
            data = data.sort_values(
                by=st.session_state.sort_by,
                ascending=st.session_state.get("sort_ascending", True),
            )

        # Add range select mode toggle
        col_info, col_toggle = st.columns([3, 1])
        with col_info:
            # Show filter info if active
            if st.session_state.get("name_filter", "").strip():
                st.info(
                    f"🔍 Filtered: {len(data)} of {original_count} objects match '{st.session_state.name_filter}'"
                )
            # Filter to show only selected items if requested
            elif st.session_state.get("show_selected_only", False):
                selected_objects = self.object_selector.get_selected_objects()
                if selected_objects:
                    # Filter data to show only selected objects
                    data = data[
                        data["ID"]
                        .apply(self._extract_id_from_hyperlink)
                        .isin(selected_objects)
                    ]
                    st.info(f"Showing {len(data)} selected objects")
                else:
                    st.info("No objects selected")
                    return

        with col_toggle:
            # Range select mode toggle
            if st.checkbox(
                "Range Select",
                key="range_select_checkbox",
                help="Enable to select multiple items in sequence",
            ):
                st.session_state.shift_select_mode = True
            else:
                st.session_state.shift_select_mode = False

        # Render object cards
        cols = st.columns(3)
        for idx, row in data.iterrows():
            with cols[idx % 3]:
                self._render_object_card(row)

    def _render_object_card(self, row: pd.Series) -> None:
        """Render object card with properly styled Streamlit button"""
        object_id = self._extract_id_from_hyperlink(row["ID"])
        is_selected = self.object_selector.is_selected(object_id)

        name = str(row["Name"])
        id_html = self._convert_excel_hyperlink_to_html(row["ID"])
        obj_type = str(row.get("Type", "N/A"))

        # Container with card styling and button positioning
        st.markdown(
            f"""
<style>
    /* Card container for object {object_id} */
    .card-container-{object_id} {{
        background: linear-gradient(135deg, #001428 0%, #00194d 100%);
        border: 2px solid {'#ffc107' if is_selected else '#334977'};
        border-radius: 12px;
        padding: 16px;
        position: relative;
        min-height: 100px;
        margin-bottom: 0.5rem;
        box-shadow: {'0 0 20px rgba(255, 193, 7, 0.3)' if is_selected else 'none'};
        transition: all 0.3s ease;
    }}
    
    .card-container-{object_id}:hover {{
        border-color: {'#ffb300' if is_selected else '#3393ff'};
        transform: translateY(-2px);
    }}
    
    /* Selected card title in yellow */
    .card-container-{object_id} .card-title {{
        color: {'#ffc107' if is_selected else '#ffffff'} !important;
        font-weight: {'700' if is_selected else '600'} !important;
    }}
    
    /* Position the button wrapper absolutely within the card */
    .button-wrapper-{object_id} {{
        position: absolute;
        top: 12px;
        right: 12px;
        z-index: 10;
    }}
    
    /* Style the Streamlit button itself as circular yellow button */
    .button-wrapper-{object_id} button[data-testid="baseButton-secondary"] {{
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        min-height: 32px !important;
        max-width: 32px !important;
        max-height: 32px !important;
        border-radius: 50% !important;
        border: 2.5px solid {'#ffc107' if is_selected else '#334977'} !important;
        background: {'linear-gradient(135deg, #ffc107 0%, #ffb300 100%)' if is_selected else 'transparent'} !important;
        box-shadow: {'0 0 0 3px rgba(255, 193, 7, 0.25)' if is_selected else 'none'} !important;
        padding: 0 !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    /* Hover effects */
    .button-wrapper-{object_id} button[data-testid="baseButton-secondary"]:hover {{
        border-color: #ffc107 !important;
        transform: scale(1.15) !important;
        background: {'linear-gradient(135deg, #ffb300 0%, #ffc107 100%)' if is_selected else 'rgba(255, 193, 7, 0.15)'} !important;
        box-shadow: {'0 0 0 4px rgba(255, 193, 7, 0.35)' if is_selected else 'none'} !important;
    }}
    
    /* Style the button text/icon */
    .button-wrapper-{object_id} button p {{
        margin: 0 !important;
        padding: 0 !important;
        font-size: 16px !important;
        font-weight: bold !important;
        line-height: 1 !important;
        color: {'#000000' if is_selected else '#ffffff'} !important;
    }}
    
    /* Hide the button wrapper container's default styling */
    .button-wrapper-{object_id} [data-testid="stButton"] {{
        position: static !important;
        width: 32px !important;
        height: 32px !important;
    }}
</style>
<div class="card-container-{object_id}">
    <div class="card-title" style="font-size:16px; margin-bottom:8px; padding-right:40px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
        {name}
    </div>
    <div style="font-size:13px; color:#8b9dc3;">
        ID: {id_html} • {obj_type}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # Position button absolutely in the top-right corner
        st.markdown(f'<div class="button-wrapper-{object_id}">', unsafe_allow_html=True)

        # The actual clickable button with shift-click support
        if st.button(
            "✓" if is_selected else "○",
            key=f"select_{object_id}",
            type="secondary",
        ):
            # Check if shift-click range selection is active
            if st.session_state.get(
                "shift_select_mode", False
            ) and st.session_state.get("last_selected_id"):
                # Get all object IDs from current data
                data = st.session_state.get("data", pd.DataFrame())
                if not data.empty:
                    all_ids = [
                        self._extract_id_from_hyperlink(row["ID"])
                        for _, row in data.iterrows()
                    ]

                    last_id = st.session_state.last_selected_id
                    if last_id in all_ids and object_id in all_ids:
                        # Select range between last_id and object_id
                        start_idx = all_ids.index(last_id)
                        end_idx = all_ids.index(object_id)

                        # Ensure start is before end
                        if start_idx > end_idx:
                            start_idx, end_idx = end_idx, start_idx

                        # Select all items in range
                        for idx in range(start_idx, end_idx + 1):
                            self.object_selector.select_object(all_ids[idx])

                    st.session_state.shift_select_mode = False
            else:
                # Normal toggle
                self.object_selector.toggle_selection(object_id)

            # Remember last selected for range selection
            st.session_state.last_selected_id = object_id
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    def render_fab(self) -> None:
        """Render the floating action button"""
        # Inject SVG sprite
        self._inject_svg_sprite_once()

        total_count = len(st.session_state.get("data", pd.DataFrame()))
        selected_count = len(self.object_selector.get_selected_objects())
        deleted_count = st.session_state.get("deleted_count", 0)

        # Format counts for display (abbreviate large numbers)
        def format_count(count):
            if count >= 1000:
                return f"{count/1000:.1f}K".replace(".0K", "K")
            return str(count)

        total_display = format_count(total_count)
        selected_display = format_count(selected_count)
        deleted_display = format_count(deleted_count)

        # Add click handler to close FAB when clicking elsewhere
        if st.session_state.get("fab_clicked_outside", False):
            st.session_state.fab_clicked_outside = False
            # This will close the popover

        # Inject custom HTML content for FAB button with 3 SF Symbols - HORIZONTAL LAYOUT
        # Icons are dimmed (opacity 0.4) to create shadow effect
        st.markdown(
            f"""
            <style>
                .stPopover > div:first-child button {{
                    color: #ffffff !important;
                    font-size: 0 !important; /* Hide default text */
                }}
                
                .stPopover > div:first-child button p {{
                    font-size: 0 !important; /* Hide default text */
                    height: 0 !important;
                    line-height: 0 !important;
                }}
                
                /* Inject custom HTML content with 3 SF Symbols - HORIZONTAL LAYOUT */
                .stPopover > div:first-child button::after {{
                    content: '' !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    flex-direction: row !important;
                    gap: 0px !important;
                    font-size: 24px !important;
                    font-weight: 700 !important;
                    color: #ffffff !important;
                    line-height: 1 !important;
                    background-image: url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="280" height="50" viewBox="0 0 280 50"%3E%3C!-- Icon 1: Number Circle (Large) --%3E%3Cg transform="translate(12, 6) scale(1.5)" opacity="0.35"%3E%3Cpath d="M12.7148 25.4395C19.7363 25.4395 25.4395 19.7461 25.4395 12.7246C25.4395 5.70312 19.7363 0 12.7148 0C5.69336 0 0 5.70312 0 12.7246C0 19.7461 5.69336 25.4395 12.7148 25.4395ZM12.7148 23.623C6.68945 23.623 1.81641 18.75 1.81641 12.7246C1.81641 6.69922 6.68945 1.82617 12.7148 1.82617C18.7402 1.82617 23.6133 6.69922 23.6133 12.7246C23.6133 18.75 18.7402 23.623 12.7148 23.623Z" fill="%23ffd60a"/%3E%3Cpath d="M9.54102 18.7402C9.9707 18.7402 10.2344 18.5254 10.3223 18.1055L10.9082 15.3223L13.3691 15.3223L12.8223 17.9102C12.7246 18.3594 13.0469 18.7402 13.4961 18.7402C13.9453 18.7402 14.2188 18.5254 14.3066 18.1055L14.8926 15.3125L16.2695 15.3125C16.6992 15.3125 17.002 14.9902 17.002 14.5703C17.002 14.1992 16.748 13.9258 16.377 13.9258L15.1855 13.9258L15.7617 11.25L17.168 11.25C17.5977 11.25 17.9004 10.9375 17.9004 10.5176C17.9004 10.1367 17.6367 9.87305 17.2656 9.87305L16.0449 9.87305L16.5625 7.40234C16.6504 6.94336 16.3184 6.57227 15.8691 6.57227C15.4297 6.57227 15.166 6.78711 15.0781 7.19727L14.5117 9.87305L12.0508 9.87305L12.5684 7.40234C12.666 6.95312 12.3535 6.57227 11.8848 6.57227C11.4551 6.57227 11.1816 6.78711 11.0938 7.19727L10.5371 9.87305L9.13086 9.87305C8.70117 9.87305 8.39844 10.1855 8.39844 10.6055C8.39844 10.9766 8.65234 11.25 9.02344 11.25L10.2344 11.25L9.6875 13.9258L8.23242 13.9258C7.80273 13.9258 7.5 14.248 7.5 14.668C7.5 15.0391 7.76367 15.3125 8.13477 15.3125L9.38477 15.3125L8.84766 17.9102C8.75977 18.3594 9.0918 18.7402 9.54102 18.7402ZM11.123 14.043L11.7188 11.1523L14.3262 11.1523L13.7207 14.043Z" fill="white"/%3E%3C/g%3E%3C!-- Count 1 --%3E%3Ctext x="56" y="33" fill="%23ffffff" stroke="%23000000" stroke-width="2.5" paint-order="stroke" font-size="22" font-weight="900" font-family="system-ui, -apple-system" text-anchor="middle"%3E{total_display}%3C/text%3E%3C!-- Icon 2: Percent Circle --%3E%3Cg transform="translate(108, 6) scale(1.7)" opacity="0.35"%3E%3Cpath d="M25.4395 12.7246C25.4395 19.7461 19.7363 25.4395 12.7148 25.4395C5.69336 25.4395 0 19.7461 0 12.7246C0 5.70312 5.69336 0 12.7148 0C19.7363 0 25.4395 5.70312 25.4395 12.7246ZM1.81641 12.7246C1.81641 18.75 6.68945 23.623 12.7148 23.623C18.7402 23.623 23.6133 18.75 23.6133 12.7246C23.6133 6.69922 18.7402 1.82617 12.7148 1.82617C6.68945 1.82617 1.81641 6.69922 1.81641 12.7246Z" fill="%23ffd60a"/%3E%3Cpath d="M20.7031 15.6445C20.4395 16.4551 19.5215 16.6113 18.1055 16.0938L13.5575 14.4368L15.9942 13.1409ZM10.1953 9.29688C10.1953 9.84375 10.1758 10.0488 10.5273 10.2344L11.8906 10.9592C11.5614 11.2149 11.331 11.5398 11.1711 11.9527C11.1385 11.934 11.1027 11.9146 11.0645 11.8945L9.93164 11.2793C9.80469 11.2109 9.72656 11.2012 9.61914 11.2012C9.14062 11.2012 8.89648 11.6992 7.7832 11.6992C6.43555 11.6992 5.37109 10.6348 5.37109 9.29688C5.37109 7.94922 6.43555 6.875 7.7832 6.875C9.11133 6.875 10.1953 7.93945 10.1953 9.29688ZM6.2793 9.29688C6.2793 10.1367 6.95312 10.8008 7.7832 10.8008C8.61328 10.8008 9.28711 10.1367 9.28711 9.29688C9.28711 8.45703 8.61328 7.7832 7.7832 7.7832C6.95312 7.7832 6.2793 8.45703 6.2793 9.29688Z" fill="white"/%3E%3Cpath d="M7.7832 18.5742C9.11133 18.5742 10.1953 17.5 10.1953 16.1426C10.1953 15.5957 10.1758 15.4004 10.5273 15.2051L20.7031 9.79492C20.4395 8.99414 19.5215 8.82812 18.1055 9.3457L12.959 11.2207C12.2656 11.4746 11.9531 11.8164 11.7773 12.4609L11.6602 12.9004C11.5918 13.1934 11.4746 13.3301 11.0645 13.5547L9.93164 14.1602C9.80469 14.2188 9.72656 14.248 9.61914 14.248C9.14062 14.248 8.89648 13.7402 7.7832 13.7402C6.43555 13.7402 5.37109 14.8047 5.37109 16.1426C5.37109 17.4902 6.43555 18.5742 7.7832 18.5742ZM7.7832 17.666C6.95312 17.666 6.2793 16.9922 6.2793 16.1426C6.2793 15.3125 6.95312 14.6387 7.7832 14.6387C8.61328 14.6387 9.28711 15.3125 9.28711 16.1426C9.28711 16.9922 8.61328 17.666 7.7832 17.666ZM13.0762 12.8711C12.8516 12.8711 12.6367 12.666 12.6367 12.4316C12.6367 12.1777 12.8418 11.9824 13.0762 11.9824C13.3301 11.9824 13.5352 12.1777 13.5352 12.4316C13.5352 12.6758 13.3301 12.8711 13.0762 12.8711Z" fill="white"/%3E%3C/g%3E%3C!-- Count 2 --%3E%3Ctext x="149" y="33" fill="%23ffffff" stroke="%23000000" stroke-width="2.5" paint-order="stroke" font-size="22" font-weight="900" font-family="system-ui, -apple-system" text-anchor="middle"%3E{selected_display}%3C/text%3E%3C!-- Icon 3: Trash Circle --%3E%3Cg transform="translate(201, 6) scale(1.7)" opacity="0.35"%3E%3Cpath d="M12.7148 25.459C19.7266 25.459 25.4395 19.7461 25.4395 12.7344C25.4395 5.73242 19.7266 0.0195312 12.7148 0.0195312C5.71289 0.0195312 0 5.73242 0 12.7344C0 19.7461 5.71289 25.459 12.7148 25.459Z" fill="%23ff453a"/%3E%3Cpath d="M9.14062 19.8145C7.8418 19.8145 7.29492 19.1211 7.10938 17.8223L6.16211 11.3574L19.2676 11.3574L18.3301 17.8223C18.1348 19.1113 17.5879 19.8145 16.2891 19.8145ZM10.7129 17.9102C10.8594 17.9102 10.9863 17.8516 11.0742 17.7637L12.7051 16.123L14.3555 17.7637C14.4434 17.8418 14.5605 17.9102 14.7168 17.9102C14.9805 17.9102 15.2246 17.666 15.2246 17.4023C15.2246 17.2559 15.1562 17.1387 15.0781 17.041L13.4473 15.4004L15.0781 13.7598C15.1855 13.6426 15.2344 13.5352 15.2344 13.3984C15.2344 13.1055 15.0098 12.8906 14.7168 12.8906C14.5703 12.8906 14.4629 12.9492 14.3652 13.0469L12.7051 14.6777L11.0645 13.0469C10.9766 12.9492 10.8594 12.9004 10.7129 12.9004C10.4297 12.9004 10.2051 13.125 10.2051 13.3984C10.2051 13.5449 10.2637 13.6621 10.3613 13.7598L11.9824 15.4004L10.3613 17.041C10.2637 17.1387 10.2051 17.2559 10.2051 17.4023C10.2051 17.666 10.4297 17.9102 10.7129 17.9102ZM5.67383 10.3906C4.93164 10.3906 4.55078 9.94141 4.55078 9.22852L4.55078 8.47656C4.55078 7.74414 4.96094 7.30469 5.67383 7.30469L19.7656 7.30469C20.498 7.30469 20.8887 7.74414 20.8887 8.47656L20.8887 9.22852C20.8887 9.94141 20.498 10.3906 19.7656 10.3906Z" fill="white"/%3E%3C/g%3E%3C!-- Count 3 --%3E%3Ctext x="242" y="33" fill="%23ffffff" stroke="%23000000" stroke-width="2.5" paint-order="stroke" font-size="22" font-weight="900" font-family="system-ui, -apple-system" text-anchor="middle"%3E{deleted_display}%3C/text%3E%3C/svg%3E') !important;
                    background-size: contain !important;
                    background-repeat: no-repeat !important;
                    background-position: center !important;
                    width: 100% !important;
                    height: 50px !important;
                    min-height: 50px !important;
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Create the clickable FAB stats card using st.popover
        with st.popover(
            "Stats",  # Placeholder text (will be hidden by CSS)
            use_container_width=False,
        ):
            # Add close button at the top
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("✕", key="fab_close", help="Close FAB menu"):
                    st.rerun()
            with col2:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 25.8008 25.459" style="vertical-align: middle;">
                            <path d="M12.7148 25.4395C19.7363 25.4395 25.4395 19.7461 25.4395 12.7246C25.4395 5.70312 19.7363 0 12.7148 0C5.69336 0 0 5.70312 0 12.7246C0 19.7461 5.69336 25.4395 12.7148 25.4395ZM12.7148 23.623C6.68945 23.623 1.81641 18.75 1.81641 12.7246C1.81641 6.69922 6.68945 1.82617 12.7148 1.82617C18.7402 1.82617 23.6133 6.69922 23.6133 12.7246C23.6133 18.75 18.7402 23.623 12.7148 23.623Z" fill="white"/>
                            <path d="M7.14844 13.6328C7.14844 13.9258 7.38281 14.1309 7.67578 14.1309L12.0215 14.1309L9.69727 20.4004C9.4043 21.1523 10.2051 21.5527 10.6934 20.957L17.7246 12.1289C17.8516 11.9727 17.9199 11.8066 17.9199 11.6602C17.9199 11.3672 17.6855 11.1719 17.3926 11.1719L13.0469 11.1719L15.3711 4.90234C15.6641 4.15039 14.8633 3.74023 14.375 4.3457L7.34375 13.1641C7.2168 13.3301 7.14844 13.4961 7.14844 13.6328Z" fill="#0a84ff"/>
                        </svg>
                        <h3 style="margin: 0; color: white; font-size: 20px; font-weight: 600;">Actions</h3>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            # Environment and Object Type controls
            col1, col2 = st.columns(2)
            with col1:
                # Environment selector (no mapping needed now)
                env_options = ["sandbox", "production"]
                current_env_idx = env_options.index(
                    st.session_state.current_environment
                )

                new_env = st.selectbox(
                    "Environment", env_options, index=current_env_idx, key="fab_env"
                )

                if new_env != st.session_state.current_environment:
                    st.session_state.current_environment = new_env
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.rerun()

            with col2:
                types = ["searches", "policies", "profiles", "packages", "groups"]
                current_type_idx = types.index(st.session_state.current_object_type)
                new_type = st.selectbox(
                    "Object Type", types, index=current_type_idx, key="fab_type"
                )
                if new_type != st.session_state.current_object_type:
                    st.session_state.current_object_type = new_type
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.rerun()

            st.divider()

            # Filter section with magnifying glass icon
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 35.9668 28.6426" style="vertical-align: middle;">
                        <path d="M4.74609 20.0381L4.74609 21.9434C4.74609 23.3496 5.48828 24.0723 6.8457 24.0723L18.0613 24.0723L19.7877 25.8008L6.81641 25.8008C4.29688 25.8008 3.00781 24.541 3.00781 22.041L3.00781 18.6961C3.52945 19.2107 4.11156 19.6632 4.74609 20.0381ZM32.5977 6.61133L32.5977 22.041C32.5977 24.5215 31.3281 25.8008 28.7988 25.8008L26.688 25.8008C26.6894 25.7913 26.6895 25.7814 26.6895 25.7715C26.6895 25.1464 26.4843 24.5534 26.1285 24.0723L28.7598 24.0723C30.0977 24.0723 30.8691 23.3496 30.8691 21.9434L30.8691 6.69922C30.8691 5.30273 30.0977 4.57031 28.7598 4.57031L16.7965 4.57031C16.0954 3.8774 15.289 3.29148 14.4014 2.8418L28.7988 2.8418C31.3281 2.8418 32.5977 4.12109 32.5977 6.61133Z" fill="white"/>
                        <path d="M9.88281 21.4941C15.332 21.4941 19.7656 17.0605 19.7656 11.6113C19.7656 6.17188 15.332 1.73828 9.88281 1.73828C4.43359 1.73828 0 6.17188 0 11.6113C0 17.0605 4.43359 21.4941 9.88281 21.4941ZM9.88281 19.668C5.43945 19.668 1.83594 16.0547 1.83594 11.6113C1.83594 7.17773 5.43945 3.56445 9.88281 3.56445C14.3262 3.56445 17.9395 7.17773 17.9395 11.6113C17.9395 16.0547 14.3262 19.668 9.88281 19.668ZM16.9727 17.041L15.0684 18.877L22.8906 26.709C23.1543 26.9727 23.4766 27.0898 23.8281 27.0898C24.5996 27.0898 25.127 26.5039 25.127 25.7715C25.127 25.4199 24.9902 25.0879 24.7656 24.8535Z" fill="#0a84ff"/>
                        <path d="M5.71289 10.7422L14.0527 10.7422C14.4824 10.7422 14.8145 10.4004 14.8145 9.98047C14.8145 9.56055 14.4824 9.21875 14.0527 9.21875L5.71289 9.21875C5.27344 9.21875 4.95117 9.56055 4.95117 9.98047C4.95117 10.4004 5.27344 10.7422 5.71289 10.7422ZM5.71289 14.0039L11.8262 14.0039C12.2461 14.0039 12.5879 13.6719 12.5879 13.252C12.5879 12.8223 12.2461 12.4805 11.8262 12.4805L5.71289 12.4805C5.27344 12.4805 4.95117 12.8223 4.95117 13.252C4.95117 13.6719 5.27344 14.0039 5.71289 14.0039Z" fill="#0a84ff"/>
                    </svg>
                    <h3 style="margin: 0; color: white; font-size: 20px; font-weight: 600;">Filters</h3>
                </div>
            """,
                unsafe_allow_html=True,
            )

            # Name filter
            name_filter = st.text_input(
                "Search Name",
                value=st.session_state.name_filter,
                key="fab_name_filter",
                placeholder="Type to filter by name...",
                help="Filter objects by name (case-insensitive)",
            )
            if name_filter != st.session_state.name_filter:
                st.session_state.name_filter = name_filter
                st.rerun()

            # Sort options
            col_sort1, col_sort2 = st.columns([3, 1])
            with col_sort1:
                # Get available columns from data
                data = st.session_state.get("data", pd.DataFrame())
                sort_options = ["Name", "ID"] if not data.empty else list(data.columns)
                if "Name" in sort_options:
                    current_sort_idx = (
                        sort_options.index(st.session_state.sort_by)
                        if st.session_state.sort_by in sort_options
                        else 0
                    )
                    new_sort = st.selectbox(
                        "Sort By",
                        sort_options,
                        index=current_sort_idx,
                        key="fab_sort_by",
                    )
                    if new_sort != st.session_state.sort_by:
                        st.session_state.sort_by = new_sort
                        st.rerun()

            with col_sort2:
                # Sort direction toggle
                sort_icon = "↑" if st.session_state.sort_ascending else "↓"
                if st.button(
                    sort_icon,
                    key="fab_sort_direction",
                    help="Toggle sort direction",
                    use_container_width=True,
                ):
                    st.session_state.sort_ascending = (
                        not st.session_state.sort_ascending
                    )
                    st.rerun()

            # Clear filters button
            if st.session_state.name_filter:
                if st.button(
                    "Clear Filters",
                    key="fab_clear_filters",
                    use_container_width=True,
                    type="secondary",
                ):
                    st.session_state.name_filter = ""
                    st.rerun()

            st.divider()

            # Action buttons
            if st.button("Gather Data", key="fab_gather", use_container_width=True):
                self._handle_gather_data()

            if st.button("Export Selected", key="fab_export", use_container_width=True):
                self._handle_export_selected()

            # Review/Restore deleted objects button
            deleted_history = st.session_state.get("deleted_objects_history", [])
            if deleted_history:
                if st.button(
                    f"📋 Review Deleted ({len(deleted_history)})",
                    key="fab_review_deleted",
                    use_container_width=True,
                    type="secondary",
                ):
                    st.session_state.show_deleted_review = True
                    st.rerun()

            # Selection actions
            if selected_count > 0:
                st.divider()
                st.markdown(
                    '<h3 style="margin: 0 0 16px 0; color: white; font-size: 20px; font-weight: 600;">Selection Actions</h3>',
                    unsafe_allow_html=True,
                )

                st.info(f"{selected_count} items currently selected")

                # Neat selected items preview (name and ID)
                selected_preview = self._get_selected_items_details(limit=6)
                if selected_preview:
                    for item in selected_preview:
                        st.markdown(f"- **{item['name']}**  `ID:{item['id']}`")
                    if selected_count > len(selected_preview):
                        st.markdown(
                            f"… and {selected_count - len(selected_preview)} more"
                        )

                if st.button(
                    "View Selected Items",
                    key="fab_view_selected",
                    use_container_width=True,
                ):
                    st.session_state.show_selected_only = True
                    st.rerun()

                if st.button(
                    "Deselect All",
                    key="fab_deselect_all",
                    use_container_width=True,
                    type="secondary",
                ):
                    self.object_selector.clear_selection()
                    st.success("Deselected all objects")
                    st.rerun()

                if st.button(
                    "Delete Selected",
                    key="fab_delete_selected",
                    use_container_width=True,
                    type="primary",
                ):
                    # Set session state to show delete confirmation
                    selected_objects = self.object_selector.get_selected_objects()
                    if selected_objects:
                        st.session_state.show_delete_confirmation = True
                        st.session_state.delete_object_ids = selected_objects
                        st.rerun()
                    else:
                        st.warning("No objects selected for deletion")
            else:
                st.info("No items selected for deletion")

    def _render_delete_confirmation_direct(self, object_ids: List[str]) -> None:
        """Render delete confirmation - clean dialog with environment info"""

        # Get environment info
        env = st.session_state.current_environment
        env_display = {"sandbox": "Sandbox", "production": "Production"}.get(env, env)
        object_type = st.session_state.current_object_type

        # Center content
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)

            # Warning header with environment
            st.markdown(
                f"""
                <div style="text-align: center; background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                     padding: 24px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #ff4444;">
                    <h2 style="color: white; font-size: 32px; margin: 0;">⚠️ CONFIRM DELETION</h2>
                    <p style="color: white; font-size: 16px; margin: 10px 0 0 0;">This action CANNOT be undone!</p>
                    <div style="margin-top: 15px; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 8px; display: inline-block;">
                        <span style="color: #ffdc2e; font-weight: bold;">Environment:</span>
                        <span style="color: white; font-weight: bold;">{env_display}</span>
                        <span style="margin: 0 8px; color: #fff;">•</span>
                        <span style="color: #ffdc2e; font-weight: bold;">Type:</span>
                        <span style="color: white; font-weight: bold;">{object_type.title()}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Warning message
            st.warning(
                f"**You are about to PERMANENTLY DELETE {len(object_ids)} {object_type}**"
            )

            # Objects list - compact
            st.markdown("**Objects to be deleted:**")

            items = self._get_selected_items_details(ids=object_ids)
            list_html = [
                '<div style="max-height: 200px; overflow-y: auto; background: #0b1b3f; border: 1px solid #2b3e6b; border-radius: 8px; padding: 8px 12px; margin-bottom: 16px;">'
            ]
            for it in items:
                safe_name = str(it["name"]).replace("<", "&lt;").replace(">", "&gt;")
                list_html.append(
                    f'<div style="display:flex; align-items:center; gap:8px; padding:4px 0; border-bottom: 1px dashed #2b3e6b;">'
                    f'<div style="flex:1; min-width:0; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"><strong>{safe_name}</strong></div>'
                    f"<code style=\"color:#b9c4cb; font-size:11px;\">ID:{it['id']}</code>"
                    f"</div>"
                )
            list_html.append("</div>")
            st.markdown("".join(list_html), unsafe_allow_html=True)

            # Action buttons
            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button(
                    "✕ Cancel",
                    key="cancel_delete_direct",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.show_delete_confirmation = False
                    st.session_state.delete_object_ids = []
                    st.rerun()

            with col_btn2:
                if st.button(
                    "🔥 CONFIRM DELETION",
                    key="confirm_delete_direct",
                    type="primary",
                    use_container_width=True,
                ):
                    self._handle_delete_objects(object_ids)

    def render_delete_confirmation(self, object_ids: List[str]) -> None:
        """Render delete confirmation dialog"""
        if not st.session_state.get("show_delete_confirmation", False):
            return

        # Create a full-width container for the delete confirmation
        with st.container():
            st.markdown("---")

            # Destructive warning banner
            st.markdown(
                """
            <div style="background-color: #ff4444; color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                <div style="display:flex; gap:10px; justify-content:center; align-items:center;">
                    <span class="ai" style="color:white"><svg><use href="#ai-warning" /></svg></span>
                    <h2 style="margin:0;">DESTRUCTIVE OPERATION</h2>
                    <span class="ai" style="color:white"><svg><use href="#ai-warning" /></svg></span>
                </div>
                <p style="font-size: 18px; margin: 6px 0 0 0;">This will PERMANENTLY DELETE objects from JAMF Pro</p>
                <p style="font-size: 14px; margin: 10px 0 0 0;">This action CANNOT be undone</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Show objects to be deleted
        st.markdown("### Objects to be DELETED:")
        for obj_id in object_ids:
            st.markdown(
                f"""
            <div style="background-color: #3d2a2a; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #dc3545;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="ai delete"><svg><use href="#ai-trash" /></svg></span>
                    <div>
                        <div style="font-weight: bold; color: #ff6b6b; font-size: 16px;">Object ID: {obj_id}</div>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Confirmation buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Permanently Delete",
                key="confirm_delete",
                type="primary",
                use_container_width=True,
            ):
                self._handle_delete_objects(object_ids)

        with col2:
            if st.button(
                "Cancel",
                key="cancel_delete",
                type="secondary",
                use_container_width=True,
            ):
                st.session_state.show_delete_confirmation = False
                st.rerun()

    def _handle_gather_data(self) -> None:
        """Handle gather data action"""
        try:
            with st.spinner("Gathering data..."):
                # Import here to get better error messages
                from core.config.object_type_manager import ObjectTypeManager
                import subprocess

                object_manager = ObjectTypeManager()
                jpapi_command = object_manager.get_jpapi_command(
                    st.session_state.current_object_type
                )

                # Normalize environment name (dev→sandbox, prod→production)
                normalized_env = normalize_environment(
                    st.session_state.current_environment
                )

                # Split jpapi_command if it contains spaces (e.g., "macos profiles")
                command_parts = jpapi_command.split()

                # Construct command
                cmd = [
                    "python3",
                    "src/jpapi_main.py",
                    "--env",
                    normalized_env,
                    "export",
                    *command_parts,  # Unpack command parts (handles multi-word commands)
                    "--format",
                    "csv",
                ]

                st.info(f"Running: {' '.join(cmd)}")

                # Execute command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd="/Users/charles.hetzel/Documents/cursor/jpapi",
                )

                # DEBUG: Show what happened
                st.write(f"**Return code:** {result.returncode}")
                if result.stdout:
                    with st.expander("Command output"):
                        st.code(result.stdout)
                if result.stderr:
                    with st.expander("Command errors"):
                        st.code(result.stderr)

                if result.returncode == 0:
                    st.success("Data gathered successfully!")
                    # Clear cache (use normalized environment for cache key)
                    cache_key = (
                        f"data_{st.session_state.current_object_type}_{normalized_env}"
                    )
                    st.write(f"**Clearing cache key:** {cache_key}")
                    if cache_key in st.session_state:
                        del st.session_state[cache_key]
                        st.write("✅ Cache cleared")
                    else:
                        st.write("ℹ️ No cache to clear")
                    st.write("🔄 Reloading page...")
                    st.rerun()
                else:
                    # Check if it's an authentication error
                    output = result.stdout if result.stdout else result.stderr
                    if (
                        "Authentication" in output
                        or "401" in output
                        or "credentials" in output.lower()
                    ):
                        st.error(
                            f"Authentication failed for {st.session_state.current_environment}"
                        )
                        st.warning("Your JAMF Pro API credentials may have expired.")
                        st.info("To fix this:")
                        st.markdown(
                            """
                        1. Go to your JAMF Pro instance
                        2. Navigate to **Settings → API Roles and Clients**
                        3. Create a new API client or refresh existing credentials
                        4. Run in terminal: `jpapi setup auth {env}`
                        """.format(
                                env=st.session_state.current_environment
                            )
                        )
                        if output:
                            with st.expander("Full error message"):
                                st.code(output)
                    else:
                        st.error(f"Command failed with code {result.returncode}")
                        if result.stderr:
                            st.error(f"Error output: {result.stderr}")
                        if result.stdout:
                            st.info(f"Output: {result.stdout}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback

            st.error(f"Details: {traceback.format_exc()}")

    def _handle_export_selected(self) -> None:
        """Handle export selected action"""
        selected_objects = self.object_selector.get_selected_objects()
        if selected_objects:
            st.success(f"Exporting {len(selected_objects)} selected items...")
        else:
            st.warning("No items selected for export")

    def _handle_delete_objects(self, object_ids: List[str]) -> None:
        """Handle delete objects action - actually deletes from JAMF Pro using jpapi"""
        try:
            # Track objects being deleted with metadata
            from datetime import datetime

            data_df = st.session_state.get("data", pd.DataFrame())
            for obj_id in object_ids:
                # Find object details from data
                matching_rows = data_df[
                    data_df["ID"].apply(self._extract_id_from_hyperlink) == obj_id
                ]
                if len(matching_rows) > 0:
                    obj_name = str(matching_rows.iloc[0]["Name"])
                    obj_type = st.session_state.current_object_type
                    obj_env = st.session_state.current_environment

                    # Add to deleted history
                    st.session_state.deleted_objects_history.append(
                        {
                            "id": obj_id,
                            "name": obj_name,
                            "type": obj_type,
                            "environment": obj_env,
                            "deleted_at": datetime.now().isoformat(),
                            "can_restore": False,  # For now, restoration is not implemented
                        }
                    )

            deleted_count = len(object_ids)

            # Show progress
            st.markdown("### Deleting objects...")
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Determine object type and command
            object_type = st.session_state.current_object_type
            env = st.session_state.current_environment

            # Normalize environment name (dev→sandbox, prod→production)
            normalized_env = normalize_environment(env)

            # Map object types to jpapi delete bulk arguments (only some support bulk)
            bulk_type_map = {
                "policies": "--policies",
                "profiles": "--profiles",
            }

            # Map object types to jpapi delete commands (for individual deletion)
            individual_type_map = {
                "groups": "group",
                "searches": "search",
                "packages": "package",
                "scripts": "script",
            }

            # Handle individual deletion for types that don't support bulk
            if object_type in individual_type_map:
                import subprocess

                success_count = 0
                failure_count = 0
                total = len(object_ids)
                delete_cmd = individual_type_map[object_type]
                object_label = object_type.rstrip(
                    "s"
                )  # Remove trailing 's' for singular form

                for idx, obj_id in enumerate(object_ids, start=1):
                    status_text.text(
                        f"Deleting {object_label} {obj_id} ({idx}/{total})..."
                    )
                    progress = int(10 + (idx - 1) * (80 / max(total, 1)))
                    progress_bar.progress(min(progress, 95))

                    cmd = [
                        "python3",
                        "src/jpapi_main.py",
                        "--env",
                        normalized_env,
                        "delete",
                        delete_cmd,
                        str(obj_id),
                        "--force",
                    ]

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd="/Users/charles.hetzel/Documents/cursor/jpapi",
                    )

                    if result.returncode == 0:
                        success_count += 1
                    else:
                        failure_count += 1

                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()

                if success_count and not failure_count:
                    st.success(f"Successfully deleted {success_count} {object_type}")
                elif success_count:
                    st.warning(
                        f"Deleted {success_count} {object_type}, {failure_count} failed"
                    )
                else:
                    st.error(f"Failed to delete selected {object_type}")

                current_deleted = st.session_state.get("deleted_count", 0)
                st.session_state.deleted_count = current_deleted + success_count
                self.object_selector.clear_selection()
                st.session_state.show_delete_confirmation = False
                st.session_state.delete_object_ids = []
                for key in list(st.session_state.keys()):
                    if key.startswith("data_"):
                        del st.session_state[key]
                if success_count:
                    import time

                    st.balloons()
                    time.sleep(1)
                    # Auto gather data after deletions
                    self._handle_gather_data()
                st.rerun()
                return

            if object_type in bulk_type_map:
                # Bulk deletion for supported types (policies, profiles)
                import subprocess

                cmd = (
                    [
                        "python3",
                        "src/jpapi_main.py",
                        "--env",
                        normalized_env,
                        "delete",
                        "bulk",
                        bulk_type_map[object_type],
                    ]
                    + object_ids
                    + ["--force"]
                )

                status_text.text(f"Deleting {deleted_count} {object_type}...")
                progress_bar.progress(30)

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd="/Users/charles.hetzel/Documents/cursor/jpapi",
                )

                progress_bar.progress(80)

                if result.returncode == 0:
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()

                    st.success(f"Successfully deleted {deleted_count} {object_type}!")

                    current_deleted = st.session_state.get("deleted_count", 0)
                    st.session_state.deleted_count = current_deleted + deleted_count

                    self.object_selector.clear_selection()
                    st.session_state.show_delete_confirmation = False
                    st.session_state.delete_object_ids = []

                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]

                    st.balloons()

                    import time

                    time.sleep(1)
                    # Auto gather data after deletions
                    self._handle_gather_data()
                    st.rerun()
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("Deletion failed")
                    if result.stderr:
                        st.error(f"Error: {result.stderr}")
                    if result.stdout:
                        st.info(f"Output: {result.stdout}")
                return

            # If we get here, object type is not supported
            st.error(f"❌ Delete not yet supported for {object_type}.")
            st.info(
                "💡 Supported types: policies, profiles, groups, searches, packages, scripts"
            )
            return

        except Exception as e:
            st.error(f"Error during deletion: {e}")
            import traceback

            st.error(f"Details: {traceback.format_exc()}")

    def _render_deleted_objects_review(self) -> None:
        """Render deleted objects review modal"""
        deleted_history = st.session_state.get("deleted_objects_history", [])

        if not deleted_history:
            st.info("No deleted objects to review")
            if st.button("Close", key="close_empty_deleted"):
                st.session_state.show_deleted_review = False
                st.rerun()
            return

        # Center content
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)

            # Header
            st.markdown(
                f"""
                <div style="text-align: center; background: linear-gradient(135deg, #0078ff 0%, #3393ff 100%);
                     padding: 24px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #3393ff;">
                    <h2 style="color: white; font-size: 32px; margin: 0;">📋 Deleted Objects Review</h2>
                    <p style="color: white; font-size: 16px; margin: 10px 0 0 0;">Review recently deleted objects</p>
                    <div style="margin-top: 15px; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 8px; display: inline-block;">
                        <span style="color: #ffdc2e; font-weight: bold;">Total Deleted:</span>
                        <span style="color: white; font-weight: bold;">{len(deleted_history)}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.info(
                f"**{len(deleted_history)} objects** have been deleted during this session"
            )

            # Display deleted objects in a scrollable container
            st.markdown("**Deleted Objects:**")

            # Group by object type and environment
            from collections import defaultdict

            grouped = defaultdict(list)
            for obj in deleted_history:
                key = f"{obj['type']} ({obj['environment']})"
                grouped[key].append(obj)

            # Display grouped objects
            list_html = [
                '<div style="max-height: 400px; overflow-y: auto; background: #0b1b3f; border: 1px solid #2b3e6b; border-radius: 8px; padding: 12px; margin-bottom: 16px;">'
            ]

            for group_key, objects in grouped.items():
                list_html.append('<div style="margin-bottom: 16px;">')
                list_html.append(
                    f'<div style="color: #3393ff; font-weight: bold; margin-bottom: 8px; font-size: 14px;">{group_key}</div>'
                )

                for obj in objects:
                    safe_name = (
                        str(obj["name"]).replace("<", "&lt;").replace(">", "&gt;")
                    )
                    # Format timestamp
                    from datetime import datetime

                    deleted_time = datetime.fromisoformat(obj["deleted_at"])
                    time_str = deleted_time.strftime("%Y-%m-%d %H:%M:%S")

                    list_html.append(
                        f'<div style="display:flex; align-items:center; gap:8px; padding:8px; background: #001428; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #dc3545;">'
                        f'<div style="flex:1; min-width:0;">'
                        f'<div style="color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"><strong>{safe_name}</strong></div>'
                        f'<div style="color:#8b9dc3; font-size:11px;">Deleted: {time_str}</div>'
                        f"</div>"
                        f"<code style=\"color:#b9c4cb; font-size:11px;\">ID:{obj['id']}</code>"
                        f"</div>"
                    )
                list_html.append("</div>")

            list_html.append("</div>")
            st.markdown("".join(list_html), unsafe_allow_html=True)

            # Action buttons
            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button(
                    "✕ Close",
                    key="close_deleted_review",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.show_deleted_review = False
                    st.rerun()

            with col_btn2:
                if st.button(
                    "🗑️ Clear History",
                    key="clear_deleted_history",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.deleted_objects_history = []
                    st.session_state.show_deleted_review = False
                    st.success("Deleted objects history cleared!")
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            st.info(
                "💡 **Note:** Object restoration is not currently implemented. This review shows recently deleted objects for reference."
            )

    def _extract_id_from_hyperlink(self, id_value: str) -> str:
        """Extract ID from hyperlink"""
        if "=HYPERLINK(" in str(id_value):
            # Extract from Excel hyperlink formula
            import re

            match = re.search(r'=HYPERLINK\("[^"]*",\s*"(\d+)"\)', str(id_value))
            if match:
                return match.group(1)
        elif "<a href=" in str(id_value):
            # Extract from HTML hyperlink
            import re

            match = re.search(r">(\d+)<", str(id_value))
            if match:
                return match.group(1)
        return str(id_value)

    def _convert_excel_hyperlink_to_html(self, id_value: str) -> str:
        """Convert Excel hyperlink to HTML"""
        if "=HYPERLINK(" in str(id_value):
            # Convert Excel hyperlink to HTML
            import re

            match = re.search(r'=HYPERLINK\("([^"]*)",\s*"(\d+)"\)', str(id_value))
            if match:
                url, id_num = match.groups()
                return f'<a href="{url}" target="_blank" style="color: #3393ff; text-decoration: none; font-weight: bold;">{id_num}</a>'
        return str(id_value)

    def _get_selected_items_details(
        self, ids: Optional[List[str]] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Return details for selected items: list of dicts with name and id."""
        try:
            data_df = st.session_state.get("data", pd.DataFrame())
            if data_df.empty:
                return []

            # Build ID->Name map from current data frame
            id_to_name: Dict[str, str] = {}
            for _, row in data_df.iterrows():
                extracted_id = self._extract_id_from_hyperlink(row.get("ID", ""))
                id_to_name[str(extracted_id)] = str(row.get("Name", "Unknown"))

            selected_ids = ids or self.object_selector.get_selected_objects()
            items = [
                {"id": str(sid), "name": id_to_name.get(str(sid), "Unknown")}
                for sid in selected_ids
            ]

            if limit is not None:
                return items[:limit]
            return items
        except Exception:
            return []

    def _inject_svg_sprite_once(self) -> None:
        """Inject Apple-like inline SVG sprite and basic styles once per session."""
        if st.session_state.get("apple_icons_injected", False):
            return
        sprite = """
        <style>
            .ai { width: 22px; height: 22px; display: inline-flex; vertical-align: -3px; }
            .ai svg { width: 22px; height: 22px; stroke: currentColor; fill: none; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round; }
            .ai.delete { color: #ff6b6b; }
            .ai.sf-symbol svg { stroke: none; }
            .fab-icon { width: 28px; height: 28px; display: inline-flex; vertical-align: -6px; }
            .fab-icon svg { width: 28px; height: 28px; }
        </style>
        <svg width=\"0\" height=\"0\" style=\"position:absolute; visibility:hidden\">
            <symbol id=\"sf-number-circle-fill\" viewBox=\"0 0 20.2832 19.9316\">
                <path d=\"M9.96094 19.9219C15.459 19.9219 19.9219 15.459 19.9219 9.96094C19.9219 4.46289 15.459 0 9.96094 0C4.46289 0 0 4.46289 0 9.96094C0 15.459 4.46289 19.9219 9.96094 19.9219ZM9.96094 18.2617C5.37109 18.2617 1.66016 14.5508 1.66016 9.96094C1.66016 5.37109 5.37109 1.66016 9.96094 1.66016C14.5508 1.66016 18.2617 5.37109 18.2617 9.96094C18.2617 14.5508 14.5508 18.2617 9.96094 18.2617Z\" fill=\"#ffd60a\"/>
                <path d=\"M7.43164 14.7266C7.82227 14.7266 8.05664 14.5312 8.125 14.1699L8.57422 12.0703L10.3906 12.0703L9.99023 13.9844C9.90234 14.3848 10.1855 14.7266 10.5859 14.7266C10.9766 14.7266 11.2305 14.5312 11.3086 14.1699L11.748 12.0605L12.7637 12.0605C13.1445 12.0605 13.418 11.7773 13.418 11.4062C13.418 11.0742 13.1836 10.8301 12.8613 10.8301L12.0117 10.8301L12.4316 8.84766L13.457 8.84766C13.8379 8.84766 14.1113 8.56445 14.1113 8.19336C14.1113 7.86133 13.877 7.61719 13.5547 7.61719L12.6855 7.61719L13.0664 5.79102C13.1348 5.39062 12.8516 5.04883 12.4512 5.04883C12.0703 5.04883 11.8262 5.24414 11.748 5.61523L11.3281 7.61719L9.51172 7.61719L9.88281 5.79102C9.9707 5.40039 9.6875 5.04883 9.28711 5.04883C8.89648 5.04883 8.65234 5.24414 8.57422 5.61523L8.1543 7.61719L7.12891 7.61719C6.74805 7.61719 6.47461 7.90039 6.47461 8.27148C6.47461 8.60352 6.70898 8.84766 7.04102 8.84766L7.89062 8.84766L7.48047 10.8301L6.43555 10.8301C6.05469 10.8301 5.78125 11.1133 5.78125 11.4844C5.78125 11.8164 6.01562 12.0605 6.33789 12.0605L7.2168 12.0605L6.82617 13.9844C6.74805 14.3848 7.04102 14.7266 7.43164 14.7266ZM8.75 10.9473L9.19922 8.75L11.1719 8.75L10.7031 10.9473Z\" fill=\"white\"/>
            </symbol>
            <symbol id=\"sf-percent-circle\" viewBox=\"0 0 25.8008 25.459\">
                <path d=\"M25.4395 12.7246C25.4395 19.7461 19.7363 25.4395 12.7148 25.4395C5.69336 25.4395 0 19.7461 0 12.7246C0 5.70312 5.69336 0 12.7148 0C19.7363 0 25.4395 5.70312 25.4395 12.7246ZM1.81641 12.7246C1.81641 18.75 6.68945 23.623 12.7148 23.623C18.7402 23.623 23.6133 18.75 23.6133 12.7246C23.6133 6.69922 18.7402 1.82617 12.7148 1.82617C6.68945 1.82617 1.81641 6.69922 1.81641 12.7246Z\" fill=\"#ffd60a\"/>
                <path d=\"M20.7031 15.6445C20.4395 16.4551 19.5215 16.6113 18.1055 16.0938L13.5575 14.4368L15.9942 13.1409ZM10.1953 9.29688C10.1953 9.84375 10.1758 10.0488 10.5273 10.2344L11.8906 10.9592C11.5614 11.2149 11.331 11.5398 11.1711 11.9527C11.1385 11.934 11.1027 11.9146 11.0645 11.8945L9.93164 11.2793C9.80469 11.2109 9.72656 11.2012 9.61914 11.2012C9.14062 11.2012 8.89648 11.6992 7.7832 11.6992C6.43555 11.6992 5.37109 10.6348 5.37109 9.29688C5.37109 7.94922 6.43555 6.875 7.7832 6.875C9.11133 6.875 10.1953 7.93945 10.1953 9.29688ZM6.2793 9.29688C6.2793 10.1367 6.95312 10.8008 7.7832 10.8008C8.61328 10.8008 9.28711 10.1367 9.28711 9.29688C9.28711 8.45703 8.61328 7.7832 7.7832 7.7832C6.95312 7.7832 6.2793 8.45703 6.2793 9.29688Z\" fill=\"white\"/>
                <path d=\"M7.7832 18.5742C9.11133 18.5742 10.1953 17.5 10.1953 16.1426C10.1953 15.5957 10.1758 15.4004 10.5273 15.2051L20.7031 9.79492C20.4395 8.99414 19.5215 8.82812 18.1055 9.3457L12.959 11.2207C12.2656 11.4746 11.9531 11.8164 11.7773 12.4609L11.6602 12.9004C11.5918 13.1934 11.4746 13.3301 11.0645 13.5547L9.93164 14.1602C9.80469 14.2188 9.72656 14.248 9.61914 14.248C9.14062 14.248 8.89648 13.7402 7.7832 13.7402C6.43555 13.7402 5.37109 14.8047 5.37109 16.1426C5.37109 17.4902 6.43555 18.5742 7.7832 18.5742ZM7.7832 17.666C6.95312 17.666 6.2793 16.9922 6.2793 16.1426C6.2793 15.3125 6.95312 14.6387 7.7832 14.6387C8.61328 14.6387 9.28711 15.3125 9.28711 16.1426C9.28711 16.9922 8.61328 17.666 7.7832 17.666ZM13.0762 12.8711C12.8516 12.8711 12.6367 12.666 12.6367 12.4316C12.6367 12.1777 12.8418 11.9824 13.0762 11.9824C13.3301 11.9824 13.5352 12.1777 13.5352 12.4316C13.5352 12.6758 13.3301 12.8711 13.0762 12.8711Z\" fill=\"white\"/>
            </symbol>
            <symbol id=\"sf-trash-circle-fill\" viewBox=\"0 0 25.8008 25.459\">
                <path d=\"M12.7148 25.459C19.7266 25.459 25.4395 19.7461 25.4395 12.7344C25.4395 5.73242 19.7266 0.0195312 12.7148 0.0195312C5.71289 0.0195312 0 5.73242 0 12.7344C0 19.7461 5.71289 25.459 12.7148 25.459Z\" fill=\"#ff453a\"/>
                <path d=\"M9.14062 19.8145C7.8418 19.8145 7.29492 19.1211 7.10938 17.8223L6.16211 11.3574L19.2676 11.3574L18.3301 17.8223C18.1348 19.1113 17.5879 19.8145 16.2891 19.8145ZM10.7129 17.9102C10.8594 17.9102 10.9863 17.8516 11.0742 17.7637L12.7051 16.123L14.3555 17.7637C14.4434 17.8418 14.5605 17.9102 14.7168 17.9102C14.9805 17.9102 15.2246 17.666 15.2246 17.4023C15.2246 17.2559 15.1562 17.1387 15.0781 17.041L13.4473 15.4004L15.0781 13.7598C15.1855 13.6426 15.2344 13.5352 15.2344 13.3984C15.2344 13.1055 15.0098 12.8906 14.7168 12.8906C14.5703 12.8906 14.4629 12.9492 14.3652 13.0469L12.7051 14.6777L11.0645 13.0469C10.9766 12.9492 10.8594 12.9004 10.7129 12.9004C10.4297 12.9004 10.2051 13.125 10.2051 13.3984C10.2051 13.5449 10.2637 13.6621 10.3613 13.7598L11.9824 15.4004L10.3613 17.041C10.2637 17.1387 10.2051 17.2559 10.2051 17.4023C10.2051 17.666 10.4297 17.9102 10.7129 17.9102ZM5.67383 10.3906C4.93164 10.3906 4.55078 9.94141 4.55078 9.22852L4.55078 8.47656C4.55078 7.74414 4.96094 7.30469 5.67383 7.30469L19.7656 7.30469C20.498 7.30469 20.8887 7.74414 20.8887 8.47656L20.8887 9.22852C20.8887 9.94141 20.498 10.3906 19.7656 10.3906Z\" fill=\"white\"/>
            </symbol>
            <symbol id=\"ai-bolt\" viewBox=\"0 0 24 24\">
                <path d=\"M13 2l-8 11h6l-1 9 8-12h-6z\" />
            </symbol>
            <symbol id=\"ai-bars\" viewBox=\"0 0 24 24\">
                <rect x=\"4\" y=\"12\" width=\"3.5\" height=\"8\" rx=\"1\" />
                <rect x=\"10.25\" y=\"9\" width=\"3.5\" height=\"11\" rx=\"1\" />
                <rect x=\"16.5\" y=\"5\" width=\"3.5\" height=\"15\" rx=\"1\" />
            </symbol>
            <symbol id=\"ai-radio\" viewBox=\"0 0 24 24\">
                <circle cx=\"12\" cy=\"12\" r=\"7.5\" />
                <circle cx=\"12\" cy=\"12\" r=\"3.5\" fill=\"currentColor\" stroke=\"none\" />
            </symbol>
            <symbol id=\"ai-trash\" viewBox=\"0 0 24 24\">
                <path d=\"M4 7h16\" />
                <path d=\"M9 3h6l1 2H8z\" />
                <rect x=\"6\" y=\"7\" width=\"12\" height=\"13\" rx=\"2\" />
            </symbol>
            <symbol id=\"ai-warning\" viewBox=\"0 0 24 24\">
                <path d=\"M12 3l10 18H2z\" />
                <path d=\"M12 9v5M12 18.5h.01\" />
            </symbol>
            <symbol id=\"ai-eye\" viewBox=\"0 0 24 24\">
                <path d=\"M2 12s4-6 10-6 10 6 10 6-4 6-10 6S2 12 2 12z\" />
                <circle cx=\"12\" cy=\"12\" r=\"3.5\" />
            </symbol>
            <symbol id=\"ai-x\" viewBox=\"0 0 24 24\">
                <path d=\"M6 6l12 12M18 6L6 18\" />
            </symbol>
            <symbol id=\"ai-download\" viewBox=\"0 0 24 24\">
                <path d=\"M12 3v11\" />
                <path d=\"M8 10l4 4 4-4\" />
                <path d=\"M5 21h14\" />
            </symbol>
            <symbol id=\"ai-upload\" viewBox=\"0 0 24 24\">
                <path d=\"M12 21V10\" />
                <path d=\"M8 13l4-4 4 4\" />
                <path d=\"M5 3h14\" />
            </symbol>
            <symbol id=\"ai-check-circle\" viewBox=\"0 0 24 24\">
                <circle cx=\"12\" cy=\"12\" r=\"9\" />
                <path d=\"M8.5 12.5l2.5 2.5 4.5-5\" />
            </symbol>
            <symbol id=\"ai-info\" viewBox=\"0 0 24 24\">
                <circle cx=\"12\" cy=\"12\" r=\"9\" />
                <path d=\"M12 10v7M12 7h.01\" />
            </symbol>
        </svg>
        """
        st.markdown(sprite, unsafe_allow_html=True)
        st.session_state["apple_icons_injected"] = True
