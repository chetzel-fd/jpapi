#!/usr/bin/env python3
"""
Installomator Factory
Factory for creating Installomator services
"""

import sys
from pathlib import Path
from typing import Optional

# Add the main jpapi modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# Mock auth manager for now
class MockAuthManager:
    """Mock auth manager for Installomator factory"""

    def __init__(self):
        pass


from .installomator_service import InstallomatorService


class InstallomatorFactory:
    """Factory for creating Installomator services"""

    def __init__(self):
        self._auth_manager = None

    def create_installomator_service(
        self, environment: str = "dev", use_mock_components: bool = False
    ) -> InstallomatorService:
        """Create an Installomator service"""
        if not self._auth_manager:
            self._auth_manager = MockAuthManager()

        return InstallomatorService(
            auth_manager=self._auth_manager, environment=environment
        )
