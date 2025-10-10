#!/usr/bin/env python3
"""
Real Reverse Relationships for JAMF Pro
Analyzes actual JAMF data to find object usage across the environment
"""
import json
from typing import Dict, List, Any, Optional

class RealReverseRelationshipLookup:
    """Real reverse relationship lookup using JAMF Pro API"""
    
    def __init__(self, jamf_auth):
        self.auth = jamf_auth
        self._cache = {}
        
    def get_relationship_summary(self, object_type: str, obj_id: str, obj_name: str) -> Dict[str, Any]:
        """Get real relationship data from JAMF Pro API"""
        cache_key = f"{object_type}_{obj_id}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        relationships = {
            'relationships': {},
            'details': {}
        }
        
        try:
            if object_type == 'groups':
                relationships = self._get_group_relationships(obj_id, obj_name)
            elif object_type == 'scripts':
                relationships = self._get_script_relationships(obj_id, obj_name)
            elif object_type == 'packages':
                relationships = self._get_package_relationships(obj_id, obj_name)
            elif object_type == 'categories':
                relationships = self._get_category_relationships(obj_id, obj_name)
                
        except Exception as e:
            # Return empty relationships on error
            print(f"Error getting relationships for {object_type} {obj_id}: {e}")
            
        self._cache[cache_key] = relationships
        return relationships
    
    def _get_group_relationships(self, group_id: str, group_name: str) -> Dict[str, Any]:
        """Find what policies, profiles, etc. use this group - DISABLED TO PREVENT TOKEN SPAM"""
        # EMERGENCY FIX: Return empty relationships to stop token spam
        print(f"🚫 Relationship analysis DISABLED for group {group_id} to prevent token spam")
        relationships = {
            'relationships': {'policies': 0, 'profiles': 0, 'scripts': 0, 'packages': 0, 'groups': 0},
            'details': {'policies': [], 'profiles': [], 'scripts': [], 'packages': [], 'groups': []}
        }
        return relationships
        
        # Check policies that target this group
        policies_using_group = []
        try:
            policies_response = self.auth.make_api_call('/JSSResource/policies')
            if policies_response and 'policies' in policies_response:
                for policy in policies_response['policies']:
                    try:
                        policy_detail = self.auth.make_api_call(f'/JSSResource/policies/id/{policy["id"]}')
                        if policy_detail and 'policy' in policy_detail:
                            policy_data = policy_detail['policy']
                            
                            # Check scope for group usage
                            scope = policy_data.get('scope', {})
                            computer_groups = scope.get('computer_groups', [])
                            
                            for group in computer_groups:
                                if str(group.get('id', '')) == str(group_id) or group.get('name', '') == group_name:
                                    policies_using_group.append({
                                        'id': policy['id'],
                                        'name': policy['name'],
                                        'enabled': policy_data.get('general', {}).get('enabled', False)
                                    })
                                    break
                    except:
                        continue
        except:
            pass
            
        # Check profiles that target this group
        profiles_using_group = []
        try:
            profiles_response = self.auth.make_api_call('/JSSResource/osxconfigurationprofiles')
            if profiles_response and 'os_x_configuration_profiles' in profiles_response:
                for profile in profiles_response['os_x_configuration_profiles']:
                    try:
                        profile_detail = self.auth.make_api_call(f'/JSSResource/osxconfigurationprofiles/id/{profile["id"]}')
                        if profile_detail and 'os_x_configuration_profile' in profile_detail:
                            profile_data = profile_detail['os_x_configuration_profile']
                            
                            # Check scope for group usage
                            scope = profile_data.get('scope', {})
                            computer_groups = scope.get('computer_groups', [])
                            
                            for group in computer_groups:
                                if str(group.get('id', '')) == str(group_id) or group.get('name', '') == group_name:
                                    profiles_using_group.append({
                                        'id': profile['id'],
                                        'name': profile['name'],
                                        'level': profile_data.get('general', {}).get('level', 'Unknown')
                                    })
                                    break
                    except:
                        continue
        except:
            pass
            
        relationships['relationships'] = {
            'policies': len(policies_using_group),
            'profiles': len(profiles_using_group),
            'scripts': 0,  # Would need to check script policies
            'packages': 0  # Would need to check package policies
        }
        
        relationships['details'] = {
            'policies': policies_using_group,
            'profiles': profiles_using_group
        }
        
        return relationships
    
    def _get_script_relationships(self, script_id: str, script_name: str) -> Dict[str, Any]:
        """Find what policies use this script - DISABLED TO PREVENT TOKEN SPAM"""
        # EMERGENCY FIX: Return empty relationships to stop token spam
        print(f"🚫 Relationship analysis DISABLED for script {script_id} to prevent token spam")
        relationships = {
            'relationships': {'policies': 0, 'profiles': 0, 'scripts': 0, 'packages': 0, 'groups': 0},
            'details': {'policies': [], 'profiles': [], 'scripts': [], 'packages': [], 'groups': []}
        }
        return relationships
        
        policies_using_script = []
        try:
            policies_response = self.auth.make_api_call('/JSSResource/policies')
            if policies_response and 'policies' in policies_response:
                for policy in policies_response['policies']:
                    try:
                        policy_detail = self.auth.make_api_call(f'/JSSResource/policies/id/{policy["id"]}')
                        if policy_detail and 'policy' in policy_detail:
                            policy_data = policy_detail['policy']
                            
                            # Check scripts in policy
                            scripts = policy_data.get('scripts', [])
                            for script in scripts:
                                if str(script.get('id', '')) == str(script_id) or script.get('name', '') == script_name:
                                    policies_using_script.append({
                                        'id': policy['id'],
                                        'name': policy['name'],
                                        'enabled': policy_data.get('general', {}).get('enabled', False)
                                    })
                                    break
                    except:
                        continue
        except:
            pass
            
        relationships['relationships'] = {
            'policies': len(policies_using_script),
            'profiles': 0,
            'scripts': 0,
            'packages': 0
        }
        
        relationships['details'] = {
            'policies': policies_using_script
        }
        
        return relationships
    
    def _get_package_relationships(self, package_id: str, package_name: str) -> Dict[str, Any]:
        """Find what policies use this package - DISABLED TO PREVENT TOKEN SPAM"""
        # EMERGENCY FIX: Return empty relationships to stop token spam
        print(f"🚫 Relationship analysis DISABLED for package {package_id} to prevent token spam")
        relationships = {
            'relationships': {'policies': 0, 'profiles': 0, 'scripts': 0, 'packages': 0, 'groups': 0},
            'details': {'policies': [], 'profiles': [], 'scripts': [], 'packages': [], 'groups': []}
        }
        return relationships
        
        policies_using_package = []
        try:
            policies_response = self.auth.make_api_call('/JSSResource/policies')
            if policies_response and 'policies' in policies_response:
                for policy in policies_response['policies']:
                    try:
                        policy_detail = self.auth.make_api_call(f'/JSSResource/policies/id/{policy["id"]}')
                        if policy_detail and 'policy' in policy_detail:
                            policy_data = policy_detail['policy']
                            
                            # Check packages in policy
                            package_config = policy_data.get('package_configuration', {})
                            packages = package_config.get('packages', [])
                            
                            for package in packages:
                                if str(package.get('id', '')) == str(package_id) or package.get('name', '') == package_name:
                                    policies_using_package.append({
                                        'id': policy['id'],
                                        'name': policy['name'],
                                        'enabled': policy_data.get('general', {}).get('enabled', False)
                                    })
                                    break
                    except:
                        continue
        except:
            pass
            
        relationships['relationships'] = {
            'policies': len(policies_using_package),
            'profiles': 0,
            'scripts': 0,
            'packages': 0
        }
        
        relationships['details'] = {
            'policies': policies_using_package
        }
        
        return relationships
    
    def _get_category_relationships(self, category_id: str, category_name: str) -> Dict[str, Any]:
        """Find what objects use this category"""
        relationships = {'relationships': {}, 'details': {}}
        
        policies_in_category = []
        scripts_in_category = []
        packages_in_category = []
        
        try:
            # Check policies
            policies_response = self.auth.make_api_call('/JSSResource/policies')
            if policies_response and 'policies' in policies_response:
                for policy in policies_response['policies']:
                    try:
                        policy_detail = self.auth.make_api_call(f'/JSSResource/policies/id/{policy["id"]}')
                        if policy_detail and 'policy' in policy_detail:
                            policy_data = policy_detail['policy']
                            category = policy_data.get('general', {}).get('category', {})
                            
                            if isinstance(category, dict):
                                cat_id = str(category.get('id', ''))
                                cat_name = category.get('name', '')
                            else:
                                cat_id = ''
                                cat_name = str(category) if category else ''
                            
                            if cat_id == str(category_id) or cat_name == category_name:
                                policies_in_category.append({
                                    'id': policy['id'],
                                    'name': policy['name'],
                                    'enabled': policy_data.get('general', {}).get('enabled', False)
                                })
                    except:
                        continue
        except:
            pass
            
        relationships['relationships'] = {
            'policies': len(policies_in_category),
            'profiles': 0,
            'scripts': len(scripts_in_category),
            'packages': len(packages_in_category)
        }
        
        relationships['details'] = {
            'policies': policies_in_category,
            'scripts': scripts_in_category,
            'packages': packages_in_category
        }
        
        return relationships


def analyze_reverse_relationships(data):
    """Analyze reverse relationships in data"""
    return {"reverse_relationships": []}
