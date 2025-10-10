#!/usr/bin/env python3
"""
Move Command for jpapi CLI
Move JAMF objects between categories, groups, and organizational units
"""
from argparse import ArgumentParser, Namespace
import argparse
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add base to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.command import BaseCommand

class MoveCommand(BaseCommand):
    """📦 Move JAMF objects between categories and organizational units"""
    
    def __init__(self):
        super().__init__(
            name="move",
            description="📦 Move JAMF objects between categories and organizational units"
        )
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add move command arguments with comprehensive aliases"""
        # Support flexible positional arguments
        parser.add_argument('move_target', nargs='?', 
                          help='What to move (disabled, policies/pol, profiles/prf, devices)')
        parser.add_argument('move_action', nargs='?',
                          help='Move action or destination')
        parser.add_argument('move_terms', nargs='*',
                          help='Additional parameters')
        
        # Traditional subcommand structure
        subparsers = parser.add_subparsers(dest='move_object', help='Object type to move')
        
        # Move disabled policies - main command
        disabled_parser = subparsers.add_parser('disabled', help='Move disabled objects (also: inactive)')
        disabled_subparsers = disabled_parser.add_subparsers(dest='disabled_type', help='Type of disabled objects')
        
        disabled_policies_parser = disabled_subparsers.add_parser('policies', help='Move disabled policies')
        disabled_policies_parser.add_argument('--to-category', default='Archive', help='Target category (default: Archive)')
        disabled_policies_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
        self.setup_common_args(disabled_policies_parser)
        
        disabled_profiles_parser = disabled_subparsers.add_parser('profiles', help='Move disabled profiles')
        disabled_profiles_parser.add_argument('--to-category', default='Archive', help='Target category (default: Archive)')
        disabled_profiles_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
        self.setup_common_args(disabled_profiles_parser)
        
        # Hidden aliases for disabled
        for alias in ['inactive', 'unused']:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_subparsers = alias_parser.add_subparsers(dest='disabled_type', help='Type of disabled objects')
            
            alias_policies_parser = alias_subparsers.add_parser('policies', help='Move disabled policies')
            alias_policies_parser.add_argument('--to-category', default='Archive', help='Target category')
            alias_policies_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
            self.setup_common_args(alias_policies_parser)
            
            alias_profiles_parser = alias_subparsers.add_parser('profiles', help='Move disabled profiles')
            alias_profiles_parser.add_argument('--to-category', default='Archive', help='Target category')
            alias_profiles_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
            self.setup_common_args(alias_profiles_parser)
        
        # Move policies - main command with aliases in help
        policies_parser = subparsers.add_parser('policies', help='Move policies to category (also: policy, pol)')
        policies_parser.add_argument('policy_filter', help='Policy name filter (supports wildcards)')
        policies_parser.add_argument('--to-category', required=True, help='Target category name')
        policies_parser.add_argument('--from-category', help='Source category filter')
        policies_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
        self.setup_common_args(policies_parser)
        
        # Hidden aliases for policies
        for alias in ['policy', 'pol']:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument('policy_filter', help='Policy name filter (supports wildcards)')
            alias_parser.add_argument('--to-category', required=True, help='Target category name')
            alias_parser.add_argument('--from-category', help='Source category filter')
            alias_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
            self.setup_common_args(alias_parser)
        
        # Move profiles - main command with aliases in help
        profiles_parser = subparsers.add_parser('profiles', help='Move profiles to category (also: profile, prf)')
        profiles_parser.add_argument('profile_filter', help='Profile name filter (supports wildcards)')
        profiles_parser.add_argument('--to-category', required=True, help='Target category name')
        profiles_parser.add_argument('--from-category', help='Source category filter')
        profiles_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
        self.setup_common_args(profiles_parser)
        
        # Hidden aliases for profiles
        for alias in ['profile', 'prf', 'config', 'configs']:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument('profile_filter', help='Profile name filter (supports wildcards)')
            alias_parser.add_argument('--to-category', required=True, help='Target category name')
            alias_parser.add_argument('--from-category', help='Source category filter')
            alias_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
            self.setup_common_args(alias_parser)
        
        # Move devices - main command with aliases in help
        devices_parser = subparsers.add_parser('devices', help='Move devices between groups (also: device, dev)')
        devices_parser.add_argument('device_filter', help='Device name filter (supports wildcards)')
        devices_parser.add_argument('--to-group', required=True, help='Target group name')
        devices_parser.add_argument('--from-group', help='Source group filter')
        devices_parser.add_argument('--type', choices=['computer', 'mobile'], default='computer', help='Device type')
        devices_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
        self.setup_common_args(devices_parser)
        
        # Hidden aliases for devices
        for alias in ['device', 'dev', 'computers', 'mobile']:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_parser.add_argument('device_filter', help='Device name filter (supports wildcards)')
            alias_parser.add_argument('--to-group', required=True, help='Target group name')
            alias_parser.add_argument('--from-group', help='Source group filter')
            alias_parser.add_argument('--type', choices=['computer', 'mobile'], 
                                    default='computer' if alias in ['computers', 'device', 'dev'] else 'mobile', 
                                    help='Device type')
            alias_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
            self.setup_common_args(alias_parser)
    
    def execute(self, args: Namespace) -> int:
        """Execute the move command with flexible parsing"""
        if not self.check_auth(args):
            return 1
        
        try:
            # Handle conversational patterns
            if hasattr(args, 'move_target') and args.move_target:
                return self._handle_conversational_move(args)
            
            # Handle traditional subcommand structure
            if not args.move_object:
                print("📦 Move JAMF Objects - Bulk Organization:")
                print()
                print("💬 Quick Move:")
                print("   jpapi move disabled policies")
                print("   jpapi move policies '*Chrome*' --to-category Software")
                print("   jpapi move devices 'MacBook*' --to-group 'IT Department'")
                print()
                print("🏗️  Traditional Move:")
                print("   jpapi move disabled policies --to-category Archive")
                print("   jpapi move profiles 'WiFi*' --to-category Network")
                print("   jpapi move devices 'iPad*' --to-group Students --type mobile")
                print()
                print("📦 Available Operations:")
                print("   disabled - Move disabled policies/profiles to archive")
                print("   policies - Move policies between categories")
                print("   profiles - Move profiles between categories")
                print("   devices - Move devices between groups")
                return 1
            
            # Route to appropriate handler
            if args.move_object in ['disabled', 'inactive', 'unused']:
                return self._handle_disabled_move(args)
            elif args.move_object in ['policies', 'policy', 'pol']:
                return self._move_policies(args)
            elif args.move_object in ['profiles', 'profile', 'prf', 'config', 'configs']:
                return self._move_profiles(args)
            elif args.move_object in ['devices', 'device', 'dev', 'computers', 'mobile']:
                return self._move_devices(args)
            else:
                print(f"❌ Unknown move object: {args.move_object}")
                return 1
                
        except Exception as e:
            return self.handle_api_error(e)
    
    def _handle_conversational_move(self, args: Namespace) -> int:
        """Handle conversational move patterns"""
        target = args.move_target.lower()
        action = args.move_action.lower() if args.move_action else None
        terms = args.move_terms if args.move_terms else []
        
        print(f"📦 Moving {target}: {action} {' '.join(terms)}")
        
        # Handle "disabled policies" pattern
        if target == 'disabled' and action in ['policies', 'policy', 'pol']:
            return self._move_disabled_policies_conversational(terms, args)
        elif target == 'disabled' and action in ['profiles', 'profile', 'prf']:
            return self._move_disabled_profiles_conversational(terms, args)
        
        # Handle "policies to category" pattern
        elif target in ['policies', 'policy', 'pol']:
            if not action:
                print("❌ Please specify policy filter")
                return 1
            return self._move_policies_conversational(action, terms, args)
        
        # Handle "profiles to category" pattern
        elif target in ['profiles', 'profile', 'prf']:
            if not action:
                print("❌ Please specify profile filter")
                return 1
            return self._move_profiles_conversational(action, terms, args)
        
        # Handle "devices to group" pattern
        elif target in ['devices', 'device', 'dev', 'computers', 'mobile']:
            if not action:
                print("❌ Please specify device filter")
                return 1
            device_type = 'mobile' if target == 'mobile' else 'computer'
            return self._move_devices_conversational(action, terms, device_type, args)
        
        else:
            print(f"❌ Unknown move pattern: {target} {action}")
            print("   Try: disabled policies, policies <filter>, devices <filter>")
            return 1
    
    def _handle_disabled_move(self, args: Namespace) -> int:
        """Handle moving disabled objects"""
        if not hasattr(args, 'disabled_type') or not args.disabled_type:
            print("📦 Move Disabled Objects:")
            print("   jpapi move disabled policies  # Move disabled policies to Archive")
            print("   jpapi move disabled profiles  # Move disabled profiles to Archive")
            return 1
        
        if args.disabled_type == 'policies':
            return self._move_disabled_policies(args)
        elif args.disabled_type == 'profiles':
            return self._move_disabled_profiles(args)
        else:
            print(f"❌ Unknown disabled type: {args.disabled_type}")
            return 1
    
    def _move_disabled_policies(self, args: Namespace) -> int:
        """Move all disabled policies to specified category"""
        try:
            print(f"📋 Moving Disabled Policies to Category: {args.to_category}")
            
            # Get all policies
            response = self.auth.api_request('GET', '/JSSResource/policies')
            
            if 'policies' not in response or 'policy' not in response['policies']:
                print("❌ No policies found")
                return 1
            
            policies = response['policies']['policy']
            disabled_policies = []
            
            # Find disabled policies
            for policy in policies:
                # Get detailed policy info to check enabled status
                try:
                    detail_response = self.auth.api_request('GET', f'/JSSResource/policies/id/{policy["id"]}')
                    if 'policy' in detail_response:
                        policy_detail = detail_response['policy']
                        if not policy_detail.get('general', {}).get('enabled', True):
                            disabled_policies.append(policy_detail)
                except Exception:
                    continue
            
            if not disabled_policies:
                print("✅ No disabled policies found")
                return 0
            
            print(f"📋 Found {len(disabled_policies)} disabled policies:")
            for policy in disabled_policies[:5]:  # Show first 5
                print(f"   - {policy.get('general', {}).get('name', 'Unknown')}")
            if len(disabled_policies) > 5:
                print(f"   ... and {len(disabled_policies) - 5} more")
            
            # Confirm operation
            if not args.confirm:
                confirm = input(f"\n❓ Move {len(disabled_policies)} disabled policies to '{args.to_category}' category? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("❌ Operation cancelled")
                    return 1
            
            # Move policies
            moved_count = 0
            for policy in disabled_policies:
                try:
                    # Update policy category
                    policy_data = {
                        'policy': {
                            'general': {
                                'id': policy['general']['id'],
                                'name': policy['general']['name'],
                                'category': {'name': args.to_category}
                            }
                        }
                    }
                    
                    update_response = self.auth.api_request('PUT', f'/JSSResource/policies/id/{policy["general"]["id"]}', data=policy_data)
                    
                    if update_response:
                        moved_count += 1
                        print(f"   ✅ Moved: {policy['general']['name']}")
                    else:
                        print(f"   ❌ Failed: {policy['general']['name']}")
                        
                except Exception as e:
                    print(f"   ❌ Error moving {policy['general']['name']}: {e}")
            
            print(f"\n✅ Successfully moved {moved_count}/{len(disabled_policies)} disabled policies")
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _move_disabled_profiles(self, args: Namespace) -> int:
        """Move all disabled profiles to specified category"""
        try:
            print(f"⚙️ Moving Disabled Profiles to Category: {args.to_category}")
            
            # Get all profiles
            response = self.auth.api_request('GET', '/JSSResource/osxconfigurationprofiles')
            
            if 'os_x_configuration_profiles' not in response:
                print("❌ No profiles found")
                return 1
            
            profiles = response['os_x_configuration_profiles'].get('os_x_configuration_profile', [])
            disabled_profiles = []
            
            # Find disabled profiles (profiles without deployment targets are considered disabled)
            for profile in profiles:
                try:
                    detail_response = self.auth.api_request('GET', f'/JSSResource/osxconfigurationprofiles/id/{profile["id"]}')
                    if 'os_x_configuration_profile' in detail_response:
                        profile_detail = detail_response['os_x_configuration_profile']
                        # Check if profile has no scope (considered disabled)
                        scope = profile_detail.get('scope', {})
                        if not scope.get('computers') and not scope.get('computer_groups'):
                            disabled_profiles.append(profile_detail)
                except Exception:
                    continue
            
            if not disabled_profiles:
                print("✅ No disabled profiles found")
                return 0
            
            print(f"⚙️ Found {len(disabled_profiles)} disabled profiles:")
            for profile in disabled_profiles[:5]:  # Show first 5
                print(f"   - {profile.get('general', {}).get('name', 'Unknown')}")
            if len(disabled_profiles) > 5:
                print(f"   ... and {len(disabled_profiles) - 5} more")
            
            # Confirm operation
            if not args.confirm:
                confirm = input(f"\n❓ Move {len(disabled_profiles)} disabled profiles to '{args.to_category}' category? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("❌ Operation cancelled")
                    return 1
            
            # Move profiles
            moved_count = 0
            for profile in disabled_profiles:
                try:
                    # Update profile category
                    profile_data = {
                        'os_x_configuration_profile': {
                            'general': {
                                'id': profile['general']['id'],
                                'name': profile['general']['name'],
                                'category': {'name': args.to_category}
                            }
                        }
                    }
                    
                    update_response = self.auth.api_request('PUT', f'/JSSResource/osxconfigurationprofiles/id/{profile["general"]["id"]}', data=profile_data)
                    
                    if update_response:
                        moved_count += 1
                        print(f"   ✅ Moved: {profile['general']['name']}")
                    else:
                        print(f"   ❌ Failed: {profile['general']['name']}")
                        
                except Exception as e:
                    print(f"   ❌ Error moving {profile['general']['name']}: {e}")
            
            print(f"\n✅ Successfully moved {moved_count}/{len(disabled_profiles)} disabled profiles")
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _move_policies(self, args: Namespace) -> int:
        """Move policies matching filter to specified category"""
        try:
            print(f"📋 Moving Policies: {args.policy_filter} → {args.to_category}")
            
            # Get all policies
            response = self.auth.api_request('GET', '/JSSResource/policies')
            
            if 'policies' not in response or 'policy' not in response['policies']:
                print("❌ No policies found")
                return 1
            
            policies = response['policies']['policy']
            matching_policies = []
            
            # Filter policies
            for policy in policies:
                policy_name = policy.get('name', '')
                
                # Apply name filter
                if self._matches_filter(policy_name, args.policy_filter):
                    # Apply category filter if specified
                    if args.from_category:
                        try:
                            detail_response = self.auth.api_request('GET', f'/JSSResource/policies/id/{policy["id"]}')
                            if 'policy' in detail_response:
                                current_category = detail_response['policy'].get('general', {}).get('category', {}).get('name', '')
                                if args.from_category.lower() in current_category.lower():
                                    matching_policies.append(detail_response['policy'])
                        except Exception:
                            continue
                    else:
                        matching_policies.append(policy)
            
            if not matching_policies:
                print(f"❌ No policies match filter: {args.policy_filter}")
                return 1
            
            print(f"📋 Found {len(matching_policies)} matching policies:")
            for policy in matching_policies[:5]:  # Show first 5
                name = policy.get('general', {}).get('name', policy.get('name', 'Unknown'))
                print(f"   - {name}")
            if len(matching_policies) > 5:
                print(f"   ... and {len(matching_policies) - 5} more")
            
            # Confirm operation
            if not args.confirm:
                confirm = input(f"\n❓ Move {len(matching_policies)} policies to '{args.to_category}' category? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("❌ Operation cancelled")
                    return 1
            
            # Move policies
            moved_count = 0
            for policy in matching_policies:
                try:
                    policy_id = policy.get('general', {}).get('id', policy.get('id'))
                    policy_name = policy.get('general', {}).get('name', policy.get('name', 'Unknown'))
                    
                    # Update policy category
                    policy_data = {
                        'policy': {
                            'general': {
                                'id': policy_id,
                                'name': policy_name,
                                'category': {'name': args.to_category}
                            }
                        }
                    }
                    
                    update_response = self.auth.api_request('PUT', f'/JSSResource/policies/id/{policy_id}', data=policy_data)
                    
                    if update_response:
                        moved_count += 1
                        print(f"   ✅ Moved: {policy_name}")
                    else:
                        print(f"   ❌ Failed: {policy_name}")
                        
                except Exception as e:
                    print(f"   ❌ Error moving {policy_name}: {e}")
            
            print(f"\n✅ Successfully moved {moved_count}/{len(matching_policies)} policies")
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _move_profiles(self, args: Namespace) -> int:
        """Move profiles matching filter to specified category"""
        try:
            print(f"⚙️ Moving Profiles: {args.profile_filter} → {args.to_category}")
            
            # Similar implementation to _move_policies but for profiles
            # Implementation would follow the same pattern as policies
            print("⚠️  Profile moving functionality coming soon...")
            print("   This would move configuration profiles between categories")
            print(f"   Filter: {args.profile_filter}")
            print(f"   Target Category: {args.to_category}")
            if args.from_category:
                print(f"   Source Category: {args.from_category}")
            
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _move_devices(self, args: Namespace) -> int:
        """Move devices matching filter between groups"""
        try:
            print(f"📱 Moving {args.type.title()} Devices: {args.device_filter} → {args.to_group}")
            
            # Implementation would move devices between groups
            print("⚠️  Device moving functionality coming soon...")
            print("   This would move devices between computer/mobile device groups")
            print(f"   Device Type: {args.type}")
            print(f"   Filter: {args.device_filter}")
            print(f"   Target Group: {args.to_group}")
            if args.from_group:
                print(f"   Source Group: {args.from_group}")
            
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _move_disabled_policies_conversational(self, terms: List[str], args: Namespace) -> int:
        """Move disabled policies using conversational terms"""
        # Parse target category from terms
        to_category = 'Archive'  # default
        for term in terms:
            if term.lower() not in ['to', 'into', 'category']:
                to_category = term.title()
                break
        
        # Create mock args
        mock_args = Namespace()
        mock_args.to_category = to_category
        mock_args.confirm = getattr(args, 'confirm', False)
        mock_args.format = getattr(args, 'format', 'table')
        mock_args.output = getattr(args, 'output', None)
        
        return self._move_disabled_policies(mock_args)
    
    def _move_disabled_profiles_conversational(self, terms: List[str], args: Namespace) -> int:
        """Move disabled profiles using conversational terms"""
        # Parse target category from terms
        to_category = 'Archive'  # default
        for term in terms:
            if term.lower() not in ['to', 'into', 'category']:
                to_category = term.title()
                break
        
        # Create mock args
        mock_args = Namespace()
        mock_args.to_category = to_category
        mock_args.confirm = getattr(args, 'confirm', False)
        mock_args.format = getattr(args, 'format', 'table')
        mock_args.output = getattr(args, 'output', None)
        
        return self._move_disabled_profiles(mock_args)
    
    def _move_policies_conversational(self, policy_filter: str, terms: List[str], args: Namespace) -> int:
        """Move policies using conversational terms"""
        # Parse target category from terms
        to_category = None
        from_category = None
        
        # Look for "to" keyword
        terms_text = ' '.join(terms)
        if 'to' in terms_text:
            words = terms_text.split()
            try:
                to_index = words.index('to')
                if to_index + 1 < len(words):
                    to_category = words[to_index + 1].title()
            except ValueError:
                pass
        
        if not to_category and terms:
            to_category = terms[0].title()
        
        if not to_category:
            print("❌ Please specify target category")
            return 1
        
        # Create mock args
        mock_args = Namespace()
        mock_args.policy_filter = policy_filter
        mock_args.to_category = to_category
        mock_args.from_category = from_category
        mock_args.confirm = getattr(args, 'confirm', False)
        mock_args.format = getattr(args, 'format', 'table')
        mock_args.output = getattr(args, 'output', None)
        
        return self._move_policies(mock_args)
    
    def _move_profiles_conversational(self, profile_filter: str, terms: List[str], args: Namespace) -> int:
        """Move profiles using conversational terms"""
        # Similar to policies conversational parsing
        to_category = None
        
        # Look for "to" keyword
        terms_text = ' '.join(terms)
        if 'to' in terms_text:
            words = terms_text.split()
            try:
                to_index = words.index('to')
                if to_index + 1 < len(words):
                    to_category = words[to_index + 1].title()
            except ValueError:
                pass
        
        if not to_category and terms:
            to_category = terms[0].title()
        
        if not to_category:
            print("❌ Please specify target category")
            return 1
        
        # Create mock args
        mock_args = Namespace()
        mock_args.profile_filter = profile_filter
        mock_args.to_category = to_category
        mock_args.from_category = None
        mock_args.confirm = getattr(args, 'confirm', False)
        mock_args.format = getattr(args, 'format', 'table')
        mock_args.output = getattr(args, 'output', None)
        
        return self._move_profiles(mock_args)
    
    def _move_devices_conversational(self, device_filter: str, terms: List[str], device_type: str, args: Namespace) -> int:
        """Move devices using conversational terms"""
        # Parse target group from terms
        to_group = None
        
        # Look for "to" keyword
        terms_text = ' '.join(terms)
        if 'to' in terms_text:
            words = terms_text.split()
            try:
                to_index = words.index('to')
                if to_index + 1 < len(words):
                    to_group = ' '.join(words[to_index + 1:])
            except ValueError:
                pass
        
        if not to_group and terms:
            to_group = ' '.join(terms)
        
        if not to_group:
            print("❌ Please specify target group")
            return 1
        
        # Create mock args
        mock_args = Namespace()
        mock_args.device_filter = device_filter
        mock_args.to_group = to_group
        mock_args.from_group = None
        mock_args.type = device_type
        mock_args.confirm = getattr(args, 'confirm', False)
        mock_args.format = getattr(args, 'format', 'table')
        mock_args.output = getattr(args, 'output', None)
        
        return self._move_devices(mock_args)
    
    def _matches_filter(self, text: str, filter_pattern: str) -> bool:
        """Check if text matches filter pattern (supports wildcards)"""
        import re
        
        if '*' in filter_pattern:
            # Convert wildcard pattern to regex
            regex_pattern = filter_pattern.replace('*', '.*')
            return bool(re.match(regex_pattern, text, re.IGNORECASE))
        else:
            return filter_pattern.lower() in text.lower()
