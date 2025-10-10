#!/usr/bin/env python3
"""
PPPC CLI Command - Privacy Preferences Policy Control Scanner
"""

import click
import json
import sys
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.pppc_scanner import PPPCScanner, ScanResults

# Try to import ConfigManager, fallback to mock if not available
try:
    from core.config.config_manager import ConfigManager
except ImportError:
    # Mock ConfigManager for standalone usage
    class ConfigManager:
        def __init__(self, environment="dev"):
            self.environment = environment


@click.group()
def pppc():
    """Privacy Preferences Policy Control (PPPC) Scanner Commands"""
    pass


@pppc.command()
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Environment to use",
)
@click.option(
    "--paths", "-p", multiple=True, help="Additional paths to scan for applications"
)
@click.option("--output", "-o", help="Output directory for reports and profiles")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "csv"]),
    help="Output format",
)
def scan(
    env: str, paths: List[str], output: Optional[str], verbose: bool, output_format: str
):
    """Scan core applications for PPPC analysis"""
    console = Console()

    # Initialize scanner
    config_manager = ConfigManager(environment=env)
    output_dir = Path(output) if output else Path.cwd() / "data" / "pppc-profiles"
    output_dir.mkdir(exist_ok=True)

    scanner = PPPCScanner(config_manager, str(output_dir))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning applications...", total=None)

        try:
            scan_results = scanner.scan_core_applications(list(paths))
            progress.update(task, description="Generating reports...")

            # Generate report
            report_path = (
                output_dir
                / f"pppc_scan_report_{scan_results.scan_timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            )
            scanner.generate_report(scan_results, str(report_path))

            # Generate profiles for non-compliant apps
            profile_count = 0
            for analysis in scan_results.app_analyses:
                if analysis.compliance_status in ["NEEDS_IMPROVEMENT", "NON_COMPLIANT"]:
                    profile_path = (
                        output_dir
                        / f"{analysis.app_name.replace(' ', '_')}_pppc.mobileconfig"
                    )
                    if scanner.generate_pppc_profile(analysis, str(profile_path)):
                        profile_count += 1

            progress.update(task, description="Scan complete!")

        except Exception as e:
            console.print(f"[red]Error during scan: {e}[/red]")
            return 1

    # Display results
    if output_format == "table":
        _display_scan_results_table(console, scan_results)
    elif output_format == "json":
        _display_scan_results_json(console, scan_results)
    elif output_format == "csv":
        _display_scan_results_csv(console, scan_results)

    # Summary
    console.print(f"\n[green]✅ Scan Complete![/green]")
    console.print(f"   📊 Report: {report_path}")
    console.print(f"   📁 Profiles: {profile_count} generated")
    console.print(f"   📂 Output: {output_dir}")

    return 0


@pppc.command()
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Environment to use",
)
@click.option("--app-path", required=True, help="Path to the application bundle")
@click.option("--output", "-o", help="Output path for the profile")
def generate(env: str, app_path: str, output: Optional[str]):
    """Generate a PPPC profile for a specific application"""
    console = Console()

    if not Path(app_path).exists():
        console.print(f"[red]Error: Application not found at {app_path}[/red]")
        return 1

    # Initialize scanner
    config_manager = ConfigManager(environment=env)
    scanner = PPPCScanner(config_manager)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing application...", total=None)

        try:
            analysis = scanner._analyze_application(app_path)
            if not analysis:
                console.print(
                    f"[red]Error: Could not analyze application at {app_path}[/red]"
                )
                return 1

            progress.update(task, description="Generating profile...")

            # Generate profile
            if not output:
                output = f"{analysis.app_name.replace(' ', '_')}_pppc.mobileconfig"

            if scanner.generate_pppc_profile(analysis, output):
                console.print(f"[green]✅ Generated PPPC profile: {output}[/green]")

                # Display analysis summary
                _display_app_analysis(console, analysis)
                return 0
            else:
                console.print(f"[red]Error: Failed to generate profile[/red]")
                return 1

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return 1


@pppc.command()
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Environment to use",
)
@click.option("--profiles-dir", help="Directory containing PPPC profiles")
def analyze_profiles(env: str, profiles_dir: Optional[str]):
    """Analyze existing PPPC profiles"""
    console = Console()

    # Initialize scanner
    config_manager = ConfigManager(environment=env)
    profiles_dir = profiles_dir or str(Path.cwd() / "data" / "macos-profiles")
    scanner = PPPCScanner(config_manager, profiles_dir)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing profiles...", total=None)

        try:
            profiles = scanner.profile_analyzer.find_pppc_profiles()
            progress.update(task, description="Processing profiles...")

            profile_data = []
            for profile_path in profiles:
                services = scanner.profile_analyzer.extract_pppc_services(profile_path)
                profile_data.append(
                    {
                        "path": str(profile_path),
                        "name": profile_path.stem,
                        "services": services,
                    }
                )

            progress.update(task, description="Analysis complete!")

        except Exception as e:
            console.print(f"[red]Error analyzing profiles: {e}[/red]")
            return 1

    # Display results
    _display_profile_analysis(console, profile_data)
    return 0


