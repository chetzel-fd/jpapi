"""
Deletion Component - SOLID SRP compliance
Handles all deletion management functionality
"""

import streamlit as st
from typing import Any
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stateful_button import button


class DeletionComponent:
    """Deletion management component following SOLID SRP"""

    @staticmethod
    def render_deletion_management(manager: Any, object_type: str) -> None:
        """Render deletion management interface using streamlit-extras"""
        if not st.session_state.marked_for_deletion:
            return

        colored_header(
            label="🗑️ Deletion Management",
            description="Manage objects marked for deletion",
            color_name="red-70",
        )

        # Show marked objects
        st.write(
            f"**{len(st.session_state.marked_for_deletion)} objects marked for deletion:**"
        )

        for object_id in list(st.session_state.marked_for_deletion):
            st.write(f"• {object_id}")

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if button("✅ Confirm Deletion", key="confirm_delete", type="primary"):
                DeletionComponent._confirm_deletion(manager, object_type)

        with col2:
            if button("❌ Cancel", key="cancel_delete", type="secondary"):
                st.session_state.marked_for_deletion.clear()
                st.rerun()

        with col3:
            if button("🔄 Clear All", key="clear_all", type="secondary"):
                st.session_state.marked_for_deletion.clear()
                st.rerun()

    @staticmethod
    def _confirm_deletion(manager: Any, object_type: str) -> None:
        """Confirm and execute deletion"""
        if not st.session_state.marked_for_deletion:
            return

        try:
            # Move marked items to deleted
            for object_id in list(st.session_state.marked_for_deletion):
                st.session_state.deleted_objects.add(object_id)

            # Clear marked items
            deleted_count = len(st.session_state.marked_for_deletion)
            st.session_state.marked_for_deletion.clear()

            st.success(f"✅ Successfully deleted {deleted_count} {object_type}")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error during deletion: {str(e)}")
