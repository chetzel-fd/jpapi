#!/usr/bin/env python3
"""
Enhanced JAMF Pro Dashboard - Advanced Searches & Policies
Updated to use new instance prefix naming and export utilities
"""
import streamlit as st
import pandas as pd
import subprocess
from pathlib import Path
from datetime import datetime
import sys
import json
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import new export utilities
try:
    from src.lib.exports.export_utils import (
        get_export_file_pattern,
        get_export_directory,
        clean_old_exports,
        get_instance_prefix
    )
    EXPORT_UTILS_AVAILABLE = True
except ImportError:
    EXPORT_UTILS_AVAILABLE = False
    st.warning("⚠️ Export utilities not available. Some features may be limited.")

st.set_page_config(page_title="JAMF Pro Dashboard", page_icon="📊", layout="wide")


def load_advanced_searches(environment="dev"):
    """Load the most recent advanced searches CSV using new export utilities"""
    try:
        if EXPORT_UTILS_AVAILABLE:
            # Use new export utilities
            csv_dir = get_export_directory(environment)
            pattern = get_export_file_pattern("advanced-searches", "csv", environment)
            files = list(csv_dir.glob(pattern))
        else:
            # Fallback to old method
            csv_dir = Path("storage/data/csv-exports")
            files = list(csv_dir.glob("*-advanced-searches-export-*.csv"))

        if not files:
            return pd.DataFrame(), "No files found", 0, environment

        # Get the most recent file
        latest_file = max(files, key=lambda x: x.stat().st_mtime)

        try:
            df = pd.read_csv(latest_file)
            file_age = datetime.now().timestamp() - latest_file.stat().st_mtime
            age_minutes = int(file_age / 60)

            return df, latest_file.name, age_minutes, environment
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return pd.DataFrame(), "Error", 0, environment
        except Exception as e:
        st.error(f"Error accessing export directory: {e}")
        return pd.DataFrame(), "Error", 0, environment


def load_policies(environment="dev"):
    """Load the most recent policies CSV using new export utilities"""
    try:
        if EXPORT_UTILS_AVAILABLE:
            # Use new export utilities
            csv_dir = get_export_directory(environment)
            pattern = get_export_file_pattern("policies", "csv", environment)
            files = list(csv_dir.glob(pattern))
        else:
            # Fallback to old method
            csv_dir = Path("storage/data/csv-exports")
            files = list(csv_dir.glob("*-policies-export-*.csv"))

        if not files:
            return pd.DataFrame(), "No files found", 0, environment

        # Get the most recent file
        latest_file = max(files, key=lambda x: x.stat().st_mtime)

        try:
            df = pd.read_csv(latest_file)
            file_age = datetime.now().timestamp() - latest_file.stat().st_mtime
            age_minutes = int(file_age / 60)

            return df, latest_file.name, age_minutes, environment
        except Exception as e:
            st.error(f"Error loading policies CSV: {e}")
            return pd.DataFrame(), "Error", 0, environment
    except Exception as e:
        st.error(f"Error accessing policies export directory: {e}")
        return pd.DataFrame(), "Error", 0, environment


def create_export(export_type="advanced-searches", environment="dev"):
    """Create a new export using the new CLI"""
    try:
        # Use the new jpapi_main.py (fix path issue)
        cmd = [
            sys.executable,
            "jpapi_main.py",  # Use relative path from project root
            "export",
            export_type,
            "--env",
            environment,
            "--format",
            "csv"
        ]

            result = subprocess.run(
            cmd,
                capture_output=True,
                text=True,
            timeout=120,  # Increased timeout for larger exports
            cwd=str(project_root)
        )

        if result.returncode == 0:
            st.success(f"✅ {export_type} export completed successfully!")
            st.rerun()
        else:
            st.error(f"❌ Export failed: {result.stderr}")
            if "Authentication failed" in result.stderr or "not configured" in result.stderr:
                st.info("💡 Run `python3 jpapi_main.py setup auth` to configure JAMF Pro credentials")
            elif "not found" in result.stderr:
                st.info("💡 Make sure you're in the correct directory and jpapi_main.py exists")
    except subprocess.TimeoutExpired:
        st.error("❌ Export timed out. Try again or check your connection.")
        except Exception as e:
        st.error(f"❌ Export error: {e}")


