#!/usr/bin/env python3
"""
Profile Generator for Installomator Apps
Automatically generates PPPC and configuration profiles based on Installomator labels
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.pppc_scanner import PPPCScanner
from tools.profile_manifests import ProfileManifestManager


@dataclass
class AppProfileInfo:
    """Information about an app's profile requirements"""

    app_name: str
    label: str
    bundle_id: str
    category: str
    requires_pppc: bool = True
    requires_preferences: bool = True
    pppc_permissions: List[str] = None
    preference_domains: List[str] = None

    def __post_init__(self):
        if self.pppc_permissions is None:
            self.pppc_permissions = []
        if self.preference_domains is None:
            self.preference_domains = []


class InstallomatorProfileGenerator:
    """Generates configuration profiles for Installomator apps"""

    def __init__(self, output_dir: str = "storage/data/installomator-profiles"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # App profile mappings - maps Installomator labels to profile requirements
        self.app_profiles = self._load_app_profile_mappings()

        # Initialize profile generators
        self.pppc_scanner = PPPCScanner()
        self.manifest_manager = ProfileManifestManager()

    def _load_app_profile_mappings(self) -> Dict[str, AppProfileInfo]:
        """Load mappings of Installomator labels to profile requirements"""
        return {
            "adobecreativeclouddesktop": AppProfileInfo(
                app_name="Adobe Creative Cloud Desktop",
                label="adobecreativeclouddesktop",
                bundle_id="com.adobe.acc.installer.v2",
                category="Productivity",
                requires_pppc=True,
                requires_preferences=True,
                pppc_permissions=[
                    "SystemEvents",
                    "Automation",
                    "Accessibility",
                    "ScreenCapture",
                    "Camera",
                    "Microphone",
                ],
                preference_domains=[
                    "com.adobe.acc.installer.v2",
                    "com.adobe.acc.installer",
                    "com.adobe.acc",
                ],
            ),
            "googlechrome": AppProfileInfo(
                app_name="Google Chrome",
                label="googlechrome",
                bundle_id="com.google.Chrome",
                category="Browsers",
                requires_pppc=True,
                requires_preferences=True,
                pppc_permissions=["SystemEvents", "Automation", "Accessibility"],
                preference_domains=["com.google.Chrome", "com.google.Chrome.canary"],
            ),
            "microsoftteams": AppProfileInfo(
                app_name="Microsoft Teams",
                label="microsoftteams",
                bundle_id="com.microsoft.teams",
                category="Communication",
                requires_pppc=True,
                requires_preferences=True,
                pppc_permissions=[
                    "SystemEvents",
                    "Automation",
                    "Accessibility",
                    "Camera",
                    "Microphone",
                    "ScreenCapture",
                ],
                preference_domains=[
                    "com.microsoft.teams",
                    "com.microsoft.teams.standalone",
                ],
            ),
            "slack": AppProfileInfo(
                app_name="Slack",
                label="slack",
                bundle_id="com.tinyspeck.slackmacgap",
                category="Communication",
                requires_pppc=True,
                requires_preferences=True,
                pppc_permissions=[
                    "SystemEvents",
                    "Automation",
                    "Accessibility",
                    "Camera",
                    "Microphone",
                    "ScreenCapture",
                ],
                preference_domains=[
                    "com.tinyspeck.slackmacgap",
                    "com.tinyspeck.slackmacgap.helper",
                ],
            ),
            "zoom": AppProfileInfo(
                app_name="Zoom",
                label="zoom",
                bundle_id="us.zoom.xos",
                category="Communication",
                requires_pppc=True,
                requires_preferences=True,
                pppc_permissions=[
                    "SystemEvents",
                    "Automation",
                    "Accessibility",
                    "Camera",
                    "Microphone",
                    "ScreenCapture",
                ],
                preference_domains=["us.zoom.xos", "us.zoom.xos.helper"],
            ),
            "microsoftoffice": AppProfileInfo(
                app_name="Microsoft Office",
                label="microsoftoffice",
                bundle_id="com.microsoft.office",
                category="Productivity",
                requires_pppc=True,
                requires_preferences=True,
                pppc_permissions=["SystemEvents", "Automation", "Accessibility"],
                preference_domains=[
                    "com.microsoft.office",
                    "com.microsoft.Word",
                    "com.microsoft.Excel",
                    "com.microsoft.PowerPoint",
                ],
            ),
            "1password": AppProfileInfo(
                app_name="1Password",
                label="1password",
                bundle_id="com.1password.1password",
                category="Security",
                requires_pppc=True,
                requires_preferences=True,
                pppc_permissions=["SystemEvents", "Automation", "Accessibility"],
                preference_domains=[
                    "com.1password.1password",
                    "com.1password.1password.helper",
                ],
            ),
            "dropbox": AppProfileInfo(
                app_name="Dropbox",
                label="dropbox",
                bundle_id="com.dropbox.DropboxMacUpdate",
                category="Storage",
                requires_pppc=True,
                requires_preferences=True,
                pppc_permissions=["SystemEvents", "Automation", "Accessibility"],
                preference_domains=[
                    "com.dropbox.DropboxMacUpdate",
                    "com.dropbox.DropboxMacUpdate.agent",
                ],
            ),
            "spotify": AppProfileInfo(
                app_name="Spotify",
                label="spotify",
                bundle_id="com.spotify.client",
                category="Entertainment",
                requires_pppc=False,
                requires_preferences=True,
                pppc_permissions=[],
                preference_domains=["com.spotify.client"],
            ),
            "vlc": AppProfileInfo(
                app_name="VLC",
                label="vlc",
                bundle_id="org.videolan.vlc",
                category="Media",
                requires_pppc=False,
                requires_preferences=True,
                pppc_permissions=[],
                preference_domains=["org.videolan.vlc"],
            ),
        }

    def generate_profiles_for_app(
        self, label: str, output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate all profiles for a specific Installomator app"""
        if label not in self.app_profiles:
            raise ValueError(
                f"No profile mapping found for Installomator label: {label}"
            )

        app_info = self.app_profiles[label]
        output_path = Path(output_dir) if output_dir else self.output_dir / label
        output_path.mkdir(parents=True, exist_ok=True)

        results = {
            "app_name": app_info.app_name,
            "label": app_info.label,
            "bundle_id": app_info.bundle_id,
            "generated_profiles": [],
            "output_directory": str(output_path),
        }

        # Generate PPPC profile if required
        if app_info.requires_pppc:
            pppc_profile = self._generate_pppc_profile(app_info, output_path)
            if pppc_profile:
                results["generated_profiles"].append(pppc_profile)

        # Generate preferences profile if required
        if app_info.requires_preferences:
            prefs_profile = self._generate_preferences_profile(app_info, output_path)
            if prefs_profile:
                results["generated_profiles"].append(prefs_profile)

        # Generate combined profile
        combined_profile = self._generate_combined_profile(app_info, output_path)
        if combined_profile:
            results["generated_profiles"].append(combined_profile)

        return results

    def _generate_pppc_profile(
        self, app_info: AppProfileInfo, output_path: Path
    ) -> Optional[Dict[str, Any]]:
        """Generate PPPC profile for an app"""
        try:
            profile_name = f"{app_info.app_name} PPPC"
            profile_file = output_path / f"{app_info.label}_pppc.mobileconfig"

            # Create PPPC profile structure
            profile = {
                "PayloadContent": [
                    {
                        "PayloadType": "com.apple.TCC.configuration-profile-policy",
                        "PayloadIdentifier": f"com.jamf.pppc.{app_info.bundle_id}",
                        "PayloadUUID": str(uuid.uuid4()),
                        "PayloadVersion": 1,
                        "Services": {},
                    }
                ],
                "PayloadDescription": f"PPPC profile for {app_info.app_name}",
                "PayloadDisplayName": profile_name,
                "PayloadIdentifier": f"com.jamf.pppc.{app_info.bundle_id}",
                "PayloadOrganization": "JAMF Pro",
                "PayloadType": "Configuration",
                "PayloadUUID": str(uuid.uuid4()),
                "PayloadVersion": 1,
            }

            # Add TCC services for each permission
            for permission in app_info.pppc_permissions:
                profile["PayloadContent"][0]["Services"][permission] = {
                    "Allowed": True,
                    "Authorization": "Allow",
                    "CodeRequirement": f'identifier "{app_info.bundle_id}" and anchor apple',
                    "Identifier": app_info.bundle_id,
                    "IdentifierType": "bundleID",
                }

            # Write profile to file
            with open(profile_file, "w") as f:
                json.dump(profile, f, indent=2)

            return {
                "type": "PPPC",
                "name": profile_name,
                "file": str(profile_file),
                "permissions": app_info.pppc_permissions,
            }

        except Exception as e:
            print(f"Error generating PPPC profile for {app_info.app_name}: {e}")
            return None

    def _generate_preferences_profile(
        self, app_info: AppProfileInfo, output_path: Path
    ) -> Optional[Dict[str, Any]]:
        """Generate preferences profile for an app"""
        try:
            profile_name = f"{app_info.app_name} Preferences"
            profile_file = output_path / f"{app_info.label}_preferences.mobileconfig"

            # Create preferences profile structure
            profile = {
                "PayloadContent": [],
                "PayloadDescription": f"Preferences profile for {app_info.app_name}",
                "PayloadDisplayName": profile_name,
                "PayloadIdentifier": f"com.jamf.preferences.{app_info.bundle_id}",
                "PayloadOrganization": "JAMF Pro",
                "PayloadType": "Configuration",
                "PayloadUUID": str(uuid.uuid4()),
                "PayloadVersion": 1,
            }

            # Add preference payloads for each domain
            for domain in app_info.preference_domains:
                payload = {
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadIdentifier": f"com.jamf.preferences.{domain}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadVersion": 1,
                    "PayloadEnabled": True,
                    "Forced": [
                        {
                            "mcx_preference_settings": {
                                # Add common preferences based on app type
                                "AutoUpdate": True,
                                "DisableAutoUpdate": False,
                                "CheckForUpdates": True,
                            }
                        }
                    ],
                }

                # Add app-specific preferences
                if "adobe" in app_info.label.lower():
                    payload["Forced"][0]["mcx_preference_settings"].update(
                        {
                            "AutoUpdate": True,
                            "DisableAutoUpdate": False,
                            "CheckForUpdates": True,
                            "EnableCrashReporting": False,
                            "EnableUsageReporting": False,
                        }
                    )
                elif "microsoft" in app_info.label.lower():
                    payload["Forced"][0]["mcx_preference_settings"].update(
                        {
                            "AutoUpdate": True,
                            "DisableAutoUpdate": False,
                            "CheckForUpdates": True,
                            "EnableTelemetry": False,
                        }
                    )
                elif "google" in app_info.label.lower():
                    payload["Forced"][0]["mcx_preference_settings"].update(
                        {
                            "AutoUpdate": True,
                            "DisableAutoUpdate": False,
                            "CheckForUpdates": True,
                            "EnableCrashReporting": False,
                        }
                    )

                profile["PayloadContent"].append(payload)

            # Write profile to file
            with open(profile_file, "w") as f:
                json.dump(profile, f, indent=2)

            return {
                "type": "Preferences",
                "name": profile_name,
                "file": str(profile_file),
                "domains": app_info.preference_domains,
            }

        except Exception as e:
            print(f"Error generating preferences profile for {app_info.app_name}: {e}")
            return None

    def _generate_combined_profile(
        self, app_info: AppProfileInfo, output_path: Path
    ) -> Optional[Dict[str, Any]]:
        """Generate a combined profile with both PPPC and preferences"""
        try:
            profile_name = f"{app_info.app_name} Complete"
            profile_file = output_path / f"{app_info.label}_complete.mobileconfig"

            # Create combined profile structure
            profile = {
                "PayloadContent": [],
                "PayloadDescription": f"Complete profile for {app_info.app_name} (PPPC + Preferences)",
                "PayloadDisplayName": profile_name,
                "PayloadIdentifier": f"com.jamf.complete.{app_info.bundle_id}",
                "PayloadOrganization": "JAMF Pro",
                "PayloadType": "Configuration",
                "PayloadUUID": str(uuid.uuid4()),
                "PayloadVersion": 1,
            }

            # Add PPPC payload if required
            if app_info.requires_pppc:
                pppc_payload = {
                    "PayloadType": "com.apple.TCC.configuration-profile-policy",
                    "PayloadIdentifier": f"com.jamf.pppc.{app_info.bundle_id}",
                    "PayloadUUID": str(uuid.uuid4()),
                    "PayloadVersion": 1,
                    "Services": {},
                }

                for permission in app_info.pppc_permissions:
                    pppc_payload["Services"][permission] = {
                        "Allowed": True,
                        "Authorization": "Allow",
                        "CodeRequirement": f'identifier "{app_info.bundle_id}" and anchor apple',
                        "Identifier": app_info.bundle_id,
                        "IdentifierType": "bundleID",
                    }

                profile["PayloadContent"].append(pppc_payload)

            # Add preferences payloads if required
            if app_info.requires_preferences:
                for domain in app_info.preference_domains:
                    payload = {
                        "PayloadType": "com.apple.ManagedClient.preferences",
                        "PayloadIdentifier": f"com.jamf.preferences.{domain}",
                        "PayloadUUID": str(uuid.uuid4()),
                        "PayloadVersion": 1,
                        "PayloadEnabled": True,
                        "Forced": [
                            {
                                "mcx_preference_settings": {
                                    "AutoUpdate": True,
                                    "DisableAutoUpdate": False,
                                    "CheckForUpdates": True,
                                }
                            }
                        ],
                    }
                    profile["PayloadContent"].append(payload)

            # Write profile to file
            with open(profile_file, "w") as f:
                json.dump(profile, f, indent=2)

            return {
                "type": "Combined",
                "name": profile_name,
                "file": str(profile_file),
                "includes_pppc": app_info.requires_pppc,
                "includes_preferences": app_info.requires_preferences,
            }

        except Exception as e:
            print(f"Error generating combined profile for {app_info.app_name}: {e}")
            return None

    def list_supported_apps(self) -> List[AppProfileInfo]:
        """List all apps that have profile mappings"""
        return list(self.app_profiles.values())

    def get_app_profile_info(self, label: str) -> Optional[AppProfileInfo]:
        """Get profile information for a specific app"""
        return self.app_profiles.get(label)

    def add_app_profile_mapping(self, app_info: AppProfileInfo):
        """Add a new app profile mapping"""
        self.app_profiles[app_info.label] = app_info

    def generate_all_profiles(self, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Generate profiles for all supported apps"""
        results = {
            "total_apps": len(self.app_profiles),
            "generated_profiles": [],
            "output_directory": str(self.output_dir),
        }

        for label, app_info in self.app_profiles.items():
            try:
                app_results = self.generate_profiles_for_app(label, output_dir)
                results["generated_profiles"].append(app_results)
            except Exception as e:
                print(f"Error generating profiles for {label}: {e}")

        return results
