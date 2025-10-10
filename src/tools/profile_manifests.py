#!/usr/bin/env python3
"""
Profile Manifests Manager
Manages macOS configuration profile manifests for JAMF Pro
"""

import json
import requests
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class ManifestType(Enum):
    """Types of profile manifests"""

    APPLE = "apple"
    DEVELOPER = "developer"
    APPLICATION = "application"
    CUSTOM = "custom"


@dataclass
class ManifestInfo:
    """Information about a profile manifest"""

    bundle_id: str
    app_name: str
    description: str
    payload_type: str
    version: str
    last_updated: datetime
    manifest_url: str
    is_enterprise: bool = False
    requires_code_requirement: bool = True
    requires_bundle_id: bool = True
    category: str = ""


@dataclass
class ManifestResult:
    """Result of manifest operations"""

    success: bool
    manifest_count: int = 0
    updated_count: int = 0
    error_message: Optional[str] = None
    manifests: List[ManifestInfo] = field(default_factory=list)


class ProfileManifestManager:
    """Manager for profile manifests"""

    def __init__(
        self, config_manager=None, output_dir: str = "storage/data/manifest-data"
    ):
        self.config_manager = config_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Manifest sources
        self.manifest_sources = {
            "apple": "https://raw.githubusercontent.com/Jamf-Custom-Profile-Schemas/ProfileManifestsMirror/main/manifests/ManifestsApple/",
            "developer": "https://raw.githubusercontent.com/Jamf-Custom-Profile-Schemas/ProfileManifestsMirror/main/manifests/Developer/",
            "applications": "https://raw.githubusercontent.com/Jamf-Custom-Profile-Schemas/ProfileManifestsMirror/main/manifests/Applications/",
        }

        # Local manifest cache
        self.manifest_cache = {}

    def update_manifests(self, manifest_types: List[str] = None) -> ManifestResult:
        """Update profile manifests from remote sources"""
        if manifest_types is None:
            manifest_types = ["apple", "developer", "applications"]

        all_manifests = []
        updated_count = 0

        try:
            for manifest_type in manifest_types:
                manifests = self._fetch_manifests(manifest_type)
                if manifests:
                    all_manifests.extend(manifests)
                    updated_count += len(manifests)

            # Save manifests to local storage
            self._save_manifests(all_manifests)

            return ManifestResult(
                success=True,
                manifest_count=len(all_manifests),
                updated_count=updated_count,
                manifests=all_manifests,
            )

        except Exception as e:
            return ManifestResult(
                success=False, error_message=f"Failed to update manifests: {str(e)}"
            )

    def _fetch_manifests(self, manifest_type: str) -> List[ManifestInfo]:
        """Fetch manifests from remote source"""
        manifests = []

        try:
            # Get manifest index
            index_url = f"{self.manifest_sources[manifest_type]}index.json"
            response = requests.get(index_url, timeout=30)
            response.raise_for_status()

            index_data = response.json()

            for manifest_data in index_data.get("manifests", []):
                manifest = ManifestInfo(
                    bundle_id=manifest_data.get("bundle_id", ""),
                    app_name=manifest_data.get("app_name", ""),
                    description=manifest_data.get("description", ""),
                    payload_type=manifest_data.get("payload_type", ""),
                    version=manifest_data.get("version", "1.0"),
                    last_updated=datetime.now(),
                    manifest_url=manifest_data.get("manifest_url", ""),
                    is_enterprise=manifest_data.get("is_enterprise", False),
                    requires_code_requirement=manifest_data.get(
                        "requires_code_requirement", True
                    ),
                    requires_bundle_id=manifest_data.get("requires_bundle_id", True),
                    category=manifest_type,
                )
                manifests.append(manifest)

        except Exception as e:
            print(f"Error fetching {manifest_type} manifests: {e}")

        return manifests

    def _save_manifests(self, manifests: List[ManifestInfo]):
        """Save manifests to local storage"""
        # Group manifests by type
        grouped_manifests = {}
        for manifest in manifests:
            if manifest.category not in grouped_manifests:
                grouped_manifests[manifest.category] = []
            grouped_manifests[manifest.category].append(manifest)

        # Save each group
        for category, category_manifests in grouped_manifests.items():
            category_dir = self.output_dir / category
            category_dir.mkdir(exist_ok=True)

            # Save as JSON
            json_file = category_dir / f"{category}_manifests.json"
            manifest_data = []
            for manifest in category_manifests:
                manifest_dict = {
                    "bundle_id": manifest.bundle_id,
                    "app_name": manifest.app_name,
                    "description": manifest.description,
                    "payload_type": manifest.payload_type,
                    "version": manifest.version,
                    "last_updated": manifest.last_updated.isoformat(),
                    "manifest_url": manifest.manifest_url,
                    "is_enterprise": manifest.is_enterprise,
                    "requires_code_requirement": manifest.requires_code_requirement,
                    "requires_bundle_id": manifest.requires_bundle_id,
                }
                manifest_data.append(manifest_dict)

            with open(json_file, "w") as f:
                json.dump(manifest_data, f, indent=2)

            # Save as CSV
            csv_file = category_dir / f"{category}_manifests.csv"
            self._save_manifests_csv(category_manifests, csv_file)

    def _save_manifests_csv(self, manifests: List[ManifestInfo], output_file: Path):
        """Save manifests as CSV"""
        try:
            import csv

            with open(output_file, "w", newline="") as f:
                if manifests:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "bundle_id",
                            "app_name",
                            "description",
                            "payload_type",
                            "version",
                            "last_updated",
                            "manifest_url",
                            "is_enterprise",
                            "requires_code_requirement",
                            "requires_bundle_id",
                        ]
                    )

                    for manifest in manifests:
                        writer.writerow(
                            [
                                manifest.bundle_id,
                                manifest.app_name,
                                manifest.description,
                                manifest.payload_type,
                                manifest.version,
                                manifest.last_updated.isoformat(),
                                manifest.manifest_url,
                                manifest.is_enterprise,
                                manifest.requires_code_requirement,
                                manifest.requires_bundle_id,
                            ]
                        )
        except Exception as e:
            print(f"Error saving CSV: {e}")

    def search_manifests(
        self, search_term: str, manifest_types: List[str] = None
    ) -> List[ManifestInfo]:
        """Search for manifests matching the search term"""
        if manifest_types is None:
            manifest_types = ["apple", "developer", "applications"]

        results = []

        for manifest_type in manifest_types:
            manifest_file = (
                self.output_dir / manifest_type / f"{manifest_type}_manifests.json"
            )
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r") as f:
                        manifests_data = json.load(f)

                    for manifest_data in manifests_data:
                        if (
                            search_term.lower()
                            in manifest_data.get("app_name", "").lower()
                            or search_term.lower()
                            in manifest_data.get("bundle_id", "").lower()
                            or search_term.lower()
                            in manifest_data.get("description", "").lower()
                        ):

                            manifest = ManifestInfo(
                                bundle_id=manifest_data.get("bundle_id", ""),
                                app_name=manifest_data.get("app_name", ""),
                                description=manifest_data.get("description", ""),
                                payload_type=manifest_data.get("payload_type", ""),
                                version=manifest_data.get("version", "1.0"),
                                last_updated=datetime.fromisoformat(
                                    manifest_data.get(
                                        "last_updated", datetime.now().isoformat()
                                    )
                                ),
                                manifest_url=manifest_data.get("manifest_url", ""),
                                is_enterprise=manifest_data.get("is_enterprise", False),
                                requires_code_requirement=manifest_data.get(
                                    "requires_code_requirement", True
                                ),
                                requires_bundle_id=manifest_data.get(
                                    "requires_bundle_id", True
                                ),
                                category=manifest_type,
                            )
                            results.append(manifest)

                except Exception as e:
                    print(f"Error reading {manifest_type} manifests: {e}")

        return results

    def get_manifest_details(self, bundle_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific manifest"""
        try:
            # Search for the manifest
            manifests = self.search_manifests(bundle_id)
            if not manifests:
                return None

            # Get the first match
            manifest = manifests[0]

            # Fetch detailed manifest from URL
            if manifest.manifest_url:
                response = requests.get(manifest.manifest_url, timeout=30)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            print(f"Error getting manifest details: {e}")

        return None

    def generate_manifest_report(self, output_path: str) -> bool:
        """Generate a comprehensive manifest report"""
        try:
            report = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "output_directory": str(self.output_dir),
                },
                "manifest_summary": {},
                "manifests": [],
            }

            # Count manifests by type
            for manifest_type in ["apple", "developer", "applications"]:
                manifest_file = (
                    self.output_dir / manifest_type / f"{manifest_type}_manifests.json"
                )
                if manifest_file.exists():
                    with open(manifest_file, "r") as f:
                        manifests_data = json.load(f)
                        report["manifest_summary"][manifest_type] = len(manifests_data)
                        report["manifests"].extend(manifests_data)

            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)

            return True

        except Exception as e:
            print(f"Error generating manifest report: {e}")
            return False
