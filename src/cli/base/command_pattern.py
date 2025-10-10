#!/usr/bin/env python3
"""
Command Pattern Data Class
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CommandPattern:
    """Represents a conversational command pattern"""

    pattern: str
    handler: str
    description: str
    aliases: List[str] = None
    required_args: List[str] = None
    optional_args: Dict[str, Any] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.required_args is None:
            self.required_args = []
        if self.optional_args is None:
            self.optional_args = {}
