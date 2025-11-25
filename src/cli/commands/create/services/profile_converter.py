#!/usr/bin/env python3
"""
Profile Converter Service - SOLID SRP
Handles conversion between mobileconfig, JSON, and XML formats
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import plistlib
import xml.sax.saxutils


class IProfileConverter(ABC):
    """Interface for profile conversion operations"""
    
    @abstractmethod
    def mobileconfig_to_xml(self, mobileconfig_data: Dict[str, Any]) -> str:
        """Convert mobileconfig data to XML-escaped string"""
        pass
    
    @abstractmethod
    def json_to_mobileconfig_xml(self, json_data: Dict[str, Any]) -> str:
        """Convert JSON data to mobileconfig XML format"""
        pass


class ProfileConverterService(IProfileConverter):
    """Service for converting profile formats"""
    
    def mobileconfig_to_xml(self, mobileconfig_data: Dict[str, Any]) -> str:
        """Convert mobileconfig data to XML-escaped string for Jamf Pro"""
        # Convert mobileconfig to XML string
        mobileconfig_xml = plistlib.dumps(
            mobileconfig_data, fmt=plistlib.FMT_XML
        ).decode("utf-8")
        
        # XML-escape the content for embedding in Jamf Pro XML
        escaped_xml = xml.sax.saxutils.escape(mobileconfig_xml)
        
        return escaped_xml
    
    def json_to_mobileconfig_xml(self, json_data: Dict[str, Any]) -> str:
        """Convert JSON data to mobileconfig XML format for Jamf Pro"""
        # Convert JSON to mobileconfig format
        mobileconfig_data = {
            "PayloadUUID": json_data.get("PayloadUUID", "auto-generated"),
            "PayloadType": "com.apple.TCC.configuration-profile-policy",
            "PayloadOrganization": json_data.get(
                "PayloadOrganization", "Your Organization"
            ),
            "PayloadIdentifier": json_data.get("PayloadIdentifier", "auto-generated"),
            "PayloadDisplayName": json_data.get(
                "PayloadDisplayName", "Configuration Profile"
            ),
            "PayloadDescription": json_data.get(
                "PayloadDescription", "Configuration profile created by jpapi"
            ),
            "PayloadVersion": 1,
            "PayloadEnabled": True,
            "PayloadRemovalDisallowed": False,
            "PayloadScope": "System",
            "PayloadContent": json_data.get("PayloadContent", []),
        }
        
        # Convert to XML string
        mobileconfig_xml = plistlib.dumps(
            mobileconfig_data, fmt=plistlib.FMT_XML
        ).decode("utf-8")
        
        # XML-escape the content for embedding in Jamf Pro XML
        escaped_xml = xml.sax.saxutils.escape(mobileconfig_xml)
        
        return escaped_xml









