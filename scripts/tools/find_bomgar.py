#!/usr/bin/env python3
"""
Bomgar/BeyondTrust Remote Support Finder Tool

This script searches for Bomgar BeyondTrust Remote Support installations
on macOS systems and provides detailed information about the installation.

Author: Generated for IT Administration
Version: 1.0
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BomgarFinder:
    """Finds and analyzes Bomgar/BeyondTrust Remote Support installations."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.installations = []
        self.running_processes = []

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

    def find_application_installations(self) -> List[Dict]:
        """Find Bomgar/BeyondTrust applications in common locations."""
        installations = []
        search_paths = [
            "/Applications",
            "/Applications/Utilities",
            "/System/Applications",
            "/System/Applications/Utilities",
        ]

        self.log("Searching for Bomgar/BeyondTrust applications...")

        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue

            # Search for Bomgar/BeyondTrust related apps
            patterns = ["*Bomgar*", "*Beyond*", "*Remote*", "*.com.bomgar.*"]

            for pattern in patterns:
                cmd = f'find "{search_path}" -name "{pattern}" -type d 2>/dev/null'
                exit_code, stdout, stderr = self.run_command(cmd)

                if exit_code == 0 and stdout.strip():
                    for line in stdout.strip().split("\n"):
                        if line and os.path.exists(line):
                            app_info = self.analyze_application(line)
                            if app_info:
                                installations.append(app_info)

        return installations

    def analyze_application(self, app_path: str) -> Optional[Dict]:
        """Analyze a potential Bomgar/BeyondTrust application."""
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
        }

        try:
            # Get file stats
            stat = os.stat(app_path)
            app_info["size"] = stat.st_size
            app_info["modified"] = stat.st_mtime

            # Check if it's an app bundle
            if app_path.endswith(".app"):
                app_info["type"] = "app_bundle"
                info_plist = os.path.join(app_path, "Contents", "Info.plist")

                if os.path.exists(info_plist):
                    # Try to extract bundle info
                    cmd = f'plutil -p "{info_plist}" 2>/dev/null'
                    exit_code, stdout, stderr = self.run_command(cmd)

                    if exit_code == 0:
                        # Extract key information from plist
                        if "CFBundleIdentifier" in stdout:
                            for line in stdout.split("\n"):
                                if "CFBundleIdentifier" in line:
                                    app_info["bundle_id"] = (
                                        line.split('"')[1] if '"' in line else None
                                    )
                                    break

                        if "CFBundleShortVersionString" in stdout:
                            for line in stdout.split("\n"):
                                if "CFBundleShortVersionString" in line:
                                    app_info["version"] = (
                                        line.split('"')[1] if '"' in line else None
                                    )
                                    break

                # Find executable
                macos_dir = os.path.join(app_path, "Contents", "MacOS")
                if os.path.exists(macos_dir):
                    executables = [
                        f
                        for f in os.listdir(macos_dir)
                        if os.path.isfile(os.path.join(macos_dir, f))
                    ]
                    if executables:
                        app_info["executable"] = os.path.join(macos_dir, executables[0])

            # Determine if this is likely a Bomgar/BeyondTrust installation
            is_bomgar = any(
                keyword in app_path.lower()
                for keyword in ["bomgar", "beyond", "remote", "support", "scc"]
            )

            if is_bomgar:
                app_info["confirmed"] = True
                return app_info
            else:
                # Check contents for Bomgar indicators
                if self.check_for_bomgar_indicators(app_path):
                    app_info["confirmed"] = True
                    return app_info

        except Exception as e:
            self.log(f"Error analyzing {app_path}: {e}")

        return None

    def check_for_bomgar_indicators(self, path: str) -> bool:
        """Check if a path contains indicators of Bomgar/BeyondTrust installation."""
        indicators = [
            "sdcust",
            "bomgar",
            "beyondtrust",
            "remote support",
            "com.bomgar",
            "bomgar-ps",
        ]

        try:
            # Search for indicators in the directory
            for root, dirs, files in os.walk(path):
                for file in files:
                    if any(indicator in file.lower() for indicator in indicators):
                        return True
                for dir_name in dirs:
                    if any(indicator in dir_name.lower() for indicator in indicators):
                        return True
        except Exception:
            pass

        return False

    def find_system_files(self) -> List[Dict]:
        """Find Bomgar/BeyondTrust system files and configurations."""
        system_files = []
        search_locations = [
            "/Library/BeyondTrust",
            "/Library/LaunchDaemons",
            "/Library/LaunchAgents",
            "/usr/local/bin",
            "/opt",
        ]

        self.log("Searching for system files...")

        for location in search_locations:
            if not os.path.exists(location):
                continue

            cmd = f'find "{location}" -name "*bomgar*" -o -name "*beyond*" 2>/dev/null'
            exit_code, stdout, stderr = self.run_command(cmd)

            if exit_code == 0 and stdout.strip():
                for line in stdout.strip().split("\n"):
                    if line and os.path.exists(line):
                        file_info = {
                            "path": line,
                            "type": "system_file",
                            "size": (
                                os.path.getsize(line) if os.path.isfile(line) else 0
                            ),
                            "modified": (
                                os.path.getmtime(line) if os.path.isfile(line) else 0
                            ),
                        }
                        system_files.append(file_info)

        return system_files

    def find_running_processes(self) -> List[Dict]:
        """Find running Bomgar/BeyondTrust processes."""
        self.log("Checking for running processes...")

        cmd = "ps aux | grep -i bomgar | grep -v grep"
        exit_code, stdout, stderr = self.run_command(cmd)

        processes = []
        if exit_code == 0 and stdout.strip():
            for line in stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 11:
                        process_info = {
                            "user": parts[0],
                            "pid": parts[1],
                            "cpu": parts[2],
                            "mem": parts[3],
                            "command": " ".join(parts[10:]),
                        }
                        processes.append(process_info)

        return processes

    def find_launch_services(self) -> List[Dict]:
        """Find Bomgar/BeyondTrust launch services."""
        self.log("Checking launch services...")

        services = []

        # Check LaunchDaemons
        cmd = "launchctl list | grep -i bomgar"
        exit_code, stdout, stderr = self.run_command(cmd)

        if exit_code == 0 and stdout.strip():
            for line in stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        service_info = {
                            "label": parts[2],
                            "pid": parts[0] if parts[0] != "-" else None,
                            "status": parts[1],
                            "type": "launch_daemon",
                        }
                        services.append(service_info)

        return services

    def generate_report(self, output_format: str = "text") -> str:
        """Generate a comprehensive report of findings."""
        self.log("Generating report...")

        # Gather all information
        installations = self.find_application_installations()
        system_files = self.find_system_files()
        processes = self.find_running_processes()
        services = self.find_launch_services()

        if output_format == "json":
            report = {
                "installations": installations,
                "system_files": system_files,
                "running_processes": processes,
                "launch_services": services,
                "summary": {
                    "total_installations": len(installations),
                    "total_system_files": len(system_files),
                    "total_processes": len(processes),
                    "total_services": len(services),
                },
            }
            return json.dumps(report, indent=2)

        else:  # text format
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("BOMGAR/BEYONDTRUST REMOTE SUPPORT FINDER REPORT")
            report_lines.append("=" * 60)
            report_lines.append("")

            # Installations
            report_lines.append(f"APPLICATIONS FOUND: {len(installations)}")
            report_lines.append("-" * 40)
            if installations:
                for app in installations:
                    report_lines.append(f"Path: {app['path']}")
                    report_lines.append(f"Name: {app['name']}")
                    report_lines.append(f"Type: {app['type']}")
                    if app.get("version"):
                        report_lines.append(f"Version: {app['version']}")
                    if app.get("bundle_id"):
                        report_lines.append(f"Bundle ID: {app['bundle_id']}")
                    if app.get("executable"):
                        report_lines.append(f"Executable: {app['executable']}")
                    report_lines.append(f"Size: {app['size']:,} bytes")
                    report_lines.append("")
            else:
                report_lines.append("No applications found.")
                report_lines.append("")

            # System Files
            report_lines.append(f"SYSTEM FILES FOUND: {len(system_files)}")
            report_lines.append("-" * 40)
            if system_files:
                for file_info in system_files:
                    report_lines.append(f"Path: {file_info['path']}")
                    report_lines.append(f"Size: {file_info['size']:,} bytes")
                    report_lines.append("")
            else:
                report_lines.append("No system files found.")
                report_lines.append("")

            # Running Processes
            report_lines.append(f"RUNNING PROCESSES: {len(processes)}")
            report_lines.append("-" * 40)
            if processes:
                for proc in processes:
                    report_lines.append(
                        f"PID: {proc['pid']} | User: {proc['user']} | CPU: {proc['cpu']}% | Mem: {proc['mem']}%"
                    )
                    report_lines.append(f"Command: {proc['command']}")
                    report_lines.append("")
            else:
                report_lines.append("No Bomgar/BeyondTrust processes running.")
                report_lines.append("")

            # Launch Services
            report_lines.append(f"LAUNCH SERVICES: {len(services)}")
            report_lines.append("-" * 40)
            if services:
                for service in services:
                    report_lines.append(f"Label: {service['label']}")
                    report_lines.append(f"PID: {service['pid'] or 'N/A'}")
                    report_lines.append(f"Status: {service['status']}")
                    report_lines.append(f"Type: {service['type']}")
                    report_lines.append("")
            else:
                report_lines.append("No Bomgar/BeyondTrust launch services found.")
                report_lines.append("")

            # Summary
            report_lines.append("SUMMARY")
            report_lines.append("-" * 40)
            report_lines.append(f"Total Applications: {len(installations)}")
            report_lines.append(f"Total System Files: {len(system_files)}")
            report_lines.append(f"Running Processes: {len(processes)}")
            report_lines.append(f"Launch Services: {len(services)}")

            if installations or system_files or processes or services:
                report_lines.append(
                    "\nBomgar/BeyondTrust Remote Support is installed on this system."
                )
            else:
                report_lines.append(
                    "\nNo Bomgar/BeyondTrust Remote Support installation detected."
                )

            return "\n".join(report_lines)

    def run(
        self, output_format: str = "text", output_file: Optional[str] = None
    ) -> None:
        """Run the Bomgar finder and output results."""
        try:
            report = self.generate_report(output_format)

            if output_file:
                with open(output_file, "w") as f:
                    f.write(report)
                print(f"Report saved to: {output_file}")
            else:
                print(report)

        except Exception as e:
            print(f"Error generating report: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Find Bomgar/BeyondTrust Remote Support installations on macOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Basic scan with text output
  %(prog)s -v                       # Verbose output with debug info
  %(prog)s -f json -o report.json   # JSON output to file
  %(prog)s -f text -o report.txt    # Text output to file
        """,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output with debug information",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")

    args = parser.parse_args()

    # Check if running on macOS
    if sys.platform != "darwin":
        print("Error: This tool is designed for macOS systems only.", file=sys.stderr)
        sys.exit(1)

    # Create and run the finder
    finder = BomgarFinder(verbose=args.verbose)
    finder.run(output_format=args.format, output_file=args.output)


if __name__ == "__main__":
    main()
