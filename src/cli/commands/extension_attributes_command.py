#!/usr/bin/env python3
"""
Extension Attributes Command for jpapi CLI - Simplified
Delegates CRUD operations to top-level commands, focuses on listing
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
from resources.config.api_endpoints import APIRegistry


class ExtensionAttributesCommand(BaseCommand):
    """Extension attributes command - simplified to focus on listing"""

    def __init__(self):
        super().__init__(
            name="extension-attributes",
            description="🔧 Extension attributes (computer, mobile, user)",
        )
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup conversational patterns for extension attributes"""

        # Computer extension attributes
        self.add_conversational_pattern(
            pattern="computer",
            handler="_list_computer_attributes",
            description="List computer extension attributes",
            aliases=["computer attributes", "mac", "macos"],
        )

        # Mobile device extension attributes
        self.add_conversational_pattern(
            pattern="mobile",
            handler="_list_mobile_attributes",
            description="List mobile device extension attributes",
            aliases=["mobile attributes", "ios", "ipad", "iphone"],
        )

        # User extension attributes
        self.add_conversational_pattern(
            pattern="user",
            handler="_list_user_attributes",
            description="List user extension attributes",
            aliases=["user attributes", "users"],
        )

        # All extension attributes (default)
        self.add_conversational_pattern(
            pattern="all",
            handler="_list_all_attributes",
            description="List all extension attributes",
            aliases=["attributes", "list"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        super().add_arguments(parser)

        # Add filtering options
        parser.add_argument(
            "--data-type",
            choices=["String", "Integer", "Date", "Boolean"],
            help="Filter by data type",
        )
        parser.add_argument(
            "--input-type",
            choices=["Text Field", "Pop-up Menu", "Script", "LDAP Mapping"],
            help="Filter by input type",
        )

    def _list_computer_attributes(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List computer extension attributes"""
        return self._list_attributes("computer", args)

    def _list_mobile_attributes(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List mobile device extension attributes"""
        return self._list_attributes("mobile", args)

    def _list_user_attributes(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List user extension attributes"""
        return self._list_attributes("user", args)

    def _list_all_attributes(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List all extension attributes"""
        return self._list_attributes("all", args)

    def _list_attributes(self, attribute_type: str, args: Namespace) -> int:
        """Generic method to list extension attributes"""
        try:
            if attribute_type == "all":
                # List all types using APIRegistry
                all_attributes = []
                for attr_type_name in ["computer", "mobile", "user"]:
                    attributes = self._fetch_attributes(attr_type_name)
                    all_attributes.extend(attributes)
                attributes = all_attributes
            else:
                # Validate attribute type exists in APIRegistry
                try:
                    APIRegistry.get_list_endpoint(attribute_type)
                except ValueError:
                    print(f"❌ Unknown attribute type: {attribute_type}")
                    return 1
                attributes = self._fetch_attributes(attribute_type)

            if not attributes:
                print(f"❌ No {attribute_type} extension attributes found")
                return 1

            # Apply filtering
            filtered_attributes = self._apply_attribute_filters(attributes, args)

            # Format and output
            formatted_data = self._format_attributes_for_display(
                filtered_attributes, args
            )
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)

            print(
                f"✅ Found {len(filtered_attributes)} {attribute_type} extension attributes"
            )
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _fetch_attributes(self, attribute_type: str) -> List[Dict[str, Any]]:
        """Fetch attributes from API using APIRegistry"""
        print(f"🔧 Fetching {attribute_type} extension attributes...")

        # Get endpoint from APIRegistry
        endpoint = APIRegistry.get_list_endpoint(attribute_type)
        response = self.auth.api_request("GET", endpoint)

        # Extract attributes using APIRegistry
        attributes = APIRegistry.extract_list_response(attribute_type, response)
        if attributes:
            return attributes

        # Fallback for backward compatibility
        if attribute_type == "computer":
            if "computer_extension_attributes" in response:
                attrs_data = response["computer_extension_attributes"]
                if isinstance(attrs_data, list):
                    return attrs_data
                elif isinstance(attrs_data, dict):
                    # Handle legacy format with nested extension_attribute
                    if "extension_attribute" in attrs_data:
                        attributes = attrs_data["extension_attribute"]
                        return (
                            attributes if isinstance(attributes, list) else [attributes]
                        )
                return [attrs_data] if attrs_data else []

        elif attribute_type == "mobile":
            if "mobile_device_extension_attributes" in response:
                attrs_data = response["mobile_device_extension_attributes"]
                if isinstance(attrs_data, list):
                    return attrs_data
                elif isinstance(attrs_data, dict):
                    # Handle legacy format with nested extension_attribute
                    if "extension_attribute" in attrs_data:
                        attributes = attrs_data["extension_attribute"]
                        return (
                            attributes if isinstance(attributes, list) else [attributes]
                        )
                return [attrs_data] if attrs_data else []

        elif attribute_type == "user":
            if "user_extension_attributes" in response:
                attrs_data = response["user_extension_attributes"]
                if isinstance(attrs_data, list):
                    return attrs_data
                elif isinstance(attrs_data, dict):
                    # Handle legacy format with nested extension_attribute
                    if "extension_attribute" in attrs_data:
                        attributes = attrs_data["extension_attribute"]
                        return (
                            attributes if isinstance(attributes, list) else [attributes]
                        )
                return [attrs_data] if attrs_data else []

        return []

    def _apply_attribute_filters(
        self, attributes: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Apply filters to attributes"""
        filtered = attributes

        # Name filtering
        if hasattr(args, "filter") and args.filter:
            from lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(filtered)
            filtered = filter_obj.filter_objects(filtered, "name", args.filter)
            print(f"🔍 Filtered from {original_count} to {len(filtered)} attributes")

        # Data type filtering
        if hasattr(args, "data_type") and args.data_type:
            filtered = [
                attr
                for attr in filtered
                if attr.get("data_type", "").lower() == args.data_type.lower()
            ]

        # Input type filtering
        if hasattr(args, "input_type") and args.input_type:
            filtered = [
                attr
                for attr in filtered
                if attr.get("input_type", {}).get("type", "").lower()
                == args.input_type.lower()
            ]

        return filtered

    def _format_attributes_for_display(
        self, attributes: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format attributes for display"""
        if not attributes:
            return []

        formatted = []
        for attr in attributes:
            formatted_attr = {
                "ID": attr.get("id", ""),
                "Name": attr.get("name", ""),
                "Type": self._determine_attribute_type(attr),
                "Data Type": attr.get("data_type", ""),
                "Input Type": self._get_input_type(attr),
                "Enabled": attr.get("enabled", False),
            }

            # Add detailed fields if requested
            if hasattr(args, "detailed") and args.detailed:
                if "description" in attr:
                    formatted_attr["Description"] = attr.get("description", "")

                if "inventory_display" in attr:
                    formatted_attr["Inventory Display"] = attr.get(
                        "inventory_display", ""
                    )

                if "recon_display" in attr:
                    formatted_attr["Recon Display"] = attr.get("recon_display", "")

                if "site" in attr:
                    site = attr["site"]
                    if isinstance(site, dict):
                        formatted_attr["Site"] = site.get("name", "")
                    else:
                        formatted_attr["Site"] = site

                # Show script details if it's a script-based attribute
                if "input_type" in attr:
                    if attr["input_type"].get("type") == "Script":
                        script = attr["input_type"].get("script", {})
                        if script:
                            formatted_attr["Script Name"] = script.get("name", "")
                            formatted_attr["Script ID"] = script.get("id", "")

            formatted.append(formatted_attr)

        return formatted

    def _determine_attribute_type(self, attr: Dict[str, Any]) -> str:
        """Determine attribute type from attribute data"""
        # Check for type-specific markers
        if "computer" in str(attr.get("id", "")):
            return "Computer"
        elif "mobile" in str(attr.get("id", "")):
            return "Mobile"
        elif "user" in str(attr.get("id", "")):
            return "User"
        else:
            return "Unknown"

    def _get_input_type(self, attr: Dict[str, Any]) -> str:
        """Get input type from attribute"""
        input_type = attr.get("input_type", {})
        if isinstance(input_type, dict):
            return input_type.get("type", "Unknown")
        return str(input_type) if input_type else "Unknown"
