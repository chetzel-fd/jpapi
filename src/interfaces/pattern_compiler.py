#!/usr/bin/env python3
"""
Pattern Compiler Interface
"""

from abc import ABC, abstractmethod
from typing import List, Any


class IPatternCompiler(ABC):
    """Interface for pattern compilation"""

    @abstractmethod
    def compile(self, pattern: str) -> Any:
        """Compile a pattern for matching"""
        pass

    @abstractmethod
    def match(self, pattern: Any, text: str) -> bool:
        """Match text against compiled pattern"""
        pass
