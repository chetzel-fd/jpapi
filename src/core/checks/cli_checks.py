#!/usr/bin/env python3
"""
Production-Safe CLI Wrapper
Wraps jpapi CLI commands with production guardrails
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.checks.api_checks import ProductionGuardrails, with_production_guardrails

class ProductionSafeCLI:
    """
    Production-safe wrapper for jpapi CLI commands
    """
    
    def __init__(self, environment: str = 'dev'):
        self.environment = environment
        self.guardrails = ProductionGuardrails(environment)
        self.destructive_commands = {
            'delete', 'remove', 'uninstall', 'destroy', 'clear', 'reset',
            'update', 'modify', 'change', 'create', 'add', 'install',
            'move', 'transfer', 'sync', 'apply'
        }
    
    def is_destructive_command(self, command: str, subcommand: str = None) -> bool:
        """
        Check if a command is potentially destructive
        """
        full_command = f"{command} {subcommand}" if subcommand else command
        return any(destructive in full_command.lower() for destructive in self.destructive_commands)
    
    def safe_execute_command(self, command: str, subcommand: str = None, 
                           args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Safely execute a CLI command with production guardrails
        """
        args = args or []
        full_command = f"{command} {subcommand}" if subcommand else command
        
        # Check if this is a destructive command
        if self.is_destructive_command(command, subcommand):
            self.guardrails.register_destructive_action(
                action_type="CLI_COMMAND",
                description=f"Execute command: {full_command}",
                target=self.environment,
                details={
                    'command': command,
                    'subcommand': subcommand,
                    'args': args,
                    'environment': self.environment
                }
            )
        
        # Check environment safety
        if not self.guardrails.check_environment_safety():
            return {
                'success': False,
                'error': 'Environment safety check failed',
                'command': full_command
            }
        
        # Confirm destructive actions if needed
        if self.guardrails.confirmation_required:
            if not self.guardrails.confirm_destructive_actions():
                return {
                    'success': False,
                    'error': 'User cancelled destructive operations',
                    'command': full_command
                }
        
        # Execute the command
        try:
            result = self._execute_cli_command(command, subcommand, args, **kwargs)
            self.guardrails._log_operation(full_command, "SUCCESS", result)
            return {
                'success': True,
                'result': result,
                'command': full_command
            }
        except Exception as e:
            self.guardrails._log_operation(full_command, "ERROR", str(e))
            return {
                'success': False,
                'error': str(e),
                'command': full_command
            }
    
    def _execute_cli_command(self, command: str, subcommand: str = None, 
                           args: List[str] = None, **kwargs) -> Any:
        """
        Execute the actual CLI command
        This would integrate with the actual jpapi CLI
        """
        # This is a placeholder - in practice, this would call the actual CLI
        print(f"Executing: {command} {subcommand} {' '.join(args or [])}")
        return f"Command executed: {command} {subcommand}"
    
    def get_safety_status(self) -> Dict[str, Any]:
        """
        Get current safety status
        """
        return self.guardrails.get_safety_summary()
    
    def show_audit_log(self, limit: int = 20) -> None:
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
            if entry['result']:
                print(f"   Result: {entry['result'][:100]}...")
    
    def clear_safety_state(self) -> None:
        """
        Clear current safety state
        """
        self.guardrails.clear_destructive_actions()
        print("✅ Safety state cleared")


# Production-safe decorators for specific operations
@with_production_guardrails('prod')
def safe_delete_policy(policy_id: str, environment: str = 'prod') -> bool:
    """
    Safely delete a policy with production guardrails
    """
    print(f"Deleting policy {policy_id} from {environment}")
    # Actual deletion logic would go here
    return True


@with_production_guardrails('prod')
def safe_update_policy(policy_id: str, updates: Dict[str, Any], environment: str = 'prod') -> bool:
    """
    Safely update a policy with production guardrails
    """
    print(f"Updating policy {policy_id} with {updates} in {environment}")
    # Actual update logic would go here
    return True


@with_production_guardrails('prod')
def safe_create_policy(policy_data: Dict[str, Any], environment: str = 'prod') -> bool:
    """
    Safely create a policy with production guardrails
    """
    print(f"Creating policy with {policy_data} in {environment}")
    # Actual creation logic would go here
    return True


# Integration with existing jpapi commands
def wrap_jpapi_command(environment: str = 'dev'):
    """
    Wrap jpapi commands with production guardrails
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cli = ProductionSafeCLI(environment)
            return cli.safe_execute_command(func.__name__, args=args, **kwargs)
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Test the production-safe CLI
    cli = ProductionSafeCLI('prod')
    
    print("Testing Production-Safe CLI:")
    print("=" * 40)
    
    # Test safe command execution
    result = cli.safe_execute_command('list', 'policies', ['--detailed'])
    print(f"Command result: {result}")
    
    # Test destructive command
    result = cli.safe_execute_command('delete', 'policy', ['123'])
    print(f"Destructive command result: {result}")
    
    # Show safety status
    status = cli.get_safety_status()
    print(f"Safety status: {status}")
    
    # Show audit log
    cli.show_audit_log(5)
