#!/usr/bin/env python3
"""
Extension Attributes Command for jpapi CLI
Handles computer, mobile device, and user extension attributes
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
from core.auth.login_manager import UnifiedJamfAuth


class ExtensionAttributesCommand(BaseCommand):
    """Extension attributes command for JAMF Pro extension attribute functionality"""

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
            pattern="computer attributes",
            handler="_list_computer_attributes",
            description="List computer extension attributes",
            aliases=["computer", "mac attributes", "macos attributes"],
        )

        # Mobile device extension attributes
        self.add_conversational_pattern(
            pattern="mobile attributes",
            handler="_list_mobile_attributes",
            description="List mobile device extension attributes",
            aliases=[
                "mobile",
                "ios attributes",
                "ipad attributes",
                "iphone attributes",
            ],
        )

        # User extension attributes
        self.add_conversational_pattern(
            pattern="user attributes",
            handler="_list_user_attributes",
            description="List user extension attributes",
            aliases=["user", "users"],
        )

        # All extension attributes
        self.add_conversational_pattern(
            pattern="all attributes",
            handler="_list_all_attributes",
            description="List all extension attributes",
            aliases=["all", "attributes"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        super().add_arguments(parser)

        # Create subparsers for different actions
        subparsers = parser.add_subparsers(
            dest="attr_action", help="Extension attribute actions"
        )

        # List action (default)
        list_parser = subparsers.add_parser("list", help="List extension attributes")
        list_parser.add_argument(
            "--type",
            choices=["computer", "mobile", "user", "all"],
            default="all",
            help="Filter by attribute type",
        )
        list_parser.add_argument(
            "--data-type",
            choices=["String", "Integer", "Date", "Boolean"],
            help="Filter by data type",
        )
        list_parser.add_argument(
            "--input-type",
            choices=["Text Field", "Pop-up Menu", "Script", "LDAP Mapping"],
            help="Filter by input type",
        )
        self.setup_common_args(list_parser)

        # Create action
        create_parser = subparsers.add_parser(
            "create", help="Create extension attribute"
        )
        create_parser.add_argument(
            "type",
            choices=["computer", "mobile", "user"],
            help="Extension attribute type",
        )
        create_parser.add_argument("name", help="Extension attribute name")
        create_parser.add_argument(
            "--description", help="Extension attribute description"
        )
        create_parser.add_argument(
            "--data-type",
            choices=["String", "Integer", "Date", "Boolean"],
            default="String",
            help="Data type",
        )
        create_parser.add_argument(
            "--input-type",
            choices=["Text Field", "Pop-up Menu", "Script", "LDAP Mapping"],
            default="Text Field",
            help="Input type",
        )
        create_parser.add_argument(
            "--enabled",
            action="store_true",
            default=True,
            help="Enable the extension attribute",
        )
        self.setup_common_args(create_parser)

        # Update action
        update_parser = subparsers.add_parser(
            "update", help="Update extension attribute"
        )
        update_parser.add_argument("id", help="Extension attribute ID")
        update_parser.add_argument(
            "--type",
            choices=["computer", "mobile", "user"],
            default="computer",
            help="Extension attribute type",
        )
        update_parser.add_argument(
            "--name", help="New name for the extension attribute"
        )
        update_parser.add_argument(
            "--description", help="New description for the extension attribute"
        )
        update_parser.add_argument(
            "--enabled", type=bool, help="Enable/disable the extension attribute"
        )
        self.setup_common_args(update_parser)

        # Delete action
        delete_parser = subparsers.add_parser(
            "delete", help="Delete extension attribute"
        )
        delete_parser.add_argument("id", help="Extension attribute ID")
        delete_parser.add_argument(
            "--type",
            choices=["computer", "mobile", "user"],
            default="computer",
            help="Extension attribute type",
        )
        delete_parser.add_argument(
            "--force", action="store_true", help="Force deletion without confirmation"
        )
        self.setup_common_args(delete_parser)

        # Set default action to list for backward compatibility
        parser.set_defaults(attr_action="list")

    def execute(self, args: Namespace, auth: UnifiedJamfAuth) -> int:
        """Execute the extension attributes command"""
        self.auth = auth

        # Handle different actions
        if args.attr_action == "list":
            return self._list_attributes(args.type, args)
        elif args.attr_action == "create":
            return self._handle_create(args, auth)
        elif args.attr_action == "update":
            return self._handle_update(args, auth)
        elif args.attr_action == "delete":
            return self._handle_delete(args, auth)
        else:
            # Default to list for backward compatibility
            return self._list_attributes(args.type, args)

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
            # API endpoint mapping
            endpoints = {
                "computer": "/JSSResource/computerextensionattributes",
                "mobile": "/JSSResource/mobiledeviceextensionattributes",
                "user": "/JSSResource/userextensionattributes",
            }

            if attribute_type == "all":
                # List all types
                all_attributes = []
                for attr_type_name, endpoint in endpoints.items():
                    attributes = self._fetch_attributes(endpoint, attr_type_name)
                    all_attributes.extend(attributes)
                attributes = all_attributes
            else:
                endpoint = endpoints.get(attribute_type)
                if not endpoint:
                    print(f"❌ Unknown attribute type: {attribute_type}")
                    return 1
                attributes = self._fetch_attributes(endpoint, attribute_type)

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
                f"\n✅ Found {len(filtered_attributes)} {attribute_type} extension attributes"
            )
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _fetch_attributes(
        self, endpoint: str, attribute_type: str
    ) -> List[Dict[str, Any]]:
        """Fetch attributes from API endpoint"""
        print(f"🔧 Fetching {attribute_type} extension attributes...")
        response = self.auth.api_request("GET", endpoint)

        # Extract attributes from response based on type
        if attribute_type == "computer":
            if "computer_extension_attributes" in response:
                attrs_data = response["computer_extension_attributes"]
                if "extension_attribute" in attrs_data:
                    attributes = attrs_data["extension_attribute"]
                    return attributes if isinstance(attributes, list) else [attributes]

        elif attribute_type == "mobile":
            if "mobile_device_extension_attributes" in response:
                attrs_data = response["mobile_device_extension_attributes"]
                if "extension_attribute" in attrs_data:
                    attributes = attrs_data["extension_attribute"]
                    return attributes if isinstance(attributes, list) else [attributes]

        elif attribute_type == "user":
            if "user_extension_attributes" in response:
                attrs_data = response["user_extension_attributes"]
                if "extension_attribute" in attrs_data:
                    attributes = attrs_data["extension_attribute"]
                    return attributes if isinstance(attributes, list) else [attributes]

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
                if "input_type" in attr and attr["input_type"].get("type") == "Script":
                    script = attr["input_type"].get("script", {})
                    if script:
                        formatted_attr["Script Name"] = script.get("name", "")
                        formatted_attr["Script ID"] = script.get("id", "")

            formatted.append(formatted_attr)

        return formatted

    def _determine_attribute_type(self, attr: Dict[str, Any]) -> str:
        """Determine attribute type from attribute data"""
        # This is a simplified approach - in practice, you might need to track
        # the source endpoint or add metadata to determine the type
        if "computer_extension_attribute" in str(attr):
            return "Computer"
        elif "mobile_device_extension_attribute" in str(attr):
            return "Mobile"
        elif "user_extension_attribute" in str(attr):
            return "User"
        else:
            return "Unknown"

    def _get_input_type(self, attr: Dict[str, Any]) -> str:
        """Get input type from attribute"""
        input_type = attr.get("input_type", {})
        if isinstance(input_type, dict):
            return input_type.get("type", "Unknown")
        return str(input_type) if input_type else "Unknown"

    def _handle_create(self, args: Namespace, auth: UnifiedJamfAuth) -> int:
        """Handle extension attribute creation"""
        try:
            print(f"🔧 Creating {args.type} extension attribute: {args.name}")

            # API endpoint mapping
            endpoints = {
                "computer": "/JSSResource/computerextensionattributes",
                "mobile": "/JSSResource/mobiledeviceextensionattributes",
                "user": "/JSSResource/userextensionattributes",
            }

            endpoint = endpoints.get(args.type)
            if not endpoint:
                print(f"❌ Unknown attribute type: {args.type}")
                return 1

            # Build extension attribute data
            attr_data = {
                "extension_attribute": {
                    "name": args.name,
                    "description": getattr(args, "description", ""),
                    "data_type": getattr(args, "data_type", "String"),
                    "input_type": {"type": getattr(args, "input_type", "Text Field")},
                    "enabled": getattr(args, "enabled", True),
                    "inventory_display": "General",
                    "recon_display": "General",
                }
            }

            # Make API request
            response = auth.api_request("POST", endpoint, data=attr_data)

            if response:
                print("✅ Extension attribute created successfully!")
                if hasattr(response, "get") and response.get("id"):
                    print(f"   ID: {response['id']}")
                return 0
            else:
                print("❌ Failed to create extension attribute: No response from API")
                return 1

        except Exception as e:
            print(f"❌ Failed to create extension attribute: {e}")
            return 1

    def _handle_update(self, args: Namespace, auth: UnifiedJamfAuth) -> int:
        """Handle extension attribute update"""
        try:
            print(f"🔧 Updating {args.type} extension attribute: {args.id}")

            # API endpoint mapping
            endpoints = {
                "computer": f"/JSSResource/computerextensionattributes/id/{args.id}",
                "mobile": f"/JSSResource/mobiledeviceextensionattributes/id/{args.id}",
                "user": f"/JSSResource/userextensionattributes/id/{args.id}",
            }

            endpoint = endpoints.get(args.type)
            if not endpoint:
                print(f"❌ Unknown attribute type: {args.type}")
                return 1

            # First, get the existing attribute
            get_response = auth.api_request("GET", endpoint)
            if not get_response:
                print(f"❌ Extension attribute with ID {args.id} not found")
                return 1

            # Extract the extension attribute data
            attr_key = f"{args.type}_extension_attribute"
            if attr_key not in get_response:
                print(f"❌ Invalid response format for {args.type} extension attribute")
                return 1

            attr_data = get_response[attr_key]

            # Update fields if provided
            if hasattr(args, "name") and args.name:
                attr_data["name"] = args.name
            if hasattr(args, "description") and args.description is not None:
                attr_data["description"] = args.description
            if hasattr(args, "enabled") and args.enabled is not None:
                attr_data["enabled"] = args.enabled

            # Prepare update data
            update_data = {attr_key: attr_data}

            # Make API request
            response = auth.api_request("PUT", endpoint, data=update_data)

            if response:
                print("✅ Extension attribute updated successfully!")
                return 0
            else:
                print("❌ Failed to update extension attribute: No response from API")
                return 1

        except Exception as e:
            print(f"❌ Failed to update extension attribute: {e}")
            return 1

    def _handle_delete(self, args: Namespace, auth: UnifiedJamfAuth) -> int:
        """Handle extension attribute deletion"""
        try:
            print(f"🗑️ Deleting {args.type} extension attribute: {args.id}")

            # Confirmation unless force flag is used
            if not getattr(args, "force", False):
                confirm = input(
                    f"Are you sure you want to delete {args.type} extension attribute {args.id}? (y/N): "
                )
                if confirm.lower() not in ["y", "yes"]:
                    print("❌ Deletion cancelled")
                    return 1

            # API endpoint mapping
            endpoints = {
                "computer": f"/JSSResource/computerextensionattributes/id/{args.id}",
                "mobile": f"/JSSResource/mobiledeviceextensionattributes/id/{args.id}",
                "user": f"/JSSResource/userextensionattributes/id/{args.id}",
            }

            endpoint = endpoints.get(args.type)
            if not endpoint:
                print(f"❌ Unknown attribute type: {args.type}")
                return 1

            # Make API request
            response = auth.api_request("DELETE", endpoint)

            if response is not None:  # DELETE can return empty response on success
                print("✅ Extension attribute deleted successfully!")
                return 0
            else:
                print("❌ Failed to delete extension attribute: No response from API")
                return 1

        except Exception as e:
            print(f"❌ Failed to delete extension attribute: {e}")
            return 1
