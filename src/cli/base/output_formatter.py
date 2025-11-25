#!/usr/bin/env python3
"""
Output Formatter for CLI Commands
Handles formatting of data output to various formats (JSON, CSV, table)
Extracted from BaseCommand for SRP compliance
"""

from typing import Any, Optional
from pathlib import Path
import json
import csv
import io


class OutputFormatter:
    """Handles output formatting for CLI commands"""

    def format_output(self, data: Any, format_type: str = "table") -> str:
        """
        Format output data

        Args:
            data: Data to format
            format_type: Output format (json, csv, table)

        Returns:
            Formatted string output
        """
        if format_type == "json":
            return self.format_json(data)
        elif format_type == "csv":
            return self.format_csv(data)
        else:
            return self.format_table(data)

    def format_json(self, data: Any) -> str:
        """Format data as JSON"""
        return json.dumps(data, indent=2)

    def format_csv(self, data: Any) -> str:
        """Format data as CSV"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        else:
            return str(data)

    def format_table(self, data: Any) -> str:
        """Format data as table"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Simple table formatting
            headers = list(data[0].keys())
            rows = []

            # Header
            header_row = " | ".join(f"{h:15}" for h in headers)
            separator = "-" * len(header_row)
            rows.append(header_row)
            rows.append(separator)

            # Data rows
            for item in data:
                row = " | ".join(f"{str(item.get(h, '')):15}" for h in headers)
                rows.append(row)

            return "\n".join(rows)
        else:
            return str(data)

    def save_output(
        self, content: str, output_path: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Save output to file or print to stdout

        Args:
            content: Content to save
            output_path: Optional file path to save to

        Returns:
            Tuple of (success, message)
        """
        if output_path:
            try:
                # Ensure directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(content)
                return True, f"✅ Output saved to: {output_path}"
            except Exception as e:
                return False, f"❌ Failed to save output: {e}\n{content}"
        else:
            # Print to stdout
            print(content)
            return True, ""
