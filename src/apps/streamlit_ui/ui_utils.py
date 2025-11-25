#!/usr/bin/env python3
"""
Shared utilities for Streamlit UI
Provides common helper functions to avoid duplication
Note: Path setup must be done by importing module before importing this
"""

from pathlib import Path

# Import central config (assumes path is already set up by caller)
from resources.config.central_config import central_config


def normalize_environment(env: str) -> str:
    """
    Normalize environment name for consistency.
    Maps internal names (dev, prod) to CLI names (sandbox, production).

    Args:
        env: Environment name (dev, prod, sandbox, production, etc.)

    Returns:
        Normalized environment name (sandbox or production)
    """
    return central_config.normalize_environment(env)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def get_storage_path(subdir: str = "") -> Path:
    """Get path to storage directory."""
    storage = get_project_root() / "storage"
    if subdir:
        storage = storage / subdir
    return storage
