#!/usr/bin/env python3
"""
Export utilities for JPAPI
Handles filename generation with instance prefixes
"""

from datetime import datetime
from pathlib import Path
from typing import Optional


def get_instance_prefix(environment: str = "dev") -> str:
    """
    Get the instance prefix for the given environment

    Args:
        environment: The environment name (dev, staging, prod, etc.)

    Returns:
        The instance prefix (e.g., "sandbox", "production", "dev")
    """
    # Map environments to instance prefixes
    instance_mapping = {
        "dev": "sandbox",
        "development": "sandbox",
        "staging": "staging",
        "prod": "production",
        "production": "production",
        "test": "test",
        "testing": "test",
    }

    return instance_mapping.get(environment.lower(), environment.lower())


def generate_export_filename(
    object_type: str,
    format: str = "csv",
    environment: str = "dev",
    timestamp: Optional[datetime] = None,
    custom_suffix: Optional[str] = None,
) -> str:
    """
    Generate an export filename with instance prefix

    Args:
        object_type: Type of object being exported
        format: Export format (csv, json, xlsx, etc.)
        environment: Environment name for instance prefix
        timestamp: Optional timestamp (defaults to now)
        custom_suffix: Optional custom suffix to add before timestamp

    Returns:
        Generated filename with instance prefix
    """
    if timestamp is None:
        timestamp = datetime.now()

    # Get instance prefix
    instance_prefix = get_instance_prefix(environment)

    # Format timestamp
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

    # Build filename components
    parts = [instance_prefix, object_type, "export"]

    if custom_suffix:
        parts.append(custom_suffix)

    parts.append(timestamp_str)

    # Join parts and add extension
    filename = "-".join(parts) + f".{format}"

    return filename


def get_export_file_pattern(
    object_type: str, format: str = "csv", environment: str = "dev"
) -> str:
    """
    Get the file pattern for finding export files with instance prefix

    Args:
        object_type: Type of object being exported
        format: Export format
        environment: Environment name for instance prefix

    Returns:
        Glob pattern for finding export files
    """
    instance_prefix = get_instance_prefix(environment)
    return f"{instance_prefix}-{object_type}-export-*.{format}"


def get_export_directory(environment: str = "dev") -> Path:
    """
    Get the export directory for the given environment

    Args:
        environment: Environment name

    Returns:
        Path to the export directory
    """
    # Base export directory - all environments use the same root directory
    # since files now have environment labels in their names
    return Path("storage/data/csv-exports")


def clean_old_exports(
    object_type: str, environment: str = "dev", format: str = "csv", keep_count: int = 5
) -> None:
    """
    Clean old export files, keeping only the most recent ones

    Args:
        object_type: Type of object being exported
        environment: Environment name
        format: Export format
        keep_count: Number of recent files to keep
    """
    try:
        export_dir = get_export_directory(environment)
        pattern = get_export_file_pattern(object_type, format, environment)

        # Find all matching files
        files = list(export_dir.glob(pattern))

        if len(files) <= keep_count:
            return

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # Remove old files
        for old_file in files[keep_count:]:
            try:
                old_file.unlink()
                print(f"Removed old export: {old_file.name}")
            except Exception as e:
                print(f"Warning: Could not remove {old_file.name}: {e}")

    except Exception as e:
        print(f"Warning: Could not clean old exports: {e}")
