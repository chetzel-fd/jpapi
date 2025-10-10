#!/usr/bin/env python3
"""
Subcommand Config Data Class
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class SubcommandConfig:
    """Configuration for subcommand creation"""

    name: str
    aliases: List[str]
    description: str
    handler_method: str
    arguments: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.arguments is None:
            self.arguments = []
