#!/usr/bin/env python3
"""
Category Create Handler - SOLID SRP
Handles category creation operations
"""

from argparse import Namespace
from .base_handler import BaseCreateHandler


class CategoryCreateHandler(BaseCreateHandler):
    """Handler for creating categories"""
    
    def can_handle(self, object_type: str) -> bool:
        """Check if this handler can handle the given object type"""
        return object_type in ["category", "cat", "cats"]
    
    def create(self, args: Namespace) -> int:
        """Create a new category"""
        try:
            # Production guardrails
            if not getattr(args, "force", False) and self.production_checker:
                if not self.production_checker.check_destructive_operation(
                    "Create Category", args.name
                ):
                    return 1
            
            # Dry-run mode
            dry_run_result = self.check_dry_run(args, "Category", args.name)
            if dry_run_result is not None:
                return dry_run_result
            
            # Add signature to name
            signed_name = self.apply_signature(args.name)
            print(f"📁 Creating Category: {signed_name}")
            
            # Validate priority
            priority = getattr(args, "priority", 9)
            if priority < 1 or priority > 20:
                print("❌ Priority must be between 1 and 20")
                return 1
            
            # Prepare category data
            category_data = {
                "category": {"name": signed_name, "priority": priority}
            }
            
            # Create category via API
            response = self.auth.api_request(
                "POST", "/JSSResource/categories/id/0", data=category_data
            )
            
            if response and "category" in response:
                created_category = response["category"]
                print(f"✅ Category created successfully!")
                print(f"   ID: {created_category.get('id', 'Unknown')}")
                print(f"   Name: {created_category.get('name', signed_name)}")
                print(f"   Priority: {created_category.get('priority', priority)}")
                return 0
            else:
                print("❌ Failed to create category")
                return 1
                
        except Exception as e:
            return self.handle_api_error(e)









