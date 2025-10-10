#!/usr/bin/env python3
"""
Connection Factory
Creates and manages connection analyzer instances
"""

from typing import Dict, Optional, List

from ..connections import (
    analyze_connections,
    analyze_composite,
    analyze_reverse_relationships,
    connect_jamf,
    connect_mobile,
    find_connections,
)


class ConnectionFactory:
    """Factory for creating connection analyzers"""

    _analyzers: Dict[str, callable] = {
        "default": analyze_connections,
        "composite": analyze_composite,
        "reverse": analyze_reverse_relationships,
        "jamf": connect_jamf,
        "mobile": connect_mobile,
        "finder": find_connections,
    }

    @classmethod
    def register_analyzer(cls, name: str, analyzer_func: callable) -> None:
        """
        Register a new analyzer function

        Args:
            name: Name to register the analyzer under
            analyzer_func: Analyzer function to register
        """
        cls._analyzers[name] = analyzer_func

    @classmethod
    def create_analyzer(cls, analyzer_type: str = "default") -> Optional[callable]:
        """
        Get an analyzer function

        Args:
            analyzer_type: Type of analyzer to get

        Returns:
            Analyzer function or None if type not found
        """
        return cls._analyzers.get(analyzer_type)

    @classmethod
    def create_composite_analyzer(cls, analyzer_types: List[str]) -> Optional[callable]:
        """
        Create a composite analyzer with multiple analyzer types

        Args:
            analyzer_types: List of analyzer types to combine

        Returns:
            Composite analyzer function or None if any type not found
        """

        def composite_analyzer(data):
            results = []
            for analyzer_type in analyzer_types:
                func = cls.create_analyzer(analyzer_type)
                if func:
                    results.append(func(data))
            return {"composite_results": results}

        return composite_analyzer

    @classmethod
    def get_available_analyzers(cls) -> Dict[str, callable]:
        """
        Get all registered analyzer functions

        Returns:
            Dict mapping analyzer names to their functions
        """
        return cls._analyzers.copy()
