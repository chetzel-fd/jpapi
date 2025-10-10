import streamlit as st
import pandas as pd


class UIComponents:
    @staticmethod
    def apply_styling():
        """Apply the Design #4 Hybrid Navigation styling"""
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
            
            /* Global Styles */
            .stApp {
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
                color: #ffffff;
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            }
            
            /* Hide Streamlit default elements */
            .stApp > header { visibility: hidden; }
            .stApp > div[data-testid="stToolbar"] { visibility: hidden; }
            .stApp > div[data-testid="stDecoration"] { visibility: hidden; }
            
            /* Main container */
            .main-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            /* Top Navigation Bar */
            .top-nav {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 16px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .nav-left {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .nav-title {
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                margin: 0;
            }
            
            .nav-subtitle {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.7);
                margin: 0;
            }
            
            .nav-right {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            /* Instance Switcher */
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
            
            /* Actions Button */
            .actions-button {
                background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
                border: 1px solid #007AFF;
                border-radius: 10px;
                padding: 10px 16px;
                color: #ffffff;
                font-weight: 500;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                gap: 8px;
                box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
            }
            
            .actions-button:hover {
                transform: translateY(-3px) scale(1.08);
                box-shadow: 0 12px 30px rgba(0, 122, 255, 0.4);
            }
            
            /* Count Cards */
            .count-cards {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 16px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                max-width: 300px;
            }
            
            .count-item {
                text-align: center;
                min-width: 50px;
                flex: 1;
            }
            
            .count-number {
                font-size: 18px;
                font-weight: 700;
                line-height: 1.2;
            }
            
            .count-label {
                font-size: 11px;
                color: rgba(255, 255, 255, 0.7);
                font-weight: 500;
            }
            
            .count-total { color: #007AFF; }
            .count-selected { color: #34C759; }
            .count-deleted { color: #FF3B30; }
            
            /* Main Content */
            .main-content {
                background: rgba(255, 255, 255, 0.03);
                padding: 24px;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-bottom: 20px;
            }
            
            .content-title {
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                margin: 0 0 8px 0;
            }
            
            .content-subtitle {
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
                margin: 0 0 20px 0;
            }
            
            /* Object Cards Grid */
            .objects-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
            }
            
            .object-card {
                background: rgba(255, 255, 255, 0.05);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .object-card:hover {
                transform: translateY(-4px) scale(1.02);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                background: rgba(255, 255, 255, 0.08);
            }
            
            .object-icon {
                font-size: 24px;
                margin-bottom: 8px;
            }
            
            .object-label {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.7);
            }
            
            /* Minimal Streamlit overrides */
            .stSelectbox > div > div {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
                padding: 4px 8px;
                min-height: 28px;
            }
            
            .stSelectbox > div > div:hover {
                background: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.2);
                color: rgba(255, 255, 255, 0.9);
            }
            
            .stPopover > button {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
                padding: 4px 8px;
                min-height: 28px;
            }
            
            .stPopover > button:hover {
                background: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.2);
                color: rgba(255, 255, 255, 0.9);
            }
            
            .stButton > button {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
                padding: 4px 8px;
                height: 28px;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                background: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.2);
                color: rgba(255, 255, 255, 0.9);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_top_navigation(data_loader, current_env, current_object_type, data):
        """Render the top navigation bar with Design #4 styling"""
        # Get counts
        total_count = len(data)
        selected_count = len(st.session_state.selected_objects)
        deleted_count = len(st.session_state.deleted_objects)

        # Create columns for layout
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 1.5])

        with col1:
            # Left side - Title and counts
            st.markdown(
                f"""
                <div class="nav-left">
                    <div style="font-size: 24px;">🍎</div>
                    <div>
                        <div class="nav-title">jpapi manager</div>
                        <div class="nav-subtitle">Advanced Search Management</div>
                    </div>
                    <div class="count-cards">
                        <div class="count-item">
                            <div class="count-number count-total">{total_count}</div>
                            <div class="count-label">Total</div>
                        </div>
                        <div class="count-item">
                            <div class="count-number count-selected">{selected_count}</div>
                            <div class="count-label">Sel</div>
                        </div>
                        <div class="count-item">
                            <div class="count-number count-deleted">{deleted_count}</div>
                            <div class="count-label">Del</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            # Instance switcher
            instance_options = {"sandbox": "🧪 Sandbox", "production": "🚀 Production"}

            selected_instance = st.selectbox(
                "Instance",
                options=list(instance_options.keys()),
                format_func=lambda x: instance_options[x],
                key="instance_selector",
                label_visibility="collapsed",
            )

        with col3:
            # Object type selector
            object_types = {
                "advanced_searches": "🔍 Advanced Searches",
                "policies": "📋 Policies",
                "config_profiles": "⚙️ Config Profiles",
                "packages": "📦 Packages",
                "smart_groups": "👥 Smart Groups",
            }

            selected_type = st.selectbox(
                "Object Type",
                options=list(object_types.keys()),
                format_func=lambda x: object_types[x],
                key="object_type_selector",
                label_visibility="collapsed",
            )

        with col4:
            # Actions dropdown
            with st.popover("⚡ Actions", use_container_width=True):
                if st.button("📥 Create Export", use_container_width=True):
                    st.success("Export created successfully!")

                if st.button("🔍 Advanced Search", use_container_width=True):
                    st.info("Advanced search initiated")

                if st.button("📊 Generate Report", use_container_width=True):
                    st.info("Report generation started")

                if st.button("🗑️ Delete Selected", use_container_width=True):
                    if selected_count > 0:
                        st.session_state.selected_objects.clear()
                        st.rerun()
                    else:
                        st.warning("No items selected")

                if st.button("⚙️ Settings", use_container_width=True):
                    st.info("Settings panel opened")

        with col5:
            # Alerts button
            alert_count = len(st.session_state.get("csv_errors", [])) + len(
                st.session_state.get("csv_warnings", [])
            )
            alert_text = (
                f"🔔 Alerts ({alert_count})" if alert_count > 0 else "🔔 Alerts"
            )

            with st.popover(alert_text, use_container_width=True):
                if alert_count > 0:
                    if st.session_state.get("csv_errors"):
                        st.error(
                            f"❌ **Errors:** {len(st.session_state.csv_errors)} CSV loading errors"
                        )
                    if st.session_state.get("csv_warnings"):
                        st.warning(
                            f"⚠️ **Warnings:** {len(st.session_state.csv_warnings)} CSV warnings"
                        )
                else:
                    st.success("✅ **All systems operational** - No alerts")

                if st.button(
                    "📊 View Status", key="view_status", use_container_width=True
                ):
                    st.info(
                        f"📊 **Current Status:**\n- {len(st.session_state.selected_objects)} items selected\n- {len(st.session_state.deleted_objects)} items deleted\n- {len(data)} total objects"
                    )

    @staticmethod
    def render_object_cards(data, selected_objects: set, deleted_objects: set):
        """Render objects in Design #4 grid layout"""
        if data.empty:
            st.markdown(
                """
                <div class="main-content">
                    <div class="content-title">No Data Available</div>
                    <div class="content-subtitle">No objects found for the current selection</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        # Create a grid layout - 3 columns
        num_objects = len(data)
        cols_per_row = 3

        for i in range(0, num_objects, cols_per_row):
            # Create columns for this row
            cols = st.columns(cols_per_row)

            for j, col in enumerate(cols):
                if i + j < num_objects:
                    index = i + j
                    row = data.iloc[index]
                    object_id = f"{row['Name']}_{row['ID']}"
                    is_selected = object_id in selected_objects
                    is_deleted = object_id in deleted_objects

                    with col:
                        # Object card with Design #4 styling
                        name = str(row["Name"])
                        if len(name) > 25:
                            name = name[:22] + "..."

                        # Status indicators
                        status_dot = "●" if is_selected else "○"
                        delete_dot = "●" if is_deleted else "○"
                        status_color = (
                            "#34C759" if is_selected else "rgba(255, 255, 255, 0.3)"
                        )
                        delete_color = (
                            "#FF3B30" if is_deleted else "rgba(255, 255, 255, 0.3)"
                        )

                        st.markdown(
                            f"""
                            <div class="object-card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                                    <div style="display: flex; gap: 4px;">
                                        <span style="color: {status_color}; font-size: 12px;">{status_dot}</span>
                                        <span style="color: {delete_color}; font-size: 12px;">{delete_dot}</span>
                                    </div>
                                </div>
                                <div style="font-size: 15px; font-weight: 600; color: #ffffff; margin-bottom: 6px; line-height: 1.3;">{name}</div>
                                <div style="font-size: 11px; color: rgba(255, 255, 255, 0.6); margin-bottom: 8px;">ID: {row['ID']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Selection checkbox
                        if st.checkbox(
                            "Select item",
                            value=is_selected,
                            key=f"select_{index}",
                            help="Select for deletion",
                            label_visibility="collapsed",
                        ):
                            if object_id not in selected_objects:
                                selected_objects.add(object_id)
                            else:
                                selected_objects.remove(object_id)
                            st.rerun()

                        # Action button
                        button_icon = "↩" if is_deleted else "×"
                        button_help = "Restore" if is_deleted else "Delete"

                        if st.button(
                            button_icon,
                            key=f"delete_{index}",
                            help=button_help,
                            use_container_width=True,
                        ):
                            if object_id in deleted_objects:
                                deleted_objects.remove(object_id)
                            else:
                                deleted_objects.add(object_id)
                            st.rerun()

    @staticmethod
    def render_stats(data, selected_objects: set, deleted_objects: set):
        """Render the statistics display - now integrated into top nav"""
        pass  # Stats are now in the top navigation
