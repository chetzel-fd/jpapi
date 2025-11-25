#!/usr/bin/env python3
"""
JPAPI Relationship Analyzer - Main Entry Point
Standalone Streamlit app for analyzing JAMF object relationships
"""

import streamlit as st
import sys
from pathlib import Path

# Ensure local directory is first in path
_current_dir = Path(__file__).parent
_project_src = _current_dir.parent.parent

for p in [str(_current_dir), str(_project_src)]:
    while p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(_current_dir))
sys.path.insert(1, str(_project_src))

# Import analyzer components
from analyzer_data_provider import AnalyzerDataProvider
from relationship_engine import CSVRelationshipEngine
from orphan_detector import CSVOrphanDetector
from impact_analyzer import CSVImpactAnalyzer
from analyzer_controller import ReverseObjectAnalyzerController
from analyzer_styles import get_analyzer_css, get_hide_sidebar_css

# Page configuration
st.set_page_config(
    page_title="JPAPI Relationship Analyzer",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply styles
st.markdown(get_hide_sidebar_css(), unsafe_allow_html=True)
st.markdown(get_analyzer_css(), unsafe_allow_html=True)


def main():
    """Main application function"""
    # Initialize SOLID components (Dependency Injection)
    data_provider = AnalyzerDataProvider()
    relationship_engine = CSVRelationshipEngine(data_provider)
    orphan_detector = CSVOrphanDetector(relationship_engine, data_provider)
    impact_analyzer = CSVImpactAnalyzer(relationship_engine, data_provider)

    # Create controller
    controller = ReverseObjectAnalyzerController(
        relationship_engine=relationship_engine,
        orphan_detector=orphan_detector,
        impact_analyzer=impact_analyzer,
        data_provider=data_provider,
    )

    # Render header
    controller.render_header()

    # Render mode selector
    current_mode = controller.render_mode_selector()

    st.markdown("<br>", unsafe_allow_html=True)

    # Render content based on mode
    if current_mode == "individual":
        render_individual_analysis_mode(controller)
    elif current_mode == "batch":
        render_batch_analysis_mode(controller)
    elif current_mode == "orphan":
        render_orphan_finder_mode(controller)
    elif current_mode == "impact":
        render_impact_analysis_mode(controller)

    # Render FAB (sidebar stats)
    controller.render_fab()


def render_individual_analysis_mode(controller: ReverseObjectAnalyzerController):
    """Render individual object analysis mode"""
    # Render object selector
    selection = controller.render_object_selector("individual")

    # If object was selected and analyzed
    if selection:
        obj_type = selection["type"]
        obj_id = selection["id"]

        # Show loading spinner
        with st.spinner(f"Analyzing {obj_type} {obj_id}..."):
            # Analyze relationships
            relationships = controller.relationship_engine.analyze_object(
                obj_type, obj_id
            )

            # Render results
            st.markdown("<br>", unsafe_allow_html=True)
            controller.render_relationship_view(relationships)

            # Show dependency tree
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🌳 View Dependency Tree", expanded=False):
                tree_data = controller.relationship_engine.build_dependency_tree(
                    obj_type, obj_id, max_depth=3
                )
                if "error" not in tree_data:
                    st.json(tree_data)
                else:
                    st.error(tree_data["error"])

    # Show previously analyzed object if exists
    elif st.session_state.selected_object_id:
        obj_type = st.session_state.selected_object_type
        obj_id = st.session_state.selected_object_id

        relationships = controller.relationship_engine.analyze_object(obj_type, obj_id)
        st.markdown("<br>", unsafe_allow_html=True)
        controller.render_relationship_view(relationships)


def render_batch_analysis_mode(controller: ReverseObjectAnalyzerController):
    """Render batch analysis mode"""
    # Render batch selector
    batch_selection = controller.render_object_selector("batch")

    if batch_selection:
        with st.spinner("Analyzing batch..."):
            # Analyze batch
            batch_results = controller.relationship_engine.analyze_batch(
                batch_selection
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.success(f"✅ Analyzed {len(batch_selection)} objects")

            # Show shared dependencies
            shared = batch_results.get("shared_dependencies", [])
            if shared:
                st.markdown(
                    f'<div class="section-header"><span class="section-header-icon">🔗</span><span class="section-header-title">Shared Dependencies</span><span class="section-header-count">{len(shared)}</span></div>',
                    unsafe_allow_html=True,
                )

                for dep_info in shared:
                    dep_key = dep_info["dependency"]
                    users = dep_info["used_by"]
                    st.info(f"**{dep_key}** is used by {len(users)} selected objects")
            else:
                st.info("No shared dependencies found among selected objects")

            # Show dependency matrix
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-header"><span class="section-header-icon">📊</span><span class="section-header-title">Dependency Matrix</span></div>',
                unsafe_allow_html=True,
            )

            matrix = batch_results.get("dependency_matrix")
            if not matrix.empty:
                st.dataframe(matrix, use_container_width=True)

            # Individual results
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-header"><span class="section-header-icon">📋</span><span class="section-header-title">Individual Results</span></div>',
                unsafe_allow_html=True,
            )

            for obj_result in batch_results["objects"]:
                with st.expander(
                    f"{obj_result['object']['type']}: {obj_result['object']['name']}"
                ):
                    controller.render_relationship_view(obj_result)


