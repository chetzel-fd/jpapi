#!/usr/bin/env python3
"""
Filter Service - SOLID SRP compliance
Handles all data filtering and search operations
"""
from typing import Dict, Any, Optional
import pandas as pd
from abc import ABC, abstractmethod


class FilterServiceInterface(ABC):
    """Interface for filtering operations - SOLID DIP"""

    @abstractmethod
    def apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe"""
        pass


class FilterService(FilterServiceInterface):
    """Filter service implementation - SOLID SRP"""

    def __init__(self):
        self.computer_keywords = [
            "mac",
            "macbook",
            "computer",
            "laptop",
            "desktop",
            "imac",
        ]
        self.mobile_keywords = ["iphone", "ipad", "mobile", "device", "ios", "android"]
        self.user_keywords = ["user", "people", "person", "staff", "employee"]

    def apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply all filters to dataframe - SOLID SRP"""
        if df is None or df.empty:
            return df

        # Apply search type filter
        df = self._apply_search_type_filter(df, filters.get("search_type", "All"))

        # Apply status filter
        df = self._apply_status_filter(df, filters.get("status_filter", "All"))

        # Apply name search filter
        df = self._apply_name_search_filter(df, filters.get("name_search", ""))

        return df

    def _apply_search_type_filter(
        self, df: pd.DataFrame, search_type: str
    ) -> pd.DataFrame:
        """Apply search type filter - SOLID SRP"""
        if search_type == "All":
            return df

        if search_type == "Computer":
            return self._filter_by_keywords(df, self.computer_keywords)
        elif search_type == "Mobile":
            return self._filter_by_keywords(df, self.mobile_keywords)
        elif search_type == "User":
            return self._filter_by_keywords(df, self.user_keywords)

        return df

    def _apply_status_filter(
        self, df: pd.DataFrame, status_filter: str
    ) -> pd.DataFrame:
        """Apply status filter - SOLID SRP"""
        if status_filter == "All":
            return df

        if "Smart" in df.columns:
            if status_filter == "Smart":
                return df[df["Smart"] == True]
            elif status_filter == "Static":
                return df[df["Smart"] == False]

        return df

    def _apply_name_search_filter(
        self, df: pd.DataFrame, name_search: str
    ) -> pd.DataFrame:
        """Apply name search filter - SOLID SRP"""
        if not name_search or "Name" not in df.columns:
            return df

        search_term = name_search.lower()
        return df[df["Name"].str.contains(search_term, case=False, na=False)]

    def _filter_by_keywords(self, df: pd.DataFrame, keywords: list) -> pd.DataFrame:
        """Filter dataframe by keywords - SOLID SRP"""
        if "Name" not in df.columns:
            return df

        pattern = "|".join(keywords)
        return df[df["Name"].str.contains(pattern, case=False, na=False)]

    def get_available_search_types(self) -> list:
        """Get available search types - SOLID SRP"""
        return ["All", "Computer", "Mobile", "User"]

    def get_available_status_filters(self) -> list:
        """Get available status filters - SOLID SRP"""
        return ["All", "Smart", "Static"]
