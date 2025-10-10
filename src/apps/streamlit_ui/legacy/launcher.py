#!/usr/bin/env python3
"""
Enhanced Dashboard Launcher
Launches the appropriate Streamlit dashboard based on user selection
"""
import streamlit as st
import subprocess
import sys
from pathlib import Path


def main():
    st.set_page_config(
        page_title="JPAPI Dashboard Launcher", page_icon="🚀", layout="wide"
    )

    st.title("🚀 JPAPI Dashboard Launcher")
    st.markdown("**Choose your dashboard experience**")

    # Dashboard options
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📊 Main Dashboard")
        st.markdown("**Advanced Searches & Policies**")
        st.markdown(
            """
        - View both Advanced Searches and Policies
        - Environment selection (dev/staging/prod)
        - Export functionality with new naming
        - Authentication status checking
        - Clean old exports
        """
        )

        if st.button("Launch Main Dashboard", type="primary", use_container_width=True):
            launch_dashboard("main")

    with col2:
        st.markdown("### 🔍 Advanced Search Viewer")
        st.markdown("**Dedicated Search Management**")
        st.markdown(
            """
        - Advanced search management
        - Visual bubble charts
        - Deletion management
        - DaisyUI styling
        - Environment support
        """
        )

        if st.button("Launch Search Viewer", type="primary", use_container_width=True):
            launch_dashboard("advanced_searches")

    with col3:
        st.markdown("### 📋 Policies Viewer")
        st.markdown("**Dedicated Policy Management**")
        st.markdown(
            """
        - Policy management interface
        - Category distribution charts
        - Status filtering
        - DaisyUI styling
        - Environment support
        """
        )

        if st.button(
            "Launch Policies Viewer", type="primary", use_container_width=True
        ):
            launch_dashboard("policies")

    st.divider()

    # Quick actions
    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔐 Setup Authentication"):
            st.info("Run: `python3 jpapi_main.py setup auth`")

    with col2:
        if st.button("📤 Quick Export"):
            st.info(
                "Run: `python3 jpapi_main.py export 'advanced searches' --format csv`"
            )

    with col3:
        if st.button("🧹 Clean Exports"):
            st.info("Use the Clean Old Exports button in the main dashboard")

    # System info
    st.divider()
    st.markdown("### ℹ️ System Information")

    # Check if export utilities are available
    try:
        from src.lib.exports.export_utils import get_instance_prefix

        st.success("✅ Export utilities available")
    except ImportError:
        st.warning("⚠️ Export utilities not available")

    # Check authentication
    auth_file = Path("resources/config/authentication.json")
    if auth_file.exists():
        st.success("✅ Authentication configured")
    else:
        st.error("❌ Authentication not configured")
        st.info("Run: `python3 jpapi_main.py setup auth`")


def launch_dashboard(dashboard_type):
    """Launch the specified dashboard"""
    dashboard_files = {
        "main": "jpapi_dashboard.py",
        "advanced_searches": "advanced_search_viewer.py",
        "policies": "policies_viewer.py",
    }

    dashboard_file = dashboard_files.get(dashboard_type)
    if not dashboard_file:
        st.error(f"Unknown dashboard type: {dashboard_type}")
        return

    # Get the path to the dashboard file
    current_dir = Path(__file__).parent
    dashboard_path = current_dir / dashboard_file

    if not dashboard_path.exists():
        st.error(f"Dashboard file not found: {dashboard_path}")
        return

    # Launch the dashboard
    try:
        st.info(f"🚀 Launching {dashboard_type} dashboard...")

        # Use streamlit run command
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard_path),
            "--server.port",
            "8501",
            "--server.headless",
            "true",
        ]

        # Run in background
        subprocess.Popen(cmd, cwd=str(current_dir.parent.parent.parent))

        st.success(f"✅ {dashboard_type} dashboard launched!")
        st.info("The dashboard should open in your browser automatically.")

    except Exception as e:
        st.error(f"❌ Failed to launch dashboard: {e}")


if __name__ == "__main__":
    main()
