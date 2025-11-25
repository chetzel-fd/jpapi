#!/usr/bin/env python3
"""
Base Handler for Create Operations - SOLID SRP
Provides common functionality for all create handlers
"""

from abc import ABC, abstractmethod
from argparse import Namespace
from typing import Optional
from core.auth.login_types import AuthInterface
from lib.utils.manage_signatures import add_signature_to_name


class ICreateHandler(ABC):
    """Interface for create operation handlers"""
    
    @abstractmethod
    def create(self, args: Namespace) -> int:
        """Create the object and return exit code"""
        pass
    
    @abstractmethod
    def can_handle(self, object_type: str) -> bool:
        """Check if this handler can handle the given object type"""
        pass


class BaseCreateHandler(ICreateHandler):
    """Base class for all create handlers with common functionality"""
    
    def __init__(self, auth: AuthInterface, xml_converter, production_checker=None):
        """
        Initialize handler with dependencies
        
        Args:
            auth: Authentication interface for API requests
            xml_converter: Service for XML conversion
            production_checker: Optional service for production safety checks
        """
        self.auth = auth
        self.xml_converter = xml_converter
        self.production_checker = production_checker
    
    def apply_signature(self, name: str) -> str:
        """Apply signature to object name"""
        return add_signature_to_name(name)
    
    def handle_api_error(self, error: Exception) -> int:
        """Handle API errors consistently"""
        print(f"❌ API Error: {error}")
        import traceback
        traceback.print_exc()
        return 1
    
    def check_dry_run(self, args: Namespace, object_type: str, name: str) -> Optional[int]:
        """Check if dry-run mode and return early if so"""
        if getattr(args, "dry_run", False):
            signed_name = self.apply_signature(name)
            print(f"🔍 DRY-RUN: Would create {object_type}: {signed_name}")
            print("\n✅ Dry-run complete. Use without --dry-run to actually create.")
            return 0
        return None









