#!/usr/bin/env python3
"""
Common Imports Module for CLI Commands
Eliminates duplicate import boilerplate across all command files

This module provides a centralized location for common imports used across
all CLI command modules, reducing code duplication and ensuring consistency.

Usage:
    from .common_imports import ArgumentParser, Namespace, BaseCommand

Features:
    - Automatic path setup for proper imports
    - Common type hints and classes
    - Consistent import patterns across all commands
"""

from argparse import ArgumentParser, Namespace
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Using proper package structure via pip install -e .
# No manual path manipulation needed!

# Common imports that all commands need
from ..base.command import BaseCommand

# Re-export commonly used types and classes
__all__ = [
    "ArgumentParser",
    "Namespace",
    "Dict",
    "Any",
    "List",
    "Optional",
    "sys",
    "Path",
    "BaseCommand",
]
