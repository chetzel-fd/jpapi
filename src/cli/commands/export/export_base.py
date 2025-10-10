#!/usr/bin/env python3
"""
Base Export Functions
Common functions for exporting JAMF data
"""

from typing import Dict, Any, List, Optional
from argparse import Namespace
import json
import csv
import io
import time
from pathlib import Path
from lib.utils import create_filter
from lib.exports.manage_exports import (
    generate_export_filename,
    get_export_directory,
)
from core.logging.command_mixin import log_operation, LoggingCommandMixin


class ExportBase(LoggingCommandMixin):
    """Base class for exporting JAMF data"""

    def __init__(self, auth, data_type: str):
        self.auth = auth
        self.data_type = data_type
        # Initialize logging
        LoggingCommandMixin.__init__(self)

    @log_operation("Export Data")
    def export(self, args: Namespace) -> int:
        """Export data to file"""
        try:
            # Get data from JAMF
            data = self._fetch_data(args)

            if not data:
                self.log_error(f"No {self.data_type} found")
                return 1

            self.log_success(f"Found {len(data)} {self.data_type} to export")

            # Format data for saving
            export_data = self._format_data(data, args)

            # Save to file
            self.log_info("Saving data")
            self._save_output(export_data, args)

            return 0

        except Exception as e:
            return self._handle_error(e)

    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Get data from JAMF - override in subclasses"""
        raise NotImplementedError("Subclasses must implement _fetch_data")

    def _apply_filter(
        self, data: List[Dict[str, Any]], args: Namespace, filter_obj
    ) -> List[Dict[str, Any]]:
        """Filter data - can override in subclasses"""
        return filter_obj.filter_objects(data, "name", args.filter)

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format data for saving - override in subclasses"""
        raise NotImplementedError("Subclasses must implement _format_data")

    def _get_detailed_info(
        self, item_id: str, endpoint: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed info for an item"""
        try:
            response = self.auth.api_request("GET", f"{endpoint}/id/{item_id}")
            # Get main object from response
            for key in response.keys():
                if key != "id" and isinstance(response[key], dict):
                    return response[key]
            return None
        except Exception as e:
            print(f"   ⚠️  Could not get details for {self.data_type} {item_id}: {e}")
            return None

    def _save_output(self, data: List[Dict[str, Any]], args: Namespace) -> None:
        """Save data to file with optional analysis"""
        if not data:
            return

        # Get environment from args or default to dev
        environment = getattr(args, "env", "dev")

        if args.format == "csv":
            output = self._generate_csv(data)
            if args.output:
                filename = args.output
            else:
                # Use the export management system for proper naming
                filename = generate_export_filename(
                    object_type=self.data_type.replace(" ", "-"),
                    format="csv",
                    environment=environment,
                )
                # Get the full path
                export_dir = get_export_directory(environment)
                filename = str(export_dir / filename)
        elif args.format == "json":
            output = json.dumps(data, indent=2)
            if args.output:
                filename = args.output
            else:
                # Use the export management system for proper naming
                filename = generate_export_filename(
                    object_type=self.data_type.replace(" ", "-"),
                    format="json",
                    environment=environment,
                )
                # Get the full path
                export_dir = get_export_directory(environment)
                filename = str(export_dir / filename)
        else:
            output = self._format_table_output(data, args.format)
            filename = args.output

        # Save or print output
        if filename:
            self._write_file(output, filename)

            # Generate analysis if requested
            if getattr(args, "analysis", False):
                self._generate_analysis_report(data, filename)
        else:
            print(output)

    def _generate_analysis_report(
        self, data: List[Dict[str, Any]], filename: str
    ) -> None:
        """Generate analysis report for the export"""
        try:
            from lib.utils.export_analysis import ExportAnalyzer

            analyzer = ExportAnalyzer()
            analysis = analyzer.analyze_export_data(data, self.data_type)

            # Save analysis report
            analysis_filename = str(Path(filename).with_suffix(".analysis.json"))
            with open(analysis_filename, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2)

            print(f"📊 Analysis report saved: {analysis_filename}")

            # Print summary
            summary = analysis.get("summary", {})
            print(f"\n📈 Export Analysis Summary:")
            print(f"   Total items: {summary.get('total_items', 0)}")
            print(
                f"   Enabled: {summary.get('enabled_items', 0)} ({summary.get('enabled_percentage', 0)}%)"
            )
            print(f"   Disabled: {summary.get('disabled_items', 0)}")

            # Print insights
            insights = analysis.get("insights", [])
            if insights:
                print(f"\n💡 Key Insights:")
                for insight in insights[:5]:  # Show top 5 insights
                    print(f"   {insight}")

            # Print health score
            health = analysis.get("health_check", {})
            score = health.get("overall_score", 0)
            print(f"\n🏥 Health Score: {score}/100")

        except Exception as e:
            print(f"⚠️ Could not generate analysis report: {e}")

    def _generate_csv(self, data: List[Dict[str, Any]]) -> str:
        """Generate CSV output with enhanced columns"""
        if not data:
            return ""

        # Add analysis columns to each row
        enhanced_data = []
        for row in data:
            enhanced_row = self._add_analysis_columns(row)
            enhanced_data.append(enhanced_row)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=enhanced_data[0].keys())
        writer.writeheader()
        writer.writerows(enhanced_data)
        return output.getvalue()

    def _add_analysis_columns(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Add analysis columns to a data row"""
        enhanced_row = row.copy()

        # Add description column if not present
        if "Description" not in enhanced_row:
            enhanced_row["Description"] = self._generate_description(row)

        # Add analysis columns
        enhanced_row.update(
            {
                "Analysis_Status": self._analyze_status(row),
                "Analysis_Priority": self._analyze_priority(row),
                "Analysis_Complexity": self._analyze_complexity(row),
                "Analysis_Last_Modified": self._analyze_last_modified(row),
                "Analysis_Category": self._analyze_category(row),
                "Analysis_Scope": self._analyze_scope(row),
                "Analysis_Recommendations": self._generate_recommendations(row),
            }
        )

        return enhanced_row

    def _generate_description(self, row: Dict[str, Any]) -> str:
        """Generate a description for the item"""
        name = row.get("Name", row.get("name", ""))
        category = row.get("Category", row.get("category", ""))
        status = row.get("Status", row.get("enabled", ""))

        if self.data_type == "policies":
            trigger = row.get("Trigger", "")
            frequency = row.get("Frequency", "")
            return f"Policy: {name} | Category: {category} | Status: {status} | Trigger: {trigger} | Frequency: {frequency}"
        elif self.data_type == "scripts":
            info = row.get("info", "")
            return f"Script: {name} | Category: {category} | Info: {info[:50]}..."
        elif self.data_type == "profiles":
            level = row.get("Level", "")
            return f"Profile: {name} | Category: {category} | Level: {level}"
        else:
            return f"{self.data_type.title()}: {name} | Category: {category}"

    def _analyze_status(self, row: Dict[str, Any]) -> str:
        """Analyze the status of the item"""
        enabled = row.get("Enabled", row.get("enabled", False))
        status = row.get("Status", "")

        if enabled or status == "Enabled":
            return "✅ Active"
        elif status == "Disabled":
            return "❌ Inactive"
        else:
            return "⚠️ Unknown"

    def _analyze_priority(self, row: Dict[str, Any]) -> str:
        """Analyze the priority/importance of the item"""
        name = row.get("Name", row.get("name", "")).lower()
        category = row.get("Category", row.get("category", "")).lower()

        # High priority indicators
        if any(
            keyword in name
            for keyword in ["security", "compliance", "critical", "essential"]
        ):
            return "🔴 High"
        elif any(
            keyword in category for keyword in ["security", "compliance", "critical"]
        ):
            return "🔴 High"
        elif any(keyword in name for keyword in ["update", "patch", "maintenance"]):
            return "🟡 Medium"
        else:
            return "🟢 Low"

    def _analyze_complexity(self, row: Dict[str, Any]) -> str:
        """Analyze the complexity of the item"""
        if self.data_type == "policies":
            scripts = row.get("Script_Name", "")
            parameters = row.get("Script_Parameters", "")
            if scripts and parameters:
                return "🔴 Complex"
            elif scripts:
                return "🟡 Medium"
            else:
                return "🟢 Simple"
        elif self.data_type == "profiles":
            scope_all = row.get("Scope All Computers", "")
            if scope_all:
                return "🟡 Medium"
            else:
                return "🟢 Simple"
        else:
            return "🟢 Simple"

    def _analyze_last_modified(self, row: Dict[str, Any]) -> str:
        """Analyze when the item was last modified"""
        modified = row.get("Modified Date", row.get("modified", ""))
        if not modified:
            return "❓ Unknown"

        # This would need date parsing in a real implementation
        return f"📅 {modified}"

    def _analyze_category(self, row: Dict[str, Any]) -> str:
        """Analyze the category of the item"""
        category = row.get("Category", row.get("category", ""))
        if not category:
            return "📂 Uncategorized"

        # Categorize by type
        if "security" in category.lower():
            return "🔒 Security"
        elif "compliance" in category.lower():
            return "📋 Compliance"
        elif "maintenance" in category.lower():
            return "🔧 Maintenance"
        else:
            return f"📂 {category}"

    def _analyze_scope(self, row: Dict[str, Any]) -> str:
        """Analyze the scope of the item"""
        if self.data_type == "policies":
            trigger = row.get("Trigger", "")
            if trigger == "EVENT":
                return "🎯 Event-driven"
            elif trigger == "CHECKIN":
                return "⏰ Scheduled"
            else:
                return "🔧 Manual"
        elif self.data_type == "profiles":
            scope_all = row.get("Scope All Computers", "")
            if scope_all:
                return "🌐 All Devices"
            else:
                return "🎯 Targeted"
        else:
            return "📊 Standard"

    def _generate_recommendations(self, row: Dict[str, Any]) -> str:
        """Generate recommendations for the item"""
        recommendations = []

        # Check for common issues
        if self.data_type == "policies":
            if not row.get("Script_Name"):
                recommendations.append("Add script")
            if row.get("Status") == "Disabled":
                recommendations.append("Review if needed")

        elif self.data_type == "profiles":
            if not row.get("Description"):
                recommendations.append("Add description")
            if row.get("Level") == "System":
                recommendations.append("Review scope")

        if not recommendations:
            recommendations.append("No issues found")

        return " | ".join(recommendations)

    def _format_table_output(self, data: List[Dict[str, Any]], format_type: str) -> str:
        """Format as table"""
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
        """Write content to file"""
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"📁 Saved: {file_path}")

    def _handle_error(self, error: Exception) -> int:
        """Handle errors consistently"""
        print(f"❌ Error exporting {self.data_type}: {error}")
        return 1

    def _create_safe_filename(self, name: str, item_id: str, extension: str) -> str:
        """Create safe filename"""
        safe_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_name = safe_name.replace(" ", "_")
        return f"{item_id}_{safe_name}.{extension}"

    def _download_file(self, content: str, filename: str, directory: str = None) -> str:
        """Save a file"""
        if directory is None:
            directory = f"data/csv-exports/{self.data_type}"

        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Make executable if it's a script
        if filename.endswith(".sh"):
            file_path.chmod(0o755)

        print(f"   📁 Saved: {file_path}")
        return str(file_path)
