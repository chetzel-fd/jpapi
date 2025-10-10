"""
Theme Manager - Single Responsibility Principle
Manages application theming and styling
"""

import streamlit as st
from typing import Dict, Any, Optional

# Import constants directly
APP_NAME = "JPAPI Manager"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "JAMF Pro API Management Dashboard"

# UI Constants
DEFAULT_PAGE_TITLE = "JPAPI Manager"
DEFAULT_PAGE_ICON = "⚡"
DEFAULT_LAYOUT = "wide"
DEFAULT_SIDEBAR_STATE = "expanded"

# Cache Constants
CACHE_PREFIX = "data_"
CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_MAX_SIZE_MB = 100

# Export Constants
DEFAULT_EXPORT_FORMAT = "csv"
SUPPORTED_EXPORT_FORMATS = ["csv", "json", "xlsx"]
MAX_EXPORT_ROWS = 10000

# Status Constants
VALID_STATUSES = ["Active", "Deleted", "Inactive"]
DEFAULT_STATUS = "Active"

# Smart Group Constants
SMART_TRUE_VALUES = [True, 1, "True", "true", "1"]
SMART_FALSE_VALUES = [False, 0, "False", "false", "0"]

# File Pattern Constants
CSV_FILE_EXTENSIONS = [".csv"]
JSON_FILE_EXTENSIONS = [".json"]
EXCEL_FILE_EXTENSIONS = [".xlsx", ".xls"]

# Environment Constants
DEFAULT_ENVIRONMENT = "sandbox"
ENVIRONMENT_SANDBOX = "sandbox"
ENVIRONMENT_PRODUCTION = "production"

# Object Type Constants
DEFAULT_OBJECT_TYPE = "searches"
OBJECT_TYPE_SEARCHES = "searches"
OBJECT_TYPE_POLICIES = "policies"
OBJECT_TYPE_PROFILES = "profiles"
OBJECT_TYPE_SCRIPTS = "scripts"

# UI Component Constants
HEADER_HEIGHT = 60
SIDEBAR_WIDTH = 300
CARD_HEIGHT = 120
BUTTON_HEIGHT = 36
BUTTON_WIDTH = 36

# Color Constants
COLOR_PRIMARY = "#1f77b4"
COLOR_SECONDARY = "#ff7f0e"
COLOR_SUCCESS = "#2ca02c"
COLOR_WARNING = "#d62728"
COLOR_INFO = "#17a2b8"

# Status Colors
STATUS_ACTIVE_COLOR = "#28a745"
STATUS_DELETED_COLOR = "#dc3545"
STATUS_INACTIVE_COLOR = "#6c757d"

# Animation Constants
ANIMATION_DURATION_MS = 300
ANIMATION_EASING = "ease-in-out"

# Validation Constants
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 255
REQUIRED_COLUMNS = ["Name", "Status", "Modified"]
OPTIONAL_COLUMNS = ["Smart", "Description", "Category"]

# Error Messages
ERROR_NO_DATA_FOUND = "No data found for the selected criteria"
ERROR_INVALID_ENVIRONMENT = "Invalid environment selected"
ERROR_INVALID_OBJECT_TYPE = "Invalid object type selected"
ERROR_CSV_LOAD_FAILED = "Failed to load CSV data"
ERROR_CACHE_ERROR = "Cache operation failed"

# Success Messages
SUCCESS_DATA_LOADED = "Data loaded successfully"
SUCCESS_CACHE_CLEARED = "Cache cleared successfully"
SUCCESS_DATA_EXPORTED = "Data exported successfully"
SUCCESS_DATA_GATHERED = "Data gathered successfully"


