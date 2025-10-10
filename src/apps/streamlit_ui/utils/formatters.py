"""
Data Formatters - Data Formatting Utilities
Utility functions for formatting data in the JPAPI Streamlit UI
"""

import pandas as pd
from typing import Any, Dict, List, Optional
from datetime import datetime
import re


class DataFormatter:
    """Data formatting utilities"""

    @staticmethod
    def format_status(status: str) -> str:
        """Format status with appropriate styling"""
        status_map = {
            "Active": "🟢 Active",
            "Deleted": "🔴 Deleted",
            "Inactive": "🟡 Inactive",
        }
        return status_map.get(status, f"❓ {status}")

    @staticmethod
    def format_smart(smart: Any) -> str:
        """Format smart group indicator"""
        if smart in [True, 1, "True", "true", "1"]:
            return "🧠 Smart"
        else:
            return "📋 Static"

    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date string for display"""
        try:
            if isinstance(date_str, str):
                # Try to parse common date formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
            return str(date_str)
        except:
            return str(date_str)

    @staticmethod
    def format_name(name: str, max_length: int = 50) -> str:
        """Format object name with length limit"""
        if len(name) > max_length:
            return name[: max_length - 3] + "..."
        return name

    @staticmethod
    def format_count(count: int) -> str:
        """Format count with appropriate styling"""
        if count == 0:
            return "0"
        elif count < 1000:
            return str(count)
        elif count < 1000000:
            return f"{count/1000:.1f}K"
        else:
            return f"{count/1000000:.1f}M"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    @staticmethod
    def format_percentage(value: float, total: float) -> str:
        """Format percentage"""
        if total == 0:
            return "0%"
        percentage = (value / total) * 100
        return f"{percentage:.1f}%"

    @staticmethod
    def format_object_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Format object summary statistics"""
        if df.empty:
            return {"total": 0, "active": 0, "deleted": 0, "smart": 0, "static": 0}

        total = len(df)
        active = (
            len(df[df.get("Status", "") == "Active"]) if "Status" in df.columns else 0
        )
        deleted = (
            len(df[df.get("Status", "") == "Deleted"]) if "Status" in df.columns else 0
        )
        smart = len(df[df.get("Smart", False) == True]) if "Smart" in df.columns else 0
        static = total - smart

        return {
            "total": total,
            "active": active,
            "deleted": deleted,
            "smart": smart,
            "static": static,
        }

    @staticmethod
    def format_search_highlight(text: str, search_term: str) -> str:
        """Format text with search term highlighted"""
        if not search_term:
            return text

        # Escape special regex characters
        escaped_term = re.escape(search_term)
        # Case-insensitive replacement
        pattern = re.compile(escaped_term, re.IGNORECASE)
        return pattern.sub(f"**{search_term}**", text)

    @staticmethod
    def format_error_message(error: Exception) -> str:
        """Format error message for display"""
        error_type = type(error).__name__
        error_msg = str(error)

        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."

        return f"**{error_type}**: {error_msg}"

    @staticmethod
    def format_validation_errors(errors: List[str]) -> str:
        """Format validation errors for display"""
        if not errors:
            return "✅ No validation errors"

        formatted_errors = []
        for i, error in enumerate(errors, 1):
            formatted_errors.append(f"{i}. {error}")

        return "❌ **Validation Errors:**\n" + "\n".join(formatted_errors)
