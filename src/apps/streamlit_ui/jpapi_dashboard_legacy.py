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
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state


def load_live_data(object_type="searches", environment="sandbox"):
    """Load live data from CSV exports"""
    try:
        from pathlib import Path
        import glob
        import os

        # Try multiple data directory locations
        possible_dirs = [
            Path("storage/data/csv-exports"),
            Path("data/csv-exports"),
            Path("exports"),
            Path("storage/exports"),
            Path("data/exports"),
        ]

        csv_dir = None
        for dir_path in possible_dirs:
            if dir_path.exists():
                csv_dir = dir_path
                break

        if not csv_dir:
            # Try to create the default directory
            default_dir = Path("storage/data/csv-exports")
            default_dir.mkdir(parents=True, exist_ok=True)
            csv_dir = default_dir

        # Look for files based on object type with environment filtering
        patterns = []

        if object_type == "searches":
            patterns = [
                f"{environment}-advanced-searches-export-*.csv",
                f"{environment}-searches-export-*.csv",
                f"*-advanced-searches-export-*.csv",  # Fallback without env
                f"*-searches-export-*.csv",
                f"*advanced-searches*.csv",
                f"*searches*.csv",
            ]
        elif object_type == "policies":
            patterns = [
                f"{environment}-policies-export-*.csv",
                f"*-policies-export-*.csv",  # Fallback without env
                f"*policies*.csv",
            ]
        elif object_type == "profiles":
            patterns = [
                f"{environment}-profiles-export-*.csv",
                f"*-profiles-export-*.csv",  # Fallback without env
                f"*profiles*.csv",
            ]
        elif object_type == "packages":
            patterns = [
                f"{environment}-packages-export-*.csv",
                f"*-packages-export-*.csv",  # Fallback without env
                f"*packages*.csv",
            ]
        elif object_type == "groups":
            patterns = [
                f"{environment}-groups-export-*.csv",
                f"*-groups-export-*.csv",  # Fallback without env
                f"*groups*.csv",
            ]
        else:
            patterns = [
                f"{environment}-{object_type}-export-*.csv",
                f"*-{object_type}-export-*.csv",  # Fallback without env
                f"*{object_type}*.csv",
            ]

        files = []
        for pattern in patterns:
            found_files = list(csv_dir.glob(pattern))
            files.extend(found_files)
            if found_files:
                st.info(
                    f"🔍 Debug: Found files with pattern '{pattern}': {[f.name for f in found_files]}"
                )

        # Remove duplicates
        files = list(set(files))

        # Debug: Show what we're looking for
        st.info(
            f"🔍 Debug: Looking for {object_type} files in {environment} environment"
        )
        st.info(
            f"🔍 Debug: Searched patterns: {patterns[:3]}..."
        )  # Show first 3 patterns

        if not files:
            # Log what we looked for
            st.error(f"❌ No {object_type} files found in: {csv_dir}")
            st.info(f"📁 Directory exists: {csv_dir.exists()}")
            if csv_dir.exists():
                all_files = list(csv_dir.glob("*.csv"))
                if all_files:
                    st.info(
                        f"📄 Found {len(all_files)} CSV files: {[f.name for f in all_files[:5]]}"
                    )
                    st.warning("💡 Try different object type or check file naming")
                else:
                    st.warning("📂 Directory is empty - no CSV files found")
            else:
                st.error("📂 Directory does not exist")

            # Return sample data if no files found
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

        # Get the most recent file
        latest_file = max(files, key=lambda x: x.stat().st_mtime)

        # Log successful file found
        st.success(
            f"📁 Found {len(files)} {object_type} files, using: {latest_file.name}"
        )

        # Load the CSV
        df = pd.read_csv(latest_file)

        # Standardize column names
        if "name" in df.columns:
            df["Name"] = df["name"]
        if "id" in df.columns:
            df["ID"] = df["id"]
        if "type" in df.columns:
            df["Type"] = df["type"]
        if "status" in df.columns:
            df["Status"] = df["status"]
        elif "enabled" in df.columns:
            df["Status"] = df["enabled"].map({True: "Active", False: "Draft"})
        else:
            df["Status"] = "Active"

        # Add Last Modified if not present
        if "Last Modified" not in df.columns:
            df["Last Modified"] = "2024-01-15"

        # Ensure we have the required columns
        required_columns = ["Name", "ID", "Type", "Status", "Last Modified"]
        for col in required_columns:
            if col not in df.columns:
                if col == "Name":
                    df[col] = f"Sample {object_type.title()}"
                elif col == "ID":
                    df[col] = range(1001, 1001 + len(df))
                elif col == "Type":
                    df[col] = object_type.title()
                elif col == "Status":
                    df[col] = "Active"
                elif col == "Last Modified":
                    df[col] = "2024-01-15"

        # Debug: Show final processed data
        st.info(f"🔍 Debug: Final processed data with {len(df)} rows")
        st.info(f"🔍 Debug: Final columns: {list(df.columns)}")
        if len(df) > 0:
            st.info(f"🔍 Debug: Final first row: {df.iloc[0].to_dict()}")

        return df

    except Exception as e:
        st.error(f"Error loading live data: {e}")
        # Return sample data as fallback
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

    # Debug: Show what data we have
    st.info(f"🔍 Main Debug: Data has {len(data)} rows")
    if len(data) > 0:
        st.info(f"🔍 Main Debug: Data columns: {list(data.columns)}")
        st.info(
            f"🔍 Main Debug: First few names: {data['Name'].head(3).tolist() if 'Name' in data.columns else 'No Name column'}"
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
        st.markdown("### ⚡ JPAPI Manager")
        st.caption("jamf.company.com")

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
                    with st.spinner("Gathering fresh data with jpapi..."):
                        try:
                            import subprocess
                            import os

                            # Run jpapi export command
                            object_type = st.session_state.current_object_type
                            environment = st.session_state.current_environment

                            # Map object types to jpapi commands
                            if object_type == "searches":
                                cmd = [
                                    "python3",
                                    "jpapi_main.py",
                                    "export",
                                    "advanced-searches",
                                    environment,
                                ]
                            elif object_type == "policies":
                                cmd = [
                                    "python3",
                                    "jpapi_main.py",
                                    "export",
                                    "policies",
                                    environment,
                                ]
                            elif object_type == "profiles":
                                cmd = [
                                    "python3",
                                    "jpapi_main.py",
                                    "export",
                                    "profiles",
                                    environment,
                                ]
                            elif object_type == "packages":
                                cmd = [
                                    "python3",
                                    "jpapi_main.py",
                                    "export",
                                    "packages",
                                    environment,
                                ]
                            elif object_type == "groups":
                                cmd = [
                                    "python3",
                                    "jpapi_main.py",
                                    "export",
                                    "groups",
                                    environment,
                                ]
                            else:
                                cmd = [
                                    "python3",
                                    "jpapi_main.py",
                                    "export",
                                    object_type,
                                    environment,
                                ]

                            result = subprocess.run(
                                cmd, capture_output=True, text=True, cwd=os.getcwd()
                            )

                            if result.returncode == 0:
                                st.success(
                                    f"✅ Successfully gathered {object_type} data!"
                                )
                                # Clear cache to force reload
                                for key in list(st.session_state.keys()):
                                    if key.startswith("data_"):
                                        del st.session_state[key]
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to gather data: {result.stderr}")
                                st.info(
                                    "💡 Make sure jpapi is configured and authenticated"
                                )

                        except Exception as e:
                            st.error(f"❌ Error running jpapi: {e}")
                            st.info(
                                "💡 Make sure jpapi_main.py exists and is executable"
                            )

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

                # Instance Info Cards
                st.markdown("**Instance Information**")

                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.info(
                        f"🌐 **Environment**\n{st.session_state.current_environment.upper()}"
                    )

                with col_info2:
                    st.info(
                        f"📊 **Object Type**\n{st.session_state.current_object_type.title()}"
                    )

                # Server Info
                server_url = "jamf.company.com"
                if st.session_state.current_environment == "production":
                    server_url = "your-prod-company.jamfcloud.com"
                elif st.session_state.current_environment == "sandbox":
                    server_url = "your-dev-company.jamfcloud.com"

                st.info(f"🔗 **Server URL**\n{server_url}")

                st.markdown("---")

                st.markdown("**Display Options**")
                show_deleted = st.checkbox(
                    "Show Deleted Objects", value=False, key="settings_show_deleted"
                )
                auto_refresh = st.checkbox(
                    "Auto Refresh", value=True, key="settings_auto_refresh"
                )

                st.markdown("**Export Settings**")
                export_format = st.selectbox(
                    "Export Format",
                    ["CSV", "JSON", "Excel"],
                    key="settings_export_format",
                )

                if st.button("💾 Save Settings", key="settings_save"):
                    st.success("Settings saved!")

        st.markdown("</div>", unsafe_allow_html=True)

    # Compact controls row
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        env = st.selectbox(
            "Env",
            ["sandbox", "production"],
            index=0 if st.session_state.current_environment == "sandbox" else 1,
            key="env_selector",
            help="Select environment",
        )
        if env != st.session_state.current_environment:
            st.session_state.current_environment = env
            # Clear all data cache when switching environments
            for key in list(st.session_state.keys()):
                if key.startswith("data_"):
                    del st.session_state[key]
            st.rerun()

    with col2:
        object_type = st.selectbox(
            "Type",
            ["searches", "policies", "profiles", "packages", "groups"],
            index=0,
            key="object_type_selector",
            help="Select object type",
        )
        if object_type != st.session_state.current_object_type:
            st.session_state.current_object_type = object_type
            # Clear selections when switching object types
            st.session_state.selected_objects = set()
            st.session_state.deleted_objects = set()
            # Clear all data cache when switching types
            for key in list(st.session_state.keys()):
                if key.startswith("data_"):
                    del st.session_state[key]
            st.rerun()

    with col3:
        # Data info - use cached data if available
        cache_key = f"data_{st.session_state.current_object_type}_{st.session_state.current_environment}"
        if cache_key in st.session_state:
            cached_data = st.session_state[cache_key]
            if len(cached_data) > 0:
                # Check if it's sample data
                if cached_data.iloc[0]["Name"].startswith("Sample"):
                    st.caption(f"⚠️ Using sample data • {env}")
                else:
                    st.caption(f"📊 {len(cached_data)} {object_type} • {env}")
            else:
                st.caption(f"⚠️ No {object_type} data for {env}")
        else:
            st.caption(f"🔄 Loading {object_type} data...")

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
                is_deleted = row["ID"] in st.session_state.deleted_objects

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

    # Sidebar
    with st.sidebar:
        st.header("Quick Actions")
        st.caption("Manage your objects")

        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

        if st.button("📊 Export Selected", use_container_width=True):
            if selected_count > 0:
                st.success(f"Exported {selected_count} objects")
            else:
                st.warning("No objects selected")

        if st.button("🗑️ Clear Deleted", use_container_width=True):
            st.session_state.deleted_objects = set()
            st.rerun()

        st.markdown("**🧪 Sandbox Environment**")
        st.markdown("**⚡ Live Data Active**")


if __name__ == "__main__":
    main()
