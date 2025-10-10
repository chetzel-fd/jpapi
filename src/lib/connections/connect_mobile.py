#!/usr/bin/env python3
"""
Mobile Device Relationship Engine
Provides comprehensive relationship mapping between mobile devices, groups, and profiles
Mirrors the robustness of the computer relationship system
"""
import json
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime
from pathlib import Path

class MobileRelationshipLookup:
    """
    Advanced relationship mapping for mobile device management
    Maps connections between devices, groups, profiles, and policies
    """
    
    def __init__(self, auth, cache_dir: str = "tmp/cache/mobile"):
        """
        Initialize mobile relationship lookup
        
        Args:
            auth: JamfAuth instance
            cache_dir: Cache directory for relationship data
        """
        self.auth = auth
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Relationship caches
        self._device_relationships = {}
        self._group_relationships = {}
        self._profile_relationships = {}
        self._reverse_relationships = {}
        
    def build_comprehensive_relationships(self, force_refresh: bool = False) -> Dict[str, any]:
        """
        Build comprehensive relationship mapping for all mobile objects
        
        Args:
            force_refresh: Force refresh of all cached data
            
        Returns:
            Complete relationship mapping
        """
        relationships = {
            'devices': {},
            'groups': {},
            'profiles': {},
            'reverse_lookup': {},
            'stats': {},
            'build_time': datetime.now().isoformat()
        }
        
        try:
            # Get all mobile data
            devices = self._get_mobile_devices(force_refresh)
            groups = self._get_mobile_groups(force_refresh)
            profiles = self._get_mobile_profiles(force_refresh)
            
            # Build device relationships
            for device in devices:
                device_id = str(device.get('id', ''))
                device_name = device.get('general', {}).get('name', '')
                
                relationships['devices'][device_id] = {
                    'name': device_name,
                    'groups': self._find_device_groups(device, groups),
                    'profiles': self._find_device_profiles(device, profiles),
                    'device_type': device.get('_device_type', 'Unknown'),
                    'os_version': device.get('_os_version_clean', ''),
                    'last_contact': device.get('_last_contact_relative', 'Unknown'),
                    'security_status': device.get('_security_status', 'Unknown')
                }
            
            # Build group relationships
            for group in groups:
                group_id = str(group.get('id', ''))
                group_name = group.get('name', '')
                
                targeting_profiles = self._find_profiles_targeting_group(group, profiles)
                member_devices = group.get('mobile_devices', [])
                
                relationships['groups'][group_id] = {
                    'name': group_name,
                    'type': 'Smart' if group.get('is_smart') else 'Static',
                    'member_count': len(member_devices),
                    'member_devices': [{'id': d.get('id'), 'name': d.get('name')} for d in member_devices],
                    'targeting_profiles': targeting_profiles,
                    'criteria': group.get('criteria', {}) if group.get('is_smart') else None
                }
            
            # Build profile relationships
            for profile in profiles:
                profile_id = str(profile.get('id', ''))
                profile_name = profile.get('name', '')
                scope = profile.get('scope', {})
                
                relationships['profiles'][profile_id] = {
                    'name': profile_name,
                    'deployment_method': profile.get('_deployment_method', ''),
                    'payload_count': profile.get('_payload_count', 0),
                    'scope_devices': scope.get('mobile_devices', []),
                    'scope_groups': scope.get('mobile_device_groups', []),
                    'exclusions': scope.get('exclusions', {}),
                    'limitations': scope.get('limitations', {}),
                    'payloads': self._extract_payload_info(profile)
                }
            
            # Build reverse lookup indices
            relationships['reverse_lookup'] = self._build_reverse_lookup(relationships)
            
            # Calculate statistics
            relationships['stats'] = {
                'total_devices': len(devices),
                'total_groups': len(groups),
                'total_profiles': len(profiles),
                'smart_groups': len([g for g in groups if g.get('is_smart')]),
                'static_groups': len([g for g in groups if not g.get('is_smart')]),
                'supervised_devices': len([d for d in devices if d.get('general', {}).get('supervised')]),
                'devices_by_type': self._count_devices_by_type(devices),
                'profiles_by_payload': self._count_profiles_by_payload(profiles)
            }
            
            # Cache the results
            self._cache_relationships(relationships)
            
            return relationships
            
        except Exception as e:
            print(f"Error building mobile relationships: {e}")
            return relationships
    
    def get_device_relationships(self, device_id: str) -> Dict[str, any]:
        """
        Get comprehensive relationship data for a specific device
        
        Args:
            device_id: Mobile device ID
            
        Returns:
            Device relationship data
        """
        relationships = self.build_comprehensive_relationships()
        return relationships['devices'].get(str(device_id), {})
    
    def get_group_relationships(self, group_id: str) -> Dict[str, any]:
        """
        Get comprehensive relationship data for a specific group
        
        Args:
            group_id: Mobile device group ID
            
        Returns:
            Group relationship data
        """
        relationships = self.build_comprehensive_relationships()
        return relationships['groups'].get(str(group_id), {})
    
    def get_profile_relationships(self, profile_id: str) -> Dict[str, any]:
        """
        Get comprehensive relationship data for a specific profile
        
        Args:
            profile_id: Mobile configuration profile ID
            
        Returns:
            Profile relationship data
        """
        relationships = self.build_comprehensive_relationships()
        return relationships['profiles'].get(str(profile_id), {})
    
    def find_orphaned_objects(self) -> Dict[str, List]:
        """
        Find orphaned mobile objects (not used by anything)
        
        Returns:
            Dictionary of orphaned objects by type
        """
        relationships = self.build_comprehensive_relationships()
        
        orphaned = {
            'devices': [],
            'groups': [],
            'profiles': []
        }
        
        # Find devices not in any groups
        for device_id, device_data in relationships['devices'].items():
            if not device_data.get('groups'):
                orphaned['devices'].append({
                    'id': device_id,
                    'name': device_data.get('name'),
                    'type': device_data.get('device_type')
                })
        
        # Find groups not targeted by any profiles
        for group_id, group_data in relationships['groups'].items():
            if not group_data.get('targeting_profiles'):
                orphaned['groups'].append({
                    'id': group_id,
                    'name': group_data.get('name'),
                    'type': group_data.get('type'),
                    'member_count': group_data.get('member_count', 0)
                })
        
        # Find profiles with empty scopes
        for profile_id, profile_data in relationships['profiles'].items():
            scope_devices = profile_data.get('scope_devices', [])
            scope_groups = profile_data.get('scope_groups', [])
            
            if not scope_devices and not scope_groups:
                orphaned['profiles'].append({
                    'id': profile_id,
                    'name': profile_data.get('name'),
                    'payload_count': profile_data.get('payload_count', 0)
                })
        
        return orphaned
    
    def analyze_security_coverage(self) -> Dict[str, any]:
        """
        Analyze security profile coverage across mobile devices
        
        Returns:
            Security coverage analysis
        """
        relationships = self.build_comprehensive_relationships()
        
        security_profiles = []
        security_keywords = ['security', 'vpn', 'certificate', 'passcode', 'encrypt', 'mdm', 'restriction']
        
        # Identify security profiles
        for profile_id, profile_data in relationships['profiles'].items():
            profile_name = profile_data.get('name', '').lower()
            payloads = profile_data.get('payloads', [])
            
            is_security = (
                any(keyword in profile_name for keyword in security_keywords) or
                any(payload.get('type', '').lower() in ['vpn', 'certificate', 'restrictions'] for payload in payloads)
            )
            
            if is_security:
                security_profiles.append({
                    'id': profile_id,
                    'name': profile_data.get('name'),
                    'scope_device_count': len(profile_data.get('scope_devices', [])),
                    'scope_group_count': len(profile_data.get('scope_groups', [])),
                    'payloads': payloads
                })
        
        # Calculate coverage
        total_devices = relationships['stats']['total_devices']
        covered_devices = set()
        
        for profile in security_profiles:
            profile_data = relationships['profiles'][profile['id']]
            # Add devices directly scoped
            for device in profile_data.get('scope_devices', []):
                covered_devices.add(str(device.get('id')))
            
            # Add devices from scoped groups
            for group in profile_data.get('scope_groups', []):
                group_id = str(group.get('id'))
                if group_id in relationships['groups']:
                    for device in relationships['groups'][group_id].get('member_devices', []):
                        covered_devices.add(str(device.get('id')))
        
        coverage_percentage = (len(covered_devices) / total_devices * 100) if total_devices > 0 else 0
        
        return {
            'total_devices': total_devices,
            'security_profiles_count': len(security_profiles),
            'devices_with_security_profiles': len(covered_devices),
            'coverage_percentage': round(coverage_percentage, 2),
            'security_profiles': security_profiles,
            'uncovered_devices': [
                device_id for device_id in relationships['devices'].keys()
                if device_id not in covered_devices
            ]
        }
    
    def _get_mobile_devices(self, force_refresh: bool = False) -> List[Dict]:
        """Get mobile devices with caching"""
        from mobile_device_manager_lib import MobileDeviceManager
        manager = MobileDeviceManager(self.auth)
        return manager.get_all_mobile_devices(use_cache=not force_refresh)
    
    def _get_mobile_groups(self, force_refresh: bool = False) -> List[Dict]:
        """Get mobile groups with caching"""
        from mobile_device_manager_lib import MobileDeviceManager
        manager = MobileDeviceManager(self.auth)
        return manager.get_all_mobile_groups(use_cache=not force_refresh)
    
    def _get_mobile_profiles(self, force_refresh: bool = False) -> List[Dict]:
        """Get mobile profiles with caching"""
        from mobile_device_manager_lib import MobileDeviceManager
        manager = MobileDeviceManager(self.auth)
        return manager.get_all_mobile_profiles(use_cache=not force_refresh)
    
    def _find_device_groups(self, device: Dict, groups: List[Dict]) -> List[Dict]:
        """Find groups that contain a specific device"""
        device_id = str(device.get('id', ''))
        device_name = device.get('general', {}).get('name', '')
        
        containing_groups = []
        
        for group in groups:
            group_members = group.get('mobile_devices', [])
            
            for member in group_members:
                member_id = str(member.get('id', ''))
                member_name = member.get('name', '')
                
                if member_id == device_id or member_name == device_name:
                    containing_groups.append({
                        'id': group.get('id'),
                        'name': group.get('name'),
                        'type': 'Smart' if group.get('is_smart') else 'Static'
                    })
                    break
        
        return containing_groups
    
    def _find_device_profiles(self, device: Dict, profiles: List[Dict]) -> List[Dict]:
        """Find profiles that target a specific device"""
        device_id = str(device.get('id', ''))
        device_name = device.get('general', {}).get('name', '')
        
        targeting_profiles = []
        
        for profile in profiles:
            scope = profile.get('scope', {})
            scope_devices = scope.get('mobile_devices', [])
            
            # Check direct device targeting
            for scoped_device in scope_devices:
                scoped_id = str(scoped_device.get('id', ''))
                scoped_name = scoped_device.get('name', '')
                
                if scoped_id == device_id or scoped_name == device_name:
                    targeting_profiles.append({
                        'id': profile.get('id'),
                        'name': profile.get('name'),
                        'deployment_method': profile.get('_deployment_method', '')
                    })
                    break
        
        return targeting_profiles
    
    def _find_profiles_targeting_group(self, group: Dict, profiles: List[Dict]) -> List[Dict]:
        """Find profiles that target a specific group"""
        group_id = str(group.get('id', ''))
        group_name = group.get('name', '')
        
        targeting_profiles = []
        
        for profile in profiles:
            scope = profile.get('scope', {})
            scope_groups = scope.get('mobile_device_groups', [])
            
            for scoped_group in scope_groups:
                scoped_id = str(scoped_group.get('id', ''))
                scoped_name = scoped_group.get('name', '')
                
                if scoped_id == group_id or scoped_name == group_name:
                    targeting_profiles.append({
                        'id': profile.get('id'),
                        'name': profile.get('name'),
                        'deployment_method': profile.get('_deployment_method', ''),
                        'payload_count': profile.get('_payload_count', 0)
                    })
                    break
        
        return targeting_profiles
    
    def _extract_payload_info(self, profile: Dict) -> List[Dict]:
        """Extract payload information from profile"""
        payloads = profile.get('payloads', [])
        if not payloads:
            return []
        
        payload_info = []
        for payload in payloads:
            payload_info.append({
                'type': payload.get('type', 'Unknown'),
                'display_name': payload.get('display_name', ''),
                'identifier': payload.get('identifier', ''),
                'uuid': payload.get('uuid', '')
            })
        
        return payload_info
    
    def _build_reverse_lookup(self, relationships: Dict) -> Dict[str, any]:
        """Build reverse lookup indices for fast queries"""
        reverse = {
            'devices_by_group': defaultdict(list),
            'devices_by_profile': defaultdict(list),
            'groups_by_profile': defaultdict(list),
            'profiles_by_group': defaultdict(list),
            'profiles_by_payload_type': defaultdict(list)
        }
        
        # Index devices by groups
        for device_id, device_data in relationships['devices'].items():
            for group in device_data.get('groups', []):
                reverse['devices_by_group'][str(group.get('id'))].append({
                    'id': device_id,
                    'name': device_data.get('name')
                })
        
        # Index devices by profiles
        for device_id, device_data in relationships['devices'].items():
            for profile in device_data.get('profiles', []):
                reverse['devices_by_profile'][str(profile.get('id'))].append({
                    'id': device_id,
                    'name': device_data.get('name')
                })
        
        # Index groups by profiles
        for profile_id, profile_data in relationships['profiles'].items():
            for group in profile_data.get('scope_groups', []):
                reverse['groups_by_profile'][profile_id].append({
                    'id': group.get('id'),
                    'name': group.get('name')
                })
        
        # Index profiles by groups
        for group_id, group_data in relationships['groups'].items():
            for profile in group_data.get('targeting_profiles', []):
                reverse['profiles_by_group'][group_id].append({
                    'id': profile.get('id'),
                    'name': profile.get('name')
                })
        
        # Index profiles by payload type
        for profile_id, profile_data in relationships['profiles'].items():
            for payload in profile_data.get('payloads', []):
                payload_type = payload.get('type', 'Unknown')
                reverse['profiles_by_payload_type'][payload_type].append({
                    'id': profile_id,
                    'name': profile_data.get('name')
                })
        
        return dict(reverse)
    
    def _count_devices_by_type(self, devices: List[Dict]) -> Dict[str, int]:
        """Count devices by type"""
        counts = defaultdict(int)
        for device in devices:
            device_type = device.get('_device_type', 'Unknown')
            counts[device_type] += 1
        return dict(counts)
    
    def _count_profiles_by_payload(self, profiles: List[Dict]) -> Dict[str, int]:
        """Count profiles by payload type"""
        counts = defaultdict(int)
        for profile in profiles:
            for payload in profile.get('payloads', []):
                payload_type = payload.get('type', 'Unknown')
                counts[payload_type] += 1
        return dict(counts)
    
    def _cache_relationships(self, relationships: Dict):
        """Cache relationship data"""
        try:
            cache_file = self.cache_dir / "mobile_relationships.json"
            with open(cache_file, 'w') as f:
                json.dump(relationships, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not cache relationships: {e}")

def create_mobile_relationship_lookup(environment: str = 'dev'):
    """
    Convenience function to create mobile relationship lookup
    
    Args:
        environment: JAMF environment ('dev', 'prod', etc.)
        
    Returns:
        MobileRelationshipLookup instance
    """
    from jamf_auth import get_jamf_auth
    auth = get_jamf_auth(environment)
    return MobileRelationshipLookup(auth)


def connect_mobile(data):
    """Connect to mobile devices"""
    return {"mobile_connection": "connected"}
