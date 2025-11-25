#!/usr/bin/env python3
"""
Installomator Service
Main service for managing Installomator policies and apps
"""

import json
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# Add the main jpapi modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# Import auth manager - simplified for now
class MockAuthManager:
    """Mock auth manager for Installomator service"""

    def __init__(self):
        pass


from .policy_config import PolicyConfig, PolicyType, TriggerType


@dataclass
class AppInfo:
    """Information about an Installomator app"""

    app_name: str
    label: str
    description: str = ""
    category: str = ""


@dataclass
class PolicyResult:
    """Result of policy creation"""

    success: bool
    policy_id: Optional[str] = None
    policy_name: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class InstallomatorService:
    """Service for managing Installomator policies"""

    def __init__(self, auth_manager=None, environment: str = "dev"):
        self.auth_manager = auth_manager or MockAuthManager()
        self.environment = environment
        self.apps_cache = []
        self._load_apps()

    def _load_apps(self):
        """Load available Installomator apps from the script"""
        # This would normally parse the Installomator script for available apps
        # For now, we'll use a simplified list based on common apps
        self.apps_cache = [
            AppInfo(
                "Google Chrome", "googlechrome", "Google Chrome browser", "Browsers"
            ),
            AppInfo("Firefox", "firefox", "Mozilla Firefox browser", "Browsers"),
            AppInfo("Slack", "slack", "Slack communication platform", "Communication"),
            AppInfo("Zoom", "zoom", "Zoom video conferencing", "Communication"),
            AppInfo(
                "Microsoft Office",
                "microsoftoffice",
                "Microsoft Office suite",
                "Productivity",
            ),
            AppInfo(
                "Adobe Acrobat", "adobeacrobat", "Adobe Acrobat Reader", "Productivity"
            ),
            AppInfo(
                "Adobe Creative Cloud Desktop",
                "adobecreativeclouddesktop",
                "Adobe Creative Cloud Desktop application",
                "Productivity",
            ),
            AppInfo("1Password", "1password", "1Password password manager", "Security"),
            AppInfo("Dropbox", "dropbox", "Dropbox file sync", "Storage"),
            AppInfo("Spotify", "spotify", "Spotify music streaming", "Entertainment"),
            AppInfo("VLC", "vlc", "VLC media player", "Media"),
        ]

    def list_all_apps(self) -> List[AppInfo]:
        """List all available Installomator apps"""
        return self.apps_cache

    def search_apps(self, search_term: str) -> List[AppInfo]:
        """Search for apps matching the search term"""
        search_term = search_term.lower()
        return [
            app
            for app in self.apps_cache
            if (
                search_term in app.app_name.lower()
                or search_term in app.label.lower()
                or search_term in app.description.lower()
            )
        ]

    def create_policy_interactive(self) -> PolicyResult:
        """Create a policy through interactive prompts"""
        print("🎯 Interactive Policy Creation")
        print("=" * 50)

        # Get app selection
        apps = self.list_all_apps()
        print("\n📱 Available Apps:")
        for i, app in enumerate(apps[:10], 1):  # Show first 10
            print(f"   {i:2d}. {app.app_name:<20} ({app.label})")

        try:
            choice = int(input(f"\nSelect app (1-{min(10, len(apps))}): ")) - 1
            if 0 <= choice < min(10, len(apps)):
                selected_app = apps[choice]
            else:
                return PolicyResult(False, error_message="Invalid app selection")
        except (ValueError, IndexError):
            return PolicyResult(False, error_message="Invalid selection")

        # Get policy details
        policy_name = input(
            f"\nPolicy name (default: Install {selected_app.app_name}): "
        ).strip()
        if not policy_name:
            policy_name = f"Install {selected_app.app_name}"

        # Get policy type
        print("\nPolicy Type:")
        print("  1. Install (one-time)")
        print("  2. Daily Update")
        print("  3. Latest Version")

        try:
            type_choice = int(input("Select type (1-3): "))
            type_map = {
                1: PolicyType.INSTALL,
                2: PolicyType.DAILY_UPDATE,
                3: PolicyType.LATEST_VERSION,
            }
            policy_type = type_map.get(type_choice, PolicyType.INSTALL)
        except (ValueError, KeyError):
            policy_type = PolicyType.INSTALL

        # Create policy configuration
        config = PolicyConfig(
            app_name=selected_app.app_name,
            label=selected_app.label,
            policy_name=policy_name,
            policy_type=policy_type,
            trigger=TriggerType.EVENT,
            description=f"Installomator policy for {selected_app.app_name}",
        )

        # Create the policy
        return self.create_policy(config)

    def create_policy(self, config: PolicyConfig) -> PolicyResult:
        """Create a single policy with duplicate protection"""
        try:
            # Check for existing policy with same name
            existing_policies = self._check_existing_policies(config.policy_name)
            if existing_policies:
                return PolicyResult(
                    success=False,
                    error_message=f"Policy with name '{config.policy_name}' already exists (IDs: {', '.join(existing_policies)})",
                )

            # This would normally create the policy via JAMF API
            # For now, we'll simulate success
            print(f"🚀 Creating policy: {config.policy_name}")
            print(f"   App: {config.app_name}")
            print(f"   Label: {config.label}")
            print(f"   Type: {config.policy_type.value}")

            # Simulate policy creation
            policy_id = f"POL-{hash(config.policy_name) % 10000}"

            return PolicyResult(
                success=True,
                policy_id=policy_id,
                policy_name=config.policy_name,
                warnings=[
                    "Policy created in simulation mode - not actually created in JAMF"
                ],
            )

        except Exception as e:
            return PolicyResult(
                success=False, error_message=f"Failed to create policy: {str(e)}"
            )

    def _check_existing_policies(self, policy_name: str) -> List[str]:
        """Check for existing policies with the same name"""
        # This would normally query JAMF API for existing policies
        # For now, return empty list (no duplicates found)
        return []

    def create_batch_policies(self, configs: List[PolicyConfig]) -> List[PolicyResult]:
        """Create multiple policies from a batch"""
        results = []
        for config in configs:
            result = self.create_policy(config)
            results.append(result)
        return results

    @property
    def batch_processor(self):
        """Get batch processor for loading batch files"""
        return BatchProcessor()

    @property
    def interactive_ui(self):
        """Get interactive UI for displaying results"""
        return InteractiveUI()


class BatchProcessor:
    """Process batch files for policy creation"""

    def load_batch_from_file(self, file_path: str) -> List[PolicyConfig]:
        """Load batch configurations from file"""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            configs = []
            for item in data.get("policies", []):
                config = PolicyConfig(
                    app_name=item.get("app_name", ""),
                    label=item.get("label", ""),
                    policy_name=item.get("policy_name", ""),
                    policy_type=PolicyType(item.get("policy_type", "install")),
                    trigger=TriggerType(item.get("trigger", "EVENT")),
                    category=item.get("category", "IT"),
                    description=item.get("description", ""),
                )
                configs.append(config)

            return configs
        except Exception as e:
            print(f"❌ Error loading batch file: {e}")
            return []


class InteractiveUI:
    """Interactive UI for displaying results"""

    def display_results(self, results: List[PolicyResult]):
        """Display batch creation results"""
        print(f"\n📊 Batch Creation Results:")
        print("=" * 50)

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")

        if successful:
            print("\n✅ Successful Policies:")
            for result in successful:
                print(f"   • {result.policy_name} (ID: {result.policy_id})")

        if failed:
            print("\n❌ Failed Policies:")
            for result in failed:
                print(f"   • {result.policy_name}: {result.error_message}")
