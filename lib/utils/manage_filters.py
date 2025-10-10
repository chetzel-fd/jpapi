#!/usr/bin/env python3
"""
Unified Filter Utilities for JPAPIDev
Provides consistent filtering across all commands using wildcards and regex
"""

from typing import List, Dict, Any, Union, Optional

from ..interfaces.pattern_compiler import IPatternCompiler
from enum import Enum


class FilterType(Enum):
    """Types of filtering supported"""

    WILDCARD = "wildcard"
    REGEX = "regex"
    EXACT = "exact"
    CONTAINS = "contains"


class FilterField(Enum):
    """Common fields that can be filtered"""

    NAME = "name"
    ID = "id"
    CATEGORY = "category"
    ENABLED = "enabled"
    LEVEL = "level"
    USER_REMOVABLE = "user_removable"
    DISTRIBUTION_METHOD = "distribution_method"
    FREQUENCY = "frequency"
    TRIGGER = "trigger"
    MODEL = "model"
    OS_VERSION = "os_version"
    SERIAL_NUMBER = "serial_number"
    TYPE = "type"


class FilterManager:
    """
    Unified filtering system for JPAPIDev commands
    Supports wildcards, regex, and exact matching
    """

    def __init__(
        self,
        filter_type: FilterType = FilterType.WILDCARD,
        pattern_compiler: Optional[IPatternCompiler] = None,
    ):
        """
        Initialize FilterManager

        Args:
            filter_type: Type of filtering to use
            pattern_compiler: Optional pattern compiler implementation
        """
        from .compile_patterns import (
            ExactPatternCompiler,
            ContainsPatternCompiler,
            WildcardPatternCompiler,
            RegexPatternCompiler,
        )

        self.filter_type = filter_type
        self._compiler = (
            pattern_compiler
            or {
                FilterType.EXACT: ExactPatternCompiler(),
                FilterType.CONTAINS: ContainsPatternCompiler(),
                FilterType.WILDCARD: WildcardPatternCompiler(),
                FilterType.REGEX: RegexPatternCompiler(),
            }[filter_type]
        )

    def matches(self, value: str, pattern: str, case_sensitive: bool = False) -> bool:
        """
        Check if a value matches a pattern

        Args:
            value: The value to check
            pattern: The pattern to match against
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            True if value matches pattern
        """
        if not value or not pattern:
            return False

        compiled = self._compiler.compile_pattern(pattern, case_sensitive)
        return self._compiler.match(compiled, value, case_sensitive)

    def filter_objects(
        self,
        objects: List[Dict[str, Any]],
        field: Union[str, FilterField],
        pattern: str,
        case_sensitive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Filter a list of objects by a field pattern

        Args:
            objects: List of objects to filter
            field: Field name to filter on
            pattern: Pattern to match
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            Filtered list of objects
        """
        if not objects or not pattern:
            return objects

        # Convert FilterField enum to string
        if isinstance(field, FilterField):
            field = field.value

        filtered_objects = []

        for obj in objects:
            # Get field value (support nested fields like 'general.name')
            field_value = self._get_nested_field(obj, field)

            if field_value is not None:
                # Convert to string for pattern matching
                field_str = str(field_value)

                if self.matches(field_str, pattern, case_sensitive):
                    filtered_objects.append(obj)

        return filtered_objects

    def _get_nested_field(self, obj: Dict[str, Any], field: str) -> Any:
        """
        Get a field value from an object, supporting nested fields

        Args:
            obj: The object to get field from
            field: Field name (supports dot notation like 'general.name')

        Returns:
            Field value or None if not found
        """
        if "." not in field:
            return obj.get(field)

        # Handle nested fields
        parts = field.split(".")
        current = obj

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def filter_by_multiple_criteria(
        self,
        objects: List[Dict[str, Any]],
        criteria: Dict[str, str],
        case_sensitive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Filter objects by multiple criteria (AND operation)

        Args:
            objects: List of objects to filter
            criteria: Dictionary of field -> pattern mappings
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            Filtered list of objects
        """
        if not objects or not criteria:
            return objects

        filtered_objects = objects

        for field, pattern in criteria.items():
            filtered_objects = self.filter_objects(
                filtered_objects, field, pattern, case_sensitive
            )

        return filtered_objects

    def get_filter_summary(self, original_count: int, filtered_count: int) -> str:
        """
        Get a summary of filtering results

        Args:
            original_count: Original number of objects
            filtered_count: Number of objects after filtering

        Returns:
            Summary string
        """
        if filtered_count == original_count:
            return f"Showing all {original_count} objects"
        else:
            return f"Showing {filtered_count} of {original_count} objects (filtered)"


# Convenience functions for common filtering operations
def create_filter(filter_type: str = "wildcard") -> FilterManager:
    """
    Create a filter instance

    Args:
        filter_type: Type of filtering ('wildcard', 'regex', 'exact', 'contains')

    Returns:
        UnifiedFilter instance
    """
    try:
        filter_enum = FilterType(filter_type.lower())
        return FilterManager(filter_enum)
    except ValueError:
        # Default to wildcard if invalid type
        return FilterManager(FilterType.WILDCARD)


def filter_policies(
    policies: List[Dict[str, Any]],
    name_pattern: Optional[str] = None,
    category_pattern: Optional[str] = None,
    enabled: Optional[bool] = None,
    filter_type: str = "wildcard",
) -> List[Dict[str, Any]]:
    """
    Filter policies by common criteria

    Args:
        policies: List of policy objects
        name_pattern: Pattern to match policy names
        category_pattern: Pattern to match categories
        enabled: Filter by enabled status
        filter_type: Type of filtering

    Returns:
        Filtered list of policies
    """
    filter_obj = create_filter(filter_type)
    filtered = policies

    if name_pattern:
        filtered = filter_obj.filter_objects(filtered, FilterField.NAME, name_pattern)

    if category_pattern:
        filtered = filter_obj.filter_objects(
            filtered, FilterField.CATEGORY, category_pattern
        )

    if enabled is not None:
        filtered = [p for p in filtered if p.get("enabled") == enabled]

    return filtered


def filter_profiles(
    profiles: List[Dict[str, Any]],
    name_pattern: Optional[str] = None,
    level_pattern: Optional[str] = None,
    user_removable: Optional[bool] = None,
    filter_type: str = "wildcard",
) -> List[Dict[str, Any]]:
    """
    Filter configuration profiles by common criteria

    Args:
        profiles: List of profile objects
        name_pattern: Pattern to match profile names
        level_pattern: Pattern to match levels
        user_removable: Filter by user removable status
        filter_type: Type of filtering

    Returns:
        Filtered list of profiles
    """
    filter_obj = create_filter(filter_type)
    filtered = profiles

    if name_pattern:
        filtered = filter_obj.filter_objects(filtered, FilterField.NAME, name_pattern)

    if level_pattern:
        filtered = filter_obj.filter_objects(filtered, FilterField.LEVEL, level_pattern)

    if user_removable is not None:
        filtered = [p for p in filtered if p.get("user_removable") == user_removable]

    return filtered


def filter_packages(
    packages: List[Dict[str, Any]],
    name_pattern: Optional[str] = None,
    category_pattern: Optional[str] = None,
    filter_type: str = "wildcard",
) -> List[Dict[str, Any]]:
    """
    Filter packages by common criteria

    Args:
        packages: List of package objects
        name_pattern: Pattern to match package names
        category_pattern: Pattern to match categories
        filter_type: Type of filtering

    Returns:
        Filtered list of packages
    """
    filter_obj = create_filter(filter_type)
    filtered = packages

    if name_pattern:
        filtered = filter_obj.filter_objects(filtered, FilterField.NAME, name_pattern)

    if category_pattern:
        filtered = filter_obj.filter_objects(
            filtered, FilterField.CATEGORY, category_pattern
        )

    return filtered


def filter_computers(
    computers: List[Dict[str, Any]],
    name_pattern: Optional[str] = None,
    model_pattern: Optional[str] = None,
    os_version_pattern: Optional[str] = None,
    filter_type: str = "wildcard",
) -> List[Dict[str, Any]]:
    """
    Filter computers by common criteria

    Args:
        computers: List of computer objects
        name_pattern: Pattern to match computer names
        model_pattern: Pattern to match models
        os_version_pattern: Pattern to match OS versions
        filter_type: Type of filtering

    Returns:
        Filtered list of computers
    """
    filter_obj = create_filter(filter_type)
    filtered = computers

    if name_pattern:
        filtered = filter_obj.filter_objects(filtered, FilterField.NAME, name_pattern)

    if model_pattern:
        filtered = filter_obj.filter_objects(filtered, FilterField.MODEL, model_pattern)

    if os_version_pattern:
        filtered = filter_obj.filter_objects(
            filtered, FilterField.OS_VERSION, os_version_pattern
        )

    return filtered


# Example usage and testing
if __name__ == "__main__":
    # Test the filter system
    filter_obj = create_filter("wildcard")

    # Test wildcard matching
    print("Testing wildcard matching:")
    print(f"  'test*' matches 'test123': {filter_obj.matches('test123', 'test*')}")
    print(f"  'test*' matches 'testing': {filter_obj.matches('testing', 'test*')}")
    print(f"  'test*' matches 'other': {filter_obj.matches('other', 'test*')}")

    # Test regex matching
    regex_filter = create_filter("regex")
    print("\nTesting regex matching:")
    pattern = r"^test\d+$"
    print(
        f"  '{pattern}' matches 'test123': {regex_filter.matches('test123', pattern)}"
    )
    print(
        f"  '{pattern}' matches 'testabc': {regex_filter.matches('testabc', pattern)}"
    )

    # Test object filtering
    test_objects = [
        {"name": "Test Policy 1", "enabled": True, "category": "Security"},
        {"name": "Another Policy", "enabled": False, "category": "General"},
        {"name": "Test Policy 2", "enabled": True, "category": "Security"},
    ]

    print("\nTesting object filtering:")
    filtered = filter_obj.filter_objects(test_objects, "name", "Test*")
    print(f"  Filtered {len(test_objects)} objects to {len(filtered)} objects")
    for obj in filtered:
        print(f"    - {obj['name']}")
