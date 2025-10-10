#!/usr/bin/env python3
"""
Core Interfaces Package
Unified interfaces for the entire JPAPI system following SOLID principles
"""

from .configuration import IConfigurationManager, IConfigurationValidator
from .authentication import IAuthProvider, IAuthManager, IAuthCredentials

__all__ = [
    # Configuration
    "IConfigurationManager",
    "IConfigurationValidator",
    # Authentication
    "IAuthProvider",
    "IAuthManager",
    "IAuthCredentials",
]
