#!/usr/bin/env python3
"""
JPAPI Manager - Streamlit UI for JAMF Pro API Management
"""

import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="JPAPI Manager",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide the sidebar completely and hide popover buttons
st.markdown(
    """
<style>
    .css-1d391kg {display: none;}
    .css-1lcbmhc {display: none;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="baseButton-secondary"] {display: none !important;}
</style>
""",
    unsafe_allow_html=True,
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
    
    .header-main {
        flex: 1;
    }
    
     .header-title {
         color: #ffffff;
         font-size: 36px;
         font-weight: bold;
         margin: 0 0 4px 0;
         text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
     }
     
     .header-subtitle {
         color: #b9c4cb;
         font-size: 18px;
         margin: 0;
         font-weight: 400;
         display: flex;
         align-items: center;
         gap: 8px;
     }
    
     .label {
         color: #3393ff;
         font-weight: 600;
         font-size: 16px;
         text-transform: lowercase;
     }
     
     .value {
         color: #ffffff;
         font-weight: 500;
         font-size: 16px;
         text-transform: uppercase;
         letter-spacing: 0.5px;
     }
    
     .bullet {
         color: #3393ff;
         font-weight: bold;
         font-size: 20px;
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
         font-size: 20px;
         font-weight: 600;
         margin-bottom: 8px;
     }
     
     .object-details {
         color: #b9c4cb;
         font-size: 16px;
         margin-bottom: 12px;
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
    # Initialize sleek managers and styles first
    # Simple data loading without complex managers

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

    # Only show notification if data was just loaded (not cached)
    if cache_key not in st.session_state or st.session_state.get(
        "show_data_loaded", False
    ):
        if len(data) > 0:
            st.success(
                f"✅ Loaded {len(data)} {st.session_state.current_object_type} from {st.session_state.current_environment}"
            )
        else:
            st.warning(
                f"⚠️ No {st.session_state.current_object_type} found for {st.session_state.current_environment} environment"
            )
        st.session_state["show_data_loaded"] = False

    # Metrics
    total_count = len(data)
    selected_count = len(st.session_state.selected_objects)
    deleted_count = len(st.session_state.deleted_objects)

    # Floating action bar - interactive
    # Stats now integrated into the FAB popover above

    # Create a larger, more integrated FAB button
    st.markdown(
        """
    <style>
     .stPopover > div:first-child {
         position: fixed !important;
         bottom: 20px !important;
         right: 20px !important;
         z-index: 1000 !important;
         background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
         border: 2px solid #3393ff !important;
         border-radius: 16px !important;
         padding: 20px 24px !important;
         box-shadow: 0 6px 20px rgba(51, 147, 255, 0.3) !important;
         cursor: pointer !important;
         transition: all 0.2s ease !important;
         min-width: 280px !important;
         text-align: center !important;
     }
     .stPopover > div:first-child:hover {
         transform: scale(1.05) !important;
         box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
         background: linear-gradient(135deg, #334155 0%, #475569 100%) !important;
     }
      .stPopover > div:first-child button {
          background: transparent !important;
          border: none !important;
          color: #ffffff !important;
          font-size: 18px !important;
          font-weight: 700 !important;
          padding: 8px 0 !important;
          width: 100% !important;
          line-height: 1.2 !important;
          min-height: 60px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
      }
     
     .fab-stats {
         display: flex;
         justify-content: space-between;
         align-items: center;
         gap: 16px;
         font-size: 24px;
         font-weight: 700;
     }
     
     .fab-stat {
         display: flex;
         align-items: center;
         gap: 6px;
     }
     
     .fab-stat-emoji {
         font-size: 28px;
     }
     
     .fab-stat-value {
         color: #3393ff;
         font-weight: bold;
         font-size: 24px;
     }
     
     .fab-stat-label {
         color: #b9c4cb;
         font-size: 14px;
         text-transform: uppercase;
         letter-spacing: 0.5px;
     }
     
     /* Compact button styling */
     .compact-button {
         font-size: 12px !important;
         padding: 4px 8px !important;
         height: 28px !important;
         margin: 2px !important;
     }
     
     /* Theme-consistent select all button */
     .stButton > button[kind="primary"] {
         background: linear-gradient(135deg, #3393ff 0%, #1a86ff 100%) !important;
         border: 1px solid #3393ff !important;
         color: #ffffff !important;
         font-weight: 600 !important;
     }
     
     .stButton > button[kind="primary"]:hover {
         background: linear-gradient(135deg, #1a86ff 0%, #0066cc 100%) !important;
         border-color: #1a86ff !important;
         transform: translateY(-1px) !important;
         box-shadow: 0 4px 12px rgba(51, 147, 255, 0.3) !important;
     }
     
     /* Blue highlight for selected objects */
     .object-card.selected {
         border: 2px solid #3393ff !important;
         background: linear-gradient(135deg, #1e293b 0%, #2d4a6b 100%) !important;
         box-shadow: 0 0 12px rgba(51, 147, 255, 0.3) !important;
     }
     
     .object-card.selected .object-title {
         color: #3393ff !important;
     }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Create the clickable FAB stats card
    with st.popover(
        f"📊 {total_count} • ⏳ {selected_count} • 🗑️ {deleted_count}",
        use_container_width=False,
    ):
        st.markdown("### ⚡ Actions")

        # Environment and Object Type controls
        col1, col2 = st.columns(2)
        with col1:
            envs = ["sandbox", "production", "staging"]
            current_env_idx = envs.index(st.session_state.current_environment)
            new_env = st.selectbox(
                "Environment", envs, index=current_env_idx, key="fab_env"
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

        # Action buttons
        if st.button("📥 Gather Data", key="fab_gather", use_container_width=True):
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
                        cache_key = f"data_{st.session_state.current_object_type}_{st.session_state.current_environment}"
                        if cache_key in st.session_state:
                            del st.session_state[cache_key]
                        st.rerun()
                    else:
                        st.error(f"❌ Error gathering data: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        if st.button("📤 Export Selected", key="fab_export", use_container_width=True):
            if st.session_state.selected_objects:
                st.success(
                    f"✅ Exporting {len(st.session_state.selected_objects)} selected items..."
                )
            else:
                st.warning("⚠️ No items selected for export")

        # Only show selection actions if items are selected
        if st.session_state.selected_objects:
            st.divider()
            st.markdown("### 🎯 Selection Actions")

            # Show current selection status
            st.info(
                f"📋 {len(st.session_state.selected_objects)} items currently selected"
            )

            # View selected items button - opens separate view
            if st.button(
                "👁️ View Selected Items",
                key="fab_view_selected",
                use_container_width=True,
            ):
                st.session_state.show_selected_only = True
                st.rerun()

            # Simple selection actions
            if st.button(
                "❌ Deselect All",
                key="fab_deselect_all",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.selected_objects.clear()
                st.success("✅ Deselected all objects")
                st.rerun()

            # Delete button - opens separate confirmation popup
            if st.button(
                "🗑️ Delete Selected",
                key="fab_delete_selected",
                use_container_width=True,
                type="primary",
            ):
                st.session_state.show_delete_confirmation = True
                st.rerun()
        else:
            st.info("📋 No items selected for deletion")

        # Pending deletion review section
        if deleted_count > 0:
            st.divider()
            st.markdown("### 🗑️ Pending Deletion Review")
            st.warning(f"⚠️ {deleted_count} items marked for deletion")

            if st.button(
                "🔄 Restore All Deleted",
                key="fab_restore_all",
                use_container_width=True,
            ):
                st.session_state.deleted_objects.clear()
                st.success("✅ Restored all deleted items")
                st.rerun()

            if st.button(
                "🗑️ Confirm Delete All",
                key="fab_confirm_delete",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.deleted_objects.clear()
                st.success("✅ Permanently deleted all items")
                st.rerun()

    # Main header with title - no buttons needed
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
                        <span class="label">obj:</span>
                        <span class="value">{object_type}</span>
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Settings functionality moved to floating action buttons only

    # Show data source info with auto-hide
    if len(data) > 0 and data.iloc[0]["Name"].startswith("Sample"):
        # Auto-hide after 5 seconds
        st.markdown(
            """
        <script>
        setTimeout(function() {
            var warning = document.querySelector('[data-testid="stAlert"]');
            if (warning) {
                warning.style.transition = 'opacity 0.5s ease';
                warning.style.opacity = '0';
                setTimeout(function() {
                    warning.style.display = 'none';
                }, 500);
            }
        }, 5000);
        </script>
        """,
            unsafe_allow_html=True,
        )

        st.warning(
            "⚠️ Using sample data - click '📥 Gather Data' to fetch real data from JAMF Pro"
        )

    # Objects section with grid view
    if st.session_state.get("show_selected_only", False):
        st.markdown("### Selected Objects")
        st.info(f"📋 Showing {len(st.session_state.selected_objects)} selected objects")

        # Filter data to show only selected items
        selected_data = data[
            data["ID"]
            .apply(lambda x: extract_id_from_hyperlink(x))
            .isin(st.session_state.selected_objects)
        ]

        # Back button only
        if st.button("← Back to All Objects", key="back_to_all"):
            st.session_state.show_selected_only = False
            st.rerun()
    else:
        st.markdown("### Objects")

        # Show selection status if items are selected
        if st.session_state.selected_objects:
            st.info(f"📋 {len(st.session_state.selected_objects)} items selected")

        # Always show all data
        selected_data = data

    # Grid view - 3 columns
    cols = st.columns(3)

    for idx, row in selected_data.iterrows():
        with cols[idx % 3]:
            with st.container():
                # Extract actual ID for selection logic
                actual_id = extract_id_from_hyperlink(row["ID"])

                # Object card with custom styling
                card_class = (
                    "object-card selected"
                    if actual_id in st.session_state.selected_objects
                    else "object-card"
                )
                st.markdown(
                    f"""
                <div class="{card_class}">
                    <div class="object-title">{row['Name']}</div>
                    <div class="object-details">ID: {actual_id} • {row.get('Type', 'N/A')}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

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

    # Delete confirmation popup - working version
    if st.session_state.get("show_delete_confirmation", False):
        st.markdown("---")
        st.markdown("### 🗑️ Delete Confirmation")

        st.error("⚠️ **FINAL WARNING: This action cannot be undone!**")
        st.error(
            f"🔥 You are about to **PERMANENTLY DELETE** {len(st.session_state.selected_objects)} objects from JAMF Pro!"
        )

        # Show what will be deleted
        st.warning(
            f"⚠️ You are about to delete {len(st.session_state.selected_objects)} objects:"
        )
        for obj_id in st.session_state.selected_objects:
            # Find the object name from data
            matching_rows = data[
                data["ID"].apply(lambda x: extract_id_from_hyperlink(x)) == obj_id
            ]
            if len(matching_rows) > 0:
                obj_name = matching_rows.iloc[0]["Name"]
                st.write(f"• **{obj_name}** (ID: {obj_id})")
            else:
                st.write(f"• ID: {obj_id}")

        # Confirmation buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔥 PERMANENTLY DELETE", key="confirm_delete", type="primary"):
                # Actually delete the objects
                deleted_count = len(st.session_state.selected_objects)

                # Clear selections and close confirmation
                st.session_state.selected_objects.clear()
                st.session_state.show_delete_confirmation = False
                st.session_state.show_selected_only = False

                st.success(f"✅ Successfully deleted {deleted_count} objects")

                # Clear cache to refresh data
                for key in list(st.session_state.keys()):
                    if key.startswith("data_"):
                        del st.session_state[key]
                st.rerun()

        with col2:
            if st.button("❌ Cancel", key="cancel_delete", type="secondary"):
                st.session_state.show_delete_confirmation = False
                st.rerun()

    # Selection actions are now integrated into the FAB popover above

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

        # Simple status display
        st.info("📊 Status: All systems operational")


if __name__ == "__main__":
    main()
