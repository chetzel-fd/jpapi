"""
Object Card Component - Single Responsibility Principle
Renders individual object cards with status badges and selection
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List
from .base import BaseComponent
from ...utils.formatters import DataFormatter
from ...utils.helpers import HelperFunctions


class ObjectCardComponent(BaseComponent):
    """Object card component for displaying individual objects"""

    def __init__(self, component_id: str = "object_card"):
        super().__init__(component_id)
        self.formatter = DataFormatter()
        self.helpers = HelperFunctions()

    def render_object_card(self, row: pd.Series, index: int) -> None:
        """Render a single object card"""
        self._render_object_card_css()

        # Get object data
        name = self.helpers.safe_get_column(pd.DataFrame([row]), "Name", "Unknown")
        status = self.helpers.safe_get_column(pd.DataFrame([row]), "Status", "Unknown")
        smart = self.helpers.safe_get_column(pd.DataFrame([row]), "Smart", False)
        modified = self.helpers.safe_get_column(
            pd.DataFrame([row]), "Modified", "Unknown"
        )

        # Create object ID for selection tracking
        object_id = f"obj_{index}_{name}"
        is_selected = self._is_object_selected(object_id)

        # Render card
        with st.container():
            st.markdown(
                f"""
            <div class="object-card {'selected' if is_selected else ''}">
                <div class="object-header">
                    <div class="object-title">{self.formatter.format_name(name)}</div>
                    <div class="object-actions">
                        {self._render_selection_button(object_id, is_selected)}
                    </div>
                </div>
                <div class="object-details">
                    <div class="object-status">
                        {self._render_status_badge(status)}
                        {self._render_smart_indicator(smart)}
                    </div>
                    <div class="object-meta">
                        <span class="modified-date">📅 {self.formatter.format_date(modified)}</span>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    def _render_object_card_css(self) -> None:
        """Render object card CSS"""
        st.markdown(
            """
        <style>
        .object-card {
            background-color: #ffffff;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }
        
        .object-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transform: translateY(-1px);
        }
        
        .object-card.selected {
            border-color: #007bff;
            background-color: #f8f9ff;
        }
        
        .object-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .object-title {
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            flex: 1;
            margin-right: 12px;
        }
        
        .object-actions {
            display: flex;
            gap: 8px;
        }
        
        .object-details {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .object-status {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        
        .object-meta {
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #666666;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-active {
            background-color: #28a745;
            color: white;
        }
        
        .status-deleted {
            background-color: #dc3545;
            color: white;
        }
        
        .status-inactive {
            background-color: #6c757d;
            color: white;
        }
        
        .smart-indicator {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: bold;
        }
        
        .smart-true {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        .smart-false {
            background-color: #f3e5f5;
            color: #7b1fa2;
        }
        
        .selection-button {
            width: 32px;
            height: 32px;
            border-radius: 16px;
            border: 2px solid #e1e5e9;
            background-color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .selection-button:hover {
            border-color: #007bff;
            background-color: #f8f9fa;
        }
        
        .selection-button.selected {
            border-color: #007bff;
            background-color: #007bff;
            color: white;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def _render_status_badge(self, status: str) -> str:
        """Render status badge"""
        status_classes = {
            "Active": "status-active",
            "Deleted": "status-deleted",
            "Inactive": "status-inactive",
        }

        css_class = status_classes.get(status, "status-inactive")
        return f'<span class="status-badge {css_class}">{status}</span>'

    def _render_smart_indicator(self, smart: Any) -> str:
        """Render smart group indicator"""
        if smart in [True, 1, "True", "true", "1"]:
            return '<span class="smart-indicator smart-true">🧠 Smart</span>'
        else:
            return '<span class="smart-indicator smart-false">📋 Static</span>'

    def _render_selection_button(self, object_id: str, is_selected: bool) -> str:
        """Render selection button"""
        button_class = (
            "selection-button selected" if is_selected else "selection-button"
        )
        icon = "✓" if is_selected else "○"

        return f"""
        <div class="{button_class}" onclick="toggleSelection('{object_id}')">
            {icon}
        </div>
        """

    def _is_object_selected(self, object_id: str) -> bool:
        """Check if object is selected"""
        selected_objects = st.session_state.get("selected_objects", [])
        return object_id in selected_objects

    def render_object_grid(self, df: pd.DataFrame) -> None:
        """Render grid of object cards"""
        if df.empty:
            st.info("No objects to display")
            return

        # Add JavaScript for selection handling
        st.markdown(
            """
        <script>
        function toggleSelection(objectId) {
            // This would be handled by Streamlit in a real implementation
            console.log('Toggle selection for:', objectId);
        }
        </script>
        """,
            unsafe_allow_html=True,
        )

        # Render cards in columns
        cols = st.columns(3)

        for index, (_, row) in enumerate(df.iterrows()):
            with cols[index % 3]:
                self.render_object_card(row, index)

    def render_object_list(self, df: pd.DataFrame) -> None:
        """Render list of object cards"""
        if df.empty:
            st.info("No objects to display")
            return

        # Render cards in a single column
        for index, (_, row) in enumerate(df.iterrows()):
            self.render_object_card(row, index)

    def get_selected_objects(self) -> List[str]:
        """Get list of selected objects"""
        return st.session_state.get("selected_objects", [])

    def clear_selection(self) -> None:
        """Clear all selected objects"""
        st.session_state["selected_objects"] = []

    def select_all_objects(self, df: pd.DataFrame) -> None:
        """Select all objects in the dataframe"""
        object_ids = [
            f"obj_{index}_{row.get('Name', 'Unknown')}"
            for index, (_, row) in enumerate(df.iterrows())
        ]
        st.session_state["selected_objects"] = object_ids

    def get_selection_count(self) -> int:
        """Get count of selected objects"""
        return len(self.get_selected_objects())

    def get_component_info(self) -> Dict[str, Any]:
        """Get object card component information"""
        info = super().get_component_info()
        info.update(
            {
                "selected_objects": self.get_selected_objects(),
                "selection_count": self.get_selection_count(),
            }
        )
        return info
