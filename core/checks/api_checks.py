#!/usr/bin/env python3
"""
Production Guardrails Module
Provides safety mechanisms for all operations targeting production environments
"""

import sys
import getpass
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import json

class ProductionGuardrails:
    """
    Production safety guardrails to prevent accidental destructive operations
    """
    
    def __init__(self, environment: str = 'dev'):
        self.environment = environment
        self.is_production = environment.lower() in ['prod', 'production']
        self.destructive_actions = []
        self.confirmation_required = False
        
    def check_environment_safety(self) -> bool:
        """
        Check if the current environment is safe for operations
        Returns True if safe, False if production requires confirmation
        """
        if not self.is_production:
            print(f"✅ Safe environment: {self.environment}")
            return True
        
        print("⚠️  PRODUCTION ENVIRONMENT DETECTED")
        print("=" * 50)
        print(f"Environment: {self.environment.upper()}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Check if user is connected to dev first
        if not self._confirm_dev_connection():
            print("❌ Operation cancelled - must be connected to DEV first")
            return False
        
        return True
    
    def _confirm_dev_connection(self) -> bool:
        """
        Confirm user is connected to DEV environment first
        """
        print("\n🔍 PRODUCTION SAFETY CHECK")
        print("Before proceeding with PRODUCTION operations, confirm you are connected to DEV:")
        
        dev_connected = input("Are you currently connected to DEV environment? (y/N): ").strip().lower()
        
        if dev_connected not in ['y', 'yes']:
            print("❌ Please connect to DEV environment first before working with PRODUCTION")
            print("   This ensures you can verify changes in a safe environment")
            return False
        
        print("✅ DEV connection confirmed")
        return True
    
    def register_destructive_action(self, action_type: str, description: str, 
                                 target: str, details: Dict[str, Any] = None) -> None:
        """
        Register a potentially destructive action for confirmation
        """
        action = {
            'type': action_type,
            'description': description,
            'target': target,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.destructive_actions.append(action)
        self.confirmation_required = True
    
    def confirm_destructive_actions(self) -> bool:
        """
        Present all destructive actions for confirmation
        Returns True if user confirms, False if cancelled
        """
        if not self.destructive_actions:
            return True
        
        if not self.is_production:
            print(f"✅ Non-production environment ({self.environment}) - no confirmation needed")
            return True
        
        print("\n" + "=" * 60)
        print("⚠️  DESTRUCTIVE ACTIONS REQUIRING CONFIRMATION")
        print("=" * 60)
        
        for i, action in enumerate(self.destructive_actions, 1):
            print(f"\n{i}. {action['type'].upper()}")
            print(f"   Description: {action['description']}")
            print(f"   Target: {action['target']}")
            print(f"   Time: {action['timestamp']}")
            
            if action['details']:
                print("   Details:")
                for key, value in action['details'].items():
                    print(f"     {key}: {value}")
        
        print("\n" + "=" * 60)
        print("⚠️  WARNING: These actions will be performed on PRODUCTION")
        print("=" * 60)
        
        # Get confirmation
        confirmation = input("\nDo you want to proceed with these actions? (yes/NO): ").strip().lower()
        
        if confirmation not in ['yes', 'y']:
            print("❌ Operation cancelled by user")
            return False
        
        # Additional safety check
        safety_word = input("Type 'PRODUCTION' to confirm: ").strip()
        if safety_word != 'PRODUCTION':
            print("❌ Safety word incorrect - operation cancelled")
            return False
        
        print("✅ Confirmed - proceeding with production operations")
        return True
    
    def safe_execute(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Safely execute an operation with guardrails
        """
        if not self.check_environment_safety():
            raise Exception("Environment safety check failed")
        
        if self.confirmation_required:
            if not self.confirm_destructive_actions():
                raise Exception("User cancelled destructive operations")
        
        # Execute the operation
        try:
            result = operation(*args, **kwargs)
            self._log_operation(operation.__name__, "SUCCESS", result)
            return result
        except Exception as e:
            self._log_operation(operation.__name__, "ERROR", str(e))
            raise
    
    def _log_operation(self, operation_name: str, status: str, result: Any) -> None:
        """
        Log operation results for audit trail
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'operation': operation_name,
            'status': status,
            'result': str(result)[:500] if result else None
        }
        
        # Log to file
        log_file = Path.home() / '.jpapi' / 'production_audit.log'
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_audit_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent audit log entries
        """
        log_file = Path.home() / '.jpapi' / 'production_audit.log'
        
        if not log_file.exists():
            return []
        
        entries = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return entries[-limit:]
    
    def clear_destructive_actions(self) -> None:
        """
        Clear the list of destructive actions
        """
        self.destructive_actions.clear()
        self.confirmation_required = False
    
    def get_safety_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current safety status
        """
        return {
            'environment': self.environment,
            'is_production': self.is_production,
            'destructive_actions_count': len(self.destructive_actions),
            'confirmation_required': self.confirmation_required,
            'timestamp': datetime.now().isoformat()
        }


class ProductionGuardrailsDecorator:
    """
    Decorator class for adding guardrails to functions
    """
    
    def __init__(self, environment: str = 'dev'):
        self.guardrails = ProductionGuardrails(environment)
    
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to add guardrails to a function
        """
        def wrapper(*args, **kwargs):
            # Check if this is a destructive operation
            if self._is_destructive_operation(func.__name__):
                self.guardrails.register_destructive_action(
                    action_type="FUNCTION_CALL",
                    description=f"Executing {func.__name__}",
                    target=self.guardrails.environment,
                    details={'function': func.__name__, 'args': str(args)[:200]}
                )
            
            return self.guardrails.safe_execute(func, *args, **kwargs)
        
        return wrapper
    
    def _is_destructive_operation(self, function_name: str) -> bool:
        """
        Check if a function name suggests a destructive operation
        """
        destructive_keywords = [
            'delete', 'remove', 'uninstall', 'destroy', 'clear', 'reset',
            'update', 'modify', 'change', 'create', 'add', 'install'
        ]
        
        return any(keyword in function_name.lower() for keyword in destructive_keywords)


# Convenience functions for common operations
def create_production_guardrails(environment: str = 'dev') -> ProductionGuardrails:
    """
    Create a production guardrails instance
    """
    return ProductionGuardrails(environment)


def with_production_guardrails(environment: str = 'dev'):
    """
    Decorator factory for adding guardrails to functions
    """
    return ProductionGuardrailsDecorator(environment)


def check_production_safety(environment: str) -> bool:
    """
    Quick safety check for production environment
    """
    guardrails = ProductionGuardrails(environment)
    return guardrails.check_environment_safety()


# Example usage and testing
if __name__ == "__main__":
    # Test the guardrails
    guardrails = ProductionGuardrails('prod')
    
    print("Testing Production Guardrails:")
    print("=" * 40)
    
    # Test environment check
    safe = guardrails.check_environment_safety()
    print(f"Environment safe: {safe}")
    
    # Test destructive action registration
    guardrails.register_destructive_action(
        "DELETE_POLICY",
        "Delete policy 'Test Policy'",
        "Policy ID 123",
        {"policy_name": "Test Policy", "policy_id": 123}
    )
    
    # Test confirmation
    confirmed = guardrails.confirm_destructive_actions()
    print(f"Actions confirmed: {confirmed}")
    
    # Test safety summary
    summary = guardrails.get_safety_summary()
    print(f"Safety summary: {summary}")
