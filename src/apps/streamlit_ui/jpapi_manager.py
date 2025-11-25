#!/usr/bin/env python3
"""
JPAPI Manager - SOLID Refactored Version
Maintains exact same functionality as original
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Ensure local directory is first in path BEFORE any imports
_current_dir = Path(__file__).parent
_project_src = _current_dir.parent.parent

# Clean and set path priority
for p in [str(_current_dir), str(_project_src)]:
    while p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(_current_dir))  # Local first
sys.path.insert(1, str(_project_src))  # Project second

# Import utilities and local modules using absolute paths from current dir
import importlib.util
import os

# Explicitly load local interfaces module
_interfaces_path = os.path.join(str(_current_dir), "interfaces.py")
_spec = importlib.util.spec_from_file_location("streamlit_interfaces", _interfaces_path)
_interfaces = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_interfaces)

# Extract classes from local interfaces
DataLoader = _interfaces.DataLoader
DataExporter = _interfaces.DataExporter
ObjectSelector = _interfaces.ObjectSelector
ObjectDeleter = _interfaces.ObjectDeleter
NotificationManager = _interfaces.NotificationManager
UIController = _interfaces.UIController

# Now import other local modules and utilities
from ui_utils import normalize_environment
from data_loader import CSVDataLoader, FileDataLoader
from data_exporter import JPAPIDataExporter
from object_selector import StreamlitObjectSelector
from object_deleter import MockObjectDeleter
from notification_manager import StreamlitNotificationManager
from ui_controller import JPAPIManagerController
from ui_styles import get_hide_sidebar_css, get_custom_css, get_javascript

# Page configuration
st.set_page_config(
    page_title="JPAPI Manager",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply custom styles
st.markdown(get_hide_sidebar_css(), unsafe_allow_html=True)
st.markdown(get_custom_css(), unsafe_allow_html=True)
st.markdown(get_javascript(), unsafe_allow_html=True)


def load_live_data(object_type: str, environment: str) -> pd.DataFrame:
    """Load live data with caching"""
    # Normalize environment name for consistent caching and file lookup
    normalized_env = normalize_environment(environment)
    cache_key = f"data_{object_type}_{normalized_env}"

    if cache_key in st.session_state:
        return st.session_state[cache_key]

    # Load data using our SOLID components (pass normalized env)
    data_loader = FileDataLoader()
    data = data_loader.load_data(object_type, normalized_env)

    if not data.empty:
        st.session_state[cache_key] = data
        st.session_state["show_data_loaded"] = True
        st.session_state["show_data_loaded_env"] = normalized_env
    else:
        # Fallback to sample data
        data_loader = CSVDataLoader()
        data = data_loader.load_data(object_type, normalized_env)
        st.session_state[cache_key] = data
        st.session_state["show_data_loaded"] = False  # Mark as fallback
        st.session_state["show_data_loaded_env"] = normalized_env

    return data


def main():
    """Main application function"""
    # Initialize SOLID components
    data_loader = FileDataLoader()
    data_exporter = JPAPIDataExporter()
    object_selector = StreamlitObjectSelector()
    object_deleter = MockObjectDeleter()
    notification_manager = StreamlitNotificationManager()

    # Create main controller
    controller = JPAPIManagerController(
        data_loader=data_loader,
        data_exporter=data_exporter,
        object_selector=object_selector,
        object_deleter=object_deleter,
        notification_manager=notification_manager,
    )

    # Render header
    controller.render_header()

    # Load data
    data = load_live_data(
        st.session_state.current_object_type, st.session_state.current_environment
    )

    # Show data loaded notification
    if st.session_state.get("show_data_loaded", False):
        normalized_env = normalize_environment(st.session_state.current_environment)
        loaded_env = st.session_state.get("show_data_loaded_env", normalized_env)

        if len(data) > 0:
            st.success(
                f"✅ Loaded {len(data)} {st.session_state.current_object_type} from {loaded_env}"
            )
        else:
            st.warning(
                f"⚠️ No {st.session_state.current_object_type} found for {loaded_env} environment"
            )
        st.session_state["show_data_loaded"] = False

    # Store data in session state for FAB
    st.session_state["data"] = data

    # Render delete confirmation if needed - FULL SCREEN, NO OTHER CONTENT
    if st.session_state.get("show_delete_confirmation", False):
        delete_object_ids = st.session_state.get("delete_object_ids", [])
        controller._render_delete_confirmation_direct(delete_object_ids)
        # STOP HERE - don't render anything else
        return

    # Render deleted objects review if needed - FULL SCREEN, NO OTHER CONTENT
    if st.session_state.get("show_deleted_review", False):
        controller._render_deleted_objects_review()
        # STOP HERE - don't render anything else
        return

    # Render data grid
    controller.render_data_grid(data)

    # Render FAB with stats
    controller.render_fab()


if __name__ == "__main__":
    main()
