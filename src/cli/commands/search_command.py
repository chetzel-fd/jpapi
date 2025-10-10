#!/usr/bin/env python3
"""
Search Command for jpapi CLI
Advanced search capabilities with criteria-based filtering
"""

from argparse import ArgumentParser, Namespace
import argparse
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
import json
import re

# Add base to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.command import BaseCommand

class SearchCommand(BaseCommand):
    """Advanced search operations with criteria-based filtering"""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="Advanced search operations with criteria-based filtering"
        )
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add search command arguments with flexible parsing"""
        # Support both traditional and conversational patterns
        
        # Add positional arguments for natural flow
        parser.add_argument('search_target', nargs='?', 
                          help='What to search (computers, mobile, devices, etc.)')
        parser.add_argument('search_terms', nargs='*',
                          help='Search terms or criteria')
        
        # Traditional subcommand structure
        subparsers = parser.add_subparsers(dest='search_type', help='Search operations')
        
        # Computer searches - main command only in help
        computer_parser = subparsers.add_parser('computers', help='Search computers/Macs (also: comp, mac)')
        computer_subparsers = computer_parser.add_subparsers(dest='computer_search_action', help='Computer search actions')
        
        # Criteria search
        comp_criteria_parser = computer_subparsers.add_parser('criteria', help='Search by criteria')
        comp_criteria_parser.add_argument('--name', help='Filter by computer name (supports wildcards)')
        comp_criteria_parser.add_argument('--model', help='Filter by computer model')
        comp_criteria_parser.add_argument('--os-version', help='Filter by OS version')
        comp_criteria_parser.add_argument('--department', help='Filter by department')
        comp_criteria_parser.add_argument('--building', help='Filter by building')
        comp_criteria_parser.add_argument('--managed', choices=['true', 'false'], help='Filter by managed status')
        self.setup_common_args(comp_criteria_parser)
        
        # Query search
        comp_query_parser = computer_subparsers.add_parser('query', help='Search with query syntax')
        comp_query_parser.add_argument('query_string', help='Query string (e.g., "name:MacBook AND department:IT")')
        self.setup_common_args(comp_query_parser)
        
        # Natural language search
        comp_find_parser = computer_subparsers.add_parser('find', help='Natural language search')
        comp_find_parser.add_argument('search_phrase', nargs='+', help='Natural search phrase')
        self.setup_common_args(comp_find_parser)
        
        # Add hidden aliases for computers
        for alias in ['computer', 'comp', 'mac', 'macs', 'macos']:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_subparsers = alias_parser.add_subparsers(dest='computer_search_action', help='Computer search actions')
            
            # Copy the same structure for aliases
            alias_criteria_parser = alias_subparsers.add_parser('criteria', help='Search by criteria')
            alias_criteria_parser.add_argument('--name', help='Filter by computer name (supports wildcards)')
            alias_criteria_parser.add_argument('--model', help='Filter by computer model')
            alias_criteria_parser.add_argument('--os-version', help='Filter by OS version')
            alias_criteria_parser.add_argument('--department', help='Filter by department')
            alias_criteria_parser.add_argument('--building', help='Filter by building')
            alias_criteria_parser.add_argument('--managed', choices=['true', 'false'], help='Filter by managed status')
            self.setup_common_args(alias_criteria_parser)
            
            alias_query_parser = alias_subparsers.add_parser('query', help='Search with query syntax')
            alias_query_parser.add_argument('query_string', help='Query string')
            self.setup_common_args(alias_query_parser)
            
            alias_find_parser = alias_subparsers.add_parser('find', help='Natural language search')
            alias_find_parser.add_argument('search_phrase', nargs='+', help='Natural search phrase')
            self.setup_common_args(alias_find_parser)
        
        # Mobile device searches - main command only in help
        mobile_parser = subparsers.add_parser('mobile', help='Search mobile devices (also: ios, ipad)')
        mobile_subparsers = mobile_parser.add_subparsers(dest='mobile_search_action', help='Mobile search actions')
        
        # Criteria search
        mobile_criteria_parser = mobile_subparsers.add_parser('criteria', help='Search by criteria')
        mobile_criteria_parser.add_argument('--name', help='Filter by device name (supports wildcards)')
        mobile_criteria_parser.add_argument('--model', help='Filter by device model (e.g., iPad, iPhone)')
        mobile_criteria_parser.add_argument('--os-version', help='Filter by iOS version')
        mobile_criteria_parser.add_argument('--supervised', choices=['true', 'false'], help='Filter by supervision status')
        mobile_criteria_parser.add_argument('--managed', choices=['true', 'false'], help='Filter by managed status')
        mobile_criteria_parser.add_argument('--carrier', help='Filter by carrier')
        self.setup_common_args(mobile_criteria_parser)
        
        # Query search
        mobile_query_parser = mobile_subparsers.add_parser('query', help='Search with query syntax')
        mobile_query_parser.add_argument('query_string', help='Query string (e.g., "model:iPad AND supervised:true")')
        self.setup_common_args(mobile_query_parser)
        
        # Natural language search
        mobile_find_parser = mobile_subparsers.add_parser('find', help='Natural language search')
        mobile_find_parser.add_argument('search_phrase', nargs='+', help='Natural search phrase')
        self.setup_common_args(mobile_find_parser)
        
        # Add hidden aliases for mobile
        for alias in ['ios', 'ipad', 'ipads', 'iphone', 'iphones', 'devices']:
            alias_parser = subparsers.add_parser(alias, help=argparse.SUPPRESS)
            alias_subparsers = alias_parser.add_subparsers(dest='mobile_search_action', help='Mobile search actions')
            
            # Copy the same structure for aliases
            alias_criteria_parser = alias_subparsers.add_parser('criteria', help='Search by criteria')
            alias_criteria_parser.add_argument('--name', help='Filter by device name (supports wildcards)')
            alias_criteria_parser.add_argument('--model', help='Filter by device model')
            alias_criteria_parser.add_argument('--os-version', help='Filter by iOS version')
            alias_criteria_parser.add_argument('--supervised', choices=['true', 'false'], help='Filter by supervision status')
            alias_criteria_parser.add_argument('--managed', choices=['true', 'false'], help='Filter by managed status')
            alias_criteria_parser.add_argument('--carrier', help='Filter by carrier')
            self.setup_common_args(alias_criteria_parser)
            
            alias_query_parser = alias_subparsers.add_parser('query', help='Search with query syntax')
            alias_query_parser.add_argument('query_string', help='Query string')
            self.setup_common_args(alias_query_parser)
            
            alias_find_parser = alias_subparsers.add_parser('find', help='Natural language search')
            alias_find_parser.add_argument('search_phrase', nargs='+', help='Natural search phrase')
            self.setup_common_args(alias_find_parser)
        
        # Quick search options (conversational)
        quick_parser = subparsers.add_parser('for', help='Quick conversational search')
        quick_parser.add_argument('search_phrase', nargs='+', help='What to search for')
        self.setup_common_args(quick_parser)
        
        # Search management
        results_parser = subparsers.add_parser('results', help='Manage search results')
        results_subparsers = results_parser.add_subparsers(dest='results_action', help='Results actions')
        
        results_list_parser = results_subparsers.add_parser('list', help='List saved search results')
        results_list_parser.add_argument('--type', choices=['mobile', 'computer'], help='Filter by search type')
        self.setup_common_args(results_list_parser)
        
        results_export_parser = results_subparsers.add_parser('export', help='Export search results')
        results_export_parser.add_argument('search_id', help='Search result ID to export')
        self.setup_common_args(results_export_parser)
        
        # Search templates
        templates_parser = subparsers.add_parser('templates', help='Manage search templates')
        templates_subparsers = templates_parser.add_subparsers(dest='templates_action', help='Template actions')
        
        templates_list_parser = templates_subparsers.add_parser('list', help='List search templates')
        self.setup_common_args(templates_list_parser)
        
        templates_save_parser = templates_subparsers.add_parser('save', help='Save search as template')
        templates_save_parser.add_argument('name', help='Template name')
        templates_save_parser.add_argument('--search-type', choices=['mobile', 'computer'], required=True, help='Search type')
        templates_save_parser.add_argument('--query', help='Search query to save')
    
    def execute(self, args: Namespace) -> int:
        """Execute the search command with flexible parsing"""
        if not self.check_auth(args):
            return 1
        
        try:
            # Handle conversational patterns first
            if hasattr(args, 'search_target') and args.search_target:
                return self._handle_conversational_search(args)
            
            # Handle traditional subcommand structure
            if not args.search_type:
                print("🔍 Advanced Search - Multiple Ways to Search:")
                print()
                print("💬 Conversational Style:")
                print("   jpapi search computers MacBook")
                print("   jpapi search mobile iPad")
                print("   jpapi search for iPads in IT department")
                print()
                print("🖥️  Traditional Computer Searches:")
                print("   jpapi search computers criteria --name 'MacBook*'")
                print("   jpapi search computers query 'name:MacBook AND department:IT'")
                print("   jpapi search computers find MacBook Pro in IT")
                print()
                print("📱 Traditional Mobile Device Searches:")
                print("   jpapi search mobile criteria --model iPad --supervised true")
                print("   jpapi search ios query 'model:iPad AND supervised:true'")
                print("   jpapi search ipad find supervised devices")
                print()
                print("🔧 Search Management:")
                print("   jpapi search results list --type mobile")
                print("   jpapi search templates list")
                return 1
            
            # Route to appropriate handler based on search type
            if args.search_type in ['computers', 'computer', 'macs', 'macos']:
                return self._handle_computer_search(args)
            elif args.search_type in ['mobile', 'ios', 'ipad', 'iphone', 'devices']:
                return self._handle_mobile_search(args)
            elif args.search_type == 'for':
                return self._handle_quick_search(args)
            elif args.search_type == 'results':
                return self._handle_search_results(args)
            elif args.search_type == 'templates':
                return self._handle_search_templates(args)
            else:
                print(f"❌ Unknown search type: {args.search_type}")
                return 1
                
        except Exception as e:
            return self.handle_api_error(e)
    
    def _handle_conversational_search(self, args: Namespace) -> int:
        """Handle conversational search patterns"""
        target = args.search_target.lower()
        terms = args.search_terms if args.search_terms else []
        
        print(f"🔍 Searching for {target}: {' '.join(terms)}")
        
        # Determine search type from target
        if target in ['computers', 'computer', 'macs', 'macos', 'mac']:
            return self._search_computers_conversational(terms, args)
        elif target in ['mobile', 'ios', 'ipad', 'iphone', 'devices', 'device']:
            return self._search_mobile_conversational(terms, args)
        else:
            # Try to infer from terms
            combined_text = f"{target} {' '.join(terms)}".lower()
            if any(word in combined_text for word in ['ipad', 'iphone', 'ios', 'mobile']):
                return self._search_mobile_conversational([target] + terms, args)
            elif any(word in combined_text for word in ['mac', 'computer', 'laptop', 'imac']):
                return self._search_computers_conversational([target] + terms, args)
            else:
                print(f"❌ Could not determine search target from: {target}")
                print("   Try: jpapi search computers <terms> or jpapi search mobile <terms>")
                return 1
    
    def _search_computers_conversational(self, terms: List[str], args: Namespace) -> int:
        """Search computers using conversational terms"""
        # Convert terms to search criteria
        criteria = self._parse_conversational_terms(terms)
        
        # Create mock args for criteria search
        mock_args = Namespace()
        mock_args.name = criteria.get('name')
        mock_args.model = criteria.get('model') 
        mock_args.department = criteria.get('department')
        mock_args.building = criteria.get('building')
        mock_args.managed = criteria.get('managed')
        mock_args.os_version = criteria.get('os_version')
        mock_args.format = getattr(args, 'format', 'table')
        mock_args.output = getattr(args, 'output', None)
        
        return self._search_computers_by_criteria(mock_args)
    
    def _search_mobile_conversational(self, terms: List[str], args: Namespace) -> int:
        """Search mobile devices using conversational terms"""
        # Convert terms to search criteria
        criteria = self._parse_conversational_terms(terms)
        
        # Create mock args for criteria search
        mock_args = Namespace()
        mock_args.name = criteria.get('name')
        mock_args.model = criteria.get('model')
        mock_args.supervised = criteria.get('supervised')
        mock_args.managed = criteria.get('managed')
        mock_args.carrier = criteria.get('carrier')
        mock_args.os_version = criteria.get('os_version')
        mock_args.format = getattr(args, 'format', 'table')
        mock_args.output = getattr(args, 'output', None)
        
        return self._search_mobile_by_criteria(mock_args)
    
    def _parse_conversational_terms(self, terms: List[str]) -> Dict[str, str]:
        """Parse conversational terms into search criteria"""
        criteria = {}
        terms_text = ' '.join(terms).lower()
        
        # Look for device models
        if 'macbook' in terms_text:
            criteria['model'] = 'MacBook'
        elif 'imac' in terms_text:
            criteria['model'] = 'iMac'
        elif 'ipad' in terms_text:
            criteria['model'] = 'iPad'
        elif 'iphone' in terms_text:
            criteria['model'] = 'iPhone'
        
        # Look for departments/buildings
        dept_keywords = ['it', 'hr', 'finance', 'marketing', 'sales', 'engineering']
        for dept in dept_keywords:
            if dept in terms_text:
                criteria['department'] = dept.upper()
                break
        
        # Look for management status
        if 'managed' in terms_text:
            criteria['managed'] = 'true'
        elif 'unmanaged' in terms_text:
            criteria['managed'] = 'false'
        
        # Look for supervision status (mobile)
        if 'supervised' in terms_text:
            criteria['supervised'] = 'true'
        elif 'unsupervised' in terms_text:
            criteria['supervised'] = 'false'
        
        # Look for specific names (anything not matching keywords)
        name_terms = []
        skip_words = ['in', 'with', 'for', 'the', 'and', 'or', 'managed', 'supervised', 'devices', 'computers']
        for term in terms:
            if term.lower() not in skip_words and term.lower() not in dept_keywords:
                if not any(model in term.lower() for model in ['macbook', 'imac', 'ipad', 'iphone']):
                    name_terms.append(term)
        
        if name_terms:
            criteria['name'] = '*' + '*'.join(name_terms) + '*'
        
        return criteria
    
    def _handle_quick_search(self, args: Namespace) -> int:
        """Handle 'search for' quick search"""
        search_phrase = ' '.join(args.search_phrase)
        print(f"🔍 Quick search for: {search_phrase}")
        
        # Parse the phrase and route appropriately
        phrase_lower = search_phrase.lower()
        
        if any(word in phrase_lower for word in ['ipad', 'iphone', 'ios', 'mobile']):
            return self._search_mobile_conversational(args.search_phrase, args)
        else:
            # Default to computer search
            return self._search_computers_conversational(args.search_phrase, args)
    
    def _handle_computer_search(self, args: Namespace) -> int:
        """Handle computer search operations"""
        if not hasattr(args, 'computer_search_action') or not args.computer_search_action:
            print("❌ Please specify computer search action")
            print("Available: criteria, query")
            return 1
        
        if args.computer_search_action == 'criteria':
            return self._search_computers_by_criteria(args)
        elif args.computer_search_action == 'query':
            return self._search_computers_by_query(args)
        else:
            print(f"❌ Unknown computer search action: {args.computer_search_action}")
            return 1
    
    def _search_computers_by_criteria(self, args: Namespace) -> int:
        """Search computers using criteria filters"""
        try:
            print("🔍 Searching Computers by Criteria...")
            
            # Get all computers first
            response = self.auth.api_request('GET', '/JSSResource/computers')
            
            if 'computers' not in response or 'computer' not in response['computers']:
                print("❌ No computers found")
                return 1
            
            computers = response['computers']['computer']
            filtered_computers = []
            
            # Apply filters
            for computer in computers:
                if self._matches_computer_criteria(computer, args):
                    # Get detailed info if we have specific criteria
                    if any([args.department, args.building, args.managed]):
                        try:
                            detail_response = self.auth.api_request('GET', f'/JSSResource/computers/id/{computer["id"]}')
                            if 'computer' in detail_response:
                                computer_detail = detail_response['computer']
                                if self._matches_detailed_computer_criteria(computer_detail, args):
                                    filtered_computers.append(self._format_computer_result(computer_detail, detailed=True))
                        except Exception:
                            # Fall back to basic info if detailed fetch fails
                            filtered_computers.append(self._format_computer_result(computer, detailed=False))
                    else:
                        filtered_computers.append(self._format_computer_result(computer, detailed=False))
            
            if not filtered_computers:
                print("❌ No computers match the specified criteria")
                return 1
            
            # Output results
            output = self.format_output(filtered_computers, args.format)
            self.save_output(output, args.output)
            
            print(f"\n✅ Found {len(filtered_computers)} computers matching criteria")
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _search_computers_by_query(self, args: Namespace) -> int:
        """Search computers using query syntax"""
        try:
            print(f"🔍 Searching Computers with Query: {args.query_string}")
            
            # Parse query string
            criteria = self._parse_query_string(args.query_string)
            
            # Convert to criteria format and search
            mock_args = Namespace()
            for key, value in criteria.items():
                setattr(mock_args, key.replace('-', '_'), value)
            
            # Copy format and output settings
            mock_args.format = args.format
            mock_args.output = args.output
            
            return self._search_computers_by_criteria(mock_args)
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _handle_mobile_search(self, args: Namespace) -> int:
        """Handle mobile device search operations"""
        if not hasattr(args, 'mobile_search_action') or not args.mobile_search_action:
            print("❌ Please specify mobile search action")
            print("Available: criteria, query")
            return 1
        
        if args.mobile_search_action == 'criteria':
            return self._search_mobile_by_criteria(args)
        elif args.mobile_search_action == 'query':
            return self._search_mobile_by_query(args)
        else:
            print(f"❌ Unknown mobile search action: {args.mobile_search_action}")
            return 1
    
    def _search_mobile_by_criteria(self, args: Namespace) -> int:
        """Search mobile devices using criteria filters"""
        try:
            print("🔍 Searching Mobile Devices by Criteria...")
            
            # Get all mobile devices first
            response = self.auth.api_request('GET', '/JSSResource/mobiledevices')
            
            if 'mobile_devices' not in response or 'mobile_device' not in response['mobile_devices']:
                print("❌ No mobile devices found")
                return 1
            
            devices = response['mobile_devices']['mobile_device']
            filtered_devices = []
            
            # Apply filters
            for device in devices:
                if self._matches_mobile_criteria(device, args):
                    # Get detailed info if we have specific criteria
                    if any([args.supervised, args.managed, args.carrier]):
                        try:
                            detail_response = self.auth.api_request('GET', f'/JSSResource/mobiledevices/id/{device["id"]}')
                            if 'mobile_device' in detail_response:
                                device_detail = detail_response['mobile_device']
                                if self._matches_detailed_mobile_criteria(device_detail, args):
                                    filtered_devices.append(self._format_mobile_result(device_detail, detailed=True))
                        except Exception:
                            # Fall back to basic info if detailed fetch fails
                            filtered_devices.append(self._format_mobile_result(device, detailed=False))
                    else:
                        filtered_devices.append(self._format_mobile_result(device, detailed=False))
            
            if not filtered_devices:
                print("❌ No mobile devices match the specified criteria")
                return 1
            
            # Output results
            output = self.format_output(filtered_devices, args.format)
            self.save_output(output, args.output)
            
            print(f"\n✅ Found {len(filtered_devices)} mobile devices matching criteria")
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _search_mobile_by_query(self, args: Namespace) -> int:
        """Search mobile devices using query syntax"""
        try:
            print(f"🔍 Searching Mobile Devices with Query: {args.query_string}")
            
            # Parse query string
            criteria = self._parse_query_string(args.query_string)
            
            # Convert to criteria format and search
            mock_args = Namespace()
            for key, value in criteria.items():
                setattr(mock_args, key.replace('-', '_'), value)
            
            # Copy format and output settings
            mock_args.format = args.format
            mock_args.output = args.output
            
            return self._search_mobile_by_criteria(mock_args)
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _handle_search_results(self, args: Namespace) -> int:
        """Handle search results management"""
        if not hasattr(args, 'results_action') or not args.results_action:
            print("❌ Please specify results action")
            print("Available: list, export")
            return 1
        
        if args.results_action == 'list':
            print("📋 Saved Search Results:")
            print("   (Search result persistence not yet implemented)")
            print("   This would show previously saved search results")
            return 0
        elif args.results_action == 'export':
            print(f"📤 Exporting Search Results: {args.search_id}")
            print("   (Search result export not yet implemented)")
            print("   This would export a previously saved search result")
            return 0
        else:
            print(f"❌ Unknown results action: {args.results_action}")
            return 1
    
    def _handle_search_templates(self, args: Namespace) -> int:
        """Handle search templates management"""
        if not hasattr(args, 'templates_action') or not args.templates_action:
            print("❌ Please specify templates action")
            print("Available: list, save")
            return 1
        
        if args.templates_action == 'list':
            print("📋 Search Templates:")
            print("   (Search templates not yet implemented)")
            print("   This would show saved search templates")
            return 0
        elif args.templates_action == 'save':
            print(f"💾 Saving Search Template: {args.name}")
            print(f"   Type: {args.search_type}")
            if args.query:
                print(f"   Query: {args.query}")
            print("   (Template saving not yet implemented)")
            return 0
        else:
            print(f"❌ Unknown templates action: {args.templates_action}")
            return 1
    
    def _matches_computer_criteria(self, computer: Dict[str, Any], args: Namespace) -> bool:
        """Check if computer matches basic criteria"""
        if args.name and not self._matches_pattern(computer.get('name', ''), args.name):
            return False
        if args.model and args.model.lower() not in computer.get('model', '').lower():
            return False
        if args.os_version and not self._matches_version(computer.get('os_version', ''), args.os_version):
            return False
        return True
    
    def _matches_detailed_computer_criteria(self, computer_detail: Dict[str, Any], args: Namespace) -> bool:
        """Check if computer matches detailed criteria"""
        general = computer_detail.get('general', {})
        
        if args.department and args.department.lower() not in general.get('department', '').lower():
            return False
        if args.building and args.building.lower() not in general.get('building', '').lower():
            return False
        if args.managed:
            managed_status = general.get('remote_management', {}).get('managed', False)
            if args.managed == 'true' and not managed_status:
                return False
            if args.managed == 'false' and managed_status:
                return False
        return True
    
    def _matches_mobile_criteria(self, device: Dict[str, Any], args: Namespace) -> bool:
        """Check if mobile device matches basic criteria"""
        if args.name and not self._matches_pattern(device.get('name', ''), args.name):
            return False
        if args.model and args.model.lower() not in device.get('model', '').lower():
            return False
        if args.os_version and not self._matches_version(device.get('os_version', ''), args.os_version):
            return False
        return True
    
    def _matches_detailed_mobile_criteria(self, device_detail: Dict[str, Any], args: Namespace) -> bool:
        """Check if mobile device matches detailed criteria"""
        general = device_detail.get('general', {})
        
        if args.supervised:
            supervised_status = general.get('supervised', False)
            if args.supervised == 'true' and not supervised_status:
                return False
            if args.supervised == 'false' and supervised_status:
                return False
        if args.managed:
            managed_status = general.get('managed', False)
            if args.managed == 'true' and not managed_status:
                return False
            if args.managed == 'false' and managed_status:
                return False
        if args.carrier and args.carrier.lower() not in general.get('carrier_settings_version', '').lower():
            return False
        return True
    
    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches pattern (supports wildcards)"""
        if '*' in pattern:
            # Convert wildcard pattern to regex
            regex_pattern = pattern.replace('*', '.*')
            return bool(re.match(regex_pattern, value, re.IGNORECASE))
        else:
            return pattern.lower() in value.lower()
    
    def _matches_version(self, value: str, criteria: str) -> bool:
        """Check if version matches criteria (supports >=, <=, =)"""
        if criteria.startswith('>='):
            return value >= criteria[2:]
        elif criteria.startswith('<='):
            return value <= criteria[2:]
        elif criteria.startswith('='):
            return value == criteria[1:]
        else:
            return criteria in value
    
    def _parse_query_string(self, query: str) -> Dict[str, str]:
        """Parse query string into criteria dictionary"""
        criteria = {}
        
        # Simple parser for "key:value AND key:value" format
        parts = query.split(' AND ')
        for part in parts:
            part = part.strip()
            if ':' in part:
                key, value = part.split(':', 1)
                criteria[key.strip()] = value.strip()
        
        return criteria
    
    def _format_computer_result(self, computer: Dict[str, Any], detailed: bool = False) -> Dict[str, Any]:
        """Format computer search result"""
        result = {
            'ID': computer.get('id', ''),
            'Name': computer.get('name', ''),
            'Model': computer.get('model', ''),
            'Serial': computer.get('serial_number', ''),
            'OS Version': computer.get('os_version', '')
        }
        
        if detailed and 'general' in computer:
            general = computer['general']
            result.update({
                'Department': general.get('department', ''),
                'Building': general.get('building', ''),
                'Managed': general.get('remote_management', {}).get('managed', False),
                'Last Contact': general.get('last_contact_time', '')
            })
        
        return result
    
    def _format_mobile_result(self, device: Dict[str, Any], detailed: bool = False) -> Dict[str, Any]:
        """Format mobile device search result"""
        result = {
            'ID': device.get('id', ''),
            'Name': device.get('name', ''),
            'Model': device.get('model', ''),
            'Serial': device.get('serial_number', ''),
            'OS Version': device.get('os_version', '')
        }
        
        if detailed and 'general' in device:
            general = device['general']
            result.update({
                'Supervised': general.get('supervised', False),
                'Managed': general.get('managed', False),
                'Carrier': general.get('carrier_settings_version', ''),
                'Last Inventory': general.get('last_inventory_update', '')
            })
        
        return result
