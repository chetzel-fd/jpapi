#!/usr/bin/env python3
"""
Mobile Apps Command for jpapi CLI
Handles mobile device applications
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


class MobileAppsCommand(BaseCommand):
    """Mobile apps command for JAMF Pro mobile device applications"""

    def __init__(self):
        super().__init__(
            name="mobile-apps",
            description="📱 Mobile device applications",
        )
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup conversational patterns for mobile apps"""

        # All mobile apps
        self.add_conversational_pattern(
            pattern="all apps",
            handler="_list_all_apps",
            description="List all mobile device applications",
            aliases=["all", "apps", "applications"],
        )

        # iOS apps
        self.add_conversational_pattern(
            pattern="ios apps",
            handler="_list_ios_apps",
            description="List iOS applications",
            aliases=["ios", "iphone apps", "ipad apps"],
        )

        # Android apps
        self.add_conversational_pattern(
            pattern="android apps",
            handler="_list_android_apps",
            description="List Android applications",
            aliases=["android"],
        )

        # App Store apps
        self.add_conversational_pattern(
            pattern="app store apps",
            handler="_list_app_store_apps",
            description="List App Store applications",
            aliases=["app store", "store apps"],
        )

        # Internal apps
        self.add_conversational_pattern(
            pattern="internal apps",
            handler="_list_internal_apps",
            description="List internal applications",
            aliases=["internal", "enterprise apps"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        super().add_arguments(parser)

        # Add app type filtering
        parser.add_argument(
            "--type",
            choices=["ios", "android", "all"],
            default="all",
            help="Filter by app type",
        )

        # Add source filtering
        parser.add_argument(
            "--source",
            choices=["App Store", "Internal", "All"],
            default="All",
            help="Filter by app source",
        )

        # Add bundle ID filtering
        parser.add_argument(
            "--bundle-id",
            help="Filter by bundle identifier",
        )

        # Add version filtering
        parser.add_argument(
            "--version",
            help="Filter by app version",
        )

    def _list_all_apps(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List all mobile device applications"""
        return self._list_apps("all", args)

    def _list_ios_apps(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List iOS applications"""
        return self._list_apps("ios", args)

    def _list_android_apps(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List Android applications"""
        return self._list_apps("android", args)

    def _list_app_store_apps(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List App Store applications"""
        return self._list_apps("app_store", args)

    def _list_internal_apps(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List internal applications"""
        return self._list_apps("internal", args)

    def _list_apps(self, app_type: str, args: Namespace) -> int:
        """Generic method to list mobile device applications"""
        try:
            # API endpoint
            endpoint = "/JSSResource/mobiledeviceapplications"

            print(f"📱 Fetching mobile device applications...")
            response = self.auth.api_request("GET", endpoint)

            # Extract apps from response
            apps = self._extract_apps_from_response(response)

            if not apps:
                print("❌ No mobile device applications found")
                return 1

            # Apply filtering
            filtered_apps = self._apply_app_filters(apps, app_type, args)

            # Format and output
            formatted_data = self._format_apps_for_display(
                filtered_apps, args
            )
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)

            print(f"\n✅ Found {len(filtered_apps)} mobile device applications")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _extract_apps_from_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract apps from API response"""
        if "mobile_device_applications" in response:
            apps_data = response["mobile_device_applications"]
            if "mobile_device_application" in apps_data:
                apps = apps_data["mobile_device_application"]
                return apps if isinstance(apps, list) else [apps]
        return []

    def _apply_app_filters(
        self, apps: List[Dict[str, Any]], app_type: str, args: Namespace
    ) -> List[Dict[str, Any]]:
        """Apply filters to apps"""
        filtered = apps

        # Name filtering
        if hasattr(args, "filter") and args.filter:
            from src.lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(filtered)
            filtered = filter_obj.filter_objects(filtered, "name", args.filter)
            print(f"🔍 Filtered from {original_count} to {len(filtered)} apps")

        # App type filtering
        if app_type != "all":
            if app_type == "ios":
                filtered = [app for app in filtered if self._is_ios_app(app)]
            elif app_type == "android":
                filtered = [app for app in filtered if self._is_android_app(app)]
            elif app_type == "app_store":
                filtered = [app for app in filtered if self._is_app_store_app(app)]
            elif app_type == "internal":
                filtered = [app for app in filtered if self._is_internal_app(app)]

        # Bundle ID filtering
        if hasattr(args, "bundle_id") and args.bundle_id:
            filtered = [
                app for app in filtered
                if args.bundle_id.lower() in app.get("bundle_id", "").lower()
            ]

        # Version filtering
        if hasattr(args, "version") and args.version:
            filtered = [
                app for app in filtered
                if args.version.lower() in app.get("version", "").lower()
            ]

        # Source filtering
        if hasattr(args, "source") and args.source != "All":
            filtered = [
                app for app in filtered
                if self._app_matches_source(app, args.source)
            ]

        return filtered

    def _is_ios_app(self, app: Dict[str, Any]) -> bool:
        """Check if app is iOS"""
        # Check for iOS-specific fields or bundle ID patterns
        bundle_id = app.get("bundle_id", "")
        return bundle_id.startswith("com.apple.") or "ios" in app.get("name", "").lower()

    def _is_android_app(self, app: Dict[str, Any]) -> bool:
        """Check if app is Android"""
        # Check for Android-specific fields or bundle ID patterns
        bundle_id = app.get("bundle_id", "")
        return "android" in app.get("name", "").lower() or bundle_id.startswith("com.google.")

    def _is_app_store_app(self, app: Dict[str, Any]) -> bool:
        """Check if app is from App Store"""
        # Check for App Store source or specific fields
        return app.get("source", "").lower() == "app store" or "app store" in app.get("name", "").lower()

    def _is_internal_app(self, app: Dict[str, Any]) -> bool:
        """Check if app is internal/enterprise"""
        # Check for internal source or specific fields
        return app.get("source", "").lower() == "internal" or "internal" in app.get("name", "").lower()

    def _app_matches_source(self, app: Dict[str, Any], source: str) -> bool:
        """Check if app matches source filter"""
        app_source = app.get("source", "").lower()
        return source.lower() in app_source

    def _format_apps_for_display(
        self, apps: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format apps for display"""
        if not apps:
            return []

        formatted = []
        for app in apps:
            formatted_app = {
                "ID": app.get("id", ""),
                "Name": app.get("name", ""),
                "Bundle ID": app.get("bundle_id", ""),
                "Version": app.get("version", ""),
                "Source": app.get("source", ""),
            }

            # Add detailed fields if requested
            if hasattr(args, "detailed") and args.detailed:
                if "description" in app:
                    formatted_app["Description"] = app.get("description", "")

                if "category" in app:
                    category = app["category"]
                    if isinstance(category, dict):
                        formatted_app["Category"] = category.get("name", "")
                    else:
                        formatted_app["Category"] = category

                if "site" in app:
                    site = app["site"]
                    if isinstance(site, dict):
                        formatted_app["Site"] = site.get("name", "")
                    else:
                        formatted_app["Site"] = site

                if "itunes_store_id" in app:
                    formatted_app["iTunes Store ID"] = app.get("itunes_store_id", "")

                if "itunes_store_url" in app:
                    formatted_app["iTunes Store URL"] = app.get("itunes_store_url", "")

                if "icon" in app:
                    icon = app["icon"]
                    if isinstance(icon, dict):
                        formatted_app["Icon URL"] = icon.get("uri", "")
                    else:
                        formatted_app["Icon URL"] = icon

                if "bundle_size" in app:
                    formatted_app["Bundle Size"] = app.get("bundle_size", "")

                if "minimum_os_version" in app:
                    formatted_app["Minimum OS Version"] = app.get("minimum_os_version", "")

            formatted.append(formatted_app)

        return formatted
