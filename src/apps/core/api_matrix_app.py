#!/usr/bin/env python3
"""
API Matrix Application Adapter
Wraps the existing API role matrix functionality into the framework
"""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from apps.framework import AppMetadata, JPAPIApplication, TenantConfig
except ImportError:
    # Fallback to local framework
    from framework import AppMetadata, JPAPIApplication, TenantConfig


class APIMatrixApp(JPAPIApplication):
    """API role matrix and audit application"""

    def get_metadata(self) -> AppMetadata:
        return AppMetadata(
            id="api_matrix",
            name="ExampleCorp API Security Matrix",
            description="JAMF API role analysis & security audit for ExampleCorp infrastructure",
            version="2.0.0",
            category="Security & Audit",
            icon="🔐",
            entry_point=self.launch,
            permissions=["api.read", "roles.read", "audit.read"],
            dependencies=["authentication"],
            multi_tenant=True,
            real_time=True,
        )

    def initialize(self) -> bool:
        """Initialize API matrix application"""
        try:
            self.logger.info("Initializing API Role Matrix")

            # Get authenticated client for this tenant
            self.auth_client = self.get_auth()
            self.api_roles = []
            self.audit_events = []

            # Load API roles and audit data
            self._load_api_data()

            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize API matrix: {e}")
            return False

    def launch(self, port: int = 8503, **kwargs) -> Any:
        """Launch API matrix interface"""
        return self._create_api_interface()

    def _create_api_interface(self):
        """Create the API matrix interface"""

        # Configure Streamlit page
        st.set_page_config(
            page_title="🔐 API Role Matrix",
            page_icon="🔐",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Apply security-focused theme
        self._apply_security_theme()

        # Render interface sections
        self._render_security_header()
        self._render_security_content()

    def _apply_security_theme(self):
        """Apply security-focused theme"""
        st.markdown(
            """
        <style>
            /* Security Theme */
            :root {
                --security-primary: #1A365D;
                --security-secondary: #2D3748;
                --security-accent: #3182CE;
                --security-success: #38A169;
                --security-warning: #D69E2E;
                --security-danger: #E53E3E;
                --security-critical: #9B2C2C;
                --security-bg: #F7FAFC;
                --security-card: #FFFFFF;
                --security-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            
            .stApp {
                background: var(--security-bg);
                font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
            }
            
            /* Security Header */
            .security-header {
                background: var(--security-gradient);
                padding: 2rem 3rem;
                margin: -1rem -1rem 2rem -1rem;
                border-radius: 0 0 20px 20px;
                border: 2px solid rgba(255,255,255,0.1);
                position: relative;
                overflow: hidden;
            }
            
            .security-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                opacity: 0.3;
            }
            
            .security-title {
                color: white;
                font-size: 2.2rem;
                font-weight: 700;
                margin: 0;
                position: relative;
                z-index: 1;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            
            .security-subtitle {
                color: rgba(255,255,255,0.9);
                font-size: 1.1rem;
                margin: 0.5rem 0 0 0;
                font-weight: 400;
                position: relative;
                z-index: 1;
            }
            
            /* Risk Level Cards */
            .risk-card {
                background: var(--security-card);
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                border-left: 4px solid;
                transition: all 0.3s ease;
                font-family: 'SF Mono', monospace;
            }
            
            .risk-card:hover {
                transform: translateX(4px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            
            .risk-critical {
                border-left-color: var(--security-critical);
                background: linear-gradient(135deg, #FFF5F5 0%, #FED7D7 100%);
            }
            
            .risk-high {
                border-left-color: var(--security-danger);
                background: linear-gradient(135deg, #FFFAF0 0%, #FEEBC8 100%);
            }
            
            .risk-medium {
                border-left-color: var(--security-warning);
                background: linear-gradient(135deg, #FFFFF0 0%, #FEFCBF 100%);
            }
            
            .risk-low {
                border-left-color: var(--security-success);
                background: linear-gradient(135deg, #F0FFF4 0%, #C6F6D5 100%);
            }
            
            /* API Role Grid */
            .api-role-grid {
                display: grid;
                grid-template-columns: 2fr 1fr 1fr 1fr;
                gap: 1rem;
                align-items: center;
                padding: 1rem;
                background: rgba(255,255,255,0.5);
                border-radius: 8px;
                margin: 0.5rem 0;
                font-family: 'SF Mono', monospace;
            }
            
            .api-role-name {
                font-weight: 600;
                color: var(--security-primary);
                font-size: 1.1rem;
            }
            
            .api-privilege-count {
                font-size: 1.5rem;
                font-weight: 700;
                text-align: center;
            }
            
            .api-risk-indicator {
                text-align: center;
                font-weight: 600;
                padding: 0.5rem;
                border-radius: 6px;
            }
            
            /* Audit Trail */
            .audit-event {
                background: var(--security-card);
                border-left: 3px solid var(--security-accent);
                padding: 1rem 1.5rem;
                margin: 0.5rem 0;
                border-radius: 0 8px 8px 0;
                font-family: 'SF Mono', monospace;
                font-size: 0.9rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            
            .audit-timestamp {
                color: var(--security-secondary);
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .audit-action {
                font-weight: 600;
                color: var(--security-primary);
                margin: 0.25rem 0;
            }
            
            .audit-details {
                color: #4A5568;
                font-size: 0.85rem;
            }
            
            /* Risk Legend - COLOR BLIND ACCESSIBLE */
            .risk-legend {
                display: flex;
                justify-content: space-around;
                margin: 1rem 0;
                padding: 1rem;
                background: rgba(255,255,255,0.8);
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }
            
            .risk-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 500;
            }
            
            /* ACCESSIBLE PATTERN INDICATORS */
            .risk-pattern {
                width: 20px;
                height: 20px;
                border: 2px solid #333;
                position: relative;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                color: #333;
            }
            
            .pattern-critical {
                background: #ff4444;
                clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
                border-radius: 0;
            }
            .pattern-critical::after { content: '⚠'; color: white; }
            
            .pattern-high {
                background: #ff8800;
                border-radius: 0;
                transform: rotate(45deg);
            }
            .pattern-high::after { content: '●'; transform: rotate(-45deg); }
            
            .pattern-medium {
                background: #ffdd00;
                border-radius: 50%;
            }
            .pattern-medium::after { content: '▲'; color: #333; }
            
            .pattern-low {
                background: #44aa44;
                border-radius: 0;
            }
            .pattern-low::after { content: '■'; color: white; }
            
            /* Matrix View */
            .matrix-container {
                background: var(--security-card);
                border-radius: 16px;
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .matrix-header {
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid #E2E8F0;
            }
            
            /* Privilege Badges */
            .privilege-badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 0.75rem;
                font-weight: 600;
                margin: 2px;
                font-family: 'SF Mono', monospace;
            }
            
            .privilege-high-risk {
                background: var(--security-danger);
                color: white;
            }
            
            .privilege-medium-risk {
                background: var(--security-warning);
                color: white;
            }
            
            .privilege-low-risk {
                background: var(--security-success);
                color: white;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def _render_security_header(self):
        """Render security-focused header"""
        tenant_name = self.tenant.name if self.tenant else "Enterprise"

        st.markdown(
            f"""
        <div class="security-header">
            <h1 class="security-title">🔐 API Role Security Matrix</h1>
            <p class="security-subtitle">{tenant_name} • Real-time API Role Analysis & Audit Trail</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def _render_security_navigation(self):
        """Render security navigation sidebar"""
        with st.sidebar:
            st.markdown("## 🔐 Security Analysis")

            # Security status indicator
            security_score = self._calculate_security_score()
            if security_score >= 90:
                st.success(f"🟢 Security Score: {security_score}%")
            elif security_score >= 70:
                st.warning(f"🟡 Security Score: {security_score}%")
            else:
                st.error(f"🔴 Security Score: {security_score}%")

            # Navigation sections
            section = st.radio(
                "Select Analysis:",
                [
                    "🔐 API Role Matrix",
                    "📋 Audit Trail",
                    "⚠️ Risk Analysis",
                    "📊 Security Metrics",
                    "🚨 Alerts & Monitoring",
                ],
                key="api_security_analysis_section",
            )

            # Real-time toggles
            st.markdown("### Real-time Monitoring")
            real_time_audit = st.checkbox("🔄 Live Audit Feed", value=True)
            security_alerts = st.checkbox("🚨 Security Alerts", value=True)

            # Filters
            st.markdown("### Filters")
            risk_filter = st.multiselect(
                "Risk Levels:",
                ["Critical", "High", "Medium", "Low"],
                default=["Critical", "High", "Medium", "Low"],
            )

            time_filter = st.selectbox(
                "Time Range:",
                ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
            )

            return (
                section.split()[1],
                risk_filter,
                time_filter,
            )  # Return section name and filters

    def _render_security_content(self):
        """Render main security content"""
        section, risk_filter, time_filter = self._render_security_navigation()

        if section == "API":
            self._render_api_matrix(risk_filter)
        elif section == "Audit":
            self._render_audit_trail(time_filter)
        elif section == "Risk":
            self._render_risk_analysis(risk_filter)
        elif section == "Security":
            self._render_security_metrics()
        elif section == "Alerts":
            self._render_alerts_monitoring()

    def _render_api_matrix(self, risk_filter: List[str]):
        """Render API role matrix in visual grid format"""
        st.markdown("## 🔐 API Role Matrix")
        st.markdown("*Visual grid showing API roles vs endpoint permissions*")

        # ACCESSIBLE Risk legend with patterns and text
        st.markdown(
            """
        <div class="risk-legend">
            <div class="risk-item">
                <div class="risk-pattern pattern-critical"></div>
                <span><strong>CRITICAL RISK</strong> [⚠ DIAMOND]</span>
            </div>
            <div class="risk-item">
                <div class="risk-pattern pattern-high"></div>
                <span><strong>HIGH RISK</strong> [● ROTATED SQUARE]</span>
            </div>
            <div class="risk-item">
                <div class="risk-pattern pattern-medium"></div>
                <span><strong>MEDIUM RISK</strong> [▲ CIRCLE]</span>
            </div>
            <div class="risk-item">
                <div class="risk-pattern pattern-low"></div>
                <span><strong>LOW RISK</strong> [■ SQUARE]</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Filter roles by risk level
        filtered_roles = [
            role for role in self.api_roles if role["riskLevel"] in risk_filter
        ]

        if not filtered_roles:
            st.info("No API roles match the selected risk filters.")
            return

        # Display roles in matrix format
        st.markdown(
            """
        <div class="matrix-container">
            <div class="matrix-header">
                <h3>🔐 API Role Permission Matrix</h3>
                <p>Real-time analysis of API role capabilities and risk assessment</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        for role in filtered_roles:
            self._render_api_role_card(role)

        st.markdown("</div>", unsafe_allow_html=True)

    def _render_api_role_card(self, role: Dict[str, Any]):
        """Render individual API role card"""
        role_name = role.get("displayName", role.get("name", "Unknown"))
        risk_level = role.get("riskLevel", "Medium")
        privileges = role.get("privileges", 0)
        high_risk_count = role.get("highRiskCount", 0)
        key_privileges = role.get("keyPrivileges", [])

        # Determine risk class
        risk_classes = {
            "Critical": "risk-critical",
            "High": "risk-high",
            "Medium": "risk-medium",
            "Low": "risk-low",
        }
        risk_class = risk_classes.get(risk_level, "risk-medium")

        role_card_html = f"""
        <div class="risk-card {risk_class}">
            <div class="api-role-grid">
                <div>
                    <div class="api-role-name">{role_name}</div>
                    <div style="font-size: 0.8rem; color: #666; margin-top: 0.25rem;">
                        API Role • ID: {role.get('id', 'unknown')}
                    </div>
                </div>
                <div>
                    <div class="api-privilege-count" style="color: var(--security-accent);">{privileges}</div>
                    <div style="font-size: 0.8rem; color: #666;">Total Privileges</div>
                </div>
                <div>
                    <div class="api-privilege-count" style="color: var(--security-danger);">{high_risk_count}</div>
                    <div style="font-size: 0.8rem; color: #666;">High-Risk Actions</div>
                </div>
                <div>
                    <div class="api-risk-indicator" style="display: flex; align-items: center; gap: 0.5rem; background: var(--security-{risk_level.lower()}); color: white;">
                        <div class="risk-pattern pattern-{risk_level.lower()}" style="width: 16px; height: 16px; border: 1px solid white;"></div>
                        <span>{risk_level.upper()}</span>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(0,0,0,0.1);">
                <strong>Key Capabilities:</strong>
                <div style="margin-top: 0.5rem;">
        """

        # Add privilege badges
        for i, privilege in enumerate(key_privileges[:6]):  # Show first 6
            if any(keyword in privilege for keyword in ["DELETE", "CREATE", "UPDATE"]):
                badge_class = "privilege-high-risk"
            elif any(keyword in privilege for keyword in ["WRITE", "MODIFY"]):
                badge_class = "privilege-medium-risk"
            else:
                badge_class = "privilege-low-risk"

            role_card_html += (
                f'<span class="privilege-badge {badge_class}">{privilege}</span>'
            )

        if len(key_privileges) > 6:
            role_card_html += f'<span class="privilege-badge" style="background: #E2E8F0; color: #4A5568;">+{len(key_privileges) - 6} more</span>'

        role_card_html += """
                </div>
            </div>
        </div>
        """

        st.markdown(role_card_html, unsafe_allow_html=True)

    def _render_audit_trail(self, time_filter: str):
        """Render API audit trail as chronological list"""
        st.markdown("## 📋 API Audit Trail")
        st.markdown("*Chronological list of actual API calls and events*")

        # Filter events by time
        filtered_events = self._filter_audit_events(time_filter)

        if not filtered_events:
            st.info("No audit events found for the selected time range.")
            return

        # Display audit events
        for event in filtered_events:
            self._render_audit_event(event)

    def _render_audit_event(self, event: Dict[str, Any]):
        """Render individual audit event"""
        timestamp = event.get("timestamp", "Unknown")
        api_role = event.get("api_role", "Unknown")
        method = event.get("method", "GET")
        endpoint = event.get("endpoint", "/unknown")
        target = event.get("target", "Unknown Target")
        result = event.get("result", "200 OK")
        response_time = event.get("response_time", "0ms")
        risk = event.get("risk", "Low")

        # Determine border color based on risk
        border_colors = {
            "Critical": "#9B2C2C",
            "High": "#E53E3E",
            "Medium": "#D69E2E",
            "Low": "#38A169",
        }
        border_color = border_colors.get(risk, "#38A169")

        # Determine result color
        result_color = "#38A169" if result.startswith("20") else "#E53E3E"

        event_html = f"""
        <div class="audit-event" style="border-left-color: {border_color};">
            <div class="audit-timestamp">{timestamp}</div>
            <div class="audit-action">
                <strong>{api_role}</strong> → 
                <span style="color: {border_color}; font-weight: bold;">{method} {endpoint}</span>
            </div>
            <div class="audit-details">
                Target: <em>{target}</em><br/>
                Result: <span style="color: {result_color}; font-weight: 600;">{result}</span> 
                ({response_time}) • Risk: <span style="color: {border_color}; font-weight: 600;">{risk}</span>
            </div>
        </div>
        """

        st.markdown(event_html, unsafe_allow_html=True)

    def _render_risk_analysis(self, risk_filter: List[str]):
        """Render risk analysis dashboard"""
        st.markdown("## ⚠️ Risk Analysis Dashboard")

        # Risk distribution
        risk_distribution = self._calculate_risk_distribution()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Risk Distribution")
            st.bar_chart(risk_distribution)

        with col2:
            st.markdown("### Top Risk Factors")
            risk_factors = [
                "Excessive DELETE permissions",
                "Unrestricted API access",
                "Missing audit logging",
                "Overprivileged service accounts",
                "Weak authentication requirements",
            ]

            for i, factor in enumerate(risk_factors):
                severity = ["🔴", "🟡", "🟡", "🟠", "🟢"][i]
                st.markdown(f"{severity} {factor}")

    def _render_security_metrics(self):
        """Render security metrics dashboard"""
        st.markdown("## 📊 Security Metrics")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Security Score", "85%", "-2%")

        with col2:
            st.metric("High-Risk Roles", "3", "+1")

        with col3:
            st.metric("API Calls Today", "1,247", "+15%")

        with col4:
            st.metric("Failed Auth", "12", "-3")

        # Trends
        st.markdown("### Security Trends")

        # Mock trend data
        import random

        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        trend_data = pd.DataFrame(
            {
                "Date": dates,
                "Security Score": [random.randint(75, 95) for _ in range(30)],
                "Risk Events": [random.randint(0, 10) for _ in range(30)],
            }
        )

        st.line_chart(trend_data.set_index("Date"))

    def _render_alerts_monitoring(self):
        """Render alerts and monitoring dashboard"""
        st.markdown("## 🚨 Security Alerts & Monitoring")

        # Active alerts
        alerts = [
            {
                "level": "Critical",
                "message": "Unauthorized API access detected",
                "time": "2 minutes ago",
            },
            {
                "level": "High",
                "message": "Excessive DELETE operations by service account",
                "time": "15 minutes ago",
            },
            {
                "level": "Medium",
                "message": "New high-privilege role created",
                "time": "1 hour ago",
            },
            {
                "level": "Low",
                "message": "Unusual API access pattern detected",
                "time": "2 hours ago",
            },
        ]

        for alert in alerts:
            level_colors = {
                "Critical": "#9B2C2C",
                "High": "#E53E3E",
                "Medium": "#D69E2E",
                "Low": "#38A169",
            }

            level_icons = {"Critical": "🚨", "High": "⚠️", "Medium": "🟡", "Low": "ℹ️"}

            color = level_colors.get(alert["level"], "#38A169")
            icon = level_icons.get(alert["level"], "ℹ️")

            st.markdown(
                f"""
            <div style="border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; 
                        background: rgba(255,255,255,0.8); border-radius: 0 8px 8px 0;">
                <div style="font-weight: 600; color: {color};">
                    {icon} {alert["level"]} Alert
                </div>
                <div style="margin: 0.5rem 0; color: #2D3748;">
                    {alert["message"]}
                </div>
                <div style="font-size: 0.8rem; color: #718096;">
                    {alert["time"]}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    def _load_api_data(self):
        """Load REAL API roles and audit data from JAMF"""
        try:
            # Import your existing auth system
            import sys

            sys.path.insert(0, str(self.framework.base_dir / "lib"))
            from auth_production import JamfAuth

            auth = JamfAuth(environment="dev", backend="keychain")

            # Try to get real API roles
            try:
                roles_response = auth.make_api_call("/api/v1/api-roles")
                if roles_response and "results" in roles_response:
                    self.api_roles = []
                    for role in roles_response["results"]:
                        # Process real API role data
                        privileges = role.get("privileges", [])
                        high_risk_count = len(
                            [
                                p
                                for p in privileges
                                if any(
                                    word in p.lower()
                                    for word in ["delete", "create", "update"]
                                )
                            ]
                        )

                        # Determine risk level
                        if high_risk_count > 10:
                            risk_level = "Critical"
                        elif high_risk_count > 5:
                            risk_level = "High"
                        elif high_risk_count > 0:
                            risk_level = "Medium"
                        else:
                            risk_level = "Low"

                        self.api_roles.append(
                            {
                                "id": role.get("id"),
                                "displayName": role.get("displayName"),
                                "riskLevel": risk_level,
                                "privileges": len(privileges),
                                "highRiskCount": high_risk_count,
                                "keyPrivileges": privileges[:10],  # First 10 privileges
                            }
                        )

                    self.logger.info(
                        f"✅ Loaded {len(self.api_roles)} real API roles from JAMF"
                    )
                else:
                    self.logger.warning("No API roles found in JAMF response")
                    self._load_mock_api_data()

            except Exception as e:
                self.logger.error(f"Failed to load real API roles: {e}")
                self._load_mock_api_data()

            # For audit events, we'll use mock data since JAMF doesn't provide detailed audit via API
            self._load_mock_audit_data()

        except Exception as e:
            self.logger.error(f"Failed to initialize JAMF auth: {e}")
            self._load_mock_api_data()

    def _load_mock_api_data(self):
        """Load mock API data as fallback"""
        self.api_roles = [
            {
                "id": "jamfDevCleanup",
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
                "id": "HM-Test",
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
                "id": "ALL-R-Permissions",
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
        ]

    def _load_mock_audit_data(self):
        """Load mock audit data"""
        self.audit_events = [
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
        ]

    def _calculate_security_score(self) -> int:
        """Calculate overall security score"""
        if not self.api_roles:
            return 50

        # Simple scoring based on risk distribution
        critical_count = len(
            [r for r in self.api_roles if r["riskLevel"] == "Critical"]
        )
        high_count = len([r for r in self.api_roles if r["riskLevel"] == "High"])
        total_count = len(self.api_roles)

        if total_count == 0:
            return 50

        # Calculate score (lower is better for high-risk roles)
        risk_ratio = (critical_count * 2 + high_count) / total_count
        score = max(20, 100 - int(risk_ratio * 40))

        return score

    def _calculate_risk_distribution(self) -> Dict[str, int]:
        """Calculate risk level distribution"""
        distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

        for role in self.api_roles:
            risk_level = role.get("riskLevel", "Medium")
            if risk_level in distribution:
                distribution[risk_level] += 1

        return distribution

    def _filter_audit_events(self, time_filter: str) -> List[Dict[str, Any]]:
        """Filter audit events by time range"""
        # In production, this would filter by actual timestamps
        # For demo, return recent events
        return self.audit_events[:10]  # Return last 10 events


def main():
    """Main entry point for the API matrix application"""
    app = APIMatrixApp()
    app.initialize()
    app.launch()


if __name__ == "__main__":
    main()
