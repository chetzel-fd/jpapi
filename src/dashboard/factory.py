#!/usr/bin/env python3
"""
Simple ManagerFactory fallback for dashboard applications
"""
import streamlit as st
import pandas as pd


class BaseManager:
    """Base manager class with common functionality"""

    def __init__(self, manager_type):
        self.type = manager_type
        self.data = []
        self.status = "demo"

    def load_data(self):
        """Load data for the manager - demo implementation"""
        # Return demo DataFrame with standard column names
        return pd.DataFrame(
            {
                "ID": [1, 2, 3],
                "Name": [
                    f"Demo {self.type.replace('-', ' ').title()} 1",
                    f"Demo {self.type.replace('-', ' ').title()} 2",
                    f"Demo {self.type.replace('-', ' ').title()} 3",
                ],
                "Status": ["Active", "Inactive", "Pending"],
                "Type": [self.type.replace("-", " ").title()] * 3,
                "Smart": [True, False, True],
            }
        )

    def get_data(self):
        """Get current data"""
        return self.data

    def set_data(self, data):
        """Set data"""
        self.data = data

    def get_display_name(self, row):
        """Get display name for a row - demo implementation"""
        if hasattr(row, "get"):
            return row.get("Name", row.get("name", "Unknown"))
        else:
            return "Unknown"

    def get_object_type(self, object_id, df):
        """Get object type for a given ID - demo implementation"""
        return self.type.replace("-", " ").title()


class ManagerFactory:
    """Simple factory class for dashboard applications"""

    def __init__(self):
        self.available_types = [
            "advanced-searches",
            "policies",
            "mobile-devices",
            "computer-groups",
        ]

    def get_available_types(self):
        """Return available manager types"""
        return self.available_types

    @staticmethod
    def get_available_managers():
        """Return available manager types (legacy method)"""
        return ["advanced-searches", "policies", "mobile-devices", "computer-groups"]

    def create_manager(self, manager_type):
        """Create a manager instance"""
        return BaseManager(manager_type)
