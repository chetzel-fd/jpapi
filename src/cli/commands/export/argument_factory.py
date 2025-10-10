#!/usr/bin/env python3
"""
Argument Factory for jpapi CLI Export Commands
Unified factory for creating standardized export arguments
"""

from typing import Dict, Any, List, Optional
from argparse import Namespace

class ArgumentFactory:
    """Factory for creating standardized export arguments"""
    
    # Default configurations for different export types
    EXPORT_DEFAULTS = {
        'scripts': {
            'format': 'json',
            'include_content': True,
            'download_files': True,
            'category': None,
            'name': None,
            'id': None
        },
        'mobile': {
            'format': 'csv',
            'detailed': False,
            'filter': None,
            'filter_type': 'wildcard'
        },
        'computers': {
            'format': 'csv',
            'detailed': False,
            'filter': None,
            'filter_type': 'wildcard'
        },
        'computer-groups': {
            'format': 'csv',
            'detailed': False,
            'filter': None,
            'filter_type': 'wildcard'
        },
        'policies': {
            'format': 'csv',
            'status': 'all',
            'download': False,
            'no_download': False,
            'filter': None,
            'filter_type': 'wildcard'
        },
        'macos-profiles': {
            'format': 'csv',
            'detailed': False
        },
        'ios-profiles': {
            'format': 'csv',
            'detailed': False
        },
        'profiles': {
            'format': 'csv',
            'detailed': False
        },
        'categories': {
            'format': 'csv'
        },
        'advanced-searches': {
            'format': 'csv',
            'detailed': False,
            'name': None,
            'id': None
        }
    }
    
    @classmethod
    def create_export_args(cls, base_args: Namespace, export_type: str, 
                          extra_args: Dict[str, Any] = None) -> Namespace:
        """Create standardized export arguments"""
        export_args = Namespace()
        
        # Copy common attributes from base args
        common_attrs = ['format', 'output', 'verbose', 'detailed', 'environment', 'filter', 'filter_type']
        for attr in common_attrs:
            if hasattr(base_args, attr):
                setattr(export_args, attr, getattr(base_args, attr))
        
        # Set export-specific defaults (only if not already set)
        defaults = cls.EXPORT_DEFAULTS.get(export_type, {})
        for key, value in defaults.items():
            if not hasattr(export_args, key) or getattr(export_args, key) is None:
                setattr(export_args, key, value)
        
        # Override with any provided extra arguments
        if extra_args:
            for key, value in extra_args.items():
                setattr(export_args, key, value)
        
        # Always set the export object type
        export_args.export_object = export_type
        
        return export_args
    
    @classmethod
    def create_script_args(cls, base_args: Namespace, terms: List[str] = None) -> Namespace:
        """Create script-specific arguments with term parsing"""
        script_args = cls.create_export_args(base_args, 'scripts')
        
        if terms:
            # Parse filters from terms
            for i, term in enumerate(terms):
                if term == 'category' and i + 1 < len(terms):
                    script_args.category = terms[i + 1]
                elif term == 'name' and i + 1 < len(terms):
                    script_args.name = terms[i + 1]
                elif term == 'id' and i + 1 < len(terms):
                    script_args.id = terms[i + 1]
        
        return script_args
    
    @classmethod
    def create_device_args(cls, base_args: Namespace, device_type: str) -> Namespace:
        """Create device-specific arguments"""
        return cls.create_export_args(base_args, device_type)
    
    @classmethod
    def create_generic_args(cls, base_args: Namespace, export_type: str) -> Namespace:
        """Create generic arguments for most export types"""
        return cls.create_export_args(base_args, export_type)
    
    @classmethod
    def merge_args(cls, base_args: Namespace, override_args: Namespace) -> Namespace:
        """Merge two Namespace objects, with override_args taking precedence"""
        merged = Namespace()
        
        # Copy all attributes from base_args
        for attr in dir(base_args):
            if not attr.startswith('_'):
                setattr(merged, attr, getattr(base_args, attr))
        
        # Override with attributes from override_args
        for attr in dir(override_args):
            if not attr.startswith('_'):
                setattr(merged, attr, getattr(override_args, attr))
        
        return merged
    
    @classmethod
    def validate_args(cls, args: Namespace, export_type: str) -> List[str]:
        """Validate arguments for a specific export type"""
        errors = []
        
        # Common validations
        if hasattr(args, 'format') and args.format not in ['csv', 'json', 'table']:
            errors.append(f"Invalid format '{args.format}'. Must be csv, json, or table")
        
        if hasattr(args, 'output') and args.output:
            # Basic path validation
            if not isinstance(args.output, str) or len(args.output.strip()) == 0:
                errors.append("Output path must be a non-empty string")
        
        # Type-specific validations
        if export_type == 'scripts':
            if hasattr(args, 'category') and args.category and not isinstance(args.category, str):
                errors.append("Category filter must be a string")
            if hasattr(args, 'name') and args.name and not isinstance(args.name, str):
                errors.append("Name filter must be a string")
            if hasattr(args, 'id') and args.id and not str(args.id).isdigit():
                errors.append("ID filter must be a number")
        
        elif export_type == 'policies':
            if hasattr(args, 'status') and args.status not in ['enabled', 'disabled', 'all']:
                errors.append(f"Invalid status '{args.status}'. Must be enabled, disabled, or all")
        
        return errors
