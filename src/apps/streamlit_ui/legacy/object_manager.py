#!/usr/bin/env python3
"""
Elegant Object Manager v4 - Clean, minimal interface with instance switching
Incorporates Design #4 with top navigation and instance switcher
"""
import streamlit as st
import pandas as pd
import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import export utilities with fallback
try:
    from src.lib.exports.export_utils import (
        get_export_file_pattern,
        get_export_directory,
        clean_old_exports,
        get_instance_prefix,
    )

    EXPORT_UTILS_AVAILABLE = True
except ImportError:
    EXPORT_UTILS_AVAILABLE = False

    # Define fallback functions
    def get_export_file_pattern(*args, **kwargs):
        return "*.csv"

    def get_export_directory(*args, **kwargs):
        return "data/csv-exports"

    def clean_old_exports(*args, **kwargs):
        pass

    def get_instance_prefix(*args, **kwargs):
        return "dev"


# Initialize session state early
if "selected_objects" not in st.session_state:
    st.session_state.selected_objects = set()
if "deleted_objects" not in st.session_state:
    st.session_state.deleted_objects = set()
if "current_environment" not in st.session_state:
    st.session_state.current_environment = "sandbox"
if "current_object_type" not in st.session_state:
    st.session_state.current_object_type = "advanced-searches"
if "object_data_cache" not in st.session_state:
    st.session_state.object_data_cache = {}

