#!/usr/bin/env python3
"""
Improved Devices Command for jpapi CLI
Uses existing libraries instead of duplicating functionality - reduces from 625 to ~100 lines
"""

from .common_imports import (
    Namespace,
    Dict,
    Any,
    List,
    Optional,
    BaseCommand,
)
from lib.managers import ComputerManager, MobileDeviceManager
from pathlib import Path


class DevicesCommand(BaseCommand):
    """Improved devices command using existing libraries"""

    def __init__(self):
        super().__init__(
            name="devices",
            description="📱 Device management operations (uses existing libraries)",
        )
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup conversational patterns for device operations"""

        # Computer device operations
        self.add_conversational_pattern(
            pattern="mac info",
            handler="_device_info",
            description="Get computer information",
            aliases=["computer", "macos", "comp"],
        )

        self.add_conversational_pattern(
            pattern="mac list",
            handler="_list_computers",
            description="List all computers",
            aliases=["computer", "macos", "comp"],
        )

        self.add_conversational_pattern(
            pattern="mac update",
            handler="_update_computer",
            description="Update computer inventory",
            aliases=["computer", "macos", "comp"],
        )

        # Bulk lock MUST come before single device lock patterns
        # to prevent "bulk lock" from matching "mac lock" or "ios lock"
        self.add_conversational_pattern(
            pattern="bulk lock",
            handler="_bulk_lock_from_csv",
            description="Bulk lock devices from CSV with usernames/emails",
            aliases=["lock csv", "csv lock", "bulk-lock"],
        )

        self.add_conversational_pattern(
            pattern="mac lock",
            handler="_lock_computer",
            description="Lock computer with passcode",
            aliases=["computer lock", "macos lock", "comp lock"],
        )

        # Mobile device operations
        self.add_conversational_pattern(
            pattern="ios info",
            handler="_device_info",
            description="Get mobile device information",
            aliases=["mobile", "ipad", "iphone"],
        )

        self.add_conversational_pattern(
            pattern="ios list",
            handler="_list_mobile_devices",
            description="List all mobile devices",
            aliases=["mobile", "ipad", "iphone"],
        )

        self.add_conversational_pattern(
            pattern="ios update",
            handler="_update_mobile",
            description="Update mobile device inventory",
            aliases=["mobile", "ipad", "iphone"],
        )

        self.add_conversational_pattern(
            pattern="ios lock",
            handler="_lock_mobile",
            description="Lock mobile device with passcode",
            aliases=["mobile lock", "ipad lock", "iphone lock"],
        )

        # Generic device operations
        self.add_conversational_pattern(
            pattern="devices list",
            handler="_list_all_devices",
            description="List all devices (computers and mobile)",
            aliases=["list devices", "all devices"],
        )

    def _device_info(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """
        Get device information using existing libraries

        Args:
            args: Parsed command line arguments
            pattern: Optional pattern match information

        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        try:
            device_id = args.terms[0] if args.terms else None
            if not device_id:
                print("❌ Please specify a device ID, name, or serial number")
                return 1

            # Determine device type from pattern
            device_type = self._get_device_type_from_pattern(pattern)

            if device_type == "computer":
                return self._get_computer_info(device_id, args)
            elif device_type == "mobile":
                return self._get_mobile_info(device_id, args)
            else:
                print("❌ Could not determine device type")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _list_computers(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List computers using ComputerManager library"""
        try:
            print("🖥️  Listing computers...")

            computer_manager = ComputerManager(self.auth)
            computers = computer_manager.get_all_computers()

            if not computers:
                print("❌ No computers found")
                return 1

            # Apply filtering
            if hasattr(args, "filter") and args.filter:
                computers = self._apply_device_filter(computers, args.filter, "name")

            # Format for display
            formatted_data = self._format_computers_for_display(computers, args)
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)

            print(f"\n✅ Found {len(computers)} computers")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _list_mobile_devices(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """List mobile devices using MobileDeviceManager library"""
        try:
            print("📱 Listing mobile devices...")

            mobile_manager = MobileDeviceManager(self.auth)
            devices = mobile_manager.get_all_mobile_devices()

            if not devices:
                print("❌ No mobile devices found")
                return 1

            # Apply filtering
            if hasattr(args, "filter") and args.filter:
                devices = self._apply_device_filter(devices, args.filter, "name")

            # Format for display
            formatted_data = self._format_mobile_devices_for_display(devices, args)
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)

            print(f"\n✅ Found {len(devices)} mobile devices")
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _list_all_devices(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List all devices using both libraries"""
        try:
            print("📱🖥️  Listing all devices...")

            # Get computers
            computer_manager = ComputerManager(self.auth)
            computers = computer_manager.get_all_computers()

            # Get mobile devices
            mobile_manager = MobileDeviceManager(self.auth)
            mobile_devices = mobile_manager.get_all_mobile_devices()

            # Format and combine
            all_devices = []

            # Add computers
            for computer in computers:
                device_info = {
                    "Type": "Computer",
                    "ID": computer.get("id", ""),
                    "Name": computer.get("general", {}).get("name", ""),
                    "Model": computer.get("hardware", {}).get("model", ""),
                    "OS Version": computer.get("general", {}).get("os_version", ""),
                    "Serial": computer.get("general", {}).get("serial_number", ""),
                    "Last Contact": computer.get("general", {}).get(
                        "last_contact_time", ""
                    ),
                }
                all_devices.append(device_info)

            # Add mobile devices
            for device in mobile_devices:
                device_info = {
                    "Type": "Mobile",
                    "ID": device.get("id", ""),
                    "Name": device.get("general", {}).get("name", ""),
                    "Model": device.get("general", {}).get("model", ""),
                    "OS Version": device.get("general", {}).get("os_version", ""),
                    "Serial": device.get("general", {}).get("serial_number", ""),
                    "Last Contact": device.get("general", {}).get(
                        "last_inventory_update", ""
                    ),
                }
                all_devices.append(device_info)

            if not all_devices:
                print("❌ No devices found")
                return 1

            # Apply filtering
            if hasattr(args, "filter") and args.filter:
                all_devices = self._apply_device_filter(
                    all_devices, args.filter, "Name"
                )

            # Output
            output = self.format_output(all_devices, args.format)
            self.save_output(output, args.output)

            print(
                f"\n✅ Found {len(all_devices)} total devices ({len(computers)} computers, {len(mobile_devices)} mobile)"
            )
            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _update_computer(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Update computer inventory using direct API call"""
        try:
            device_id = args.terms[0] if args.terms else None
            if not device_id:
                print("❌ Please specify a device ID, name, or serial number")
                return 1

            print(f"🔄 Updating computer inventory: {device_id}")

            # Find computer first
            computer = self._find_device_by_identifier(device_id, "computer")
            if not computer:
                return 1

            # Send inventory update command
            response = self.auth.api_request(
                "POST",
                f'/JSSResource/computercommands/command/UpdateInventory/id/{computer["id"]}',
            )

            if response:
                print(f"✅ Inventory update sent to {computer['name']}")
                return 0
            else:
                print("❌ Failed to send inventory update")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _update_mobile(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Update mobile device inventory using direct API call"""
        try:
            device_id = args.terms[0] if args.terms else None
            if not device_id:
                print("❌ Please specify a device ID, name, or serial number")
                return 1

            print(f"🔄 Updating mobile device inventory: {device_id}")

            # Find mobile device first
            device = self._find_device_by_identifier(device_id, "mobile")
            if not device:
                return 1

            # Send inventory update command
            response = self.auth.api_request(
                "POST",
                f'/JSSResource/mobiledevicecommands/command/UpdateInventory/id/{device["id"]}',
            )

            if response:
                print(f"✅ Inventory update sent to {device['name']}")
                return 0
            else:
                print("❌ Failed to send inventory update")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _lock_computer(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Lock computer with passcode using direct API call"""
        try:
            device_id = args.terms[0] if args.terms else None
            passcode = args.terms[1] if args.terms and len(args.terms) > 1 else None

            if not device_id:
                print("❌ Please specify a device ID, name, or serial number")
                return 1

            if not passcode:
                print("❌ Please specify a passcode to lock the device")
                print("   Usage: jpapi devices mac lock <device_id> <passcode>")
                return 1

            # Try direct lookup by ID first (more efficient for known IDs)
            computer = None
            computer_id = None
            computer_name = device_id

            # If device_id is numeric, try direct API lookup first
            if device_id.isdigit():
                try:
                    response = self.auth.api_request(
                        "GET", f"/JSSResource/computers/id/{device_id}"
                    )
                    if response and "computer" in response:
                        computer = response["computer"]
                        computer_id = computer.get("id", device_id)
                        computer_name = computer.get("general", {}).get(
                            "name", device_id
                        )
                except Exception:
                    pass  # Fall through to list-based search

            # If direct lookup didn't work, try list-based search
            if not computer:
                computer = self._find_device_by_identifier(device_id, "computer")
                if not computer:
                    print(f"❌ Computer not found: {device_id}")
                    print("   Please verify the device ID, name, or serial number")
                    return 1
                computer_id = computer.get("id", "")
                computer_name = computer.get("general", {}).get("name", device_id)

            # Production safety checks
            if self.is_production_environment():
                changes_summary = f"""
Device Lock Summary:
  • Device ID: {computer_id}
  • Device Name: {computer_name}
  • Serial Number: {computer.get('general', {}).get('serial_number', 'N/A')}
  • Action: LOCK DEVICE
  • Passcode: {'*' * len(passcode)} (hidden for security)
  • Impact: Device will be immediately locked and require passcode to unlock
  • Scope: ONLY this specific device will be locked
  • Risk Level: HIGH - Device will be locked immediately
  • Recovery: Device can be unlocked with the provided passcode
"""

                if not self.require_production_confirmation(
                    "Lock Computer",
                    f"Locking computer: {computer_name} (ID: {computer_id})",
                    changes_summary,
                    args,
                ):
                    print("❌ Operation cancelled - production safety check failed")
                    return 1

            # Dry-run mode
            if getattr(args, "dry_run", False):
                print("🔍 DRY-RUN MODE: Would lock computer")
                print(f"   Device ID: {computer_id}")
                print(f"   Device Name: {computer_name}")
                print(
                    f"   Serial Number: {computer.get('general', {}).get('serial_number', 'N/A')}"
                )
                print(f"   Passcode: {'*' * len(passcode)} (hidden)")
                print(
                    f"   Endpoint: /JSSResource/computercommands/command/DeviceLock/passcode/****/id/{computer_id}"
                )
                print(
                    "\n✅ Dry-run complete. Use without --dry-run to actually lock the device."
                )
                return 0

            print(f"🔒 Locking computer: {computer_name} (ID: {computer_id})")

            # Send lock command with passcode
            endpoint = f"/JSSResource/computercommands/command/DeviceLock/passcode/{passcode}/id/{computer_id}"
            response = self.auth.api_request("POST", endpoint)

            if response:
                print(f"✅ Lock command sent to {computer_name}")
                print(f"   Device ID: {computer_id}")
                print(f"   Device will be locked with the provided passcode")
                print(
                    f"   Passcode: {'*' * len(passcode)} (save this for your records)"
                )
                return 0
            else:
                print("❌ Failed to send lock command")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _lock_mobile(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """Lock mobile device with passcode using direct API call"""
        try:
            device_id = args.terms[0] if args.terms else None
            passcode = args.terms[1] if args.terms and len(args.terms) > 1 else None

            if not device_id:
                print("❌ Please specify a device ID, name, or serial number")
                return 1

            if not passcode:
                print("❌ Please specify a passcode to lock the device")
                print("   Usage: jpapi devices ios lock <device_id> <passcode>")
                return 1

            # Try direct lookup by ID first (more efficient for known IDs)
            device = None
            device_id_num = None
            device_name = device_id

            # If device_id is numeric, try direct API lookup first
            if device_id.isdigit():
                try:
                    response = self.auth.api_request(
                        "GET", f"/JSSResource/mobiledevices/id/{device_id}"
                    )
                    if response and "mobile_device" in response:
                        device = response["mobile_device"]
                        device_id_num = device.get("id", device_id)
                        device_name = device.get("general", {}).get("name", device_id)
                except Exception:
                    pass  # Fall through to list-based search

            # If direct lookup didn't work, try list-based search
            if not device:
                device = self._find_device_by_identifier(device_id, "mobile")
                if not device:
                    print(f"❌ Mobile device not found: {device_id}")
                    print("   Please verify the device ID, name, or serial number")
                    return 1
                device_id_num = device.get("id", "")
                device_name = device.get("general", {}).get("name", device_id)

            # Production safety checks
            if self.is_production_environment():
                changes_summary = f"""
Device Lock Summary:
  • Device ID: {device_id_num}
  • Device Name: {device_name}
  • Serial Number: {device.get('general', {}).get('serial_number', 'N/A')}
  • UDID: {device.get('general', {}).get('udid', 'N/A')}
  • Action: LOCK DEVICE
  • Passcode: {'*' * len(passcode)} (hidden for security)
  • Impact: Device will be immediately locked and require passcode to unlock
  • Scope: ONLY this specific device will be locked
  • Risk Level: HIGH - Device will be locked immediately
  • Recovery: Device can be unlocked with the provided passcode
"""

                if not self.require_production_confirmation(
                    "Lock Mobile Device",
                    f"Locking mobile device: {device_name} (ID: {device_id_num})",
                    changes_summary,
                    args,
                ):
                    print("❌ Operation cancelled - production safety check failed")
                    return 1

            # Dry-run mode
            if getattr(args, "dry_run", False):
                print("🔍 DRY-RUN MODE: Would lock mobile device")
                print(f"   Device ID: {device_id_num}")
                print(f"   Device Name: {device_name}")
                print(
                    f"   Serial Number: {device.get('general', {}).get('serial_number', 'N/A')}"
                )
                print(f"   Passcode: {'*' * len(passcode)} (hidden)")
                print(
                    f"   Endpoint: /JSSResource/mobiledevicecommands/command/DeviceLock/passcode/****/id/{device_id_num}"
                )
                print(
                    "\n✅ Dry-run complete. Use without --dry-run to actually lock the device."
                )
                return 0

            print(f"🔒 Locking mobile device: {device_name} (ID: {device_id_num})")

            # Send lock command with passcode
            endpoint = f"/JSSResource/mobiledevicecommands/command/DeviceLock/passcode/{passcode}/id/{device_id_num}"
            response = self.auth.api_request("POST", endpoint)

            if response:
                print(f"✅ Lock command sent to {device_name}")
                print(f"   Device ID: {device_id_num}")
                print(f"   Device will be locked with the provided passcode")
                print(
                    f"   Passcode: {'*' * len(passcode)} (save this for your records)"
                )
                return 0
            else:
                print("❌ Failed to send lock command")
                return 1

        except Exception as e:
            return self.handle_api_error(e)

    def _get_computer_info(self, device_id: str, args: Namespace) -> int:
        """Get computer info using existing library"""
        try:
            print(f"🖥️  Getting computer info: {device_id}")

            computer_manager = ComputerManager(self.auth)
            computers = computer_manager.get_all_computers()

            # Find the specific computer
            computer = self._find_device_in_list(computers, device_id, "computer")
            if not computer:
                return 1

            # Format for display
            info_data = {
                "ID": computer.get("id", ""),
                "Name": computer.get("general", {}).get("name", ""),
                "Model": computer.get("hardware", {}).get("model", ""),
                "Serial Number": computer.get("general", {}).get("serial_number", ""),
                "OS Version": computer.get("general", {}).get("os_version", ""),
                "OS Build": computer.get("general", {}).get("os_build", ""),
                "Last Contact": computer.get("general", {}).get(
                    "last_contact_time", ""
                ),
                "IP Address": computer.get("general", {}).get("ip_address", ""),
                "Managed": computer.get("general", {})
                .get("remote_management", {})
                .get("managed", ""),
                "Processor": computer.get("hardware", {}).get("processor_type", ""),
                "RAM": computer.get("hardware", {}).get("total_ram_mb", ""),
                "Storage": f"{computer.get('hardware', {}).get('total_disk_space_mb', '')} MB",
            }

            output = self.format_output([info_data], args.format)
            self.save_output(output, args.output)

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    def _get_mobile_info(self, device_id: str, args: Namespace) -> int:
        """Get mobile device info using existing library"""
        try:
            print(f"📱 Getting mobile device info: {device_id}")

            mobile_manager = MobileDeviceManager(self.auth)
            devices = mobile_manager.get_all_mobile_devices()

            # Find the specific device
            device = self._find_device_in_list(devices, device_id, "mobile")
            if not device:
                return 1

            # Format for display
            info_data = {
                "ID": device.get("id", ""),
                "Name": device.get("general", {}).get("name", ""),
                "Model": device.get("general", {}).get("model", ""),
                "Serial Number": device.get("general", {}).get("serial_number", ""),
                "UDID": device.get("general", {}).get("udid", ""),
                "OS Version": device.get("general", {}).get("os_version", ""),
                "Capacity": device.get("general", {}).get("capacity_mb", ""),
                "Available": device.get("general", {}).get("available_mb", ""),
                "Battery Level": device.get("general", {}).get("battery_level", ""),
                "Last Inventory": device.get("general", {}).get(
                    "last_inventory_update", ""
                ),
                "Managed": device.get("general", {}).get("managed", ""),
                "Supervised": device.get("general", {}).get("supervised", ""),
            }

            output = self.format_output([info_data], args.format)
            self.save_output(output, args.output)

            return 0

        except Exception as e:
            return self.handle_api_error(e)

    # Helper methods
    def _get_device_type_from_pattern(self, pattern) -> str:
        """Determine device type from conversational pattern"""
        if not pattern:
            return "computer"  # Default

        pattern_str = pattern.pattern.lower()
        if "mac" in pattern_str or "computer" in pattern_str or "comp" in pattern_str:
            return "computer"
        elif (
            "ios" in pattern_str
            or "mobile" in pattern_str
            or "ipad" in pattern_str
            or "iphone" in pattern_str
        ):
            return "mobile"
        else:
            return "computer"  # Default

    def _find_device_by_identifier(
        self, identifier: str, device_type: str
    ) -> Optional[Dict[str, Any]]:
        """Find device by ID, name, or serial using existing libraries"""
        try:
            if device_type == "computer":
                computer_manager = ComputerManager(self.auth)
                computers = computer_manager.get_all_computers()
                return self._find_device_in_list(computers, identifier, "computer")
            elif device_type == "mobile":
                mobile_manager = MobileDeviceManager(self.auth)
                devices = mobile_manager.get_all_mobile_devices()
                return self._find_device_in_list(devices, identifier, "mobile")
        except Exception as e:
            print(f"❌ Error finding device: {e}")
            return None

    def _find_device_in_list(
        self, devices: List[Dict[str, Any]], identifier: str, device_type: str
    ) -> Optional[Dict[str, Any]]:
        """Find device in list by ID, name, or serial"""
        for device in devices:
            # Check ID
            if str(device.get("id", "")) == str(identifier):
                return device

            # Check name
            name = device.get("general", {}).get("name", "")
            if name and identifier.lower() in name.lower():
                return device

            # Check serial
            serial = device.get("general", {}).get("serial_number", "")
            if serial and identifier.lower() in serial.lower():
                return device

        print(f"❌ {device_type.title()} not found: {identifier}")
        return None

    def _apply_device_filter(
        self, devices: List[Dict[str, Any]], filter_text: str, name_field: str
    ) -> List[Dict[str, Any]]:
        """Apply filtering to device list"""
        if not filter_text:
            return devices

        filtered = []
        filter_lower = filter_text.lower()

        for device in devices:
            # Handle different data structures
            if isinstance(device, dict):
                if "general" in device:
                    # Enhanced device structure
                    name = device.get("general", {}).get("name", "")
                    model = device.get("general", {}).get("model", "")
                else:
                    # Simple device structure
                    name = device.get(name_field, "")
                    model = device.get("model", "")
            else:
                continue

            # Check both name and model
            if filter_lower in name.lower() or filter_lower in model.lower():
                filtered.append(device)

        return filtered

    def _format_computers_for_display(
        self, computers: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format computers for display"""
        formatted = []
        for computer in computers:
            formatted.append(
                {
                    "ID": computer.get("id", ""),
                    "Name": computer.get("general", {}).get("name", ""),
                    "Model": computer.get("hardware", {}).get("model", ""),
                    "Serial": computer.get("general", {}).get("serial_number", ""),
                    "OS Version": computer.get("general", {}).get("os_version", ""),
                    "Last Contact": computer.get("general", {}).get(
                        "last_contact_time", ""
                    ),
                }
            )
        return formatted

    def _format_mobile_devices_for_display(
        self, devices: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format mobile devices for display"""
        formatted = []
        for device in devices:
            formatted.append(
                {
                    "ID": device.get("id", ""),
                    "Name": device.get("general", {}).get("name", ""),
                    "Model": device.get("general", {}).get("model", ""),
                    "Serial": device.get("general", {}).get("serial_number", ""),
                    "OS Version": device.get("general", {}).get("os_version", ""),
                    "Last Contact": device.get("general", {}).get(
                        "last_inventory_update", ""
                    ),
                }
            )
        return formatted

    def _bulk_lock_from_csv(
        self, args: Namespace, pattern: Optional[Any] = None
    ) -> int:
        """Bulk lock devices from CSV/Excel file with usernames/emails"""
        try:
            from .bulk_lock import BulkLockService

            # Get file path or URL from args
            file_source = args.terms[0] if args.terms else None
            if not file_source:
                print("❌ Please specify a CSV/Excel file path or SharePoint link")
                print("   Usage: jpapi devices bulk lock <file_path_or_sharepoint_url>")
                print("   CSV Format: Should have 'username' or 'email' column")
                print("   Excel Format: Will write lock codes to column E")
                return 1

            # Initialize service
            service = BulkLockService(self.auth)

            # Determine file type for output
            is_excel = (
                file_source.lower().endswith((".xlsx", ".xls"))
                or "sharepoint.com" in file_source.lower()
            )

            # Production safety checks
            if self.is_production_environment() and not getattr(args, "dry_run", False):
                # We need to know device count first, so do a dry-run match
                from .bulk_lock import FileReaderFactory, DeviceMatcher

                file_reader = FileReaderFactory.create(file_source)
                users, _, _ = file_reader.read(file_source)

                if not users:
                    print("❌ No users to process")
                    return 1

                device_matcher = DeviceMatcher(self.auth)
                devices_to_lock, _ = device_matcher.match_users_to_devices(users)

                if devices_to_lock:
                    changes_summary = f"""
Bulk Device Lock Summary:
  • Total Devices: {len(devices_to_lock)}
  • Source File: {file_source}
  • Action: LOCK DEVICES
  • Passcodes: Random 6-digit PINs will be generated
  • Impact: All listed devices will be immediately locked
  • Scope: {len(devices_to_lock)} specific devices will be locked
  • Risk Level: HIGH - Bulk operation affecting multiple devices
  • Recovery: Each device can be unlocked with its generated passcode
  • Export: Results will be saved to CSV/Excel with passcodes
"""

                    if not self.require_production_confirmation(
                        "Bulk Lock Devices",
                        f"Locking {len(devices_to_lock)} devices from CSV",
                        changes_summary,
                        args,
                    ):
                        print("❌ Operation cancelled - production safety check failed")
                        return 1

            # Execute bulk lock
            exit_code, results, users_not_found, output_file = service.execute(
                file_source,
                dry_run=getattr(args, "dry_run", False),
                force=getattr(args, "force", False),
            )

            # Report users not found
            if users_not_found:
                print(f"\n⚠️  {len(users_not_found)} users without devices found:")
                for user in users_not_found[:10]:
                    print(f"   • {user}")
                if len(users_not_found) > 10:
                    print(f"   ... and {len(users_not_found) - 10} more")

            # Calculate summary
            success_count = sum(
                1
                for r in results
                if "Success" in r.get("Status", "") or "Dry-Run" in r.get("Status", "")
            )
            failed_count = len(results) - success_count

            # Summary
            print(f"\n{'='*60}")
            print(f"📊 Bulk Lock Summary:")
            print(f"   ✅ Successful: {success_count}")
            print(f"   ❌ Failed: {failed_count}")
            if output_file:
                print(f"   📄 Results exported to: {output_file}")
            print(f"   📊 Format: {'Excel' if is_excel else 'CSV'}")
            if is_excel:
                print(f"   📝 Computer names and lock codes added to spreadsheet")
            print(f"{'='*60}")
            print(f"\n🔐 IMPORTANT: Save the file - it contains all passcodes!")

            return exit_code

        except Exception as e:
            return self.handle_api_error(e)

    def _read_csv_file(self, csv_path: Path) -> tuple:
        """Read users from CSV file with hostname and lock code support"""
        users = []
        username_col = None
        email_col = None
        hostname_col = None
        lock_code_col = None

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Find relevant columns (case-insensitive)
            if reader.fieldnames:
                for col in reader.fieldnames:
                    col_lower = col.lower()
                    if "username" in col_lower or "user" in col_lower:
                        username_col = col
                    if "email" in col_lower:
                        email_col = col
                    if "hostname" in col_lower or "computer" in col_lower:
                        hostname_col = col
                    if "lock" in col_lower and "code" in col_lower:
                        lock_code_col = col

            # Read users - search by user/email, optionally use hostname as hint
            for row in reader:
                username = ""
                hostname = ""

                # Get username/email
                if email_col and row.get(email_col):
                    username = row[email_col].strip()
                elif username_col and row.get(username_col):
                    username = row[username_col].strip()

                # Skip if no username/email
                if not username:
                    continue

                # Skip if already has lock code
                if lock_code_col and row.get(lock_code_col, "").strip():
                    print(f"   ⏭️  Skipping {username} - already has lock code")
                    continue

                # Get hostname if available (optional hint)
                if hostname_col and row.get(hostname_col):
                    hostname = row[hostname_col].strip()

                # Always add user, with hostname as optional hint
                if hostname:
                    users.append({"username": username, "hostname": hostname})
                else:
                    users.append(username)

        return users, None, csv_path

    def _read_excel_file(self, file_path: str) -> tuple:
        """Read users from Excel file, skipping those with existing lock codes in column E"""
        try:
            import pandas as pd

            df = pd.read_excel(file_path)
            users = []
            username_col = None

            # Find username/email column
            for col in df.columns:
                if "username" in col.lower() or "email" in col.lower():
                    username_col = col
                    break

            if username_col:
                # Check each row - skip if column E (index 4) has a value
                for idx, row in df.iterrows():
                    username = str(row[username_col]).strip()
                    if username and username != "nan":
                        # Check if column E has a value (already locked)
                        if len(df.columns) > 4:
                            lock_code = row.iloc[4] if pd.notna(row.iloc[4]) else None
                            if lock_code and str(lock_code).strip():
                                print(
                                    f"   ⏭️  Skipping {username} - already has lock code: {lock_code}"
                                )
                                continue
                        users.append(username)

            return users, df, file_path
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            print(
                "   Ensure pandas and openpyxl are installed: pip install pandas openpyxl"
            )
            return [], None, file_path

    def _read_sharepoint_file(self, sharepoint_url: str) -> tuple:
        """Download and read Excel file from SharePoint, skipping rows with existing lock codes"""
        try:
            import pandas as pd

            # Convert SharePoint sharing link to direct download URL
            download_url = self._convert_sharepoint_url(sharepoint_url)

            print(f"   Downloading file...")
            response = requests.get(download_url, allow_redirects=True)
            response.raise_for_status()

            # Save temporarily
            temp_file = Path(
                f'temp_sharepoint_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            with open(temp_file, "wb") as f:
                f.write(response.content)

            print(f"   ✅ Downloaded successfully")
            print(f"   📋 Checking for existing lock codes in column E...")

            # Read Excel file
            df = pd.read_excel(temp_file)
            users = []
            username_col = None
            skipped_count = 0

            # Find username/email column
            for col in df.columns:
                if "username" in col.lower() or "email" in col.lower():
                    username_col = col
                    break

            if username_col:
                # Check each row - skip if column E (index 4) has a value
                for idx, row in df.iterrows():
                    username = str(row[username_col]).strip()
                    if username and username != "nan":
                        # Check if column E has a value (already locked)
                        if len(df.columns) > 4:
                            lock_code = row.iloc[4] if pd.notna(row.iloc[4]) else None
                            if lock_code and str(lock_code).strip():
                                print(
                                    f"   ⏭️  Skipping {username} - already has lock code: {lock_code}"
                                )
                                skipped_count += 1
                                continue
                        users.append(username)

            if skipped_count > 0:
                print(f"   ℹ️  Skipped {skipped_count} users with existing lock codes")

            return users, df, temp_file

        except Exception as e:
            print(f"❌ Error downloading from SharePoint: {e}")
            print("   Ensure the link is accessible and pandas/openpyxl are installed")
            return [], None, None

    def _convert_sharepoint_url(self, url: str) -> str:
        """Convert SharePoint sharing URL to direct download URL"""
        # Extract the file ID and construct download URL
        if "?e=" in url:
            base_url = url.split("?e=")[0]
            return base_url + "?download=1"
        return url + "?download=1"

    def _write_excel_with_passcodes(
        self, original_df, results: List[Dict], file_path: Path, timestamp: str
    ) -> str:
        """Write computer names and passcodes to Excel file matching original format"""
        try:
            import pandas as pd

            # Create a copy of the original dataframe
            output_df = original_df.copy()

            # Create mappings from results
            username_to_data = {}
            for r in results:
                username = r["Username"]
                username_to_data[username] = {
                    "computer_name": r["Device Name"],
                    "passcode": r["Passcode"],
                    "status": r["Status"],
                }

            # Find the username column
            username_col = None
            for col in output_df.columns:
                if "username" in col.lower() or "email" in col.lower():
                    username_col = col
                    break

            # Determine which columns to add/update
            # We'll add computer name before lock code if needed
            col_names = list(output_df.columns)

            # Ensure we have at least 5 columns
            while len(output_df.columns) < 4:
                output_df[f"Column_{len(output_df.columns)}"] = ""

            # Add Computer Name column (D) and Lock Code column (E) if they don't exist
            if len(output_df.columns) == 4:
                output_df["Computer Name"] = ""
                output_df["Lock Code"] = ""
            elif len(output_df.columns) == 5:
                output_df["Lock Code"] = ""

            # Write computer names and passcodes
            if username_col:
                for idx, row in output_df.iterrows():
                    username = str(row[username_col]).strip()
                    if username in username_to_data:
                        data = username_to_data[username]
                        # Write computer name to column D (index 3)
                        if len(output_df.columns) > 3:
                            output_df.iloc[idx, 3] = data["computer_name"]
                        # Write lock code to column E (index 4)
                        if len(output_df.columns) > 4:
                            output_df.iloc[idx, 4] = data["passcode"]

            # Save to new file
            output_file = f"device_lock_results_{timestamp}.xlsx"
            output_df.to_excel(output_file, index=False, engine="openpyxl")

            print(f"   ✅ Computer names written to column D")
            print(f"   ✅ Lock codes written to column E")

            return output_file

        except Exception as e:
            print(f"⚠️  Error writing Excel file: {e}")
            print("   Falling back to CSV export")
            # Fallback to CSV
            output_file = f"device_lock_results_{timestamp}.csv"
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            return output_file
