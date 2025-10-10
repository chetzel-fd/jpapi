#!/usr/bin/env python3
"""
PPPC Scanner Tool
Privacy Preferences Policy Control Scanner for macOS applications
"""

import json
import plistlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class ComplianceStatus(Enum):
    """PPPC compliance status levels"""

    COMPLIANT = "COMPLIANT"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN = "UNKNOWN"


@dataclass
class AppAnalysis:
    """Analysis results for a single application"""

    app_name: str
    bundle_id: str
    app_path: str
    compliance_status: ComplianceStatus
    required_permissions: List[str] = field(default_factory=list)
    missing_permissions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_level: str = "LOW"
    last_analyzed: datetime = field(default_factory=datetime.now)


@dataclass
class ScanResults:
    """Results from a PPPC scan"""

    scan_timestamp: datetime
    total_apps_scanned: int
    compliant_apps: int
    non_compliant_apps: int
    app_analyses: List[AppAnalysis] = field(default_factory=list)
    scan_duration: float = 0.0
    output_directory: str = ""


class PPPCScanner:
    """Privacy Preferences Policy Control Scanner"""

    def __init__(
        self,
        config_manager=None,
        output_dir: str = "storage/data/pppc-enterprise-profiles",
    ):
        self.config_manager = config_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Common application paths to scan
        self.app_paths = [
            "/Applications",
            "/System/Applications",
            "/System/Library/CoreServices",
            "/usr/local/bin",
            "/opt/homebrew/bin",
        ]

        # Known problematic permissions
        self.critical_permissions = [
            "SystemPolicyAllFiles",
            "SystemPolicyDesktopFolder",
            "SystemPolicyDocumentsFolder",
            "SystemPolicyDownloadsFolder",
            "SystemPolicyNetworkVolumes",
            "SystemPolicyRemovableVolumes",
            "SystemPolicySysAdminFiles",
        ]

    def scan_core_applications(self, additional_paths: List[str] = None) -> ScanResults:
        """Scan core applications for PPPC analysis"""
        start_time = datetime.now()

        # Combine default and additional paths
        scan_paths = self.app_paths.copy()
        if additional_paths:
            scan_paths.extend(additional_paths)

        # Find applications
        apps = self._find_applications(scan_paths)

        # Analyze each application
        analyses = []
        for app_path in apps:
            try:
                analysis = self._analyze_application(app_path)
                if analysis:
                    analyses.append(analysis)
            except Exception as e:
                print(f"⚠️  Error analyzing {app_path}: {e}")
                continue

        # Calculate statistics
        compliant_count = sum(
            1 for a in analyses if a.compliance_status == ComplianceStatus.COMPLIANT
        )
        non_compliant_count = sum(
            1 for a in analyses if a.compliance_status != ComplianceStatus.COMPLIANT
        )

        scan_duration = (datetime.now() - start_time).total_seconds()

        return ScanResults(
            scan_timestamp=start_time,
            total_apps_scanned=len(analyses),
            compliant_apps=compliant_count,
            non_compliant_apps=non_compliant_count,
            app_analyses=analyses,
            scan_duration=scan_duration,
            output_directory=str(self.output_dir),
        )

    def _find_applications(self, paths: List[str]) -> List[str]:
        """Find application bundles in specified paths"""
        apps = []

        for path in paths:
            path_obj = Path(path).resolve() if isinstance(path, str) else path
            if not path_obj.exists():
                continue

            try:
                # Find .app bundles
                for app in path_obj.rglob("*.app"):
                    if app.is_dir() and (app / "Contents" / "Info.plist").exists():
                        apps.append(str(app))
            except (PermissionError, OSError):
                continue

        return apps

    def _analyze_application(self, app_path: str) -> Optional[AppAnalysis]:
        """Analyze a single application for PPPC compliance"""
        try:
            # Get app info from Info.plist
            info_plist = Path(app_path) / "Contents" / "Info.plist"
            if not info_plist.exists():
                return None

            with open(info_plist, "rb") as f:
                plist_data = plistlib.load(f)

            app_name = plist_data.get("CFBundleName", Path(app_path).stem)
            bundle_id = plist_data.get("CFBundleIdentifier", "")

            # Check for problematic permissions
            required_permissions = self._get_required_permissions(app_path)
            missing_permissions = self._check_missing_permissions(required_permissions)

            # Determine compliance status
            compliance_status = self._determine_compliance_status(missing_permissions)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                missing_permissions, app_name
            )

            # Determine risk level
            risk_level = self._determine_risk_level(missing_permissions)

            return AppAnalysis(
                app_name=app_name,
                bundle_id=bundle_id,
                app_path=app_path,
                compliance_status=compliance_status,
                required_permissions=required_permissions,
                missing_permissions=missing_permissions,
                recommendations=recommendations,
                risk_level=risk_level,
            )

        except Exception as e:
            print(f"Error analyzing {app_path}: {e}")
            return None

    def _get_required_permissions(self, app_path: str) -> List[str]:
        """Get required permissions for an application"""
        # This is a simplified implementation
        # In a real implementation, you would analyze the app's entitlements,
        # code signatures, and behavior to determine required permissions

        permissions = []

        # Check for common permission requirements based on app type
        app_name = Path(app_path).stem.lower()

        if any(
            browser in app_name for browser in ["chrome", "firefox", "safari", "edge"]
        ):
            permissions.extend(["SystemPolicyAllFiles", "SystemPolicyDownloadsFolder"])

        if any(comm in app_name for comm in ["slack", "teams", "zoom", "discord"]):
            permissions.extend(["SystemPolicyAllFiles", "SystemPolicyDesktopFolder"])

        if any(
            office in app_name for office in ["word", "excel", "powerpoint", "office"]
        ):
            permissions.extend(["SystemPolicyAllFiles", "SystemPolicyDocumentsFolder"])

        return permissions

    def _check_missing_permissions(self, required_permissions: List[str]) -> List[str]:
        """Check which permissions are missing from current PPPC profiles"""
        # This would check against existing PPPC profiles in JAMF
        # For now, we'll simulate missing permissions
        return required_permissions  # Simplified - assume all are missing

    def _determine_compliance_status(
        self, missing_permissions: List[str]
    ) -> ComplianceStatus:
        """Determine compliance status based on missing permissions"""
        if not missing_permissions:
            return ComplianceStatus.COMPLIANT
        elif len(missing_permissions) <= 2:
            return ComplianceStatus.NEEDS_IMPROVEMENT
        else:
            return ComplianceStatus.NON_COMPLIANT

    def _generate_recommendations(
        self, missing_permissions: List[str], app_name: str
    ) -> List[str]:
        """Generate recommendations for improving compliance"""
        recommendations = []

        if missing_permissions:
            recommendations.append(f"Create PPPC profile for {app_name}")
            recommendations.append(f"Add permissions: {', '.join(missing_permissions)}")
            recommendations.append(
                "Test profile in staging environment before deployment"
            )

        return recommendations

    def _determine_risk_level(self, missing_permissions: List[str]) -> str:
        """Determine risk level based on missing permissions"""
        critical_missing = [
            p for p in missing_permissions if p in self.critical_permissions
        ]

        if critical_missing:
            return "HIGH"
        elif len(missing_permissions) > 3:
            return "MEDIUM"
        else:
            return "LOW"

    def generate_pppc_profile(self, analysis: AppAnalysis, output_path: str) -> bool:
        """Generate a PPPC profile for an application"""
        try:
            # Create PPPC profile structure
            profile = {
                "PayloadContent": [
                    {
                        "PayloadType": "com.apple.TCC.configuration-profile-policy",
                        "PayloadIdentifier": f"com.jamf.pppc.{analysis.bundle_id}",
                        "PayloadUUID": f"12345678-1234-1234-1234-{analysis.bundle_id[:12]}",
                        "PayloadVersion": 1,
                        "Services": {
                            analysis.bundle_id: {
                                "Allowed": True,
                                "Authorization": "Allow",
                            }
                        },
                    }
                ],
                "PayloadDescription": f"PPPC profile for {analysis.app_name}",
                "PayloadDisplayName": f"{analysis.app_name} PPPC",
                "PayloadIdentifier": f"com.jamf.pppc.{analysis.bundle_id}",
                "PayloadOrganization": "JAMF Pro",
                "PayloadType": "Configuration",
                "PayloadUUID": f"87654321-4321-4321-4321-{analysis.bundle_id[:12]}",
                "PayloadVersion": 1,
            }

            # Write profile to file
            with open(output_path, "w") as f:
                json.dump(profile, f, indent=2)

            return True

        except Exception as e:
            print(f"Error generating PPPC profile: {e}")
            return False

    def generate_report(self, results: ScanResults, output_path: str) -> bool:
        """Generate a comprehensive scan report"""
        try:
            report = {
                "scan_metadata": {
                    "timestamp": results.scan_timestamp.isoformat(),
                    "duration_seconds": results.scan_duration,
                    "total_apps": results.total_apps_scanned,
                    "compliant_apps": results.compliant_apps,
                    "non_compliant_apps": results.non_compliant_apps,
                },
                "applications": [],
            }

            for analysis in results.app_analyses:
                app_data = {
                    "app_name": analysis.app_name,
                    "bundle_id": analysis.bundle_id,
                    "app_path": analysis.app_path,
                    "compliance_status": analysis.compliance_status.value,
                    "required_permissions": analysis.required_permissions,
                    "missing_permissions": analysis.missing_permissions,
                    "recommendations": analysis.recommendations,
                    "risk_level": analysis.risk_level,
                    "last_analyzed": analysis.last_analyzed.isoformat(),
                }
                report["applications"].append(app_data)

            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)

            return True

        except Exception as e:
            print(f"Error generating report: {e}")
            return False
