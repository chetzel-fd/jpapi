#!/usr/bin/env python3
"""
Mobile Device Management Core - iOS/iPadOS Toolkit
Provides comprehensive mobile device management functionality with same robustness as computer toolkit
"""
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from pathlib import Path

class MobileDeviceManager:
    """
    Comprehensive mobile device management with export/sync capabilities
    """
    
    def __init__(self, auth):
        """
        Initialize mobile device manager
        
        Args:
            auth: JamfAuth instance for API calls
        """
        self.auth = auth
        self.cache_dir = Path("tmp/cache/mobile")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get_all_mobile_devices(self, use_cache: bool = True, cache_ttl_minutes: int = 30) -> List[Dict]:
        """
        Get all mobile devices with intelligent caching
        
        Args:
            use_cache: Whether to use cached data
            cache_ttl_minutes: Cache TTL in minutes
            
        Returns:
            List of mobile device objects with enhanced data
        """
        cache_file = self.cache_dir / "mobile_devices.json"
        
        # Check cache validity
        if use_cache and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(minutes=cache_ttl_minutes):
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        try:
            # Get basic device list
            devices_response = self.auth.api_request('GET', '/JSSResource/mobiledevices')
            if not devices_response or 'mobile_devices' not in devices_response:
                return []
            
            devices = devices_response['mobile_devices']
            enhanced_devices = []
            
            # Enhance each device with detailed information
            for device_summary in devices:
                try:
                    device_id = device_summary.get('id')
                    if device_id:
                        # Get detailed device info
                        detail_response = self.auth.api_request('GET', f'/JSSResource/mobiledevices/id/{device_id}')
                        if detail_response and 'mobile_device' in detail_response:
                            device_detail = detail_response['mobile_device']
                            
                            # Enhance with summary data and computed fields
                            device_detail['_summary'] = device_summary
                            device_detail['_device_type'] = self._determine_device_type(device_detail)
                            device_detail['_os_version_clean'] = self._clean_os_version(device_detail)
                            device_detail['_last_contact_relative'] = self._get_relative_time(device_detail)
                            device_detail['_security_status'] = self._assess_security_status(device_detail)
                            
                            enhanced_devices.append(device_detail)
                except Exception as e:
                    # Continue processing other devices if one fails
                    continue
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump(enhanced_devices, f, indent=2)
            except:
                pass
            
            return enhanced_devices
            
        except Exception as e:
            return []
    
    def get_all_mobile_groups(self, use_cache: bool = True, cache_ttl_minutes: int = 60) -> List[Dict]:
        """
        Get all mobile device groups with relationship data
        
        Args:
            use_cache: Whether to use cached data
            cache_ttl_minutes: Cache TTL in minutes
            
        Returns:
            List of mobile device group objects with relationship data
        """
        cache_file = self.cache_dir / "mobile_groups.json"
        
        # Check cache validity
        if use_cache and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(minutes=cache_ttl_minutes):
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        try:
            # Get basic group list
            groups_response = self.auth.make_api_call('/JSSResource/mobiledevicegroups')
            if not groups_response or 'mobile_device_groups' not in groups_response:
                return []
            
            groups = groups_response['mobile_device_groups']
            enhanced_groups = []
            
            # Enhance each group with detailed information
            for group_summary in groups:
                try:
                    group_id = group_summary.get('id')
                    if group_id:
                        # Get detailed group info
                        detail_response = self.auth.make_api_call(f'/JSSResource/mobiledevicegroups/id/{group_id}')
                        if detail_response and 'mobile_device_group' in detail_response:
                            group_detail = detail_response['mobile_device_group']
                            
                            # Enhance with summary data and computed fields
                            group_detail['_summary'] = group_summary
                            group_detail['_member_count'] = len(group_detail.get('mobile_devices', []))
                            group_detail['_group_type'] = 'Smart' if group_detail.get('is_smart') else 'Static'
                            group_detail['_targeting_profiles'] = []
                            group_detail['_targeting_policies'] = []
                            
                            enhanced_groups.append(group_detail)
                except Exception as e:
                    continue
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump(enhanced_groups, f, indent=2)
            except:
                pass
            
            return enhanced_groups
            
        except Exception as e:
            return []
    
    def get_all_mobile_profiles(self, use_cache: bool = True, cache_ttl_minutes: int = 60) -> List[Dict]:
        """
        Get all mobile configuration profiles with targeting data
        
        Args:
            use_cache: Whether to use cached data
            cache_ttl_minutes: Cache TTL in minutes
            
        Returns:
            List of mobile configuration profile objects
        """
        cache_file = self.cache_dir / "mobile_profiles.json"
        
        # Check cache validity
        if use_cache and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(minutes=cache_ttl_minutes):
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        try:
            # Get basic profile list
            profiles_response = self.auth.make_api_call('/JSSResource/mobiledeviceconfigurationprofiles')
            if not profiles_response or 'mobile_device_configuration_profiles' not in profiles_response:
                return []
            
            profiles = profiles_response['mobile_device_configuration_profiles']
            enhanced_profiles = []
            
            # Enhance each profile with detailed information
            for profile_summary in profiles:
                try:
                    profile_id = profile_summary.get('id')
                    if profile_id:
                        # Get detailed profile info
                        detail_response = self.auth.make_api_call(f'/JSSResource/mobiledeviceconfigurationprofiles/id/{profile_id}')
                        if detail_response and 'mobile_device_configuration_profile' in detail_response:
                            profile_detail = detail_response['mobile_device_configuration_profile']
                            
                            # Enhance with summary data and computed fields
                            profile_detail['_summary'] = profile_summary
                            profile_detail['_payload_count'] = len(profile_detail.get('payloads', []))
                            profile_detail['_scope_device_count'] = len(profile_detail.get('scope', {}).get('mobile_devices', []))
                            profile_detail['_scope_group_count'] = len(profile_detail.get('scope', {}).get('mobile_device_groups', []))
                            profile_detail['_deployment_method'] = profile_detail.get('deployment_method', 'Install Automatically')
                            
                            enhanced_profiles.append(profile_detail)
                except Exception as e:
                    continue
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump(enhanced_profiles, f, indent=2)
            except:
                pass
            
            return enhanced_profiles
            
        except Exception as e:
            return []
    
    def export_mobile_profiles(self, output_format: str = 'json', output_dir: str = None) -> Dict[str, str]:
        """
        Export mobile configuration profiles in various formats
        
        Args:
            output_format: 'json', 'csv', or 'both'
            output_dir: Output directory (defaults to tmp/exports/mobile)
            
        Returns:
            Dict with export file paths and status
        """
        if not output_dir:
            output_dir = Path("tmp/exports/mobile")
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all profiles
        profiles = self.get_all_mobile_profiles(use_cache=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_results = {}
        
        # JSON Export
        if output_format in ['json', 'both']:
            json_file = output_dir / f"mobile_profiles_{timestamp}.json"
            try:
                with open(json_file, 'w') as f:
                    json.dump({
                        'export_date': datetime.now().isoformat(),
                        'total_profiles': len(profiles),
                        'profiles': profiles
                    }, f, indent=2)
                export_results['json'] = str(json_file)
            except Exception as e:
                export_results['json_error'] = str(e)
        
        # CSV Export
        if output_format in ['csv', 'both']:
            csv_file = output_dir / f"mobile_profiles_{timestamp}.csv"
            try:
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Write header with DELETE column first
                    writer.writerow([
                        'DELETE', 'ID', 'Name', 'Description', 'Deployment Method', 'Payload Count',
                        'Scope Device Count', 'Scope Group Count', 'Level', 'UUID'
                    ])
                    
                    # Write profile data with DELETE column
                    for profile in profiles:
                        writer.writerow([
                            'FALSE',  # Default to not delete
                            profile.get('id', ''),
                            profile.get('name', ''),
                            profile.get('description', ''),
                            profile.get('_deployment_method', ''),
                            profile.get('_payload_count', 0),
                            profile.get('_scope_device_count', 0),
                            profile.get('_scope_group_count', 0),
                            profile.get('level', ''),
                            profile.get('uuid', '')
                        ])
                
                export_results['csv'] = str(csv_file)
            except Exception as e:
                export_results['csv_error'] = str(e)
        
        return export_results
    
    def export_mobile_groups(self, output_format: str = 'json', output_dir: str = None) -> Dict[str, str]:
        """
        Export mobile device groups in various formats
        
        Args:
            output_format: 'json', 'csv', or 'both'
            output_dir: Output directory (defaults to tmp/exports/mobile)
            
        Returns:
            Dict with export file paths and status
        """
        if not output_dir:
            output_dir = Path("tmp/exports/mobile")
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all groups
        groups = self.get_all_mobile_groups(use_cache=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_results = {}
        
        # JSON Export
        if output_format in ['json', 'both']:
            json_file = output_dir / f"mobile_groups_{timestamp}.json"
            try:
                with open(json_file, 'w') as f:
                    json.dump({
                        'export_date': datetime.now().isoformat(),
                        'total_groups': len(groups),
                        'groups': groups
                    }, f, indent=2)
                export_results['json'] = str(json_file)
            except Exception as e:
                export_results['json_error'] = str(e)
        
        # CSV Export
        if output_format in ['csv', 'both']:
            csv_file = output_dir / f"mobile_groups_{timestamp}.csv"
            try:
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Write header with DELETE column first
                    writer.writerow([
                        'DELETE', 'ID', 'Name', 'Type', 'Member Count', 'Is Smart', 'Site ID', 'Site Name'
                    ])
                    
                    # Write group data with DELETE column
                    for group in groups:
                        site_info = group.get('site', {})
                        writer.writerow([
                            'FALSE',  # Default to not delete
                            group.get('id', ''),
                            group.get('name', ''),
                            group.get('_group_type', ''),
                            group.get('_member_count', 0),
                            group.get('is_smart', False),
                            site_info.get('id', '') if site_info else '',
                            site_info.get('name', '') if site_info else ''
                        ])
                
                export_results['csv'] = str(csv_file)
            except Exception as e:
                export_results['csv_error'] = str(e)
        
        return export_results
    
    def sync_mobile_profiles_to_groups(self, dry_run: bool = True) -> Dict[str, any]:
        """
        Intelligent sync of mobile profiles to appropriate groups
        
        Args:
            dry_run: If True, only analyze without making changes
            
        Returns:
            Sync analysis and results
        """
        profiles = self.get_all_mobile_profiles(use_cache=False)
        groups = self.get_all_mobile_groups(use_cache=False)
        
        sync_recommendations = []
        
        for profile in profiles:
            profile_name = profile.get('name', '').lower()
            current_groups = profile.get('scope', {}).get('mobile_device_groups', [])
            current_group_names = [g.get('name', '') for g in current_groups]
            
            # Intelligent matching based on profile name and purpose
            recommended_groups = []
            
            for group in groups:
                group_name = group.get('name', '').lower()
                
                # Smart matching logic
                if any(keyword in profile_name for keyword in ['executive', 'leadership', 'exec']):
                    if any(keyword in group_name for keyword in ['executive', 'leadership', 'exec', 'vip']):
                        recommended_groups.append(group)
                
                elif any(keyword in profile_name for keyword in ['wifi', 'network']):
                    if 'all' in group_name or 'everyone' in group_name:
                        recommended_groups.append(group)
                
                elif any(keyword in profile_name for keyword in ['security', 'vpn', 'certificate']):
                    if not any(keyword in group_name for keyword in ['test', 'temp', 'staging']):
                        recommended_groups.append(group)
            
            if recommended_groups:
                sync_recommendations.append({
                    'profile_id': profile.get('id'),
                    'profile_name': profile.get('name'),
                    'current_groups': current_group_names,
                    'recommended_groups': [g.get('name') for g in recommended_groups],
                    'action': 'add_to_scope' if not dry_run else 'recommend_add'
                })
        
        return {
            'dry_run': dry_run,
            'total_profiles_analyzed': len(profiles),
            'total_groups_available': len(groups),
            'sync_recommendations': sync_recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _determine_device_type(self, device: Dict) -> str:
        """Determine device type from device data"""
        general = device.get('general', {})
        model = general.get('model', '').lower()
        
        if 'ipad' in model:
            return 'iPad'
        elif 'iphone' in model:
            return 'iPhone'
        elif 'ipod' in model:
            return 'iPod'
        elif 'apple tv' in model:
            return 'Apple TV'
        else:
            return 'iOS Device'
    
    def _clean_os_version(self, device: Dict) -> str:
        """Clean and standardize OS version"""
        general = device.get('general', {})
        os_version = general.get('os_version', '')
        if os_version:
            # Extract major.minor version
            parts = os_version.split('.')
            if len(parts) >= 2:
                return f"{parts[0]}.{parts[1]}"
        return os_version
    
    def _get_relative_time(self, device: Dict) -> str:
        """Get relative time since last contact"""
        general = device.get('general', {})
        last_contact = general.get('last_inventory_update')
        if not last_contact:
            return 'Unknown'
        
        try:
            # Parse the date and calculate relative time
            from datetime import datetime
            last_date = datetime.fromisoformat(last_contact.replace('Z', '+00:00'))
            now = datetime.now(last_date.tzinfo)
            diff = now - last_date
            
            if diff.days > 30:
                return f"{diff.days} days ago"
            elif diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600} hours ago"
            else:
                return "Recently"
        except:
            return 'Unknown'
    
    def _assess_security_status(self, device: Dict) -> str:
        """Assess device security status"""
        security = device.get('security', {})
        general = device.get('general', {})
        
        issues = []
        
        # Check passcode
        if not security.get('passcode_present', False):
            issues.append('No Passcode')
        
        # Check encryption
        if not security.get('data_protection', False):
            issues.append('Not Encrypted')
        
        # Check jailbreak
        if security.get('jailbreak_detected', False):
            issues.append('Jailbroken')
        
        # Check supervision
        if not general.get('supervised', False):
            issues.append('Not Supervised')
        
        if not issues:
            return 'Secure'
        elif len(issues) == 1:
            return f'Warning: {issues[0]}'
        else:
            return f'Issues: {len(issues)} problems'

def create_mobile_manager(environment: str = 'dev'):
    """
    Convenience function to create mobile device manager
    
    Args:
        environment: JAMF environment ('dev', 'prod', etc.)
        
    Returns:
        MobileDeviceManager instance
    """
    from jamf_auth import get_jamf_auth
    auth = get_jamf_auth(environment)
    return MobileDeviceManager(auth)
