#!/usr/bin/env python3
"""
API Integration Tests for Groups Functionality
Tests real API interactions with JAMF Pro
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cli.commands.list_command import ListCommand
from src.cli.commands.export_command import ExportCommand
from src.cli.commands.create_command import CreateCommand
from src.lib.managers.computer_manager import ComputerManager


class TestGroupsAPIIntegration(unittest.TestCase):
    """Integration tests with real JAMF Pro API"""

    def setUp(self):
        """Set up integration test environment"""
        # These tests require a real JAMF Pro instance
        # Skip if no credentials are available
        try:
            from src.core.auth.login_manager import LoginManager

            self.auth = LoginManager()
            # Test if we can authenticate
            self.auth.get_token()
        except Exception:
            self.skipTest("No JAMF Pro credentials available for integration testing")

    def test_real_computer_groups_listing(self):
        """Test real computer groups listing"""
        list_command = ListCommand()
        list_command.auth = self.auth

        args = Mock()
        args.format = "table"
        args.filter = None

        result = list_command._list_objects("computer-groups", args)

        # Should succeed
        self.assertEqual(result, 0)

    def test_real_computer_groups_export(self):
        """Test real computer groups export"""
        export_command = ExportCommand()
        export_command.auth = self.auth

        args = Mock()
        args.format = "csv"
        args.output = None

        result = export_command._export_objects("computer-groups", args)

        # Should succeed
        self.assertEqual(result, 0)

    def test_real_group_creation(self):
        """Test real group creation"""
        create_command = CreateCommand()
        create_command.auth = self.auth

        args = Mock()
        args.name = "API Test Group"
        args.type = "computer"
        args.smart = False
        args.criteria = None

        result = create_command._create_group(args)

        # Should succeed
        self.assertEqual(result, 0)

    def test_real_smart_group_creation(self):
        """Test real smart group creation"""
        create_command = CreateCommand()
        create_command.auth = self.auth

        args = Mock()
        args.name = "API Smart Test Group"
        args.type = "computer"
        args.smart = True
        args.criteria = (
            '[{"name": "Computer Name", "operator": "is", "value": "TestMac"}]'
        )

        result = create_command._create_group(args)

        # Should succeed
        self.assertEqual(result, 0)

    def test_real_computer_manager(self):
        """Test real ComputerManager functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ComputerManager(self.auth, Path(temp_dir))

            # Test getting computer groups
            groups = manager.get_all_computer_groups(use_cache=False)

            # Should return groups
            self.assertIsInstance(groups, list)

    def test_real_advanced_searches(self):
        """Test real advanced searches listing"""
        list_command = ListCommand()
        list_command.auth = self.auth

        args = Mock()
        args.format = "table"
        args.filter = None

        result = list_command._list_objects("computer-advanced-searches", args)

        # Should succeed
        self.assertEqual(result, 0)


class TestGroupsPerformance(unittest.TestCase):
    """Performance tests for groups functionality"""

    def setUp(self):
        """Set up performance test environment"""
        try:
            from src.core.auth.login_manager import LoginManager

            self.auth = LoginManager()
            self.auth.get_token()
        except Exception:
            self.skipTest("No JAMF Pro credentials available for performance testing")

    def test_groups_listing_performance(self):
        """Test performance of groups listing"""
        import time

        list_command = ListCommand()
        list_command.auth = self.auth

        args = Mock()
        args.format = "table"
        args.filter = None

        start_time = time.time()
        result = list_command._list_objects("computer-groups", args)
        end_time = time.time()

        # Should succeed and complete within reasonable time
        self.assertEqual(result, 0)
        self.assertLess(end_time - start_time, 10)  # Should complete within 10 seconds

    def test_groups_export_performance(self):
        """Test performance of groups export"""
        import time

        export_command = ExportCommand()
        export_command.auth = self.auth

        args = Mock()
        args.format = "csv"
        args.output = None

        start_time = time.time()
        result = export_command._export_objects("computer-groups", args)
        end_time = time.time()

        # Should succeed and complete within reasonable time
        self.assertEqual(result, 0)
        self.assertLess(end_time - start_time, 15)  # Should complete within 15 seconds

    def test_groups_caching_performance(self):
        """Test performance of groups caching"""
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ComputerManager(self.auth, Path(temp_dir))

            # First call (no cache)
            start_time = time.time()
            groups1 = manager.get_all_computer_groups(use_cache=False)
            first_call_time = time.time() - start_time

            # Second call (with cache)
            start_time = time.time()
            groups2 = manager.get_all_computer_groups(use_cache=True)
            second_call_time = time.time() - start_time

            # Cached call should be faster
            self.assertLess(second_call_time, first_call_time)
            self.assertEqual(len(groups1), len(groups2))


if __name__ == "__main__":
    unittest.main()
