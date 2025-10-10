#!/usr/bin/env python3
"""
Export Configuration for jpapi CLI
Configuration-driven approach for export command arguments
"""

from typing import Dict, List, Any
import argparse

# Export type configurations
EXPORT_CONFIGS = {
    "mobile": {
        "aliases": [
            "ios",
            "ipad",
            "ipads",
            "iphone",
            "iphones",
            "ios-devices",
            "mobile-devices",
        ],
        "help": "Export mobile devices (also: ios, ipad)",
        "arguments": [
            (
                "--detailed",
                {"action": "store_true", "help": "Include detailed device information"},
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
            (
                "--filter",
                {
                    "help": "Filter devices by name, type, or OS version (supports wildcards: *, ?)"
                },
            ),
            (
                "--filter-type",
                {
                    "choices": ["wildcard", "regex", "exact", "contains"],
                    "default": "wildcard",
                    "help": "Type of filtering to use",
                },
            ),
        ],
    },
    "computers": {
        "aliases": [
            "comp",
            "mac",
            "macs",
            "macos",
            "macos-devices",
            "computer-devices",
        ],
        "help": "Export computers/macOS devices (also: comp, mac)",
        "arguments": [
            (
                "--detailed",
                {"action": "store_true", "help": "Include detailed device information"},
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
            (
                "--filter",
                {
                    "help": "Filter computers by name, model, or OS version (supports wildcards: *, ?)"
                },
            ),
            (
                "--filter-type",
                {
                    "choices": ["wildcard", "regex", "exact", "contains"],
                    "default": "wildcard",
                    "help": "Type of filtering to use",
                },
            ),
        ],
    },
    "computer-groups": {
        "aliases": ["macos-groups", "groups"],
        "help": "Export computer groups (also: macos-groups, groups)",
        "arguments": [
            (
                "--detailed",
                {
                    "action": "store_true",
                    "help": "Include detailed group information including criteria and members",
                },
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
        ],
    },
    "mobile-searches": {
        "aliases": ["mobile-searches", "advanced-mobile", "ios-searches"],
        "help": "Export advanced mobile device searches (also: mobile-searches, advanced-mobile, ios-searches)",
        "arguments": [
            (
                "--detailed",
                {
                    "action": "store_true",
                    "help": "Include detailed search information including criteria and display fields",
                },
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
            ("--filter", {"help": "Filter searches by name or description"}),
        ],
    },
    "policies": {
        "aliases": ["policy", "pol"],
        "help": "Export policies (also: policy, pol)",
        "arguments": [
            (
                "--status",
                {
                    "choices": ["enabled", "disabled", "all"],
                    "default": "all",
                    "help": "Filter by policy status",
                },
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
            (
                "--download",
                {
                    "action": "store_true",
                    "help": "Download individual policy files as XML",
                },
            ),
            (
                "--no-download",
                {
                    "action": "store_true",
                    "help": "Skip downloading individual policy files",
                },
            ),
            (
                "--filter",
                {
                    "help": "Filter policies by name, category, or other fields (supports wildcards: *, ?)"
                },
            ),
            (
                "--filter-type",
                {
                    "choices": ["wildcard", "regex", "exact", "contains"],
                    "default": "wildcard",
                    "help": "Type of filtering to use",
                },
            ),
        ],
    },
    "macos-profiles": {
        "aliases": ["mac-profiles", "osx-profiles"],
        "help": "Export macOS configuration profiles (also: mac-profiles, osx-profiles)",
        "arguments": [
            (
                "--detailed",
                {
                    "action": "store_true",
                    "help": "Include detailed profile information",
                },
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
            (
                "--filter",
                {
                    "help": "Filter profiles by name, level, or other fields (supports wildcards: *, ?)"
                },
            ),
            (
                "--filter-type",
                {
                    "choices": ["wildcard", "regex", "exact", "contains"],
                    "default": "wildcard",
                    "help": "Type of filtering to use",
                },
            ),
        ],
    },
    "ios-profiles": {
        "aliases": ["mobile-profiles", "iphone-profiles", "ipad-profiles"],
        "help": "Export iOS configuration profiles (also: mobile-profiles, iphone-profiles)",
        "arguments": [
            (
                "--detailed",
                {
                    "action": "store_true",
                    "help": "Include detailed profile information",
                },
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
        ],
    },
    "profiles": {
        "aliases": ["profile", "prf", "config", "configs"],
        "help": "Export all configuration profiles ()",
        "arguments": [
            (
                "--detailed",
                {
                    "action": "store_true",
                    "help": "Include detailed profile information",
                },
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
        ],
    },
    "categories": {
        "aliases": ["category", "cat", "cats"],
        "help": "Export categories (also: category, cat)",
        "arguments": [
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
        ],
    },
    "scripts": {
        "aliases": ["script"],
        "help": "Export and download scripts (also: script)",
        "arguments": [
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "json",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
            (
                "--include-content",
                {
                    "action": "store_true",
                    "default": True,
                    "help": "Include full script content (default)",
                },
            ),
            ("--category", {"help": "Filter by script category"}),
            ("--name", {"help": "Filter by script name (supports wildcards)"}),
            ("--id", {"help": "Filter by specific script ID"}),
            (
                "--no-download",
                {
                    "action": "store_true",
                    "help": "Skip downloading individual .sh files",
                },
            ),
        ],
    },
    "advanced-searches": {
        "aliases": [
            "adv",
            "advanced",
            "searches",
            "computer-searches",
            "advanced-computer-searches",
        ],
        "help": "Export advanced computer searches (also: adv, advanced, searches)",
        "arguments": [
            (
                "--detailed",
                {
                    "action": "store_true",
                    "help": "Include detailed search information including criteria and display fields",
                },
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
            ("--name", {"help": "Filter by search name (supports wildcards)"}),
            ("--id", {"help": "Filter by specific search ID"}),
        ],
    },
    "packages": {
        "aliases": ["pkg", "pkgs", "installers", "package"],
        "help": "Export packages (also: pkg, pkgs, installers)",
        "arguments": [
            (
                "--detailed",
                {
                    "action": "store_true",
                    "help": "Include detailed package information including manifest and history",
                },
            ),
            (
                "--format",
                {
                    "choices": ["csv", "json", "table"],
                    "default": "csv",
                    "help": "Export format",
                },
            ),
            ("--output", {"help": "Output file path"}),
            (
                "--filter",
                {
                    "help": "Filter packages by name, category, or other fields (supports wildcards: *, ?)"
                },
            ),
            (
                "--filter-type",
                {
                    "choices": ["wildcard", "regex", "exact", "contains"],
                    "default": "wildcard",
                    "help": "Type of filtering to use",
                },
            ),
            (
                "--download",
                {
                    "action": "store_true",
                    "help": "Download individual package files and manifests",
                },
            ),
            (
                "--no-download",
                {
                    "action": "store_true",
                    "help": "Skip downloading individual package files",
                },
            ),
            (
                "--include-history",
                {
                    "action": "store_true",
                    "help": "Include package history in detailed export",
                },
            ),
            (
                "--include-manifest",
                {
                    "action": "store_true",
                    "help": "Include package manifest information",
                },
            ),
        ],
    },
}

# Update configurations
UPDATE_CONFIGS = {
    "update": {
        "aliases": ["sync"],
        "help": "Update JAMF objects from CSV file (also: sync)",
        "arguments": [
            (
                "object_type",
                {"help": "Object type to update (computer-groups, policies, etc.)"},
            ),
            ("csv_file", {"help": "CSV file to sync from"}),
            (
                "--dry-run",
                {
                    "action": "store_true",
                    "help": "Show what would be changed without actually making changes",
                },
            ),
            (
                "--confirm",
                {"action": "store_true", "help": "Skip confirmation prompts"},
            ),
            ("--verbose", {"action": "store_true", "help": "Verbose output"}),
        ],
    }
}


def create_export_subparsers(parser: argparse.ArgumentParser) -> None:
    """Create export subparsers using configuration"""
    subparsers = parser.add_subparsers(
        dest="export_object", help="Object type to export"
    )

    # Create main subparsers
    for export_type, config in EXPORT_CONFIGS.items():
        main_parser = subparsers.add_parser(export_type, help=config["help"])
        _add_arguments_to_parser(main_parser, config["arguments"])

        # Create alias subparsers
        for alias in config["aliases"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            _add_arguments_to_parser(alias_parser, config["arguments"])

    # Create update subparsers
    for update_type, config in UPDATE_CONFIGS.items():
        main_parser = subparsers.add_parser(update_type, help=config["help"])
        _add_arguments_to_parser(main_parser, config["arguments"])

        # Create alias subparsers
        for alias in config["aliases"]:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            _add_arguments_to_parser(alias_parser, config["arguments"])


def _add_arguments_to_parser(
    parser: argparse.ArgumentParser, arguments: List[tuple]
) -> None:
    """Add arguments to a parser based on configuration"""
    for arg_spec in arguments:
        if isinstance(arg_spec[0], tuple):
            # Handle positional arguments
            parser.add_argument(arg_spec[0][0], **arg_spec[1])
        else:
            # Handle optional arguments
            parser.add_argument(arg_spec[0], **arg_spec[1])


def get_export_type_from_alias(alias: str) -> str:
    """Get the main export type from an alias"""
    for export_type, config in EXPORT_CONFIGS.items():
        if alias in config["aliases"]:
            return export_type
    return alias


def get_update_type_from_alias(alias: str) -> str:
    """Get the main update type from an alias"""
    for update_type, config in UPDATE_CONFIGS.items():
        if alias in config["aliases"]:
            return update_type
    return alias
