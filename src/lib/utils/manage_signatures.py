#!/usr/bin/env python3
"""
Signature Utilities for JPAPI Dev
Provides standardized signature generation for Jamf objects
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.config_storage import IConfigStorage
import re


class SignatureManager:
    """Generates standardized signatures for Jamf objects"""

    def __init__(
        self,
        user_signature: str = "admin",
        config_storage: Optional["IConfigStorage"] = None,
    ):
        """
        Initialize signature manager

        Args:
            user_signature: The user signature to append (default: "admin")
            config_storage: Optional configuration storage implementation
        """
        from .store_config_env import EnvConfigStorage
        from .store_config_file import FileConfigStorage
        from .store_config_composite import CompositeConfigStorage

        # Initialize configuration storage
        self._storage = config_storage or CompositeConfigStorage(
            [EnvConfigStorage(), FileConfigStorage()]
        )

        # Initialize user signature
        stored_sig = self._storage.get_config("signature")
        self.user_signature = stored_sig or user_signature

    def generate_signature(self, include_date: bool = True) -> str:
        """
        Generate a signature string

        Args:
            include_date: Whether to include the current date in the signature

        Returns:
            Signature string in format " - username YYYY.MM.DD" or " - username"
        """
        signature = f" - {self.user_signature}"

        if include_date:
            current_date = datetime.now()
            date_str = current_date.strftime("%Y.%m.%d")
            signature += f" {date_str}"

        return signature

    def add_signature_to_name(self, name: str, include_date: bool = True) -> str:
        """
        Add signature to an object name

        Args:
            name: The original object name
            include_date: Whether to include the current date in the signature

        Returns:
            Name with signature appended
        """
        # Check if signature is already present
        if self._has_existing_signature(name):
            return name

        signature = self.generate_signature(include_date)
        return f"{name}{signature}"

    def _has_existing_signature(self, name: str) -> bool:
        """
        Check if a name already has a signature

        Args:
            name: The name to check

        Returns:
            True if signature is already present
        """
        # Look for the pattern " - username" followed by optional date

        pattern = r" - [a-zA-Z0-9_]+(\s+\d{4}\.\d{2}\.\d{2})?$"
        return bool(re.search(pattern, name))

    def remove_signature_from_name(self, name: str) -> str:
        """
        Remove signature from a name

        Args:
            name: The name with signature

        Returns:
            Name without signature
        """

        pattern = r" - [a-zA-Z0-9_]+(\s+\d{4}\.\d{2}\.\d{2})?$"
        return re.sub(pattern, "", name).strip()

    def update_signature_in_name(self, name: str, include_date: bool = True) -> str:
        """
        Update or add signature to a name

        Args:
            name: The original name
            include_date: Whether to include the current date in the signature

        Returns:
            Name with updated signature
        """
        # Remove existing signature if present
        clean_name = self.remove_signature_from_name(name)

        # Add new signature
        return self.add_signature_to_name(clean_name, include_date)


def get_user_signature() -> str:
    """
    Get the user signature from configuration

    Returns:
        User signature string
    """
    from .store_config_env import EnvConfigStorage
    from .store_config_file import FileConfigStorage
    from .store_config_composite import CompositeConfigStorage

    storage = CompositeConfigStorage([EnvConfigStorage(), FileConfigStorage()])

    return storage.get_config("signature") or "admin"


def set_user_signature(signature: str) -> None:
    """
    Set the user signature in configuration

    Args:
        signature: The signature to set
    """
    from .store_config_env import EnvConfigStorage
    from .store_config_file import FileConfigStorage
    from .store_config_composite import CompositeConfigStorage

    storage = CompositeConfigStorage([EnvConfigStorage(), FileConfigStorage()])

    storage.set_config("signature", signature)


# Global instance for easy access - now configurable
default_signature_manager = SignatureManager(get_user_signature())

# Test signature manager for AI-created test objects
test_signature_manager = SignatureManager("bsimpson")


def add_signature_to_name(name: str, include_date: bool = True) -> str:
    """
    Convenience function to add signature to a name

    Args:
        name: The original object name
        include_date: Whether to include the current date in the signature

    Returns:
        Name with signature appended
    """
    # Refresh the global manager to get the latest signature
    global default_signature_manager
    default_signature_manager = SignatureManager(get_user_signature())
    return default_signature_manager.add_signature_to_name(name, include_date)


def remove_signature_from_name(name: str) -> str:
    """
    Convenience function to remove signature from a name

    Args:
        name: The name with signature

    Returns:
        Name without signature
    """
    # Refresh the global manager to get the latest signature
    global default_signature_manager
    default_signature_manager = SignatureManager(get_user_signature())
    return default_signature_manager.remove_signature_from_name(name)


def update_signature_in_name(name: str, include_date: bool = True) -> str:
    """
    Convenience function to update signature in a name

    Args:
        name: The original name
        include_date: Whether to include the current date in the signature

    Returns:
        Name with updated signature
    """
    # Refresh the global manager to get the latest signature
    global default_signature_manager
    default_signature_manager = SignatureManager(get_user_signature())
    return default_signature_manager.update_signature_in_name(name, include_date)


def add_test_signature_to_name(name: str, include_date: bool = True) -> str:
    """Add test signature (bsimpson) to a name.

    Used for test objects.

    Args:
        name: Name to sign
        include_date: Add date
    """
    return test_signature_manager.add_signature_to_name(name, include_date)
