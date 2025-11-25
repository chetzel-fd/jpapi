#!/usr/bin/env python3
"""
Object Selector Implementation - SOLID Principles
"""

import streamlit as st
import sys
import os
from pathlib import Path
from typing import List

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
ObjectSelector = _interfaces.ObjectSelector


class StreamlitObjectSelector(ObjectSelector):
    """Concrete implementation of ObjectSelector using Streamlit session state"""

    def __init__(self, session_key: str = "selected_objects"):
        self.session_key = session_key
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = set()

    def select_object(self, object_id: str) -> None:
        """Select an object by ID"""
        st.session_state[self.session_key].add(object_id)

    def deselect_object(self, object_id: str) -> None:
        """Deselect an object by ID"""
        st.session_state[self.session_key].discard(object_id)

    def get_selected_objects(self) -> List[str]:
        """Get list of selected object IDs"""
        return list(st.session_state[self.session_key])

    def clear_selection(self) -> None:
        """Clear all selected objects"""
        st.session_state[self.session_key].clear()

    def is_selected(self, object_id: str) -> bool:
        """Check if an object is selected"""
        return object_id in st.session_state[self.session_key]

    def toggle_selection(self, object_id: str) -> None:
        """Toggle selection of an object"""
        if self.is_selected(object_id):
            self.deselect_object(object_id)
        else:
            self.select_object(object_id)
