#!/usr/bin/env python3
"""
Improved Export Command for jpapi CLI
Uses configuration-driven patterns to reduce code complexity while maintaining functionality
"""

from .common_imports import (
    ArgumentParser,
    Namespace,
    Dict,
    Any,
    List,
    Optional,
    BaseCommand,
)
from core.logging.command_mixin import LoggingCommandMixin
from pathlib import Path


class ExportCommand(BaseCommand, LoggingCommandMixin):
    """Improved export command using configuration-driven patterns"""

    def __init__(self):
        super().__init__(
            name="export", description="📤 Export JAMF data to various formats"
        )
        LoggingCommandMixin.__init__(self)
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup conversational patterns for natural language commands"""

        # Device exports
        self.add_conversational_pattern(
            pattern="ios devices",
            handler="_export_mobile_devices",
            description="Export iOS/mobile devices",
            aliases=["mobile", "ipad", "iphone"],
        )

        self.add_conversational_pattern(
            pattern="macos devices",
            handler="_export_computers",
            description="Export macOS computers",
            aliases=["computers", "mac", "macs"],
        )

        # Policy exports
        self.add_conversational_pattern(
            pattern="policies",
            handler="_export_policies",
            description="Export policies",
            aliases=["policy"],
        )

        # Profile exports
        self.add_conversational_pattern(
            pattern="macos profiles",
            handler="_export_macos_profiles",
            description="Export macOS configuration profiles",
            aliases=["mac-profiles", "osx-profiles"],
        )

        self.add_conversational_pattern(
            pattern="ios profiles",
            handler="_export_ios_profiles",
            description="Export iOS configuration profiles",
            aliases=["mobile-profiles", "iphone-profiles", "ipad-profiles"],
        )

        # Other exports
        self.add_conversational_pattern(
            pattern="categories",
            handler="_export_categories",
            description="Export categories",
            aliases=["category", "cat", "cats"],
        )

        self.add_conversational_pattern(
            pattern="scripts",
            handler="_export_scripts",
            description="Export scripts",
            aliases=["script"],
        )

        self.add_conversational_pattern(
            pattern="computer groups",
            handler="_export_computer_groups",
            description="Export computer groups",
            aliases=["macos-groups", "groups"],
        )

        # Advanced searches exports
        self.add_conversational_pattern(
            pattern="computer advanced-searches",
            handler="_export_computer_advanced_searches",
            description="Export advanced computer searches",
            aliases=["computer-searches", "mac-searches", "advanced-computer"],
        )

        self.add_conversational_pattern(
            pattern="mobile advanced-searches",
            handler="_export_mobile_advanced_searches",
            description="Export advanced mobile device searches",
            aliases=["mobile-searches", "advanced-mobile", "ios-searches"],
        )

        self.add_conversational_pattern(
            pattern="user advanced-searches",
            handler="_export_user_advanced_searches",
            description="Export advanced user searches",
            aliases=["user-searches", "advanced-user"],
        )

        self.add_conversational_pattern(
            pattern="advanced searches",
            handler="_export_advanced_searches",
            description="Export advanced searches",
            aliases=[
                "advanced-searches",
                "searches",
                "computer-searches",
                "mobile-searches",
            ],
        )

        # Special patterns
        self.add_conversational_pattern(
            pattern="download scripts",
            handler="_export_scripts_with_files",
            description="Download scripts with files",
            aliases=["scripts download"],
        )

        # Package exports
        self.add_conversational_pattern(
            pattern="packages",
            handler="_export_packages",
            description="Export packages",
            aliases=["pkg", "pkgs", "installers", "package"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Override to set CSV as default format for exports"""
        super().add_arguments(parser)

        # Add download arguments
        parser.add_argument(
            "--download",
            action="store_true",
            help="Download individual files (for policies, scripts, etc.)",
        )
        parser.add_argument(
            "--no-download",
            action="store_true",
            help="Skip downloading individual files",
        )
        parser.add_argument(
            "--analysis",
            "-a",
            action="store_true",
            help="Generate analysis report with insights and recommendations",
        )

        # Override format default for exports
        for action in parser._actions:
            if action.dest == "format":
                action.default = "csv"
                break

    # Handler methods for each export type
    def _export_mobile_devices(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export mobile devices"""
        return self._export_objects("mobile", args)

    def _export_computers(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Export computers"""
        return self._export_objects("computers", args)

    def _export_policies(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Export policies using ExportPolicies"""
        try:
            from .export.export_policies import ExportPolicies

            # Create policy export handler
            handler = ExportPolicies(self.auth)

            # Execute export using handler
            return handler.export(args)

        except Exception as e:
            print(f"❌ Error exporting policies: {e}")
            return 1

    def _export_macos_profiles(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export macOS profiles using ProfileExportHandler"""
        try:
            from .export.export_profiles import ExportProfiles

            # Create macOS profile export handler
            handler = ExportProfiles(self.auth, "macos")

            # Execute export using handler
            return handler.export(args)

        except Exception as e:
            print(f"❌ Error exporting macOS profiles: {e}")
            return 1

    def _export_ios_profiles(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export iOS profiles"""
        return self._export_objects("ios-profiles", args)

    def _export_categories(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Export categories"""
        return self._export_objects("categories", args)

    def _export_scripts(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Export scripts using ExportScripts"""
        try:
            from .export.export_scripts import ExportScripts

            handler = ExportScripts(self.auth)
            return handler.export(args)
        except Exception as e:
            print(f"❌ Error exporting scripts: {e}")
            return 1

    def _export_scripts_with_files(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export scripts with file downloads using ExportScripts"""
        try:
            from .export.export_scripts import ExportScripts

            handler = ExportScripts(self.auth)
            # Set download flag
            args.download = True
            return handler.export(args)
        except Exception as e:
            print(f"❌ Error exporting scripts: {e}")
            return 1

    def _export_packages(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Export packages using ExportPackages"""
        try:
            from .export.export_packages import ExportPackages

            handler = ExportPackages(self.auth)
            return handler.export(args)
        except Exception as e:
            print(f"❌ Error exporting packages: {e}")
            return 1

    def _export_computer_groups(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export computer groups"""
        return self._export_objects("computer-groups", args)

    def _export_computer_advanced_searches(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export advanced computer searches"""
        return self._export_objects("computer-advanced-searches", args)

    def _export_mobile_advanced_searches(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export advanced mobile device searches"""
        from .export.export_mobile_searches import ExportMobileSearches

        handler = ExportMobileSearches(self.auth)
        return handler.export(args)

    def _export_user_advanced_searches(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export advanced user searches"""
        return self._export_objects("user-advanced-searches", args)

    def _export_advanced_searches(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Export advanced searches"""
        return self._export_objects("advanced-searches", args)

    def _export_objects(self, export_type: str, args: Namespace) -> int:
        """Generic method to export objects"""
        try:
            # API endpoint mapping
            endpoints = {
                "mobile": "/JSSResource/mobiledevices",
                "computers": "/JSSResource/computers",
                "policies": "/api/v1/policies",
                "macos-profiles": "/JSSResource/osxconfigurationprofiles",
                "ios-profiles": "/JSSResource/mobiledeviceconfigurationprofiles",
                "categories": "/JSSResource/categories",
                "scripts": "/JSSResource/scripts",
                "computer-groups": "/JSSResource/computergroups",
                "computer-advanced-searches": "/JSSResource/advancedcomputersearches",
                "mobile-advanced-searches": "/api/v1/advanced-mobile-device-searches",
                "user-advanced-searches": "/JSSResource/advancedusersearches",
                "advanced-searches": "/JSSResource/advancedcomputersearches",
            }

            endpoint = endpoints.get(export_type)
            if not endpoint:
                self.log_error(f"Unknown export type: {export_type}")
                return 1

            self.log_info(f"Starting {export_type} export")

            # Handle pagination for policies
            if export_type == "policies":
                self.log_info("Using pagination for policies")
                objects = self._export_policies_with_pagination(endpoint)
            else:
                # Make API call with progress tracking
                with self.progress_tracker(
                    1, f"Fetching {export_type} from JAMF API"
                ) as tracker:
                    response = self.auth.api_request("GET", endpoint)
                    tracker.update()

                # Extract objects from response
                self.log_info("Processing API response")
                objects = self._extract_objects_from_response(response, export_type)

            if not objects:
                self.log_error(f"No {export_type} found to export")
                return 1

            self.log_success(f"Found {len(objects)} {export_type} to export")

            # Apply filtering
            if hasattr(args, "filter") and args.filter:
                self.log_info("Applying filters")
                objects = self._apply_filters(objects, args, export_type)
                self.log_info(f"After filtering: {len(objects)} {export_type}")

            # Format objects for export
            self.log_info("Formatting data for export")
            formatted_data = self._format_objects_for_export(objects, args, export_type)

            # Handle file downloads for scripts
            if export_type == "scripts" and getattr(args, "download_files", False):
                self.log_info("Downloading script files")
                self._download_script_files(objects, args)

            # Output
            self.log_info("Generating output")
            output = self.format_output(formatted_data, args.format)

            # Generate filename with instance prefix if no output path specified
            if args.output is None:
                from src.lib.exports.manage_exports import generate_export_filename

                filename = generate_export_filename(
                    export_type, args.format, self.environment
                )
                # Ensure the export directory exists
                from src.lib.exports.manage_exports import get_export_directory

                export_dir = get_export_directory(self.environment)
                export_dir.mkdir(parents=True, exist_ok=True)
                output_path = export_dir / filename
            else:
                output_path = args.output

            self.log_info(f"Saving export to: {output_path}")
            self.save_output(output, str(output_path))

            self.log_success(f"Successfully exported {len(objects)} {export_type}")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _export_policies_with_pagination(self, endpoint: str) -> List[Dict[str, Any]]:
        """Export all policies with pagination handling"""
        all_policies = []
        page = 0
        page_size = 100

        self.log_info("Starting paginated policy fetch")

        while True:
            url = f"{endpoint}?page={page}&page-size={page_size}&sort=id"
            self.log_info(f"Fetching page {page + 1}...")

            try:
                response = self.auth.api_request("GET", url)
                if "results" in response:
                    policies = response["results"]
                    if not policies:
                        self.log_info("No more policies found, pagination complete")
                        break

                    all_policies.extend(policies)
                    self.log_success(
                        f"Found {len(policies)} policies on page {page + 1} (Total: {len(all_policies)})"
                    )

                    if len(policies) < page_size:
                        self.log_info("Last page reached")
                        break
                    page += 1
                else:
                    self.log_warning("No results in response, stopping pagination")
                    break
            except Exception as e:
                self.log_error(f"Error fetching page {page + 1}: {e}")
                break

        self.log_success(
            f"Policy pagination complete: {len(all_policies)} total policies retrieved"
        )
        return all_policies

    def _extract_objects_from_response(
        self, response: Dict[str, Any], export_type: str
    ) -> List[Dict[str, Any]]:
        """Extract objects from API response based on export type"""
        if export_type == "mobile":
            if (
                "mobile_devices" in response
                and "mobile_device" in response["mobile_devices"]
            ):
                devices = response["mobile_devices"]["mobile_device"]
                return devices if isinstance(devices, list) else [devices]

        elif export_type == "computers":
            if "computers" in response and "computer" in response["computers"]:
                computers = response["computers"]["computer"]
                return computers if isinstance(computers, list) else [computers]

        elif export_type == "policies":
            if "results" in response:
                return response["results"]

        elif export_type in ["macos-profiles", "ios-profiles"]:
            if "os_x_configuration_profiles" in response:
                profiles = response["os_x_configuration_profiles"].get(
                    "os_x_configuration_profile", []
                )
                return profiles if isinstance(profiles, list) else [profiles]

        elif export_type == "categories":
            if "categories" in response and "category" in response["categories"]:
                return response["categories"]["category"]

        elif export_type == "scripts":
            if "scripts" in response:
                scripts = response["scripts"]
                if isinstance(scripts, dict) and "script" in scripts:
                    scripts = scripts["script"]
                return scripts if isinstance(scripts, list) else [scripts]

        elif export_type == "computer-groups":
            if "computer_groups" in response:
                groups = response["computer_groups"]
                if isinstance(groups, dict) and "computer_group" in groups:
                    groups = groups["computer_group"]
                return groups if isinstance(groups, list) else [groups]

        elif export_type == "advanced-searches":
            # Handle both JSON and XML responses from JAMF Pro Classic API
            if "raw_response" in response:
                import xml.etree.ElementTree as ET

                try:
                    root = ET.fromstring(response["raw_response"])
                    searches = []
                    for search_elem in root.findall(".//advanced_computer_search"):
                        search_data = {}
                        for child in search_elem:
                            search_data[child.tag] = child.text
                        searches.append(search_data)
                    return searches
                except ET.ParseError:
                    return []
            elif "advanced_computer_searches" in response:
                searches = response["advanced_computer_searches"]
                # Handle both array format and nested format
                if isinstance(searches, list):
                    return searches
                elif "advanced_computer_search" in searches:
                    search_list = searches["advanced_computer_search"]
                    return (
                        search_list if isinstance(search_list, list) else [search_list]
                    )
                else:
                    return []

        return []

    def _apply_filters(
        self, objects: List[Dict[str, Any]], args: Namespace, export_type: str
    ) -> List[Dict[str, Any]]:
        """Apply filters to objects"""
        filtered = objects

        # Name filtering
        if hasattr(args, "filter") and args.filter:
            from src.lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(filtered)
            filtered = filter_obj.filter_objects(filtered, "name", args.filter)
            print(f"🔍 Filtered from {original_count} to {len(filtered)} {export_type}")

        # Status filtering for policies
        if (
            export_type == "policies"
            and hasattr(args, "status")
            and args.status != "all"
        ):
            enabled_filter = args.status == "enabled"
            filtered = [obj for obj in filtered if obj.get("enabled") == enabled_filter]

        return filtered

    def _format_objects_for_export(
        self, objects: List[Dict[str, Any]], args: Namespace, export_type: str
    ) -> List[Dict[str, Any]]:
        """Format objects for export based on type and arguments"""
        if not objects:
            return []

        formatted = []
        for obj in objects:
            formatted_obj = {"ID": obj.get("id", ""), "Name": obj.get("name", "")}

            # Add type-specific fields
            if "category" in obj:
                if isinstance(obj["category"], dict):
                    formatted_obj["Category"] = obj["category"].get("name", "")
                else:
                    formatted_obj["Category"] = obj["category"]

            if "enabled" in obj:
                formatted_obj["Enabled"] = obj.get("enabled", False)

            if "model" in obj:
                formatted_obj["Model"] = obj.get("model", "")

            if "serial_number" in obj:
                formatted_obj["Serial Number"] = obj.get("serial_number", "")

            if "os_version" in obj:
                formatted_obj["OS Version"] = obj.get("os_version", "")

            if "description" in obj:
                formatted_obj["Description"] = obj.get("description", "")

            # Add detailed fields if requested
            if hasattr(args, "detailed") and args.detailed:
                if "uuid" in obj:
                    formatted_obj["UUID"] = obj.get("uuid", "")

                if "frequency" in obj:
                    formatted_obj["Frequency"] = obj.get("frequency", "")

                if "trigger" in obj:
                    formatted_obj["Trigger"] = obj.get("trigger", "")

                if "priority" in obj:
                    formatted_obj["Priority"] = obj.get("priority", "")

            formatted.append(formatted_obj)

        return formatted

    def _download_script_files(
        self, scripts: List[Dict[str, Any]], args: Namespace
    ) -> None:
        """Download script files if requested"""
        self.log_info(f"Starting download of {len(scripts)} script files")

        with self.progress_tracker(len(scripts), "Downloading script files") as tracker:
            for i, script in enumerate(scripts):
                script_id = script.get("id")
                script_name = script.get("name", f"script_{script_id}")

                if script_id:
                    try:
                        tracker.set_description(f"Downloading: {script_name}")

                        # Download script file
                        response = self.auth.api_request(
                            "GET", f"/JSSResource/scripts/id/{script_id}"
                        )

                        if (
                            "script" in response
                            and "script_contents" in response["script"]
                        ):
                            content = response["script"]["script_contents"]

                            # Save to file
                            filename = f"{script_name}.sh"
                            if args.output:
                                output_dir = Path(args.output).parent
                                output_dir.mkdir(parents=True, exist_ok=True)
                                filepath = output_dir / filename
                            else:
                                filepath = Path(filename)

                            with open(filepath, "w") as f:
                                f.write(content)

                            self.log_success(f"Downloaded {script_name} to {filepath}")

                    except Exception as e:
                        self.log_error(f"Failed to download {script_name}: {e}")

                tracker.update()

        self.log_success("Script file download complete")
