"""
Stats Component - SOLID SRP compliance
Handles all statistics display functionality
"""

import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards


class StatsComponent:
    """Statistics display component following SOLID SRP"""

    @staticmethod
    def render_stats_overview(df: pd.DataFrame, object_type: str) -> None:
        """Render clean stats overview using streamlit-extras"""
        if df.empty:
            st.info("No data available")
            return

        # Calculate stats
        total_objects = len(df)
        marked_for_deletion = len(st.session_state.get("marked_for_deletion", set()))
        deleted_objects = len(st.session_state.get("deleted_objects", set()))
        remaining = total_objects - marked_for_deletion - deleted_objects

        # Create compact stats cards with different colors
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Total",
                value=total_objects,
                delta=None,
            )

        with col2:
            st.metric(label="Pending", value=marked_for_deletion, delta=None)

        with col3:
            st.metric(label="Deleted", value=deleted_objects, delta=None)

        with col4:
            st.metric(label="Active", value=remaining, delta=None)

        # Apply custom styling with different colors for each metric
        style_metric_cards(
            background_color="#1e1e1e",
            border_left_color="#3b82f6",  # Blue for total
            border_color="#2d2d2d",
            box_shadow="#000000",
        )