st.set_page_config(
    page_title="jpapi manager",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Enhanced styling for Design #4
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
    
    /* Clean dark theme with glass morphism */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }
    
    /* Top navigation bar */
    .top-nav {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(20px);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .nav-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .nav-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Instance switcher */
    .instance-switcher {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .instance-switcher:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .instance-icon {
        font-size: 16px;
    }
    
    .instance-label {
        font-size: 12px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .instance-arrow {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.6);
        transition: transform 0.3s ease;
    }
    
    /* Actions dropdown */
    .actions-button {
        background: rgba(0, 122, 255, 0.1);
        border: 1px solid rgba(0, 122, 255, 0.3);
        border-radius: 8px;
        padding: 8px 16px;
        color: #007AFF;
        font-weight: 500;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .actions-button:hover {
        background: rgba(0, 122, 255, 0.2);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.2);
    }
    
    /* Stats container */
    .stats-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 24px;
        backdrop-filter: blur(20px);
    }
    
    .stat-item {
        text-align: center;
        padding: 16px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .stat-item:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-2px);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
    }
    
    .stat-label {
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
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 500;
    }
    
    .status-active {
        background: rgba(40, 167, 69, 0.2);
        color: #28a745;
        border: 1px solid rgba(40, 167, 69, 0.3);
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
    
    /* Enhanced buttons */
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
    
    /* Main content area */
    .main-content {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(20px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state already initialized at the top of the file

# Object type configuration
OBJECT_TYPES = {
    "advanced-searches": {
        "name": "Advanced Searches",
        "icon": "🔍",
        "description": "Search configurations and criteria",
        "available_envs": ["sandbox", "prod"],
    },
    "policies": {
        "name": "Policies",
        "icon": "📋",
        "description": "Device management policies",
        "available_envs": ["sandbox"],
    },
    "config-profiles": {
        "name": "Config Profiles",
        "icon": "⚙️",
        "description": "Configuration profiles for devices",
        "available_envs": ["sandbox", "prod"],
    },
    "packages": {
        "name": "Packages",
        "icon": "📦",
        "description": "Software packages and installers",
        "available_envs": ["sandbox", "prod"],
    },
    "smart-groups": {
        "name": "Smart Groups",
        "icon": "🧠",
        "description": "Dynamic device and user groups",
        "available_envs": ["sandbox", "prod"],
    },
}


def get_current_object_type_info():
    """Get information about the current object type"""
    return OBJECT_TYPES.get(
        st.session_state.current_object_type, OBJECT_TYPES["advanced-searches"]
    )


def is_object_type_available_in_env(object_type, environment):
    """Check if an object type is available in the current environment"""
    return environment in OBJECT_TYPES.get(object_type, {}).get("available_envs", [])


def get_available_object_types_for_env(environment):
    """Get list of object types available in the current environment"""
    return [
        obj_type
        for obj_type, config in OBJECT_TYPES.items()
        if environment in config["available_envs"]
    ]


def load_object_data(object_type, environment="sandbox", force_refresh=False):
    """Load data for any object type with caching"""
    cache_key = f"{object_type}_{environment}"

    # Check cache first (unless force refresh)
    if not force_refresh and cache_key in st.session_state.object_data_cache:
        return st.session_state.object_data_cache[cache_key]

    # Load data based on object type
    if object_type == "advanced-searches":
        data = load_advanced_searches(environment)
    elif object_type == "policies":
        data = load_policies_data(environment)
    elif object_type == "config-profiles":
        data = load_config_profiles_data(environment)
    elif object_type == "packages":
        data = load_packages_data(environment)
    elif object_type == "smart-groups":
        data = load_smart_groups_data(environment)
    else:
        data = get_sample_data()

    # Cache the data
    st.session_state.object_data_cache[cache_key] = data
    return data


def create_object_export(object_type, environment="sandbox"):
    """Create an export for any object type"""
    try:
        import subprocess
        import shutil

        # Try to find the correct Python executable
        python_cmd = None
        for cmd in [
            "python3",
            "python",
            "/usr/bin/python3",
            "/opt/homebrew/bin/python3",
        ]:
            if shutil.which(cmd):
                python_cmd = cmd
                break

        if not python_cmd:
            st.error("❌ Python executable not found")
            return False

        # Run the export command
        result = subprocess.run(
            [
                python_cmd,
                "jpapi_main.py",
                "--env",
                environment,
                "export",
                object_type,
            ],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode == 0:
            st.success(
                f"🎉 {OBJECT_TYPES[object_type]['name']} export created successfully for {environment}"
            )
            return True
        else:
            st.error(
                f"❌ {OBJECT_TYPES[object_type]['name']} export failed: {result.stderr}"
            )
            return False

    except Exception as e:
        st.error(f"❌ {OBJECT_TYPES[object_type]['name']} export error: {e}")
        return False


# Load real advanced searches data
def load_advanced_searches(environment="sandbox", show_progress=True):
    """Load real advanced searches from CSV export using new naming convention"""
    try:
        if show_progress:
            # Show loading indicator
            with st.spinner(f"🔄 Loading advanced searches from {environment}..."):
                time.sleep(0.3)  # Brief pause for visual feedback

        # Use the new export utilities
        export_dir = get_export_directory(environment)
        file_pattern = get_export_file_pattern("advanced-searches", "csv", environment)

        # Find matching files
        import glob

        csv_files = glob.glob(str(export_dir / file_pattern))

        if not csv_files:
            if show_progress:
                st.warning(
                    f"⚠️ No advanced searches exports found for {environment} environment"
                )
                st.info("💡 Use the '📥 Create Export' button to generate fresh data")
            return get_sample_data()

        # Get the most recent file
        latest_file = sorted(csv_files)[-1]

        if show_progress:
            st.info(f"📁 Loading from: `{os.path.basename(latest_file)}`")

        # Load and process the CSV
        df = pd.read_csv(latest_file)

        # Convert to our format
        data = {
            "Name": df["Name"].tolist(),
            "ID": df["ID"].tolist(),
            "Type": ["Advanced Search"]
            * len(df),  # Default type since CSV doesn't have Type column
        }

        if show_progress:
            st.success(
                f"✅ Loaded {len(data['Name'])} advanced searches from {environment}"
            )

        return pd.DataFrame(data)

    except Exception as e:
        if show_progress:
            st.error(f"❌ Error loading advanced searches: {e}")
        return get_sample_data()


def get_sample_data():
    """Fallback sample data"""
    return pd.DataFrame(
        {
            "Name": [
                "macOS 14 Base Level Apps - Crowdstrike",
                "macOS 12 + Netskope + Tenable",
                "macOS 14 Base Level Apps - Netskope",
                "macOS 12 + Tenable v10+",
                "macOS 14 Base Level Apps - Outlook",
                "macOS 12 + Tenable",
                "macOS 14 Base Level Apps - Tenable",
                "No Check-in for 30 Days",
            ],
            "ID": [155, 35, 162, 37, 165, 36, 164, 13],
            "Type": [
                "Static",
                "Smart",
                "Static",
                "Smart",
                "Static",
                "Smart",
                "Static",
                "Static",
            ],
        }
    )


def create_export(environment="sandbox"):
    """Create a new export using jpapi with live progress feedback"""
    try:
        import subprocess
        import time

        # Create progress containers
        progress_container = st.container()
        status_container = st.container()

        with progress_container:
            st.markdown("### 📥 Creating Export...")
            progress_bar = st.progress(0)
            status_text = st.empty()

        # Update status
        status_text.text("🔄 Initializing export process...")
        progress_bar.progress(10)
        time.sleep(0.5)

        status_text.text("🔐 Authenticating with JAMF Pro...")
        progress_bar.progress(25)
        time.sleep(0.5)

        status_text.text("📡 Fetching advanced searches data...")
        progress_bar.progress(50)

        # Run the export command - use python3 and handle different environments
        import shutil

        # Try to find the correct Python executable
        python_cmd = None
        for cmd in [
            "python3",
            "python",
            "/usr/bin/python3",
            "/opt/homebrew/bin/python3",
        ]:
            if shutil.which(cmd):
                python_cmd = cmd
                break

        if not python_cmd:
            st.error("❌ Python executable not found")
            return False

        result = subprocess.run(
            [
                python_cmd,
                "jpapi_main.py",
                "--env",
                environment,
                "export",
                "advanced-searches",
            ],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        status_text.text("💾 Processing and saving data...")
        progress_bar.progress(75)
        time.sleep(0.5)

        if result.returncode == 0:
            status_text.text("✅ Export completed successfully!")
            progress_bar.progress(100)
            time.sleep(1)

            with status_container:
                st.success(f"🎉 Export created successfully for {environment}")
                st.info(
                    f"📊 Data exported with instance prefix: `{get_instance_prefix(environment)}`"
                )
            return True
        else:
            status_text.text("❌ Export failed!")
            progress_bar.progress(100)

            with status_container:
                st.error(f"❌ Export failed: {result.stderr}")

                # Check if it's an authentication error
                if "Authentication failed" in result.stderr or "401" in result.stderr:
                    st.warning("🔐 OAuth Permissions Issue Detected")
                    st.error(
                        "**Root Cause:** OAuth token lacks permissions for Advanced Searches"
                    )

                    # One-click fix buttons
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("🚀 Auto-Fix & Test", type="primary"):
                            with st.spinner("Running auto-fix diagnostic..."):
                                import subprocess

                                result = subprocess.run(
                                    ["python", "debug_auth.py"],
                                    capture_output=True,
                                    text=True,
                                    cwd=project_root,
                                )
                                st.code(result.stdout)
                                if result.stderr:
                                    st.error(result.stderr)
                                st.rerun()

                    with col2:
                        if st.button("🔄 Clear & Reconfigure"):
                            with st.spinner("Clearing credentials..."):
                                import subprocess

                                subprocess.run(
                                    [
                                        "security",
                                        "delete-generic-password",
                                        "-s",
                                        "jpapi_sandbox",
                                        "-a",
                                        "sandbox",
                                    ],
                                    capture_output=True,
                                )
                                st.success("✅ Credentials cleared")
                                st.info("Run: `jpapi setup` to reconfigure")

                    with col3:
                        if st.button("📋 Show Manual Fix"):
                            st.markdown(
                                """
                            **JAMF Pro Admin Fix:**
                            1. Go to **Settings** → **System Settings** → **API Clients**
                            2. Find OAuth app: `b5828169-d67d-4bfe-a1f8-89bdecfe92ab`
                            3. Click **Edit** → **Scopes**
                            4. Enable **Advanced Computer Searches** permission
                            5. Save and test again
                            """
                            )
            return False

    except Exception as e:
        with status_container:
            st.error(f"❌ Export error: {e}")
        return False


# Live data refresh function
def refresh_data_live(environment):
    """Refresh data with live visual feedback"""
    with st.spinner("🔄 Refreshing data..."):
        # Clear any existing data
        if "sample_data" in st.session_state:
            del st.session_state.sample_data

        # Load fresh data
        new_data = load_advanced_searches(environment, show_progress=False)

        # Update session state
        st.session_state.current_data = new_data
        st.session_state.current_environment = environment

        st.success(
            f"🔄 Data refreshed! Loaded {len(new_data)} records from {environment}"
        )
        return new_data


# Load policies data function
def load_policies_data(environment="sandbox"):
    """Load policies data from CSV export"""
    try:
        with st.spinner(f"🔄 Loading policies from {environment}..."):
            time.sleep(0.3)  # Brief pause for visual feedback

        # Use the export utilities for policies
        export_dir = get_export_directory(environment)
        file_pattern = get_export_file_pattern("policies", "csv", environment)

        # Find matching files
        import glob

        csv_files = glob.glob(str(export_dir / file_pattern))

        if not csv_files:
            # Try to create an export automatically
            if create_object_export("policies", environment):
                # Try again after export
                csv_files = glob.glob(str(export_dir / file_pattern))
                if not csv_files:
                    return get_sample_policies_data()
            else:
                return get_sample_policies_data()

        # Get the most recent file
        latest_file = sorted(csv_files)[-1]

        # Load and process the CSV with proper handling of JSON data
        df = pd.read_csv(latest_file, quotechar='"', escapechar="\\")

        # Extract policy names and IDs from the JSON data in the 'general' column
        import json

        names = []
        ids = []

        for _, row in df.iterrows():
            try:
                # Parse the JSON in the 'general' column
                general_data = json.loads(row["general"])
                policy_name = general_data.get("name", {}).get("text", "Unknown Policy")
                policy_id = general_data.get("id", {}).get("text", "Unknown ID")

                names.append(policy_name)
                ids.append(policy_id)
            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                # Fallback if JSON parsing fails
                names.append(f"Policy {len(names) + 1}")
                ids.append(f"ID{len(ids) + 1}")

        # Convert to our format
        data = {
            "Name": names,
            "ID": ids,
            "Type": ["Policy"] * len(names),
        }

        # Success - data loaded
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Error loading policies: {e}")
        return get_sample_policies_data()


def create_policies_export(environment="sandbox"):
    """Create a policies export using jpapi"""
    try:
        import subprocess
        import shutil

        # Try to find the correct Python executable
        python_cmd = None
        for cmd in [
            "python3",
            "python",
            "/usr/bin/python3",
            "/opt/homebrew/bin/python3",
        ]:
            if shutil.which(cmd):
                python_cmd = cmd
                break

        if not python_cmd:
            st.error("❌ Python executable not found")
            return False

        # Run the export command for policies
        result = subprocess.run(
            [
                python_cmd,
                "jpapi_main.py",
                "--env",
                environment,
                "export",
                "policies",
            ],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode == 0:
            st.success(f"🎉 Policies export created successfully for {environment}")
            return True
        else:
            st.error(f"❌ Policies export failed: {result.stderr}")
            return False

    except Exception as e:
        st.error(f"❌ Policies export error: {e}")
        return False


def get_sample_policies_data():
    """Fallback sample policies data"""
    return pd.DataFrame(
        {
            "Name": [
                "macOS Security Policy - FileVault",
                "Network Access Control",
                "Application Restrictions",
                "Device Compliance Policy",
                "Data Loss Prevention",
                "Remote Access Policy",
                "Backup and Recovery",
                "User Authentication",
            ],
            "ID": [101, 102, 103, 104, 105, 106, 107, 108],
            "Type": ["Policy"] * 8,
        }
    )


def load_config_profiles_data(environment="sandbox"):
    """Load config profiles data from CSV export"""
    try:
        with st.spinner(f"🔄 Loading config profiles from {environment}..."):
            time.sleep(0.3)

        export_dir = get_export_directory(environment)
        file_pattern = get_export_file_pattern("config-profiles", "csv", environment)

        import glob

        csv_files = glob.glob(str(export_dir / file_pattern))

        if not csv_files:
            st.warning(
                f"⚠️ No config profiles exports found for {environment} environment"
            )
            st.info("💡 Use the '📥 Export' button to generate fresh data")
            if create_object_export("config-profiles", environment):
                csv_files = glob.glob(str(export_dir / file_pattern))
                if not csv_files:
                    return get_sample_config_profiles_data()
            else:
                return get_sample_config_profiles_data()

        latest_file = sorted(csv_files)[-1]
        st.info(f"📁 Loading from: `{os.path.basename(latest_file)}`")

        df = pd.read_csv(latest_file)
        data = {
            "Name": df["Name"].tolist(),
            "ID": df["ID"].tolist(),
            "Type": ["Config Profile"] * len(df),
        }

        st.success(f"✅ Loaded {len(data['Name'])} config profiles from {environment}")
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Error loading config profiles: {e}")
        return get_sample_config_profiles_data()


def load_packages_data(environment="sandbox"):
    """Load packages data from CSV export"""
    try:
        with st.spinner(f"🔄 Loading packages from {environment}..."):
            time.sleep(0.3)

        export_dir = get_export_directory(environment)
        file_pattern = get_export_file_pattern("packages", "csv", environment)

        import glob

        csv_files = glob.glob(str(export_dir / file_pattern))

        if not csv_files:
            st.warning(f"⚠️ No packages exports found for {environment} environment")
            st.info("💡 Use the '📥 Export' button to generate fresh data")
            if create_object_export("packages", environment):
                csv_files = glob.glob(str(export_dir / file_pattern))
                if not csv_files:
                    return get_sample_packages_data()
            else:
                return get_sample_packages_data()

        latest_file = sorted(csv_files)[-1]
        st.info(f"📁 Loading from: `{os.path.basename(latest_file)}`")

        df = pd.read_csv(latest_file)
        data = {
            "Name": df["Name"].tolist(),
            "ID": df["ID"].tolist(),
            "Type": ["Package"] * len(df),
        }

        st.success(f"✅ Loaded {len(data['Name'])} packages from {environment}")
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Error loading packages: {e}")
        return get_sample_packages_data()


def load_smart_groups_data(environment="sandbox"):
    """Load smart groups data from CSV export"""
    try:
        with st.spinner(f"🔄 Loading smart groups from {environment}..."):
            time.sleep(0.3)

        export_dir = get_export_directory(environment)
        file_pattern = get_export_file_pattern("smart-groups", "csv", environment)

        import glob

        csv_files = glob.glob(str(export_dir / file_pattern))

        if not csv_files:
            st.warning(f"⚠️ No smart groups exports found for {environment} environment")
            st.info("💡 Use the '📥 Export' button to generate fresh data")
            if create_object_export("smart-groups", environment):
                csv_files = glob.glob(str(export_dir / file_pattern))
                if not csv_files:
                    return get_sample_smart_groups_data()
            else:
                return get_sample_smart_groups_data()

        latest_file = sorted(csv_files)[-1]
        st.info(f"📁 Loading from: `{os.path.basename(latest_file)}`")

        df = pd.read_csv(latest_file)
        data = {
            "Name": df["Name"].tolist(),
            "ID": df["ID"].tolist(),
            "Type": ["Smart Group"] * len(df),
        }

        st.success(f"✅ Loaded {len(data['Name'])} smart groups from {environment}")
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Error loading smart groups: {e}")
        return get_sample_smart_groups_data()


def get_sample_config_profiles_data():
    """Fallback sample config profiles data"""
    return pd.DataFrame(
        {
            "Name": [
                "WiFi Configuration",
                "VPN Settings",
                "Email Configuration",
                "Security Settings",
                "App Restrictions",
                "Wallpaper Settings",
                "Browser Configuration",
                "Network Preferences",
            ],
            "ID": [201, 202, 203, 204, 205, 206, 207, 208],
            "Type": ["Config Profile"] * 8,
        }
    )


def get_sample_packages_data():
    """Fallback sample packages data"""
    return pd.DataFrame(
        {
            "Name": [
                "Google Chrome",
                "Microsoft Office",
                "Adobe Creative Suite",
                "Slack",
                "Zoom",
                "Visual Studio Code",
                "Docker Desktop",
                "Node.js Runtime",
            ],
            "ID": [301, 302, 303, 304, 305, 306, 307, 308],
            "Type": ["Package"] * 8,
        }
    )


def get_sample_smart_groups_data():
    """Fallback sample smart groups data"""
    return pd.DataFrame(
        {
            "Name": [
                "All MacBooks",
                "iOS Devices",
                "High Memory Computers",
                "Outdated Software",
                "Remote Workers",
                "Development Team",
                "Sales Department",
                "Executive Devices",
            ],
            "ID": [401, 402, 403, 404, 405, 406, 407, 408],
            "Type": ["Smart Group"] * 8,
        }
    )


# Top Navigation Bar
def render_top_navigation():
    """Render the top navigation bar with instance switcher and actions"""

    # Instance switcher
    instance_options = {
        "sandbox": {"icon": "🧪", "label": "Sandbox"},
        "prod": {"icon": "🚀", "label": "Production"},
    }

    current_env = st.session_state.current_environment
    current_instance = instance_options[current_env]

    # Create columns for the navigation - adjusted to include counts
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([2, 1, 1, 1])

    with nav_col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                <div>
                    <div style="font-size: 18px; font-weight: 600; color: #ffffff;">jpapi manager</div>
                    <div style="font-size: 12px; color: rgba(255, 255, 255, 0.7);">Advanced Search Management</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav_col2:
        # Instance selection (styled to match the visual design)
        new_env = st.selectbox(
            "Environment:",
            ["sandbox", "prod"],
            index=["sandbox", "prod"].index(current_env),
            format_func=lambda x: f"{instance_options[x]['icon']} {instance_options[x]['label']}",
            label_visibility="collapsed",
            key="instance_selector",
        )

        if new_env != current_env:
            st.session_state.current_environment = new_env
            st.rerun()

        # Object type selector
        available_types = get_available_object_types_for_env(current_env)
        current_type_info = get_current_object_type_info()

        # Find current index
        current_index = (
            available_types.index(st.session_state.current_object_type)
            if st.session_state.current_object_type in available_types
            else 0
        )

        new_object_type = st.selectbox(
            "Object Type:",
            available_types,
            index=current_index,
            format_func=lambda x: f"{OBJECT_TYPES[x]['icon']} {OBJECT_TYPES[x]['name']}",
            label_visibility="collapsed",
            key="object_type_selector",
        )

        if new_object_type != st.session_state.current_object_type:
            st.session_state.current_object_type = new_object_type
            # Clear cache for new object type
            cache_key = f"{new_object_type}_{current_env}"
            if cache_key in st.session_state.object_data_cache:
                del st.session_state.object_data_cache[cache_key]
            st.rerun()

    with nav_col3:
        # Actions dropdown menu with all buttons integrated
        current_type_info = get_current_object_type_info()
        with st.popover("⚡ Actions", use_container_width=True):
            if st.button("📥 Export", key="nav_export", use_container_width=True):
                with st.spinner(f"Creating {current_type_info['name']} export..."):
                    if create_object_export(
                        st.session_state.current_object_type, current_env
                    ):
                        # Clear cache to force reload
                        cache_key = (
                            f"{st.session_state.current_object_type}_{current_env}"
                        )
                        if cache_key in st.session_state.object_data_cache:
                            del st.session_state.object_data_cache[cache_key]
                        st.rerun()

            if st.button(
                "🗑️ Delete Selected", key="nav_delete", use_container_width=True
            ):
                if st.session_state.selected_objects:
                    with st.spinner("Processing deletions..."):
                        st.session_state.deleted_objects.update(
                            st.session_state.selected_objects
                        )
                        st.session_state.selected_objects.clear()
                        st.success(
                            f"🗑️ {len(st.session_state.deleted_objects)} items marked for deletion"
                        )
                        st.rerun()
                else:
                    st.warning("⚠️ No items selected")

            if st.button("🔄 Clear All", key="nav_clear", use_container_width=True):
                with st.spinner("Clearing selections..."):
                    st.session_state.selected_objects.clear()
                    st.session_state.deleted_objects.clear()
                    st.success("🧹 All selections cleared")
                    st.rerun()

            if st.button("🔄 Refresh", key="nav_refresh", use_container_width=True):
                # Force refresh by clearing cache
                cache_key = f"{st.session_state.current_object_type}_{current_env}"
                if cache_key in st.session_state.object_data_cache:
                    del st.session_state.object_data_cache[cache_key]
                st.rerun()


# Add sticky CSS for the top navigation
st.markdown(
    """
    <style>
    /* Make the entire top portion persistent */
    .stApp > div:first-child {
        position: sticky !important;
        top: 0 !important;
        z-index: 1000 !important;
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%) !important;
        backdrop-filter: blur(20px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        padding: 16px 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }
    
    /* Ensure proper stacking */
    .stApp {
        position: relative !important;
    }
    
    /* Style the integrated buttons */
    .stApp button {
        transition: all 0.3s ease;
    }
    
    .stApp button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Make the navigation more prominent */
    .stApp > div:first-child .stMarkdown {
        margin-bottom: 0;
    }
    
    /* Ensure proper positioning */
    .stApp > div:first-child {
        position: sticky !important;
        top: 0 !important;
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Use current environment from session state
environment = st.session_state.current_environment
instance_prefix = get_instance_prefix(environment)

# Authentication status
with st.sidebar:
    st.markdown("### 🔐 Authentication")
    try:
        import subprocess

        result = subprocess.run(
            ["python", "jpapi_main.py", "setup", "--list-credentials"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        if result.returncode == 0:
            # Test if authentication actually works
            test_result = subprocess.run(
                [
                    "python",
                    "jpapi_main.py",
                    "--env",
                    environment,
                    "export",
                    "advanced-searches",
                    "--format",
                    "csv",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                cwd=project_root,
            )
            if test_result.returncode == 0:
                st.success("✅ Authentication working")
            else:
                st.error("❌ OAuth permissions issue")
                st.warning("🔧 Token lacks Advanced Searches permission")
                st.info("**Fix:** Enable Advanced Searches scope in JAMF Pro")
        else:
            st.error("❌ Authentication not configured")
            st.info("**Setup:** Run `jpapi setup` to configure")
    except Exception as e:
        st.warning(f"⚠️ Unable to check authentication: {e}")

    st.markdown("### 🔧 Controls")
    sort_by = st.selectbox(
        "Sort by:",
        ["Name (A-Z)", "Name (Z-A)", "ID (Low-High)", "ID (High-Low)", "Type"],
        index=0,
    )

# Render top navigation
render_top_navigation()


# Load the real data using the new object type system
sample_data = load_object_data(st.session_state.current_object_type, environment)

# Show authentication warning if needed
if (
    len(sample_data) == 8
    and sample_data.iloc[0]["Name"] == "macOS 14 Base Level Apps - Crowdstrike"
):
    st.warning("⚠️ **Authentication Issue Detected** - Showing sample data")
    st.info(
        "🔧 **To fix:** Run `jpapi setup oauth` in terminal to refresh OAuth credentials"
    )
    st.markdown("---")


# Add sorting functionality
def shorten_name(name, max_length=40):
    """Shorten long names for better display"""
    if len(name) <= max_length:
        return name
    return name[: max_length - 3] + "..."


# Apply name shortening
sample_data["ShortName"] = sample_data["Name"].apply(shorten_name)

# Add sorting options
sort_options = {
    "Name (A-Z)": "Name",
    "Name (Z-A)": "Name_desc",
    "ID (Low-High)": "ID",
    "ID (High-Low)": "ID_desc",
    "Type": "Type",
}

# Apply sorting based on sidebar selection
if sort_by == "Name (A-Z)":
    sample_data = sample_data.sort_values("Name")
elif sort_by == "Name (Z-A)":
    sample_data = sample_data.sort_values("Name", ascending=False)
elif sort_by == "ID (Low-High)":
    sample_data = sample_data.sort_values("ID")
elif sort_by == "ID (High-Low)":
    sample_data = sample_data.sort_values("ID", ascending=False)
elif sort_by == "Type":
    sample_data = sample_data.sort_values("Type")

# Calculate counts for the top navigation - ensure accuracy
selected_count = len(st.session_state.selected_objects)
deleted_count = len(st.session_state.deleted_objects)
total_count = len(sample_data)

# Store counts in session state for consistency
st.session_state.total_count = total_count
st.session_state.selected_count = selected_count
st.session_state.deleted_count = deleted_count

# Main content area
current_type_info = get_current_object_type_info()
st.markdown(
    f"""
    <div class="main-content">
        <h3 style="color: #ffffff; margin-bottom: 16px;">{current_type_info['icon']} {current_type_info['name']}</h3>
        <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 20px;">{current_type_info['description']} • Use the toggle switches to select objects for deletion</p>
    """,
    unsafe_allow_html=True,
)

# Grid view with integrated toggles
# Create 3-column grid for better layout
cols_per_row = 3
for i in range(0, len(sample_data), cols_per_row):
    cols = st.columns(cols_per_row)

    for j, col in enumerate(cols):
        if i + j < len(sample_data):
            row = sample_data.iloc[i + j]
            object_id = str(row["ID"])
            object_name = row["ShortName"]  # Use shortened name
            full_name = row["Name"]  # Keep full name for tooltip
            object_type = row["Type"]
            is_selected = object_id in st.session_state.selected_objects
            is_deleted = object_id in st.session_state.deleted_objects

            with col:
                # Card styling
                card_class = "object-card"
                if is_deleted:
                    card_class += " deleted"
                elif is_selected:
                    card_class += " selected"

                # Status badge
                if is_deleted:
                    status_badge = (
                        '<span class="status-badge status-deleted">🗑️ Deleted</span>'
                    )
                elif is_selected:
                    status_badge = (
                        '<span class="status-badge status-selected">⚠️ Selected</span>'
                    )
                else:
                    status_badge = (
                        '<span class="status-badge status-active">✅ Active</span>'
                    )

                # Render card content with bigger text
                st.markdown(
                    f"""
                    <div class="{card_class}" title="{full_name}">
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

# Close main content div
st.markdown("</div>", unsafe_allow_html=True)

# Elegant hover sidebar for quick glance counts
st.markdown(
    f"""
    <div id="hover-sidebar" style="
        position: fixed;
        top: 50%;
        right: 0;
        transform: translateY(-50%);
        width: 60px;
        height: 200px;
        background: linear-gradient(135deg, rgba(30, 30, 30, 0.95) 0%, rgba(45, 45, 45, 0.95) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-right: none;
        border-radius: 20px 0 0 20px;
        box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
        z-index: 999;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 20px;
            padding: 20px 10px;
        ">
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #007AFF;">{st.session_state.total_count}</div>
                <div style="font-size: 8px; color: rgba(255, 255, 255, 0.6); text-transform: uppercase; letter-spacing: 1px;">TOTAL</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #34C759;">{st.session_state.selected_count}</div>
                <div style="font-size: 8px; color: rgba(255, 255, 255, 0.6); text-transform: uppercase; letter-spacing: 1px;">SELECTED</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #FF3B30;">{st.session_state.deleted_count}</div>
                <div style="font-size: 8px; color: rgba(255, 255, 255, 0.6); text-transform: uppercase; letter-spacing: 1px;">DELETED</div>
            </div>
        </div>
        
        <!-- Expanded content on hover -->
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(30, 30, 30, 0.98) 0%, rgba(45, 45, 45, 0.98) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-right: none;
            border-radius: 20px 0 0 20px;
            box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 20px;
            padding: 20px;
            width: 200px;
        ">
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: 700; color: #007AFF;">{st.session_state.total_count}</div>
                <div style="font-size: 12px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px;">Total Objects</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: 700; color: #34C759;">{st.session_state.selected_count}</div>
                <div style="font-size: 12px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px;">Selected Items</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: 700; color: #FF3B30;">{st.session_state.deleted_count}</div>
                <div style="font-size: 12px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px;">Marked for Deletion</div>
            </div>
        </div>
    </div>
    
    <style>
    #hover-sidebar:hover {{
        width: 200px;
    }}
    
    #hover-sidebar:hover > div:last-child {{
        opacity: 1;
        transform: translateX(0);
    }}
    
    #hover-sidebar:hover > div:first-child {{
        opacity: 0;
        transform: translateX(-100%);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Action buttons moved to top navigation

# Status info moved to top navigation
