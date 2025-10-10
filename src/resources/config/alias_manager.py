#!/usr/bin/env python3
"""
Alias Manager for jpapi CLI
Centralized management of command aliases
"""

from typing import Dict, List, Optional, Set
from .command_configs import COMMAND_CONFIGS, CommandConfig

class AliasManager:
    """Manages command aliases and provides lookup functionality"""
    
    def __init__(self):
        self._alias_map: Dict[str, str] = {}
        self._build_alias_map()
    
    def _build_alias_map(self) -> None:
        """Build the alias to command name mapping"""
        for command_name, config in COMMAND_CONFIGS.items():
            # Map aliases to main command name
            for alias in config.aliases:
                self._alias_map[alias] = command_name
            
            # Map subcommand aliases
            if config.subcommands:
                for subcommand_name, subcommand_config in config.subcommands.items():
                    for alias in subcommand_config.aliases:
                        self._alias_map[alias] = f"{command_name}.{subcommand_name}"
    
    def resolve_alias(self, alias: str) -> Optional[str]:
        """Resolve an alias to its main command name"""
        return self._alias_map.get(alias)
    
    def get_command_name(self, input_name: str) -> str:
        """Get the canonical command name from input (which might be an alias)"""
        resolved = self.resolve_alias(input_name)
        return resolved if resolved else input_name
    
    def get_aliases(self, command_name: str) -> List[str]:
        """Get all aliases for a command"""
        aliases = []
        
        # Check main commands
        if command_name in COMMAND_CONFIGS:
            aliases.extend(COMMAND_CONFIGS[command_name].aliases)
        
        # Check subcommands
        for main_command, config in COMMAND_CONFIGS.items():
            if config.subcommands:
                for subcommand_name, subcommand_config in config.subcommands.items():
                    if f"{main_command}.{subcommand_name}" == command_name:
                        aliases.extend(subcommand_config.aliases)
        
        return aliases
    
    def get_all_aliases(self) -> Dict[str, List[str]]:
        """Get all aliases organized by command"""
        all_aliases = {}
        
        for command_name, config in COMMAND_CONFIGS.items():
            all_aliases[command_name] = config.aliases.copy()
            
            # Add subcommand aliases
            if config.subcommands:
                for subcommand_name, subcommand_config in config.subcommands.items():
                    full_name = f"{command_name}.{subcommand_name}"
                    all_aliases[full_name] = subcommand_config.aliases.copy()
        
        return all_aliases
    
    def is_alias(self, name: str) -> bool:
        """Check if a name is an alias"""
        return name in self._alias_map
    
    def get_command_by_alias(self, alias: str) -> Optional[CommandConfig]:
        """Get command configuration by alias"""
        resolved_name = self.resolve_alias(alias)
        if not resolved_name:
            return None
        
        # Handle subcommand resolution
        if '.' in resolved_name:
            main_command, subcommand = resolved_name.split('.', 1)
            if main_command in COMMAND_CONFIGS:
                config = COMMAND_CONFIGS[main_command]
                if config.subcommands and subcommand in config.subcommands:
                    return config.subcommands[subcommand]
        else:
            return COMMAND_CONFIGS.get(resolved_name)
        
        return None
    
    def suggest_aliases(self, partial_name: str) -> List[str]:
        """Suggest aliases that start with the partial name"""
        suggestions = []
        partial_lower = partial_name.lower()
        
        for alias in self._alias_map.keys():
            if alias.lower().startswith(partial_lower):
                suggestions.append(alias)
        
        return sorted(suggestions)
    
    def get_help_text(self, command_name: str) -> str:
        """Get help text for a command, including aliases"""
        config = self.get_command_by_alias(command_name)
        if not config:
            return f"Command '{command_name}' not found"
        
        help_text = config.description
        
        # Add aliases if any
        aliases = self.get_aliases(command_name)
        if aliases:
            help_text += f" (also: {', '.join(aliases)})"
        
        return help_text
    
    def validate_alias(self, alias: str) -> bool:
        """Validate that an alias is properly formatted"""
        if not alias or not isinstance(alias, str):
            return False
        
        # Check for reserved words
        reserved_words = {'help', 'version', 'config', 'setup', 'test'}
        if alias.lower() in reserved_words:
            return False
        
        # Check for conflicts
        if alias in self._alias_map:
            return False
        
        return True
    
    def add_alias(self, command_name: str, alias: str) -> bool:
        """Add a new alias for a command"""
        if not self.validate_alias(alias):
            return False
        
        # This would require updating the configuration
        # For now, just add to the runtime map
        self._alias_map[alias] = command_name
        return True
    
    def remove_alias(self, alias: str) -> bool:
        """Remove an alias"""
        if alias in self._alias_map:
            del self._alias_map[alias]
            return True
        return False

# Global alias manager instance
alias_manager = AliasManager()
