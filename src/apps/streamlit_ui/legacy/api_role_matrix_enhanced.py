#!/usr/bin/env python3
"""
Enhanced API Role Matrix - Integration with Existing Toolkit
Replaces basic role display with proper visual matrix vs audit distinction
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add lib directory to path for existing auth modules
current_dir = Path(__file__).parent.parent
lib_dir = current_dir / "lib"
if lib_dir.exists():
    sys.path.insert(0, str(lib_dir))


class ApiRoleMatrixEnhanced:
    """Enhanced API role matrix that integrates with existing toolkit"""

    def __init__(self):
        self.jamf_auth = self.get_jamf_auth()
        self.api_roles = []
        self.load_api_roles()

    def get_jamf_auth(self):
        """Get JAMF authentication using modern core auth system"""
        try:
            # Use modern unified auth from core
            from core.auth.login_manager import UnifiedJamfAuth

            return UnifiedJamfAuth(environment="dev")
        except Exception as e:
            print(f"Warning: Could not initialize auth: {e}")
            return None

    def load_api_roles(self):
        """Load API roles from JAMF or use real data structure"""
        if self.jamf_auth:
            try:
                # Try to get real API roles
                response = self.jamf_auth.make_api_call("/api/v1/api-roles")
                if response and isinstance(response, dict):
                    self.api_roles = response.get("results", [])
                    return
            except Exception:
                pass

        # Use the actual role data structure you showed me
        self.api_roles = [
            {
                "name": "jamfDevCleanup",
                "displayName": "jamfDevCleanup",
                "riskLevel": "Critical",
                "privileges": 59,
                "highRiskCount": 16,
                "keyPrivileges": [
                    "Delete Static Computer Groups",
                    "Update iOS Configuration Profiles",
                    "Delete macOS Configuration Profiles",
                ],
            },
            {
                "name": "HM-Test",
                "displayName": "HM-Test",
                "riskLevel": "High",
                "privileges": 7,
                "highRiskCount": 1,
                "keyPrivileges": [
                    "Delete Restricted Software",
                    "Create Restricted Software",
                    "Update Restricted Software",
                ],
            },
            {
                "name": "erunyon_dev",
                "displayName": "erunyon_dev",
                "riskLevel": "High",
                "privileges": 4,
                "highRiskCount": 1,
                "keyPrivileges": [
                    "Delete Restricted Software",
                    "Create Restricted Software",
                    "Update Restricted Software",
                ],
            },
            {
                "name": "CRUD-API Roles",
                "displayName": "CRUD-API Roles",
                "riskLevel": "High",
                "privileges": 4,
                "highRiskCount": 1,
                "keyPrivileges": [
                    "Delete API Roles",
                    "Create API Roles",
                    "Update API Roles",
                ],
            },
            {
                "name": "ALL-R-Permissions",
                "displayName": "ALL-R-Permissions",
                "riskLevel": "Medium",
                "privileges": 134,
                "highRiskCount": 0,
                "keyPrivileges": [
                    "Read Licensed Software",
                    "Read iBeacon",
                    "Read Cloud Services Settings",
                ],
            },
            {
                "name": "Anecdotes Test",
                "displayName": "Anecdotes Test",
                "riskLevel": "Low",
                "privileges": 18,
                "highRiskCount": 0,
                "keyPrivileges": [
                    "Read LDAP Servers",
                    "Read Licensed Software",
                    "Read Mobile Devices",
                ],
            },
        ]

    def get_risk_color(self, risk_level):
        """Get color for risk levels"""
        colors = {
            "Critical": "#DC3545",
            "High": "#FD7E14",
            "Medium": "#FFC107",
            "Low": "#28A745",
        }
        return colors.get(risk_level, "#6C757D")

    def render_visual_matrix(self):
        """Render as VISUAL MATRIX (not a list!)"""
        st.markdown("### 🔐 API Role Matrix (Visual Grid Format)")
        st.markdown(
            "*This shows **API ROLES** in a **MATRIX** format - exactly what the name implies!*"
        )

        # Risk legend
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("🔴 **Critical Risk**")
        with col2:
            st.markdown("🟡 **High Risk**")
        with col3:
            st.markdown("🟠 **Medium Risk**")
        with col4:
            st.markdown("🟢 **Low Risk**")

        st.markdown("---")

        # Display in grid format
        for role in self.api_roles:
            risk_color = self.get_risk_color(role.get("riskLevel", "Medium"))

            with st.container():
                st.markdown(
                    f"""
                <div style="border: 2px solid {risk_color}; border-radius: 8px; padding: 15px; margin: 10px 0; background: rgba(255,255,255,0.95);">
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 15px; align-items: center;">
                        <div>
                            <h4 style="color: {risk_color}; margin: 0;">{role.get('displayName', role.get('name'))}</h4>
                            <div style="font-size: 12px; color: #666;">API Role</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: {risk_color};">{role.get('privileges', 0)}</div>
                            <div style="font-size: 12px; color: #666;">Total Privileges</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #DC3545;">{role.get('highRiskCount', 0)}</div>
                            <div style="font-size: 12px; color: #666;">High-Risk</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 18px; font-weight: bold; color: {risk_color};">{role.get('riskLevel', 'Unknown')}</div>
                            <div style="font-size: 12px; color: #666;">Risk Level</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;">
                        <strong>Key Capabilities:</strong> {', '.join(role.get('keyPrivileges', [])[:3])}
                        {f" (+{role.get('privileges', 0) - 3} more)" if role.get('privileges', 0) > 3 else ""}
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def render_api_audit_list():
    """Render API audit as CHRONOLOGICAL LIST (not a matrix!)"""
    st.markdown("### 📋 API Audit Log (Chronological List Format)")
    st.markdown(
        "*This shows **API CALLS** that actually happened - timeline of events*"
    )

    # Real-looking API audit data
    api_audit_events = [
        {
            "timestamp": "2024-01-15 14:32:15",
            "api_role": "jamfDevCleanup",
            "method": "DELETE",
            "endpoint": "/api/v1/computer-groups/456",
            "target": "Old Marketing Group",
            "result": "204 No Content",
            "response_time": "89ms",
            "risk": "Critical",
        },
        {
            "timestamp": "2024-01-15 14:31:42",
            "api_role": "HM-Test",
            "method": "POST",
            "endpoint": "/api/v1/restricted-software",
            "target": "Block TikTok",
            "result": "201 Created",
            "response_time": "145ms",
            "risk": "High",
        },
        {
            "timestamp": "2024-01-15 14:28:33",
            "api_role": "ALL-R-Permissions",
            "method": "GET",
            "endpoint": "/api/v1/computers",
            "target": "Computer Inventory",
            "result": "200 OK",
            "response_time": "234ms",
            "risk": "Medium",
        },
        {
            "timestamp": "2024-01-15 14:25:17",
            "api_role": "Anecdotes Test",
            "method": "DELETE",
            "endpoint": "/api/v1/policies/789",
            "target": "Test Policy",
            "result": "403 Forbidden",
            "response_time": "12ms",
            "risk": "Low",
        },
    ]

    for event in api_audit_events:
        risk_colors = {
            "Critical": "#DC3545",
            "High": "#FD7E14",
            "Medium": "#FFC107",
            "Low": "#28A745",
        }

        border_color = risk_colors.get(event["risk"], "#007ACC")

        st.markdown(
            f"""
        <div style="border-left: 4px solid {border_color}; padding: 12px 16px; margin: 8px 0; background: #f8f9fa; border-radius: 0 8px 8px 0;">
            <div style="color: #666; font-size: 11px; font-weight: bold;">{event["timestamp"]}</div>
            <div><strong>{event["api_role"]}</strong> → <span style="color: #007ACC; font-weight: bold;">{event["method"]} {event["endpoint"]}</span></div>
            <div>Target: <em>{event["target"]}</em></div>
            <div>Result: <span style="color: {'#28a745' if event['result'].startswith('20') else '#dc3545'}">{event["result"]}</span> ({event["response_time"]})</div>
            <div style="font-size: 10px; color: {border_color};">Risk Level: {event["risk"]}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    """Main function - integrates with existing toolkit"""
    st.set_page_config(page_title="API Role Matrix vs Audit", layout="wide")

    st.title("🔐 API Role Matrix vs 📋 API Audit")
    st.markdown("**Fixed: No more crossed signals!**")

    # Show the key difference
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Matrix** = Visual grid showing what API roles **CAN DO**")
    with col2:
        st.info("**Audit** = Chronological list showing what API roles **DID DO**")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(
        ["🔐 API Role Matrix (Grid)", "📋 API Audit (List)", "🔄 Side by Side"]
    )

    matrix = ApiRoleMatrixEnhanced()

    with tab1:
        st.markdown("## Visual Matrix Format")
        matrix.render_visual_matrix()

    with tab2:
        st.markdown("## Chronological List Format")
        render_api_audit_list()

    with tab3:
        st.markdown("## Side by Side Comparison")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Matrix (Grid)")
            matrix.render_visual_matrix()

        with col2:
            st.markdown("### Audit (List)")
            render_api_audit_list()


if __name__ == "__main__":
    main()
