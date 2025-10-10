#!/usr/bin/env python3
"""
Composite Connection Analyzer
Combines multiple connection analyzers into a single interface
"""

from typing import Dict, List, Any, Optional
from interfaces import IConnectionAnalyzer


class CompositeAnalyzer(IConnectionAnalyzer):
    """Combines multiple connection analyzers"""

    def __init__(self, analyzers: List[IConnectionAnalyzer]):
        """
        Initialize with list of analyzers

        Args:
            analyzers: List of analyzer instances to combine
        """
        self._analyzers = analyzers

    def analyze_policy_connections(self, policy_id: str) -> Dict[str, List[str]]:
        """Combine policy connection analysis from all analyzers"""
        results = {}
        for analyzer in self._analyzers:
            analyzer_results = analyzer.analyze_policy_connections(policy_id)
            for connection_type, ids in analyzer_results.items():
                if connection_type not in results:
                    results[connection_type] = []
                results[connection_type].extend(ids)
        return self._deduplicate_results(results)

    def analyze_script_connections(self, script_id: str) -> Dict[str, List[str]]:
        """Combine script connection analysis from all analyzers"""
        results = {}
        for analyzer in self._analyzers:
            analyzer_results = analyzer.analyze_script_connections(script_id)
            for connection_type, ids in analyzer_results.items():
                if connection_type not in results:
                    results[connection_type] = []
                results[connection_type].extend(ids)
        return self._deduplicate_results(results)

    def analyze_profile_connections(self, profile_id: str) -> Dict[str, List[str]]:
        """Combine profile connection analysis from all analyzers"""
        results = {}
        for analyzer in self._analyzers:
            analyzer_results = analyzer.analyze_profile_connections(profile_id)
            for connection_type, ids in analyzer_results.items():
                if connection_type not in results:
                    results[connection_type] = []
                results[connection_type].extend(ids)
        return self._deduplicate_results(results)

    def analyze_group_connections(self, group_id: str) -> Dict[str, List[str]]:
        """Combine group connection analysis from all analyzers"""
        results = {}
        for analyzer in self._analyzers:
            analyzer_results = analyzer.analyze_group_connections(group_id)
            for connection_type, ids in analyzer_results.items():
                if connection_type not in results:
                    results[connection_type] = []
                results[connection_type].extend(ids)
        return self._deduplicate_results(results)

    def analyze_device_connections(self, device_id: str) -> Dict[str, List[str]]:
        """Combine device connection analysis from all analyzers"""
        results = {}
        for analyzer in self._analyzers:
            analyzer_results = analyzer.analyze_device_connections(device_id)
            for connection_type, ids in analyzer_results.items():
                if connection_type not in results:
                    results[connection_type] = []
                results[connection_type].extend(ids)
        return self._deduplicate_results(results)

    def find_orphaned_objects(self, object_type: str) -> List[str]:
        """Find objects that are orphaned according to all analyzers"""
        orphaned = None
        for analyzer in self._analyzers:
            analyzer_orphaned = set(analyzer.find_orphaned_objects(object_type))
            if orphaned is None:
                orphaned = analyzer_orphaned
            else:
                # Only keep objects that are orphaned according to all analyzers
                orphaned &= analyzer_orphaned
        return list(orphaned) if orphaned is not None else []

    def find_circular_dependencies(self) -> List[List[str]]:
        """Combine circular dependencies from all analyzers"""
        circles = []
        for analyzer in self._analyzers:
            circles.extend(analyzer.find_circular_dependencies())
        return self._deduplicate_circles(circles)

    def get_dependency_graph(self, object_id: str, object_type: str) -> Dict[str, Any]:
        """Combine dependency graphs from all analyzers"""
        combined = None
        for analyzer in self._analyzers:
            graph = analyzer.get_dependency_graph(object_id, object_type)
            if combined is None:
                combined = graph
            else:
                combined = self._merge_graphs(combined, graph)
        return combined if combined is not None else {}

    def _deduplicate_results(
        self, results: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Remove duplicate IDs from results"""
        return {
            connection_type: list(set(ids)) for connection_type, ids in results.items()
        }

    def _deduplicate_circles(self, circles: List[List[str]]) -> List[List[str]]:
        """Remove duplicate circular dependencies"""
        unique_circles = []
        for circle in circles:
            # Normalize circle by rotating to start with smallest ID
            min_index = circle.index(min(circle))
            normalized = circle[min_index:] + circle[:min_index]
            if normalized not in unique_circles:
                unique_circles.append(normalized)
        return unique_circles

    def _merge_graphs(
        self, graph1: Dict[str, Any], graph2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two dependency graphs"""
        if not graph1:
            return graph2
        if not graph2:
            return graph1

        merged = graph1.copy()
        if "dependencies" not in merged:
            merged["dependencies"] = []

        # Add new dependencies from graph2
        if "dependencies" in graph2:
            for dep in graph2["dependencies"]:
                if dep not in merged["dependencies"]:
                    merged["dependencies"].append(dep)

        return merged


def analyze_composite(data):
    """Analyze composite connections in data"""
    return {"composite_connections": [], "merged_relationships": []}
