#!/usr/bin/env python3
"""
Dashboard Controller - SOLID SRP compliance
Orchestrates services for dashboard operations
"""
from typing import Optional, Dict, Any, List
import pandas as pd
from abc import ABC, abstractmethod

from services.data_service import DataServiceInterface
from services.filter_service import FilterServiceInterface
from services.manager_coordinator import ManagerCoordinatorInterface


class DashboardControllerInterface(ABC):
    """Interface for dashboard operations - SOLID DIP"""

    @abstractmethod
    def load_and_filter_data(
        self, object_type: str, filters: Dict[str, Any]
    ) -> Optional[pd.DataFrame]:
        """Load and filter data for object type"""
        pass

    @abstractmethod
    def refresh_data(self, object_type: str) -> tuple[bool, str]:
        """Refresh data for object type"""
        pass

    @abstractmethod
    def get_available_types(self) -> List[str]:
        """Get available object types"""
        pass


class DashboardController(DashboardControllerInterface):
    """Dashboard controller implementation - SOLID SRP"""

    def __init__(
        self,
        data_service: DataServiceInterface,
        filter_service: FilterServiceInterface,
        manager_coordinator: ManagerCoordinatorInterface,
    ):
        self.data_service = data_service
        self.filter_service = filter_service
        self.manager_coordinator = manager_coordinator

    def load_and_filter_data(
        self, object_type: str, filters: Dict[str, Any]
    ) -> Optional[pd.DataFrame]:
        """Load and filter data for object type - SOLID SRP"""
        # Create manager
        manager = self.manager_coordinator.create_manager(object_type)
        if not manager:
            return None

        # Load data
        df = self.data_service.load_data(manager)
        if df is None or df.empty:
            return None

        # Apply filters
        filtered_df = self.filter_service.apply_filters(df, filters)

        return filtered_df

    def refresh_data(self, object_type: str) -> tuple[bool, str]:
        """Refresh data for object type - SOLID SRP"""
        # Get existing manager or create new one
        manager = self.manager_coordinator.get_manager(object_type)
        if not manager:
            manager = self.manager_coordinator.create_manager(object_type)

        if not manager:
            return False, "Could not create manager"

        # Refresh data
        return self.data_service.refresh_data(manager)

    def get_available_types(self) -> List[str]:
        """Get available object types - SOLID DIP"""
        return self.manager_coordinator.get_available_types()

    def get_manager(self, object_type: str):
        """Get manager for object type"""
        return self.manager_coordinator.get_manager(object_type)

    def get_data_service(self) -> DataServiceInterface:
        """Get data service - for UI access"""
        return self.data_service

    def get_filter_service(self) -> FilterServiceInterface:
        """Get filter service - for UI access"""
        return self.filter_service
