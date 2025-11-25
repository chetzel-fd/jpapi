#!/usr/bin/env python3
"""
Comprehensive Test Runner for Groups Functionality
Runs all groups-related tests with detailed reporting
"""

import unittest
import sys
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test_groups_functionality import TestGroupsFunctionality, TestGroupsIntegration
from test_groups_api_integration import TestGroupsAPIIntegration, TestGroupsPerformance
from test_groups_config import (
    GroupsTestConfig,
    GroupsTestFixtures,
    GroupsTestValidators,
)


class GroupsTestRunner:
    """Comprehensive test runner for groups functionality"""

    def __init__(self, verbose: bool = False, integration: bool = False):
        self.verbose = verbose
        self.integration = integration
        self.results = {}

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests for groups functionality"""
        print("🧪 Running Unit Tests for Groups Functionality...")
        print("=" * 60)

        # Create test suite
        test_suite = unittest.TestSuite()

        # Add unit test classes
        test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(TestGroupsFunctionality)
        )

        # Run tests
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(test_suite)

        # Store results
        self.results["unit_tests"] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success_rate": (
                (
                    (result.testsRun - len(result.failures) - len(result.errors))
                    / result.testsRun
                    * 100
                )
                if result.testsRun > 0
                else 0
            ),
        }

        return self.results["unit_tests"]

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for groups functionality"""
        if not self.integration:
            print("⏭️  Skipping integration tests (use --integration flag to enable)")
            return {"skipped": True}

        print("🔗 Running Integration Tests for Groups Functionality...")
        print("=" * 60)

        # Create test suite
        test_suite = unittest.TestSuite()

        # Add integration test classes
        test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(TestGroupsIntegration)
        )
        test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(TestGroupsAPIIntegration)
        )
        test_suite.addTest(
            unittest.TestLoader().loadTestsFromTestCase(TestGroupsPerformance)
        )

        # Run tests
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(test_suite)

        # Store results
        self.results["integration_tests"] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success_rate": (
                (
                    (result.testsRun - len(result.failures) - len(result.errors))
                    / result.testsRun
                    * 100
                )
                if result.testsRun > 0
                else 0
            ),
        }

        return self.results["integration_tests"]

    def run_functionality_tests(self) -> Dict[str, Any]:
        """Run specific functionality tests"""
        print("⚙️  Running Functionality Tests...")
        print("=" * 60)

        functionality_results = {}

        # Test 1: Groups Listing
        print("📋 Testing Groups Listing...")
        try:
            from src.cli.commands.list_command import ListCommand

            list_command = ListCommand()
            list_command.auth = GroupsTestConfig.create_mock_auth()

            args = GroupsTestConfig.create_test_args()
            result = list_command._list_objects("computer-groups", args)
            functionality_results["groups_listing"] = result == 0
        except Exception as e:
            functionality_results["groups_listing"] = False
            print(f"❌ Groups listing test failed: {e}")

        # Test 2: Groups Export
        print("📤 Testing Groups Export...")
        try:
            from src.cli.commands.export_command import ExportCommand

            export_command = ExportCommand()
            export_command.auth = GroupsTestConfig.create_mock_auth()

            args = GroupsTestConfig.create_test_args(format="csv")
            result = export_command._export_objects("computer-groups", args)
            functionality_results["groups_export"] = result == 0
        except Exception as e:
            functionality_results["groups_export"] = False
            print(f"❌ Groups export test failed: {e}")

        # Test 3: Group Creation
        print("➕ Testing Group Creation...")
        try:
            from src.cli.commands.create_command import CreateCommand

            create_command = CreateCommand()
            create_command.auth = GroupsTestConfig.create_mock_auth()

            args = GroupsTestConfig.create_test_args(
                name="Test Group", type="computer", smart=False
            )
            result = create_command._create_group(args)
            functionality_results["group_creation"] = result == 0
        except Exception as e:
            functionality_results["group_creation"] = False
            print(f"❌ Group creation test failed: {e}")

        # Test 4: Smart Group Creation
        print("🧠 Testing Smart Group Creation...")
        try:
            from src.cli.commands.create_command import CreateCommand

            create_command = CreateCommand()
            create_command.auth = GroupsTestConfig.create_mock_auth()

            args = GroupsTestConfig.create_test_args(
                name="Smart Test Group",
                type="computer",
                smart=True,
                criteria='[{"name": "Computer Name", "operator": "is", "value": "TestMac"}]',
            )
            result = create_command._create_group(args)
            functionality_results["smart_group_creation"] = result == 0
        except Exception as e:
            functionality_results["smart_group_creation"] = False
            print(f"❌ Smart group creation test failed: {e}")

        # Test 5: Data Validation
        print("✅ Testing Data Validation...")
        try:
            # Test group structure validation
            test_group = GroupsTestFixtures.create_computer_group_fixture()
            structure_valid = GroupsTestValidators.validate_group_structure(test_group)

            # Test smart group criteria validation
            test_criteria = GroupsTestConfig.SAMPLE_CRITERIA
            criteria_valid = GroupsTestValidators.validate_smart_group_criteria(
                test_criteria
            )

            # Test XML structure validation
            from src.cli.commands.create_command import CreateCommand

            create_command = CreateCommand()
            group_data = {"computer_group": {"name": "Test", "is_smart": False}}
            xml_data = create_command._convert_group_data_to_xml(group_data, "computer")
            xml_valid = GroupsTestValidators.validate_xml_structure(
                xml_data, "computer"
            )

            functionality_results["data_validation"] = (
                structure_valid and criteria_valid and xml_valid
            )
        except Exception as e:
            functionality_results["data_validation"] = False
            print(f"❌ Data validation test failed: {e}")

        # Store results
        self.results["functionality_tests"] = functionality_results

        return functionality_results

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        print("=" * 60)

        performance_results = {}

        # Test 1: Groups Listing Performance
        print("📋 Testing Groups Listing Performance...")
        try:
            start_time = time.time()

            from src.cli.commands.list_command import ListCommand

            list_command = ListCommand()
            list_command.auth = GroupsTestConfig.create_mock_auth()

            args = GroupsTestConfig.create_test_args()
            result = list_command._list_objects("computer-groups", args)

            end_time = time.time()
            execution_time = end_time - start_time

            performance_results["listing_performance"] = {
                "success": result == 0,
                "execution_time": execution_time,
                "within_limit": execution_time
                < 5.0,  # Should complete within 5 seconds
            }
        except Exception as e:
            performance_results["listing_performance"] = {
                "success": False,
                "execution_time": 0,
                "within_limit": False,
                "error": str(e),
            }

        # Test 2: Groups Export Performance
        print("📤 Testing Groups Export Performance...")
        try:
            start_time = time.time()

            from src.cli.commands.export_command import ExportCommand

            export_command = ExportCommand()
            export_command.auth = GroupsTestConfig.create_mock_auth()

            args = GroupsTestConfig.create_test_args(format="csv")
            result = export_command._export_objects("computer-groups", args)

            end_time = time.time()
            execution_time = end_time - start_time

            performance_results["export_performance"] = {
                "success": result == 0,
                "execution_time": execution_time,
                "within_limit": execution_time
                < 10.0,  # Should complete within 10 seconds
            }
        except Exception as e:
            performance_results["export_performance"] = {
                "success": False,
                "execution_time": 0,
                "within_limit": False,
                "error": str(e),
            }

        # Store results
        self.results["performance_tests"] = performance_results

        return performance_results

    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("📊 GROUPS FUNCTIONALITY TEST REPORT")
        report.append("=" * 50)
        report.append("")

        # Unit Tests Summary
        if "unit_tests" in self.results:
            ut = self.results["unit_tests"]
            report.append("🧪 UNIT TESTS")
            report.append(f"   Tests Run: {ut['tests_run']}")
            report.append(f"   Failures: {ut['failures']}")
            report.append(f"   Errors: {ut['errors']}")
            report.append(f"   Success Rate: {ut['success_rate']:.1f}%")
            report.append("")

        # Integration Tests Summary
        if "integration_tests" in self.results:
            it = self.results["integration_tests"]
            if "skipped" in it:
                report.append("🔗 INTEGRATION TESTS: SKIPPED")
            else:
                report.append("🔗 INTEGRATION TESTS")
                report.append(f"   Tests Run: {it['tests_run']}")
                report.append(f"   Failures: {it['failures']}")
                report.append(f"   Errors: {it['errors']}")
                report.append(f"   Success Rate: {it['success_rate']:.1f}%")
            report.append("")

        # Functionality Tests Summary
        if "functionality_tests" in self.results:
            ft = self.results["functionality_tests"]
            report.append("⚙️  FUNCTIONALITY TESTS")
            for test_name, result in ft.items():
                status = "✅ PASS" if result else "❌ FAIL"
                report.append(f"   {test_name.replace('_', ' ').title()}: {status}")
            report.append("")

        # Performance Tests Summary
        if "performance_tests" in self.results:
            pt = self.results["performance_tests"]
            report.append("⚡ PERFORMANCE TESTS")
            for test_name, result in pt.items():
                if isinstance(result, dict):
                    status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                    exec_time = result.get("execution_time", 0)
                    within_limit = result.get("within_limit", False)
                    report.append(f"   {test_name.replace('_', ' ').title()}: {status}")
                    report.append(f"     Execution Time: {exec_time:.2f}s")
                    report.append(
                        f"     Within Limit: {'✅' if within_limit else '❌'}"
                    )
            report.append("")

        # Overall Summary
        total_tests = 0
        total_passed = 0

        for category, results in self.results.items():
            if category == "unit_tests" and "tests_run" in results:
                total_tests += results["tests_run"]
                total_passed += (
                    results["tests_run"] - results["failures"] - results["errors"]
                )
            elif category == "integration_tests" and "tests_run" in results:
                total_tests += results["tests_run"]
                total_passed += (
                    results["tests_run"] - results["failures"] - results["errors"]
                )
            elif category == "functionality_tests":
                total_tests += len(results)
                total_passed += sum(1 for result in results.values() if result)
            elif category == "performance_tests":
                for test_result in results.values():
                    if isinstance(test_result, dict):
                        total_tests += 1
                        if test_result.get("success", False):
                            total_passed += 1

        overall_success_rate = (
            (total_passed / total_tests * 100) if total_tests > 0 else 0
        )

        report.append("📈 OVERALL SUMMARY")
        report.append(f"   Total Tests: {total_tests}")
        report.append(f"   Passed: {total_passed}")
        report.append(f"   Failed: {total_tests - total_passed}")
        report.append(f"   Success Rate: {overall_success_rate:.1f}%")
        report.append("")

        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        if overall_success_rate >= 90:
            report.append("   ✅ Groups functionality is working excellently!")
        elif overall_success_rate >= 75:
            report.append(
                "   ⚠️  Groups functionality is mostly working with some issues."
            )
        else:
            report.append(
                "   ❌ Groups functionality has significant issues that need attention."
            )

        report.append("")
        report.append("🔧 NEXT STEPS")
        report.append("   1. Review any failed tests and fix underlying issues")
        report.append("   2. Run integration tests with real JAMF Pro instance")
        report.append("   3. Monitor performance in production environment")
        report.append("   4. Add more test coverage for edge cases")

        return "\n".join(report)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories"""
        print("🚀 Starting Comprehensive Groups Functionality Testing")
        print("=" * 70)
        print("")

        # Run all test categories
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_functionality_tests()
        self.run_performance_tests()

        # Generate and display report
        report = self.generate_report()
        print(report)

        # Save report to file
        report_file = Path("groups_test_report.txt")
        with open(report_file, "w") as f:
            f.write(report)

        print(f"📄 Detailed report saved to: {report_file}")

        return self.results


def main():
    """Main function for running groups tests"""
    parser = argparse.ArgumentParser(
        description="Run comprehensive tests for jpapi groups functionality"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--integration", "-i", action="store_true", help="Run integration tests"
    )
    parser.add_argument(
        "--unit-only", "-u", action="store_true", help="Run only unit tests"
    )
    parser.add_argument(
        "--functionality-only",
        "-f",
        action="store_true",
        help="Run only functionality tests",
    )
    parser.add_argument(
        "--performance-only",
        "-p",
        action="store_true",
        help="Run only performance tests",
    )

    args = parser.parse_args()

    # Create test runner
    runner = GroupsTestRunner(verbose=args.verbose, integration=args.integration)

    if args.unit_only:
        runner.run_unit_tests()
    elif args.functionality_only:
        runner.run_functionality_tests()
    elif args.performance_only:
        runner.run_performance_tests()
    else:
        runner.run_all_tests()


if __name__ == "__main__":
    main()
