#!/usr/bin/env python3
"""
Test Configuration for Groups Functionality
Provides test data, fixtures, and configuration for groups testing
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock


class GroupsTestConfig:
    """Configuration and test data for groups functionality testing"""

    # Sample computer groups data
    SAMPLE_COMPUTER_GROUPS = [
        {
            "id": "1",
            "name": "All Managed Clients",
            "is_smart": False,
            "description": "All managed computers",
            "site": {"id": "1", "name": "Default Site"},
            "computers": [
                {"id": "1", "name": "MacBook-Pro-1"},
                {"id": "2", "name": "MacBook-Pro-2"},
            ],
        },
        {
            "id": "2",
            "name": "Smart Group - macOS 13+",
            "is_smart": True,
            "description": "Computers running macOS 13 or later",
            "site": {"id": "1", "name": "Default Site"},
            "criteria": [
                {
                    "name": "Operating System Version",
                    "operator": "greater than or equal",
                    "value": "13.0",
                }
            ],
        },
        {
            "id": "3",
            "name": "Test Group",
            "is_smart": False,
            "description": "Test group for automation",
            "site": {"id": "1", "name": "Default Site"},
            "computers": [],
        },
    ]

    # Sample user groups data
    SAMPLE_USER_GROUPS = [
        {
            "id": "1",
            "name": "All Users",
            "is_smart": False,
            "description": "All users in the system",
            "site": {"id": "1", "name": "Default Site"},
            "users": [
                {"id": "1", "username": "admin"},
                {"id": "2", "username": "user1"},
            ],
        },
        {
            "id": "2",
            "name": "Smart User Group",
            "is_smart": True,
            "description": "Users with specific criteria",
            "site": {"id": "1", "name": "Default Site"},
            "criteria": [{"name": "Department", "operator": "is", "value": "IT"}],
        },
    ]

    # Sample advanced searches data
    SAMPLE_ADVANCED_SEARCHES = [
        {
            "id": "1",
            "name": "All Managed Machines",
            "view_as": "Standard",
            "sort_1": "Computer Name",
            "sort_2": "",
            "sort_3": "",
            "site": {"id": "1", "name": "Default Site"},
            "criteria": [
                {
                    "name": "Computer Name",
                    "search_type": "is",
                    "value": "*",
                    "and_or": "AND",
                }
            ],
            "display_fields": [
                {"name": "Computer Name"},
                {"name": "Last Contact"},
                {"name": "Operating System Version"},
            ],
            "computers": [
                {"id": "1", "name": "MacBook-Pro-1"},
                {"id": "2", "name": "MacBook-Pro-2"},
            ],
        }
    ]

    # API response templates
    COMPUTER_GROUPS_RESPONSE = {
        "computer_groups": {"computer_group": SAMPLE_COMPUTER_GROUPS}
    }

    USER_GROUPS_RESPONSE = {"user_groups": {"user_group": SAMPLE_USER_GROUPS}}

    ADVANCED_SEARCHES_RESPONSE = {
        "advanced_computer_searches": {
            "advanced_computer_search": SAMPLE_ADVANCED_SEARCHES
        }
    }

    # Test criteria examples
    SAMPLE_CRITERIA = [
        {"name": "Computer Name", "operator": "is", "value": "TestMac"},
        {
            "name": "Operating System Version",
            "operator": "greater than or equal",
            "value": "13.0",
        },
        {"name": "Last Contact", "operator": "less than", "value": "7 days"},
    ]

    # XML templates for group creation
    COMPUTER_GROUP_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<computer_group>
    <name>{name}</name>
    <is_smart>{is_smart}</is_smart>
    <description>{description}</description>
    <site>
        <id>{site_id}</id>
        <name>{site_name}</name>
    </site>
    {criteria_section}
</computer_group>"""

    MOBILE_DEVICE_GROUP_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<mobile_device_group>
    <name>{name}</name>
    <is_smart>{is_smart}</is_smart>
    <description>{description}</description>
    <site>
        <id>{site_id}</id>
        <name>{site_name}</name>
    </site>
    {criteria_section}
