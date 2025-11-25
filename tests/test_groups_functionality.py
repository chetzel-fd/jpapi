#!/usr/bin/env python3
"""
Comprehensive Test Suite for jpapi Groups Functionality
Tests all aspects of computer groups, user groups, and advanced searches
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cli.commands.list_command import ListCommand
from src.cli.commands.export_command import ExportCommand
from src.cli.commands.create_command import CreateCommand
from src.cli.commands.user_groups_command import UserGroupsCommand
from src.lib.managers.computer_manager import ComputerManager
from src.lib.managers.mobile_device_manager import MobileDeviceManager


class TestGroupsFunctionality(unittest.TestCase):
    """Test suite for groups functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_auth = Mock()
        self.mock_auth.api_request.return_value = {
            "computer_groups": [
                {"id": "1", "name": "Test Group 1", "is_smart": False},
                {"id": "2", "name": "Smart Group 1", "is_smart": True},
            ]
        }

        # Mock successful API responses
        self.mock_auth.make_api_call.return_value = {
            "computer_groups": [
                {"id": "1", "name": "Test Group 1", "is_smart": False},
                {"id": "2", "name": "Smart Group 1", "is_smart": True},
            ]
        }

        self.list_command = ListCommand()
        self.export_command = ExportCommand()
        self.create_command = CreateCommand()
        self.user_groups_command = UserGroupsCommand()

        # Set up mock authentication
        self.list_command.auth = self.mock_auth
        self.export_command.auth = self.mock_auth
        self.create_command.auth = self.mock_auth
        self.user_groups_command.auth = self.mock_auth

    def test_computer_groups_listing(self):
        """Test computer groups listing functionality"""
        # Mock the API response
        mock_response = {
            "computer_groups": [
                {"id": "1", "name": "Test Group 1", "is_smart": False},
                {"id": "2", "name": "Smart Group 1", "is_smart": True},
            ]
        }
        self.mock_auth.api_request.return_value = mock_response

        # Test listing computer groups
        args = Mock()
        args.format = "table"
        args.filter = None
        args.filter_type = "wildcard"

        result = self.list_command._list_objects("computer-groups", args)

        # Should succeed
        self.assertEqual(result, 0)

        # Verify API was called correctly
        self.mock_auth.api_request.assert_called_with(
            "GET", "/JSSResource/computergroups"
        )

    def test_computer_groups_export(self):
        """Test computer groups export functionality"""
        # Mock the API response
        mock_response = {
            "computer_groups": [
                {"id": "1", "name": "Test Group 1", "is_smart": False},
                {"id": "2", "name": "Smart Group 1", "is_smart": True},
            ]
        }
        self.mock_auth.api_request.return_value = mock_response

        # Test export
        args = Mock()
        args.format = "csv"
        args.output = None
        args.detailed = False

        result = self.export_command._export_objects("computer-groups", args)

        # Should succeed
        self.assertEqual(result, 0)

    def test_computer_groups_creation(self):
        """Test computer groups creation functionality"""
        # Mock successful creation response
        self.mock_auth.api_request_xml.return_value = {"success": True}

        # Test group creation
        args = Mock()
        args.name = "Test Group"
        args.type = "computer"
        args.smart = False
        args.criteria = None

        result = self.create_command._create_group(args)

        # Should succeed
        self.assertEqual(result, 0)

        # Verify XML API was called
        self.mock_auth.api_request_xml.assert_called_once()

    def test_smart_group_creation(self):
        """Test smart group creation with criteria"""
        # Mock successful creation response
        self.mock_auth.api_request_xml.return_value = {"success": True}

        # Test smart group creation
        args = Mock()
        args.name = "Smart Test Group"
        args.type = "computer"
        args.smart = True
        args.criteria = (
            '[{"name": "Computer Name", "operator": "is", "value": "TestMac"}]'
        )

        result = self.create_command._create_group(args)

        # Should succeed
        self.assertEqual(result, 0)

    def test_user_groups_listing(self):
        """Test user groups listing functionality"""
        # Mock user groups API responses
        self.mock_auth.api_request.side_effect = [
            {
                "user_groups": [
                    {"id": "1", "name": "Smart User Group", "is_smart": True}
                ]
            },
            {
                "user_groups": [
                    {"id": "2", "name": "Static User Group", "is_smart": False}
                ]
            },
        ]

        # Test smart user groups
        args = Mock()
        args.format = "table"
        args.site = None

        result = self.user_groups_command._list_smart_groups(args)

        # Should succeed
        self.assertEqual(result, 0)

    def test_advanced_searches_listing(self):
        """Test advanced searches listing functionality"""
        # Mock advanced searches response
        mock_response = {
            "advanced_computer_searches": [
                {"id": "1", "name": "All Managed Machines", "view_as": "Standard"}
            ]
        }
        self.mock_auth.api_request.return_value = mock_response

        # Test advanced searches listing
        args = Mock()
        args.format = "table"
        args.filter = None

        result = self.list_command._list_objects("computer-advanced-searches", args)

        # Should succeed
        self.assertEqual(result, 0)

    def test_computer_manager_functionality(self):
        """Test ComputerManager class functionality"""
        # Create a temporary cache directory
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ComputerManager(self.mock_auth, Path(temp_dir))

            # Test getting computer groups
            groups = manager.get_all_computer_groups(use_cache=False)

            # Should return groups
            self.assertIsInstance(groups, list)
            self.assertGreater(len(groups), 0)

    def test_mobile_device_manager_functionality(self):
        """Test MobileDeviceManager class functionality"""
        # Create a temporary cache directory
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = MobileDeviceManager(self.mock_auth, Path(temp_dir))

            # Mock mobile device groups response
            self.mock_auth.make_api_call.return_value = {
                "mobile_device_groups": [
                    {"id": "1", "name": "Mobile Test Group", "is_smart": False}
                ]
            }

            # Test getting mobile device groups
            groups = manager.get_all_mobile_groups(use_cache=False)

            # Should return groups
            self.assertIsInstance(groups, list)

    def test_group_data_validation(self):
        """Test group data validation and formatting"""
        # Test group data structure
        group_data = {
            "computer_group": {
                "name": "Test Group",
                "is_smart": False,
                "description": "Test Description",
            }
        }

        # Test XML conversion
        xml_data = self.create_command._convert_group_data_to_xml(
            group_data, "computer"
        )

        # Should contain expected XML elements
        self.assertIn("<computer_group>", xml_data)
        self.assertIn("<name>Test Group</name>", xml_data)
        self.assertIn("<is_smart>false</is_smart>", xml_data)

    def test_smart_group_criteria_parsing(self):
        """Test smart group criteria parsing"""
        # Test criteria parsing
        criteria_input = "name:Computer Name,operator:is,value:TestMac"
        criteria = self.create_command._parse_criteria(criteria_input)

        # Should parse correctly
        self.assertIsInstance(criteria, list)
        self.assertGreater(len(criteria), 0)

    def test_export_data_formatting(self):
        """Test export data formatting"""
        # Mock detailed group data
        group_data = {
            "id": "1",
            "name": "Test Group",
            "is_smart": False,
            "description": "Test Description",
            "site": {"name": "Test Site"},
            "computers": [{"name": "TestMac1"}, {"name": "TestMac2"}],
        }

        # Test basic group data formatting
        from src.cli.commands.export.export_groups import ExportComputerGroups

        export_handler = ExportComputerGroups(self.mock_auth)

        basic_data = export_handler._get_basic_group_data(group_data)

        # Should contain expected fields
        self.assertIn("ID", basic_data)
        self.assertIn("Name", basic_data)
        self.assertIn("Smart", basic_data)
        self.assertEqual(basic_data["Name"], "Test Group")

    def test_error_handling(self):
        """Test error handling in groups functionality"""
        # Mock API error
        self.mock_auth.api_request.side_effect = Exception("API Error")

        # Test error handling in listing
        args = Mock()
        args.format = "table"
        args.filter = None

        result = self.list_command._list_objects("computer-groups", args)

        # Should handle error gracefully
        self.assertEqual(result, 1)

    def test_filtering_functionality(self):
        """Test filtering functionality for groups"""
        # Mock groups data
        groups_data = [
            {"id": "1", "name": "Test Group 1", "is_smart": False},
            {"id": "2", "name": "Test Group 2", "is_smart": True},
            {"id": "3", "name": "Other Group", "is_smart": False},
        ]

        # Test name filtering
        from src.lib.utils import create_filter

        filter_obj = create_filter("wildcard")
        filtered = filter_obj.filter_objects(groups_data, "name", "Test*")

        # Should filter correctly
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all("Test" in group["name"] for group in filtered))

    def test_cache_functionality(self):
        """Test caching functionality for groups"""
        # Create a temporary cache directory
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ComputerManager(self.mock_auth, Path(temp_dir))

            # First call should use API
            groups1 = manager.get_all_computer_groups(use_cache=True)

            # Second call should use cache
            groups2 = manager.get_all_computer_groups(use_cache=True)

            # Should return same data
            self.assertEqual(len(groups1), len(groups2))

    def test_group_creation_validation(self):
        """Test group creation input validation"""
        # Test invalid JSON criteria
        args = Mock()
        args.name = "Test Group"
        args.type = "computer"
        args.smart = True
        args.criteria = "invalid json"

        result = self.create_command._create_group(args)

        # Should fail with invalid JSON
        self.assertEqual(result, 1)

    def test_export_file_creation(self):
        """Test export file creation and formatting"""
        # Create temporary directory for export
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock export with specific output path
            args = Mock()
            args.format = "csv"
            args.output = os.path.join(temp_dir, "test_export.csv")
            args.detailed = False

            # Mock API response
            mock_response = {
                "computer_groups": [
                    {"id": "1", "name": "Test Group 1", "is_smart": False}
                ]
            }
            self.mock_auth.api_request.return_value = mock_response

            # Test export
            result = self.export_command._export_objects("computer-groups", args)

            # Should succeed
            self.assertEqual(result, 0)

            # Check if file was created
            self.assertTrue(os.path.exists(args.output))

    def test_group_type_detection(self):
        """Test group type detection functionality"""
        # Test different group types
        smart_group = {"is_smart": True, "criteria": [{"name": "test"}]}
        static_group = {"is_smart": False, "computers": [{"name": "test"}]}

        # Test type detection
        from src.cli.commands.user_groups_command import UserGroupsCommand

        command = UserGroupsCommand()

        smart_type = command._determine_group_type(smart_group)
        static_type = command._determine_group_type(static_group)

        # Should detect types correctly
        self.assertIn("Smart", smart_type)
        self.assertIn("Static", static_type)


