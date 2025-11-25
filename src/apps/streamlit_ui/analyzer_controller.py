#!/usr/bin/env python3
"""
Analyzer Controller - SOLID UI Controller
Handles all UI rendering for the Reverse Object Analyzer
"""

import os
import streamlit as st
from typing import Dict, List, Any, Optional
from analyzer_interfaces import (
    AnalyzerUIController,
    RelationshipEngine,
    OrphanDetector,
    ImpactAnalyzer,
    DataProvider,
)


class ReverseObjectAnalyzerController(AnalyzerUIController):
    """Main UI controller for Reverse Object Analyzer"""

    def __init__(
        self,
        relationship_engine: RelationshipEngine,
        orphan_detector: OrphanDetector,
        impact_analyzer: ImpactAnalyzer,
        data_provider: DataProvider,
    ):
        self.relationship_engine = relationship_engine
        self.orphan_detector = orphan_detector
        self.impact_analyzer = impact_analyzer
        self.data_provider = data_provider

        # Initialize session state
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state variables"""
        if "analyzer_mode" not in st.session_state:
            st.session_state.analyzer_mode = "individual"
        if "analyzer_environment" not in st.session_state:
            st.session_state.analyzer_environment = "sandbox"
        if "selected_object_type" not in st.session_state:
            st.session_state.selected_object_type = "policies"
        if "selected_object_id" not in st.session_state:
            st.session_state.selected_object_id = None
        if "selected_objects_batch" not in st.session_state:
            st.session_state.selected_objects_batch = []
        if "orphan_results" not in st.session_state:
            st.session_state.orphan_results = None
        if "impact_result" not in st.session_state:
            st.session_state.impact_result = None

    def render_header(self) -> None:
        """Render the analyzer header"""
        env_display = {"sandbox": "sbox", "production": "prod"}.get(
            st.session_state.analyzer_environment, st.session_state.analyzer_environment
        )

        mode_config = {
            "individual": "🔍 Individual Analysis",
            "batch": "📊 Batch Analysis",
            "orphan": "⚠️ Orphan Finder",
            "impact": "💥 Impact Analysis",
        }

        mode_display = mode_config.get(st.session_state.analyzer_mode, "Analysis")

        # Get server info from environment
        server_name = os.environ.get("JPAPI_SERVER_NAME", "jamf-server")
        server_url = os.environ.get("JPAPI_SERVER_URL", "#")

        # Load object counts
        object_summary = self.data_provider.get_all_objects_summary(
            st.session_state.analyzer_environment
        )
        total_objects = sum(object_summary.values())

        st.markdown(
            f"""
            <div class="analyzer-header">
                <div class="analyzer-title">
                    <span class="icon">🔗</span>jpapi relationship analyzer
                </div>
                <div class="analyzer-subtitle">
                    <span style="color: #3393ff; font-weight: 700;">env:</span>
                    <span style="color: #fff; font-weight: 500;">{env_display}</span>
                    <span style="color: #3393ff; margin: 0 8px;">•</span>
                    <span style="color: #fff; font-weight: 500;">{server_name}</span>
                    <a href="{server_url}" target="_blank" style="color: #ffd60a; text-decoration: none; font-size: 14px; font-weight: 600;">(url)</a>
                    <span style="color: #3393ff; margin: 0 8px;">•</span>
                    <span style="color: #3393ff; font-weight: 700;">mode:</span>
                    <span style="color: #ffd60a; font-weight: 600;">{mode_display}</span>
                    <span style="color: #3393ff; margin: 0 8px;">•</span>
                    <span style="color: #b9c4cb;">{total_objects} objects loaded</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_mode_selector(self) -> str:
        """Render mode selection UI"""
        st.markdown('<div class="mode-tabs">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button(
                "🔍 Individual",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.analyzer_mode == "individual"
                    else "secondary"
                ),
            ):
                st.session_state.analyzer_mode = "individual"
                st.rerun()

        with col2:
            if st.button(
                "📊 Batch",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.analyzer_mode == "batch"
                    else "secondary"
                ),
            ):
                st.session_state.analyzer_mode = "batch"
                st.rerun()

        with col3:
            if st.button(
                "⚠️ Orphans",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.analyzer_mode == "orphan"
                    else "secondary"
                ),
            ):
                st.session_state.analyzer_mode = "orphan"
                st.rerun()

        with col4:
            if st.button(
                "💥 Impact",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.analyzer_mode == "impact"
                    else "secondary"
                ),
            ):
                st.session_state.analyzer_mode = "impact"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        return st.session_state.analyzer_mode

    def render_object_selector(self, mode: str) -> Any:
        """Render object selection UI based on current mode"""
        if mode == "individual":
            return self._render_individual_selector()
        elif mode == "batch":
            return self._render_batch_selector()
        elif mode == "orphan":
            return self._render_orphan_selector()
        elif mode == "impact":
            return self._render_impact_selector()

    def _render_individual_selector(self) -> Optional[Dict[str, str]]:
        """Render selector for individual object analysis"""
        st.markdown(
            '<div class="section-header"><span class="section-header-icon">🔍</span><span class="section-header-title">Select Object to Analyze</span></div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 2])

        with col1:
            obj_types = self.data_provider.get_all_object_types()
            selected_type = st.selectbox(
                "Object Type",
                obj_types,
                index=(
                    obj_types.index(st.session_state.selected_object_type)
                    if st.session_state.selected_object_type in obj_types
                    else 0
                ),
                key="individual_obj_type",
            )
            st.session_state.selected_object_type = selected_type

        with col2:
            # Load objects of selected type
            objects_df = self.data_provider.load_objects(
                selected_type, st.session_state.analyzer_environment
            )

            if objects_df.empty:
                st.warning(
                    f"No {selected_type} found for {st.session_state.analyzer_environment}"
                )
                return None

            # Create object selection dropdown
            object_options = []
            for _, row in objects_df.iterrows():
                obj_id = self._extract_id(row.get("ID", ""))
                obj_name = row.get("Name", "Unknown")
                object_options.append(f"{obj_name} (ID: {obj_id})")

            selected_obj = st.selectbox(
                "Select Object", object_options, key="individual_obj_select"
            )

            if selected_obj:
                # Extract ID from selection
                import re

                match = re.search(r"ID: (\d+)", selected_obj)
                if match:
                    selected_id = match.group(1)

                    # Analyze button
                    if st.button(
                        "🔍 Analyze Relationships",
                        type="primary",
                        use_container_width=True,
                    ):
                        st.session_state.selected_object_id = selected_id
                        return {"type": selected_type, "id": selected_id}

        return None

    def _render_batch_selector(self) -> Optional[List[Dict[str, str]]]:
        """Render selector for batch analysis"""
        st.markdown(
            '<div class="section-header"><span class="section-header-icon">�</span><span class="section-header-title">Select Multiple Objects for Batch Analysis</span></div>',
            unsafe_allow_html=True,
        )

        st.info(
            "📝 Batch analysis allows you to analyze multiple objects simultaneously and identify shared dependencies."
        )

        # Object type selector
        obj_types = self.data_provider.get_all_object_types()
        selected_type = st.selectbox("Object Type", obj_types, key="batch_obj_type")

        # Load objects
        objects_df = self.data_provider.load_objects(
            selected_type, st.session_state.analyzer_environment
        )

        if objects_df.empty:
            st.warning(f"No {selected_type} found")
            return None

        # Multi-select
        object_options = {}
        for _, row in objects_df.iterrows():
            obj_id = self._extract_id(row.get("ID", ""))
            obj_name = row.get("Name", "Unknown")
            object_options[f"{obj_name} (ID: {obj_id})"] = obj_id

        selected_objs = st.multiselect(
            "Select Objects (2 or more)",
            list(object_options.keys()),
            key="batch_obj_multiselect",
        )

        if len(selected_objs) >= 2:
            if st.button("📊 Analyze Batch", type="primary"):
                batch_list = [
                    {"type": selected_type, "id": object_options[obj]}
                    for obj in selected_objs
                ]
                return batch_list
        elif len(selected_objs) == 1:
            st.info("Please select at least 2 objects for batch analysis")

        return None

    def _render_orphan_selector(self) -> Optional[str]:
        """Render selector for orphan finding"""
        st.markdown(
            '<div class="section-header"><span class="section-header-icon">⚠️</span><span class="section-header-title">Find Orphaned Objects</span></div>',
            unsafe_allow_html=True,
        )

        st.info(
            "🔍 Scan for objects that are not used by any other objects in your JAMF environment."
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            scan_type = st.selectbox(
                "Scan For",
                ["All Types", "Groups Only", "Scripts Only", "Packages Only"],
                key="orphan_scan_type",
            )

        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button(
                "🔍 Scan for Orphans", type="primary", use_container_width=True
            ):
                # Map selection to type
                type_map = {
                    "All Types": None,
                    "Groups Only": "groups",
                    "Scripts Only": "scripts",
                    "Packages Only": "packages",
                }
                return type_map[scan_type]

        return "no_scan"

    def _render_impact_selector(self) -> Optional[Dict[str, str]]:
        """Render selector for impact analysis"""
        st.markdown(
            '<div class="section-header"><span class="section-header-icon">💥</span><span class="section-header-title">Pre-Deletion Impact Analysis</span></div>',
            unsafe_allow_html=True,
        )

        st.info(
            "⚠️ Assess the impact of deleting an object before proceeding with deletion."
        )

        col1, col2 = st.columns([1, 2])

        with col1:
            obj_types = self.data_provider.get_all_object_types()
            selected_type = st.selectbox(
                "Object Type", obj_types, key="impact_obj_type"
            )

        with col2:
            objects_df = self.data_provider.load_objects(
                selected_type, st.session_state.analyzer_environment
            )

            if objects_df.empty:
                st.warning(f"No {selected_type} found")
                return None

            object_options = []
            for _, row in objects_df.iterrows():
                obj_id = self._extract_id(row.get("ID", ""))
                obj_name = row.get("Name", "Unknown")
                object_options.append(f"{obj_name} (ID: {obj_id})")

            selected_obj = st.selectbox(
                "Select Object", object_options, key="impact_obj_select"
            )

            if selected_obj:
                import re

                match = re.search(r"ID: (\d+)", selected_obj)
                if match:
                    selected_id = match.group(1)

                    if st.button(
                        "💥 Assess Impact", type="primary", use_container_width=True
                    ):
                        return {"type": selected_type, "id": selected_id}

        return None

    def render_relationship_view(self, relationships: Dict[str, Any]) -> None:
        """Render relationship visualization"""
        if "error" in relationships:
            st.error(f"Error: {relationships['error']}")
            return

        obj_info = relationships["object"]
        uses = relationships.get("uses", [])
        used_by = relationships.get("used_by", [])

        # Object header
        st.markdown(
            f"""
            <div class="relationship-card">
                <div class="relationship-card-header">
                    <div class="relationship-card-title">{obj_info['type'].title()}: "{obj_info['name']}" (ID: {obj_info['id']})</div>
                    <div class="relationship-card-badge">{len(uses) + len(used_by)} relationships</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f'<div class="section-header"><span class="section-header-title">USES</span><span class="section-header-count">{len(uses)}</span></div>',
                unsafe_allow_html=True,
            )

            if uses:
                for obj in uses:
                    self._render_object_reference_card(obj)
            else:
                st.markdown(
                    '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-description">This object doesn\'t use any other objects</div></div>',
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown(
                f'<div class="section-header"><span class="section-header-title">USED BY</span><span class="section-header-count">{len(used_by)}</span></div>',
                unsafe_allow_html=True,
            )

            if used_by:
                for obj in used_by:
                    self._render_object_reference_card(obj)
            else:
                st.markdown(
                    '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-description">No objects reference this one</div></div>',
                    unsafe_allow_html=True,
                )

        # Impact summary
        if len(used_by) > 0:
            st.warning(
                f"⚠️ **IMPACT**: Deleting this would affect {len(used_by)} object(s)"
            )
        else:
            st.success("✅ **Safe to delete** - No objects reference this one")

    def _render_object_reference_card(self, obj: Dict[str, Any]):
        """Render a single object reference card"""
        icon_map = {
            "policies": "📋",
            "profiles": "⚙️",
            "groups": "👥",
            "scripts": "📜",
            "packages": "📦",
            "searches": "🔍",
        }

        icon = icon_map.get(obj["type"], "📄")

        st.markdown(
            f"""
            <div class="object-ref-card">
                <div class="object-ref-icon">{icon}</div>
                <div class="object-ref-content">
                    <div class="object-ref-name">{obj['name']}</div>
                    <div class="object-ref-meta">
                        <span class="object-type-badge {obj['type']}">{obj['type']}</span>
                        <span style="color: #b9c4cb; margin-left: 8px;">ID: {obj['id']}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_orphan_results(self, orphans: Dict[str, List[Dict[str, Any]]]) -> None:
        """Render orphaned objects results"""
        total_orphans = sum(len(orphan_list) for orphan_list in orphans.values())

        if total_orphans == 0:
            st.success("✅ **No orphaned objects found!** Your environment is clean.")
            return

        st.warning(f"⚠️ **Found {total_orphans} orphaned objects**")

        for obj_type, orphan_list in orphans.items():
            if not orphan_list:
                continue

            icon_map = {"groups": "👥", "scripts": "📜", "packages": "📦"}

            st.markdown(
                f'<div class="section-header"><span class="section-header-icon">{icon_map.get(obj_type, "📄")}</span><span class="section-header-title">{obj_type.upper()}</span><span class="section-header-count">{len(orphan_list)} orphaned</span></div>',
                unsafe_allow_html=True,
            )

            for orphan in orphan_list:
                self._render_orphan_card(orphan)

    def _render_orphan_card(self, orphan: Dict[str, Any]):
        """Render a single orphan card"""
        st.markdown(
            f"""
            <div class="orphan-card">
                <div class="orphan-card-title">{orphan['name']}</div>
                <div class="orphan-card-meta">
                    ID: {orphan['id']} • Last Modified: {orphan.get('last_modified', 'Unknown')}
                </div>
                <div class="orphan-card-stats">
                    <div class="orphan-stat">
                        <span class="orphan-stat-label">References:</span>
                        <span class="orphan-stat-value">0</span>
                    </div>
                    <div class="orphan-stat">
                        <span class="orphan-stat-label">Status:</span>
                        <span class="orphan-stat-value">{orphan.get('status', 'Unknown')}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_impact_report(self, impact_data: Dict[str, Any]) -> None:
        """Render deletion impact report"""
        if "error" in impact_data:
            st.error(f"Error: {impact_data['error']}")
            return

        obj_info = impact_data["object"]
        risk_level = impact_data["risk_level"]
        affected = impact_data["affected_objects"]
        recommendations = impact_data["recommendations"]

        # Risk badge
        risk_icons = {"low": "✅", "medium": "⚠️", "high": "🔴"}
        risk_colors = {"low": "#28a745", "medium": "#ffc107", "high": "#dc3545"}

        st.markdown(
            f"""
            <div class="impact-card {risk_level}-risk">
                <div class="impact-risk-badge {risk_level}">
                    {risk_icons.get(risk_level, '❓')} {risk_level.upper()} RISK
                </div>
                <div style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 8px;">
                    {obj_info['type'].title()}: "{obj_info['name']}" (ID: {obj_info['id']})
                </div>
            """,
            unsafe_allow_html=True,
        )

        # Affected objects
        if affected:
            st.markdown(
                '<div class="impact-details"><div style="font-weight: 700; color: #ffd60a; margin-bottom: 12px;">This deletion will affect:</div>',
                unsafe_allow_html=True,
            )
            for obj in affected[:5]:  # Show first 5
                st.markdown(
                    f'<div class="impact-detail-item"><span class="impact-detail-bullet">•</span><span>{obj["type"]}: {obj["name"]} (ID: {obj["id"]})</span></div>',
                    unsafe_allow_html=True,
                )
            if len(affected) > 5:
                st.markdown(
                    f'<div class="impact-detail-item"><span class="impact-detail-bullet">…</span><span>and {len(affected) - 5} more objects</span></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Recommendations
        if recommendations:
            st.markdown(
                '<div class="impact-recommendations"><div class="impact-recommendations-title">💡 RECOMMENDATIONS</div>',
                unsafe_allow_html=True,
            )
            for rec in recommendations:
                st.markdown(
                    f'<div style="color: #fff; margin: 4px 0;">{rec}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    def render_fab(self) -> None:
        """Render floating action button with analyzer stats"""
        # Get stats
        object_summary = self.data_provider.get_all_objects_summary(
            st.session_state.analyzer_environment
        )
        total_objects = sum(object_summary.values())

        # Get orphan count (cached)
        orphan_count = 0
        if st.session_state.orphan_results:
            orphan_count = sum(
                len(orphans) for orphans in st.session_state.orphan_results.values()
            )

        # Display stats in sidebar (simpler than FAB for now)
        with st.sidebar:
            st.markdown("### 📊 Stats")
            st.metric("Total Objects", total_objects)
            st.metric("Orphans Found", orphan_count if orphan_count > 0 else "-")

            st.markdown("---")
            st.markdown("### ⚙️ Settings")

            # Environment selector
            env = st.selectbox(
                "Environment",
                ["sandbox", "production"],
                index=0 if st.session_state.analyzer_environment == "sandbox" else 1,
            )
            if env != st.session_state.analyzer_environment:
                st.session_state.analyzer_environment = env
                self.data_provider.set_environment(env)
                self.data_provider.reload_data()
                st.rerun()

    def _extract_id(self, id_value: Any) -> str:
        """Extract ID from various formats"""
        import re

        id_str = str(id_value)

        if "=HYPERLINK(" in id_str:
            match = re.search(r'=HYPERLINK\("[^"]*",\s*"(\d+)"\)', id_str)
            if match:
                return match.group(1)

        if "<a href=" in id_str:
            match = re.search(r">(\d+)<", id_str)
            if match:
                return match.group(1)

        return id_str.strip()
