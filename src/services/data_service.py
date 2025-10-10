#!/usr/bin/env python3
"""
Data Service - SOLID SRP compliance
Handles all data loading, processing, and management operations
"""
from typing import Optional, Dict, Any
import pandas as pd
from abc import ABC, abstractmethod


class DataServiceInterface(ABC):
    """Interface for data operations - SOLID DIP"""

    @abstractmethod
    def load_data(self, manager) -> Optional[pd.DataFrame]:
        """Load data using manager"""
        pass

    @abstractmethod
    def refresh_data(self, manager) -> tuple[bool, str]:
        """Refresh data from source"""
        pass


class DataService(DataServiceInterface):
    """Data service implementation - SOLID SRP"""

    def __init__(self):
        self.cache = {}

    def load_data(self, manager) -> Optional[pd.DataFrame]:
        """Load data using manager - SOLID DIP"""
        if not manager:
            return None

        try:
            # Load data from manager
            df = manager.load_data()

            # Cache the data
            cache_key = f"{manager.type}_{id(manager)}"
            self.cache[cache_key] = df

            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def refresh_data(self, manager) -> tuple[bool, str]:
        """Refresh data from source"""
        if not manager:
            return False, "No manager provided"

        try:
            # Clear cache
            cache_key = f"{manager.type}_{id(manager)}"
            if cache_key in self.cache:
                del self.cache[cache_key]

            # Reload data
            df = self.load_data(manager)

            if df is not None:
                return True, f"Successfully refreshed {len(df)} records"
            else:
                return False, "Failed to load data after refresh"

        except Exception as e:
            return False, f"Refresh failed: {e}"

    def get_cached_data(self, manager) -> Optional[pd.DataFrame]:
        """Get cached data for manager"""
        cache_key = f"{manager.type}_{id(manager)}"
        return self.cache.get(cache_key)

    def clear_cache(self, manager=None):
        """Clear cache for specific manager or all"""
        if manager:
            cache_key = f"{manager.type}_{id(manager)}"
            if cache_key in self.cache:
                del self.cache[cache_key]
        else:
            self.cache.clear()
