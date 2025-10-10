#!/usr/bin/env python3
"""
Clean Grid Viewer - Elegant Apple-style interface
Simple, elegant grid view with minimal wasted space
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

st.set_page_config(
    page_title="JAMF Pro Manager",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Clean, minimal styling
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
    
    /* Clean dark theme */
    .stApp {
        background: #0a0a0a;
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }
    
    /* Better stats buttons */
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
    
    /* Elegant grid cards */
    .grid-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 8px 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        backdrop-filter: blur(20px);
        user-select: none;
    }
    
    .grid-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .grid-card.selected {
        background: rgba(255, 193, 7, 0.15);
        border-color: #ffc107;
        box-shadow: 0 0 0 1px rgba(255, 193, 7, 0.3);
    }
    
    .grid-card.deleted {
        background: rgba(220, 53, 69, 0.15);
        border-color: #dc3545;
        box-shadow: 0 0 0 1px rgba(220, 53, 69, 0.3);
    }
    
    /* Hide the invisible buttons */
    .stButton > button[data-testid*="card_"] {
        display: none !important;
    }
    
    /* Action buttons */
    .action-btn {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 12px 24px;
        color: #ffffff;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.2s ease;
        cursor: pointer;
        width: 100%;
    }
    
    .action-btn:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
        transform: translateY(-1px);
    }
    
    .action-btn.primary {
        background: #ffc107;
        border-color: #ffc107;
        color: #000000;
    }
    
    .action-btn.primary:hover {
        background: #ffb300;
        border-color: #ffb300;
    }
    
    /* Clean typography */
    .card-title {
        font-size: 16px;
        font-weight: 600;
        margin: 0 0 8px 0;
        color: #ffffff;
    }
    
    .card-subtitle {
        font-size: 13px;
        color: rgba(255, 255, 255, 0.7);
        margin: 0 0 4px 0;
    }
    
    .card-meta {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.5);
        margin: 0;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 500;
        margin-top: 8px;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "selected_objects" not in st.session_state:
    st.session_state.selected_objects = set()
if "deleted_objects" not in st.session_state:
    st.session_state.deleted_objects = set()

# Header
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0; color: #ffffff;">🍎 jpapi manager</h1>
        <p style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.7); margin: 0.5rem 0 0 0;">elegant object management</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Create sample data
sample_data = pd.DataFrame(
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
            "macOS 14 Base Level Apps - Crowdstrike",
            "macOS 12 + Netskope + Tenable",
            "macOS 14 Base Level Apps - Netskope",
            "macOS 12 + Tenable v10+",
        ],
        "ID": [155, 35, 162, 37, 165, 36, 164, 13, 155, 35, 162, 37],
        "Type": [
            "Static",
            "Smart",
            "Static",
            "Smart",
            "Static",
            "Smart",
            "Static",
            "Static",
            "Static",
            "Smart",
            "Static",
            "Smart",
        ],
    }
)

# Better stats buttons
selected_count = len(st.session_state.selected_objects)
deleted_count = len(st.session_state.deleted_objects)
active_count = len(sample_data) - deleted_count

st.markdown(
    f"""
    <div class="stats-container">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
            <div class="stat-item">
                <div class="stat-number">{len(sample_data)}</div>
                <div class="stat-label">total</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{selected_count}</div>
                <div class="stat-label">selected</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{deleted_count}</div>
                <div class="stat-label">deleted</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{active_count}</div>
                <div class="stat-label">active</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Grid view
st.markdown("### Advanced Searches")
st.markdown("Click cards to select for deletion")

# Create 4-column grid
cols = st.columns(4)

for index, row in sample_data.iterrows():
    object_id = f"obj_{index}"
    is_selected = object_id in st.session_state.selected_objects
    is_deleted = object_id in st.session_state.deleted_objects

    # Determine which column to use
    col_index = index % 4
    with cols[col_index]:
        # Card styling
        card_class = "grid-card"
        if is_deleted:
            card_class += " deleted"
        elif is_selected:
            card_class += " selected"

        # Status badge
        if is_deleted:
            status_badge = '<span class="status-badge status-deleted">🗑️ Deleted</span>'
        elif is_selected:
            status_badge = (
                '<span class="status-badge status-selected">⚠️ Selected</span>'
            )
        else:
            status_badge = '<span class="status-badge status-active">✅ Active</span>'

        # Render clickable card content
        st.markdown(
            f"""
            <div class="{card_class}" onclick="selectCard('{object_id}')">
                <div class="card-title">{row['Name']}</div>
                <div class="card-subtitle">ID: {row['ID']}</div>
                <div class="card-meta">Type: {row['Type']}</div>
                {status_badge}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Hidden button for Streamlit callback
        if st.button(
            "",
            key=f"card_{object_id}",
            help="Click to select for deletion",
            type="primary" if is_selected else "secondary",
        ):
            if object_id in st.session_state.selected_objects:
                st.session_state.selected_objects.remove(object_id)
            else:
                st.session_state.selected_objects.add(object_id)
            st.rerun()

# Action buttons
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("🗑️ Delete Selected", type="primary", use_container_width=True):
        if st.session_state.selected_objects:
            st.session_state.deleted_objects.update(st.session_state.selected_objects)
            st.session_state.selected_objects.clear()
            st.rerun()
        else:
            st.warning("No items selected")

with col2:
    if st.button("🔄 Clear All", use_container_width=True):
        st.session_state.selected_objects.clear()
        st.session_state.deleted_objects.clear()
        st.rerun()

with col3:
    st.info(
        f"**{len(st.session_state.selected_objects)}** selected • **{len(st.session_state.deleted_objects)}** deleted"
    )

# JavaScript for card clicks
st.markdown(
    """
    <script>
    function selectCard(objectId) {
        // Find the corresponding hidden button and click it
        const buttons = document.querySelectorAll('button[data-testid*="card_"]');
        for (let button of buttons) {
            if (button.getAttribute('data-testid').includes(objectId)) {
                button.click();
                break;
            }
        }
    }
    
    // Make sure cards are clickable
    document.addEventListener('DOMContentLoaded', function() {
        const cards = document.querySelectorAll('.grid-card');
        cards.forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function(e) {
                e.preventDefault();
                const objectId = this.getAttribute('onclick').match(/'([^']+)'/)[1];
                selectCard(objectId);
            });
        });
    });
    </script>
    """,
    unsafe_allow_html=True,
)
