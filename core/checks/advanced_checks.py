#!/usr/bin/env python3
"""
Robust Production Guardrails - SOLID Principles Implementation
Provides fail-safe production protection with comprehensive validation
"""

import sys
import getpass
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, Protocol
from datetime import datetime
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum

class EnvironmentType(Enum):
    """Environment types for safety validation"""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
    PRODUCTION = "production"

class OperationRisk(Enum):
    """Risk levels for operations"""
    SAFE = "safe"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class OperationContext:
    """Context information for an operation"""
    operation_name: str
    environment: EnvironmentType
    risk_level: OperationRisk
    details: str
    changes_summary: str
    timestamp: datetime
    user: str
    session_id: str

class GuardrailValidator(Protocol):
    """Protocol for guardrail validators following Interface Segregation Principle"""
    
    def validate(self, context: OperationContext) -> bool:
        """Validate if operation should proceed"""
        ...

class InteractiveValidator(GuardrailValidator):
    """Validates interactive confirmation requirements"""
    
    def validate(self, context: OperationContext) -> bool:
        """Ensure operation is interactive and confirmed"""
        if context.environment not in [EnvironmentType.PROD, EnvironmentType.PRODUCTION]:
            return True
            
        # Check if input is interactive
        if not sys.stdin.isatty():
            print("❌ CRITICAL ERROR: Production operations require interactive confirmation")
            print("   Piped input is blocked for production safety")
            print("   Please run the command interactively")
            return False
            
        return True

class ForceFlagValidator(GuardrailValidator):
    """Validates force flag usage with additional safety checks"""
    
    def __init__(self, force_flag: bool = False):
        self.force_flag = force_flag
        
    def validate(self, context: OperationContext) -> bool:
        """Validate force flag usage with safety checks"""
        if not self.force_flag:
            return True
            
        if context.environment not in [EnvironmentType.PROD, EnvironmentType.PRODUCTION]:
            return True
            
        # Additional safety checks for force flag in production
        print("🔒 FORCE FLAG DETECTED - Additional Safety Checks Required")
        
        # Check if running in CI/CD environment
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS') or os.getenv('JENKINS_URL'):
            print("❌ CRITICAL ERROR: Force flag not allowed in CI/CD environments")
            print("   This prevents accidental production changes from automated systems")
            return False
            
        # Check if running as root/system user
        if os.getuid() == 0 or getpass.getuser() in ['root', 'system', 'admin']:
            print("❌ CRITICAL ERROR: Force flag not allowed for system users")
            print("   This prevents accidental production changes from system accounts")
            return False
            
        # Require additional confirmation for force flag
        print("⚠️  WARNING: Force flag bypasses normal safety checks")
        print("   This will modify PRODUCTION data without standard confirmation")
        
        # Double confirmation for force flag
        response1 = input("Type 'FORCE' to confirm force flag usage: ").strip()
        if response1 != 'FORCE':
            print("❌ Force flag confirmation failed")
            return False
            
        response2 = input("Type 'PRODUCTION' to confirm production modification: ").strip()
        if response2 != 'PRODUCTION':
            print("❌ Production confirmation failed")
            return False
            
        print("✅ Force flag confirmed with double verification")
        return True

