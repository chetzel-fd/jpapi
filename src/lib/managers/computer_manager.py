#!/usr/bin/env python3
"""
Computer Management Core - macOS Toolkit
Provides comprehensive computer management functionality with same robustness as mobile toolkit
"""
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from pathlib import Path

class ComputerManager:
    """
    Comprehensive computer management with export/sync capabilities
    """
    
    def __init__(self, auth):
        """
        Initialize computer manager
        
        Args:
            auth: JamfAuth instance for API calls
        """
        self.auth = auth
        self.cache_dir = Path("tmp/cache/computer")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get_all_computers(self, use_cache: bool = True, cache_ttl_minutes: int = 30) -> List[Dict]:
        """
        Get all computers with intelligent caching
        
        Args:
            use_cache: Whether to use cached data
            cache_ttl_minutes: Cache TTL in minutes
            
        Returns:
            List of computer objects with enhanced data
        """
        cache_file = self.cache_dir / "computers.json"
        
        # Check cache validity
        if use_cache and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(minutes=cache_ttl_minutes):
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        # Fetch from API
        try:
            print("🔄 Getting fresh token for /JSSResource/computers")
            response = self.auth.api_request('GET', "/JSSResource/computers")
            print(f"🔍 Debug: Response type: {type(response)}")
            if response:
                print(f"🔍 Debug: Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            
            if response and 'computers' in response:
                computers = response['computers']
                
                # Enhance each computer with additional data
                enhanced_computers = []
                for computer in computers:
                    enhanced_computer = self._enhance_computer_data(computer)
                    enhanced_computers.append(enhanced_computer)
                
                # Cache the results
                with open(cache_file, 'w') as f:
                    json.dump(enhanced_computers, f, indent=2)
                
                return enhanced_computers
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error fetching computers: {e}")
            # If it's a 401 error, it might mean no computers exist or no permission
            if "401" in str(e):
                print("ℹ️  No computers found or insufficient permissions for computer management")
            return []
    
    def get_all_computer_groups(self, use_cache: bool = True, cache_ttl_minutes: int = 60) -> List[Dict]:
        """
        Get all computer groups with intelligent caching
        
        Args:
            use_cache: Whether to use cached data
            cache_ttl_minutes: Cache TTL in minutes
            
        Returns:
            List of computer group objects with enhanced data
        """
        cache_file = self.cache_dir / "computer_groups.json"
        
        # Check cache validity
        if use_cache and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(minutes=cache_ttl_minutes):
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        # Fetch from API
        try:
            print("🔄 Getting fresh token for /JSSResource/computergroups")
            response = self.auth.make_api_call("/JSSResource/computergroups")
            
            if response and 'computer_groups' in response:
                groups = response['computer_groups']
                
                # Enhance each group with additional data
                enhanced_groups = []
                for group in groups:
                    enhanced_group = self._enhance_group_data(group)
                    enhanced_groups.append(enhanced_group)
                
                # Cache the results
                with open(cache_file, 'w') as f:
                    json.dump(enhanced_groups, f, indent=2)
                
                return enhanced_groups
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error fetching computer groups: {e}")
            # If it's a 401 error, it might mean no groups exist or no permission
            if "401" in str(e):
                print("ℹ️  No computer groups found or insufficient permissions for computer group management")
            return []
    
    def get_all_computer_policies(self, use_cache: bool = True, cache_ttl_minutes: int = 60) -> List[Dict]:
        """
        Get all computer policies with intelligent caching
        
        Args:
            use_cache: Whether to use cached data
            cache_ttl_minutes: Cache TTL in minutes
            
        Returns:
            List of computer policy objects with enhanced data
        """
        cache_file = self.cache_dir / "computer_policies.json"
        
        # Check cache validity
        if use_cache and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(minutes=cache_ttl_minutes):
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        # Fetch from API
        try:
            print("🔄 Getting fresh token for /JSSResource/policies")
            response = self.auth.make_api_call("/JSSResource/policies")
            
            if response and 'policies' in response:
                policies = response['policies']
                
                # Enhance each policy with additional data
                enhanced_policies = []
                for policy in policies:
                    enhanced_policy = self._enhance_policy_data(policy)
                    enhanced_policies.append(enhanced_policy)
                
                # Cache the results
                with open(cache_file, 'w') as f:
                    json.dump(enhanced_policies, f, indent=2)
                
                return enhanced_policies
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error fetching computer policies: {e}")
            # If it's a 401 error, it might mean no policies exist or no permission
            if "401" in str(e):
                print("ℹ️  No computer policies found or insufficient permissions for computer policy management")
            return []
    
    def _enhance_computer_data(self, computer: Dict) -> Dict:
        """
        Enhance computer data with additional fields and relationships
        
        Args:
            computer: Raw computer data from API
            
        Returns:
            Enhanced computer data
        """
        enhanced = computer.copy()
        
        # Add summary fields for easy access
        enhanced['_summary'] = {
            'id': computer.get('id', ''),
            'name': computer.get('name', ''),
            'serial_number': computer.get('serial_number', ''),
            'mac_address': computer.get('mac_address', ''),
            'managed': computer.get('managed', False),
            'supervised': computer.get('supervised', False),
            'model': computer.get('model', ''),
            'username': computer.get('username', '')
        }
        
        # Add device type
        enhanced['_device_type'] = 'Mac'
        
        # Add OS version clean
        os_version = computer.get('os_version', '')
        enhanced['_os_version_clean'] = os_version.split('.')[0] + '.' + os_version.split('.')[1] if '.' in os_version else os_version
        
        # Add last contact relative
        last_contact = computer.get('last_contact_time', '')
        enhanced['_last_contact_relative'] = self._get_relative_time(last_contact)
        
        # Add security status
        enhanced['_security_status'] = self._get_security_status(computer)
        
        return enhanced
    
    def _enhance_group_data(self, group: Dict) -> Dict:
        """
        Enhance group data with additional fields
        
        Args:
            group: Raw group data from API
            
        Returns:
            Enhanced group data
        """
        enhanced = group.copy()
        
        # Add device count if not present
        if 'device_count' not in enhanced:
            enhanced['device_count'] = group.get('computers', {}).get('size', 0) if 'computers' in group else 0
        
        return enhanced
    
    def _enhance_policy_data(self, policy: Dict) -> Dict:
        """
        Enhance policy data with additional fields
        
        Args:
            policy: Raw policy data from API
            
        Returns:
            Enhanced policy data
        """
        enhanced = policy.copy()
        
        # Add summary fields for easy access
        enhanced['_summary'] = {
            'id': policy.get('id', ''),
            'name': policy.get('name', ''),
            'enabled': policy.get('general', {}).get('enabled', False),
            'category': policy.get('general', {}).get('category', {}).get('name', 'None'),
            'frequency': policy.get('general', {}).get('frequency', 'Once per computer per user'),
            'trigger': policy.get('general', {}).get('trigger', '')
        }
        
        return enhanced
    
    def _get_relative_time(self, timestamp: str) -> str:
        """
        Convert timestamp to relative time
        
        Args:
            timestamp: ISO timestamp string
            
        Returns:
            Relative time string
        """
        if not timestamp:
            return "Unknown"
        
        try:
            # Parse the timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
            else:
                return "Just now"
        except:
            return "Unknown"
    
    def _get_security_status(self, computer: Dict) -> str:
        """
        Get security status summary for computer
        
        Args:
            computer: Computer data
            
        Returns:
            Security status string
        """
        issues = []
        
        # Check FileVault
        if not computer.get('security', {}).get('filevault2_enabled', False):
            issues.append("FileVault disabled")
        
        # Check Gatekeeper
        if not computer.get('security', {}).get('gatekeeper_enabled', False):
            issues.append("Gatekeeper disabled")
        
        # Check SIP
        if not computer.get('security', {}).get('sip_enabled', False):
            issues.append("SIP disabled")
        
        if issues:
            return f"Issues: {len(issues)} problems"
        else:
            return "Secure"
    
    def export_computers(self, output_file: str, format: str = 'json') -> bool:
        """
        Export computers to file
        
        Args:
            output_file: Output file path
            format: Export format (json, csv, xlsx)
            
        Returns:
            True if successful
        """
        try:
            computers = self.get_all_computers()
            
            if format == 'json':
                with open(output_file, 'w') as f:
                    json.dump(computers, f, indent=2)
            elif format == 'csv':
                self._export_to_csv(computers, output_file, 'computers')
            elif format == 'xlsx':
                self._export_to_xlsx(computers, output_file, 'computers')
            
            print(f"✅ Exported {len(computers)} computers to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def export_computer_groups(self, output_file: str, format: str = 'json') -> bool:
        """
        Export computer groups to file
        
        Args:
            output_file: Output file path
            format: Export format (json, csv, xlsx)
            
        Returns:
            True if successful
        """
        try:
            groups = self.get_all_computer_groups()
            
            if format == 'json':
                with open(output_file, 'w') as f:
                    json.dump(groups, f, indent=2)
            elif format == 'csv':
                self._export_to_csv(groups, output_file, 'computer_groups')
            elif format == 'xlsx':
                self._export_to_xlsx(groups, output_file, 'computer_groups')
            
            print(f"✅ Exported {len(groups)} computer groups to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def export_computer_policies(self, output_file: str, format: str = 'json') -> bool:
        """
        Export computer policies to file
        
        Args:
            output_file: Output file path
            format: Export format (json, csv, xlsx)
            
        Returns:
            True if successful
        """
        try:
            policies = self.get_all_computer_policies()
            
            if format == 'json':
                with open(output_file, 'w') as f:
                    json.dump(policies, f, indent=2)
            elif format == 'csv':
                self._export_to_csv(policies, output_file, 'computer_policies')
            elif format == 'xlsx':
                self._export_to_xlsx(policies, output_file, 'computer_policies')
            
            print(f"✅ Exported {len(policies)} computer policies to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def _export_to_csv(self, data: List[Dict], output_file: str, data_type: str) -> None:
        """
        Export data to CSV format
        
        Args:
            data: List of dictionaries to export
            output_file: Output file path
            data_type: Type of data for field mapping
        """
        if not data:
            return
        
        # Define field mappings for different data types
        field_mappings = {
            'computers': [
                'id', 'name', 'serial_number', 'mac_address', 'model', 
                'os_version', 'username', 'managed', 'supervised', 'last_contact_time'
            ],
            'computer_groups': [
                'id', 'name', 'is_smart', 'device_count', 'site'
            ],
            'computer_policies': [
                'id', 'name', 'enabled', 'category', 'frequency', 'trigger'
            ]
        }
        
        fields = field_mappings.get(data_type, list(data[0].keys()))
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            
            for item in data:
                # Flatten nested data for CSV
                flat_item = {}
                for field in fields:
                    if field in item:
                        flat_item[field] = item[field]
                    elif field in item.get('general', {}):
                        flat_item[field] = item['general'][field]
                    else:
                        flat_item[field] = ''
                
                writer.writerow(flat_item)
    
    def _export_to_xlsx(self, data: List[Dict], output_file: str, data_type: str) -> None:
        """
        Export data to Excel format
        
        Args:
            data: List of dictionaries to export
            output_file: Output file path
            data_type: Type of data for field mapping
        """
        try:
            import pandas as pd
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Flatten nested columns
            if 'general' in df.columns:
                general_df = pd.json_normalize(df['general'])
                df = pd.concat([df.drop('general', axis=1), general_df], axis=1)
            
            # Save to Excel
            df.to_excel(output_file, index=False)
            
        except ImportError:
            print("⚠️  pandas not available, falling back to CSV")
            csv_file = output_file.replace('.xlsx', '.csv')
            self._export_to_csv(data, csv_file, data_type)
        except Exception as e:
            print(f"⚠️  Excel export failed: {e}")
            csv_file = output_file.replace('.xlsx', '.csv')
            self._export_to_csv(data, csv_file, data_type)
