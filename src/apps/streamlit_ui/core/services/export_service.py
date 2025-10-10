"""
Export Service - Single Responsibility Principle
Handles data export functionality
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List
from io import BytesIO
import json


class ExportService:
    """Data export service"""

    def __init__(self):
        self.supported_formats = ["csv", "json", "xlsx"]
        self.default_format = "csv"

    def export_data(
        self, data: pd.DataFrame, format: str = None, filename: str = None
    ) -> Dict[str, Any]:
        """Export data in specified format"""
        if data.empty:
            return {
                "success": False,
                "message": "No data to export",
                "error": "Empty DataFrame",
            }

        format = format or self.default_format
        if format not in self.supported_formats:
            return {
                "success": False,
                "message": f"Unsupported format: {format}",
                "error": f"Format must be one of: {self.supported_formats}",
            }

        try:
            if format == "csv":
                return self._export_csv(data, filename)
            elif format == "json":
                return self._export_json(data, filename)
            elif format == "xlsx":
                return self._export_xlsx(data, filename)
        except Exception as e:
            return {
                "success": False,
                "message": f"Export failed: {str(e)}",
                "error": str(e),
            }

    def _export_csv(self, data: pd.DataFrame, filename: str = None) -> Dict[str, Any]:
        """Export data as CSV"""
        csv_data = data.to_csv(index=False)
        filename = filename or "export.csv"

        return {
            "success": True,
            "data": csv_data,
            "filename": filename,
            "mime_type": "text/csv",
            "format": "csv",
        }

    def _export_json(self, data: pd.DataFrame, filename: str = None) -> Dict[str, Any]:
        """Export data as JSON"""
        json_data = data.to_json(orient="records", indent=2)
        filename = filename or "export.json"

        return {
            "success": True,
            "data": json_data,
            "filename": filename,
            "mime_type": "application/json",
            "format": "json",
        }

    def _export_xlsx(self, data: pd.DataFrame, filename: str = None) -> Dict[str, Any]:
        """Export data as Excel"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            data.to_excel(writer, index=False, sheet_name="Data")

        excel_data = output.getvalue()
        filename = filename or "export.xlsx"

        return {
            "success": True,
            "data": excel_data,
            "filename": filename,
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "format": "xlsx",
        }

    def get_export_info(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get export information for data"""
        return {
            "row_count": len(data),
            "column_count": len(data.columns),
            "columns": list(data.columns),
            "memory_usage": data.memory_usage(deep=True).sum(),
            "supported_formats": self.supported_formats,
        }

    def validate_export_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate data for export"""
        if data.empty:
            return {"valid": False, "message": "No data to export"}

        if len(data) > 10000:  # Max export rows
            return {
                "valid": False,
                "message": f"Too many rows ({len(data)}). Maximum is 10,000.",
            }

        return {"valid": True, "message": f"Ready to export {len(data)} rows"}

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return self.supported_formats

    def get_format_info(self, format: str) -> Dict[str, Any]:
        """Get information about export format"""
        format_info = {
            "csv": {
                "name": "CSV",
                "description": "Comma-separated values",
                "mime_type": "text/csv",
                "extension": ".csv",
            },
            "json": {
                "name": "JSON",
                "description": "JavaScript Object Notation",
                "mime_type": "application/json",
                "extension": ".json",
            },
            "xlsx": {
                "name": "Excel",
                "description": "Microsoft Excel format",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "extension": ".xlsx",
            },
        }
        return format_info.get(format, {})
