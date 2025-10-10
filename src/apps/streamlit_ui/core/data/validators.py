"""
Data Validators - Single Responsibility Principle
Validates CSV data structure and content
"""

import pandas as pd
from typing import List, Dict, Any
from .interfaces import DataValidatorInterface


class CSVDataValidator(DataValidatorInterface):
    """CSV data validator implementation"""

    def __init__(self):
        self.required_columns = ["Name", "Status", "Modified"]
        self.optional_columns = ["Smart", "Description", "Category"]
        self.valid_statuses = ["Active", "Deleted", "Inactive"]

    def validate_structure(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame structure"""
        if df.empty:
            return False

        # Check for required columns
        missing_columns = set(self.required_columns) - set(df.columns)
        if missing_columns:
            return False

        return True

    def validate_content(self, df: pd.DataFrame) -> bool:
        """Validate DataFrame content"""
        if not self.validate_structure(df):
            return False

        # Check for valid status values
        if "Status" in df.columns:
            invalid_statuses = df[~df["Status"].isin(self.valid_statuses)]
            if not invalid_statuses.empty:
                return False

        # Check for valid Smart column values (if present)
        if "Smart" in df.columns:
            invalid_smart = df[~df["Smart"].isin([True, False, 1, 0, "True", "False"])]
            if not invalid_smart.empty:
                return False

        return True

    def get_validation_errors(self, df: pd.DataFrame) -> List[str]:
        """Get list of validation errors"""
        errors = []

        if df.empty:
            errors.append("DataFrame is empty")
            return errors

        # Check for required columns
        missing_columns = set(self.required_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")

        # Check for valid status values
        if "Status" in df.columns:
            invalid_statuses = df[~df["Status"].isin(self.valid_statuses)]
            if not invalid_statuses.empty:
                errors.append(
                    f"Invalid status values: {invalid_statuses['Status'].unique()}"
                )

        # Check for valid Smart column values
        if "Smart" in df.columns:
            invalid_smart = df[~df["Smart"].isin([True, False, 1, 0, "True", "False"])]
            if not invalid_smart.empty:
                errors.append(
                    f"Invalid Smart values: {invalid_smart['Smart'].unique()}"
                )

        return errors

    def validate(self, df: pd.DataFrame) -> bool:
        """Main validation method"""
        return self.validate_structure(df) and self.validate_content(df)