def _display_scan_results_table(console: Console, scan_results: ScanResults):
    """Display scan results in a table format"""
    # Summary panel
    compliance_rate = (
        (scan_results.compliant_apps / scan_results.total_apps_scanned * 100)
        if scan_results.total_apps_scanned > 0
        else 0
    )

    summary_text = f"""
Total Apps Scanned: {scan_results.total_apps_scanned}
Compliant Apps: {scan_results.compliant_apps}
Non-Compliant Apps: {scan_results.non_compliant_apps}
Compliance Rate: {compliance_rate:.1f}%
Scan Duration: {scan_results.scan_duration:.2f}s
    """

    console.print(
        Panel(
            summary_text,
            title="[bold blue]PPPC Scan Summary[/bold blue]",
            border_style="blue",
        )
    )

    # Apps table
    if scan_results.app_analyses:
        table = Table(title="Application Analysis")
        table.add_column("App Name", style="cyan")
        table.add_column("Bundle ID", style="magenta")
        table.add_column("Compliance", style="green")
        table.add_column("Risk Level", style="yellow")
        table.add_column("Missing Permissions", style="red")

        for analysis in scan_results.app_analyses:
            compliance_color = {
                "COMPLIANT": "green",
                "NEEDS_IMPROVEMENT": "orange1",
                "NON_COMPLIANT": "red",
            }.get(analysis.compliance_status.value, "white")

            table.add_row(
                analysis.app_name,
                analysis.bundle_id,
                f"[{compliance_color}]{analysis.compliance_status.value}[/{compliance_color}]",
                analysis.risk_level,
                str(len(analysis.missing_permissions)),
            )

        console.print(table)

    # Recommendations
    if scan_results.app_analyses:
        console.print("\n[bold yellow]Recommendations:[/bold yellow]")
        for analysis in scan_results.app_analyses:
            if analysis.recommendations:
                console.print(f"\n[cyan]{analysis.app_name}:[/cyan]")
                for rec in analysis.recommendations:
                    console.print(f"  • {rec}")


def _display_scan_results_json(console: Console, scan_results: ScanResults):
    """Display scan results in JSON format"""
    import json
    from dataclasses import asdict

    result_dict = {
        "scan_metadata": {
            "timestamp": scan_results.scan_timestamp.isoformat(),
            "total_apps_scanned": scan_results.total_apps_scanned,
            "compliant_apps": scan_results.compliant_apps,
            "non_compliant_apps": scan_results.non_compliant_apps,
            "compliance_rate": (
                scan_results.compliant_apps / scan_results.total_apps_scanned
                if scan_results.total_apps_scanned > 0
                else 0
            ),
            "scan_duration": scan_results.scan_duration,
        },
        "app_analyses": [asdict(analysis) for analysis in scan_results.app_analyses],
    }

    console.print(json.dumps(result_dict, indent=2, default=str))


def _display_scan_results_csv(console: Console, scan_results: ScanResults):
    """Display scan results in CSV format"""
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "App Name",
            "Bundle ID",
            "Compliance Status",
            "Risk Level",
            "Missing Permissions Count",
            "Required Permissions",
            "Missing Permissions",
            "Recommendations",
        ]
    )

    # Data
    for analysis in scan_results.app_analyses:
        required_permissions = ", ".join(analysis.required_permissions)
        missing_permissions = ", ".join(analysis.missing_permissions)
        recommendations = ", ".join(analysis.recommendations)

        writer.writerow(
            [
                analysis.app_name,
                analysis.bundle_id,
                analysis.compliance_status.value,
                analysis.risk_level,
                len(analysis.missing_permissions),
                required_permissions,
                missing_permissions,
                recommendations,
            ]
        )

    console.print(output.getvalue())


def _display_app_analysis(console: Console, analysis):
    """Display analysis for a single application"""
    console.print(f"\n[bold blue]Analysis for {analysis.app_name}[/bold blue]")
    console.print(f"Bundle ID: {analysis.bundle_id}")
    console.print(f"Compliance: {analysis.compliance_status.value}")
    console.print(f"Risk Level: {analysis.risk_level}")

    if analysis.required_permissions:
        console.print(f"\n[green]Required Permissions:[/green]")
        for permission in analysis.required_permissions:
            console.print(f"  • {permission}")

    if analysis.missing_permissions:
        console.print(f"\n[red]Missing Permissions:[/red]")
        for permission in analysis.missing_permissions:
            console.print(f"  • {permission}")

    if analysis.recommendations:
        console.print(f"\n[yellow]Recommendations:[/yellow]")
        for rec in analysis.recommendations:
            console.print(f"  • {rec}")


def _display_profile_analysis(console: Console, profile_data: List[dict]):
    """Display analysis of existing profiles"""
    console.print(f"\n[bold blue]Found {len(profile_data)} PPPC profiles[/bold blue]")

    for profile in profile_data:
        console.print(f"\n[cyan]{profile['name']}[/cyan]")
        console.print(f"  Path: {profile['path']}")
        console.print(f"  Services: {len(profile['services'])}")

        if profile["services"]:
            for service in profile["services"]:
                console.print(
                    f"    • {service.service_name} - {service.identifier} ({'Allowed' if service.allowed else 'Denied'})"
                )


if __name__ == "__main__":
    pppc()
