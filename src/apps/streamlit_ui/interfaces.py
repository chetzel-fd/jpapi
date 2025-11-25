#!/usr/bin/env python3
"""
Interfaces for JPAPI Manager - SOLID Principles
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import pandas as pd


class DataLoader(ABC):
    """Interface for data loading operations"""

    @abstractmethod
    def load_data(self, object_type: str, environment: str) -> pd.DataFrame:
        """Load data for the specified object type and environment"""
        pass


class DataExporter(ABC):
    """Interface for data export operations"""

    @abstractmethod
    def export_data(self, object_type: str, environment: str) -> bool:
        """Export data for the specified object type and environment"""
        pass


class ObjectSelector(ABC):
    """Interface for object selection operations"""

    @abstractmethod
    def select_object(self, object_id: str) -> None:
        """Select an object by ID"""
        pass

    @abstractmethod
    def deselect_object(self, object_id: str) -> None:
        """Deselect an object by ID"""
        pass

    @abstractmethod
    def get_selected_objects(self) -> List[str]:
        """Get list of selected object IDs"""
        pass

    @abstractmethod
    def clear_selection(self) -> None:
        """Clear all selected objects"""
        pass

    @abstractmethod
    def is_selected(self, object_id: str) -> bool:
        """Check if an object is selected"""
        pass

    @abstractmethod
    def toggle_selection(self, object_id: str) -> None:
        """Toggle selection of an object"""
        pass


class ObjectDeleter(ABC):
    """Interface for object deletion operations"""

    @abstractmethod
    def delete_objects(self, object_ids: List[str]) -> Dict[str, Any]:
        """Delete objects by their IDs"""
        pass


class UIController(ABC):
    """Interface for UI control operations"""

    @abstractmethod
    def render_header(self) -> None:
        """Render the application header"""
        pass

    @abstractmethod
    def render_data_grid(self, data: pd.DataFrame) -> None:
        """Render the data grid"""
        pass

    @abstractmethod
    def render_fab(self) -> None:
        """Render the floating action button"""
        pass

    @abstractmethod
    def render_delete_confirmation(self, object_ids: List[str]) -> None:
        """Render delete confirmation dialog"""
        pass


class NotificationManager(ABC):
    """Interface for notification management"""

    @abstractmethod
    def add_notification(self, message: str, notification_type: str) -> None:
        """Add a notification"""
        pass

    @abstractmethod
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications"""
        pass

    @abstractmethod
    def clear_notifications(self) -> None:
        """Clear all notifications"""
        pass
