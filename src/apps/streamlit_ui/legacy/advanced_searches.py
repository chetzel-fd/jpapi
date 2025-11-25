#!/usr/bin/env python3
"""
Advanced Search Viewer - Sleek Visual Interface
Clean, intuitive interface for managing JAMF Pro advanced searches
"""
import streamlit as st
import pandas as pd
import sys
import os
import subprocess
from datetime import datetime
from typing import Dict, Any
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import numpy as np

# Add src directory to path for authentication
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

try:
    from core.auth.login_factory import get_best_auth

    LIBS_AVAILABLE = True
except ImportError as e:
    st.sidebar.error(f"⚠️ JAMF authentication libraries not found: {e}")
    st.sidebar.info("📋 Running in demo mode")
    LIBS_AVAILABLE = False

    def get_best_auth(environment="prod"):
        return None


# Sleek page config
st.set_page_config(
    page_title="Advanced Search Viewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# DaisyUI-powered interface with Tailwind CSS
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            daisyui: {
                themes: ["dark", "light", "cupcake", "bumblebee", "emerald", "corporate", "synthwave", "retro", "cyberpunk", "valentine", "halloween", "garden", "forest", "aqua", "lofi", "pastel", "fantasy", "wireframe", "black", "luxury", "dracula", "cmyk", "autumn", "business", "acid", "lemonade", "night", "coffee", "winter"],
            },
        }
    </script>
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main > div {
        padding-top: 1rem;
        max-width: none !important;
    }
    
    /* Clean DaisyUI interface */
    .stApp {
        @apply bg-base-100 text-base-content;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }
    
    /* Clean typography */
    .stMarkdown h1 {
        @apply text-3xl font-bold mb-6;
    }
    
    .stMarkdown h2 {
        @apply text-2xl font-semibold mb-4;
    }
    
    .stMarkdown h3 {
        @apply text-xl font-semibold mb-3;
    }
    
    /* Clean button styling */
    .stButton > button {
        @apply btn btn-sm w-full;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        @apply btn-primary;
        transform: translateY(-1px);
    }
    
    /* State-specific styling */
    .stButton > button.pending-state {
        @apply btn-warning;
    }
    
    .stButton > button.deleted-state,
    .stButton > button:disabled {
        @apply btn-error opacity-60;
    }
    
    /* Clean card styling */
    .search-card {
        @apply card bg-base-200 shadow-sm border border-base-300;
        transition: all 0.2s ease;
    }
    
    .search-card:hover {
        @apply shadow-md;
        transform: translateY(-2px);
    }
    
    /* Clean stats */
    .stats-section {
        @apply stats stats-horizontal shadow-sm bg-base-200 border border-base-300;
    }
    
    .stat-item {
        @apply stat;
    }
    
    .stat-value {
        @apply text-2xl font-bold;
    }
    
    .stat-title {
        @apply text-sm opacity-70;
    }
    
    /* Clean alerts */
    .alert-section {
        @apply alert shadow-sm;
    }
    
    /* Clean modals */
    .modal-section {
        @apply modal modal-open;
    }
    
    .modal-box {
        @apply bg-base-100 border border-base-300;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .stats-section {
            @apply stats-vertical;
        }
    }
    </style>
    
    <script>
    // Add DaisyUI state classes to buttons
    function addDaisyUIStateClasses() {
        const buttons = document.querySelectorAll('.stButton > button');
        buttons.forEach(button => {
            // Remove existing state classes
            button.classList.remove('pending-state', 'deleted-state');
            
            // Add appropriate DaisyUI state class
            if (button.textContent.includes('⚠️')) {
                button.classList.add('pending-state');
            } else if (button.textContent.includes('🗑️')) {
                button.classList.add('deleted-state');
            }
        });
    }
    
    // Run on page load and after Streamlit updates
    document.addEventListener('DOMContentLoaded', addDaisyUIStateClasses);
    window.addEventListener('load', addDaisyUIStateClasses);
    
    // Also run after Streamlit reruns
    const observer = new MutationObserver(addDaisyUIStateClasses);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """,
    unsafe_allow_html=True,
)


def load_csv_data(environment="dev") -> pd.DataFrame:
    """Load data from the most recent CSV export file using new export utilities"""
    import glob

    # Try to use new export utilities first
    try:
        from lib.exports.export_utils import (
            get_export_file_pattern,
            get_export_directory,
        )

        # Use new export utilities
        csv_dir = get_export_directory(environment)
        pattern = get_export_file_pattern("advanced-searches", "csv", environment)
        csv_files = list(csv_dir.glob(pattern))

        if not csv_files:
            st.warning(
                f"No advanced searches CSV files found for {environment} environment"
            )
            return pd.DataFrame()

    except ImportError:
        # Fallback to old method
        csv_pattern = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "storage",
            "data",
            "csv-exports",
            "*-advanced-searches-export-*.csv",
        )
        csv_files = glob.glob(csv_pattern)

        if not csv_files:
            st.error(
                "No advanced searches CSV files found in storage/data/csv-exports/"
            )
            return pd.DataFrame()

    # Get the most recent file
    latest_file = max(csv_files, key=os.path.getctime)

    try:
        df = pd.read_csv(latest_file)
        instance_prefix = environment if environment != "dev" else "sandbox"
        st.success(
            f"📊 Loaded {len(df)} advanced searches from {os.path.basename(latest_file)} ({instance_prefix} environment)"
        )
        return df
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()


def initialize_session_state():
    """Initialize session state variables"""
    if "marked_for_deletion" not in st.session_state:
        st.session_state.marked_for_deletion = set()
    if "deleted_items" not in st.session_state:
        st.session_state.deleted_items = set()
    if "deletion_log" not in st.session_state:
        st.session_state.deletion_log = []
    if "search_filters" not in st.session_state:
        st.session_state.search_filters = {
            "name_filter": "",
            "type_filter": "all",
            "smart_filter": "all",
        }
    if "deletion_results" not in st.session_state:
        st.session_state.deletion_results = []


def render_search_card(row, index):
    """Render clean DaisyUI search card matching the professional style"""
    search_id = f"search_{index}"
    is_marked = search_id in st.session_state.marked_for_deletion
    is_deleted = search_id in st.session_state.deleted_items

    # Clean card styling based on state
    if is_deleted:
        card_class = "card bg-base-200 shadow-sm border border-base-300 opacity-60"
        badge_class = "badge badge-error badge-sm"
        badge_text = "DELETED"
    elif is_marked:
        card_class = "card bg-warning/5 shadow-sm border border-warning/20"
        badge_class = "badge badge-warning badge-sm"
        badge_text = "PENDING"
    else:
        card_class = "card bg-base-200 shadow-sm border border-base-300 hover:shadow-md transition-all duration-200"
        badge_class = "badge badge-primary badge-sm"
        badge_text = "ACTIVE"

    # Clean card layout
    st.markdown(
        f"""
        <div class="{card_class}">
            <div class="card-body p-4">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="card-title text-base font-semibold">{row['Name']}</h3>
                    <div class="{badge_class}">{badge_text}</div>
                </div>
                
                <div class="text-sm text-base-content/70 mb-3">
                    <p>ID: {row['ID']} • {row['Type']} • {'Smart' if row['Smart'] == 'TRUE' else 'Static'}</p>
                </div>
                
                <div class="card-actions justify-end">
                    <button class="btn btn-xs btn-outline" onclick="toggleSearch('{search_id}')">
                        {f"Unmark" if is_marked else "Mark"}
                    </button>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Handle button clicks for non-deleted items
    if not is_deleted:
        if st.button(
            f"{'Unmark' if is_marked else 'Mark'}",
            key=f"action_{search_id}",
            help=f"Click to {'unmark' if is_marked else 'mark'} for deletion",
            use_container_width=True,
        ):
            if search_id in st.session_state.marked_for_deletion:
                st.session_state.marked_for_deletion.remove(search_id)
            else:
                st.session_state.marked_for_deletion.add(search_id)
            st.rerun()

        # Detailed view
        if st.session_state.get(f"show_details_{search_id}", False):
            with st.expander("Detailed Information", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Basic Info:**")
                    st.write(f"• ID: {row['ID']}")
                    st.write(f"• Name: {row['Name']}")
                    st.write(f"• Type: {row['Type']}")
                    st.write(f"• Smart: {row['Smart']}")

                with col2:
                    st.markdown("**Criteria Details:**")
                    st.write(
                        f"• Criteria: {row['Criteria'] if pd.notna(row['Criteria']) else 'None'}"
                    )
                    st.write(
                        f"• Delete Status: {'Marked' if is_marked else 'Not marked'}"
                    )

        st.markdown("</div>", unsafe_allow_html=True)


def render_stats(df):
    """Render statistics overview"""
    total_searches = len(df)
    marked_count = len(st.session_state.marked_for_deletion)
    smart_count = len(df[df["Smart"] == "TRUE"])

    # Clean stats overview
    st.markdown("### Search Overview")

    st.markdown(
        f"""
        <div class="stats stats-horizontal shadow-sm bg-base-200 border border-base-300">
            <div class="stat">
                <div class="stat-title">Total</div>
                <div class="stat-value text-primary">{total_searches}</div>
            </div>
            <div class="stat">
                <div class="stat-title">Smart</div>
                <div class="stat-value text-secondary">{smart_count}</div>
            </div>
            <div class="stat">
                <div class="stat-title">Static</div>
                <div class="stat-value text-accent">{len(df[df["Smart"] == "FALSE"])}</div>
            </div>
            <div class="stat">
                <div class="stat-title">Pending</div>
                <div class="stat-value text-warning">{marked_count}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_filters():
    """Render filter controls"""
    st.sidebar.markdown("### 🔍 Filters")

    # Name filter
    name_filter = st.sidebar.text_input(
        "Search Name Contains", value=st.session_state.search_filters["name_filter"]
    )
    st.session_state.search_filters["name_filter"] = name_filter

    # Type filter
    type_filter = st.sidebar.selectbox(
        "Search Type",
        ["all", "Unknown"],
        index=["all", "Unknown"].index(st.session_state.search_filters["type_filter"]),
    )
    st.session_state.search_filters["type_filter"] = type_filter

    # Smart filter
    smart_filter = st.sidebar.selectbox(
        "Smart Search",
        ["all", "TRUE", "FALSE"],
        index=["all", "TRUE", "FALSE"].index(
            st.session_state.search_filters["smart_filter"]
        ),
    )
    st.session_state.search_filters["smart_filter"] = smart_filter


def apply_filters(df):
    """Apply filters to data"""
    filtered_df = df.copy()
    filters = st.session_state.search_filters

    # Name filter
    if filters["name_filter"]:
        filtered_df = filtered_df[
            filtered_df["Name"].str.contains(
                filters["name_filter"], case=False, na=False
            )
        ]

    # Type filter
    if filters["type_filter"] != "all":
        filtered_df = filtered_df[filtered_df["Type"] == filters["type_filter"]]

    # Smart filter
    if filters["smart_filter"] != "all":
        filtered_df = filtered_df[filtered_df["Smart"] == filters["smart_filter"]]

    return filtered_df


def execute_deletions(df):
    """Execute actual deletions using jpapi commands"""
    if not st.session_state.marked_for_deletion:
        st.warning("No searches marked for deletion")
        return

    # Get project root
    project_root = os.path.join(os.path.dirname(__file__), "..", "..")
    venv_python = os.path.join(project_root, "venv", "bin", "python")

    if not os.path.exists(venv_python):
        st.error("Virtual environment not found. Cannot execute deletions.")
        return

    # Create deletion list
    deletion_data = []
    search_ids_to_delete = []

    for marked_id in st.session_state.marked_for_deletion:
        index = int(marked_id.split("_")[1])
        if index < len(df):
            row = df.iloc[index]
            search_ids_to_delete.append(str(row["ID"]))
            deletion_data.append(
                {
                    "ID": row["ID"],
                    "Name": row["Name"],
                    "Type": row["Type"],
                    "Smart": row["Smart"],
                    "Criteria": row["Criteria"],
                }
            )

    if not search_ids_to_delete:
        st.error("No valid searches found for deletion")
        return

    # Show confirmation
    st.markdown("### ⚠️ Deletion Confirmation")
    st.markdown(f"**{len(search_ids_to_delete)} searches will be deleted:**")

    for item in deletion_data:
        st.write(f"• {item['Name']} (ID: {item['ID']})")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Confirm Deletion", type="primary"):
            execute_deletion_commands(
                search_ids_to_delete, deletion_data, venv_python, project_root
            )

    with col2:
        if st.button("❌ Cancel", type="secondary"):
            st.session_state.marked_for_deletion.clear()
            st.rerun()


def execute_deletion_commands(search_ids, deletion_data, venv_python, project_root):
    """Execute the actual deletion commands"""
    results = []
    success_count = 0
    error_count = 0

    with st.spinner("Executing deletions..."):
        for i, search_id in enumerate(search_ids):
            try:
                # Use jpapi command to delete advanced search
                cmd = [
                    venv_python,
                    "-m",
                    "src.cli.main",
                    "advanced-searches",
                    "delete",
                    search_id,
                    "--force",
                ]

                result = subprocess.run(
                    cmd, cwd=project_root, capture_output=True, text=True, timeout=30
                )

                if result.returncode == 0:
                    results.append(
                        {
                            "ID": search_id,
                            "Name": deletion_data[i]["Name"],
                            "Status": "✅ Success",
                            "Message": "Deleted successfully",
                        }
                    )
                    success_count += 1
                else:
                    results.append(
                        {
                            "ID": search_id,
                            "Name": deletion_data[i]["Name"],
                            "Status": "❌ Error",
                            "Message": result.stderr or "Unknown error",
                        }
                    )
                    error_count += 1

            except subprocess.TimeoutExpired:
                results.append(
                    {
                        "ID": search_id,
                        "Name": deletion_data[i]["Name"],
                        "Status": "⏰ Timeout",
                        "Message": "Command timed out",
                    }
                )
                error_count += 1
            except Exception as e:
                results.append(
                    {
                        "ID": search_id,
                        "Name": deletion_data[i]["Name"],
                        "Status": "❌ Error",
                        "Message": str(e),
                    }
                )
                error_count += 1

    # Store results
    st.session_state.deletion_results = results

    # Move successfully deleted items from marked to deleted
    for i, search_id in enumerate(search_ids):
        if i < len(results) and "Success" in results[i]["Status"]:
            # Move from marked to deleted
            if search_id in st.session_state.marked_for_deletion:
                st.session_state.marked_for_deletion.remove(search_id)
            st.session_state.deleted_items.add(search_id)

            # Add to deletion log
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "DELETED",
                "id": search_id,
                "name": deletion_data[i]["Name"],
                "type": deletion_data[i]["Type"],
            }
            st.session_state.deletion_log.append(log_entry)

    # Show results
    st.markdown("### 🗑️ Deletion Results")

    if success_count > 0:
        st.success(f"✅ Successfully deleted {success_count} searches")
        st.balloons()

    if error_count > 0:
        st.error(f"❌ Failed to delete {error_count} searches")

    # Show detailed results
    if results:
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)

    st.rerun()


def export_deletion_list(df):
    """Export list of searches marked for deletion"""
    if not st.session_state.marked_for_deletion:
        st.warning("No searches marked for deletion")
        return

    # Create deletion list
    deletion_data = []

    for marked_id in st.session_state.marked_for_deletion:
        index = int(marked_id.split("_")[1])
        if index < len(df):
            row = df.iloc[index]
            deletion_data.append(
                {
                    "ID": row["ID"],
                    "Name": row["Name"],
                    "Type": row["Type"],
                    "Smart": row["Smart"],
                    "Criteria": row["Criteria"],
                    "delete": "DELETE",
                    "delete_reason": f'Marked for deletion on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                }
            )

    if deletion_data:
        # Convert to DataFrame
        df_deletion = pd.DataFrame(deletion_data)

        # Create download button
        csv = df_deletion.to_csv(index=False)
        st.download_button(
            label="📥 Download Deletion List (CSV)",
            data=csv,
            file_name=f"advanced_searches_deletion_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

        # Show preview
        st.markdown("### 📋 Deletion List Preview")
        st.dataframe(df_deletion, use_container_width=True)


def create_bubble_chart(df):
    """Create an interactive bubble chart from search data"""
    if df.empty:
        return None

    # Extract words from search names and count frequency
    all_words = []
    for name in df["Name"].dropna():
        # Split by common separators and clean words
        words = name.replace("-", " ").replace("_", " ").replace("+", " ").split()
        all_words.extend([word.lower() for word in words if len(word) > 2])

    # Count word frequency
    word_counts = Counter(all_words)

    # Get top words (limit to 50 for readability)
    top_words = dict(word_counts.most_common(50))

    if not top_words:
        return None

    # Create bubble chart data
    words = list(top_words.keys())
    counts = list(top_words.values())

    # Calculate bubble sizes (normalize to reasonable range)
    max_count = max(counts)
    bubble_sizes = [int(20 + (count / max_count) * 80) for count in counts]

    # Create random positions for better distribution
    np.random.seed(42)  # For consistent positioning
    x_positions = np.random.uniform(0, 100, len(words))
    y_positions = np.random.uniform(0, 100, len(words))

    # Create the bubble chart
    fig = go.Figure()

    # Add bubbles
    fig.add_trace(
        go.Scatter(
            x=x_positions,
            y=y_positions,
            mode="markers+text",
            marker=dict(
                size=bubble_sizes,
                color=counts,
                colorscale="Viridis",
                colorbar=dict(title="Frequency"),
                line=dict(width=2, color="rgba(0, 122, 255, 0.3)"),
                opacity=0.8,
            ),
            text=words,
            textposition="middle center",
            textfont=dict(size=10, color="white", family="Arial Black"),
            hovertemplate="<b>%{text}</b><br>Frequency: %{marker.color}<br><extra></extra>",
            name="Search Terms",
        )
    )

    # Update layout for dark theme
    fig.update_layout(
        title=dict(
            text="🔍 Advanced Search Terms Bubble Chart",
            font=dict(size=20, color="white"),
            x=0.5,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
        showlegend=False,
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return fig


def main():
    """Main application function"""
    initialize_session_state()

    # Central container for organic flow
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Header with organic glow
    st.markdown(
        """
    <div class="main-header">
        <h1>🔍 Advanced Search Viewer</h1>
        <p>Sleek visual interface for managing JAMF Pro advanced searches</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Environment selection in sidebar
    with st.sidebar:
        st.markdown("### 🌍 Environment")
        environment = st.selectbox(
            "Select Environment",
            ["dev", "staging", "prod"],
            index=0,
            help="Choose the JAMF Pro environment (configure URLs via environment variables)",
        )

        # Show instance prefix
        try:
            from lib.exports.export_utils import get_instance_prefix

            instance_prefix = get_instance_prefix(environment)
            st.info(f"Instance: {instance_prefix}")
        except ImportError:
            st.info(f"Environment: {environment}")

    # Load data
    df = load_csv_data(environment)

    if df.empty:
        st.error("No data loaded. Please check the CSV file path.")
        return

    # Render filters
    render_filters()

    # Render stats
    render_stats(df)

    # Bubble chart visualization
    if not df.empty:
        st.markdown("---")
        st.markdown("### 🌟 Search Terms Bubble Chart")

        # Create bubble chart
        bubble_fig = create_bubble_chart(df)
        if bubble_fig:
            st.plotly_chart(bubble_fig, use_container_width=True)
        else:
            st.info("Unable to generate bubble chart from search data")

    # Apply filters
    filtered_df = apply_filters(df)

    # Main content area
    if filtered_df.empty:
        st.info("No searches match the current filters")
        return

    # Render searches with advanced DaisyUI layout
    st.markdown(f"### Advanced Searches ({len(filtered_df)})")

    # Create modern card grid layout
    st.markdown(
        '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">',
        unsafe_allow_html=True,
    )

    for index, row in filtered_df.iterrows():
        render_search_card(row, index)

    st.markdown("</div>", unsafe_allow_html=True)

    # Clean deletion management
    if st.session_state.marked_for_deletion:
        st.markdown("---")
        st.markdown("### Deletion Management")

        # Clean alert
        st.markdown(
            f"""
            <div class="alert alert-warning shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
                <div>
                    <h3 class="font-bold">Warning!</h3>
                    <div class="text-xs">{len(st.session_state.marked_for_deletion)} items marked for deletion</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Clean action buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("Delete Selected", type="primary", use_container_width=True):
                st.session_state.deletion_confirmation = True
                st.rerun()

        with col2:
            if st.button("Clear All", type="secondary", use_container_width=True):
                st.session_state.marked_for_deletion.clear()
                st.rerun()

        with col3:
            if st.button("Export List", use_container_width=True):
                export_deletion_list(df)

        # Clean confirmation
        if st.session_state.get("deletion_confirmation", False):
            st.markdown(
                """
                <div class="modal modal-open">
                    <div class="modal-box bg-base-100 border border-base-300">
                        <h3 class="font-bold text-lg text-error">Confirm Deletion</h3>
                        <p class="py-4">This action cannot be undone! Are you sure?</p>
                        <div class="modal-action">
                            <button class="btn btn-error btn-sm">Delete</button>
                            <button class="btn btn-ghost btn-sm">Cancel</button>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button(
                    "Confirm Delete", type="primary", use_container_width=True
                ):
                    execute_deletions(df)
                    st.session_state.deletion_confirmation = False
                    st.rerun()

            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.deletion_confirmation = False
                    st.rerun()

        # Execute deletions
        execute_deletions(df)

    # Show deletion log
    if st.session_state.deletion_log:
        st.markdown("---")
        st.markdown("### 📋 Deletion Log")

        # Create log dataframe
        log_df = pd.DataFrame(st.session_state.deletion_log)

        # Display log with styling
        st.dataframe(log_df, use_container_width=True)

        # Show summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Deleted", len(st.session_state.deleted_items))
        with col2:
            st.metric("Pending Deletion", len(st.session_state.marked_for_deletion))
        with col3:
            st.metric(
                "Active Items",
                len(filtered_df)
                - len(st.session_state.deleted_items)
                - len(st.session_state.marked_for_deletion),
            )

    # Show previous deletion results if any
    if st.session_state.deletion_results:
        st.markdown("---")
        st.markdown("### 📊 Previous Deletion Results")
        results_df = pd.DataFrame(st.session_state.deletion_results)
        st.dataframe(results_df, use_container_width=True)

    # Close central container
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
