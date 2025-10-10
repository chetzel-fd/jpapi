#!/usr/bin/env python3
"""
Output Handler
Single Responsibility: Handles all output formatting and saving operations
"""

import csv
import json
import io
from typing import Any, Optional, Dict, List
from pathlib import Path
from datetime import datetime


class OutputHandler:
    """Handles output operations following SRP"""

    def __init__(self):
        self.supported_formats = ["table", "csv", "json", "yaml"]

    def format_output(self, data: Any, format_type: str = "table") -> str:
        """Format data for output"""
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {self.supported_formats}")

        if format_type == "table":
            return self._format_table(data)
        elif format_type == "csv":
            return self._format_csv(data)
        elif format_type == "json":
            return self._format_json(data)
        elif format_type == "yaml":
            return self._format_yaml(data)
        else:
            return str(data)

    def save_output(self, content: str, output_path: Optional[str] = None) -> str:
        """Save output to file"""
        if output_path is None:
            timestamp = self._get_timestamp()
            output_path = f"output_{timestamp}.txt"

        output_file = Path(output_path)
        
        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            return str(output_file.absolute())
        except Exception as e:
            raise IOError(f"Failed to save output to {output_path}: {e}")

    def _format_table(self, data: Any) -> str:
        """Format data as table"""
        if not data:
            return "No data available"

        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                return self._format_dict_table(data)
            else:
                return self._format_list_table(data)
        elif isinstance(data, dict):
            return self._format_dict_table([data])
        else:
            return str(data)

    def _format_dict_table(self, data: List[Dict]) -> str:
        """Format list of dictionaries as table"""
        if not data:
            return "No data available"

        headers = list(data[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = max(
                len(str(header)),
                max(len(str(row.get(header, ""))) for row in data[:10]  # Limit for performance
            )

        # Create table
        lines = []
        
        # Header
        header_line = " | ".join(f"{header:<{col_widths[header]}}" for header in headers)
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        # Data rows
        for row in data:
            row_line = " | ".join(
                f"{str(row.get(header, '')):<{col_widths[header]}}" 
                for header in headers
            )
            lines.append(row_line)
        
        return "\n".join(lines)

    def _format_list_table(self, data: List) -> str:
        """Format list as table"""
        if not data:
            return "No data available"

        lines = []
        for i, item in enumerate(data, 1):
            lines.append(f"{i:3d} | {str(item)}")
        
        return "\n".join(lines)

    def _format_csv(self, data: Any) -> str:
        """Format data as CSV"""
        if not data:
            return ""

        output = io.StringIO()
        
        if isinstance(data, list) and data and isinstance(data[0], dict):
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        elif isinstance(data, list):
            writer = csv.writer(output)
            writer.writerows([[item] for item in data])
        else:
            writer = csv.writer(output)
            writer.writerow([str(data)])
        
        return output.getvalue()

    def _format_json(self, data: Any) -> str:
        """Format data as JSON"""
        return json.dumps(data, indent=2, default=str)

    def _format_yaml(self, data: Any) -> str:
        """Format data as YAML"""
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False, indent=2)
        except ImportError:
            return "YAML formatting not available (pyyaml not installed)"

    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats"""
        return self.supported_formats.copy()

    def validate_format(self, format_type: str) -> bool:
        """Validate if format is supported"""
        return format_type in self.supported_formats

    def create_summary(self, data: Any, operation: str) -> str:
        """Create operation summary"""
        if isinstance(data, list):
            count = len(data)
            item_type = "items"
        elif isinstance(data, dict):
            count = len(data)
            item_type = "keys"
        else:
            count = 1
            item_type = "item"

        return f"✅ {operation} completed: {count} {item_type} processed"



