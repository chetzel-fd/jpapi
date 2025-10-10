#!/usr/bin/env python3
"""
Base Export Handler for jpapi CLI
Contains common functionality for all export operations
"""

from typing import Dict, Any, List, Optional
from argparse import Namespace
import json
import csv
import io
import time
from pathlib import Path
from src.lib.filter_utils import create_filter
from core.logging.command_mixin import log_operation, LoggingCommandMixin


class BaseExportHandler(LoggingCommandMixin):
    """Base class for all export handlers"""

    def __init__(self, auth, object_type: str):
        self.auth = auth
        self.object_type = object_type
        # Initialize logging mixin
        LoggingCommandMixin.__init__(self)

    @log_operation("Export Operation")
    def export(self, args: Namespace) -> int:
        """Main export method - template for all export operations"""
        try:
            # Fetch data from API
            data = self._fetch_data(args)

            if not data:
                self.log_error(f"No {self.object_type} found")
                return 1

            self.log_success(f"Found {len(data)} {self.object_type} to export")

            # Format data for export (filtering handled by individual handlers)
            export_data = self._format_data(data, args)

            # Save output
            self.log_info("Saving export data")
            self._save_output(export_data, args)

            return 0

        except Exception as e:
            return self._handle_error(e)

    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch data from JAMF API - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement _fetch_data")

    def _apply_filter(
        self, data: List[Dict[str, Any]], args: Namespace, filter_obj
    ) -> List[Dict[str, Any]]:
        """Apply filtering to data - can be overridden by subclasses for custom filtering"""
        # Default filtering by name field
        return filter_obj.filter_objects(data, "name", args.filter)

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format data for export - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement _format_data")

    def _get_detailed_info(
        self, item_id: str, endpoint: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific item"""
        try:
            response = self.auth.api_request("GET", f"{endpoint}/id/{item_id}")
            # Extract the main object from response
            for key in response.keys():
                if key != "id" and isinstance(response[key], dict):
                    return response[key]
            return None
        except Exception as e:
            print(f"   ⚠️  Could not get details for {self.object_type} {item_id}: {e}")
            return None

    def _save_output(self, data: List[Dict[str, Any]], args: Namespace) -> None:
        """Save export data to file or print to console"""
        if not data:
            return

        # Generate output based on format
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        if args.format == "csv":
            output = self._generate_csv(data)
            filename = (
                args.output
                or f"data/csv-exports/{self.object_type}-export-{timestamp}.csv"
            )
        elif args.format == "json":
            output = json.dumps(data, indent=2)
            filename = (
                args.output
                or f"data/csv-exports/{self.object_type}-export-{timestamp}.json"
            )
        else:
            output = self._format_table_output(data, args.format)
            filename = args.output

        # Save or print output
        if filename:
            self._write_file(output, filename)
        else:
            print(output)

    def _generate_csv(self, data: List[Dict[str, Any]]) -> str:
        """Generate CSV output from data"""
        if not data:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def _format_table_output(self, data: List[Dict[str, Any]], format_type: str) -> str:
        """Format data as table output"""
        # This would integrate with the existing format_output method
        # For now, return a simple representation
        if not data:
            return ""

        # Get column headers
        headers = list(data[0].keys())

        # Create table
        lines = []
        lines.append(" | ".join(headers))
        lines.append("-" * (len(" | ".join(headers))))

        for row in data:
            values = [str(row.get(header, "")) for header in headers]
            lines.append(" | ".join(values))

        return "\n".join(lines)

    def _write_file(self, content: str, filename: str) -> None:
        """Write content to file, creating directories as needed"""
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"📁 Saved: {file_path}")

    def _handle_error(self, error: Exception) -> int:
        """Handle errors consistently"""
        print(f"❌ Error exporting {self.object_type}: {error}")
        return 1

    def _create_safe_filename(self, name: str, item_id: str, extension: str) -> str:
        """Create a safe filename from item name and ID"""
        safe_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_name = safe_name.replace(" ", "_")
        return f"{item_id}_{safe_name}.{extension}"

    def _download_file(self, content: str, filename: str, directory: str = None) -> str:
        """Download a file with content to the specified directory"""
        if directory is None:
            directory = f"data/csv-exports/{self.object_type}"

        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Make executable if it's a script
        if filename.endswith(".sh"):
            file_path.chmod(0o755)

        print(f"   📁 Downloaded: {file_path}")
        return str(file_path)
