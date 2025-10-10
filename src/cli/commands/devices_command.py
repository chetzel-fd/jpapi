#!/usr/bin/env python3
"""
Improved Devices Command for jpapi CLI
Uses existing libraries instead of duplicating functionality - reduces from 625 to ~100 lines
"""

from .common_imports import ArgumentParser, Namespace, Dict, Any, List, Optional, BaseCommand
from lib.managers import ComputerManager, MobileDeviceManager

class DevicesCommand(BaseCommand):
    """Improved devices command using existing libraries"""
    
    def __init__(self):
        super().__init__(
            name="devices",
            description="📱 Device management operations (uses existing libraries)"
        )
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup conversational patterns for device operations"""
        
        # Computer device operations
        self.add_conversational_pattern(
            pattern='mac info',
            handler='_device_info',
            description='Get computer information',
            aliases=['computer', 'macos', 'comp']
        )
        
        self.add_conversational_pattern(
            pattern='mac list',
            handler='_list_computers',
            description='List all computers',
            aliases=['computer', 'macos', 'comp']
        )
        
        self.add_conversational_pattern(
            pattern='mac update',
            handler='_update_computer',
            description='Update computer inventory',
            aliases=['computer', 'macos', 'comp']
        )
        
        # Mobile device operations
        self.add_conversational_pattern(
            pattern='ios info',
            handler='_device_info',
            description='Get mobile device information',
            aliases=['mobile', 'ipad', 'iphone']
        )
        
        self.add_conversational_pattern(
            pattern='ios list',
            handler='_list_mobile_devices',
            description='List all mobile devices',
            aliases=['mobile', 'ipad', 'iphone']
        )
        
        self.add_conversational_pattern(
            pattern='ios update',
            handler='_update_mobile',
            description='Update mobile device inventory',
            aliases=['mobile', 'ipad', 'iphone']
        )
        
        # Generic device operations
        self.add_conversational_pattern(
            pattern='devices list',
            handler='_list_all_devices',
            description='List all devices (computers and mobile)',
            aliases=['list devices', 'all devices']
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
            
            if device_type == 'computer':
                return self._get_computer_info(device_id, args)
            elif device_type == 'mobile':
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
            if hasattr(args, 'filter') and args.filter:
                computers = self._apply_device_filter(computers, args.filter, 'name')
            
            # Format for display
            formatted_data = self._format_computers_for_display(computers, args)
            output = self.format_output(formatted_data, args.format)
            self.save_output(output, args.output)
            
            print(f"\n✅ Found {len(computers)} computers")
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _list_mobile_devices(self, args: Namespace, pattern: Optional[Any] = None) -> int:
        """List mobile devices using MobileDeviceManager library"""
        try:
            print("📱 Listing mobile devices...")
            
            mobile_manager = MobileDeviceManager(self.auth)
            devices = mobile_manager.get_all_mobile_devices()
            
            if not devices:
                print("❌ No mobile devices found")
                return 1
            
            # Apply filtering
            if hasattr(args, 'filter') and args.filter:
                devices = self._apply_device_filter(devices, args.filter, 'name')
            
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
                    'Type': 'Computer',
                    'ID': computer.get('id', ''),
                    'Name': computer.get('general', {}).get('name', ''),
                    'Model': computer.get('hardware', {}).get('model', ''),
                    'OS Version': computer.get('general', {}).get('os_version', ''),
                    'Serial': computer.get('general', {}).get('serial_number', ''),
                    'Last Contact': computer.get('general', {}).get('last_contact_time', '')
                }
                all_devices.append(device_info)
            
            # Add mobile devices
            for device in mobile_devices:
                device_info = {
                    'Type': 'Mobile',
                    'ID': device.get('id', ''),
                    'Name': device.get('general', {}).get('name', ''),
                    'Model': device.get('general', {}).get('model', ''),
                    'OS Version': device.get('general', {}).get('os_version', ''),
                    'Serial': device.get('general', {}).get('serial_number', ''),
                    'Last Contact': device.get('general', {}).get('last_inventory_update', '')
                }
                all_devices.append(device_info)
            
            if not all_devices:
                print("❌ No devices found")
                return 1
            
            # Apply filtering
            if hasattr(args, 'filter') and args.filter:
                all_devices = self._apply_device_filter(all_devices, args.filter, 'Name')
            
            # Output
            output = self.format_output(all_devices, args.format)
            self.save_output(output, args.output)
            
            print(f"\n✅ Found {len(all_devices)} total devices ({len(computers)} computers, {len(mobile_devices)} mobile)")
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
            computer = self._find_device_by_identifier(device_id, 'computer')
            if not computer:
                return 1
            
            # Send inventory update command
            response = self.auth.api_request('POST', f'/JSSResource/computercommands/command/UpdateInventory/id/{computer["id"]}')
            
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
            device = self._find_device_by_identifier(device_id, 'mobile')
            if not device:
                return 1
            
            # Send inventory update command
            response = self.auth.api_request('POST', f'/JSSResource/mobiledevicecommands/command/UpdateInventory/id/{device["id"]}')
            
            if response:
                print(f"✅ Inventory update sent to {device['name']}")
                return 0
            else:
                print("❌ Failed to send inventory update")
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
            computer = self._find_device_in_list(computers, device_id, 'computer')
            if not computer:
                return 1
            
            # Format for display
            info_data = {
                'ID': computer.get('id', ''),
                'Name': computer.get('general', {}).get('name', ''),
                'Model': computer.get('hardware', {}).get('model', ''),
                'Serial Number': computer.get('general', {}).get('serial_number', ''),
                'OS Version': computer.get('general', {}).get('os_version', ''),
                'OS Build': computer.get('general', {}).get('os_build', ''),
                'Last Contact': computer.get('general', {}).get('last_contact_time', ''),
                'IP Address': computer.get('general', {}).get('ip_address', ''),
                'Managed': computer.get('general', {}).get('remote_management', {}).get('managed', ''),
                'Processor': computer.get('hardware', {}).get('processor_type', ''),
                'RAM': computer.get('hardware', {}).get('total_ram_mb', ''),
                'Storage': f"{computer.get('hardware', {}).get('total_disk_space_mb', '')} MB"
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
            device = self._find_device_in_list(devices, device_id, 'mobile')
            if not device:
                return 1
            
            # Format for display
            info_data = {
                'ID': device.get('id', ''),
                'Name': device.get('general', {}).get('name', ''),
                'Model': device.get('general', {}).get('model', ''),
                'Serial Number': device.get('general', {}).get('serial_number', ''),
                'UDID': device.get('general', {}).get('udid', ''),
                'OS Version': device.get('general', {}).get('os_version', ''),
                'Capacity': device.get('general', {}).get('capacity_mb', ''),
                'Available': device.get('general', {}).get('available_mb', ''),
                'Battery Level': device.get('general', {}).get('battery_level', ''),
                'Last Inventory': device.get('general', {}).get('last_inventory_update', ''),
                'Managed': device.get('general', {}).get('managed', ''),
                'Supervised': device.get('general', {}).get('supervised', '')
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
            return 'computer'  # Default
        
        pattern_str = pattern.pattern.lower()
        if 'mac' in pattern_str or 'computer' in pattern_str or 'comp' in pattern_str:
            return 'computer'
        elif 'ios' in pattern_str or 'mobile' in pattern_str or 'ipad' in pattern_str or 'iphone' in pattern_str:
            return 'mobile'
        else:
            return 'computer'  # Default
    
    def _find_device_by_identifier(self, identifier: str, device_type: str) -> Optional[Dict[str, Any]]:
        """Find device by ID, name, or serial using existing libraries"""
        try:
            if device_type == 'computer':
                computer_manager = ComputerManager(self.auth)
                computers = computer_manager.get_all_computers()
                return self._find_device_in_list(computers, identifier, 'computer')
            elif device_type == 'mobile':
                mobile_manager = MobileDeviceManager(self.auth)
                devices = mobile_manager.get_all_mobile_devices()
                return self._find_device_in_list(devices, identifier, 'mobile')
        except Exception as e:
            print(f"❌ Error finding device: {e}")
            return None
    
    def _find_device_in_list(self, devices: List[Dict[str, Any]], identifier: str, device_type: str) -> Optional[Dict[str, Any]]:
        """Find device in list by ID, name, or serial"""
        for device in devices:
            # Check ID
            if str(device.get('id', '')) == str(identifier):
                return device
            
            # Check name
            name = device.get('general', {}).get('name', '')
            if name and identifier.lower() in name.lower():
                return device
            
            # Check serial
            serial = device.get('general', {}).get('serial_number', '')
            if serial and identifier.lower() in serial.lower():
                return device
        
        print(f"❌ {device_type.title()} not found: {identifier}")
        return None
    
    def _apply_device_filter(self, devices: List[Dict[str, Any]], filter_text: str, name_field: str) -> List[Dict[str, Any]]:
        """Apply filtering to device list"""
        if not filter_text:
            return devices
        
        filtered = []
        filter_lower = filter_text.lower()
        
        for device in devices:
            # Handle different data structures
            if isinstance(device, dict):
                if 'general' in device:
                    # Enhanced device structure
                    name = device.get('general', {}).get('name', '')
                    model = device.get('general', {}).get('model', '')
                else:
                    # Simple device structure
                    name = device.get(name_field, '')
                    model = device.get('model', '')
            else:
                continue
            
            # Check both name and model
            if (filter_lower in name.lower() or 
                filter_lower in model.lower()):
                filtered.append(device)
        
        return filtered
    
    def _format_computers_for_display(self, computers: List[Dict[str, Any]], args: Namespace) -> List[Dict[str, Any]]:
        """Format computers for display"""
        formatted = []
        for computer in computers:
            formatted.append({
                'ID': computer.get('id', ''),
                'Name': computer.get('general', {}).get('name', ''),
                'Model': computer.get('hardware', {}).get('model', ''),
                'Serial': computer.get('general', {}).get('serial_number', ''),
                'OS Version': computer.get('general', {}).get('os_version', ''),
                'Last Contact': computer.get('general', {}).get('last_contact_time', '')
            })
        return formatted
    
    def _format_mobile_devices_for_display(self, devices: List[Dict[str, Any]], args: Namespace) -> List[Dict[str, Any]]:
        """Format mobile devices for display"""
        formatted = []
        for device in devices:
            formatted.append({
                'ID': device.get('id', ''),
                'Name': device.get('general', {}).get('name', ''),
                'Model': device.get('general', {}).get('model', ''),
                'Serial': device.get('general', {}).get('serial_number', ''),
                'OS Version': device.get('general', {}).get('os_version', ''),
                'Last Contact': device.get('general', {}).get('last_inventory_update', '')
            })
        return formatted
