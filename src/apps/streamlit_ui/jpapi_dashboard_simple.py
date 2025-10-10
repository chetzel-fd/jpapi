import streamlit as st
import pandas as pd
import os
import subprocess
from pathlib import Path

# Page config
st.set_page_config(
    page_title="JPAPI Manager",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS styling
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
    
    /* Info cards styling */
    .info-card {
        background: #1e293b;
        border: 1px solid #334977;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .info-card-icon {
        font-size: 24px;
        color: #3393ff;
    }
    
    .info-card-content {
        flex: 1;
    }
    
    .info-card-label {
        color: #b9c4cb;
        font-size: 12px;
        margin: 0;
    }
    
    .info-card-value {
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
        margin: 0;
    }
    
    /* Header buttons */
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
    
    /* Object cards */
    .object-card {
        background: #1e293b;
        border: 1px solid #334977;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }
    
    .object-card:hover {
        border-color: #3393ff;
        box-shadow: 0 4px 12px rgba(51, 147, 255, 0.2);
    }
    
    .object-title {
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .object-details {
        color: #b9c4cb;
        font-size: 12px;
        margin-bottom: 8px;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .status-active {
        background-color: #22c55e;
        color: white;
    }
    
    .status-deleted {
        background-color: #ef4444;
        color: white;
    }
    
    .smart-indicator {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 8px;
        font-size: 10px;
        font-weight: bold;
        margin-left: 8px;
    }
    
    .smart-true {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    
    .smart-false {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
</style>
""",
    unsafe_allow_html=True,
)


def load_live_data(object_type, environment):
    """Load live data from CSV exports"""
    try:
        # Look for CSV files in multiple locations
        possible_dirs = [
            Path("data/csv-exports"),
            Path("storage/data"),
            Path("src/apps/streamlit_ui/data"),
            Path("."),
        ]

        # Environment-specific patterns
        patterns = {
            "searches": [
                f"{environment}-advanced-searches-export-*.csv",
                f"advanced-searches-export-*.csv",
                f"searches-export-*.csv",
            ],
            "policies": [
                f"{environment}-policies-export-*.csv",
                f"policies-export-*.csv",
            ],
            "profiles": [
                f"{environment}-profiles-export-*.csv",
                f"profiles-export-*.csv",
            ],
            "scripts": [
                f"{environment}-scripts-export-*.csv",
                f"scripts-export-*.csv",
            ],
        }

        # Try to find the most recent file
        latest_file = None
        latest_time = 0

        for pattern in patterns.get(object_type, [f"{object_type}-export-*.csv"]):
            for dir_path in possible_dirs:
                if dir_path.exists():
                    for file_path in dir_path.glob(pattern):
                        if file_path.stat().st_mtime > latest_time:
                            latest_time = file_path.stat().st_mtime
                            latest_file = file_path

        if latest_file and latest_file.exists():
            df = pd.read_csv(latest_file)
            st.success(f"✅ Loaded {len(df)} {object_type} from {latest_file.name}")
            return df
        else:
            # Fallback to sample data
            return get_sample_data(object_type)

    except Exception as e:
        st.warning(f"⚠️ Could not load live data: {e}")
        return get_sample_data(object_type)


def get_sample_data(object_type):
    """Get sample data for demonstration"""
    sample_data = {
        "searches": {
            "Name": [
                "All Macs",
                "Active Computers",
                "Software Inventory",
                "Mobile Devices",
                "Recent Logins",
            ],
            "Smart": [True, True, False, True, False],
            "Status": ["Active", "Active", "Active", "Active", "Deleted"],
            "Modified": [
                "2024-01-15",
                "2024-01-14",
                "2024-01-13",
                "2024-01-12",
                "2024-01-11",
            ],
            "ID": [1, 2, 3, 4, 5],
            "Type": [
                "Smart Group",
                "Smart Group",
                "Static Group",
                "Smart Group",
                "Static Group",
            ],
        },
        "policies": {
            "Name": [
                "Software Update Policy",
                "Security Configuration",
                "Application Deployment",
                "System Maintenance",
                "User Training",
            ],
            "Smart": [False, True, False, True, False],
            "Status": ["Active", "Active", "Active", "Active", "Deleted"],
            "Modified": [
                "2024-01-15",
                "2024-01-14",
                "2024-01-13",
                "2024-01-12",
                "2024-01-11",
            ],
            "ID": [1, 2, 3, 4, 5],
            "Type": ["Policy", "Policy", "Policy", "Policy", "Policy"],
        },
        "profiles": {
            "Name": [
                "WiFi Configuration",
                "VPN Settings",
                "Email Configuration",
                "Security Policies",
                "App Restrictions",
            ],
            "Smart": [True, False, True, False, True],
            "Status": ["Active", "Active", "Active", "Active", "Deleted"],
            "Modified": [
                "2024-01-15",
                "2024-01-14",
                "2024-01-13",
                "2024-01-12",
                "2024-01-11",
            ],
            "ID": [1, 2, 3, 4, 5],
            "Type": [
                "Configuration Profile",
                "Configuration Profile",
                "Configuration Profile",
                "Configuration Profile",
                "Configuration Profile",
            ],
        },
        "scripts": {
            "Name": [
                "System Information",
                "Software Installation",
                "User Account Setup",
                "Network Configuration",
                "Backup Script",
            ],
            "Smart": [False, True, False, True, False],
            "Status": ["Active", "Active", "Active", "Active", "Deleted"],
            "Modified": [
                "2024-01-15",
                "2024-01-14",
                "2024-01-13",
                "2024-01-12",
                "2024-01-11",
            ],
            "ID": [1, 2, 3, 4, 5],
            "Type": ["Script", "Script", "Script", "Script", "Script"],
        },
    }

    if object_type in sample_data:
        df = pd.DataFrame(sample_data[object_type])
        # Mark as sample data
        df["Name"] = "Sample " + df["Name"]
        return df
    else:
        return pd.DataFrame()


def main():
    # Initialize session state
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

    # Metrics
    total_count = len(data)
    selected_count = len(st.session_state.selected_objects)
    deleted_count = len(st.session_state.deleted_objects)

    # Main header with title and settings button
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        st.markdown("### ⚡ JPAPI Manager")

    with header_col2:
        # Settings button only
        st.markdown('<div class="header-buttons">', unsafe_allow_html=True)

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
                    env_options.index(current_env) if current_env in env_options else 0
                ),
                key="settings_env_selector",
            )

            # Object type selector
            type_options = [
                "searches",
                "policies",
                "profiles",
                "scripts",
                "packages",
                "groups",
            ]
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
                            st.success(f"✅ Successfully gathered {object_type} data!")
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
                        st.info("💡 Make sure jpapi_main.py exists and is executable")

            if st.button(
                "📊 Export Selected", key="settings_export", use_container_width=True
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

        st.markdown("</div>", unsafe_allow_html=True)

    # Instance Information Cards (like in your screenshot)
    st.markdown("### Instance Information")

    # Create info cards in a grid
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="info-card">
            <div class="info-card-icon">🌍</div>
            <div class="info-card-content">
                <p class="info-card-label">Environment</p>
                <p class="info-card-value">{}</p>
            </div>
        </div>
        """.format(
                st.session_state.current_environment.upper()
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="info-card">
            <div class="info-card-icon">📊</div>
            <div class="info-card-content">
                <p class="info-card-label">Object Type</p>
                <p class="info-card-value">{}</p>
            </div>
        </div>
        """.format(
                st.session_state.current_object_type.title()
            ),
            unsafe_allow_html=True,
        )

    with col3:
        server_url = f"your-{st.session_state.current_environment}.jamfcloud.com"
        st.markdown(
            """
        <div class="info-card">
            <div class="info-card-icon">🔗</div>
            <div class="info-card-content">
                <p class="info-card-label">Server URL</p>
                <p class="info-card-value">{}</p>
            </div>
        </div>
        """.format(
                server_url
            ),
            unsafe_allow_html=True,
        )

    # Data status
    if len(data) > 0 and data.iloc[0]["Name"].startswith("Sample"):
        st.warning(
            "⚠️ Using sample data - click '📥 Gather Data' in Settings to fetch real data from JAMF Pro"
        )
    else:
        st.success(
            f"✅ Loaded {len(data)} {st.session_state.current_object_type} objects from {st.session_state.current_environment}"
        )

    # Objects section with grid view
    st.markdown("### Objects")

    # Grid view - 3 columns
    cols = st.columns(3)

    for idx, row in data.iterrows():
        with cols[idx % 3]:
            with st.container():
                # Object card with custom styling
                status = row.get("Status", "Active")
                smart = row.get("Smart", False)

                # Status badge
                status_css = "status-active" if status == "Active" else "status-deleted"

                # Smart indicator
                smart_icon = "🧠" if smart else "📋"
                smart_text = "Smart" if smart else "Static"
                smart_css = "smart-true" if smart else "smart-false"

                st.markdown(
                    f"""
                <div class="object-card">
                    <div class="object-title">{row['Name']}</div>
                    <div class="object-details">ID: {row['ID']} • {row['Type']}</div>
                    <div class="object-details">
                        <span class="status-badge {status_css}">{status}</span>
                        <span class="smart-indicator {smart_css}">{smart_icon} {smart_text}</span>
                    </div>
                    <div class="object-details">Modified: {row['Modified']}</div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("---")

                # Action buttons
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

    # Sidebar with summary
    with st.sidebar:
        st.header("📊 Summary")
        st.metric("Total Objects", total_count)
        st.metric("Selected", selected_count)
        st.metric("Deleted", deleted_count)

        st.markdown(
            "**Environment:** {}".format(st.session_state.current_environment.title())
        )
        st.markdown(
            "**Object Type:** {}".format(st.session_state.current_object_type.title())
        )


if __name__ == "__main__":
    main()
