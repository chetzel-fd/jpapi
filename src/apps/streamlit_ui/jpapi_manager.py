#!/usr/bin/env python3
"""
JPAPI Manager - Streamlit UI for JAMF Pro API Management
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="JPAPI Manager",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for dark theme and styling
st.markdown(
    """
    <style>
    /* Dark theme base */
    .stApp {
        background: #0e1117;
        color: #ffffff;
    }
    
    /* Header styling */
    .elegant-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #334977;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
    }
    
    .header-buttons {
        display: flex;
        gap: 8px;
        flex-shrink: 0;
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
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .label {
        color: #3393ff;
        font-weight: 600;
        font-size: 12px;
        text-transform: lowercase;
    }
    
    .value {
        color: #ffffff;
        font-weight: 500;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .url-link {
        color: #3393ff;
        font-size: 11px;
    }
    
    .bullet {
        color: #3393ff;
        font-weight: bold;
        font-size: 16px;
        text-shadow: 0 0 8px rgba(51, 147, 255, 0.5);
    }
    
    .selection-actions {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #334977;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .object-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #334977;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    
    .object-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .object-title {
        color: #ffffff;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .object-details {
        color: #b9c4cb;
        font-size: 12px;
        margin-bottom: 12px;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "selected_objects" not in st.session_state:
    st.session_state.selected_objects = set()
if "deleted_objects" not in st.session_state:
    st.session_state.deleted_objects = set()
if "current_environment" not in st.session_state:
    st.session_state.current_environment = "sandbox"
if "current_object_type" not in st.session_state:
    st.session_state.current_object_type = "searches"


def convert_excel_hyperlink_to_html(hyperlink_text):
    """Convert Excel hyperlink formula to HTML link"""
    if "=HYPERLINK(" in str(hyperlink_text):
        import re

        # Extract URL and display text from =HYPERLINK("url","text")
        match = re.search(r'=HYPERLINK\("([^"]*)","([^"]*)"\)', str(hyperlink_text))
        if match:
            url = match.group(1)
            display_text = match.group(2)
            return f'<a href="{url}" target="_blank" style="color: #3393ff; text-decoration: none; font-weight: bold;">{display_text}</a>'
    return str(hyperlink_text)


def extract_id_from_hyperlink(hyperlink_text):
    """Extract actual ID from hyperlink formula"""
    if "=HYPERLINK(" in str(hyperlink_text):
        import re

        match = re.search(r'=HYPERLINK\("[^"]*","(\d+)"\)', str(hyperlink_text))
        if match:
            return match.group(1)
    return str(hyperlink_text)


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


def add_clickable_hyperlinks(df, object_type, environment):
    """Add clickable hyperlinks for object IDs that link to JAMF Pro"""
    if "ID" not in df.columns:
        return df

    # Check if ID column already contains hyperlinks
    sample_id = df["ID"].iloc[0] if len(df) > 0 else ""
    if "=HYPERLINK(" in str(sample_id) or "<a href=" in str(sample_id):
        # Already has hyperlinks, return as is
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


def main():
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

    # Store notifications in session state instead of showing them immediately
    if len(data) > 0:
        if "notifications" not in st.session_state:
            st.session_state.notifications = []
        st.session_state.notifications.append(
            {
                "type": "success",
                "message": f"✅ Loaded {len(data)} {st.session_state.current_object_type} from {st.session_state.current_environment}",
                "timestamp": pd.Timestamp.now(),
            }
        )
    else:
        if "notifications" not in st.session_state:
            st.session_state.notifications = []
        st.session_state.notifications.append(
            {
                "type": "warning",
                "message": f"⚠️ No {st.session_state.current_object_type} found for {st.session_state.current_environment} environment",
                "timestamp": pd.Timestamp.now(),
            }
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

    # Floating action buttons - functional
    with st.container():
        # Create invisible columns to position buttons
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        
        with col5:
            # Settings button
            if st.button("⚙️", key="floating_settings", help="Settings"):
                st.session_state.show_settings = not st.session_state.get('show_settings', False)
                st.rerun()
            
            # Gather Data button  
            if st.button("📥", key="floating_gather", help="Gather Data"):
                with st.spinner("Gathering fresh data with jpapi..."):
                    try:
                        import subprocess
                        import os
                        from core.config.object_type_manager import ObjectTypeManager
                        
                        object_manager = ObjectTypeManager()
                        cmd = object_manager.build_jpapi_command(
                            st.session_state.current_object_type,
                            st.session_state.current_environment,
                            "csv",
                        )
                        
                        st.info(f"Running: {' '.join(cmd)}")
                        result = subprocess.run(
                            cmd, capture_output=True, text=True, cwd=os.getcwd()
                        )
                        
                        if result.returncode == 0:
                            st.success("✅ Data gathered successfully!")
                            # Clear cache to force reload
                            cache_key = f"data_{st.session_state.current_object_type}_{st.session_state.current_environment}"
                            if cache_key in st.session_state:
                                del st.session_state[cache_key]
                            st.rerun()
                        else:
                            st.error(f"❌ Error gathering data: {result.stderr}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            
            # Export Selected button
            if st.button("📤", key="floating_export", help="Export Selected"):
                if st.session_state.selected_objects:
                    st.success(f"✅ Exporting {len(st.session_state.selected_objects)} selected items...")
                    # Add export logic here
                else:
                    st.warning("⚠️ No items selected for export")
            
            # Delete Selected button
            if st.button("🗑️", key="floating_delete", help="Delete Selected"):
                if st.session_state.selected_objects:
                    st.session_state.deleted_objects.update(st.session_state.selected_objects)
                    st.session_state.selected_objects.clear()
                    st.success(f"✅ Moved {len(st.session_state.selected_objects)} items to deleted")
                    st.rerun()
                else:
                    st.warning("⚠️ No items selected for deletion")

    # Main header with title and compact buttons - no spacing
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        # Elegant, fluid header with all info in one beautiful section
        server_url = get_jamf_server_url(st.session_state.current_environment)
        environment = st.session_state.current_environment.upper()
        object_type = st.session_state.current_object_type.title()

        # Extract instance name from URL
        instance_name = (
            server_url.replace("https://", "")
            .replace(".jamfcloud.com", "")
            .replace("http://", "")
        )

        st.markdown(
            f"""
            <div class="elegant-header">
                <div class="header-content">
                    <div class="header-main">
                        <h1 class="header-title">⚡ jpapi manager</h1>
                        <p class="header-subtitle">
                            <span class="label">env:</span>
                            <span class="value">{environment}</span>
                            <span class="bullet">•</span>
                            <span class="label">server:</span>
                            <span class="value">{instance_name}</span>
                            <span class="url-link">(<a href="{server_url}" target="_blank" style="color: #3393ff; text-decoration: none;">url</a>)</span>
                            <span class="bullet">•</span>
                            <span class="label">obj:</span>
                            <span class="value">{object_type}</span>
                        </p>
                    </div>
                    <div class="header-buttons">
            """,
            unsafe_allow_html=True,
        )

        # Clean header without old buttons - functionality moved to floating buttons

        st.markdown(
            """
                    </div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # Settings panel
    if st.session_state.get('show_settings', False):
        with st.expander("⚙️ Settings", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Environment")
                new_env = st.selectbox(
                    "Select Environment",
                    ["sandbox", "production", "staging"],
                    index=["sandbox", "production", "staging"].index(st.session_state.current_environment)
                )
                if new_env != st.session_state.current_environment:
                    st.session_state.current_environment = new_env
                    # Clear cache when environment changes
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.rerun()
            
            with col2:
                st.subheader("Object Type")
                new_type = st.selectbox(
                    "Select Object Type",
                    ["searches", "policies", "profiles", "packages", "groups"],
                    index=["searches", "policies", "profiles", "packages", "groups"].index(st.session_state.current_object_type)
                )
                if new_type != st.session_state.current_object_type:
                    st.session_state.current_object_type = new_type
                    # Clear cache when object type changes
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.rerun()
            
            st.divider()
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("🔄 Refresh Data", key="settings_refresh"):
                    # Clear all data cache
                    for key in list(st.session_state.keys()):
                        if key.startswith("data_"):
                            del st.session_state[key]
                    st.success("✅ Data cache cleared")
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Clear All Selections", key="settings_clear"):
                    st.session_state.selected_objects.clear()
                    st.session_state.deleted_objects.clear()
                    st.success("✅ All selections cleared")
                    st.rerun()

    # Show data source info
    if len(data) > 0 and data.iloc[0]["Name"].startswith("Sample"):
        st.warning(
            "⚠️ Using sample data - click '📥 Gather Data' to fetch real data from JAMF Pro"
        )

    # Objects section with grid view
    st.markdown("### Objects")

    # Debug messages removed

    # Grid view - 3 columns
    cols = st.columns(3)

    for idx, row in data.iterrows():
        with cols[idx % 3]:
            with st.container():
                # Extract actual ID for selection logic
                actual_id = extract_id_from_hyperlink(row["ID"])

                # Object card with custom styling
                st.markdown(
                    f"""
                <div class="object-card">
                    <div class="object-title">{row['Name']}</div>
                    <div class="object-details">ID: {convert_excel_hyperlink_to_html(row['ID'])} • {row.get('Type', 'N/A')}</div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("---")

                # Action buttons - matching port 8504 styling
                is_selected = actual_id in st.session_state.selected_objects

                button_text = "✓" if is_selected else "○"
                button_type = "primary" if is_selected else "secondary"

                if st.button(
                    button_text,
                    key=f"select_{actual_id}",
                    help=f"Toggle selection for {row['Name']}",
                    type=button_type,
                    use_container_width=True,
                ):
                    if is_selected:
                        st.session_state.selected_objects.discard(actual_id)
                    else:
                        st.session_state.selected_objects.add(actual_id)
                    st.rerun()

    # Add selection buttons below the grid
    if len(data) > 0:
        st.markdown("### 🎯 Selection Actions")

        # Create a styled button container
        st.markdown(
            """
        <div class="selection-actions">
        """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "✅ Select All",
                key="select_all",
                use_container_width=True,
                type="primary",
            ):
                for idx, row in data.iterrows():
                    actual_id = extract_id_from_hyperlink(row["ID"])
                    st.session_state.selected_objects.add(actual_id)
                st.rerun()

        with col2:
            if st.button(
                "❌ Deselect All",
                key="deselect_all",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.selected_objects.clear()
                st.rerun()

        with col3:
            if st.button(
                "🗑️ Delete Selected",
                key="delete_selected",
                use_container_width=True,
                type="secondary",
            ):
                for obj_id in st.session_state.selected_objects:
                    st.session_state.deleted_objects.add(obj_id)
                st.session_state.selected_objects.clear()
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

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
        object_options = [
            "searches",
            "policies",
            "profiles",
            "packages",
            "groups",
            "scripts",
        ]
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

        # Notifications tab
        st.markdown("---")
        st.markdown("### 🔔 Notifications")

        if "notifications" in st.session_state and st.session_state.notifications:
            # Show recent notifications
            recent_notifications = st.session_state.notifications[
                -5:
            ]  # Last 5 notifications

            for notification in reversed(recent_notifications):
                if notification["type"] == "success":
                    st.success(notification["message"])
                elif notification["type"] == "warning":
                    st.warning(notification["message"])
                elif notification["type"] == "error":
                    st.error(notification["message"])
                elif notification["type"] == "info":
                    st.info(notification["message"])

            # Clear notifications button
            if st.button("🗑️ Clear Notifications", key="clear_notifications"):
                st.session_state.notifications = []
                st.rerun()
        else:
            st.info("No notifications yet")


if __name__ == "__main__":
    main()
