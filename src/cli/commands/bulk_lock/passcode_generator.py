"""
Passcode Generator Module - Single Responsibility: Generate secure passcodes
"""
import secrets


class PasscodeGenerator:
    """Generates random 6-digit passcodes - Single Responsibility"""

    @staticmethod
    def generate() -> str:
        """Generate a random 6-digit passcode"""
        return f"{secrets.randbelow(1000000):06d}"









