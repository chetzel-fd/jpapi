#!/usr/bin/env python3
"""
Argument Factory for jpapi CLI
Creates argument parsers from configuration
"""

import argparse
from typing import List, Optional, Any
from .command_configs import CommandConfig, ArgumentConfig, COMMON_ARGUMENTS

class ArgumentFactory:
    """Factory for creating argument parsers from configuration"""
    
    @staticmethod
    def create_parser(config: CommandConfig) -> argparse.ArgumentParser:
        """Create an argument parser from command configuration"""
        parser = argparse.ArgumentParser(
            prog=config.name,
            description=config.description
        )
        
        # Add main arguments
        ArgumentFactory._add_arguments(parser, config.arguments)
        
        # Add common arguments
        if config.common_args:
            ArgumentFactory._add_common_arguments(parser, config.common_args)
        
        # Add subcommands if they exist
        if config.subcommands:
            ArgumentFactory._add_subcommands(parser, config.subcommands)
        
        return parser
    
    @staticmethod
    def _add_arguments(parser: argparse.ArgumentParser, arguments: List[ArgumentConfig]) -> None:
        """Add arguments to a parser"""
        for arg_config in arguments:
            ArgumentFactory._add_single_argument(parser, arg_config)
    
    @staticmethod
    def _add_single_argument(parser: argparse.ArgumentParser, arg_config: ArgumentConfig) -> None:
        """Add a single argument to a parser"""
        # Prepare argument kwargs
        kwargs = {
            'help': arg_config.help_text
        }
        
        # Add optional parameters
        if arg_config.action:
            kwargs['action'] = arg_config.action
        if arg_config.choices:
            kwargs['choices'] = arg_config.choices
        if arg_config.default is not None:
            kwargs['default'] = arg_config.default
        if arg_config.type:
            kwargs['type'] = ArgumentFactory._get_type_function(arg_config.type)
        if arg_config.nargs:
            kwargs['nargs'] = arg_config.nargs
        
        # Handle required for positional vs optional arguments
        if arg_config.name.startswith('-'):
            # Optional argument
            if arg_config.required:
                kwargs['required'] = arg_config.required
        else:
            # Positional argument - required is handled by nargs
            if arg_config.required and not arg_config.nargs:
                kwargs['nargs'] = 1
        
        # Add the argument
        parser.add_argument(arg_config.name, **kwargs)
    
    @staticmethod
    def _add_common_arguments(parser: argparse.ArgumentParser, common_arg_names: List[str]) -> None:
        """Add common arguments to a parser"""
        for arg_name in common_arg_names:
            common_config = COMMON_ARGUMENTS.get(arg_name)
            if common_config:
                ArgumentFactory._add_single_argument(parser, common_config)
    
    @staticmethod
    def _add_subcommands(parser: argparse.ArgumentParser, subcommands: dict) -> None:
        """Add subcommands to a parser"""
        subparsers = parser.add_subparsers(dest='subcommand', help='Available subcommands')
        
        for subcommand_name, subcommand_config in subcommands.items():
            # Create main subcommand
            sub_parser = subparsers.add_parser(
                subcommand_name,
                help=subcommand_config.description
            )
            ArgumentFactory._add_arguments(sub_parser, subcommand_config.arguments)
            
            # Add common arguments to subcommand
            if subcommand_config.common_args:
                ArgumentFactory._add_common_arguments(sub_parser, subcommand_config.common_args)
            
            # Create aliases
            for alias in subcommand_config.aliases:
                alias_parser = subparsers.add_parser(
                    alias,
                    help=argparse.SUPPRESS
                )
                ArgumentFactory._add_arguments(alias_parser, subcommand_config.arguments)
                
                # Add common arguments to alias
                if subcommand_config.common_args:
                    ArgumentFactory._add_common_arguments(alias_parser, subcommand_config.common_args)
    
    @staticmethod
    def _get_type_function(type_name: str):
        """Get the appropriate type function for argument validation"""
        type_functions = {
            'int': int,
            'str': str,
            'float': float,
            'bool': bool,
            'file_path': ArgumentFactory._validate_file_path,
            'wildcard_pattern': ArgumentFactory._validate_wildcard_pattern,
            'comma_separated_ids': ArgumentFactory._validate_comma_separated_ids
        }
        
        return type_functions.get(type_name, str)
    
    @staticmethod
    def _validate_file_path(file_path: str) -> str:
        """Validate that a file path exists"""
        import os
        if not os.path.exists(file_path):
            raise argparse.ArgumentTypeError(f"File does not exist: {file_path}")
        return file_path
    
    @staticmethod
    def _validate_wildcard_pattern(pattern: str) -> str:
        """Validate wildcard pattern"""
        # Basic validation - could be enhanced
        if not pattern or not isinstance(pattern, str):
            raise argparse.ArgumentTypeError("Pattern must be a non-empty string")
        return pattern
    
    @staticmethod
    def _validate_comma_separated_ids(ids_str: str) -> List[str]:
        """Validate and parse comma-separated IDs"""
        if not ids_str:
            return []
        
        try:
            ids = [id.strip() for id in ids_str.split(',')]
            # Validate that all IDs are numeric
            for id in ids:
                if not id.isdigit():
                    raise ValueError(f"Invalid ID: {id}")
            return ids
        except Exception as e:
            raise argparse.ArgumentTypeError(f"Invalid ID format: {e}")
    
    @staticmethod
    def create_aliases_parser(config: CommandConfig) -> argparse.ArgumentParser:
        """Create a parser that includes all aliases as main commands"""
        parser = argparse.ArgumentParser(
            prog=config.name,
            description=config.description
        )
        
        # Add main command
        ArgumentFactory._add_arguments(parser, config.arguments)
        
        # Add common arguments
        if config.common_args:
            ArgumentFactory._add_common_arguments(parser, config.common_args)
        
        # Add subcommands
        if config.subcommands:
            ArgumentFactory._add_subcommands(parser, config.subcommands)
        
        return parser
