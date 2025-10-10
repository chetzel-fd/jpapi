#!/usr/bin/env python3
"""
Package Export Handler for jpapi CLI
Handles export of JAMF packages using the v1 API endpoints
"""

from typing import Dict, Any, List, Optional
from argparse import Namespace
from .export_base import ExportBase
import json
from lib.utils import create_jamf_hyperlink
from lib.exports.manage_exports import get_export_directory
from core.logging.command_mixin import log_operation


class ExportPackages(ExportBase):
    """Handler for exporting JAMF packages"""

    def __init__(self, auth):
        super().__init__(auth, "packages")
        self.endpoint = "/api/v1/packages"
        self.detail_endpoint = "/api/v1/packages"
        self.environment = "dev"  # Default environment

    @log_operation("Package Data Fetch")
    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch package data from JAMF API with pagination"""
        all_packages = []
        page = 0
        page_size = 100

        self.log_info("Starting package data fetch from JAMF API")

        while True:
            url = f"{self.endpoint}?page={page}&page-size={page_size}&sort=id"
            self.log_info(f"Fetching page {page + 1}...")

            try:
                response = self.auth.api_request("GET", url)
                if "results" in response:
                    packages = response["results"]
                    if not packages:
                        self.log_info("No more packages found, pagination complete")
                        break

                    all_packages.extend(packages)
                    self.log_success(
                        f"Found {len(packages)} packages on page {page + 1} "
                        f"(Total: {len(all_packages)})"
                    )

                    if len(packages) < page_size:
                        self.log_info("Last page reached")
                        break
                    page += 1
                else:
                    self.log_warning("No results in response, stopping pagination")
                    break
            except Exception as e:
                self.log_error(f"Error fetching page {page + 1}", e)
                break

        self.log_success(
            f"Package fetch complete: {len(all_packages)} total packages retrieved"
        )
        return all_packages

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format package data for export"""
        export_data = []
        downloaded_files = []

        self.log_info(f"Starting data formatting for {len(data)} packages")

        # Apply filtering if specified
        if hasattr(args, "filter") and args.filter:
            from lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(data)

            # Try filtering by ID first, then by name if no matches
            id_filtered = filter_obj.filter_objects(data, "id", args.filter)
            if id_filtered:
                data = id_filtered
                self.log_info(
                    f"Filtered by ID from {original_count} to {len(data)} packages"
                )
            else:
                data = filter_obj.filter_objects(data, "name", args.filter)
                self.log_info(
                    f"Filtered by name from {original_count} to {len(data)} packages"
                )

        # Use progress tracker for package processing
        with self.progress_tracker(len(data), "Processing packages") as tracker:
            for i, package in enumerate(data):
                # Get package name for progress display
                package_name = (
                    package.get("packageName")
                    or package.get("fileName")
                    or f"Package-{package.get('id', i+1)}"
                )
                self.log_progress(i + 1, len(data), package_name, "Processing package")

                # Get detailed package info if requested
                detailed_package = None
                if getattr(args, "detailed", False) and package.get("id"):
                    try:
                        tracker.update(
                            description=f"Fetching details for: {package_name}"
                        )
                        detailed_package = self._get_detailed_package_info(
                            package["id"]
                        )
                    except Exception as e:
                        self.log_error(
                            f"Could not get details for package {package.get('id')}", e
                        )

                # Extract basic package data
                package_data = self._extract_basic_package_data(
                    package, detailed_package, getattr(args, "env", "dev")
                )

                # Add detailed information if available
                if detailed_package:
                    detailed_data = self._extract_detailed_package_data(
                        detailed_package, args
                    )
                    package_data.update(detailed_data)

                # Download individual package files if requested
                if getattr(args, "download", False) and not getattr(
                    args, "no_download", False
                ):
                    if package.get("id"):
                        tracker.update(
                            description=f"Downloading package files: {package_name}"
                        )
                        package_files = self._download_package_files(
                            package, detailed_package, args
                        )
                        if package_files:
                            package_data.update(package_files)
                            downloaded_files.extend(
                                package_files.get("downloaded_files", [])
                            )

                export_data.append(package_data)
                self.log_info(
                    f"Added package {package_name} to export data (total: {len(export_data)})"
                )
                tracker.update()

        # Store downloaded files for summary
        if downloaded_files:
            self._downloaded_files = downloaded_files

        self.log_success(
            f"Data formatting complete: {len(export_data)} packages processed"
        )
        return export_data

    def _get_detailed_package_info(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed package information"""
        try:
            response = self.auth.api_request(
                "GET", f"{self.detail_endpoint}/{package_id}"
            )
            return response
        except Exception as e:
            self.log_error(f"Could not get detailed info for package {package_id}", e)
            return None

    def _extract_basic_package_data(
        self,
        package: Dict[str, Any],
        detailed_package: Optional[Dict[str, Any]],
        environment: str,
    ) -> Dict[str, Any]:
        """Extract basic package information"""
        return {
            "delete": "",  # Empty column for manual deletion tracking
            "ID": create_jamf_hyperlink("packages", package.get("id", ""), environment),
            "Name": package.get("packageName", ""),  # Use packageName as the main name
            "Package Name": package.get("packageName", ""),
            "Version": package.get("version", ""),
            "Category": package.get("categoryId", ""),  # Use categoryId
            "Filename": package.get("fileName", ""),  # Use fileName
            "Size": package.get("size", ""),
            "Size_MB": self._format_size_mb(package.get("size", 0)),
            "MD5": package.get("md5", ""),
            "Package File": "",  # Will be set if downloading
        }

    def _extract_detailed_package_data(
        self, detailed_package: Dict[str, Any], args: Namespace
    ) -> Dict[str, Any]:
        """Extract detailed package information"""
        detailed_data = {}

        # Add manifest information if requested
        if getattr(args, "include_manifest", False):
            manifest = detailed_package.get("manifest", {})
            if manifest:
                detailed_data.update(
                    {
                        "Manifest Name": manifest.get("name", ""),
                        "Manifest Version": manifest.get("version", ""),
                        "Manifest Size": manifest.get("size", ""),
                        "Manifest MD5": manifest.get("md5", ""),
                    }
                )

        # Add history information if requested
        if getattr(args, "include_history", False):
            history = detailed_package.get("history", [])
            if history:
                # Get the most recent history entry
                latest_history = history[0] if history else {}
                detailed_data.update(
                    {
                        "Last Modified": latest_history.get("date", ""),
                        "Last Modified By": latest_history.get("username", ""),
                        "Last Action": latest_history.get("action", ""),
                        "History Notes": latest_history.get("notes", ""),
                    }
                )

        # Add additional detailed fields
        detailed_data.update(
            {
                "Priority": detailed_package.get("priority", ""),
                "Fill User Template": detailed_package.get("fillUserTemplate", ""),
                "Fill Existing Users": detailed_package.get("fillExistingUsers", ""),
                "Boot Drive Required": detailed_package.get("bootDriveRequired", ""),
                "Allow Uninstalled": detailed_package.get("allowUninstalled", ""),
                "Reinstall Option": detailed_package.get("reinstallOption", ""),
                "OS Requirements": detailed_package.get("osRequirements", ""),
                "Required Processor": detailed_package.get("requiredProcessor", ""),
                "Switch With Package": detailed_package.get("switchWithPackage", ""),
                "Install If Reported Available": detailed_package.get(
                    "installIfReportedAvailable", ""
                ),
            }
        )

        return detailed_data

    def _download_package_files(
        self,
        package: Dict[str, Any],
        detailed_package: Optional[Dict[str, Any]],
        args: Namespace,
    ) -> Dict[str, Any]:
        """Download individual package files and manifests"""
        downloaded_files = []
        package_name = package.get("name", "Unknown")

        try:
            # Download package file if available
            if package.get("filename"):
                package_file = self._download_package_file(package)
                if package_file:
                    downloaded_files.append(package_file)

            # Download manifest if available and requested
            if getattr(args, "include_manifest", False) and detailed_package:
                manifest_file = self._download_manifest_file(package, detailed_package)
                if manifest_file:
                    downloaded_files.append(manifest_file)

            # Download history if available and requested
            if getattr(args, "include_history", False) and detailed_package:
                history_file = self._download_history_file(package, detailed_package)
                if history_file:
                    downloaded_files.append(history_file)

            return {
                "Package File": "; ".join(
                    [f for f in downloaded_files if "package" in f.lower()]
                ),
                "Manifest File": "; ".join(
                    [f for f in downloaded_files if "manifest" in f.lower()]
                ),
                "History File": "; ".join(
                    [f for f in downloaded_files if "history" in f.lower()]
                ),
                "downloaded_files": downloaded_files,
            }

        except Exception as e:
            self.log_error(f"Failed to download files for {package_name}", e)
            return {}

    def _download_package_file(self, package: Dict[str, Any]) -> Optional[str]:
        """Download individual package file"""
        try:
            package_name = package.get("name", "Unknown")
            filename = package.get("filename", "")

            if not filename:
                return None

            # Create safe filename
            safe_name = self._create_safe_filename(
                package_name,
                package.get("id", ""),
                filename.split(".")[-1] if "." in filename else "pkg",
            )

            # For now, just create a placeholder file with package info
            # In a real implementation, you'd download the actual package file
            package_info = {
                "name": package.get("name", ""),
                "filename": filename,
                "size": package.get("size", ""),
                "md5": package.get("md5", ""),
                "version": package.get("version", ""),
            }

            # Get the proper export directory for the environment
            export_dir = get_export_directory(getattr(self, "environment", "dev"))
            packages_dir = export_dir / "packages"

            self._download_file(
                json.dumps(package_info, indent=2),
                safe_name,
                str(packages_dir),
            )

            return f"{packages_dir}/{safe_name}"

        except Exception as e:
            self.log_error(
                f"Failed to download package file for {package.get('name', '')}", e
            )
            return None

    def _download_manifest_file(
        self, package: Dict[str, Any], detailed_package: Dict[str, Any]
    ) -> Optional[str]:
        """Download package manifest file"""
        try:
            manifest = detailed_package.get("manifest", {})
            if not manifest:
                return None

            package_name = package.get("name", "Unknown")
            safe_name = self._create_safe_filename(
                f"{package_name}_manifest", package.get("id", ""), "json"
            )

            # Get the proper export directory for the environment
            export_dir = get_export_directory(getattr(self, "environment", "dev"))
            packages_dir = export_dir / "packages"

            self._download_file(
                json.dumps(manifest, indent=2),
                safe_name,
                str(packages_dir),
            )

            return f"{packages_dir}/{safe_name}"

        except Exception as e:
            self.log_error(
                f"Failed to download manifest for {package.get('name', '')}", e
            )
            return None

    def _download_history_file(
        self, package: Dict[str, Any], detailed_package: Dict[str, Any]
    ) -> Optional[str]:
        """Download package history file"""
        try:
            history = detailed_package.get("history", [])
            if not history:
                return None

            package_name = package.get("name", "Unknown")
            safe_name = self._create_safe_filename(
                f"{package_name}_history", package.get("id", ""), "json"
            )

            # Get the proper export directory for the environment
            export_dir = get_export_directory(getattr(self, "environment", "dev"))
            packages_dir = export_dir / "packages"

            self._download_file(
                json.dumps(history, indent=2),
                safe_name,
                str(packages_dir),
            )

            return f"{packages_dir}/{safe_name}"

        except Exception as e:
            self.log_error(
                f"Failed to download history for {package.get('name', '')}", e
            )
            return None

    def _format_size_mb(self, size_bytes: int) -> str:
        """Format size in MB"""
        if not size_bytes:
            return ""
        try:
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        except (TypeError, ValueError):
            return ""

    def export(self, args: Namespace) -> int:
        """Override export to handle downloaded files summary"""
        # Set environment from args
        self.environment = getattr(args, "env", "dev")
        result = super().export(args)

        # Show downloaded files summary if any
        if hasattr(self, "_downloaded_files") and self._downloaded_files:
            self.log_success(f"Downloaded {len(self._downloaded_files)} package files")
            # Get the proper export directory for the environment
            export_dir = get_export_directory(getattr(self, "environment", "dev"))
            packages_dir = export_dir / "packages"
            self.log_info(f"Files saved to: {packages_dir}")
            self.log_info("Downloaded Files:")
            for file_path in self._downloaded_files[:10]:  # Show first 10
                self.log_info(f"   {file_path}")
            if len(self._downloaded_files) > 10:
                remaining = len(self._downloaded_files) - 10
                self.log_info(f"   ... and {remaining} more files")

        return result
