#!/usr/bin/env python3
"""
Manifest CLI Command - Profile Manifests Manager
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

from src.tools.profile_manifests import (
    ProfileManifestManager,
    ManifestResult,
    ManifestInfo,
)

# Try to import ConfigManager, fallback to mock if not available
try:
    from src.core.config.config_manager import ConfigManager
except ImportError:
    # Mock ConfigManager for standalone usage
    class ConfigManager:
        def __init__(self, environment="dev"):
            self.environment = environment


@click.group()
def manifest():
    """Profile Manifests Management Commands"""
    pass


@manifest.command()
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Environment to use",
)
@click.option("--output", "-o", help="Output directory for manifest data")
@click.option(
    "--types",
    "-t",
    multiple=True,
    help="Manifest types to update (apple, developer, applications)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def update(env: str, output: Optional[str], types: List[str], verbose: bool):
    """Update profile manifests from remote sources"""
    console = Console()

    # Initialize manifest manager
    config_manager = ConfigManager(environment=env)
    output_dir = (
        Path(output) if output else Path.cwd() / "storage" / "data" / "manifest-data"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    manager = ProfileManifestManager(config_manager, str(output_dir))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Updating manifests...", total=None)

        try:
            manifest_types = list(types) if types else None
            result = manager.update_manifests(manifest_types)

            if result.success:
                progress.update(task, description="Manifests updated successfully!")

                # Display summary
                _display_update_summary(console, result)
                return 0
            else:
                console.print(f"[red]Error: {result.error_message}[/red]")
                return 1

        except Exception as e:
            console.print(f"[red]Error updating manifests: {e}[/red]")
            return 1


@manifest.command()
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Environment to use",
)
@click.option("--search", "-s", required=True, help="Search term for manifests")
@click.option(
    "--types",
    "-t",
    multiple=True,
    help="Manifest types to search (apple, developer, applications)",
)
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "csv"]),
    help="Output format",
)
def search(env: str, search: str, types: List[str], output_format: str):
    """Search for profile manifests"""
    console = Console()

    # Initialize manifest manager
    config_manager = ConfigManager(environment=env)
    manager = ProfileManifestManager(config_manager)

    try:
        manifest_types = list(types) if types else None
        results = manager.search_manifests(search, manifest_types)

        if not results:
            console.print(f"[yellow]No manifests found for '{search}'[/yellow]")
            return 0

        # Display results
        if output_format == "table":
            _display_search_results_table(console, results)
        elif output_format == "json":
            _display_search_results_json(console, results)
        elif output_format == "csv":
            _display_search_results_csv(console, results)

        return 0

    except Exception as e:
        console.print(f"[red]Error searching manifests: {e}[/red]")
        return 1


@manifest.command()
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Environment to use",
)
@click.option("--bundle-id", required=True, help="Bundle ID to get details for")
def details(env: str, bundle_id: str):
    """Get detailed information about a specific manifest"""
    console = Console()

    # Initialize manifest manager
    config_manager = ConfigManager(environment=env)
    manager = ProfileManifestManager(config_manager)

    try:
        details = manager.get_manifest_details(bundle_id)

        if not details:
            console.print(
                f"[yellow]No manifest found for bundle ID: {bundle_id}[/yellow]"
            )
            return 0

        # Display details
        _display_manifest_details(console, bundle_id, details)
        return 0

    except Exception as e:
        console.print(f"[red]Error getting manifest details: {e}[/red]")
        return 1


@manifest.command()
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Environment to use",
)
@click.option("--output", "-o", help="Output path for the report")
def report(env: str, output: Optional[str]):
    """Generate a comprehensive manifest report"""
    console = Console()

    # Initialize manifest manager
    config_manager = ConfigManager(environment=env)
    manager = ProfileManifestManager(config_manager)

    try:
        if not output:
            output = f"manifest_report_{env}.json"

        if manager.generate_manifest_report(output):
            console.print(f"[green]✅ Manifest report generated: {output}[/green]")
            return 0
        else:
            console.print(f"[red]Error generating manifest report[/red]")
            return 1

    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")
        return 1


def _display_update_summary(console: Console, result: ManifestResult):
    """Display update summary"""
    summary_text = f"""
Manifests Updated: {result.updated_count}
Total Manifests: {result.manifest_count}
Success: {result.success}
    """

    console.print(
        Panel(
            summary_text,
            title="[bold blue]Manifest Update Summary[/bold blue]",
            border_style="blue",
        )
    )


def _display_search_results_table(console: Console, results: List[ManifestInfo]):
    """Display search results in table format"""
    table = Table(title=f"Found {len(results)} Manifests")
    table.add_column("App Name", style="cyan")
    table.add_column("Bundle ID", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Enterprise", style="red")

    for manifest in results:
        table.add_row(
            manifest.app_name,
            manifest.bundle_id,
            manifest.category,
            manifest.version,
            "Yes" if manifest.is_enterprise else "No",
        )

    console.print(table)


def _display_search_results_json(console: Console, results: List[ManifestInfo]):
    """Display search results in JSON format"""
    import json
    from dataclasses import asdict

    result_dict = {
        "search_results": [asdict(manifest) for manifest in results],
        "total_count": len(results),
    }

    console.print(json.dumps(result_dict, indent=2, default=str))


def _display_search_results_csv(console: Console, results: List[ManifestInfo]):
    """Display search results in CSV format"""
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "App Name",
            "Bundle ID",
            "Description",
            "Payload Type",
            "Version",
            "Last Updated",
            "Manifest URL",
            "Is Enterprise",
            "Requires Code Requirement",
            "Requires Bundle ID",
            "Category",
        ]
    )

    # Data
    for manifest in results:
        writer.writerow(
            [
                manifest.app_name,
                manifest.bundle_id,
                manifest.description,
                manifest.payload_type,
                manifest.version,
                manifest.last_updated.isoformat(),
                manifest.manifest_url,
                manifest.is_enterprise,
                manifest.requires_code_requirement,
                manifest.requires_bundle_id,
                manifest.category,
            ]
        )

    console.print(output.getvalue())


def _display_manifest_details(console: Console, bundle_id: str, details: dict):
    """Display detailed manifest information"""
    console.print(f"\n[bold blue]Manifest Details for {bundle_id}[/bold blue]")
    console.print(json.dumps(details, indent=2, default=str))


if __name__ == "__main__":
    manifest()