class TestGroupsIntegration(unittest.TestCase):
    """Integration tests for groups functionality"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.mock_auth = Mock()

    def test_end_to_end_group_workflow(self):
        """Test complete group workflow: create, list, export, delete"""
        # This would be an integration test that requires a real JAMF instance
        # For now, we'll test the workflow components

        # 1. Create group
        create_command = CreateCommand()
        create_command.auth = self.mock_auth
        self.mock_auth.api_request_xml.return_value = {"success": True}

        args = Mock()
        args.name = "Integration Test Group"
        args.type = "computer"
        args.smart = False
        args.criteria = None

        create_result = create_command._create_group(args)
        self.assertEqual(create_result, 0)

        # 2. List groups
        list_command = ListCommand()
        list_command.auth = self.mock_auth
        self.mock_auth.api_request.return_value = {
            "computer_groups": [
                {"id": "1", "name": "Integration Test Group", "is_smart": False}
            ]
        }

        list_args = Mock()
        list_args.format = "table"
        list_args.filter = None

        list_result = list_command._list_objects("computer-groups", list_args)
        self.assertEqual(list_result, 0)

        # 3. Export groups
        export_command = ExportCommand()
        export_command.auth = self.mock_auth

        export_args = Mock()
        export_args.format = "csv"
        export_args.output = None

        export_result = export_command._export_objects("computer-groups", export_args)
        self.assertEqual(export_result, 0)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestGroupsFunctionality))
    test_suite.addTest(unittest.makeSuite(TestGroupsIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )
    print(f"{'='*50}")
