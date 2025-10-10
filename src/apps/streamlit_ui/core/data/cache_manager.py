"""
Cache Manager - Single Responsibility Principle
Handles data caching using Streamlit session state
"""

import streamlit as st
from typing import Optional, Dict, Any
import pandas as pd
from .interfaces import CacheInterface


class CacheManager(CacheInterface):
    """Cache management using Streamlit session state"""

    def __init__(self):
        self.cache_prefix = "data_"

    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached data"""
        cache_key = f"{self.cache_prefix}{key}"
        return st.session_state.get(cache_key)

    def set(self, key: str, data: pd.DataFrame) -> None:
        """Cache data"""
        cache_key = f"{self.cache_prefix}{key}"
        st.session_state[cache_key] = data

    def clear(self, pattern: Optional[str] = None) -> None:
        """Clear cache by pattern"""
        if pattern is None:
            # Clear all data cache
            keys_to_remove = [
                key
                for key in st.session_state.keys()
                if key.startswith(self.cache_prefix)
            ]
            for key in keys_to_remove:
                del st.session_state[key]
        else:
            # Clear specific pattern
            cache_key = f"{self.cache_prefix}{pattern}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]

    def invalidate(self, object_type: str, environment: str) -> None:
        """Invalidate specific cache"""
        cache_key = f"{object_type}_{environment}"
        self.clear(cache_key)

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data"""
        cache_keys = [
            key for key in st.session_state.keys() if key.startswith(self.cache_prefix)
        ]

        info = {}
        for key in cache_keys:
            data = st.session_state[key]
            if isinstance(data, pd.DataFrame):
                info[key] = {
                    "rows": len(data),
                    "columns": list(data.columns),
                    "size": data.memory_usage(deep=True).sum(),
                }

        return info
