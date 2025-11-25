"""
Device Matcher Module - Single Responsibility: Match users to devices
"""

from typing import List, Dict, Optional, Any, Tuple
import sys
from lib.managers import ComputerManager


class DeviceMatcher:
    """Matches users to their devices using multiple strategies - Single Responsibility"""

    def __init__(self, auth: Any):
        """Initialize with authentication for API calls"""
        self.auth = auth
        self.computer_manager = ComputerManager(auth)

    def match_users_to_devices(
        self, users: List[Dict[str, str]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Match users to their devices

        Returns:
            Tuple of (devices_to_lock, users_not_found)
        """
        # Get all computers summary list
        print("🔄 Fetching computers from JAMF...")
        all_computers_summary = self.computer_manager.get_all_computers()
        print(f"   📊 Retrieved {len(all_computers_summary)} computers")

        # Create lookup by hostname for quick matching
        hostname_to_computer = {
            c.get("name", "").upper(): c for c in all_computers_summary if c.get("name")
        }

        devices_to_lock = []
        users_not_found = []

        print(f"\n🔍 Matching users to computers...")
        sys.stdout.flush()
        total_users = len(users)

        for idx, user_entry in enumerate(users, 1):
            username = user_entry.get("username", "")
            hostname = user_entry.get("hostname", "")

            print(f"\n[{idx}/{total_users}] Processing: {username}")
            sys.stdout.flush()

            device = self._match_user(username, hostname, hostname_to_computer)

            if device:
                devices_to_lock.append(device)
            else:
                users_not_found.append(username)

        return devices_to_lock, users_not_found

    def _match_user(
        self, username: str, hostname: str, hostname_to_computer: Dict[str, Dict]
    ) -> Optional[Dict[str, Any]]:
        """Match a single user to their device"""
        clean_username = username.split("@")[0].lower()

        # Try hostname first if available (faster, more accurate)
        if hostname:
            device = self._match_by_hostname(
                username, hostname, hostname_to_computer, clean_username
            )
            if device:
                return device

        # Fall back to Users API lookup
        return self._match_by_users_api(username, clean_username)

    def _match_by_hostname(
        self,
        username: str,
        hostname: str,
        hostname_to_computer: Dict[str, Dict],
        clean_username: str,
    ) -> Optional[Dict[str, Any]]:
        """Match user by hostname"""
        print(f"   🔍 Looking up by hostname: {hostname}")
        sys.stdout.flush()

        if hostname.upper() not in hostname_to_computer:
            print(f"   ⚠️  Hostname not found in JAMF inventory")
            sys.stdout.flush()
            return None

        computer_summary = hostname_to_computer[hostname.upper()]
        computer_id = computer_summary.get("id")

        print(f"   📡 Fetching details for computer ID {computer_id}...")
        sys.stdout.flush()

        try:
            response = self.auth.api_request(
                "GET", f"/JSSResource/computers/id/{computer_id}"
            )
            if response and "computer" in response:
                computer_detail = response["computer"]
                location = computer_detail.get("location", {})
                comp_username = location.get("username", "").lower()
                comp_email = location.get("email_address", "").lower()

                # Verify it matches the user
                if (
                    clean_username in comp_username
                    or username.lower() in comp_email
                    or username.lower() == comp_email
                ):
                    print(
                        f"   ✅ MATCHED: {computer_summary.get('name')} (ID: {computer_id})"
                    )
                    sys.stdout.flush()
                    return {
                        "username": username,
                        "device_id": computer_id,
                        "device_name": computer_summary.get("name", "Unknown"),
                        "serial": computer_detail.get("general", {}).get(
                            "serial_number", "Unknown"
                        ),
                        "type": "computer",
                    }
                else:
                    print(
                        f"   ⚠️  Hostname matches but user doesn't match (found: {comp_username or comp_email})"
                    )
                    sys.stdout.flush()
        except Exception as e:
            print(f"   ❌ Error fetching details: {e}")
            sys.stdout.flush()

        return None

    def _match_by_users_api(
        self, username: str, clean_username: str
    ) -> Optional[Dict[str, Any]]:
        """Match user via Users API"""
        print(f"   🔍 Looking up via Users API...")
        sys.stdout.flush()

        user_record = self._find_user_record(username, clean_username)
        if not user_record:
            print(f"   ❌ User not found in JAMF")
            sys.stdout.flush()
            return None

        computer_id, computer_name = self._extract_computer_from_user(user_record)
        if not computer_id:
            print(f"      User found but no computers assigned")
            sys.stdout.flush()
            return None

        print(f"      Found computer for this user")
        sys.stdout.flush()

        # Get full computer details for serial
        try:
            comp_response = self.auth.api_request(
                "GET", f"/JSSResource/computers/id/{computer_id}"
            )
            serial = (
                comp_response.get("computer", {})
                .get("general", {})
                .get("serial_number", "Unknown")
            )
        except:
            serial = "Unknown"

        print(f"   ✅ MATCHED: {computer_name} (ID: {computer_id})")
        sys.stdout.flush()

        return {
            "username": username,
            "device_id": computer_id,
            "device_name": computer_name,
            "serial": serial,
            "type": "computer",
        }

    def _find_user_record(self, username: str, clean_username: str) -> Optional[Dict]:
        """Find user record via Users API with multiple email variations"""
        # Try different email variations (case-sensitive API)
        email_variations = [
            username,  # Original
            username.lower(),  # Lowercase
            # Title case: Firstname.Lastname@example.com
            (
                ".".join(
                    [part.capitalize() for part in username.split("@")[0].split(".")]
                )
                + "@"
                + username.split("@")[1]
                if "@" in username
                else username
            ),
        ]

        for email_variant in email_variations:
            try:
                print(f"      Trying: {email_variant}")
                sys.stdout.flush()
                response = self.auth.api_request(
                    "GET", f"/JSSResource/users/email/{email_variant}"
                )
                if response and "users" in response and len(response["users"]) > 0:
                    print(f"      ✓ Found user by email!")
                    sys.stdout.flush()
                    return response["users"][0]
            except:
                pass

        # Try username lookup (without @domain)
        try:
            print(f"      Trying username lookup: {clean_username}")
            sys.stdout.flush()
            response = self.auth.api_request(
                "GET", f"/JSSResource/users/name/{clean_username}"
            )
            if response and "user" in response:
                print(f"      ✓ Found user by username")
                sys.stdout.flush()
                return response["user"]
        except:
            pass

        return None

    def _extract_computer_from_user(
        self, user_record: Dict
    ) -> Tuple[Optional[int], str]:
        """Extract computer ID and name from user record"""
        links = user_record.get("links", [])
        computer_id = None
        computer_name = "Unknown"

        if isinstance(links, list):
            # Email lookup returns: [{"computer": [{"id": 3145}, {"name": "..."}]}, ...]
            for link in links:
                if isinstance(link, dict) and "computer" in link:
                    computer_data = link.get("computer", [])
                    # Parse the weird format: [{"id": X}, {"name": "Y"}]
                    for item in computer_data:
                        if "id" in item:
                            computer_id = item["id"]
                        if "name" in item:
                            computer_name = item["name"]
                    if computer_id:
                        break
        elif isinstance(links, dict):
            # ID lookup returns: {"computers": [{"id": X, "name": "Y"}]}
            computers = links.get("computers", [])
            if computers:
                first_computer = computers[0]
                computer_id = first_computer.get("id")
                computer_name = first_computer.get("name", "Unknown")

        return computer_id, computer_name
