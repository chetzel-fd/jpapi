"""
Chart Component - SOLID SRP compliance
Handles all chart visualization functionality
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


class ChartComponent:
    """Chart visualization component following SOLID SRP"""

    @staticmethod
    def render_bubble_chart(df: pd.DataFrame, object_type: str) -> None:
        """Render simple bar chart for object analysis"""
        if df.empty:
            return

        # Create simple bar chart instead of bubble chart
        if "Type" in df.columns:
            type_counts = df["Type"].value_counts()

            # Create a simple bar chart
            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=type_counts.index,
                    y=type_counts.values,
                    marker=dict(
                        color=type_counts.values,
                        colorscale="Viridis",
                        showscale=True,
                        colorbar=dict(title="Count"),
                    ),
                    text=type_counts.values,
                    textposition="auto",
                )
            )

            type_title = object_type.replace("-", " ").title()
            fig.update_layout(
                title=f"{type_title} Distribution",
                xaxis=dict(title="Type"),
                yaxis=dict(title="Count"),
                height=250,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
            )

            st.plotly_chart(fig, use_container_width=True)
