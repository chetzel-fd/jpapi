"""
Data Layer Interfaces - Dependency Inversion Principle
Abstract interfaces for data loading and validation
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd


class DataLoaderInterface(ABC):
    """Data loader interface - Dependency Inversion Principle"""

    @abstractmethod
    def load(self, object_type: str, environment: str) -> pd.DataFrame:
        """Load data for given object type and environment"""
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """Validate loaded data"""
        pass

    @abstractmethod
    def get_available_files(self, object_type: str, environment: str) -> List[str]:
        """Get list of available files for object type and environment"""
        pass


class CacheInterface(ABC):
    """Cache interface - Dependency Inversion Principle"""

    @abstractmethod
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached data"""
        pass

    @abstractmethod
    def set(self, key: str, data: pd.DataFrame) -> None:
        """Cache data"""
        pass

    @abstractmethod
    def clear(self, pattern: Optional[str] = None) -> None:
        """Clear cache by pattern"""
        pass

    @abstractmethod
    def invalidate(self, object_type: str, environment: str) -> None:
        """Invalidate specific cache"""
        pass


class DataValidatorInterface(ABC):
    """Data validator interface - Dependency Inversion Principle"""

    @abstractmethod
    def validate_structure(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame structure"""
        pass

    @abstractmethod
    def validate_content(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame content"""
        pass

    @abstractmethod
    def get_validation_errors(self, df: pd.DataFrame) -> List[str]:
        """Get list of validation errors"""
        pass
