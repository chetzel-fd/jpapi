"""
Card Component - SOLID SRP compliance
Handles all object card rendering functionality
"""

import streamlit as st
import pandas as pd
from typing import Any
from streamlit_extras.card import card


class CardComponent:
    """Object card rendering component following SOLID SRP"""

    @staticmethod
    def render_object_card(
        row: pd.Series, index: int, manager: Any, object_type: str
    ) -> None:
        """Render clean object card using streamlit-extras"""
        object_id = f"{object_type}_{index}"
        is_marked = object_id in st.session_state.get("marked_for_deletion", set())
        is_deleted = object_id in st.session_state.get("deleted_objects", set())

        # Get object name and details
        name = row.get("Name", f"Object {index}")
        object_id_value = row.get("ID", "Unknown")
        object_type_value = row.get("Type", "Unknown")

        # Create status text and color
        if is_deleted:
            status_text = "DELETED"
            status_color = "red"
        elif is_marked:
            status_text = "PENDING"
            status_color = "orange"
        else:
            status_text = "ACTIVE"
            status_color = "green"

        # Create card content
        card_content = f"""
        **ID:** {object_id_value}  
        **Type:** {object_type_value}  
        **Status:** {status_text}
        """

        # Create clean card using streamlit-extras
        with st.container():
            col1, col2 = st.columns([1, 5])

            with col1:
                # Selection button with icon
                if st.button(
                    "☀️" if is_marked else "🌙",
                    key=f"btn_{object_id}",
                    help="Click to select for deletion",
                    type="primary" if is_marked else "secondary",
                    use_container_width=True,
                ):
                    CardComponent._toggle_object_selection(object_id)

            with col2:
                # Object information
                st.markdown(f"**{name}**")
                st.caption(f"ID: {object_id_value} • Type: {object_type_value}")

                # Status indicator
                if is_deleted:
                    st.error("🗑️ Deleted")
                elif is_marked:
                    st.warning("⚠️ Selected for deletion")
                else:
                    st.success("✅ Active")

            # Subtle divider
            st.markdown("---")

    @staticmethod
    def _toggle_object_selection(object_id: str) -> None:
        """Toggle object selection state"""
        if "marked_for_deletion" not in st.session_state:
            st.session_state.marked_for_deletion = set()

        if object_id in st.session_state.marked_for_deletion:
            st.session_state.marked_for_deletion.remove(object_id)
        else:
            st.session_state.marked_for_deletion.add(object_id)
        st.rerun()
