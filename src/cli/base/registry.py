#!/usr/bin/env python3
"""
Command Registry for jpapi CLI
Manages registration and discovery of CLI commands
"""

from typing import Dict, Type, List
from .command import BaseCommand

class CommandRegistry:
    """Registry for CLI commands"""
    
    def __init__(self):
        self._commands: Dict[str, Type[BaseCommand]] = {}
        self._aliases: Dict[str, str] = {}
    
    def register(self, command_class: Type[BaseCommand], aliases: List[str] = None) -> None:
        """Register a command class"""
        # Create instance to get name
        instance = command_class()
        command_name = instance.name
        
        self._commands[command_name] = command_class
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self._aliases[alias] = command_name
    
    def get_command(self, name: str) -> Type[BaseCommand]:
        """Get command class by name or alias"""
        # Check aliases first
        if name in self._aliases:
            name = self._aliases[name]
        
        if name not in self._commands:
            raise ValueError(f"Unknown command: {name}")
        
        return self._commands[name]
    
    def list_commands(self) -> List[str]:
        """List all registered commands"""
        return list(self._commands.keys())
    
    def list_aliases(self) -> Dict[str, str]:
        """List all command aliases"""
        return self._aliases.copy()
    
    def has_command(self, name: str) -> bool:
        """Check if command exists"""
        return name in self._commands or name in self._aliases

# Global registry instance
registry = CommandRegistry()
