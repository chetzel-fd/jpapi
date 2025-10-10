#!/usr/bin/env python3
"""
Safety Manager for jpapi CLI
Provides production guardrails and safety features
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Using proper package structure via pip install -e .


class SafetyManager:
    """Manages safety features and production guardrails"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize safety manager with configuration"""
        if config_path is None:
            # Default config path
            config_path = (
                Path(__file__).parent.parent.parent.parent
                / "resources"
                / "config"
                / "safety_config.json"
            )

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load safety configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    return json.load(f)
            else:
                # Return default config if file doesn't exist
                return self._get_default_config()
        except Exception as e:
            print(f"⚠️ Warning: Could not load safety config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default safety configuration"""
        return {
            "production_guardrails": {
                "enabled": True,
                "require_confirmation": True,
                "require_environment_typing": True,
                "require_final_confirmation": True,
                "suggest_dry_run": True,
            },
            "destructive_operations": [
                "create",
                "update",
                "delete",
                "modify",
                "change",
                "remove",
                "install",
                "uninstall",
                "deploy",
            ],
            "production_environments": ["prod", "production", "live", "main"],
            "safe_operations": ["list", "show", "info", "status", "help", "version"],
        }

    def is_production_environment(self, environment: str) -> bool:
        """Check if environment is considered production"""
        prod_envs = self.config.get(
            "production_environments", ["prod", "production", "live"]
        )
        return environment.lower() in prod_envs

    def is_destructive_operation(self, operation: str) -> bool:
        """Check if operation is considered destructive"""
        destructive_ops = self.config.get("destructive_operations", [])
        return any(op in operation.lower() for op in destructive_ops)

    def is_safe_operation(self, operation: str) -> bool:
        """Check if operation is considered safe (read-only)"""
        safe_ops = self.config.get("safe_operations", [])
        return any(op in operation.lower() for op in safe_ops)

    def should_require_confirmation(self, environment: str, operation: str) -> bool:
        """Determine if confirmation should be required"""
        if not self.config.get("production_guardrails", {}).get("enabled", True):
            return False

        if not self.is_production_environment(environment):
            return False

        if self.is_safe_operation(operation):
            return False

        return self.is_destructive_operation(operation)

    def get_warning_message(self, warning_type: str) -> str:
        """Get warning message for specific type"""
        warnings = self.config.get("warnings", {})
        return warnings.get(warning_type, f"⚠️ {warning_type}")

    def get_production_warning(self, environment: str) -> str:
        """Get production environment warning message"""
        warning = self.get_warning_message("production_detected")
        return f"{warning}\n   Environment: {environment}\n   Use --dry-run to test operations safely\n   Use --force to skip confirmation prompts"
