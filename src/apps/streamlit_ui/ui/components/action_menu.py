"""
Action Menu Component - Single Responsibility Principle
Renders the actions popover menu
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from .base import BaseComponent
from ...core.services.jpapi_integration import JPAPIIntegrationService
from ...core.services.export_service import ExportService
from ...utils.formatters import DataFormatter


class ActionMenuComponent(BaseComponent):
    """Action menu component for actions popover"""

    def __init__(
        self,
        jpapi_service: JPAPIIntegrationService,
        export_service: ExportService,
        component_id: str = "action_menu",
    ):
        super().__init__(component_id)
        self.jpapi_service = jpapi_service
        self.export_service = export_service
        self.formatter = DataFormatter()

    def render(self) -> None:
        """Render the action menu component"""
        self._render_action_menu_css()

        # Check if actions button was clicked
        if self.get_component_state("actions_clicked", False):
            self._render_actions_popover()
            self.set_component_state("actions_clicked", False)

    def _render_action_menu_css(self) -> None:
        """Render action menu CSS"""
        st.markdown(
            """
        <style>
        .actions-dropdown {
            position: relative;
            animation: slideDown 0.3s ease-out;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .action-button {
            width: 100%;
            margin: 4px 0;
            padding: 8px 16px;
            border-radius: 6px;
            border: 1px solid #e1e5e9;
            background-color: #ffffff;
            color: #333333;
            font-size: 14px;
            transition: all 0.2s ease;
        }
        
        .action-button:hover {
            background-color: #f8f9fa;
            border-color: #007bff;
        }
        
        .action-button.danger {
            color: #dc3545;
            border-color: #dc3545;
        }
        
        .action-button.danger:hover {
            background-color: #f8d7da;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def _render_actions_popover(self) -> None:
        """Render actions popover menu"""
        with st.popover("⚡ Actions", use_container_width=True):
            st.markdown("### ⚡ Actions")

            # Refresh Data
            if st.button("🔄 Refresh Data", key="action_refresh"):
                self._handle_refresh_data()

            # Gather Data
            if st.button("📥 Gather Data", key="action_gather"):
                self._handle_gather_data()

            st.divider()

            # Export Selected
            if st.button("📤 Export Selected", key="action_export"):
                self._handle_export_selected()

            # Clear Deleted
            if st.button("🗑️ Clear Deleted", key="action_clear_deleted"):
                self._handle_clear_deleted()

            st.divider()

            # Bulk Actions
            st.markdown("**Bulk Actions**")

            if st.button("✅ Select All", key="action_select_all"):
                self._handle_select_all()

            if st.button("❌ Clear Selection", key="action_clear_selection"):
                self._handle_clear_selection()

    def _handle_refresh_data(self) -> None:
        """Handle refresh data action"""
        # Clear all data cache
        for key in st.session_state.keys():
            if key.startswith("data_"):
                del st.session_state[key]

        st.success("🔄 Data cache cleared. Data will be reloaded.")
        st.rerun()

    def _handle_gather_data(self) -> None:
        """Handle gather data action"""
        current_env = st.session_state.get("current_environment", "sandbox")
        current_type = st.session_state.get("current_object_type", "searches")

        with st.spinner(f"Gathering {current_type} data from {current_env}..."):
            result = self.jpapi_service.gather_data(current_type, current_env)

            if result["success"]:
                st.success(f"✅ {result['message']}")
                st.info(f"Command: `{result['command']}`")
                # Clear cache to force reload
                self._handle_refresh_data()
            else:
                st.error(f"❌ {result['message']}")
                if "error" in result:
                    st.error(f"Error: {result['error']}")

    def _handle_export_selected(self) -> None:
        """Handle export selected action"""
        selected_objects = st.session_state.get("selected_objects", [])

        if not selected_objects:
            st.warning("⚠️ No objects selected for export")
            return

        # Get cached data
        cache_key = f"data_{st.session_state.get('current_object_type', 'searches')}_{st.session_state.get('current_environment', 'sandbox')}"
        cached_data = st.session_state.get(cache_key)

        if cached_data is None:
            st.warning("⚠️ No data available for export")
            return

        # Filter data for selected objects
        # This is a simplified version - in reality, you'd need to match the selected objects
        # with the actual data rows

        st.success(f"📤 Exporting {len(selected_objects)} selected objects")
        st.info("Export functionality would be implemented here")

    def _handle_clear_deleted(self) -> None:
        """Handle clear deleted action"""
        cache_key = f"data_{st.session_state.get('current_object_type', 'searches')}_{st.session_state.get('current_environment', 'sandbox')}"
        cached_data = st.session_state.get(cache_key)

        if cached_data is not None and not cached_data.empty:
            # Filter out deleted objects
            if "Status" in cached_data.columns:
                filtered_data = cached_data[cached_data["Status"] != "Deleted"]
                st.session_state[cache_key] = filtered_data
                st.success(
                    f"🗑️ Removed {len(cached_data) - len(filtered_data)} deleted objects"
                )
            else:
                st.warning("⚠️ No Status column found")
        else:
            st.warning("⚠️ No data available")

    def _handle_select_all(self) -> None:
        """Handle select all action"""
        cache_key = f"data_{st.session_state.get('current_object_type', 'searches')}_{st.session_state.get('current_environment', 'sandbox')}"
        cached_data = st.session_state.get(cache_key)

        if cached_data is not None and not cached_data.empty:
            # Create object IDs for all rows
            object_ids = [
                f"obj_{index}_{row.get('Name', 'Unknown')}"
                for index, (_, row) in enumerate(cached_data.iterrows())
            ]
            st.session_state["selected_objects"] = object_ids
            st.success(f"✅ Selected all {len(object_ids)} objects")
        else:
            st.warning("⚠️ No data available to select")

    def _handle_clear_selection(self) -> None:
        """Handle clear selection action"""
        st.session_state["selected_objects"] = []
        st.success("❌ Selection cleared")

    def set_actions_clicked(self) -> None:
        """Set actions button as clicked"""
        self.set_component_state("actions_clicked", True)

    def get_component_info(self) -> Dict[str, Any]:
        """Get action menu component information"""
        info = super().get_component_info()
        info.update(
            {
                "actions_clicked": self.get_component_state("actions_clicked", False),
                "jpapi_available": self.jpapi_service.is_jpapi_available(),
                "export_formats": self.export_service.get_supported_formats(),
            }
        )
        return info
