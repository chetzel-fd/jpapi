#!/usr/bin/env python3
"""
Analyzer Interfaces - SOLID Principles
Defines contracts for the Reverse Object Analyzer components
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd


class RelationshipEngine(ABC):
    """Interface for analyzing object relationships"""

    @abstractmethod
    def analyze_object(self, obj_type: str, obj_id: str) -> Dict[str, Any]:
        """
        Analyze relationships for a single object

        Returns:
            {
                'object': {'type': str, 'id': str, 'name': str},
                'uses': [{'type': str, 'id': str, 'name': str}, ...],
                'used_by': [{'type': str, 'id': str, 'name': str}, ...],
                'usage_count': int
            }
        """
        pass

    @abstractmethod
    def analyze_batch(self, object_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze relationships for multiple objects

        Args:
            object_list: [{'type': str, 'id': str}, ...]

        Returns:
            {
                'objects': [...],
                'shared_dependencies': [...],
                'dependency_matrix': pd.DataFrame
            }
        """
        pass

    @abstractmethod
    def get_usage_count(self, obj_type: str, obj_id: str) -> int:
        """Get number of times object is referenced"""
        pass

    @abstractmethod
    def get_dependent_objects(self, obj_type: str, obj_id: str) -> List[Dict[str, Any]]:
        """Get list of objects that depend on this object"""
        pass

    @abstractmethod
    def build_dependency_tree(
        self, obj_type: str, obj_id: str, max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Build hierarchical dependency tree

        Returns:
            {
                'root': {'type': str, 'id': str, 'name': str},
                'children': [recursive tree structure],
                'depth': int
            }
        """
        pass


class OrphanDetector(ABC):
    """Interface for finding orphaned/unused objects"""

    @abstractmethod
    def find_orphaned_objects(
        self, obj_type: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find orphaned objects by type

        Args:
            obj_type: Specific type to check, or None for all types

        Returns:
            {
                'groups': [{'id': str, 'name': str, 'last_modified': str}, ...],
                'scripts': [...],
                'packages': [...]
            }
        """
        pass

    @abstractmethod
    def generate_cleanup_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive cleanup report

        Returns:
            {
                'total_orphans': int,
                'by_type': {'groups': int, 'scripts': int, ...},
                'recommendations': [str, ...],
                'safe_to_delete': [{'type': str, 'id': str, 'name': str}, ...]
            }
        """
        pass

    @abstractmethod
    def is_orphaned(self, obj_type: str, obj_id: str) -> bool:
        """Check if specific object is orphaned"""
        pass


class ImpactAnalyzer(ABC):
    """Interface for assessing deletion impact"""

    @abstractmethod
    def assess_deletion_impact(self, obj_type: str, obj_id: str) -> Dict[str, Any]:
        """
        Assess impact of deleting a single object

        Returns:
            {
                'object': {'type': str, 'id': str, 'name': str},
                'risk_level': str,  # 'low', 'medium', 'high'
                'affected_objects': [{'type': str, 'id': str, 'name': str}, ...],
                'affected_count': int,
                'recommendations': [str, ...],
                'can_delete_safely': bool
            }
        """
        pass

    @abstractmethod
    def assess_batch_impact(self, object_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Assess impact of deleting multiple objects

        Returns:
            {
                'objects': [...],
                'total_affected': int,
                'risk_level': str,
                'cascading_deletions': [...]
            }
        """
        pass

    @abstractmethod
    def get_affected_objects(self, obj_type: str, obj_id: str) -> List[Dict[str, Any]]:
        """Get list of objects affected by deletion"""
        pass

    @abstractmethod
    def calculate_risk_score(self, obj_type: str, obj_id: str) -> str:
        """
        Calculate risk level for deletion

        Returns:
            'low', 'medium', or 'high'
        """
        pass


class DataProvider(ABC):
    """Interface for loading and managing object data"""

    @abstractmethod
    def load_objects(self, obj_type: str, environment: str) -> pd.DataFrame:
        """Load objects of specific type for environment"""
        pass

    @abstractmethod
    def get_all_object_types(self) -> List[str]:
        """Get list of all available object types"""
        pass

    @abstractmethod
    def get_object_by_id(self, obj_type: str, obj_id: str) -> Optional[Dict[str, Any]]:
        """Get single object by type and ID"""
        pass

    @abstractmethod
    def reload_data(self, obj_type: Optional[str] = None) -> bool:
        """Reload data from source (CSV or API)"""
        pass


class AnalyzerUIController(ABC):
    """Interface for UI rendering operations"""

    @abstractmethod
    def render_header(self) -> None:
        """Render the analyzer header"""
        pass

    @abstractmethod
    def render_mode_selector(self) -> str:
        """
        Render mode selection UI

        Returns:
            Selected mode: 'individual', 'batch', 'orphan', or 'impact'
        """
        pass

    @abstractmethod
    def render_object_selector(self, mode: str) -> Any:
        """Render object selection UI based on current mode"""
        pass

    @abstractmethod
    def render_relationship_view(self, relationships: Dict[str, Any]) -> None:
        """Render relationship visualization"""
        pass

    @abstractmethod
    def render_orphan_results(self, orphans: Dict[str, List[Dict[str, Any]]]) -> None:
        """Render orphaned objects results"""
        pass

    @abstractmethod
    def render_impact_report(self, impact_data: Dict[str, Any]) -> None:
        """Render deletion impact report"""
        pass

    @abstractmethod
    def render_fab(self) -> None:
        """Render floating action button with analyzer stats"""
        pass