def render_orphan_finder_mode(controller: ReverseObjectAnalyzerController):
    """Render orphan finder mode"""
    # Render orphan selector
    scan_selection = controller.render_object_selector("orphan")

    if scan_selection and scan_selection != "no_scan":
        with st.spinner("Scanning for orphaned objects..."):
            # Find orphans
            orphans = controller.orphan_detector.find_orphaned_objects(scan_selection)

            # Cache results
            st.session_state.orphan_results = orphans

            st.markdown("<br>", unsafe_allow_html=True)

            # Render results
            controller.render_orphan_results(orphans)

            # Show cleanup report
            if sum(len(o) for o in orphans.values()) > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📊 View Cleanup Report", expanded=False):
                    report = controller.orphan_detector.generate_cleanup_report()

                    st.markdown(f"**Total Orphans:** {report['total_orphans']}")
                    st.markdown("**By Type:**")
                    for obj_type, count in report["by_type"].items():
                        st.markdown(f"  - {obj_type}: {count}")

                    st.markdown("**Recommendations:**")
                    for rec in report["recommendations"]:
                        st.markdown(f"- {rec}")

                    # Export button
                    if st.button("📥 Export Orphans to CSV"):
                        csv_data = controller.orphan_detector.export_orphans_csv(
                            orphans
                        )
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name="orphaned_objects.csv",
                            mime="text/csv",
                        )

    # Show previously scanned results
    elif st.session_state.orphan_results:
        st.markdown("<br>", unsafe_allow_html=True)
        controller.render_orphan_results(st.session_state.orphan_results)


def render_impact_analysis_mode(controller: ReverseObjectAnalyzerController):
    """Render impact analysis mode"""
    # Render impact selector
    selection = controller.render_object_selector("impact")

    if selection:
        obj_type = selection["type"]
        obj_id = selection["id"]

        with st.spinner(f"Assessing deletion impact for {obj_type} {obj_id}..."):
            # Assess impact
            impact_data = controller.impact_analyzer.assess_deletion_impact(
                obj_type, obj_id
            )

            # Cache result
            st.session_state.impact_result = impact_data

            st.markdown("<br>", unsafe_allow_html=True)

            # Render impact report
            controller.render_impact_report(impact_data)

            # Show detailed affected objects
            affected = impact_data.get("affected_objects", [])
            if affected:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander(f"📋 View All {len(affected)} Affected Objects"):
                    for obj in affected:
                        st.markdown(
                            f"- **{obj['type']}**: {obj['name']} (ID: {obj['id']})"
                        )

            # Show potentially orphaned objects
            orphaned = impact_data.get("potentially_orphaned", [])
            if orphaned:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander(
                    f"🗑️ View {len(orphaned)} Objects That Will Become Orphaned"
                ):
                    for obj in orphaned:
                        st.markdown(
                            f"- **{obj['type']}**: {obj['name']} (ID: {obj['id']})"
                        )

    # Show previously analyzed impact
    elif st.session_state.impact_result:
        st.markdown("<br>", unsafe_allow_html=True)
        controller.render_impact_report(st.session_state.impact_result)


if __name__ == "__main__":
    main()







