#!/usr/bin/env python3
"""
Criteria Parser Service - SOLID SRP
Handles parsing of smart group criteria
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import re


class ICriteriaParser(ABC):
    """Interface for criteria parsing operations"""
    
    @abstractmethod
    def parse_criteria(self, criteria_input: str) -> List[Dict[str, str]]:
        """Parse criteria string into list of criterion dictionaries"""
        pass
    
    @abstractmethod
    def parse_email_addresses(self, emails_input: str) -> List[str]:
        """Parse email addresses from input string"""
        pass
    
    @abstractmethod
    def parse_job_titles(self, job_titles_input: str) -> List[str]:
        """Parse job titles from input string"""
        pass


class CriteriaParserService(ICriteriaParser):
    """Service for parsing smart group criteria"""
    
    def parse_criteria(self, criteria_input: str) -> List[Dict[str, str]]:
        """Parse criteria string into list of criterion dictionaries"""
        criteria_list = []
        
        # Use regex to split by comma, but not inside quotes
        parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', criteria_input)
        
        for part in parts:
            part = part.strip()
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip().strip("\"'")  # Remove quotes
                
                if key and value:
                    criteria_list.append({"type": key, "value": value})
        
        return criteria_list
    
    def parse_email_addresses(self, emails_input: str) -> List[str]:
        """Parse email addresses from input string"""
        # Support both comma and pipe separation
        if "|" in emails_input:
            emails = [email.strip() for email in emails_input.split("|")]
        else:
            emails = [email.strip() for email in emails_input.split(",")]
        
        # Validate email format (basic validation)
        valid_emails = []
        for email in emails:
            if email:
                # Check if it's a full email address or just username
                if "@" in email and "." in email.split("@")[1]:
                    # Full email address
                    valid_emails.append(email)
                elif "@" not in email and "." in email:
                    # Username only - we'll add domain later
                    valid_emails.append(email)
                else:
                    print(f"⚠️  Skipping invalid email: {email}")
        
        return valid_emails
    
    def parse_job_titles(self, job_titles_input: str) -> List[str]:
        """Parse job titles from input string"""
        # Support both comma and pipe separation
        if "|" in job_titles_input:
            job_titles = [title.strip() for title in job_titles_input.split("|")]
        else:
            job_titles = [title.strip() for title in job_titles_input.split(",")]
        
        # Filter out empty strings
        valid_titles = [title for title in job_titles if title]
        
        return valid_titles









