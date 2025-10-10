import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="JPAPI Manager",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Simple CSS with your colors
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main .block-container {
        background: #252729;
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1600px;
    }
    
    [data-testid="metric-container"] {
        background: #00143b;
        border: 1px solid #334977;
        border-radius: 8px;
        padding: 16px;
    }
    
    .stButton > button {
        background: #3393ff;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: 500;
        font-size: 11px;
        height: 32px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Compact header buttons - emoji only */
    .header-buttons .stButton > button {
        background: #252729;
        color: #b9c4cb;
        border: 1px solid #334977;
        border-radius: 6px;
        padding: 8px;
        font-size: 18px;
        font-weight: 400;
        height: 36px;
        width: 36px;
        min-width: 36px;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .header-buttons .stButton > button:hover {
        background: #3393ff;
        color: #ffffff;
        border-color: #3393ff;
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(51, 147, 255, 0.3);
    }
    
    /* Popover styling with smaller fonts */
    .stPopover {
        font-size: 12px !important;
    }
    
    .stPopover .stMarkdown {
        font-size: 12px !important;
    }
    
    .stPopover .stButton > button {
        font-size: 11px !important;
        padding: 4px 8px !important;
        height: 28px !important;
    }
    
    .stPopover .stSelectbox > div > div {
        font-size: 11px !important;
    }
    
    .stPopover .stCheckbox > label {
        font-size: 11px !important;
    }
    
    /* Make popover content more compact */
    .stPopover .stMarkdown h3 {
        font-size: 14px !important;
        margin: 8px 0 4px 0 !important;
    }
    
    .stPopover .stMarkdown p {
        font-size: 11px !important;
        margin: 2px 0 !important;
    }
    
    .stPopover .stAlert {
        font-size: 10px !important;
        padding: 6px 8px !important;
        margin: 2px 0 !important;
    }
    
    /* Remove spacing between header elements */
    .header-buttons {
        margin: 0;
        padding: 0;
    }
    
    .header-buttons .stButton {
        margin: 0 2px;
    }
    
    .stButton > button:hover {
        background: #1a86ff;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
    
    /* Status indicators - matching the screenshot style */
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
    
    /* Object card styling */
    .object-card {
        background: #252729;
        border: 1px solid #334977;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        transition: all 0.2s ease;
    }
    
    .object-card:hover {
        border-color: #3393ff;
        box-shadow: 0 2px 8px rgba(51, 147, 255, 0.1);
    }
    
    .object-title {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
    }
    
    .object-details {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 12px;
    }
    
    /* Sticky button bar */
    .sticky-buttons {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #00143b;
        border-bottom: 1px solid #334977;
        padding: 8px 16px;
        z-index: 999;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .sticky-buttons .stButton > button {
        font-size: 9px;
        padding: 3px 6px;
        height: 24px;
        margin: 0 2px;
    }
    
    .stSelectbox > div > div {
        background: #00143b;
        border: 1px solid #334977;
        border-radius: 8px;
        color: #b9c4cb;
    }
    
    /* Floating metrics bar */
    .floating-metrics {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #00143b;
        border: 1px solid #334977;
        border-radius: 8px;
        padding: 8px 16px;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .metric-item {
        display: inline-block;
        margin: 0 8px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 16px;
        font-weight: 700;
        display: block;
    }
    
    .metric-label {
        font-size: 10px;
        color: #b9c4cb;
        text-transform: uppercase;
    }
    
    /* Floating action button */
    .floating-fab {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #3393ff;
        border: none;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        color: white;
        font-size: 24px;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(51, 147, 255, 0.3);
        transition: all 0.2s ease;
    }
    
    .floating-fab:hover {
        background: #1a86ff;
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(51, 147, 255, 0.4);
    }
    
    .floating-fab:active {
        transform: scale(0.95);
    }
    
    /* Floating action buttons container */
    .floating-actions {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .floating-btn {
        background: #3393ff;
        border: none;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        color: white;
        font-size: 18px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(51, 147, 255, 0.3);
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .floating-btn:hover {
        background: #1a86ff;
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(51, 147, 255, 0.4);
    }
    
    /* Elegant Header Styling */
    .elegant-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #334977;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .header-main {
        margin-bottom: 16px;
    }
    
    .header-title {
        color: #ffffff;
        font-size: 28px;
        font-weight: bold;
        margin: 0 0 4px 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .header-subtitle {
        color: #b9c4cb;
        font-size: 14px;
        margin: 0;
        font-weight: 400;
    }
    
    .header-info {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        align-items: center;
    }
    
    .info-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(51, 147, 255, 0.1);
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid rgba(51, 147, 255, 0.2);
    }
    
    .info-icon {
        font-size: 16px;
        color: #3393ff;
    }
    
    .info-label {
        color: #b9c4cb;
        font-size: 12px;
        font-weight: 500;
    }
    
    .info-value {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
    }
    
    .info-value a {
        color: #3393ff !important;
        text-decoration: none !important;
        font-weight: bold;
    }
    
    .info-value a:hover {
        color: #60a5fa !important;
        text-decoration: underline !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state


def add_clickable_hyperlinks(df, object_type, environment):
    """Add clickable hyperlinks for object IDs that link to JAMF Pro"""
    if "ID" not in df.columns:
        return df

    # Get the JAMF Pro server URL from environment
    server_url = get_jamf_server_url(environment)

    # Create clickable links for Streamlit
    def create_link(obj_id):
        if object_type == "policies":
            url = f"{server_url}/policies.html?id={obj_id}"
        elif object_type == "scripts":
            url = f"{server_url}/scripts.html?id={obj_id}"
        elif object_type == "profiles":
            url = f"{server_url}/osxconfigurationprofiles.html?id={obj_id}"
        elif object_type == "packages":
            url = f"{server_url}/packages.html?id={obj_id}"
        elif object_type == "groups":
            url = f"{server_url}/computergroups.html?id={obj_id}"
        elif object_type == "searches":
            url = f"{server_url}/advancedcomputersearches.html?id={obj_id}"
        else:
            url = server_url

        return f'<a href="{url}" target="_blank" style="color: #3393ff; text-decoration: none; font-weight: bold;">{obj_id}</a>'

    df["ID"] = df["ID"].apply(create_link)

    return df


def get_jamf_server_url(environment):
    """Get the JAMF Pro server URL from jpapi configuration"""
    try:
        from resources.config.central_config import CentralConfig

        config = CentralConfig()
        jamf_url = config.get_jamf_url()
        if jamf_url:
            return jamf_url
    except Exception as e:
        st.warning(f"Could not load JAMF URL from config: {e}")

    # Fallback URLs based on environment
    urls = {
        "dev": "https://your-dev-company.jamfcloud.com",
        "sandbox": "https://your-sandbox-company.jamfcloud.com",
        "production": "https://your-prod-company.jamfcloud.com",
    }
    return urls.get(environment, "https://your-company.jamfcloud.com")


def load_live_data(object_type="searches", environment="sandbox"):
    """Load live data from CSV exports using scalable configuration-driven approach"""
    try:
        from pathlib import Path
        from core.config.object_type_manager import ObjectTypeManager

        # Initialize configuration manager
        object_manager = ObjectTypeManager()

        # Use the standardized export directory
        csv_dir = Path("storage/data/csv-exports")
        csv_dir.mkdir(parents=True, exist_ok=True)

        # Get file patterns from configuration
        patterns = object_manager.get_file_patterns(object_type, environment)

        files = []
        for pattern in patterns:
            found_files = list(csv_dir.glob(pattern))
            files.extend(found_files)

        # Remove duplicates
        files = list(set(files))

        if not files:
            st.warning(f"⚠️ No {object_type} files found for {environment} environment")
            st.info("💡 Click 'Gather Data' to export fresh data from JAMF Pro")
            return object_manager.get_sample_data(object_type)

        # Get the most recent file
        latest_file = max(files, key=lambda x: x.stat().st_mtime)

        # Load the CSV
        df = pd.read_csv(latest_file)

        # Standardize the dataframe using configuration
        df = object_manager.standardize_dataframe(df, object_type)

        # Add clickable hyperlinks for IDs
        df = add_clickable_hyperlinks(df, object_type, environment)

        st.success(f"✅ Loaded {len(df)} {object_type} from {latest_file.name}")
        return df

    except Exception as e:
        st.error(f"Error loading live data: {e}")
        # Return sample data as fallback using configuration
        try:
            from core.config.object_type_manager import ObjectTypeManager

            object_manager = ObjectTypeManager()
            return object_manager.get_sample_data(object_type)
        except:
            # Ultimate fallback
            return pd.DataFrame(
                {
                    "Name": [f"Sample {object_type.title()} {i}" for i in range(1, 6)],
                    "ID": [1000 + i for i in range(1, 6)],
                    "Type": [object_type.title()] * 5,
                    "Status": ["Active", "Active", "Draft", "Active", "Active"],
                    "Last Modified": [
                        "2024-01-15",
                        "2024-01-14",
                        "2024-01-13",
                        "2024-01-12",
                        "2024-01-11",
                    ],
                }
            )


def main():
    # Initialize session state if not exists
    if "selected_objects" not in st.session_state:
        st.session_state.selected_objects = set()
    if "deleted_objects" not in st.session_state:
        st.session_state.deleted_objects = set()
    if "current_environment" not in st.session_state:
        st.session_state.current_environment = "sandbox"
    if "current_object_type" not in st.session_state:
        st.session_state.current_object_type = "searches"

    # Load live data based on current selections with caching
    cache_key = f"data_{st.session_state.current_object_type}_{st.session_state.current_environment}"

    if cache_key not in st.session_state:
        with st.spinner("Loading live data..."):
            data = load_live_data(
                object_type=st.session_state.current_object_type,
                environment=st.session_state.current_environment,
            )
            st.session_state[cache_key] = data
    else:
        data = st.session_state[cache_key]

    # Show data summary
    if len(data) > 0:
        st.success(
            f"✅ Loaded {len(data)} {st.session_state.current_object_type} from {st.session_state.current_environment}"
        )
    else:
        st.warning(
            f"⚠️ No {st.session_state.current_object_type} found for {st.session_state.current_environment} environment"
        )

    # Metrics
    total_count = len(data)
    selected_count = len(st.session_state.selected_objects)
    deleted_count = len(st.session_state.deleted_objects)

    # Floating action bar - interactive
    st.markdown(
        f"""
    <div class="floating-metrics">
        <div class="metric-item">
            <span class="metric-value" style="color: #3393ff;">{total_count}</span>
            <span class="metric-label">Total</span>
        </div>
        <div class="metric-item">
            <span class="metric-value" style="color: #22c55e;">{selected_count}</span>
            <span class="metric-label">Selected</span>
        </div>
        <div class="metric-item">
            <span class="metric-value" style="color: #ef4444;">{deleted_count}</span>
            <span class="metric-label">Deleted</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Main header with title and compact buttons - no spacing
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        # Elegant, fluid header with all info in one beautiful section
        server_url = get_jamf_server_url(st.session_state.current_environment)
        environment = st.session_state.current_environment.upper()
        object_type = st.session_state.current_object_type.title()

        st.markdown(
            f"""
            <div class="elegant-header">
                <div class="header-main">
                    <h1 class="header-title">⚡ JPAPI Manager</h1>
                    <p class="header-subtitle">JAMF Pro API Management Dashboard</p>
                </div>
                <div class="header-info">
                    <div class="info-item">
                        <span class="info-icon">🌍</span>
                        <span class="info-label">Environment:</span>
                        <span class="info-value">{environment}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-icon">📊</span>
                        <span class="info-label">Object Type:</span>
                        <span class="info-value">{object_type}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-icon">🔗</span>
                        <span class="info-label">Server:</span>
                        <span class="info-value"><a href="{server_url}" target="_blank" style="color: #3393ff; text-decoration: none;">{server_url}</a></span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with header_col2:
        # Compact button row with styling
        st.markdown('<div class="header-buttons">', unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

        with btn_col1:
            with st.popover("⚡", use_container_width=True):
                st.markdown("### 🎯 Actions")

                if st.button(
                    "🔄 Refresh Data", key="actions_refresh", use_container_width=True
                ):
                    # Clear all data cache to force data reload
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.rerun()

                if st.button(
                    "📥 Gather Data", key="actions_gather", use_container_width=True
                ):
                    # Use jpapi to gather fresh data
                    object_type = st.session_state.current_object_type
                    environment = st.session_state.current_environment

                    # Create progress containers
                    progress_container = st.container()
                    status_container = st.container()

                    with progress_container:
                        st.info(
                            f"🔄 Starting export of {object_type} from {environment}..."
                        )
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                    try:
                        import subprocess
                        import os
                        from pathlib import Path
                        import time

                        # Build command using scalable configuration
                        from core.config.object_type_manager import ObjectTypeManager

                        object_manager = ObjectTypeManager()
                        cmd = object_manager.build_jpapi_command(
                            object_type, environment, "csv"
                        )

                        # Run the command and show output
                        st.info(f"Running: {' '.join(cmd)}")
                        result = subprocess.run(
                            cmd, capture_output=True, text=True, cwd=os.getcwd()
                        )

                        if result.returncode == 0:
                            st.success(f"✅ Successfully gathered {object_type} data!")
                            if result.stdout:
                                st.info(f"Output: {result.stdout}")
                            # Clear cache to force reload
                            for key in list(st.session_state.keys()):
                                if key.startswith("data_"):
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to gather data: {result.stderr}")
                            if result.stdout:
                                st.info(f"Output: {result.stdout}")
                            st.info(
                                "💡 Make sure jpapi is configured and authenticated"
                            )

                    except Exception as e:
                        st.error(f"❌ Error running jpapi: {e}")
                        st.info("💡 Make sure jpapi_main.py exists and is executable")

                if st.button(
                    "📊 Export Selected", key="actions_export", use_container_width=True
                ):
                    if st.session_state.selected_objects:
                        st.success(
                            f"Exported {len(st.session_state.selected_objects)} objects"
                        )
                    else:
                        st.warning("No objects selected")

                if st.button(
                    "🗑️ Clear Deleted", key="actions_clear", use_container_width=True
                ):
                    st.session_state.deleted_objects = set()
                    st.rerun()

                if st.button(
                    "⚡ Bulk Actions", key="actions_bulk", use_container_width=True
                ):
                    st.success("Bulk Actions Menu Opened!")
                    if st.session_state.selected_objects:
                        st.info(
                            f"Selected {len(st.session_state.selected_objects)} objects"
                        )
                    if st.session_state.deleted_objects:
                        st.warning(
                            f"Marked {len(st.session_state.deleted_objects)} objects for deletion"
                        )

        with btn_col2:
            with st.popover("🔔", use_container_width=True):
                st.markdown("### 🔔 Notifications")
                st.warning("2 CSV warnings detected")
                st.info("1 new export available")
                st.success("System running normally")

        with btn_col3:
            if st.button(
                "🔄", key="refresh_btn", use_container_width=True, help="Refresh"
            ):
                st.rerun()

        with btn_col4:
            with st.popover("⚙️", use_container_width=True):
                st.markdown("### ⚙️ Settings")

                # Environment and Object Type controls in settings
                st.markdown("**Environment & Object Type**")

                # Environment selector
                env_options = ["sandbox", "production"]
                current_env = st.session_state.current_environment
                selected_env = st.selectbox(
                    "Environment",
                    options=env_options,
                    index=(
                        env_options.index(current_env)
                        if current_env in env_options
                        else 0
                    ),
                    key="settings_env_selector",
                )

                # Object type selector - now using configuration
                from core.config.object_type_manager import ObjectTypeManager

                object_manager = ObjectTypeManager()
                type_options = object_manager.get_available_object_types()
                current_type = st.session_state.current_object_type
                selected_type = st.selectbox(
                    "Object Type",
                    options=type_options,
                    index=(
                        type_options.index(current_type)
                        if current_type in type_options
                        else 0
                    ),
                    key="settings_type_selector",
                )

                # Handle changes
                if selected_env != current_env:
                    st.session_state.current_environment = selected_env
                    # Clear cache when switching environments
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.rerun()

                if selected_type != current_type:
                    st.session_state.current_object_type = selected_type
                    # Clear cache when switching types
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.rerun()

                st.divider()

                # Action buttons in settings
                st.markdown("**Actions**")

                if st.button(
                    "🔄 Refresh Data", key="settings_refresh", use_container_width=True
                ):
                    # Clear all data cache to force data reload
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.rerun()

                if st.button(
                    "📥 Gather Data", key="settings_gather", use_container_width=True
                ):
                    # Use jpapi to gather fresh data
                    with st.spinner("Gathering fresh data with jpapi..."):
                        try:
                            import subprocess
                            import os

                            # Run jpapi export command
                            object_type = st.session_state.current_object_type
                            environment = st.session_state.current_environment

                            # Build command using scalable configuration
                            from core.config.object_type_manager import (
                                ObjectTypeManager,
                            )

                            object_manager = ObjectTypeManager()
                            cmd = object_manager.build_jpapi_command(
                                object_type, environment, "csv"
                            )

                            # Run the command and show output
                            st.info(f"Running: {' '.join(cmd)}")
                            result = subprocess.run(
                                cmd, capture_output=True, text=True, cwd=os.getcwd()
                            )

                            if result.returncode == 0:
                                st.success(
                                    f"✅ Successfully gathered {object_type} data!"
                                )
                                if result.stdout:
                                    st.info(f"Output: {result.stdout}")
                                # Clear cache to force reload
                                for key in list(st.session_state.keys()):
                                    if key.startswith("data_"):
                                        del st.session_state[key]
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to gather data: {result.stderr}")
                                if result.stdout:
                                    st.info(f"Output: {result.stdout}")
                                st.info(
                                    "💡 Make sure jpapi is configured and authenticated"
                                )

                        except Exception as e:
                            st.error(f"❌ Error running jpapi: {e}")
                            st.info(
                                "💡 Make sure jpapi_main.py exists and is executable"
                            )

                if st.button(
                    "📊 Export Selected",
                    key="settings_export",
                    use_container_width=True,
                ):
                    if st.session_state.selected_objects:
                        st.success(
                            f"Exported {len(st.session_state.selected_objects)} objects"
                        )
                    else:
                        st.warning("No objects selected")

                if st.button(
                    "🗑️ Clear Deleted", key="settings_clear", use_container_width=True
                ):
                    st.session_state.deleted_objects = set()
                    st.rerun()

                # Server Info
                server_url = "jamf.company.com"
                if st.session_state.current_environment == "production":
                    server_url = "your-prod-company.jamfcloud.com"
                elif st.session_state.current_environment == "sandbox":
                    server_url = "your-dev-company.jamfcloud.com"

                st.info(f"🔗 **Server URL**\n{server_url}")

                st.markdown("---")

                st.markdown("**Display Options**")
                st.info("Display options will be available in future updates")

                if st.button("💾 Save Settings", key="settings_save"):
                    st.success("Settings saved!")

        st.markdown("</div>", unsafe_allow_html=True)

    # Data status info
    cache_key = f"data_{st.session_state.current_object_type}_{st.session_state.current_environment}"
    if cache_key in st.session_state:
        cached_data = st.session_state[cache_key]
        if len(cached_data) > 0:
            # Check if it's sample data
            if cached_data.iloc[0]["Name"].startswith("Sample"):
                st.caption(
                    f"⚠️ Using sample data • {st.session_state.current_environment}"
                )
            else:
                st.caption(
                    f"📊 {len(cached_data)} {st.session_state.current_object_type} • {st.session_state.current_environment}"
                )
        else:
            st.caption(
                f"⚠️ No {st.session_state.current_object_type} data for {st.session_state.current_environment}"
            )
    else:
        st.caption(f"🔄 Loading {st.session_state.current_object_type} data...")

    # Show data source info
    if len(data) > 0 and data.iloc[0]["Name"].startswith("Sample"):
        st.warning(
            "⚠️ Using sample data - click '📥 Gather Data' to fetch real data from JAMF Pro"
        )

    # Objects section with grid view
    st.markdown("### Objects")

    # Debug: Show what we're about to render
    st.info(f"🔍 Render Debug: About to render {len(data)} objects")
    if len(data) > 0:
        st.info(
            f"🔍 Render Debug: First object name: {data.iloc[0].get('Name', 'No Name')}"
        )

    # Grid view - 3 columns
    cols = st.columns(3)

    for idx, row in data.iterrows():
        with cols[idx % 3]:
            with st.container():
                # Object card with custom styling
                st.markdown(
                    f"""
                <div class="object-card">
                    <div class="object-title">{row['Name']}</div>
                    <div class="object-details">ID: {row['ID']} • {row['Type']}</div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("---")

                # Action buttons - matching port 8504 styling
                is_selected = row["ID"] in st.session_state.selected_objects

                button_text = "✓" if is_selected else "○"
                button_type = "primary" if is_selected else "secondary"

                if st.button(
                    button_text,
                    key=f"select_{row['ID']}",
                    help=f"Toggle selection for {row['Name']}",
                    type=button_type,
                    use_container_width=True,
                ):
                    if is_selected:
                        st.session_state.selected_objects.discard(row["ID"])
                    else:
                        st.session_state.selected_objects.add(row["ID"])
                    st.rerun()

    # Sidebar - Environment and Object Type Selection
    with st.sidebar:
        st.header("Configuration")

        # Environment selection
        environment_options = ["sandbox", "production"]
        current_env = st.selectbox(
            "Environment",
            environment_options,
            index=environment_options.index(st.session_state.current_environment),
            key="env_selector",
        )

        if current_env != st.session_state.current_environment:
            st.session_state.current_environment = current_env
            # Clear cache when environment changes
            for key in list(st.session_state.keys()):
                if key.startswith("data_"):
                    del st.session_state[key]
            st.rerun()

        # Object type selection
        object_options = ["searches", "policies", "profiles", "packages", "groups"]
        current_type = st.selectbox(
            "Object Type",
            object_options,
            index=object_options.index(st.session_state.current_object_type),
            key="type_selector",
        )

        if current_type != st.session_state.current_object_type:
            st.session_state.current_object_type = current_type
            # Clear cache when object type changes
            for key in list(st.session_state.keys()):
                if key.startswith("data_"):
                    del st.session_state[key]
            st.rerun()

        st.markdown(f"**🌍 {current_env.upper()} Environment**")
        st.markdown(f"**📊 {current_type.title()} Objects**")


if __name__ == "__main__":
    main()
