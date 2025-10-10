#!/usr/bin/env python3
"""
Configuration package for jpapi CLI
Centralized configuration management for commands, arguments, and aliases
"""

from .command_configs import COMMAND_CONFIGS, get_command_config
from .argument_factory import ArgumentFactory
from .alias_manager import AliasManager, alias_manager

__all__ = [
    'COMMAND_CONFIGS',
    'get_command_config',
    'ArgumentFactory',
    'AliasManager',
    'alias_manager'
]
