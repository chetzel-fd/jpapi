#!/usr/bin/env python3
"""
Optional UI Imports for JPAPI Distribution
Provides graceful fallbacks when Streamlit and Dash are not available
"""

import sys
from typing import Optional, Any, Dict, Callable
import warnings

# Global flags for UI availability
STREAMLIT_AVAILABLE = False
DASH_AVAILABLE = False
PLOTLY_AVAILABLE = False

# Import attempts with fallbacks
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
    print("✅ Streamlit available - UI features enabled")
except ImportError:
    print("⚠️  Streamlit not available - UI features disabled")
    # Create mock streamlit module
    class MockStreamlit:
        def __getattr__(self, name):
            def mock_function(*args, **kwargs):
                raise ImportError(
                    f"Streamlit feature '{name}' requires optional dependency. "
                    "Install with: pip install 'jpapi[ui]'"
                )
            return mock_function
    st = MockStreamlit()

try:
    import dash
    from dash import dcc, html, Input, Output, State, callback, dash_table
    DASH_AVAILABLE = True
    print("✅ Dash available - Dashboard features enabled")
except ImportError:
    print("⚠️  Dash not available - Dashboard features disabled")
    # Create mock dash modules
    class MockDash:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Dash features require optional dependency. "
                "Install with: pip install 'jpapi[ui]'"
            )
        def __getattr__(self, name):
            def mock_function(*args, **kwargs):
                raise ImportError(
                    f"Dash feature '{name}' requires optional dependency. "
                    "Install with: pip install 'jpapi[ui]'"
                )
            return mock_function
    
    dash = MockDash
    dcc = MockDash()
    html = MockDash()
    Input = MockDash
    Output = MockDash
    State = MockDash
    callback = MockDash
    dash_table = MockDash()

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
    print("✅ Plotly available - Chart features enabled")
except ImportError:
    print("⚠️  Plotly not available - Chart features disabled")
    # Create mock plotly modules
    class MockPlotly:
        def __getattr__(self, name):
            def mock_function(*args, **kwargs):
                raise ImportError(
                    f"Plotly feature '{name}' requires optional dependency. "
                    "Install with: pip install 'jpapi[ui]'"
                )
            return mock_function
    go = MockPlotly()
    px = MockPlotly()

def check_ui_dependencies() -> Dict[str, bool]:
    """
    Check which UI dependencies are available
    
    Returns:
        Dict with availability status for each UI framework
    """
    return {
        'streamlit': STREAMLIT_AVAILABLE,
        'dash': DASH_AVAILABLE,
        'plotly': PLOTLY_AVAILABLE
    }

def require_streamlit(func: Callable) -> Callable:
    """
    Decorator to ensure Streamlit is available before running function
    """
    def wrapper(*args, **kwargs):
        if not STREAMLIT_AVAILABLE:
            raise ImportError(
                f"Function '{func.__name__}' requires Streamlit. "
                "Install with: pip install 'jpapi[ui]'"
            )
        return func(*args, **kwargs)
    return wrapper

def require_dash(func: Callable) -> Callable:
    """
    Decorator to ensure Dash is available before running function
    """
    def wrapper(*args, **kwargs):
        if not DASH_AVAILABLE:
            raise ImportError(
                f"Function '{func.__name__}' requires Dash. "
                "Install with: pip install 'jpapi[ui]'"
            )
        return func(*args, **kwargs)
    return wrapper

def get_ui_status_message() -> str:
    """
    Get a formatted message about UI feature availability
    """
    status = check_ui_dependencies()
    
    available_features = []
    missing_features = []
    
    for feature, available in status.items():
        if available:
            available_features.append(f"✅ {feature.title()}")
        else:
            missing_features.append(f"❌ {feature.title()}")
    
    message = "🎨 UI Feature Status:\n"
    
    if available_features:
        message += "Available: " + ", ".join(available_features) + "\n"
    
    if missing_features:
        message += "Missing: " + ", ".join(missing_features) + "\n"
        message += "💡 Install UI features with: pip install 'jpapi[ui]'"
    
    return message

def show_experimental_ui_warning():
    """
    Show warning about experimental UI features
    """