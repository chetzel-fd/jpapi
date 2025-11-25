#!/usr/bin/env python3
"""
Authentication Commands for JPAPI
Handles authentication setup and management
"""

import click
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@click.group()
def auth():
    """Authentication commands for JPAPI"""
    pass


@auth.command()
@click.option(
    "--env",
    default="sandbox",
    type=click.Choice(["dev", "prod"]),
    help="Environment to configure",
)
def setup(env: str):
    """Set up authentication credentials for JPAPI"""

    click.echo(f"🔐 Setting up authentication for {env} environment")
    click.echo("=" * 50)

    # Get credentials from user
    jamf_url = click.prompt("Jamf Pro URL (e.g., https://your-company.jamfcloud.com)")
    client_id = click.prompt("Client ID")
    client_secret = click.prompt("Client Secret", hide_input=True)

    # Create credentials object
    credentials = {
        "jamf_url": jamf_url,
        "client_id": client_id,
        "client_secret": client_secret,
        "environment": env,
    }

    # Save to credentials file
    cred_file = Path.home() / f".jpapi_{env}.json"

    try:
        with open(cred_file, "w") as f:
            json.dump(credentials, f, indent=2)

        # Set secure permissions
        os.chmod(cred_file, 0o600)

        click.echo(f"✅ Credentials saved to: {cred_file}")
        click.echo(f"   Environment: {env}")
        click.echo(f"   URL: {jamf_url}")
        click.echo(f"   Client ID: {client_id[:8]}...")
        click.echo("")
        click.echo("🔒 Credentials are securely stored and ready to use!")

    except Exception as e:
        click.echo(f"❌ Error saving credentials: {e}")
        return 1

    return 0


@auth.command()
@click.option(
    "--env",
    default="sandbox",
    type=click.Choice(["dev", "prod"]),
    help="Environment to check",
)
def status(env: str):
    """Check authentication status"""

    cred_file = Path.home() / f".jpapi_{env}.json"

    if not cred_file.exists():
        click.echo(f"❌ No credentials found for {env} environment")
        click.echo(f"   Run: python3 src/cli/main.py auth setup --env {env}")
        return 1

    try:
        with open(cred_file, "r") as f:
            credentials = json.load(f)

        click.echo(f"✅ Authentication configured for {env} environment")
        click.echo(f"   URL: {credentials.get('jamf_url', 'Unknown')}")
        click.echo(f"   Client ID: {credentials.get('client_id', 'Unknown')[:8]}...")
        click.echo(f"   File: {cred_file}")

    except Exception as e:
        click.echo(f"❌ Error reading credentials: {e}")
        return 1

    return 0


if __name__ == "__main__":
    auth()
