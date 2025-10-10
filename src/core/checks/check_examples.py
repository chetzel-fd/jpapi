#!/usr/bin/env python3
"""
Production Safety Integration Example
Shows how to integrate guardrails with existing jpapi commands
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.checks.api_checks import ProductionGuardrails, with_production_guardrails
from core.auth.login_manager import UnifiedJamfAuth


class ProductionSafeJPAPIDev:
    """
    Production-safe wrapper for jpapi operations
    """

    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.guardrails = ProductionGuardrails(environment)
        self.auth = UnifiedJamfAuth(environment=environment, backend="keychain")

    def safe_list_policies(self, detailed: bool = False) -> dict:
        """
        Safely list policies with production guardrails
        """
        if not self.guardrails.check_environment_safety():
            return {"success": False, "error": "Environment safety check failed"}

        try:
            response = self.auth.api_request("GET", "/api/v1/policies")
            policies = response.get("results", [])

            result = {
                "success": True,
                "policies": policies,
                "count": len(policies),
                "environment": self.environment,
            }

            self.guardrails._log_operation(
                "list_policies", "SUCCESS", f"Found {len(policies)} policies"
            )
            return result

        except Exception as e:
            self.guardrails._log_operation("list_policies", "ERROR", str(e))
            return {"success": False, "error": str(e)}

    @with_production_guardrails("prod")
    def safe_delete_policy(self, policy_id: str) -> dict:
        """
        Safely delete a policy with production guardrails
        """
        # Register the destructive action
        self.guardrails.register_destructive_action(
            action_type="DELETE_POLICY",
            description=f"Delete policy ID {policy_id}",
            target=f"Policy ID {policy_id}",
            details={"policy_id": policy_id, "environment": self.environment},
        )

        try:
            # This would be the actual delete operation
            # response = self.auth.api_request('DELETE', f'/api/v1/policies/{policy_id}')

            # For demo purposes, just simulate success
            result = {
                "success": True,
                "message": f"Policy {policy_id} deleted successfully",
                "environment": self.environment,
            }

            self.guardrails._log_operation("delete_policy", "SUCCESS", result)
            return result

        except Exception as e:
            self.guardrails._log_operation("delete_policy", "ERROR", str(e))
            return {"success": False, "error": str(e)}

    @with_production_guardrails("prod")
    def safe_update_policy(self, policy_id: str, updates: dict) -> dict:
        """
        Safely update a policy with production guardrails
        """
        # Register the destructive action
        self.guardrails.register_destructive_action(
            action_type="UPDATE_POLICY",
            description=f"Update policy ID {policy_id}",
            target=f"Policy ID {policy_id}",
            details={
                "policy_id": policy_id,
                "updates": updates,
                "environment": self.environment,
            },
        )

        try:
            # This would be the actual update operation
            # response = self.auth.api_request('PUT', f'/api/v1/policies/{policy_id}', updates)

            # For demo purposes, just simulate success
            result = {
                "success": True,
                "message": f"Policy {policy_id} updated successfully",
                "updates": updates,
                "environment": self.environment,
            }

            self.guardrails._log_operation("update_policy", "SUCCESS", result)
            return result

        except Exception as e:
            self.guardrails._log_operation("update_policy", "ERROR", str(e))
            return {"success": False, "error": str(e)}

    def get_safety_status(self) -> dict:
        """
        Get current safety status
        """
        return self.guardrails.get_safety_summary()

    def show_audit_log(self, limit: int = 10) -> None:
        """
        Show recent audit log entries
        """
        entries = self.guardrails.get_audit_log(limit)

        if not entries:
            print("No audit log entries found")
            return

        print(f"\n📋 Recent Audit Log (last {len(entries)} entries)")
        print("=" * 60)

        for entry in entries:
            print(f"\n⏰ {entry['timestamp']}")
            print(f"   Environment: {entry['environment']}")
            print(f"   Operation: {entry['operation']}")
            print(f"   Status: {entry['status']}")
            if entry["result"]:
                print(f"   Result: {entry['result'][:100]}...")


def main():
    """
    Demonstrate production-safe jpapi operations
    """
    print("🛡️ Production-Safe JPAPIDev Example")
    print("=" * 50)

    # Test with DEV environment (should be safe)
    print("\n1. Testing with DEV environment:")
    print("-" * 40)

    dev_jpapi = ProductionSafeJPAPIDev("dev")
    result = dev_jpapi.safe_list_policies()
    print(f"List policies result: {result['success']}")

    # Test with PROD environment (should trigger guardrails)
    print("\n2. Testing with PROD environment:")
    print("-" * 40)

    prod_jpapi = ProductionSafeJPAPIDev("prod")

    # Safe operation
    result = prod_jpapi.safe_list_policies()
    print(f"List policies result: {result['success']}")

    # Destructive operation (would trigger guardrails)
    print("\n3. Testing destructive operations:")
    print("-" * 40)

    # This would trigger the guardrails in a real scenario
    print("Note: In a real scenario, these would trigger guardrails:")
    print("- delete_policy() would require DEV connection confirmation")
    print("- update_policy() would require confirmation of changes")

    # Show safety status
    print("\n4. Safety Status:")
    print("-" * 40)

    status = prod_jpapi.get_safety_status()
    for key, value in status.items():
        print(f"   {key}: {value}")

    # Show audit log
    print("\n5. Audit Log:")
    print("-" * 40)

    prod_jpapi.show_audit_log(5)

    print("\n✅ Production safety integration example completed!")
    print("\nTo use in your code:")
    print("1. Create: jpapi = ProductionSafeJPAPIDev('prod')")
    print("2. Safe ops: jpapi.safe_list_policies()")
    print("3. Destructive ops: jpapi.safe_delete_policy('123')")
    print("4. Check status: jpapi.get_safety_status()")


if __name__ == "__main__":
    main()