def check_authentication():
    """Check if authentication is configured"""
    try:
        auth_file = project_root / "resources" / "config" / "authentication.json"
        if not auth_file.exists():
            return False, "No authentication file found"
        
        with open(auth_file, 'r') as f:
            auth_config = json.load(f)
        
        if not auth_config.get('jamf_url'):
            return False, "JAMF URL not configured"
        
        return True, "Authentication configured"
        except Exception as e:
        return False, f"Error checking authentication: {e}"


def get_jamf_server_name():
    """Get the actual JAMF Pro server name from config"""
    try:
        # Use absolute path from project root
        auth_file = Path("resources/config/authentication.json")
        if auth_file.exists():
            with open(auth_file, 'r') as f:
                auth_config = json.load(f)
            jamf_url = auth_config.get('jamf_url', '')
            if jamf_url:
                # Extract server name from URL
                from urllib.parse import urlparse
                parsed = urlparse(jamf_url)
                return parsed.hostname or jamf_url
        return "Unknown Server"
    except Exception as e:
        return f"Error: {e}"


def main():
    st.title("📊 JAMF Pro Dashboard - Enhanced")
    
    # Get actual server name
    server_name = get_jamf_server_name()
    st.markdown(f"**Advanced Searches & Policies Management - {server_name}**")

    # Check authentication
    auth_configured, auth_message = check_authentication()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        
        # Environment selection (based on actual JAMF Pro server)
            environment = st.selectbox(
            "Environment",
            ["dev", "staging", "prod"],
            index=0,
            help=f"Select the JAMF Pro environment (dev={server_name})",
        )
        
        # Data type selection
        data_type = st.selectbox(
            "Data Type",
            ["Advanced Searches", "Policies"],
                index=0,
            help="Select the type of data to view",
        )
        
        st.divider()
        
        # Authentication status
        if auth_configured:
            st.success("✅ Authentication configured")
                        else:
            st.error(f"❌ {auth_message}")
            if st.button("🔐 Setup Authentication"):
                st.info("Run: `python3 jpapi_main.py setup auth`")

        st.divider()

        # Action buttons
        if st.button("🔄 Refresh Data", type="primary"):
                st.rerun()

        if st.button("📤 Create Export"):
            export_type = "advanced-searches" if data_type == "Advanced Searches" else "policies"
            create_export(export_type, environment)
        
        if st.button("🧹 Clean Old Exports"):
            if EXPORT_UTILS_AVAILABLE:
                try:
                    clean_old_exports("advanced-searches", environment)
                    clean_old_exports("policies", environment)
                    st.success("✅ Old exports cleaned")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Clean failed: {e}")
            else:
                st.warning("Export utilities not available")

    # Load data based on selection
    if data_type == "Advanced Searches":
        df, filename, age_minutes, env = load_advanced_searches(environment)
        object_name = "Advanced Searches"
    else:
        df, filename, age_minutes, env = load_policies(environment)
        object_name = "Policies"

    # Display data source info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data Source", filename)
        with col2:
        st.metric("Records", len(df))
    with col3:
        st.metric("Age", f"{age_minutes} min")
    with col4:
        instance_prefix = get_instance_prefix(environment) if EXPORT_UTILS_AVAILABLE else "unknown"
        st.metric("Instance", instance_prefix)

    if df.empty:
        st.warning(f"⚠️ No {object_name.lower()} data available. Click 'Create Export' to generate data.")
            return

    # Display data
    st.subheader(f"{object_name}")

    # Basic filtering
    search_term = st.text_input("🔍 Search", placeholder="Search by name...")

    if search_term:
        df = df[df["Name"].str.contains(search_term, case=False, na=False)]

    # Show data
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Stats based on data type
    if not df.empty:
        st.subheader("Statistics")
        
        if data_type == "Advanced Searches":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Searches", len(df))
            with col2:
                smart_count = len(df[df.get("Smart", False) == True])
                st.metric("Smart Searches", smart_count)
            with col3:
                static_count = len(df[df.get("Smart", False) == False])
                st.metric("Static Searches", static_count)
        else:  # Policies
            col1, col2, col3 = st.columns(3)
        with col1:
                st.metric("Total Policies", len(df))
        with col2:
                enabled_count = len(df[df.get("Enabled", False) == True])
                st.metric("Enabled Policies", enabled_count)
            with col3:
                disabled_count = len(df[df.get("Enabled", False) == False])
                st.metric("Disabled Policies", disabled_count)


if __name__ == "__main__":
    main()