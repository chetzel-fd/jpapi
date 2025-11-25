#!/usr/bin/env python3
"""
Notification Manager Implementation - SOLID Principles
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

# Setup path and load local interfaces
_current_dir = Path(__file__).parent
_project_src = _current_dir.parent.parent
for p in [str(_current_dir), str(_project_src)]:
    while p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(_current_dir))
sys.path.insert(1, str(_project_src))

import importlib.util

_interfaces_path = os.path.join(str(_current_dir), "interfaces.py")
_spec = importlib.util.spec_from_file_location("streamlit_interfaces", _interfaces_path)
_interfaces = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_interfaces)
NotificationManager = _interfaces.NotificationManager


class StreamlitNotificationManager(NotificationManager):
    """Concrete implementation of NotificationManager using Streamlit session state"""

    def __init__(self, session_key: str = "notifications"):
        self.session_key = session_key
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = []

    def add_notification(self, message: str, notification_type: str = "info") -> None:
        """Add a notification"""
        notification = {
            "message": message,
            "type": notification_type,
            "timestamp": pd.Timestamp.now(),
        }
        st.session_state[self.session_key].append(notification)

    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications"""
        return st.session_state[self.session_key]

    def clear_notifications(self) -> None:
        """Clear all notifications"""
        st.session_state[self.session_key] = []

    def get_notification_count(self) -> int:
        """Get count of notifications"""
        return len(st.session_state[self.session_key])

    def get_notifications_by_type(self, notification_type: str) -> List[Dict[str, Any]]:
        """Get notifications by type"""
        return [
            n
            for n in st.session_state[self.session_key]
            if n["type"] == notification_type
        ]