</mobile_device_group>"""

    @classmethod
    def create_mock_auth(cls, response_type: str = "computer_groups") -> Mock:
        """Create a mock authentication object with sample data"""
        mock_auth = Mock()

        if response_type == "computer_groups":
            mock_auth.api_request.return_value = cls.COMPUTER_GROUPS_RESPONSE
            mock_auth.make_api_call.return_value = cls.COMPUTER_GROUPS_RESPONSE
        elif response_type == "user_groups":
            mock_auth.api_request.return_value = cls.USER_GROUPS_RESPONSE
        elif response_type == "advanced_searches":
            mock_auth.api_request.return_value = cls.ADVANCED_SEARCHES_RESPONSE
        else:
            mock_auth.api_request.return_value = {}
            mock_auth.make_api_call.return_value = {}

        # Mock successful XML API calls
        mock_auth.api_request_xml.return_value = {"success": True}

        return mock_auth

    @classmethod
    def create_test_args(cls, **kwargs) -> Mock:
        """Create mock arguments for testing"""
        args = Mock()

        # Default values
        args.format = kwargs.get("format", "table")
        args.output = kwargs.get("output", None)
        args.filter = kwargs.get("filter", None)
        args.filter_type = kwargs.get("filter_type", "wildcard")
        args.detailed = kwargs.get("detailed", False)
        args.name = kwargs.get("name", "Test Group")
        args.type = kwargs.get("type", "computer")
        args.smart = kwargs.get("smart", False)
        args.criteria = kwargs.get("criteria", None)
        args.site = kwargs.get("site", None)

        return args

    @classmethod
    def create_temp_cache_dir(cls) -> Path:
        """Create a temporary cache directory for testing"""
        return Path(tempfile.mkdtemp(prefix="jpapi_test_cache_"))

    @classmethod
    def create_sample_export_file(cls, format_type: str = "csv") -> Path:
        """Create a sample export file for testing"""
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=f".{format_type}", delete=False
        )

        if format_type == "csv":
            temp_file.write("ID,Name,Smart,Description,Site,Member Count\n")
            temp_file.write("1,Test Group 1,false,Test Description,Default Site,2\n")
            temp_file.write("2,Smart Group 1,true,Smart Description,Default Site,0\n")
        elif format_type == "json":
            sample_data = {
                "groups": [
                    {"id": "1", "name": "Test Group 1", "smart": False},
                    {"id": "2", "name": "Smart Group 1", "smart": True},
                ]
            }
            json.dump(sample_data, temp_file)

        temp_file.close()
        return Path(temp_file.name)

    @classmethod
    def get_expected_export_columns(cls) -> List[str]:
        """Get expected columns for export files"""
        return [
            "ID",
            "Name",
            "Smart",
            "Description",
            "Site",
            "Member Count",
            "Criteria Count",
            "Computers",
            "Criteria",
        ]

    @classmethod
    def get_test_scenarios(cls) -> List[Dict[str, Any]]:
        """Get test scenarios for comprehensive testing"""
        return [
            {
                "name": "Basic Computer Group Creation",
                "type": "computer",
                "smart": False,
                "criteria": None,
                "expected_result": 0,
            },
            {
                "name": "Smart Computer Group Creation",
                "type": "computer",
                "smart": True,
                "criteria": '[{"name": "Computer Name", "operator": "is", "value": "TestMac"}]',
                "expected_result": 0,
            },
            {
                "name": "Mobile Device Group Creation",
                "type": "mobile",
                "smart": False,
                "criteria": None,
                "expected_result": 0,
            },
            {
                "name": "Invalid JSON Criteria",
                "type": "computer",
                "smart": True,
                "criteria": "invalid json",
                "expected_result": 1,
            },
        ]


class GroupsTestFixtures:
    """Test fixtures for groups functionality"""

    @staticmethod
    def create_computer_group_fixture(
        group_id: str = "1", name: str = "Test Group"
    ) -> Dict[str, Any]:
        """Create a computer group fixture"""
        return {
            "id": group_id,
            "name": name,
            "is_smart": False,
            "description": f"Test group {group_id}",
            "site": {"id": "1", "name": "Default Site"},
            "computers": [],
        }

    @staticmethod
    def create_smart_group_fixture(
        group_id: str = "2", name: str = "Smart Test Group"
    ) -> Dict[str, Any]:
        """Create a smart group fixture"""
        return {
            "id": group_id,
            "name": name,
            "is_smart": True,
            "description": f"Smart test group {group_id}",
            "site": {"id": "1", "name": "Default Site"},
            "criteria": [
                {"name": "Computer Name", "operator": "is", "value": "TestMac"}
            ],
        }

    @staticmethod
    def create_user_group_fixture(
        group_id: str = "1", name: str = "Test User Group"
    ) -> Dict[str, Any]:
        """Create a user group fixture"""
        return {
            "id": group_id,
            "name": name,
            "is_smart": False,
            "description": f"Test user group {group_id}",
            "site": {"id": "1", "name": "Default Site"},
            "users": [],
        }

    @staticmethod
    def create_advanced_search_fixture(
        search_id: str = "1", name: str = "Test Search"
    ) -> Dict[str, Any]:
        """Create an advanced search fixture"""
        return {
            "id": search_id,
            "name": name,
            "view_as": "Standard",
            "sort_1": "Computer Name",
            "sort_2": "",
            "sort_3": "",
            "site": {"id": "1", "name": "Default Site"},
            "criteria": [
                {
                    "name": "Computer Name",
                    "search_type": "is",
                    "value": "*",
                    "and_or": "AND",
                }
            ],
            "display_fields": [{"name": "Computer Name"}, {"name": "Last Contact"}],
            "computers": [],
        }


# Test data validation helpers
class GroupsTestValidators:
    """Validation helpers for groups testing"""

    @staticmethod
    def validate_group_structure(group: Dict[str, Any]) -> bool:
        """Validate that a group has the required structure"""
        required_fields = ["id", "name", "is_smart"]
        return all(field in group for field in required_fields)

    @staticmethod
    def validate_smart_group_criteria(criteria: List[Dict[str, Any]]) -> bool:
        """Validate smart group criteria structure"""
        if not criteria:
            return False

        for criterion in criteria:
            required_fields = ["name", "operator", "value"]
            if not all(field in criterion for field in required_fields):
                return False

        return True

    @staticmethod
    def validate_export_data(export_data: List[Dict[str, Any]]) -> bool:
        """Validate export data structure"""
        if not export_data:
            return False

        required_columns = ["ID", "Name", "Smart"]
        for row in export_data:
            if not all(col in row for col in required_columns):
                return False

        return True

    @staticmethod
    def validate_xml_structure(xml_data: str, group_type: str) -> bool:
        """Validate XML structure for group creation"""
        if group_type == "computer":
            return "<computer_group>" in xml_data and "<name>" in xml_data
        elif group_type == "mobile":
            return "<mobile_device_group>" in xml_data and "<name>" in xml_data
        return False
