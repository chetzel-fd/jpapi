#!/usr/bin/env python3
"""
Apple-styled JAMF Dashboard with LIVE DATA and Reverse Relationship Bubbles
Tim Cook-approved design with comprehensive object relationship analysis
"""
import streamlit as st
import sys
import os
import json
import webbrowser
from datetime import datetime
from pathlib import Path

# Add lib directory to path for authentication
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "lib"))

# Import with fallback for missing modules
try:
    from auth_production import JamfAuth

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

    class JamfAuth:
        def __init__(self, *args, **kwargs):
            pass

        def authenticate(self, *args, **kwargs):
            return False


try:
    from reverse_relationships import ReverseRelationshipLookup

    REVERSE_LOOKUP_AVAILABLE = True
except ImportError:
    REVERSE_LOOKUP_AVAILABLE = False

    class ReverseRelationshipLookup:
        def __init__(self, *args, **kwargs):
            pass


# Apple-style page config
st.set_page_config(
    page_title="JAMF Pro Dashboard",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tim Cook-approved Apple CSS with enhanced relationship bubbles
st.markdown(
    """
<style>
    /* Apple system fonts */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', sans-serif;
        background: #F2F2F7;
        font-feature-settings: 'kern' on, 'liga' on;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Hide Streamlit branding but keep functionality */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main > div {
        padding-top: 1rem;
        max-width: none !important;
    }
    
    /* Apple-style cards with enhanced shadows */
    .object-card {
        background: #FFFFFF;
        padding: 24px;
        border-radius: 20px;
        border: 0.33px solid rgba(60, 60, 67, 0.29);
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .object-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12);
    }
    
    .apple-header {
        background: linear-gradient(145deg, #FFFFFF 0%, #F8F9FA 100%);
        padding: 28px 36px;
        border-radius: 24px;
        margin-bottom: 28px;
        border: 0.33px solid rgba(60, 60, 67, 0.29);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    .connection-status {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 16px;
        font-size: 14px;
        font-weight: 600;
        margin-left: 16px;
        letter-spacing: 0.2px;
    }
    
    .status-live {
        background: #34C759;
        color: white;
    }
    
    .status-mock {
        background: #FF9500;
        color: white;
    }
    
    .status-error {
        background: #FF3B30;
        color: white;
    }
    
    .stat-card {
        background: #FFFFFF;
        padding: 28px;
        border-radius: 20px;
        border: 0.33px solid rgba(60, 60, 67, 0.29);
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: all 0.35s cubic-bezier(0.23, 1, 0.32, 1);
    }
    
    .stat-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    .stat-number {
        font-size: 42px;
        font-weight: 200;
        color: #000000;
        letter-spacing: -1.2px;
        margin: 0;
        line-height: 1;
    }
    
    .stat-label {
        color: #3C3C43;
        font-size: 17px;
        opacity: 0.8;
        margin-top: 8px;
        font-weight: 500;
    }
    
    .object-title {
        font-size: 22px;
        font-weight: 600;
        color: #000000;
        margin-bottom: 12px;
        letter-spacing: -0.4px;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
    }
    
    .object-title span {
        flex: 1;
        line-height: 1.3;
    }
    
    .bubbles-container {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        align-items: flex-start;
        justify-content: flex-end;
        max-width: 200px;
    }
    
    .object-meta {
        color: #3C3C43;
        font-size: 16px;
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        margin-bottom: 16px;
        opacity: 0.8;
    }
    
    .relationship-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid rgba(60, 60, 67, 0.29);
    }
    
    .relationship-chip {
        background: #007AFF;
        color: white;
        padding: 8px 16px;
        border-radius: 14px;
        font-size: 14px;
        font-weight: 600;
        display: inline-block;
        white-space: nowrap;
        letter-spacing: 0.1px;
        box-shadow: 0 2px 4px rgba(0, 122, 255, 0.3);
    }
    
    /* Enhanced relationship bubbles */
    .usage-bubble {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 14px;
        font-size: 13px;
        font-weight: 700;
        margin: 0 4px;
        color: white;
        text-align: center;
        min-width: 28px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        position: relative;
    }
    
    .usage-bubble:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    
    /* Apple's official colors for bubbles */
    .usage-policies { 
        background: linear-gradient(135deg, #FF3B30 0%, #FF9500 100%);
        box-shadow: 0 2px 8px rgba(255, 59, 48, 0.4);
    }
    .usage-profiles { 
        background: linear-gradient(135deg, #34C759 0%, #30D158 100%);
        box-shadow: 0 2px 8px rgba(52, 199, 89, 0.4);
    }
    .usage-scripts { 
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        box-shadow: 0 2px 8px rgba(0, 122, 255, 0.4);
    }
    .usage-packages { 
        background: linear-gradient(135deg, #FF9500 0%, #FFCC02 100%);
        box-shadow: 0 2px 8px rgba(255, 149, 0, 0.4);
    }
    .usage-groups { 
        background: linear-gradient(135deg, #AF52DE 0%, #FF45B5 100%);
        box-shadow: 0 2px 8px rgba(175, 82, 222, 0.4);
    }
    .usage-total { 
        background: linear-gradient(135deg, #8E8E93 0%, #636366 100%);
        box-shadow: 0 2px 8px rgba(142, 142, 147, 0.4);
    }
    
    .status-enabled {
        color: #34C759;
        font-weight: 600;
    }
    .status-disabled {
        color: #FF3B30;
        font-weight: 600;
    }
    
    .category-badge {
        background: rgba(0, 122, 255, 0.15);
        color: #007AFF;
        padding: 6px 12px;
        border-radius: 10px;
        font-size: 14px;
        font-weight: 500;
    }
    
    /* Apple sidebar styling */
    .css-1d391kg {
        background: #FFFFFF !important;
        border-right: 0.33px solid rgba(60, 60, 67, 0.29) !important;
    }
    
    .stSelectbox > div > div {
        background: #FFFFFF;
        border: 0.33px solid rgba(60, 60, 67, 0.29);
        border-radius: 12px;
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
    }
    
    h1 {
        color: #000000 !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px !important;
    }
    
    h2 {
        color: #3C3C43 !important;
        font-weight: 500 !important;
        letter-spacing: -0.3px !important;
    }
    
    h3 {
        color: #3C3C43 !important;
        font-weight: 500 !important;
        letter-spacing: -0.2px !important;
    }
    
    /* Relationship sections and buttons */
    .relationship-section {
        margin: 16px 0;
        padding: 16px;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        border: 0.33px solid rgba(60, 60, 67, 0.29);
    }
    
    .relationship-section h4 {
        color: #000000;
        font-size: 16px;
        font-weight: 600;
        margin: 0 0 12px 0;
        letter-spacing: -0.2px;
    }
    
    .relationship-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .relationship-button {
        background: #FFFFFF;
        border: 1px solid rgba(60, 60, 67, 0.29);
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 13px;
        font-weight: 500;
        color: #3C3C43;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .relationship-button:hover {
        background: #F0F0F0;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    
    .package-btn {
        border-left: 4px solid #FF9500;
    }
    
    .script-btn {
        border-left: 4px solid #007AFF;
    }
    
    .group-btn {
        border-left: 4px solid #AF52DE;
    }
    
    .computer-btn {
        border-left: 4px solid #34C759;
    }
    
    /* Compact relationship bubbles */
    .relation-bubble {
        display: inline-block;
        background: #FFFFFF;
        border: 1px solid rgba(60, 60, 67, 0.29);
        border-radius: 16px;
        padding: 4px 10px;
        margin: 0 4px 4px 0;
        font-size: 12px;
        font-weight: 600;
        color: #3C3C43;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        letter-spacing: -0.1px;
    }
    
    .relation-bubble:hover {
        background: #F2F2F7;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    
    .package-bubble {
        background: rgba(255, 149, 0, 0.1);
        border-color: #FF9500;
        color: #D2691E;
    }
    
    .script-bubble {
        background: rgba(0, 122, 255, 0.1);
        border-color: #007AFF;
        color: #0056B3;
    }
    
    .group-bubble {
        background: rgba(175, 82, 222, 0.1);
        border-color: #AF52DE;
        color: #8E44AD;
    }
    
    .computer-bubble {
        background: rgba(52, 199, 89, 0.1);
        border-color: #34C759;
        color: #27AE60;
    }
    
    .policy-bubble {
        background: rgba(255, 59, 48, 0.1);
        border-color: #FF3B30;
        color: #E74C3C;
    }
    
    .profile-bubble {
        background: rgba(255, 149, 0, 0.1);
        border-color: #FF9500;
        color: #D2691E;
    }
    
    .payload-bubble {
        background: rgba(88, 86, 214, 0.1);
        border-color: #5856D6;
        color: #6B5B95;
    }
    
    .debug-bubble {
        background: rgba(255, 204, 0, 0.1);
        border-color: #FFCC00;
        color: #B8860B;
    }
    
    /* Clickable bubble enhancements */
    .clickable-bubble {
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .clickable-bubble:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    
    .clickable-bubble:active {
        transform: translateY(0) scale(1.02);
    }
    
    /* Tooltip for bubbles */
    .relation-bubble[title]:hover::after {
        content: attr(title);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 500;
        white-space: nowrap;
        z-index: 1000;
        margin-bottom: 6px;
        letter-spacing: 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


def load_shared_viewer_state():
    """Load shared state from other viewers"""
    try:
        state_file = os.path.expanduser("~/.jamf_viewer_state.json")
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_shared_viewer_state(state_data):
    """Save shared state for other viewers"""
    try:
        state_file = os.path.expanduser("~/.jamf_viewer_state.json")
        state_data["timestamp"] = datetime.now().isoformat()
        state_data["source"] = "apple_dashboard"
        with open(state_file, "w") as f:
            json.dump(state_data, f)
    except Exception:
        pass


def get_connection_status(auth):
    """Get and display connection status from real JAMF production auth"""
    try:
        # Test connection with a simple API call
        response = auth.make_api_call("/JSSResource/categories")
        if response and (isinstance(response, dict) and len(response) > 0):
            return {
                "status": "live",
                "message": "✅ Connected to Live JAMF Pro",
                "server": auth.environment,
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ JAMF Pro Connection Error: {str(e)[:50]}...",
            "server": auth.environment,
        }

    return {
        "status": "error",
        "message": "⚠️ JAMF Pro Connection Failed - Check credentials",
        "server": auth.environment,
    }


def render_apple_header(auth, show_connection_status=False):
    """Render Apple-style header with optional connection status"""
    if show_connection_status:
        status = get_connection_status(auth)
        status_class = f"status-{status['status']}"
    else:
        # Fast loading: Skip connection check for initial render
        status = {
            "status": "pending",
            "message": "🔄 Ready to connect",
            "server": "dev",
        }
        status_class = "status-pending"

    st.markdown(
        f"""
    <div class="apple-header">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 style="margin: 0; font-size: 32px;">🍎 JAMF Pro Dashboard</h1>
                <p style="margin: 8px 0 0 0; color: #3C3C43; opacity: 0.8; font-size: 19px;">
                    Enterprise Device Management • Live Data Explorer
                </p>
                <p style="margin: 6px 0 0 0; color: #8E8E93; font-size: 16px;">
                    Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
            <div class="connection-status {status_class}">
                {status['message']}
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_stats_dashboard(auth, key_suffix=""):
    """Render Apple-style clickable statistics dashboard with live data"""
    try:
        # Load data from all object types using real JAMF API endpoints
        policies_response = auth.make_api_call("/JSSResource/policies")
        scripts_response = auth.make_api_call("/JSSResource/scripts")
        packages_response = auth.make_api_call("/JSSResource/packages")
        groups_response = auth.make_api_call("/JSSResource/computergroups")

        policies = policies_response.get("policies", []) if policies_response else []
        scripts = scripts_response.get("scripts", []) if scripts_response else []
        packages = packages_response.get("packages", []) if packages_response else []
        groups = groups_response.get("computer_groups", []) if groups_response else []

        enabled_policies = len([p for p in policies if p.get("enabled", True)])
        smart_groups = len([g for g in groups if g.get("is_smart", False)])

        # Create clickable stat cards
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            # Highlight current selection
            button_style = (
                "🔥" if st.session_state.selected_object_type == "policies" else "📋"
            )
            if st.button(
                f"{button_style} {len(policies)}\nPolicies\n{enabled_policies} enabled",
                key="nav_policies",
                help="Click to view all policies",
                type=(
                    "primary"
                    if st.session_state.selected_object_type == "policies"
                    else "secondary"
                ),
            ):
                st.session_state.selected_object_type = "policies"
                st.success("🔄 Loading Policies...")
                st.rerun()

        with col2:
            button_style = (
                "🔥" if st.session_state.selected_object_type == "scripts" else "⚙️"
            )
            if st.button(
                f"{button_style} {len(scripts)}\nScripts\nFor policies",
                key="nav_scripts",
                help="Click to view all scripts",
                type=(
                    "primary"
                    if st.session_state.selected_object_type == "scripts"
                    else "secondary"
                ),
            ):
                st.session_state.selected_object_type = "scripts"
                st.success("🔄 Loading Scripts...")
                st.rerun()

        with col3:
            button_style = (
                "🔥" if st.session_state.selected_object_type == "packages" else "📦"
            )
            if st.button(
                f"{button_style} {len(packages)}\nPackages\nFor deployment",
                key="nav_packages",
                help="Click to view all packages",
                type=(
                    "primary"
                    if st.session_state.selected_object_type == "packages"
                    else "secondary"
                ),
            ):
                st.session_state.selected_object_type = "packages"
                st.success("🔄 Loading Packages...")
                st.rerun()

        with col4:
            button_style = (
                "🔥" if st.session_state.selected_object_type == "groups" else "👥"
            )
            if st.button(
                f"{button_style} {len(groups)}\nGroups\n{smart_groups} smart",
                key="nav_groups",
                help="Click to view all computer groups",
                type=(
                    "primary"
                    if st.session_state.selected_object_type == "groups"
                    else "secondary"
                ),
            ):
                st.session_state.selected_object_type = "groups"
                st.success("🔄 Loading Groups...")
                st.rerun()

        with col5:
            # Get profiles count
            try:
                profiles_response = auth.make_api_call(
                    "/JSSResource/osxconfigurationprofiles"
                )
                profiles = (
                    profiles_response.get("os_x_configuration_profiles", [])
                    if profiles_response
                    else []
                )
                button_style = (
                    "🔥"
                    if st.session_state.selected_object_type == "profiles"
                    else "🔧"
                )
                if st.button(
                    f"{button_style} {len(profiles)}\nProfiles\nConfiguration",
                    key="nav_profiles",
                    help="Click to view all configuration profiles",
                    type=(
                        "primary"
                        if st.session_state.selected_object_type == "profiles"
                        else "secondary"
                    ),
                ):
                    st.session_state.selected_object_type = "profiles"
                    st.success("🔄 Loading Profiles...")
                    st.rerun()
            except:
                button_style = (
                    "🔥"
                    if st.session_state.selected_object_type == "profiles"
                    else "🔧"
                )
                if st.button(
                    f"{button_style} 0\nProfiles\nConfiguration",
                    key="nav_profiles",
                    help="Click to view all configuration profiles",
                    type=(
                        "primary"
                        if st.session_state.selected_object_type == "profiles"
                        else "secondary"
                    ),
                ):
                    st.session_state.selected_object_type = "profiles"
                    st.success("🔄 Loading Profiles...")
                    st.rerun()

    except Exception as e:
        st.error(f"⚠️ Error loading statistics: {e}")


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_object_data(object_type):
    """Get object data and cache it for better performance"""
    try:
        auth = JamfAuth(environment="dev")
        endpoints = {
            "policies": "/JSSResource/policies",
            "scripts": "/JSSResource/scripts",
            "packages": "/JSSResource/packages",
            "groups": "/JSSResource/computergroups",
            "profiles": "/JSSResource/osxconfigurationprofiles",
        }

        # Map response keys (some APIs use different keys than the object type)
        response_keys = {
            "policies": "policies",
            "scripts": "scripts",
            "packages": "packages",
            "groups": "computer_groups",
            "profiles": "os_x_configuration_profiles",
        }

        if object_type in endpoints:
            response = auth.make_api_call(endpoints[object_type])
            if response:
                data_key = response_keys.get(object_type, object_type)
                return response.get(data_key, [])
        return []
    except Exception as e:
        return []


@st.cache_data(
    ttl=1800, show_spinner=False
)  # Cache for 30 minutes (production-optimized)
def get_cached_relationship_data(analysis_depth="standard", smart_filter="recent"):
    """Get enterprise-scale relationship data with smart filtering and configurable depth"""
    try:
        import datetime

        auth = JamfAuth(environment="dev")

        # PRODUCTION-OPTIMIZED LIMITS based on analysis depth
        limits = {
            "quick": {"policies": 50, "profiles": 25},  # 2-3 minutes load
            "standard": {"policies": 150, "profiles": 75},  # 5-7 minutes load
            "comprehensive": {"policies": 300, "profiles": 150},  # 10-15 minutes load
            "enterprise": {"policies": 500, "profiles": 250},  # 20+ minutes load
        }

        selected_limits = limits.get(analysis_depth, limits["standard"])

        # Smart filtering options
        now = datetime.datetime.now()
        thirty_days_ago = now - datetime.timedelta(days=30)
        seven_days_ago = now - datetime.timedelta(days=7)

        # PROGRESSIVE LOADING: Start time tracking
        start_time = datetime.datetime.now()

        # Get SMART-FILTERED subset of policies for production efficiency
        detailed_policies = []
        policies_response = auth.make_api_call("/JSSResource/policies")
        if policies_response and policies_response.get("policies"):
            # Sort by ID for deterministic results
            all_policies = sorted(
                policies_response["policies"], key=lambda x: x.get("id", 0)
            )

            # Apply smart filtering based on user preference
            if smart_filter == "recent":
                # Prioritize recently modified policies (more likely to be actively managed)
                filtered_policies = []
                other_policies = []

                for policy_summary in all_policies:
                    try:
                        # Check if policy was modified recently (simplified check on name for demo)
                        # In production, you'd check actual modification dates from detailed policy data
                        policy_name = policy_summary.get("name", "").lower()
                        if any(
                            keyword in policy_name
                            for keyword in ["2024", "2025", "new", "test", "temp"]
                        ):
                            filtered_policies.append(policy_summary)
                        else:
                            other_policies.append(policy_summary)
                    except:
                        other_policies.append(policy_summary)

                # Combine: recent first, then others, up to limit
                policy_list = (filtered_policies + other_policies)[
                    : selected_limits["policies"]
                ]
            else:
                # Standard: just take first N sorted by ID
                policy_list = all_policies[: selected_limits["policies"]]

            # Get detailed policy data with progress tracking
            for policy_summary in policy_list:
                try:
                    policy_id = policy_summary.get("id")
                    if policy_id:
                        policy_detail = auth.make_api_call(
                            f"/JSSResource/policies/id/{policy_id}"
                        )
                        if policy_detail and policy_detail.get("policy"):
                            policy_data = policy_detail["policy"]
                            # Store both summary and detailed data
                            policy_data["_summary"] = policy_summary
                            detailed_policies.append(policy_data)
                except Exception as e:
                    continue

        # Get ALL configuration profiles
        detailed_profiles = []
        try:
            profiles_response = auth.make_api_call(
                "/JSSResource/osxconfigurationprofiles"
            )
            if profiles_response and profiles_response.get(
                "os_x_configuration_profiles"
            ):
                # Sort by ID and take configured limit for production scalability
                profile_list = sorted(
                    profiles_response["os_x_configuration_profiles"],
                    key=lambda x: x.get("id", 0),
                )[: selected_limits["profiles"]]

                for profile_summary in profile_list:
                    try:
                        profile_id = profile_summary.get("id")
                        if profile_id:
                            profile_detail = auth.make_api_call(
                                f"/JSSResource/osxconfigurationprofiles/id/{profile_id}"
                            )
                            if profile_detail and profile_detail.get(
                                "os_x_configuration_profile"
                            ):
                                profile_data = profile_detail[
                                    "os_x_configuration_profile"
                                ]
                                # Store both summary and detailed data
                                profile_data["_summary"] = profile_summary
                                detailed_profiles.append(profile_data)
                    except Exception as e:
                        continue
        except Exception as e:
            pass

        # Calculate performance metrics
        end_time = datetime.datetime.now()
        load_time = (end_time - start_time).total_seconds()

        return {
            "policies": detailed_policies,
            "profiles": detailed_profiles,
            "total_policies": len(detailed_policies),
            "total_profiles": len(detailed_profiles),
            "analysis_depth": analysis_depth,
            "limits_used": selected_limits,
            "smart_filter": smart_filter,
            "load_time": load_time,
            "api_calls_made": len(detailed_policies)
            + len(detailed_profiles)
            + 2,  # +2 for list calls
            "cache_timestamp": end_time.isoformat(),
        }
    except Exception as e:
        return {
            "policies": [],
            "profiles": [],
            "total_policies": 0,
            "total_profiles": 0,
        }


def get_performance_metrics():
    """Get system performance metrics for enterprise monitoring"""
    try:
        import psutil
        import time

        # Network performance (simplified)
        network_speed = "Unknown"
        try:
            start_time = time.time()
            # Simple network test (ping-like)
            import urllib.request

            urllib.request.urlopen("http://localhost:8504", timeout=1)
            response_time = (time.time() - start_time) * 1000
            if response_time < 50:
                network_speed = "Excellent"
            elif response_time < 100:
                network_speed = "Good"
            elif response_time < 200:
                network_speed = "Fair"
            else:
                network_speed = "Slow"
        except:
            network_speed = "Unknown"

        # System performance
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        return {
            "network_speed": network_speed,
            "network_latency": (
                f"{response_time:.0f}ms" if "response_time" in locals() else "Unknown"
            ),
            "cpu_usage": f"{cpu_percent:.1f}%",
            "memory_usage": f"{memory.percent:.1f}%",
            "memory_available": f"{memory.available / (1024**3):.1f}GB",
        }
    except ImportError:
        # psutil not available, return basic metrics
        return {
            "network_speed": "Unknown",
            "network_latency": "Unknown",
            "cpu_usage": "Unknown",
            "memory_usage": "Unknown",
            "memory_available": "Unknown",
        }
    except Exception as e:
        return {
            "network_speed": "Error",
            "network_latency": "Error",
            "cpu_usage": "Error",
            "memory_usage": "Error",
            "memory_available": "Error",
        }


def check_api_rate_limits(auth, recent_calls=0):
    """Monitor JAMF API rate limits and provide recommendations"""
    try:
        # Estimate API load based on analysis depth and recent calls
        recommendations = []

        if recent_calls > 200:
            recommendations.append(
                "⚠️ High API usage detected - consider reducing analysis depth"
            )
        elif recent_calls > 100:
            recommendations.append(
                "⚡ Moderate API usage - current settings are reasonable"
            )
        else:
            recommendations.append(
                "✅ Low API usage - can increase analysis depth if needed"
            )

        # Check for potential rate limiting
        if recent_calls > 500:
            recommendations.append(
                "🚨 Risk of hitting JAMF API rate limits - reduce frequency"
            )

        return {
            "recent_calls": recent_calls,
            "recommendations": recommendations,
            "estimated_server_load": (
                "High"
                if recent_calls > 300
                else "Medium" if recent_calls > 100 else "Low"
            ),
        }
    except Exception as e:
        return {
            "recent_calls": 0,
            "recommendations": ["❌ Unable to check API limits"],
            "estimated_server_load": "Unknown",
        }


@st.cache_data(ttl=300, show_spinner=False)  # Fast relationship cache
def get_fast_relationship_data():
    """Get basic relationship data for fast loading with core features"""
    try:
        auth = JamfAuth(environment="dev")

        # Get FAST subset: first 50 policies + 25 profiles for relationship analysis
        detailed_policies = []
        policies_response = auth.make_api_call("/JSSResource/policies")
        if policies_response and policies_response.get("policies"):
            # Sort by ID and take first 50 for fast but functional analysis
            policy_list = sorted(
                policies_response["policies"], key=lambda x: x.get("id", 0)
            )[:50]

            for policy_summary in policy_list:
                try:
                    policy_id = policy_summary.get("id")
                    if policy_id:
                        policy_detail = auth.make_api_call(
                            f"/JSSResource/policies/id/{policy_id}"
                        )
                        if policy_detail and policy_detail.get("policy"):
                            policy_data = policy_detail["policy"]
                            policy_data["_summary"] = policy_summary
                            detailed_policies.append(policy_data)
                except Exception:
                    continue

        # Get FAST subset of profiles
        detailed_profiles = []
        try:
            profiles_response = auth.make_api_call(
                "/JSSResource/osxconfigurationprofiles"
            )
            if profiles_response and profiles_response.get(
                "os_x_configuration_profiles"
            ):
                profile_list = sorted(
                    profiles_response["os_x_configuration_profiles"],
                    key=lambda x: x.get("id", 0),
                )[:25]

                for profile_summary in profile_list:
                    try:
                        profile_id = profile_summary.get("id")
                        if profile_id:
                            profile_detail = auth.make_api_call(
                                f"/JSSResource/osxconfigurationprofiles/id/{profile_id}"
                            )
                            if profile_detail and profile_detail.get(
                                "os_x_configuration_profile"
                            ):
                                profile_data = profile_detail[
                                    "os_x_configuration_profile"
                                ]
                                profile_data["_summary"] = profile_summary
                                detailed_profiles.append(profile_data)
                    except Exception:
                        continue
        except Exception:
            pass

        return {
            "policies": detailed_policies,
            "profiles": detailed_profiles,
            "total_policies": len(detailed_policies),
            "total_profiles": len(detailed_profiles),
            "mode": "fast",
        }
    except Exception:
        return {
            "policies": [],
            "profiles": [],
            "total_policies": 0,
            "total_profiles": 0,
            "mode": "fast",
        }


def get_relationship_bubbles(object_type, obj_id, obj_name, reverse_lookup, auth):
    """Get relationship bubbles - fast mode for core functionality"""
    try:
        bubbles = []

        # Use fast relationship data if in basic mode, full data if in advanced mode
        if st.session_state.get("detailed_data_loaded", False):
            relationship_data = get_cached_relationship_data(
                st.session_state.get("analysis_depth", "standard"),
                st.session_state.get("smart_filter", "recent"),
            )
        else:
            relationship_data = get_fast_relationship_data()
        obj_name_clean = obj_name.strip()
        obj_id_clean = str(obj_id)

        if object_type == "policies":
            # Forward relationships: what this policy contains/targets
            policy_response = auth.make_api_call(f"/JSSResource/policies/id/{obj_id}")
            if policy_response and policy_response.get("policy"):
                policy = policy_response["policy"]

                packages = policy.get("package_configuration", {}).get("packages", [])
                scripts = policy.get("scripts", [])
                scope_groups = policy.get("scope", {}).get("computer_groups", [])
                scope_computers = policy.get("scope", {}).get("computers", [])

                if packages:
                    bubbles.append(
                        f'<a href="http://localhost:8502?focus=packages&id={obj_id}&name={obj_name_clean}" target="_blank" style="text-decoration: none;"><span class="relation-bubble package-bubble clickable-bubble" title="Click to analyze {len(packages)} packages in detail">📦 {len(packages)}</span></a>'
                    )
                if scripts:
                    bubbles.append(
                        f'<a href="http://localhost:8502?focus=scripts&id={obj_id}&name={obj_name_clean}" target="_blank" style="text-decoration: none;"><span class="relation-bubble script-bubble clickable-bubble" title="Click to analyze {len(scripts)} scripts in detail">⚙️ {len(scripts)}</span></a>'
                    )
                if scope_groups:
                    bubbles.append(
                        f'<a href="http://localhost:8502?focus=groups&id={obj_id}&name={obj_name_clean}" target="_blank" style="text-decoration: none;"><span class="relation-bubble group-bubble clickable-bubble" title="Click to analyze {len(scope_groups)} groups in detail">👥 {len(scope_groups)}</span></a>'
                    )
                if scope_computers:
                    bubbles.append(
                        f'<span class="relation-bubble computer-bubble" title="Targets {len(scope_computers)} computers">💻 {len(scope_computers)}</span>'
                    )

        elif object_type == "scripts":
            # Comprehensive reverse relationships for scripts
            using_policies = []
            using_profiles = []

            # Check policies that use this script
            for policy in relationship_data.get("policies", []):
                policy_scripts = policy.get("scripts", [])
                for script in policy_scripts:
                    script_name = script.get("name", "").strip()
                    script_id = str(script.get("id", ""))
                    if (
                        script_name and script_name.lower() == obj_name_clean.lower()
                    ) or (script_id and script_id == obj_id_clean):
                        # Better policy name extraction
                        policy_name = policy.get("name")
                        if not policy_name and "_summary" in policy:
                            policy_name = policy["_summary"].get("name")
                        if not policy_name:
                            policy_name = f"Policy ID {policy.get('id', 'Unknown')}"

                        if policy_name not in using_policies:
                            using_policies.append(policy_name)
                        break

            # Check configuration profiles that use this script
            for profile in relationship_data.get("profiles", []):
                # Check if profile has scripts (some profiles can execute scripts)
                payloads = profile.get("payloads", [])
                for payload in payloads:
                    if payload.get("type") == "com.apple.scripting":
                        script_content = payload.get("script_content", "")
                        if obj_name_clean.lower() in script_content.lower():
                            # Better profile name extraction
                            profile_name = profile.get("name")
                            if not profile_name and "_summary" in profile:
                                profile_name = profile["_summary"].get("name")
                            if not profile_name:
                                profile_name = (
                                    f"Profile ID {profile.get('id', 'Unknown')}"
                                )

                            if profile_name not in using_profiles:
                                using_profiles.append(profile_name)
                            break

            # Add clickable relationship bubbles
            if using_policies:
                policy_names = ", ".join(using_policies[:2])
                if len(using_policies) > 2:
                    policy_names += f" +{len(using_policies)-2} more"
                bubbles.append(
                    f'<a href="http://localhost:8502?focus=scripts&id={obj_id}&name={obj_name_clean}&context=reverse_policies" target="_blank" style="text-decoration: none;"><span class="relation-bubble policy-bubble clickable-bubble" title="Click to analyze policies using this script: {policy_names}">📋 {len(using_policies)}</span></a>'
                )

            if using_profiles:
                profile_names = ", ".join(using_profiles[:2])
                if len(using_profiles) > 2:
                    profile_names += f" +{len(using_profiles)-2} more"
                bubbles.append(
                    f'<a href="http://localhost:8502?focus=scripts&id={obj_id}&name={obj_name_clean}&context=reverse_profiles" target="_blank" style="text-decoration: none;"><span class="relation-bubble profile-bubble clickable-bubble" title="Click to analyze profiles using this script: {profile_names}">🔧 {len(using_profiles)}</span></a>'
                )

        elif object_type == "packages":
            # Comprehensive reverse relationships for packages
            deploying_policies = []

            # Check policies that deploy this package
            for policy in relationship_data.get("policies", []):
                packages = policy.get("package_configuration", {}).get("packages", [])
                for package in packages:
                    package_name = package.get("name", "").strip()
                    package_id = str(package.get("id", ""))
                    if (
                        package_name and package_name.lower() == obj_name_clean.lower()
                    ) or (package_id and package_id == obj_id_clean):
                        # Better policy name extraction
                        policy_name = policy.get("name")
                        if not policy_name and "_summary" in policy:
                            policy_name = policy["_summary"].get("name")
                        if not policy_name:
                            policy_name = f"Policy ID {policy.get('id', 'Unknown')}"

                        if policy_name not in deploying_policies:
                            deploying_policies.append(policy_name)
                        break

            if deploying_policies:
                policy_names = ", ".join(deploying_policies[:2])
                if len(deploying_policies) > 2:
                    policy_names += f" +{len(deploying_policies)-2} more"
                bubbles.append(
                    f'<span class="relation-bubble policy-bubble" title="Deployed by policies: {policy_names}">📋 {len(deploying_policies)}</span>'
                )

        elif object_type == "groups":
            # Comprehensive reverse relationships for groups
            targeting_policies = []
            targeting_profiles = []

            # DEBUG: Special handling for 0.testcrh group
            is_test_group = obj_name_clean.lower() == "0.testcrh"
            debug_info = []

            # Check policies that target this group
            for policy in relationship_data.get("policies", []):
                scope_groups = policy.get("scope", {}).get("computer_groups", [])

                # Better policy name extraction
                policy_name = policy.get("name")
                if not policy_name and "_summary" in policy:
                    policy_name = policy["_summary"].get("name")
                if not policy_name:
                    policy_name = f"Policy ID {policy.get('id', 'Unknown')}"

                if is_test_group:
                    debug_info.append(
                        f"Policy '{policy_name}' has {len(scope_groups)} scope groups"
                    )

                for group in scope_groups:
                    group_name = group.get("name", "").strip()
                    group_id = str(group.get("id", ""))

                    if is_test_group:
                        debug_info.append(f"  - Group: '{group_name}' (ID: {group_id})")

                    # More flexible matching
                    name_match = (
                        group_name and group_name.lower() == obj_name_clean.lower()
                    )
                    id_match = group_id and group_id == obj_id_clean

                    if name_match or id_match:
                        if policy_name not in targeting_policies:
                            targeting_policies.append(policy_name)
                            if is_test_group:
                                debug_info.append(f"  ✅ MATCH! Policy: {policy_name}")
                        break

            # Check configuration profiles that target this group
            for profile in relationship_data.get("profiles", []):
                scope_groups = profile.get("scope", {}).get("computer_groups", [])

                # Better profile name extraction
                profile_name = profile.get("name")
                if not profile_name and "_summary" in profile:
                    profile_name = profile["_summary"].get("name")
                if not profile_name:
                    profile_name = f"Profile ID {profile.get('id', 'Unknown')}"

                if is_test_group:
                    debug_info.append(
                        f"Profile '{profile_name}' has {len(scope_groups)} scope groups"
                    )

                for group in scope_groups:
                    group_name = group.get("name", "").strip()
                    group_id = str(group.get("id", ""))

                    if is_test_group:
                        debug_info.append(f"  - Group: '{group_name}' (ID: {group_id})")

                    # More flexible matching
                    name_match = (
                        group_name and group_name.lower() == obj_name_clean.lower()
                    )
                    id_match = group_id and group_id == obj_id_clean

                    if name_match or id_match:
                        if profile_name not in targeting_profiles:
                            targeting_profiles.append(profile_name)
                            if is_test_group:
                                debug_info.append(
                                    f"  ✅ MATCH! Profile: {profile_name}"
                                )
                        break

            # Add relationship bubbles
            if targeting_policies:
                policy_names = ", ".join(targeting_policies[:2])
                if len(targeting_policies) > 2:
                    policy_names += f" +{len(targeting_policies)-2} more"
                bubbles.append(
                    f'<span class="relation-bubble policy-bubble" title="Targeted by policies: {policy_names}">📋 {len(targeting_policies)}</span>'
                )

            if targeting_profiles:
                profile_names = ", ".join(targeting_profiles[:2])
                if len(targeting_profiles) > 2:
                    profile_names += f" +{len(targeting_profiles)-2} more"
                bubbles.append(
                    f'<span class="relation-bubble profile-bubble" title="Targeted by profiles: {profile_names}">🔧 {len(targeting_profiles)}</span>'
                )

            # DEBUG: Add debug info for test group
            if is_test_group:
                total_found = len(targeting_policies) + len(targeting_profiles)
                debug_summary = f"Found {total_found} total relationships. Debug: {len(debug_info)} checks performed"
                bubbles.append(
                    f'<span class="relation-bubble debug-bubble" title="{debug_summary}">🐛 {total_found}</span>'
                )

            # Get group member count
            try:
                group_response = auth.make_api_call(
                    f"/JSSResource/computergroups/id/{obj_id}"
                )
                if group_response and group_response.get("computer_group"):
                    computers = group_response["computer_group"].get("computers", [])
                    if computers:
                        bubbles.append(
                            f'<span class="relation-bubble computer-bubble" title="{len(computers)} member computers">💻 {len(computers)}</span>'
                        )
            except:
                pass

        elif object_type == "profiles":
            # Forward relationships: what this profile contains/targets
            profile_response = auth.make_api_call(
                f"/JSSResource/osxconfigurationprofiles/id/{obj_id}"
            )
            if profile_response and profile_response.get("os_x_configuration_profile"):
                profile = profile_response["os_x_configuration_profile"]

                scope_groups = profile.get("scope", {}).get("computer_groups", [])
                scope_computers = profile.get("scope", {}).get("computers", [])
                payloads = profile.get("payloads", [])

                if scope_groups:
                    bubbles.append(
                        f'<span class="relation-bubble group-bubble" title="Targets {len(scope_groups)} groups">👥 {len(scope_groups)}</span>'
                    )
                if scope_computers:
                    bubbles.append(
                        f'<span class="relation-bubble computer-bubble" title="Targets {len(scope_computers)} computers">💻 {len(scope_computers)}</span>'
                    )
                if payloads:
                    bubbles.append(
                        f'<span class="relation-bubble payload-bubble" title="Contains {len(payloads)} payloads">⚙️ {len(payloads)}</span>'
                    )

        # Add mode indicator to bubbles
        mode_indicator = ""
        if relationship_data.get("mode") == "fast":
            mode_indicator = '<span style="color: #8E8E93; font-size: 10px; margin-left: 4px;">⚡</span>'

        return "".join(bubbles) + mode_indicator

    except Exception as e:
        return ""


def render_object_cards(object_type, auth, reverse_lookup):
    """Render Apple-style object cards with cached data and responsive UI feedback"""
    try:
        # Show current settings for user feedback
        analysis_depth = st.session_state.get("analysis_depth", "standard")
        smart_filter = st.session_state.get("smart_filter", "recent")

        # Informative loading with current settings
        with st.spinner(
            f"🔄 Loading {object_type} (Depth: {analysis_depth}, Filter: {smart_filter})..."
        ):
            data = get_cached_object_data(object_type)

        if not data:
            st.error(f"⚠️ No {object_type} found.")
            st.caption(f"💡 Try changing your analysis depth or smart filter settings")

            # Quick actions for empty results
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🔄 Refresh {object_type}", key=f"refresh_{object_type}"):
                    st.cache_data.clear()
                    st.rerun()
            with col2:
                if st.button(
                    "⚡ Change Settings", key=f"change_settings_{object_type}"
                ):
                    st.info("💡 Adjust Analysis Depth or Smart Filter settings above")
            return

        # Show count and limit for performance
        display_data = data[:20] if len(data) > 20 else data

        # Clean count display
        count_text = f"Showing {len(display_data)}"
        if len(data) > 20:
            count_text += f" of {len(data)}"
        count_text += f" {object_type}"
        st.caption(count_text)

        # DEBUG: Show cache status for reverse relationships
        if object_type != "policies":
            relationship_data = get_cached_relationship_data(
                st.session_state.get("analysis_depth", "standard"),
                st.session_state.get("smart_filter", "recent"),
            )
            total_policies = relationship_data.get("total_policies", 0)
            total_profiles = relationship_data.get("total_profiles", 0)
            if total_policies > 0 or total_profiles > 0:
                st.caption(
                    f"🔍 Reverse lookup cache: {total_policies} policies, {total_profiles} profiles loaded (ALL data)"
                )
            else:
                st.warning(
                    "⚠️ No detailed relationship data for reverse lookups - relationships may not show correctly"
                )

        for obj in display_data:
            render_object_card(obj, object_type, reverse_lookup, auth)

            # DEBUG: Special debug info for 0.testcrh group
            if (
                object_type == "groups"
                and obj.get("name", "").strip().lower() == "0.testcrh"
            ):
                with st.expander("🐛 DEBUG: 0.testcrh Relationship Analysis"):
                    relationship_data = get_cached_relationship_data(
                        st.session_state.get("analysis_depth", "standard"),
                        st.session_state.get("smart_filter", "recent"),
                    )
                    target_group_id = str(obj.get("id"))
                    target_group_name = obj.get("name", "").strip()

                    st.write(f"**Target Group ID:** {target_group_id}")
                    st.write(f"**Target Group Name:** '{target_group_name}'")
                    st.write(
                        f"**Total Policies Loaded:** {relationship_data.get('total_policies', 0)}"
                    )
                    st.write(
                        f"**Total Profiles Loaded:** {relationship_data.get('total_profiles', 0)}"
                    )

                    # Find ALL policies that target this group
                    matching_policies = []
                    st.write("**Checking ALL Policies:**")

                    # DEBUG: Show structure of first policy
                    if relationship_data.get("policies"):
                        first_policy = relationship_data["policies"][0]
                        st.write("**DEBUG: First policy structure:**")
                        st.write(f"  - Keys: {list(first_policy.keys())}")
                        st.write(
                            f"  - name field: '{first_policy.get('name', 'NOT FOUND')}'"
                        )
                        if "_summary" in first_policy:
                            st.write(
                                f"  - summary name: '{first_policy['_summary'].get('name', 'NOT FOUND')}'"
                            )
                        st.write("---")

                    for i, policy in enumerate(relationship_data.get("policies", [])):
                        scope_groups = policy.get("scope", {}).get(
                            "computer_groups", []
                        )

                        # Try multiple ways to get policy name
                        policy_name = policy.get("name")
                        if not policy_name and "_summary" in policy:
                            policy_name = policy["_summary"].get("name")
                        if not policy_name:
                            policy_name = f"Policy ID {policy.get('id', 'Unknown')}"

                        # Check if this policy targets our group
                        targets_our_group = False
                        for group in scope_groups:
                            group_name = group.get("name", "").strip()
                            group_id = str(group.get("id", ""))

                            if (group_name.lower() == target_group_name.lower()) or (
                                group_id == target_group_id
                            ):
                                targets_our_group = True
                                matching_policies.append(policy_name)
                                break

                        if targets_our_group:
                            st.write(
                                f"  ✅ **MATCH:** '{policy_name}' targets '{target_group_name}'"
                            )
                        elif len(scope_groups) > 0 and i < 5:
                            st.write(
                                f"  ❌ '{policy_name}' targets {len(scope_groups)} other groups"
                            )

                        # Show first few for debugging
                        if i < 5 and len(scope_groups) > 0:
                            for group in scope_groups[:2]:
                                st.write(
                                    f"      - '{group.get('name', '')}' (ID: {group.get('id', '')})"
                                )

                    # Find ALL profiles that target this group
                    matching_profiles = []
                    st.write("**Checking ALL Profiles:**")
                    for i, profile in enumerate(relationship_data.get("profiles", [])):
                        scope_groups = profile.get("scope", {}).get(
                            "computer_groups", []
                        )

                        # Better profile name extraction
                        profile_name = profile.get("name")
                        if not profile_name and "_summary" in profile:
                            profile_name = profile["_summary"].get("name")
                        if not profile_name:
                            profile_name = f"Profile ID {profile.get('id', 'Unknown')}"

                        # Check if this profile targets our group
                        targets_our_group = False
                        for group in scope_groups:
                            group_name = group.get("name", "").strip()
                            group_id = str(group.get("id", ""))

                            if (group_name.lower() == target_group_name.lower()) or (
                                group_id == target_group_id
                            ):
                                targets_our_group = True
                                matching_profiles.append(profile_name)
                                break

                        if targets_our_group:
                            st.write(
                                f"  ✅ **MATCH:** '{profile_name}' targets '{target_group_name}'"
                            )
                        elif len(scope_groups) > 0 and i < 5:
                            st.write(
                                f"  ❌ '{profile_name}' targets {len(scope_groups)} other groups"
                            )

                    st.write(f"**TOTAL MATCHES FOUND:**")
                    st.write(f"  - Policies: {len(matching_policies)}")
                    st.write(f"  - Profiles: {len(matching_profiles)}")
                    st.write(f"  - **EXPECTED TOTAL: 10-11**")

    except Exception as e:
        st.error(f"⚠️ Error loading {object_type}: {e}")


def render_object_card(obj, object_type, reverse_lookup, auth):
    """Render individual Apple-style object card with compact relationship bubbles"""
    name = obj.get("name", "Unknown")
    obj_id = obj.get("id", "Unknown")

    # Get relationship bubbles
    relationship_bubbles = get_relationship_bubbles(
        object_type, obj_id, name, reverse_lookup, auth
    )

    # Build metadata based on object type
    meta_items = [f"ID: {obj_id}"]

    if object_type == "policies":
        category = obj.get("category", {})
        if isinstance(category, dict):
            category_name = category.get("name", "None")
        else:
            category_name = str(category)
        meta_items.append(f"Category: {category_name}")

        enabled = obj.get("enabled", True)
        status = "✅ Enabled" if enabled else "❌ Disabled"
        meta_items.append(f"Status: {status}")

    elif object_type == "scripts":
        category = obj.get("category", {})
        if isinstance(category, dict):
            category_name = category.get("name", "None")
        else:
            category_name = str(category)
        meta_items.append(f"Category: {category_name}")

    elif object_type == "packages":
        category = obj.get("category", {})
        if isinstance(category, dict):
            category_name = category.get("name", "None")
        else:
            category_name = str(category)
        meta_items.append(f"Category: {category_name}")

        size = obj.get("size", 0)
        if size:
            size_mb = (
                round(size / 1024 / 1024, 1)
                if size > 1024 * 1024
                else round(size / 1024, 1)
            )
            size_label = (
                f"{size_mb} GB" if size > 1024 * 1024 * 1024 else f"{size_mb} MB"
            )
            meta_items.append(f"Size: {size_label}")

    elif object_type == "groups":
        is_smart = obj.get("is_smart", False)
        group_type = "Smart Group" if is_smart else "Static Group"
        meta_items.append(f"Type: {group_type}")

        size = obj.get("size", 0)
        meta_items.append(f"Members: {size}")

    elif object_type == "profiles":
        description = obj.get("description", "No description")[:50]
        if len(description) > 47:
            description = description[:47] + "..."
        meta_items.append(f"Description: {description}")

        distribution_method = obj.get("distribution_method", "Unknown")
        meta_items.append(f"Distribution: {distribution_method}")

    # Render the card with compact bubbles
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(
            f"""
        <div class="object-card">
            <div class="object-title">
                <span>{name}</span>
                <div class="bubbles-container">{relationship_bubbles}</div>
            </div>
            <div class="object-meta">
                {' • '.join(meta_items)}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        # Add clickable navigation buttons based on relationships
        relationship_data = get_cached_relationship_data(
            st.session_state.get("analysis_depth", "standard"),
            st.session_state.get("smart_filter", "recent"),
        )

        if object_type == "policies":
            script_count = len(obj.get("scripts", []))
            package_count = len(
                obj.get("package_configuration", {}).get("packages", [])
            )
            if script_count > 0:
                if st.button(
                    f"⚙️ {script_count}",
                    key=f"nav_scripts_{obj_id}",
                    help="View Scripts",
                ):
                    st.session_state.selected_object_type = "scripts"
                    st.rerun()
            if package_count > 0:
                if st.button(
                    f"📦 {package_count}",
                    key=f"nav_packages_{obj_id}",
                    help="View Packages",
                ):
                    st.session_state.selected_object_type = "packages"
                    st.rerun()

        elif object_type in ["scripts", "packages"]:
            # Count policies that use this script/package
            policy_count = 0
            for policy in relationship_data.get("policies", []):
                if object_type == "scripts":
                    if any(
                        s.get("name", "").lower() == name.lower()
                        for s in policy.get("scripts", [])
                    ):
                        policy_count += 1
                elif object_type == "packages":
                    if any(
                        p.get("name", "").lower() == name.lower()
                        for p in policy.get("package_configuration", {}).get(
                            "packages", []
                        )
                    ):
                        policy_count += 1

            if policy_count > 0:
                if st.button(
                    f"📋 {policy_count}",
                    key=f"nav_policies_{obj_id}",
                    help="View Policies",
                ):
                    st.session_state.selected_object_type = "policies"
                    st.rerun()

        elif object_type == "groups":
            # Count policies and profiles targeting this group
            policy_count = 0
            profile_count = 0
            for policy in relationship_data.get("policies", []):
                if any(
                    g.get("name", "").lower() == name.lower()
                    for g in policy.get("scope", {}).get("computer_groups", [])
                ):
                    policy_count += 1
            for profile in relationship_data.get("profiles", []):
                if any(
                    g.get("name", "").lower() == name.lower()
                    for g in profile.get("scope", {}).get("computer_groups", [])
                ):
                    profile_count += 1

            if policy_count > 0:
                if st.button(
                    f"📋 {policy_count}",
                    key=f"nav_policies_{obj_id}",
                    help="View Policies",
                ):
                    st.session_state.selected_object_type = "policies"
                    st.rerun()
            if profile_count > 0:
                if st.button(
                    f"🔧 {profile_count}",
                    key=f"nav_profiles_{obj_id}",
                    help="View Profiles",
                ):
                    st.session_state.selected_object_type = "profiles"
                    st.rerun()


@st.cache_data(ttl=300, show_spinner=False)  # Fast basic data cache
def get_basic_stats(_auth):
    """Get basic statistics without detailed data for fast initial load"""
    try:
        # Only get summary counts - no detailed data
        policies_response = _auth.make_api_call("/JSSResource/policies")
        scripts_response = _auth.make_api_call("/JSSResource/scripts")
        packages_response = _auth.make_api_call("/JSSResource/packages")
        groups_response = _auth.make_api_call("/JSSResource/computergroups")

        policies = policies_response.get("policies", []) if policies_response else []
        scripts = scripts_response.get("scripts", []) if scripts_response else []
        packages = packages_response.get("packages", []) if packages_response else []
        groups = groups_response.get("computer_groups", []) if groups_response else []

        # Quick profile count (no detailed data)
        try:
            profiles_response = _auth.make_api_call(
                "/JSSResource/osxconfigurationprofiles"
            )
            profiles = (
                profiles_response.get("os_x_configuration_profiles", [])
                if profiles_response
                else []
            )
        except:
            profiles = []

        return {
            "policies": len(policies),
            "scripts": len(scripts),
            "packages": len(packages),
            "groups": len(groups),
            "profiles": len(profiles),
            "enabled_policies": len([p for p in policies if p.get("enabled", True)]),
            "smart_groups": len([g for g in groups if g.get("is_smart", False)]),
        }
    except Exception as e:
        return {
            "policies": 0,
            "scripts": 0,
            "packages": 0,
            "groups": 0,
            "profiles": 0,
            "enabled_policies": 0,
            "smart_groups": 0,
        }


def main():
    """Main Apple-styled JAMF application with OPTIMIZED FAST LOADING"""

    # Initialize authentication with your existing keychain environment
    try:
        from auth_production import JamfAuth

        auth = JamfAuth(
            environment="dev"
        )  # Use your existing dev environment from keychain
    except ImportError:
        try:
            from jamf_auth import JamfAuthSimple

            auth = JamfAuthSimple(environment="dev")
        except ImportError:
            # Final fallback - create a mock auth object
            class MockJamfAuth:
                def __init__(self, *args, **kwargs):
                    self.environment = "dev"

                def make_api_call(self, *args, **kwargs):
                    return {}

                def authenticate(self, *args, **kwargs):
                    return False

            auth = MockJamfAuth()
    reverse_lookup = ReverseRelationshipLookup()

    # Handle URL parameters and shared state for cross-viewer integration
    query_params = st.query_params

    # Load shared state from detailed viewer if returning
    shared_state = load_shared_viewer_state()
    if shared_state and shared_state.get("source") == "compact_detailed_viewer":
        if shared_state.get("return_context") == "detailed_analysis_complete":
            st.success(
                f"🔍 **Analysis Complete**: Returned from Detailed Viewer • Last viewed: {shared_state.get('last_viewed_type', 'Unknown')}"
            )

    # Initialize session state for object type selection and analysis depth
    if "selected_object_type" not in st.session_state:
        st.session_state.selected_object_type = "policies"
    if "analysis_depth" not in st.session_state:
        st.session_state.analysis_depth = "standard"
    if "smart_filter" not in st.session_state:
        st.session_state.smart_filter = "recent"
    if "show_performance_metrics" not in st.session_state:
        st.session_state.show_performance_metrics = False
    if "detailed_data_loaded" not in st.session_state:
        st.session_state.detailed_data_loaded = False
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""

    # FAST INITIAL RENDER: Show UI skeleton immediately (no API calls)
    render_apple_header(auth, show_connection_status=False)

    # Unified search bar with cross-viewer functionality
    st.markdown("### 🔍 **Unified Search & Navigation**")
    search_col1, search_col2, search_col3 = st.columns([3, 1, 1])

    with search_col1:
        search_query = st.text_input(
            "Search across all JAMF objects:",
            value=st.session_state.get("search_query", ""),
            placeholder="Search policies, scripts, packages, groups...",
            help="Search will sync across both viewers",
        )
        if search_query != st.session_state.get("search_query", ""):
            st.session_state.search_query = search_query
            # Save search query for other viewers
            save_shared_viewer_state(
                {
                    "search_query": search_query,
                    "search_timestamp": datetime.now().isoformat(),
                }
            )

    with search_col2:
        if st.button(
            "🔍 **Detailed Search**", help="Search in Compact Detailed Viewer"
        ):
            save_shared_viewer_state(
                {"search_query": search_query, "context": "search_from_dashboard"}
            )
            webbrowser.open(f"http://localhost:8502?search={search_query}")

    with search_col3:
        if search_query:
            if st.button("❌ Clear", help="Clear search"):
                st.session_state.search_query = ""
                st.rerun()

    # PERFORMANCE OPTIMIZATION: Show basic stats immediately with fast cache
    with st.spinner("⚡ Loading dashboard..."):
        basic_stats = get_basic_stats(auth)

    # Quick stats display (no detailed data needed)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        button_style = (
            "🔥" if st.session_state.selected_object_type == "policies" else "📋"
        )
        if st.button(
            f"{button_style} {basic_stats['policies']}\nPolicies\n{basic_stats['enabled_policies']} enabled",
            key="nav_policies_fast",
            help="Click to view all policies",
            type=(
                "primary"
                if st.session_state.selected_object_type == "policies"
                else "secondary"
            ),
        ):
            st.session_state.selected_object_type = "policies"
            st.session_state.detailed_data_loaded = False  # Reset detailed data flag
            st.success("🔄 Loading Policies...")
            st.rerun()

    with col2:
        button_style = (
            "🔥" if st.session_state.selected_object_type == "scripts" else "⚙️"
        )
        if st.button(
            f"{button_style} {basic_stats['scripts']}\nScripts\nFor policies",
            key="nav_scripts_fast",
            help="Click to view all scripts",
            type=(
                "primary"
                if st.session_state.selected_object_type == "scripts"
                else "secondary"
            ),
        ):
            st.session_state.selected_object_type = "scripts"
            st.session_state.detailed_data_loaded = False
            st.success("🔄 Loading Scripts...")
            st.rerun()

    with col3:
        button_style = (
            "🔥" if st.session_state.selected_object_type == "packages" else "📦"
        )
        if st.button(
            f"{button_style} {basic_stats['packages']}\nPackages\nFor deployment",
            key="nav_packages_fast",
            help="Click to view all packages",
            type=(
                "primary"
                if st.session_state.selected_object_type == "packages"
                else "secondary"
            ),
        ):
            st.session_state.selected_object_type = "packages"
            st.session_state.detailed_data_loaded = False
            st.success("🔄 Loading Packages...")
            st.rerun()

    with col4:
        button_style = (
            "🔥" if st.session_state.selected_object_type == "groups" else "👥"
        )
        if st.button(
            f"{button_style} {basic_stats['groups']}\nGroups\n{basic_stats['smart_groups']} smart",
            key="nav_groups_fast",
            help="Click to view all computer groups",
            type=(
                "primary"
                if st.session_state.selected_object_type == "groups"
                else "secondary"
            ),
        ):
            st.session_state.selected_object_type = "groups"
            st.session_state.detailed_data_loaded = False
            st.success("🔄 Loading Groups...")
            st.rerun()

    with col5:
        button_style = (
            "🔥" if st.session_state.selected_object_type == "profiles" else "🔧"
        )
        if st.button(
            f"{button_style} {basic_stats['profiles']}\nProfiles\nConfiguration",
            key="nav_profiles_fast",
            help="Click to view all configuration profiles",
            type=(
                "primary"
                if st.session_state.selected_object_type == "profiles"
                else "secondary"
            ),
        ):
            st.session_state.selected_object_type = "profiles"
            st.session_state.detailed_data_loaded = False
            st.success("🔄 Loading Profiles...")
            st.rerun()

    # LAZY LOADING: Only show detailed controls if user interacts
    if st.session_state.detailed_data_loaded or st.button(
        "🎛️ Show Advanced Settings", key="show_advanced"
    ):
        st.session_state.detailed_data_loaded = True
        render_detailed_controls(auth, reverse_lookup)
    else:
        st.info(
            "💡 Click 'Show Advanced Settings' to access analysis depth, smart filtering, and performance monitoring"
        )

    # FAST CONTENT LOADING: Show basic object list immediately
    render_basic_content(auth, reverse_lookup)


def render_basic_content(auth, reverse_lookup):
    """Render basic content without heavy relationship analysis"""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Show current selection with basic title
    object_titles = {
        "policies": "📋 Policies",
        "scripts": "⚙️ Scripts",
        "packages": "📦 Packages",
        "groups": "👥 Computer Groups",
        "profiles": "🔧 Configuration Profiles",
    }
    current_title = object_titles.get(
        st.session_state.selected_object_type, "📋 Policies"
    )
    st.markdown(
        f'<h2 class="section-title">{current_title}</h2>', unsafe_allow_html=True
    )

    # Show basic object list (no relationship bubbles for fast loading)
    try:
        with st.spinner(f"⚡ Loading {st.session_state.selected_object_type}..."):
            data = get_cached_object_data(st.session_state.selected_object_type)

        if not data:
            st.error(f"⚠️ No {st.session_state.selected_object_type} found.")
            return

        # Show first 10 for fast display
        display_data = data[:10]
        st.caption(
            f"Showing first {len(display_data)} of {len(data)} {st.session_state.selected_object_type}"
        )

        # Render cards WITH relationship analysis (core feature!)
        for obj in display_data:
            render_object_card(
                obj, st.session_state.selected_object_type, reverse_lookup, auth
            )

        if len(data) > 10:
            st.info(
                "💡 Enable 'Advanced Settings' to see all objects and comprehensive relationship analysis"
            )

        # Show relationship analysis mode
        try:
            relationship_data = get_fast_relationship_data()
            st.caption(
                f"🔍 **Fast Relationship Analysis**: Using {relationship_data.get('total_policies', 0)} policies, {relationship_data.get('total_profiles', 0)} profiles for quick relationship counts"
            )
        except Exception:
            st.caption(
                "🔍 **Fast Relationship Analysis**: Loading relationship data..."
            )

    except Exception as e:
        st.error(f"⚠️ Error loading {st.session_state.selected_object_type}: {e}")


def render_basic_object_card(obj, object_type):
    """Render basic object card without expensive relationship lookups"""
    name = obj.get("name", "Unknown")
    obj_id = obj.get("id", "Unknown")

    # Build basic metadata
    meta_items = [f"ID: {obj_id}"]

    if object_type == "policies":
        category = obj.get("category", {})
        if isinstance(category, dict):
            category_name = category.get("name", "None")
        else:
            category_name = str(category)
        meta_items.append(f"Category: {category_name}")

        enabled = obj.get("enabled", True)
        status = "✅ Enabled" if enabled else "❌ Disabled"
        meta_items.append(f"Status: {status}")

    elif object_type == "scripts":
        category = obj.get("category", {})
        if isinstance(category, dict):
            category_name = category.get("name", "None")
        else:
            category_name = str(category)
        meta_items.append(f"Category: {category_name}")

    elif object_type == "packages":
        size = obj.get("size", "Unknown")
        if isinstance(size, int):
            size_mb = size / (1024 * 1024)
            if size_mb < 1:
                size_label = f"{size / 1024:.1f} KB"
            else:
                size_label = f"{size_mb:.1f} MB"
            meta_items.append(f"Size: {size_label}")

    elif object_type == "groups":
        is_smart = obj.get("is_smart", False)
        group_type = "Smart Group" if is_smart else "Static Group"
        meta_items.append(f"Type: {group_type}")

        size = obj.get("size", 0)
        meta_items.append(f"Members: {size}")

    elif object_type == "profiles":
        description = obj.get("description", "No description")[:50]
        if len(description) > 47:
            description = description[:47] + "..."
        meta_items.append(f"Description: {description}")

    # Render basic card
    st.markdown(
        f"""
    <div class="object-card">
        <div class="object-title">
            <span>{name}</span>
            <span style="color: #8E8E93; font-size: 12px;">⚡ Fast mode</span>
        </div>
        <div class="object-meta">
            {' • '.join(meta_items)}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_detailed_controls(auth, reverse_lookup):
    """Render detailed enterprise controls with full caching"""
    # Show connection status in advanced mode
    st.info("🔄 Checking JAMF Pro connection...")
    status = get_connection_status(auth)
    if status["status"] == "live":
        st.success(f"✅ {status['message']}")
    else:
        st.error(f"❌ {status['message']}")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Main controls row
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown("#### 🎛️ Analysis Settings")

        # Analysis depth selector with immediate feedback
        analysis_depth = st.selectbox(
            "Analysis Depth:",
            ["quick", "standard", "comprehensive", "enterprise"],
            index=["quick", "standard", "comprehensive", "enterprise"].index(
                st.session_state.analysis_depth
            ),
            format_func=lambda x: {
                "quick": "⚡ Quick (2-3 min)",
                "standard": "🎯 Standard (5-7 min)",
                "comprehensive": "🔍 Comprehensive (10-15 min)",
                "enterprise": "🏢 Enterprise (20+ min)",
            }[x],
            key="analysis_depth_selector",
            help="Choose analysis depth - changes take effect immediately",
        )

        # Check if analysis depth changed and trigger refresh
        if analysis_depth != st.session_state.analysis_depth:
            st.session_state.analysis_depth = analysis_depth
            st.info(
                f"🔄 Analysis depth changed to {analysis_depth} - refreshing data..."
            )
            # Clear cache to force reload with new settings
            st.cache_data.clear()
            st.rerun()

        # Smart filtering options with immediate feedback
        smart_filter = st.selectbox(
            "Smart Filtering:",
            ["recent", "all"],
            index=["recent", "all"].index(st.session_state.smart_filter),
            format_func=lambda x: {
                "recent": "🔥 Recent/Active First",
                "all": "📋 All (By ID)",
            }[x],
            key="smart_filter_selector",
            help="Choose filtering method - changes take effect immediately",
        )

        # Check if smart filter changed and trigger refresh
        if smart_filter != st.session_state.smart_filter:
            st.session_state.smart_filter = smart_filter
            st.info(f"🔄 Smart filter changed to {smart_filter} - refreshing data...")
            # Clear cache to force reload with new settings
            st.cache_data.clear()
            st.rerun()

    with col2:
        st.markdown("#### 📊 Cache & Performance Status")

        # Show detailed cache status with performance metrics and loading state
        try:
            # Show loading state while fetching data
            with st.spinner("🔄 Loading cache status..."):
                relationship_data = get_cached_relationship_data(
                    st.session_state.analysis_depth, st.session_state.smart_filter
                )
                limits = relationship_data.get("limits_used", {})
                load_time = relationship_data.get("load_time", 0)
                api_calls = relationship_data.get("api_calls_made", 0)
                cache_time = relationship_data.get("cache_timestamp", "Unknown")

                # Performance metrics
                perf_metrics = get_performance_metrics()
                api_limits = check_api_rate_limits(auth, api_calls)

            # Cache status display with color-coded status
            if load_time < 5:
                st.success(
                    f"⚡ **Fast Cache**: {relationship_data.get('total_policies', 0)} policies, {relationship_data.get('total_profiles', 0)} profiles"
                )
            elif load_time < 15:
                st.info(
                    f"🎯 **Standard Cache**: {relationship_data.get('total_policies', 0)} policies, {relationship_data.get('total_profiles', 0)} profiles"
                )
            else:
                st.warning(
                    f"🔍 **Comprehensive Cache**: {relationship_data.get('total_policies', 0)} policies, {relationship_data.get('total_profiles', 0)} profiles"
                )

            # Performance status with color coding
            if api_limits["estimated_server_load"] == "Low":
                st.success(
                    f"⏱️ **Performance**: {load_time:.1f}s load | {api_calls} API calls | {api_limits['estimated_server_load']} server load"
                )
            elif api_limits["estimated_server_load"] == "Medium":
                st.info(
                    f"⏱️ **Performance**: {load_time:.1f}s load | {api_calls} API calls | {api_limits['estimated_server_load']} server load"
                )
            else:
                st.warning(
                    f"⏱️ **Performance**: {load_time:.1f}s load | {api_calls} API calls | {api_limits['estimated_server_load']} server load"
                )

            st.caption(
                f"🔍 **Filter**: {relationship_data.get('smart_filter', 'unknown')} | **Network**: {perf_metrics['network_speed']} | **TTL**: 30min"
            )

        except Exception as e:
            # More informative error state
            st.error("⚠️ **Cache Status**: Unable to load data")
            st.caption(f"**Error**: {str(e)[:100]}...")

            # Provide actionable next steps
            if st.button("🔄 Try Loading Data", key="load_data_retry"):
                st.cache_data.clear()
                st.rerun()

    with col3:
        st.markdown("#### 🔧 Advanced Options")

        # Background refresh toggle
        if st.button("🔄 Refresh Cache", key="refresh_cache"):
            # Clear cache and reload
            st.cache_data.clear()
            st.rerun()

        # Performance metrics toggle
        show_metrics = st.checkbox(
            "📈 Show Performance", value=st.session_state.show_performance_metrics
        )
        st.session_state.show_performance_metrics = show_metrics

        # API monitoring
        try:
            relationship_data = get_cached_relationship_data(
                st.session_state.analysis_depth, st.session_state.smart_filter
            )
            api_calls = relationship_data.get("api_calls_made", 0)
            api_limits = check_api_rate_limits(auth, api_calls)

            # Show API recommendations
            for rec in api_limits["recommendations"][:1]:  # Show first recommendation
                if "⚠️" in rec or "🚨" in rec:
                    st.warning(rec)
                elif "✅" in rec:
                    st.success(rec)
                else:
                    st.info(rec)
        except:
            st.caption("💡 Load data to see API status")

    # Show expanded performance metrics if enabled
    if st.session_state.show_performance_metrics:
        st.markdown("---")
        st.markdown("#### 📈 Detailed Performance Metrics")

        try:
            perf_metrics = get_performance_metrics()
            relationship_data = get_cached_relationship_data(
                st.session_state.analysis_depth, st.session_state.smart_filter
            )
            api_limits = check_api_rate_limits(
                auth, relationship_data.get("api_calls_made", 0)
            )

            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric(
                    "🌐 Network",
                    perf_metrics["network_speed"],
                    perf_metrics["network_latency"],
                )

            with metric_col2:
                st.metric("🔥 CPU Usage", perf_metrics["cpu_usage"], "System load")

            with metric_col3:
                st.metric(
                    "💾 Memory",
                    perf_metrics["memory_usage"],
                    f"{perf_metrics['memory_available']} free",
                )

            with metric_col4:
                st.metric(
                    "🌊 API Load",
                    api_limits["estimated_server_load"],
                    f"{api_limits['recent_calls']} calls",
                )

            # Additional recommendations
            if len(api_limits["recommendations"]) > 1:
                st.markdown("**💡 Recommendations:**")
                for rec in api_limits["recommendations"][1:]:
                    st.caption(f"• {rec}")

        except Exception as e:
            st.error(f"⚠️ Performance metrics unavailable: {e}")
            st.caption(
                "💡 Install psutil for detailed system metrics: `pip install psutil`"
            )

    # Render detailed object analysis with relationship data
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Show current selection with detailed status
    object_titles = {
        "policies": "📋 Policies",
        "scripts": "⚙️ Scripts",
        "packages": "📦 Packages",
        "groups": "👥 Computer Groups",
        "profiles": "🔧 Configuration Profiles",
    }
    current_title = object_titles.get(
        st.session_state.selected_object_type, "📋 Policies"
    )

    # Add status indicator for current settings
    analysis_status = st.session_state.get("analysis_depth", "standard")
    filter_status = st.session_state.get("smart_filter", "recent")

    # Create a status bar with current selection and settings
    status_col1, status_col2 = st.columns([3, 1])
    with status_col1:
        st.markdown(
            f'<h2 class="section-title">{current_title}</h2>', unsafe_allow_html=True
        )
    with status_col2:
        st.caption(f"📊 **Analysis**: {analysis_status}")
        st.caption(f"🔍 **Filter**: {filter_status}")

    # Add a visual separator with current status
    st.markdown("---")

    # Quick status summary
    try:
        relationship_data = get_cached_relationship_data(
            st.session_state.analysis_depth, st.session_state.smart_filter
        )
        load_time = relationship_data.get("load_time", 0)
        if load_time > 0:
            status_emoji = "⚡" if load_time < 5 else "🎯" if load_time < 15 else "🔍"
            st.info(
                f"{status_emoji} **Ready**: Cache loaded in {load_time:.1f}s | {relationship_data.get('total_policies', 0)} policies, {relationship_data.get('total_profiles', 0)} profiles"
            )
        else:
            st.warning("🔄 **Loading**: Preparing data with current settings...")
    except:
        st.warning("🔄 **Initializing**: First load with current settings...")

    # Clear container for content
    st.markdown("---")

    # Render selected objects with FULL relationship analysis
    render_object_cards(st.session_state.selected_object_type, auth, reverse_lookup)

    # Cross-viewer navigation footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button(
            "🔍 Detailed Analysis →",
            help="Open Compact Detailed Viewer for comprehensive analysis",
        ):
            # Save current state and open detailed viewer
            save_shared_viewer_state(
                {
                    "selected_object_type": st.session_state.selected_object_type,
                    "analysis_depth": st.session_state.analysis_depth,
                    "search_query": st.session_state.get("search_query", ""),
                    "context": "dashboard_exploration",
                }
            )
            webbrowser.open("http://localhost:8502")

    with col2:
        st.caption(
            f"🍎 **Apple Dashboard** • Last updated: {datetime.now().strftime('%H:%M:%S')} • **Click bubbles for detailed analysis**"
        )

    with col3:
        if st.button("📱 Mobile Viewer →", help="Switch to mobile-optimized viewer"):
            webbrowser.open("http://localhost:8503")


if __name__ == "__main__":
    main()
