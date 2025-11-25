#!/usr/bin/env python3
"""
XML Converter Service - SOLID SRP
Handles conversion between dictionaries and XML for JAMF API
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import xml.etree.ElementTree as ET


class IXMLConverter(ABC):
    """Interface for XML conversion operations"""
    
    @abstractmethod
    def dict_to_xml(self, data: Dict[str, Any], root_name: str) -> str:
        """Convert dictionary to XML string"""
        pass


class XMLConverterService(IXMLConverter):
    """Service for converting dictionaries to XML format for JAMF API"""
    
    def dict_to_xml(self, data: Dict[str, Any], root_name: str) -> str:
        """Convert dictionary to XML string for JAMF API"""
        
        def dict_to_xml_elem(parent, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        child = ET.SubElement(parent, key)
                        dict_to_xml_elem(child, value)
                    else:
                        child = ET.SubElement(parent, key)
                        if value is not None:
                            child.text = str(value)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        dict_to_xml_elem(parent, item)
                    else:
                        child = ET.SubElement(parent, "item")
                        if item is not None:
                            child.text = str(item)
        
        root = ET.Element(root_name)
        dict_to_xml_elem(root, data)
        
        # Convert to string with proper formatting
        ET.indent(root, space="  ", level=0)
        return ET.tostring(root, encoding="unicode")









