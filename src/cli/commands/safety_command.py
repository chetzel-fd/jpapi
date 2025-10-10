#!/usr/bin/env python3
"""
Safety Command for jpapi CLI
Provides production safety and guardrails functionality
"""

from argparse import ArgumentParser, Namespace
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add base to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.command import BaseCommand
from core.checks.api_checks import ProductionGuardrails
from core.checks.cli_checks import ProductionSafeCLI

class SafetyCommand(BaseCommand):
    """Command for production safety and guardrails"""
    
    def __init__(self):
        super().__init__(
            name="safety",
            description="🛡️ Production safety and guardrails management"
        )
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add safety command arguments"""
        subparsers = parser.add_subparsers(dest='safety_action', help='Safety actions')
        
        # Check command
        check_parser = subparsers.add_parser('check', help='Check production safety status')
        check_parser.add_argument('--environment', default='prod', 
                                help='Environment to check (default: prod)')
        self.setup_common_args(check_parser)
        
        # Audit command
        audit_parser = subparsers.add_parser('audit', help='Show audit log')
        audit_parser.add_argument('--limit', type=int, default=20,
                                help='Number of entries to show (default: 20)')
        audit_parser.add_argument('--environment', default='prod',
                                help='Environment to audit (default: prod)')
        self.setup_common_args(audit_parser)
        
        # Clear command
        clear_parser = subparsers.add_parser('clear', help='Clear safety state')
        clear_parser.add_argument('--environment', default='prod',
                                help='Environment to clear (default: prod)')
        self.setup_common_args(clear_parser)
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Test production guardrails')
        test_parser.add_argument('--environment', default='prod',
                                help='Environment to test (default: prod)')
        self.setup_common_args(test_parser)
    
    def execute(self, args: Namespace) -> int:
        """Execute the safety command"""
        if not self.check_auth(args):
            return 1
        
        try:
            if not args.safety_action:
                print("❌ Please specify a safety action")
                print("\nAvailable actions:")
                print("  jpapi safety check")
                print("  jpapi safety audit")
                print("  jpapi safety clear")
                print("  jpapi safety test")
                return 1
            
            if args.safety_action == 'check':
                return self._check_safety(args)
            elif args.safety_action == 'audit':
                return self._show_audit(args)
            elif args.safety_action == 'clear':
                return self._clear_safety(args)
            elif args.safety_action == 'test':
                return self._test_guardrails(args)
            else:
                print(f"❌ Unknown safety action: {args.safety_action}")
                return 1
                
        except Exception as e:
            return self.handle_api_error(e)
    
    def _check_safety(self, args: Namespace) -> int:
        """Check production safety status"""
        print("🛡️ Production Safety Check")
        print("=" * 40)
        
        environment = getattr(args, 'environment', 'prod')
        guardrails = ProductionGuardrails(environment)
        
        # Check environment safety
        safe = guardrails.check_environment_safety()
        
        if safe:
            print("✅ Environment is safe for operations")
        else:
            print("❌ Environment requires additional confirmation")
        
        # Show safety summary
        summary = guardrails.get_safety_summary()
        print(f"\n📊 Safety Summary:")
        print(f"   Environment: {summary['environment']}")
        print(f"   Is Production: {summary['is_production']}")
        print(f"   Destructive Actions: {summary['destructive_actions_count']}")
        print(f"   Confirmation Required: {summary['confirmation_required']}")
        
        return 0 if safe else 1
    
    def _show_audit(self, args: Namespace) -> int:
        """Show audit log"""
        environment = getattr(args, 'environment', 'prod')
        limit = getattr(args, 'limit', 20)
        
        cli = ProductionSafeCLI(environment)
        cli.show_audit_log(limit)
        
        return 0
    
    def _clear_safety(self, args: Namespace) -> int:
        """Clear safety state"""
        environment = getattr(args, 'environment', 'prod')
        
        print(f"🧹 Clearing safety state for {environment}...")
        
        cli = ProductionSafeCLI(environment)
        cli.clear_safety_state()
        
        print("✅ Safety state cleared")
        return 0
    
    def _test_guardrails(self, args: Namespace) -> int:
        """Test production guardrails"""
        environment = getattr(args, 'environment', 'prod')
        
        print("🧪 Testing Production Guardrails")
        print("=" * 40)
        
        cli = ProductionSafeCLI(environment)
        
        # Test safe command
        print("\n1. Testing safe command (list policies)...")
        result = cli.safe_execute_command('list', 'policies', ['--detailed'])
        print(f"   Result: {result['success']}")
        
        # Test destructive command
        print("\n2. Testing destructive command (delete policy)...")
        result = cli.safe_execute_command('delete', 'policy', ['123'])
        print(f"   Result: {result['success']}")
        if not result['success']:
            print(f"   Error: {result['error']}")
        
        # Show safety status
        print("\n3. Safety status:")
        status = cli.get_safety_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Guardrails test completed")
        return 0
