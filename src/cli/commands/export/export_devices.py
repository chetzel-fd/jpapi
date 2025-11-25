#!/usr/bin/env python3
"""
Device Export Handler for jpapi CLI
Handles export of iOS and macOS devices
"""

from typing import Dict, Any, List
from argparse import Namespace
from .export_base import ExportBase
from core.logging.command_mixin import log_operation, with_progress
import json
from lib.utils import create_jamf_hyperlink


class ExportDevices(ExportBase):
    """Handler for exporting mobile and computer devices"""

    def __init__(self, auth, device_type: str):
        super().__init__(auth, f"{device_type} devices")
        self.device_type = device_type
        self.endpoint = (
            "/JSSResource/mobiledevices"
            if device_type == "mobile"
            else "/JSSResource/computers"
        )
        self.detail_endpoint = (
            "/JSSResource/mobiledevices"
            if device_type == "mobile"
            else "/JSSResource/computers"
        )

    @log_operation("Device Data Fetch")
    def _fetch_data(self, args: Namespace) -> List[Dict[str, Any]]:
        """Fetch device data from JAMF API"""
        self.log_info(f"Fetching {self.device_type} devices from JAMF API")
        response = self.auth.api_request("GET", self.endpoint)

        if (
            f"{self.device_type}_devices" not in response
            and "computers" not in response
        ):
            self.log_warning(f"No {self.device_type} devices found in API response")
            return []

        devices = response.get(f"{self.device_type}_devices") or response.get(
            "computers"
        )

        # Handle both list and dict formats
        if isinstance(devices, dict):
            device_key = "mobile_device" if self.device_type == "mobile" else "computer"
            devices = devices.get(device_key, [])

        return devices if isinstance(devices, list) else []

    def _format_data(
        self, data: List[Dict[str, Any]], args: Namespace
    ) -> List[Dict[str, Any]]:
        """Format device data for export"""
        export_data = []

        for i, device in enumerate(data):
            print(
                f"   Processing {self.device_type} device {i+1}/{len(data)}: {device.get('name', 'Unknown')}"
            )

            # Basic device data
            device_data = self._get_basic_device_data(
                device, getattr(args, "env", "sandbox")
            )

            # Add detailed info if requested
            if args.detailed and device.get("id"):
                detailed_data = self._get_detailed_device_data(device["id"])
                if detailed_data:
                    device_data.update(detailed_data)

            # Always create individual device JSON files for comprehensive export
            if device.get("id"):
                device_file = self._download_device_file(device)
                if device_file:
                    device_data["device_file"] = device_file

            export_data.append(device_data)

        return export_data

    def _download_device_file(self, device: Dict[str, Any]) -> str:
        """Download individual device JSON file"""
        try:
            # Get detailed device info
            device_id = device.get("id")
            detail_response = self.auth.api_request(
                "GET", f"{self.detail_endpoint}/id/{device_id}"
            )

            if not detail_response:
                return ""

            # Create safe filename
            safe_name = self._create_safe_filename(
                device.get("name", ""), device.get("id", ""), "json"
            )

            # Save device file as JSON
            device_file = self._download_file(
                json.dumps(detail_response, indent=2),
                safe_name,
                f"data/csv-exports/{self.device_type}_devices",
            )

            # Return relative path format to match expected CSV format
            return f"data/csv-exports/{self.device_type}_devices/{safe_name}"

        except Exception as e:
            print(f"   ⚠️ Failed to download {device.get('name', '')}: {e}")
            return ""

    def _get_basic_device_data(
        self, device: Dict[str, Any], environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """Get basic device information"""
        device_type_for_url = (
            "mobile-devices" if self.device_type == "mobile" else "computers"
        )

        if self.device_type == "mobile":
            return {
                "delete": "",  # Empty column for manual deletion tracking
                "ID": create_jamf_hyperlink(
                    device_type_for_url, device.get("id", ""), environment
                ),
                "Name": device.get("name", ""),
                "Model": device.get("model", ""),
                "Serial Number": device.get("serial_number", ""),
                "UDID": device.get("udid", ""),
                "OS Version": device.get("os_version", ""),
                "Capacity": device.get("capacity", ""),
                "Available Space": device.get("available", ""),
                "device_file": "",  # Will be set below
            }
        else:  # macOS
            return {
                "delete": "",  # Empty column for manual deletion tracking
                "ID": create_jamf_hyperlink(
                    device_type_for_url, device.get("id", ""), environment
                ),
                "Name": device.get("name", ""),
                "Model": device.get("model", ""),
                "Serial Number": device.get("serial_number", ""),
                "OS Version": device.get("os_version", ""),
                "OS Build": device.get("os_build", ""),
                "Processor Type": device.get("processor_type", ""),
                "Total RAM": device.get("total_ram", ""),
                "device_file": "",  # Will be set below
            }

    def _get_detailed_device_data(self, device_id: str) -> Dict[str, Any]:
        """Get detailed device information"""
        detail = self._get_detailed_info(device_id, self.detail_endpoint)
        if not detail:
            return {}

        if self.device_type == "mobile":
            return {
                "Last Inventory": detail.get("general", {}).get(
                    "last_inventory_update", ""
                ),
                "Managed": detail.get("general", {}).get("managed", ""),
                "Supervised": detail.get("general", {}).get("supervised", ""),
                "Battery Level": detail.get("general", {}).get("battery_level", ""),
                "Carrier": detail.get("network", {}).get("carrier", ""),
                "WiFi MAC": detail.get("network", {}).get("wifi_mac_address", ""),
            }
        else:  # macOS
            return {
                "Last Check-in": detail.get("general", {}).get("last_contact_time", ""),
                "IP Address": detail.get("general", {}).get("ip_address", ""),
                "Managed": detail.get("general", {})
                .get("remote_management", {})
                .get("managed", ""),
                "FileVault Enabled": detail.get("security", {}).get(
                    "filevault_enabled", ""
                ),
                "SIP Status": detail.get("security", {}).get("sip_status", ""),
            }
