#!/usr/bin/env python3
"""
Production Checker Service - SOLID SRP
Adapter for BaseCommand's SafetyValidator
"""

from abc import ABC, abstractmethod
from argparse import Namespace
from typing import Optional


class IProductionChecker(ABC):
    """Interface for production safety checks"""
    
    @abstractmethod
    def is_production_environment(self) -> bool:
        """Check if current environment is production"""
        pass
    
    @abstractmethod
    def check_destructive_operation(self, operation: str, name: str) -> bool:
        """Check if destructive operation should proceed"""
        pass
    
    @abstractmethod
    def require_production_confirmation(
        self, operation: str, details: str, changes_summary: str, args: Optional[Namespace] = None
    ) -> bool:
        """Require confirmation for production operations"""
        pass


class ProductionCheckerAdapter(IProductionChecker):
    """Adapter for BaseCommand's SafetyValidator"""
    
    def __init__(self, base_command):
        """
        Initialize with BaseCommand instance
        
        Args:
            base_command: BaseCommand instance with safety_validator
        """
        self.base_command = base_command
        self.environment = base_command.environment
    
    def is_production_environment(self) -> bool:
        """Check if current environment is production"""
        return self.base_command.is_production_environment()
    
    def check_destructive_operation(self, operation: str, name: str) -> bool:
        """Check if destructive operation should proceed"""
        return self.base_command.check_destructive_operation(operation, name)
    
    def require_production_confirmation(
        self, operation: str, details: str, changes_summary: str, args: Optional[Namespace] = None
    ) -> bool:
        """Require confirmation for production operations"""
        return self.base_command.require_production_confirmation(
            operation, details, changes_summary, args
        )









