#!/usr/bin/env python3
"""
Controllers Package - SOLID SRP compliance
Contains all controller layer implementations
"""

from .dashboard_controller import DashboardController, DashboardControllerInterface

__all__ = ["DashboardController", "DashboardControllerInterface"]