class EnvironmentValidator(GuardrailValidator):
    """Validates environment safety"""
    
    def validate(self, context: OperationContext) -> bool:
        """Validate environment is safe for operation"""
        if context.environment in [EnvironmentType.DEV, EnvironmentType.STAGING]:
            return True
            
        # Production environment requires additional checks
        print("🚨 PRODUCTION ENVIRONMENT DETECTED")
        print("=" * 60)
        print(f"Operation: {context.operation_name}")
        print(f"Environment: {context.environment.value.upper()}")
        print(f"Risk Level: {context.risk_level.value.upper()}")
        print(f"User: {context.user}")
        print(f"Timestamp: {context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return True

class ChangesSummaryValidator(GuardrailValidator):
    """Validates and displays changes summary"""
    
    def validate(self, context: OperationContext) -> bool:
        """Display changes summary and get confirmation"""
        if not context.changes_summary:
            return True
            
        print("\n📋 DETAILED CHANGES SUMMARY:")
        print("-" * 50)
        print(context.changes_summary)
        print("-" * 50)
        
        if context.environment in [EnvironmentType.PROD, EnvironmentType.PRODUCTION]:
            print("\n⚠️  CRITICAL: This will modify PRODUCTION data")
            print("💡 Use --dry-run to test operations safely")
            print("🔒 Use --force to skip confirmation (requires double verification)")
            print()
            
            # Require explicit confirmation
            response = input("Type 'yes' to proceed or 'no' to cancel: ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Operation cancelled by user")
                return False
                
            print("✅ Production operation confirmed")
            
        return True

class RobustGuardrails:
    """
    Robust production guardrails following SOLID principles
    - Single Responsibility: Each validator handles one concern
    - Open/Closed: Easy to add new validators without modifying existing code
    - Liskov Substitution: All validators implement the same interface
    - Interface Segregation: Validators only implement what they need
    - Dependency Inversion: Depends on abstractions, not concretions
    """
    
    def __init__(self, environment: str = 'dev'):
        self.environment = EnvironmentType(environment.lower())
        self.validators: List[GuardrailValidator] = []
        self._setup_default_validators()
        
    def _setup_default_validators(self):
        """Setup default validators"""
        self.validators.extend([
            EnvironmentValidator(),
            InteractiveValidator(),
            ChangesSummaryValidator()
        ])
        
    def add_validator(self, validator: GuardrailValidator):
        """Add a custom validator (Open/Closed Principle)"""
        self.validators.append(validator)
        
    def require_production_confirmation(
        self, 
        operation: str, 
        details: str = "", 
        changes_summary: str = "", 
        args: Optional[Any] = None
    ) -> bool:
        """
        Require production confirmation with comprehensive validation
        """
        # Check for dry run first
        if args and getattr(args, 'dry_run', False):
            print("🔍 --dry-run flag detected: Skipping production confirmation")
            return True
            
        # Create operation context
        context = OperationContext(
            operation_name=operation,
            environment=self.environment,
            risk_level=self._assess_risk_level(operation),
            details=details,
            changes_summary=changes_summary,
            timestamp=datetime.now(),
            user=getpass.getuser(),
            session_id=self._get_session_id()
        )
        
        # Check for force flag and add validator BEFORE other validators
        force_flag = args and getattr(args, 'force', False)
        if force_flag:
            # Create a new instance with force flag validator first
            force_validator = ForceFlagValidator(force_flag=True)
            if not force_validator.validate(context):
                return False
            # If force flag passes, skip other validators
            return True
            
        # Run all validators for non-force operations
        for validator in self.validators:
            if not validator.validate(context):
                return False
                
        return True
        
    def _assess_risk_level(self, operation: str) -> OperationRisk:
        """Assess risk level of operation"""
        high_risk_ops = ['delete', 'remove', 'destroy', 'clear', 'reset']
        moderate_risk_ops = ['update', 'modify', 'change', 'move', 'transfer']
        
        operation_lower = operation.lower()
        
        if any(op in operation_lower for op in high_risk_ops):
            return OperationRisk.CRITICAL
        elif any(op in operation_lower for op in moderate_risk_ops):
            return OperationRisk.HIGH
        elif 'create' in operation_lower or 'add' in operation_lower:
            return OperationRisk.MODERATE
        else:
            return OperationRisk.SAFE
            
    def _get_session_id(self) -> str:
        """Generate a session ID for tracking"""
        import uuid
        return str(uuid.uuid4())[:8]
        
    def log_operation(self, operation: str, success: bool, details: str = ""):
        """Log operation for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment.value,
            'operation': operation,
            'success': success,
            'details': details,
            'user': getpass.getuser()
        }
        
        # Log to audit file
        log_file = Path.home() / '.jpapi' / 'robust_audit.log'
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
