#!/usr/bin/env python3
"""
Unified Backend Client for JPAPIDev
Consolidates all backend API communication patterns
"""

import requests
from typing import Dict, Any, Optional

class BackendClient:
    """Unified client for communicating with backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8900"):
        self.base_url = base_url
    
    def _make_request(self, endpoint: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Make request to backend API with unified error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend API error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def check_health(self) -> Optional[Dict[str, Any]]:
        """Check backend health"""
        return self._make_request("/api/health")
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Get summary statistics"""
        return self._make_request("/api/cache/stats")
    
    def get_objects(self, object_type: str, limit: int = 1000) -> Optional[Dict[str, Any]]:
        """Get objects of specific type"""
        return self._make_request(f"/api/objects/{object_type}?limit={limit}")
    
    def get_object_detail(self, object_type: str, object_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific object"""
        return self._make_request(f"/api/objects/{object_type}/{object_id}")
    
    def get_relationships(self, object_type: str, object_id: str, object_name: str = "") -> Optional[Dict[str, Any]]:
        """Get relationships for an object using ENHANCED endpoint with intelligent caching"""
        # Backend inconsistency: objects API uses 'groups' but relationships API uses 'computer_groups'
        if object_type == 'groups':
            relationship_type = 'computer_groups'
        else:
            relationship_type = object_type
        
        # Use intelligent caching - let the backend handle cache TTL
        return self._make_request(f"/api/relationships/enhanced/{relationship_type}/{object_id}?object_name={object_name}")
    
    def get_analytics_stats(self) -> Optional[Dict[str, Any]]:
        """Get analytics statistics from the analytics backend"""
        return self._make_request("/api/analytics/stats")