class ThemeManager:
    """Theme and styling management"""

    def __init__(self):
        self.current_theme = "default"
        self._initialize_theme()

    def _initialize_theme(self) -> None:
        """Initialize default theme"""
        self.apply_default_theme()

    def apply_default_theme(self) -> None:
        """Apply default theme styling"""
        st.markdown(
            f"""
        <style>
        /* Global Styles */
        .main {{
            padding-top: 1rem;
        }}
        
        /* Header Styles */
        .header-buttons {{
            display: flex;
            gap: 8px;
            align-items: center;
            justify-content: flex-end;
        }}
        
        .header-buttons .stButton > button {{
            width: {BUTTON_WIDTH}px;
            height: {BUTTON_HEIGHT}px;
            min-width: {BUTTON_WIDTH}px;
            padding: 0;
            border-radius: 8px;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #e1e5e9;
            background-color: #ffffff;
            color: #333333;
            transition: all 0.2s ease;
        }}
        
        .header-buttons .stButton > button:hover {{
            background-color: #f8f9fa;
            border-color: {COLOR_PRIMARY};
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* Object Card Styles */
        .object-card {{
            background-color: #ffffff;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }}
        
        .object-card:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transform: translateY(-1px);
        }}
        
        .object-title {{
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 8px;
        }}
        
        .object-details {{
            font-size: 14px;
            color: #666666;
            margin-bottom: 8px;
        }}
        
        /* Status Badge Styles */
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .status-active {{
            background-color: {STATUS_ACTIVE_COLOR};
            color: white;
        }}
        
        .status-deleted {{
            background-color: {STATUS_DELETED_COLOR};
            color: white;
        }}
        
        .status-inactive {{
            background-color: {STATUS_INACTIVE_COLOR};
            color: white;
        }}
        
        /* Popover Styles */
        .stPopover {{
            font-size: 14px;
        }}
        
        .stPopover .stMarkdown {{
            font-size: 14px;
        }}
        
        .stPopover .stMarkdown h3 {{
            font-size: 16px;
            margin-bottom: 8px;
        }}
        
        .stPopover .stMarkdown p {{
            font-size: 14px;
            margin-bottom: 4px;
        }}
        
        .stPopover .stButton > button {{
            font-size: 14px;
            padding: 8px 16px;
        }}
        
        .stPopover .stSelectbox > div > div {{
            font-size: 14px;
        }}
        
        .stPopover .stCheckbox > label {{
            font-size: 14px;
        }}
        
        .stPopover .stAlert {{
            font-size: 14px;
        }}
        
        /* Info Panel Styles */
        .info-panel {{
            background-color: #f8f9fa;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        }}
        
        .info-panel h4 {{
            color: #333333;
            margin-bottom: 8px;
        }}
        
        .info-panel p {{
            color: #666666;
            margin-bottom: 4px;
        }}
        
        /* Animation Styles */
        .fade-in {{
            animation: fadeIn {ANIMATION_DURATION_MS}ms {ANIMATION_EASING};
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .header-buttons {{
                flex-direction: column;
                gap: 4px;
            }}
            
            .object-card {{
                margin: 4px 0;
                padding: 12px;
            }}
        }}
        </style>
        """,
            unsafe_allow_html=True,
        )

    def apply_dark_theme(self) -> None:
        """Apply dark theme styling"""
        st.markdown(
            """
        <style>
        /* Dark theme styles would go here */
        .main {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        
        .object-card {
            background-color: #2d2d2d;
            border-color: #404040;
            color: #ffffff;
        }
        
        .header-buttons .stButton > button {
            background-color: #2d2d2d;
            border-color: #404040;
            color: #ffffff;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def get_theme_colors(self) -> Dict[str, str]:
        """Get current theme colors"""
        themes = {
            "default": {
                "primary": COLOR_PRIMARY,
                "secondary": COLOR_SECONDARY,
                "success": COLOR_SUCCESS,
                "warning": COLOR_WARNING,
                "info": COLOR_INFO,
                "background": "#ffffff",
                "text": "#333333",
            },
            "dark": {
                "primary": "#4a9eff",
                "secondary": "#ff6b35",
                "success": "#28a745",
                "warning": "#ffc107",
                "info": "#17a2b8",
                "background": "#1a1a1a",
                "text": "#ffffff",
            },
        }
        return themes.get(self.current_theme, themes["default"])

    def set_theme(self, theme_name: str) -> None:
        """Set current theme"""
        if theme_name == "dark":
            self.apply_dark_theme()
        else:
            self.apply_default_theme()
        self.current_theme = theme_name

    def get_component_styles(self, component_type: str) -> Dict[str, Any]:
        """Get styles for specific component type"""
        styles = {
            "header": {
                "button_width": BUTTON_WIDTH,
                "button_height": BUTTON_HEIGHT,
                "font_size": "18px",
            },
            "object_card": {
                "card_height": CARD_HEIGHT,
                "border_radius": "8px",
                "padding": "16px",
            },
            "status_badge": {
                "border_radius": "12px",
                "font_size": "12px",
                "padding": "4px 8px",
            },
        }
        return styles.get(component_type, {})
