#!/usr/bin/env python3
"""
Command Configuration for jpapi CLI
Centralized configuration for all commands, arguments, and aliases
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ArgumentConfig:
    """Configuration for a command argument"""
    name: str
    help_text: str
    action: Optional[str] = None
    choices: Optional[List[str]] = None
    default: Any = None
    required: bool = False
    type: Optional[str] = None
    nargs: Optional[str] = None

@dataclass
class CommandConfig:
    """Configuration for a command"""
    name: str
    description: str
    aliases: List[str]
    arguments: List[ArgumentConfig]
    subcommands: Optional[Dict[str, 'CommandConfig']] = None
    common_args: List[str] = None

# Common argument configurations
COMMON_ARGUMENTS = {
    'format': ArgumentConfig(
        name='--format',
        help_text='Output format',
        choices=['csv', 'json', 'table'],
        default='table'
    ),
    'output': ArgumentConfig(
        name='--output',
        help_text='Output file path'
    ),
    'verbose': ArgumentConfig(
        name='--verbose',
        help_text='Verbose output',
        action='store_true'
    ),
    'force': ArgumentConfig(
        name='--force',
        help_text='Skip confirmation prompts',
        action='store_true'
    ),
    'dry_run': ArgumentConfig(
        name='--dry-run',
        help_text='Show what would be done without making changes',
        action='store_true'
    ),
    'env': ArgumentConfig(
        name='--env',
        help_text='Environment to operate in',
        choices=['dev', 'staging', 'prod'],
        default='dev'
    )
}

# Command configurations
COMMAND_CONFIGS = {
    'list': CommandConfig(
        name='list',
        description='📋 List JAMF objects (policies, devices, groups, etc.)',
        aliases=['ls', 'show'],
        arguments=[
            ArgumentConfig(
                name='list_target',
                help_text='What to list (categories, profiles, computers, mobile, etc.)',
                nargs='?'
            ),
            ArgumentConfig(
                name='list_terms',
                help_text='Additional terms or filters',
                nargs='*'
            )
        ],
        subcommands={
            'categories': CommandConfig(
                name='categories',
                description='List all categories',
                aliases=['category', 'cats'],
                arguments=[
                    ArgumentConfig(
                        name='--detailed',
                        help_text='Show detailed info including categories and certificate payloads',
                        action='store_true'
                    )
                ]
            ),
            'profiles': CommandConfig(
                name='profiles',
                description='List configuration profiles',
                aliases=['profile', 'configs', 'config'],
                arguments=[
                    ArgumentConfig(
                        name='--detailed',
                        help_text='Show detailed info including categories and certificate payloads',
                        action='store_true'
                    )
                ]
            ),
            'computers': CommandConfig(
                name='computers',
                description='List computers/Macs',
                aliases=['computer', 'macs', 'macos', 'mac'],
                arguments=[
                    ArgumentConfig(
                        name='computer_type',
                        help_text='Type of computer objects to list',
                        choices=['policies', 'devices'],
                        nargs='?'
                    ),
                    ArgumentConfig(
                        name='--filter',
                        help_text='Filter by name, model, or OS version'
                    ),
                    ArgumentConfig(
                        name='--status',
                        help_text='Filter policies by status',
                        choices=['enabled', 'disabled', 'all'],
                        default='all'
                    ),
                    ArgumentConfig(
                        name='--detailed',
                        help_text='Show detailed info',
                        action='store_true'
                    ),
                    ArgumentConfig(
                        name='--security-issues',
                        help_text='Show only items with security issues',
                        action='store_true'
                    )
                ]
            ),
            'mobile': CommandConfig(
                name='mobile',
                description='List mobile devices',
                aliases=['ipad', 'iphone', 'devices'],
                arguments=[
                    ArgumentConfig(
                        name='--filter',
                        help_text='Filter devices by name, type, or OS version'
                    ),
                    ArgumentConfig(
                        name='--security-issues',
                        help_text='Show only devices with security issues',
                        action='store_true'
                    )
                ]
            ),
            'policies': CommandConfig(
                name='policies',
                description='List policies',
                aliases=['policy'],
                arguments=[
                    ArgumentConfig(
                        name='--status',
                        help_text='Filter by policy status',
                        choices=['enabled', 'disabled', 'all'],
                        default='all'
                    ),
                    ArgumentConfig(
                        name='--detailed',
                        help_text='Show detailed info including categories and scope',
                        action='store_true'
                    )
                ]
            ),
            'scripts': CommandConfig(
                name='scripts',
                description='List scripts',
                aliases=['script'],
                arguments=[
                    ArgumentConfig(
                        name='--category',
                        help_text='Filter by script category'
                    ),
                    ArgumentConfig(
                        name='--name',
                        help_text='Filter by script name (supports wildcards)'
                    ),
                    ArgumentConfig(
                        name='--id',
                        help_text='Filter by specific script ID'
                    ),
                    ArgumentConfig(
                        name='--detailed',
                        help_text='Show detailed info including script content preview',
                        action='store_true'
                    ),
                    ArgumentConfig(
                        name='--content',
                        help_text='Show full script content',
                        action='store_true'
                    )
                ]
            )
        }
    ),
    
    'update': CommandConfig(
        name='update',
        description='🔄 Update JAMF objects from CSV files with delete column support',
        aliases=['sync', 'modify'],
        arguments=[
            ArgumentConfig(
                name='object_type',
                help_text='Object type to update (computer-groups, policies, etc.)',
                choices=['computer-groups', 'policies', 'scripts', 'advanced-searches']
            ),
            ArgumentConfig(
                name='csv_file',
                help_text='CSV file to sync from',
                type='file_path'
            ),
            ArgumentConfig(
                name='--dry-run',
                help_text='Show what would be changed without actually making changes',
                action='store_true'
            ),
            ArgumentConfig(
                name='--confirm',
                help_text='Skip confirmation prompts',
                action='store_true'
            ),
            ArgumentConfig(
                name='--filter',
                help_text='Filter policies by name pattern (supports wildcards)',
                type='wildcard_pattern'
            ),
            ArgumentConfig(
                name='--ids',
                help_text='Comma-separated list of policy IDs to update',
                type='comma_separated_ids'
            ),
            ArgumentConfig(
                name='--only-updates',
                help_text='Only process policies that have changes (skip unchanged policies)',
                action='store_true'
            ),
            ArgumentConfig(
                name='--only-deletes',
                help_text='Only process policies marked for deletion',
                action='store_true'
            ),
            ArgumentConfig(
                name='--all',
                help_text='Process all policies in CSV (default: only process policies with changes)',
                action='store_true'
            )
        ],
        common_args=['format', 'output', 'verbose', 'force', 'env']
    ),
    
    'create': CommandConfig(
        name='create',
        description='🛠️ Create new JAMF objects (categories, policies, searches)',
        aliases=['new', 'add'],
        arguments=[],
        subcommands={
            'category': CommandConfig(
                name='category',
                description='Create new category',
                aliases=['cat', 'cats'],
                arguments=[
                    ArgumentConfig(
                        name='name',
                        help_text='Category name',
                        required=True
                    ),
                    ArgumentConfig(
                        name='--priority',
                        help_text='Category priority (1-20)',
                        type='int',
                        default=9
                    )
                ]
            ),
            'policy': CommandConfig(
                name='policy',
                description='Create new policy',
                aliases=['pol', 'policies'],
                arguments=[
                    ArgumentConfig(
                        name='name',
                        help_text='Policy name',
                        required=True
                    ),
                    ArgumentConfig(
                        name='--category',
                        help_text='Policy category'
                    ),
                    ArgumentConfig(
                        name='--enabled',
                        help_text='Enable policy immediately',
                        action='store_true'
                    ),
                    ArgumentConfig(
                        name='--frequency',
                        help_text='Policy frequency',
                        choices=['Once per computer', 'Once per user', 'Ongoing'],
                        default='Ongoing'
                    ),
                    ArgumentConfig(
                        name='--trigger',
                        help_text='Policy trigger',
                        choices=['Startup', 'Login', 'Logout', 'Check-in'],
                        default='Check-in'
                    )
                ]
            ),
            'search': CommandConfig(
                name='search',
                description='Create search template',
                aliases=['find', 'searches'],
                arguments=[
                    ArgumentConfig(
                        name='name',
                        help_text='Search template name',
                        required=True
                    ),
                    ArgumentConfig(
                        name='--type',
                        help_text='Search type',
                        choices=['computer', 'mobile'],
                        default='computer'
                    ),
                    ArgumentConfig(
                        name='--criteria',
                        help_text='Search criteria (JSON format)'
                    ),
                    ArgumentConfig(
                        name='--display-fields',
                        help_text='Display fields (comma-separated)'
                    )
                ]
            ),
            'group': CommandConfig(
                name='group',
                description='Create new group',
                aliases=['grp', 'groups'],
                arguments=[
                    ArgumentConfig(
                        name='name',
                        help_text='Group name',
                        required=True
                    ),
                    ArgumentConfig(
                        name='--type',
                        help_text='Group type',
                        choices=['computer', 'mobile'],
                        default='computer'
                    ),
                    ArgumentConfig(
                        name='--smart',
                        help_text='Create smart group',
                        action='store_true'
                    ),
                    ArgumentConfig(
                        name='--criteria',
                        help_text='Smart group criteria (JSON format)'
                    )
                ]
            ),
            'smart-group': CommandConfig(
                name='smart-group',
                description='Create smart group with flexible criteria',
                aliases=['smart', 'smartgrp'],
                arguments=[
                    ArgumentConfig(
                        name='name',
                        help_text='Group name',
                        required=True
                    ),
                    ArgumentConfig(
                        name='--criteria',
                        help_text='Smart group criteria (e.g., email:"user1,user2", model:"MacBook Pro")',
                        required=True
                    ),
                    ArgumentConfig(
                        name='--type',
                        help_text='Group type',
                        choices=['computer', 'mobile'],
                        default='computer'
                    )
                ]
            ),
            'profile': CommandConfig(
                name='profile',
                description='Create new configuration profile',
                aliases=['prof', 'profiles'],
                arguments=[
                    ArgumentConfig(
                        name='name',
                        help_text='Profile name',
                        required=True
                    ),
                    ArgumentConfig(
                        name='--type',
                        help_text='Profile type',
                        choices=['macos', 'ios'],
                        default='macos'
                    ),
                    ArgumentConfig(
                        name='--description',
                        help_text='Profile description'
                    ),
                    ArgumentConfig(
                        name='--category',
                        help_text='Profile category'
                    )
                ]
            ),
            'signature': CommandConfig(
                name='signature',
                description='Configure signature settings',
                aliases=[],
                arguments=[
                    ArgumentConfig(
                        name='--set',
                        help_text='Set the signature to use (e.g., "jdoe")'
                    ),
                    ArgumentConfig(
                        name='--show',
                        help_text='Show current signature',
                        action='store_true'
                    ),
                    ArgumentConfig(
                        name='--reset',
                        help_text='Reset to default signature (chetzel)',
                        action='store_true'
                    )
                ]
            )
        },
        common_args=['format', 'output', 'verbose', 'force', 'env']
    )
}

def get_command_config(command_name: str) -> Optional[CommandConfig]:
    """Get configuration for a command by name or alias"""
    # Direct lookup
    if command_name in COMMAND_CONFIGS:
        return COMMAND_CONFIGS[command_name]
    
    # Search through aliases
    for config in COMMAND_CONFIGS.values():
        if command_name in config.aliases:
            return config
    
    return None

def get_common_argument_config(arg_name: str) -> Optional[ArgumentConfig]:
    """Get configuration for a common argument"""
    return COMMON_ARGUMENTS.get(arg_name)
