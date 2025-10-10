#!/usr/bin/env python3
"""
General-Purpose Application Finder Tool for macOS

This script searches for applications on macOS systems with flexible
search patterns and comprehensive analysis capabilities.

Author: Generated for IT Administration
Version: 1.0
"""

import os
import sys
import subprocess
import json
import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime


class AppFinder:
    """Finds and analyzes applications on macOS systems."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.apps_found = []

    def log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[DEBUG] {message}")

    def run_command(self, command: str) -> Tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def find_applications(
        self,
        search_pattern: str = "*",
        search_paths: Optional[List[str]] = None,
        case_sensitive: bool = False,
        exact_match: bool = False,
    ) -> List[Dict]:
        """Find applications matching the search pattern."""
        if search_paths is None:
            search_paths = [
                "/Applications",
                "/Applications/Utilities",
                "/System/Applications",
                "/System/Applications/Utilities",
                "/System/Library/CoreServices",
                "/usr/local/bin",
                "/opt",
            ]

        self.log(f"Searching for applications matching pattern: {search_pattern}")
        self.log(f"Search paths: {search_paths}")

        apps_found = []
        case_flag = "" if case_sensitive else "-i"

        for search_path in search_paths:
            if not os.path.exists(search_path):
                self.log(f"Path does not exist: {search_path}")
                continue

            # Search for applications
            if exact_match:
                # Exact name match
                cmd = f'find "{search_path}" -name "{search_pattern}" -type d 2>/dev/null'
            else:
                # Pattern match
                cmd = f'find "{search_path}" -iname "*{search_pattern}*" -type d 2>/dev/null'

            exit_code, stdout, stderr = self.run_command(cmd)

            if exit_code == 0 and stdout.strip():
                for line in stdout.strip().split("\n"):
                    if line and os.path.exists(line):
                        app_info = self.analyze_application(line)
                        if app_info:
                            apps_found.append(app_info)

        return apps_found

    def analyze_application(self, app_path: str) -> Optional[Dict]:
        """Analyze an application and extract detailed information."""
        if not os.path.exists(app_path):
            return None

        app_info = {
            "path": app_path,
            "name": os.path.basename(app_path),
            "type": "unknown",
            "version": None,
            "bundle_id": None,
            "executable": None,
            "size": 0,
            "modified": None,
            "created": None,
            "permissions": None,
            "is_running": False,
            "architecture": None,
            "minimum_os_version": None,
            "category": None,
        }

        try:
            # Get file stats
            stat = os.stat(app_path)
            app_info["size"] = stat.st_size
            app_info["modified"] = stat.st_mtime
            app_info["created"] = stat.st_ctime
            app_info["permissions"] = oct(stat.st_mode)[-3:]

            # Check if it's an app bundle
            if app_path.endswith(".app"):
                app_info["type"] = "app_bundle"
                app_info.update(self.analyze_app_bundle(app_path))
            elif app_path.endswith(".appex"):
                app_info["type"] = "app_extension"
                app_info.update(self.analyze_app_bundle(app_path))
            elif os.path.isfile(app_path) and os.access(app_path, os.X_OK):
                app_info["type"] = "executable"
                app_info["executable"] = app_path
                app_info.update(self.analyze_executable(app_path))
            else:
                app_info["type"] = "directory"

            # Check if running
            app_info["is_running"] = self.check_if_running(app_path)

        except Exception as e:
            self.log(f"Error analyzing {app_path}: {e}")

        return app_info

    def analyze_app_bundle(self, app_path: str) -> Dict:
        """Analyze an app bundle and extract information."""
        info = {}
        info_plist = os.path.join(app_path, "Contents", "Info.plist")

        if os.path.exists(info_plist):
            # Extract bundle information
            bundle_info = self.extract_plist_info(info_plist)
            info.update(bundle_info)

        # Find executable
        macos_dir = os.path.join(app_path, "Contents", "MacOS")
        if os.path.exists(macos_dir):
            executables = [
                f
                for f in os.listdir(macos_dir)
                if os.path.isfile(os.path.join(macos_dir, f))
            ]
            if executables:
                executable_path = os.path.join(macos_dir, executables[0])
                info["executable"] = executable_path
                info.update(self.analyze_executable(executable_path))

        return info

    def extract_plist_info(self, plist_path: str) -> Dict:
        """Extract information from Info.plist file."""
        info = {}

        try:
            cmd = f'plutil -p "{plist_path}" 2>/dev/null'
            exit_code, stdout, stderr = self.run_command(cmd)

            if exit_code == 0:
                # Extract key information
                plist_data = self.parse_plist_output(stdout)
                info.update(plist_data)

        except Exception as e:
            self.log(f"Error extracting plist info: {e}")

        return info

    def parse_plist_output(self, plist_output: str) -> Dict:
        """Parse plutil output and extract key information."""
        info = {}

        # Common keys to extract
        keys_to_extract = {
            "CFBundleIdentifier": "bundle_id",
            "CFBundleShortVersionString": "version",
            "CFBundleVersion": "build_version",
            "CFBundleName": "display_name",
            "CFBundleDisplayName": "display_name",
            "CFBundleExecutable": "executable_name",
            "CFBundlePackageType": "package_type",
            "LSMinimumSystemVersion": "minimum_os_version",
            "LSApplicationCategoryType": "category",
            "CFBundleGetInfoString": "description",
        }

        for line in plist_output.split("\n"):
            for plist_key, info_key in keys_to_extract.items():
                if plist_key in line and "=>" in line:
                    # Extract value from plist line
                    value = line.split("=>")[-1].strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    info[info_key] = value
                    break

        return info

    def analyze_executable(self, executable_path: str) -> Dict:
        """Analyze an executable file."""
        info = {}

        try:
            # Get architecture information
            cmd = f'file "{executable_path}"'
            exit_code, stdout, stderr = self.run_command(cmd)
            if exit_code == 0:
                if "universal binary" in stdout.lower():
                    info["architecture"] = "universal"
                elif "x86_64" in stdout:
                    info["architecture"] = "x86_64"
                elif "arm64" in stdout:
                    info["architecture"] = "arm64"
                elif "i386" in stdout:
                    info["architecture"] = "i386"

        except Exception as e:
            self.log(f"Error analyzing executable {executable_path}: {e}")

        return info

    def check_if_running(self, app_path: str) -> bool:
        """Check if an application is currently running."""
        try:
            # Get the app name without .app extension
            app_name = os.path.basename(app_path)
            if app_name.endswith(".app"):
                app_name = app_name[:-4]

            # Check if process is running
            cmd = f'pgrep -f "{app_name}"'
            exit_code, stdout, stderr = self.run_command(cmd)
            return exit_code == 0 and stdout.strip() != ""

        except Exception:
            return False

    def filter_apps(
        self,
        apps: List[Dict],
        name_filter: Optional[str] = None,
        bundle_id_filter: Optional[str] = None,
        version_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        running_only: bool = False,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
    ) -> List[Dict]:
        """Filter applications based on criteria."""
        filtered_apps = apps

        if name_filter:
            filtered_apps = [
                app
                for app in filtered_apps
                if name_filter.lower() in app.get("name", "").lower()
            ]

        if bundle_id_filter:
            filtered_apps = [
                app
                for app in filtered_apps
                if bundle_id_filter.lower() in app.get("bundle_id", "").lower()
            ]

        if version_filter:
            filtered_apps = [
                app
                for app in filtered_apps
                if version_filter in app.get("version", "")
            ]

        if type_filter:
            filtered_apps = [
                app for app in filtered_apps if app.get("type") == type_filter
            ]

        if running_only:
            filtered_apps = [app for app in filtered_apps if app.get("is_running")]

        if min_size is not None:
            filtered_apps = [
                app for app in filtered_apps if app.get("size", 0) >= min_size
            ]

        if max_size is not None:
            filtered_apps = [
                app for app in filtered_apps if app.get("size", 0) <= max_size
            ]

        return filtered_apps

    def generate_report(
        self,
        apps: List[Dict],
        output_format: str = "text",
        include_details: bool = True,
    ) -> str:
        """Generate a report of found applications."""
        self.log("Generating report...")

        if output_format == "json":
            return json.dumps(apps, indent=2)

        elif output_format == "csv":
            if not apps:
                return "No applications found"
            
            # Create CSV output
            output = []
            fieldnames = [
                "name", "path", "type", "version", "bundle_id", 
                "size", "is_running", "architecture"
            ]
            
            output.append(",".join(fieldnames))
            
            for app in apps:
                row = []
                for field in fieldnames:
                    value = str(app.get(field, ""))
                    # Escape commas and quotes in CSV
                    if "," in value or '"' in value:
                        value = f'"{value.replace('"', '""')}"'
                    row.append(value)
                output.append(",".join(row))
            
            return "\n".join(output)

        else:  # text format
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("APPLICATION FINDER REPORT")
            report_lines.append("=" * 80)
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Applications Found: {len(apps)}")
            report_lines.append("")

            if not apps:
                report_lines.append("No applications found matching the search criteria.")
                return "\n".join(report_lines)

            # Group by type
            by_type = {}
            for app in apps:
                app_type = app.get("type", "unknown")
                if app_type not in by_type:
                    by_type[app_type] = []
                by_type[app_type].append(app)

            for app_type, type_apps in by_type.items():
                report_lines.append(f"{app_type.upper().replace('_', ' ')} APPLICATIONS ({len(type_apps)})")
                report_lines.append("-" * 60)

                for app in type_apps:
                    report_lines.append(f"Name: {app.get('name', 'Unknown')}")
                    report_lines.append(f"Path: {app.get('path', 'Unknown')}")
                    
                    if include_details:
                        if app.get("version"):
                            report_lines.append(f"Version: {app['version']}")
                        if app.get("bundle_id"):
                            report_lines.append(f"Bundle ID: {app['bundle_id']}")
                        if app.get("executable"):
                            report_lines.append(f"Executable: {app['executable']}")
                        if app.get("size"):
                            report_lines.append(f"Size: {app['size']:,} bytes")
                        if app.get("architecture"):
                            report_lines.append(f"Architecture: {app['architecture']}")
                        if app.get("is_running"):
                            report_lines.append("Status: Running")
                        else:
                            report_lines.append("Status: Not Running")
                    
                    report_lines.append("")

            # Summary
            report_lines.append("SUMMARY")
            report_lines.append("-" * 40)
            running_count = sum(1 for app in apps if app.get("is_running"))
            total_size = sum(app.get("size", 0) for app in apps)
            
            report_lines.append(f"Total Applications: {len(apps)}")
            report_lines.append(f"Running Applications: {running_count}")
            report_lines.append(f"Total Size: {total_size:,} bytes ({total_size / (1024*1024):.1f} MB)")
            
            return "\n".join(report_lines)

    def run(
        self,
        search_pattern: str = "*",
        search_paths: Optional[List[str]] = None,
        output_format: str = "text",
        output_file: Optional[str] = None,
        include_details: bool = True,
        **filters,
    ) -> None:
        """Run the application finder."""
        try:
            # Find applications
            apps = self.find_applications(search_pattern, search_paths)
            
            # Apply filters
            if filters:
                apps = self.filter_apps(apps, **filters)
            
            # Generate report
            report = self.generate_report(apps, output_format, include_details)
            
            if output_file:
                with open(output_file, "w") as f:
                    f.write(report)
                print(f"Report saved to: {output_file}")
            else:
                print(report)

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Find applications on macOS systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Find all applications
  %(prog)s -p "Chrome"                        # Find Chrome applications
  %(prog)s -p "*.app" -f json                 # Find all .app bundles in JSON
  %(prog)s -p "Remote" --running-only         # Find running Remote applications
  %(prog)s --bundle-id "com.apple"            # Find Apple applications
  %(prog)s --type "app_bundle" --min-size 1000000  # Find large app bundles
  %(prog)s -p "Support" -o report.txt         # Save report to file
        """,
    )

    parser.add_argument(
        "-p", "--pattern", default="*", help="Search pattern (default: *)"
    )
    parser.add_argument(
        "-s", "--search-paths", nargs="+", help="Additional search paths"
    )
    parser.add_argument(
        "-f", "--format", choices=["text", "json", "csv"], default="text",
        help="Output format (default: text)"
    )
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument(
        "--no-details", action="store_true", help="Exclude detailed information"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Filter options
    parser.add_argument("--name", help="Filter by application name")
    parser.add_argument("--bundle-id", help="Filter by bundle identifier")
    parser.add_argument("--version", help="Filter by version")
    parser.add_argument("--type", help="Filter by application type")
    parser.add_argument("--running-only", action="store_true", help="Show only running apps")
    parser.add_argument("--min-size", type=int, help="Minimum size in bytes")
    parser.add_argument("--max-size", type=int, help="Maximum size in bytes")

    args = parser.parse_args()

    # Check if running on macOS
    if sys.platform != "darwin":
        print("Error: This tool is designed for macOS systems only.", file=sys.stderr)
        sys.exit(1)

    # Prepare search paths
    search_paths = [
        "/Applications",
        "/Applications/Utilities",
        "/System/Applications",
        "/System/Applications/Utilities",
        "/System/Library/CoreServices",
    ]
    if args.search_paths:
        search_paths.extend(args.search_paths)

    # Prepare filters
    filters = {}
    if args.name:
        filters["name_filter"] = args.name
    if args.bundle_id:
        filters["bundle_id_filter"] = args.bundle_id
    if args.version:
        filters["version_filter"] = args.version
    if args.type:
        filters["type_filter"] = args.type
    if args.running_only:
        filters["running_only"] = True
    if args.min_size:
        filters["min_size"] = args.min_size
    if args.max_size:
        filters["max_size"] = args.max_size

    # Create and run the finder
    finder = AppFinder(verbose=args.verbose)
    finder.run(
        search_pattern=args.pattern,
        search_paths=search_paths,
        output_format=args.format,
        output_file=args.output,
        include_details=not args.no_details,
        **filters,
    )


if __name__ == "__main__":
    main()
