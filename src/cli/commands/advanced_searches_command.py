#!/usr/bin/env python3
"""
Advanced Searches Command for jpapi CLI
Handles advanced computer searches, mobile device searches, and user searches
"""

from .common_imports import (
    ArgumentParser,
    Namespace,
    Dict,
    Any,
    List,
    Optional,
    Path,
    BaseCommand,
)
from core.logging.command_mixin import log_operation
from core.auth.login_manager import UnifiedJamfAuth


class AdvancedSearchesCommand(BaseCommand):
    """Advanced searches command for JAMF Pro advanced search functionality"""

    def __init__(self):
        super().__init__(
            name="advanced-searches",
            description="🔍 Advanced searches (computer, mobile, user searches)",
        )
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup conversational patterns for advanced searches management"""

        # Create searches
        self.add_conversational_pattern(
            pattern="create computer search",
            handler="_create_computer_search",
            description="Create advanced computer search",
            aliases=["create computer", "new computer", "add computer"],
        )

        self.add_conversational_pattern(
            pattern="create mobile search",
            handler="_create_mobile_search",
            description="Create advanced mobile device search",
            aliases=["create mobile", "new mobile", "add mobile"],
        )

        self.add_conversational_pattern(
            pattern="create user search",
            handler="_create_user_search",
            description="Create advanced user search",
            aliases=["create user", "new user", "add user"],
        )

        # Update searches
        self.add_conversational_pattern(
            pattern="update computer search",
            handler="_update_computer_search",
            description="Update advanced computer search",
            aliases=["update computer", "modify computer", "edit computer"],
        )

        self.add_conversational_pattern(
            pattern="update mobile search",
            handler="_update_mobile_search",
            description="Update advanced mobile device search",
            aliases=["update mobile", "modify mobile", "edit mobile"],
        )

        self.add_conversational_pattern(
            pattern="update user search",
            handler="_update_user_search",
            description="Update advanced user search",
            aliases=["update user", "modify user", "edit user"],
        )

        # Delete searches
        self.add_conversational_pattern(
            pattern="delete computer search",
            handler="_delete_computer_search",
            description="Delete advanced computer search",
            aliases=["delete computer", "remove computer"],
        )

        self.add_conversational_pattern(
            pattern="delete mobile search",
            handler="_delete_mobile_search",
            description="Delete advanced mobile device search",
            aliases=["delete mobile", "remove mobile"],
        )

        self.add_conversational_pattern(
            pattern="delete user search",
            handler="_delete_user_search",
            description="Delete advanced user search",
            aliases=["delete user", "remove user"],
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        super().add_arguments(parser)

        # Add common arguments for CRUD operations
        parser.add_argument("--name", help="Search name")
        parser.add_argument("--description", help="Search description")
        parser.add_argument("--id", help="Search ID for update/delete operations")
        parser.add_argument("--criteria", help="Search criteria (JSON string)")
        parser.add_argument("--display-fields", help="Display fields (comma-separated)")

    def _setup_list_arguments(self, parser: ArgumentParser) -> None:
        """Setup arguments for list command"""
        # Add search type filtering
        parser.add_argument(
            "--type",
            choices=["computer", "mobile", "user", "all"],
            default="all",
            help="Filter by search type",
        )

        # Add search criteria filtering
        parser.add_argument(
            "--smart-only",
            action="store_true",
            help="Show only smart searches (dynamic criteria)",
        )

        parser.add_argument(
            "--static-only",
            action="store_true",
            help="Show only static searches (manual assignment)",
        )

    def execute(self, args: Namespace) -> int:
        """Execute the advanced searches command"""
        if not self.check_auth(args):
            return 1

        # Store args for save_output method
        self.current_args = args

        # Use the conversational pattern system
        return super().execute(args)

    def _create_computer_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Create advanced computer search"""
        return self._create_search("computer", args)

    def _create_mobile_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Create advanced mobile device search"""
        return self._create_search("mobile", args)

    def _create_user_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Create advanced user search"""
        return self._create_search("user", args)

    def _update_computer_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Update advanced computer search"""
        return self._update_search("computer", args)

    def _update_mobile_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Update advanced mobile device search"""
        return self._update_search("mobile", args)

    def _update_user_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Update advanced user search"""
        return self._update_search("user", args)

    def _delete_computer_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Delete advanced computer search"""
        return self._delete_search("computer", args)

    def _delete_mobile_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Delete advanced mobile device search"""
        return self._delete_search("mobile", args)

    def _delete_user_search(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Delete advanced user search"""
        return self._delete_search("user", args)

    @log_operation("Advanced Searches List")
    def _list_searches(self, search_type: str, args: Namespace) -> int:
        """Generic method to list advanced searches"""
        try:
            self.log_info(f"Fetching {search_type} advanced searches...")

            # API endpoint mapping
            endpoints = {
                "computer": "/JSSResource/advancedcomputersearches",
                "mobile": "/JSSResource/advancedmobiledevicesearches",
                "user": "/JSSResource/advancedusersearches",
            }

            if search_type == "all":
                # List all types
                all_searches = []
                for search_type_name, endpoint in endpoints.items():
                    searches = self._fetch_searches(endpoint, search_type_name)
                    all_searches.extend(searches)
                searches = all_searches
            else:
                endpoint = endpoints.get(search_type)
                if not endpoint:
                    print(f"❌ Unknown search type: {search_type}")
                    return 1
                searches = self._fetch_searches(endpoint, search_type)

            if not searches:
                print(f"❌ No {search_type} searches found")
                return 1

            # Apply filtering
            filtered_searches = self._apply_search_filters(searches, args)

            # Format and output
            formatted_data = self._format_searches_for_display(filtered_searches, args)
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)

            print(f"\n✅ Found {len(filtered_searches)} {search_type} searches")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _fetch_searches(self, endpoint: str, search_type: str) -> List[Dict[str, Any]]:
        """Fetch searches from API endpoint"""
        print(f"🔍 Fetching {search_type} searches...")
        response = self.auth.api_request("GET", endpoint)

        # Extract searches from response based on type
        if search_type == "computer":
            if "advanced_computer_searches" in response:
                searches = response["advanced_computer_searches"]
                return searches if isinstance(searches, list) else [searches]

        elif search_type == "mobile":
            if "advanced_mobile_device_searches" in response:
                searches = response["advanced_mobile_device_searches"]
                return searches if isinstance(searches, list) else [searches]

        elif search_type == "user":
            if "advanced_user_searches" in response:
                searches = response["advanced_user_searches"]
                return searches if isinstance(searches, list) else [searches]

        return []

    def _apply_search_filters(
        self, searches: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Apply filters to searches"""
        filtered = searches

        # Name filtering
        if hasattr(args, "filter") and args.filter:
            from src.lib.utils import create_filter

            filter_obj = create_filter(getattr(args, "filter_type", "wildcard"))
            original_count = len(filtered)
            filtered = filter_obj.filter_objects(filtered, "name", args.filter)
            print(f"🔍 Filtered from {original_count} to {len(filtered)} searches")

        # Smart/Static filtering
        if hasattr(args, "smart_only") and args.smart_only:
            filtered = [s for s in filtered if s.get("is_smart", False)]

        if hasattr(args, "static_only") and args.static_only:
            filtered = [s for s in filtered if not s.get("is_smart", True)]

        # Type filtering
        if hasattr(args, "type") and args.type != "all":
            type_mapping = {
                "computer": "advanced_computer_search",
                "mobile": "advanced_mobile_device_search",
                "user": "advanced_user_search",
            }
            search_type = type_mapping.get(args.type)
            if search_type:
                # This would need to be implemented based on how we track search types
                pass

        return filtered

    def _format_searches_for_display(
        self, searches: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format searches for display"""
        if not searches:
            return []

        formatted = []
        for search in searches:
            formatted_search = {
                "ID": search.get("id", ""),
                "Name": search.get("name", ""),
                "Type": self._determine_search_type(search),
                "Smart": search.get("is_smart", False),
                "Criteria": self._format_search_criteria(search),
                "delete": "",  # Empty column for manual deletion tracking
            }

            # Add detailed fields if requested
            if hasattr(args, "detailed") and args.detailed:
                if "site" in search:
                    site = search["site"]
                    if isinstance(site, dict):
                        formatted_search["Site"] = site.get("name", "")
                    else:
                        formatted_search["Site"] = site

                if "criteria" in search:
                    criteria_count = (
                        len(search["criteria"]) if search["criteria"] else 0
                    )
                    formatted_search["Criteria Count"] = criteria_count

                if "display_fields" in search:
                    fields_count = (
                        len(search["display_fields"]) if search["display_fields"] else 0
                    )
                    formatted_search["Display Fields"] = fields_count

            formatted.append(formatted_search)

        return formatted

    def save_output(self, content: str, output_path: Optional[str] = None) -> None:
        """Save output to file with default naming pattern or print to stdout"""
        if output_path:
            try:
                # Ensure directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(content)
                print(f"✅ Output saved to: {output_path}")
            except Exception as e:
                print(f"❌ Failed to save output: {e}")
                print(content)
        else:
            # Generate default filename with datestamp for CSV/JSON exports
            if (
                hasattr(self, "current_args")
                and self.current_args
                and self.current_args.format in ["csv", "json"]
            ):
                import time

                timestamp = time.strftime("%Y%m%d_%H%M%S")
                default_filename = f"data/csv-exports/advanced-searches-export-{timestamp}.{self.current_args.format}"

                try:
                    # Ensure directory exists
                    Path(default_filename).parent.mkdir(parents=True, exist_ok=True)
                    with open(default_filename, "w") as f:
                        f.write(content)
                    print(f"✅ Output saved to: {default_filename}")
                except Exception as e:
                    print(f"❌ Failed to save output: {e}")
                    print(content)
            else:
                print(content)

    def _determine_search_type(self, search: Dict[str, Any]) -> str:
        """Determine search type from search data"""
        # This is a simplified approach - in practice, you might need to track
        # the source endpoint or add metadata to determine the type
        if "advanced_computer_search" in str(search):
            return "Computer"
        elif "advanced_mobile_device_search" in str(search):
            return "Mobile"
        elif "advanced_user_search" in str(search):
            return "User"
        else:
            return "Unknown"

    def _format_search_criteria(self, search: Dict[str, Any]) -> str:
        """Format search criteria for display"""
        if "criteria" in search and search["criteria"]:
            criteria = search["criteria"]
            if isinstance(criteria, list) and criteria:
                # Show first criterion as example
                first_criteria = criteria[0]
                if isinstance(first_criteria, dict):
                    criterion_name = first_criteria.get("name", "Unknown")
                    criterion_value = first_criteria.get("value", "")
                    return f"{criterion_name}: {criterion_value}"
            return f"{len(criteria)} criteria"
        return "No criteria"

    def _create_search(self, search_type: str, args: Namespace) -> int:
        """Generic method to create advanced searches"""
        try:
            self.log_info(f"Creating {search_type} advanced search...")

            # Get search name from args
            search_name = getattr(args, "name", None)
            if not search_name:
                self.log_error("Search name is required. Use --name")
                return 1

            # Create search data
            search_data = {
                "name": search_name,
                "description": getattr(args, "description", ""),
                "criteria": getattr(args, "criteria", []),
                "display_fields": getattr(args, "display_fields", []),
            }

            # Determine endpoint based on search type
            endpoints = {
                "computer": "/JSSResource/advancedcomputersearches/id/0",
                "mobile": "/api/v1/advanced-mobile-device-searches",
                "user": "/JSSResource/advancedusersearches/id/0",
            }

            endpoint = endpoints.get(search_type)
            if not endpoint:
                self.log_error(f"Unknown search type: {search_type}")
                return 1

            # Create the search
            response = self.auth.api_request("POST", endpoint, data=search_data)

            if response:
                self.log_success(f"Created {search_type} search: {search_name}")
                return 0
            else:
                self.log_error("Failed to create search")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _update_search(self, search_type: str, args: Namespace) -> int:
        """Generic method to update advanced searches"""
        try:
            search_id = getattr(args, "id", None)
            if not search_id:
                self.log_error("Search ID is required. Use --id")
                return 1

            self.log_info(f"Updating {search_type} advanced search {search_id}...")

            # Get existing search first
            endpoints = {
                "computer": f"/JSSResource/advancedcomputersearches/id/{search_id}",
                "mobile": f"/api/v1/advanced-mobile-device-searches/{search_id}",
                "user": f"/JSSResource/advancedusersearches/id/{search_id}",
            }

            endpoint = endpoints.get(search_type)
            if not endpoint:
                self.log_error(f"Unknown search type: {search_type}")
                return 1

            # Get existing search
            existing_search = self.auth.api_request("GET", endpoint)
            if not existing_search:
                self.log_error(f"Search {search_id} not found")
                return 1

            # Update fields if provided
            if hasattr(args, "name") and args.name:
                existing_search["name"] = args.name
            if hasattr(args, "description") and args.description:
                existing_search["description"] = args.description
            if hasattr(args, "criteria") and args.criteria:
                existing_search["criteria"] = args.criteria
            if hasattr(args, "display_fields") and args.display_fields:
                existing_search["display_fields"] = args.display_fields

            # Update the search
            response = self.auth.api_request("PUT", endpoint, data=existing_search)

            if response:
                self.log_success(f"Updated {search_type} search: {search_id}")
                return 0
            else:
                self.log_error("Failed to update search")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _delete_search(self, search_type: str, args: Namespace) -> int:
        """Generic method to delete advanced searches"""
        try:
            search_id = getattr(args, "id", None)
            if not search_id:
                self.log_error("Search ID is required. Use --id")
                return 1

            self.log_info(f"Deleting {search_type} advanced search {search_id}...")

            # Determine endpoint based on search type
            endpoints = {
                "computer": f"/JSSResource/advancedcomputersearches/id/{search_id}",
                "mobile": f"/api/v1/advanced-mobile-device-searches/{search_id}",
                "user": f"/JSSResource/advancedusersearches/id/{search_id}",
            }

            endpoint = endpoints.get(search_type)
            if not endpoint:
                self.log_error(f"Unknown search type: {search_type}")
                return 1

            # Delete the search
            self.auth.api_request("DELETE", endpoint)
            self.log_success(f"Deleted {search_type} search: {search_id}")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _handle_create(self, args: Namespace, auth: UnifiedJamfAuth) -> int:
        """Handle create advanced search command"""
        try:
            print(f"🔍 Creating {args.type} advanced search: {args.name}")

            # Get endpoint based on search type
            endpoint = self._get_endpoint_for_type(args.type)
            if not endpoint:
                print(f"❌ Invalid search type: {args.type}")
                return 1

            # Create search data structure
            search_data = self._create_search_data_structure(args.name, args.type)

            # Make API request
            response = auth.api_request("POST", endpoint, search_data)

            if response and "id" in response:
                print(f"✅ Advanced search created successfully! ID: {response['id']}")
                return 0
            else:
                print("❌ Failed to create advanced search - no ID returned")
                return 1

        except Exception as e:
            print(f"❌ Failed to create advanced search: {e}")
            return 1

    def _handle_update(self, args: Namespace, auth: UnifiedJamfAuth) -> int:
        """Handle update advanced search command"""
        try:
            print(f"🔄 Updating advanced search: {args.id}")

            # First, get the existing search to determine its type
            search_type = self._get_search_type_by_id(args.id, auth)
            if not search_type:
                print(f"❌ Could not determine search type for ID: {args.id}")
                return 1

            # Get endpoint for update
            endpoint = f"{self._get_endpoint_for_type(search_type)}/id/{args.id}"

            # For now, we'll implement a basic update that preserves existing data
            # In a real implementation, you'd want to allow users to specify what to update
            print("⚠️  Update functionality requires additional parameters")
            print("   Use the JAMF Pro web interface for detailed updates")

            return 0

        except Exception as e:
            print(f"❌ Failed to update advanced search: {e}")
            return 1

    def _handle_delete(self, args: Namespace, auth: UnifiedJamfAuth) -> int:
        """Handle delete advanced search command"""
        # Check if this is a bulk delete from CSV file
        if hasattr(args, "csv_file") and args.csv_file:
            return self._handle_bulk_delete(args, auth)

        # Single ID deletion
        try:
            print(f"🗑️ Deleting advanced search: {args.id}")

            # First, get the existing search to determine its type
            search_type = self._get_search_type_by_id(args.id, auth)
            if not search_type:
                print(f"❌ Could not determine search type for ID: {args.id}")
                return 1

            # Get endpoint for deletion
            endpoint = f"{self._get_endpoint_for_type(search_type)}/id/{args.id}"

            # Confirm deletion
            confirm = (
                input(f"Are you sure you want to delete search ID {args.id}? (y/N): ")
                .lower()
                .strip()
            )
            if confirm not in ["y", "yes"]:
                print("❌ Deletion cancelled")
                return 1

            # Make API request
            response = auth.api_request("DELETE", endpoint)

            print("✅ Advanced search deleted successfully!")
            return 0

        except Exception as e:
            print(f"❌ Failed to delete advanced search: {e}")
            return 1

    def _handle_bulk_delete(self, args: Namespace, auth: UnifiedJamfAuth) -> int:
        """Handle bulk delete from CSV file"""
        import csv
        from pathlib import Path

        try:
            csv_file = Path(args.csv_file)

            # Read CSV file
            searches_to_delete = []
            with open(csv_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check if delete column has a value (any non-empty value means delete)
                    delete_value = row.get("delete", "").strip()
                    if delete_value:
                        searches_to_delete.append(
                            {
                                "id": row.get("ID", ""),
                                "name": row.get("Name", ""),
                                "type": row.get("Type", "Unknown"),
                                "delete_reason": delete_value,
                            }
                        )

            if not searches_to_delete:
                print("✅ No searches marked for deletion in CSV file")
                return 0

            print(f"\n📋 Found {len(searches_to_delete)} searches marked for deletion:")
            for search in searches_to_delete:
                print(
                    f"   • {search['name']} (ID: {search['id']}, Type: {search['type']}) - Reason: {search['delete_reason']}"
                )

            if hasattr(args, "dry_run") and args.dry_run:
                print("\n🔍 DRY RUN - No changes will be made")
                return 0

            # Confirm deletion
            if not (hasattr(args, "confirm") and args.confirm):
                response = input(
                    f"\n⚠️  Are you sure you want to delete {len(searches_to_delete)} advanced searches? (yes/no): "
                )
                if response.lower() not in ["yes", "y"]:
                    print("❌ Deletion cancelled")
                    return 0

            # Delete searches with timeout protection and retry logic
            deleted_count = 0
            failed_count = 0
            retry_count = 3  # Number of retries for failed deletions
            retry_delay = 2  # Delay between retries in seconds

            for search in searches_to_delete:
                success = False
                last_error = None

                for attempt in range(retry_count):
                    try:
                        if attempt > 0:
                            print(
                                f"   🔄 Retry {attempt}/{retry_count-1} for: {search['name']}"
                            )
                            import time

                            time.sleep(retry_delay)

                        print(
                            f"🗑️  Deleting search: {search['name']} (ID: {search['id']})"
                        )

                        # Determine search type and get endpoint
                        search_type = self._get_search_type_by_id(search["id"], auth)
                        if not search_type:
                            print(
                                f"   ❌ Could not determine search type for ID: {search['id']}"
                            )
                            break  # Don't retry if we can't determine type

                        endpoint = f"{self._get_endpoint_for_type(search_type)}/id/{search['id']}"

                        # Delete via JAMF API with timeout handling
                        try:
                            response = auth.api_request("DELETE", endpoint)
                            if response is not None:
                                print(f"   ✅ Deleted: {search['name']}")
                                deleted_count += 1
                                success = True
                                break
                            else:
                                print(
                                    f"   ❌ Failed to delete: {search['name']} (no response)"
                                )
                                last_error = "No response from API"
                        except Exception as api_error:
                            error_msg = str(api_error)
                            if (
                                "timeout" in error_msg.lower()
                                or "timed out" in error_msg.lower()
                            ):
                                print(
                                    f"   ⏰ Timeout on attempt {attempt + 1}: {search['name']}"
                                )
                                last_error = f"Timeout: {error_msg}"
                            elif (
                                "401" in error_msg
                                or "unauthorized" in error_msg.lower()
                            ):
                                print(f"   🔒 Permission denied: {search['name']}")
                                last_error = f"Permission denied: {error_msg}"
                                break  # Don't retry permission errors
                            else:
                                print(
                                    f"   ❌ API error on attempt {attempt + 1}: {error_msg}"
                                )
                                last_error = f"API error: {error_msg}"

                    except Exception as e:
                        error_msg = str(e)
                        print(f"   ❌ Error on attempt {attempt + 1}: {error_msg}")
                        last_error = f"General error: {error_msg}"

                        # Don't retry certain types of errors
                        if "could not determine search type" in error_msg.lower():
                            break

                if not success:
                    print(
                        f"   ❌ Failed to delete after {retry_count} attempts: {search['name']}"
                    )
                    if last_error:
                        print(f"   📝 Last error: {last_error}")
                    failed_count += 1

            # Summary
            print(f"\n📊 Deletion Summary:")
            print(f"   ✅ Successfully deleted: {deleted_count}")
            if failed_count > 0:
                print(f"   ❌ Failed to delete: {failed_count}")

            return 0 if failed_count == 0 else 1

        except Exception as e:
            print(f"❌ Error processing CSV file: {e}")
            return 1

    def _get_endpoint_for_type(self, search_type: str) -> Optional[str]:
        """Get API endpoint for search type"""
        endpoints = {
            "computer": "/JSSResource/advancedcomputersearches",
            "mobile": "/JSSResource/advancedmobiledevicesearches",
            "user": "/JSSResource/advancedusersearches",
        }
        return endpoints.get(search_type)

    def _get_search_type_by_id(
        self, search_id: str, auth: UnifiedJamfAuth
    ) -> Optional[str]:
        """Determine search type by checking which endpoint contains the ID"""
        search_types = ["computer", "mobile", "user"]

        for search_type in search_types:
            endpoint = self._get_endpoint_for_type(search_type)
            if endpoint:
                try:
                    response = auth.api_request("GET", endpoint)
                    searches = self._extract_searches_from_response(
                        response, search_type
                    )

                    # Check if any search has the matching ID
                    for search in searches:
                        if str(search.get("id", "")) == str(search_id):
                            return search_type
                except Exception:
                    continue

        return None

    def _extract_searches_from_response(
        self, response: Dict[str, Any], search_type: str
    ) -> List[Dict[str, Any]]:
        """Extract searches from API response based on type"""
        if search_type == "computer":
            if "advanced_computer_searches" in response:
                searches = response["advanced_computer_searches"]
                return searches if isinstance(searches, list) else [searches]
        elif search_type == "mobile":
            if "advanced_mobile_device_searches" in response:
                searches = response["advanced_mobile_device_searches"]
                return searches if isinstance(searches, list) else [searches]
        elif search_type == "user":
            if "advanced_user_searches" in response:
                searches = response["advanced_user_searches"]
                return searches if isinstance(searches, list) else [searches]

        return []

    def _create_search_data_structure(
        self, name: str, search_type: str
    ) -> Dict[str, Any]:
        """Create basic search data structure for new searches"""
        base_structure = {
            "name": name,
            "is_smart": True,  # Default to smart search
            "criteria": [],
            "display_fields": [],
            "site": {"id": -1, "name": "None"},
        }

        # Add type-specific fields
        if search_type == "computer":
            base_structure["computers"] = []
        elif search_type == "mobile":
            base_structure["mobile_devices"] = []
        elif search_type == "user":
            base_structure["users"] = []

        return base_structure
