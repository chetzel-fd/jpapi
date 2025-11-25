"""
Bulk Lock Service - Orchestrates the bulk lock operation
Single Responsibility: Coordinate all components for bulk locking
"""
from typing import List, Dict, Tuple
from datetime import datetime
from .file_reader import FileReaderFactory
from .device_matcher import DeviceMatcher
from .passcode_generator import PasscodeGenerator
from .result_exporter import ResultExporter


class BulkLockService:
    """
    Service class that orchestrates bulk device locking
    Follows Dependency Inversion - depends on abstractions
    """

    def __init__(self, auth, device_matcher: DeviceMatcher = None):
        """Initialize with dependencies - Dependency Injection"""
        self.auth = auth
        self.device_matcher = device_matcher or DeviceMatcher(auth)
        self.passcode_generator = PasscodeGenerator()
        self.result_exporter = ResultExporter()

    def execute(
        self,
        file_source: str,
        dry_run: bool = False,
        force: bool = False,
    ) -> Tuple[int, List[Dict], List[str], str]:
        """
        Execute bulk lock operation
        
        Returns:
            Tuple of (exit_code, results, users_not_found, output_file)
        """
        # Read users from file
        file_reader = FileReaderFactory.create(file_source)
        users, original_df, file_path = file_reader.read(file_source)

        if not users:
            return 1, [], [], ""

        print(f"👥 Found {len(users)} users to process (excluding those already locked)")

        # Match users to devices
        devices_to_lock, users_not_found = self.device_matcher.match_users_to_devices(users)

        if not devices_to_lock:
            return 1, [], users_not_found, ""

        # Show devices to be locked
        print(f"\n📋 Devices to be locked:")
        for device in devices_to_lock[:10]:
            print(f"   • {device['device_name']} (ID: {device['device_id']}) - User: {device['username']}")
        if len(devices_to_lock) > 10:
            print(f"   ... and {len(devices_to_lock) - 10} more")

        # Confirm before proceeding (unless force or dry-run)
        if not force and not dry_run:
            response = input(f"\n⚠️  Lock {len(devices_to_lock)} devices? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                print("❌ Operation cancelled")
                return 1, [], users_not_found, ""

        # Lock devices
        results = self._lock_devices(devices_to_lock, dry_run)

        # Export results
        is_excel = file_source.lower().endswith((".xlsx", ".xls")) or "sharepoint.com" in file_source.lower()
        output_file = self.result_exporter.export(results, original_df, file_path, is_excel)

        return 0, results, users_not_found, output_file

    def _lock_devices(self, devices: List[Dict], dry_run: bool) -> List[Dict]:
        """Lock all devices and return results"""
        results = []

        print(f"\n🔒 Locking {len(devices)} devices...")

        for i, device in enumerate(devices, 1):
            passcode = self.passcode_generator.generate()

            print(f"\n[{i}/{len(devices)}] Locking {device['device_name']}...")

            if dry_run:
                print(f"   🔍 DRY-RUN: Would lock with PIN: {passcode}")
                results.append(self._create_result(device, passcode, "Dry-Run", True))
                continue

            try:
                endpoint = f'/JSSResource/computercommands/command/DeviceLock/passcode/{passcode}/id/{device["device_id"]}'
                response = self.auth.api_request("POST", endpoint)

                if response:
                    print(f"   ✅ Lock command sent successfully")
                    results.append(self._create_result(device, passcode, "Success", True))
                else:
                    print(f"   ❌ Failed to send lock command")
                    results.append(self._create_result(device, passcode, "Failed - API Error", False))

            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append(self._create_result(device, passcode, f"Failed - {str(e)}", False))

        return results

    def _create_result(self, device: Dict, passcode: str, status: str, success: bool) -> Dict:
        """Create result dictionary"""
        return {
            "Username": device["username"],
            "Device ID": device["device_id"],
            "Device Name": device["device_name"],
            "Serial Number": device["serial"],
            "Passcode": passcode,
            "Status": status,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

