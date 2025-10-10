#!/usr/bin/env python3
"""
Profile Data Analyzers for jpapi CLI
Follows SOLID principles with separate analyzers for different aspects
"""

from typing import Dict, Any, List
from abc import ABC, abstractmethod


class ProfileAnalyzer(ABC):
    """Abstract base class for profile analyzers"""
    
    @abstractmethod
    def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze profile data and return insights"""
        pass


class PayloadAnalyzer(ProfileAnalyzer):
    """Analyzes configuration profile payloads"""
    
    def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze payload configuration and types"""
        payloads = profile_data.get("payloads", [])
        if not payloads:
            return {"Payload Analysis": "No payloads found"}
        
        analysis = {
            "Total Payloads": len(payloads),
            "Payload Types": [],
            "Security Payloads": [],
            "System Payloads": [],
            "Application Payloads": [],
            "Network Payloads": [],
            "Certificate Payloads": [],
        }
        
        for payload in payloads:
            payload_type = payload.get("PayloadType", "Unknown")
            analysis["Payload Types"].append(payload_type)
            
            # Categorize payloads by type
            self._categorize_payload(payload, analysis)
        
        # Convert lists to counts and unique types
        analysis["Unique Payload Types"] = len(set(analysis["Payload Types"]))
        analysis["Security Payload Count"] = len(analysis["Security Payloads"])
        analysis["System Payload Count"] = len(analysis["System Payloads"])
        analysis["Application Payload Count"] = len(analysis["Application Payloads"])
        analysis["Network Payload Count"] = len(analysis["Network Payloads"])
        analysis["Certificate Payload Count"] = len(analysis["Certificate Payloads"])
        
        # Clean up lists, keep only unique types
        analysis["Security Payload Types"] = ", ".join(set(analysis["Security Payloads"]))
        analysis["System Payload Types"] = ", ".join(set(analysis["System Payloads"]))
        analysis["Application Payload Types"] = ", ".join(set(analysis["Application Payloads"]))
        analysis["Network Payload Types"] = ", ".join(set(analysis["Network Payloads"]))
        analysis["Certificate Payload Types"] = ", ".join(set(analysis["Certificate Payloads"]))
        
        # Remove the list fields
        for key in ["Payload Types", "Security Payloads", "System Payloads", 
                   "Application Payloads", "Network Payloads", "Certificate Payloads"]:
            del analysis[key]
        
        return analysis
    
    def _categorize_payload(self, payload: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Categorize individual payload"""
        payload_type = payload.get("PayloadType", "").lower()
        
        if any(sec_type in payload_type for sec_type in 
               ["pppc", "systempolicy", "applicationaccess", "security", "kernelextension"]):
            analysis["Security Payloads"].append(payload.get("PayloadType", "Unknown"))
        elif any(sys_type in payload_type for sys_type in 
                 ["system", "loginwindow", "screensaver", "preference", "systemextension"]):
            analysis["System Payloads"].append(payload.get("PayloadType", "Unknown"))
        elif any(app_type in payload_type for app_type in 
                 ["application", "managedapp", "appstore", "vpp"]):
            analysis["Application Payloads"].append(payload.get("PayloadType", "Unknown"))
        elif any(net_type in payload_type for net_type in 
                 ["network", "wifi", "vpn", "cellular", "apn"]):
            analysis["Network Payloads"].append(payload.get("PayloadType", "Unknown"))
        elif any(cert_type in payload_type for cert_type in 
                 ["certificate", "pkcs", "scep", "credential"]):
            analysis["Certificate Payloads"].append(payload.get("PayloadType", "Unknown"))


class ScopeAnalyzer(ProfileAnalyzer):
    """Analyzes profile scope and targeting"""
    
    def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze profile scope and targeting configuration"""
        scope = profile_data.get("scope", {})
        
        analysis = {
            "Scope All Devices": scope.get("all_computers", False) or scope.get("all_mobile_devices", False),
            "Target Computer Groups": len(scope.get("computer_groups", []) or scope.get("mobile_device_groups", [])),
            "Target Computers": len(scope.get("computers", []) or scope.get("mobile_devices", [])),
            "Target Buildings": len(scope.get("buildings", [])),
            "Target Departments": len(scope.get("departments", [])),
            "Target Users": len(scope.get("jss_users", [])),
            "Target User Groups": len(scope.get("jss_user_groups", {})),
        }
        
        # Analyze exclusions
        exclusions = scope.get("exclusions", {})
        analysis.update({
            "Excluded Computers": len(exclusions.get("computers", []) or exclusions.get("mobile_devices", [])),
            "Excluded Groups": len(exclusions.get("computer_groups", []) or exclusions.get("mobile_device_groups", [])),
            "Excluded Users": len(exclusions.get("jss_users", [])),
            "Excluded User Groups": len(exclusions.get("jss_user_groups", [])),
            "Excluded Buildings": len(exclusions.get("buildings", [])),
            "Excluded Departments": len(exclusions.get("departments", [])),
        })
        
        # Analyze limitations
        limitations = scope.get("limitations", {})
        analysis.update({
            "Limited Users": len(limitations.get("users", [])),
            "Limited User Groups": len(limitations.get("user_groups", [])),
            "Limited Network Segments": len(limitations.get("network_segments", [])),
            "Limited iBeacons": len(limitations.get("ibeacons", [])),
        })
        
        # Add names for context (first 5 of each)
        analysis.update(self._extract_names(scope, exclusions))
        
        return analysis
    
    def _extract_names(self, scope: Dict[str, Any], exclusions: Dict[str, Any]) -> Dict[str, str]:
        """Extract names for context"""
        names = {}
        
        # Target names
        computer_groups = scope.get("computer_groups", []) or scope.get("mobile_device_groups", [])
        buildings = scope.get("buildings", [])
        departments = scope.get("departments", [])
        
        names["Computer Group Names"] = ", ".join([g.get("name", "") for g in computer_groups[:5]])
        names["Building Names"] = ", ".join([b.get("name", "") for b in buildings[:5]])
        names["Department Names"] = ", ".join([d.get("name", "") for d in departments[:5]])
        
        # Exclusion names
        excluded_groups = exclusions.get("computer_groups", []) or exclusions.get("mobile_device_groups", [])
        excluded_buildings = exclusions.get("buildings", [])
        excluded_departments = exclusions.get("departments", [])
        
        names["Excluded Group Names"] = ", ".join([g.get("name", "") for g in excluded_groups[:5]])
        names["Excluded Building Names"] = ", ".join([b.get("name", "") for b in excluded_buildings[:5]])
        names["Excluded Department Names"] = ", ".join([d.get("name", "") for d in excluded_departments[:5]])
        
        return names


class SecurityAnalyzer(ProfileAnalyzer):
    """Analyzes security aspects of configuration profiles"""
    
    def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security configuration"""
        payloads = profile_data.get("payloads", [])
        
        analysis = {
            "Has PPPC": False,
            "Has System Extensions": False,
            "Has Kernel Extensions": False,
            "Has Restrictions": False,
            "Has FileVault": False,
            "Has VPN": False,
            "Has WiFi": False,
            "Has Certificates": False,
            "Security Level": "None",
            "Compliance Score": 0,
        }
        
        # Analyze payloads for security features
        security_features = []
        for payload in payloads:
            payload_type = payload.get("PayloadType", "").lower()
            display_name = payload.get("PayloadDisplayName", "").lower()
            
            if "pppc" in payload_type:
                analysis["Has PPPC"] = True
                security_features.append("PPPC")
            if "systemextension" in payload_type:
                analysis["Has System Extensions"] = True
                security_features.append("System Extensions")
            if "kernelextension" in payload_type:
                analysis["Has Kernel Extensions"] = True
                security_features.append("Kernel Extensions")
            if "applicationaccess" in payload_type:
                analysis["Has Restrictions"] = True
                security_features.append("Restrictions")
            if "filevault" in display_name:
                analysis["Has FileVault"] = True
                security_features.append("FileVault")
            if "vpn" in payload_type or "vpn" in display_name:
                analysis["Has VPN"] = True
                security_features.append("VPN")
            if "wifi" in payload_type or "wifi" in display_name:
                analysis["Has WiFi"] = True
                security_features.append("WiFi")
            if any(cert_type in payload_type for cert_type in ["certificate", "pkcs", "scep"]):
                analysis["Has Certificates"] = True
                security_features.append("Certificates")
        
        # Calculate security level and compliance score
        analysis["Security Level"] = self._calculate_security_level(payloads, security_features)
        analysis["Compliance Score"] = self._calculate_compliance_score(security_features)
        analysis["Security Features"] = ", ".join(set(security_features))
        
        return analysis
    
    def _calculate_security_level(self, payloads: List[Dict[str, Any]], security_features: List[str]) -> str:
        """Calculate overall security level"""
        if not payloads:
            return "None"
        
        security_ratio = len(set(security_features)) / len(payloads)
        
        if security_ratio >= 0.7:
            return "High"
        elif security_ratio >= 0.3:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_compliance_score(self, security_features: List[str]) -> int:
        """Calculate compliance score based on security features"""
        score = 0
        feature_weights = {
            "PPPC": 20,
            "System Extensions": 15,
            "Kernel Extensions": 15,
            "Restrictions": 10,
            "FileVault": 25,
            "VPN": 10,
            "WiFi": 5,
            "Certificates": 15,
        }
        
        for feature in set(security_features):
            score += feature_weights.get(feature, 5)
        
        return min(score, 100)  # Cap at 100


class SelfServiceAnalyzer(ProfileAnalyzer):
    """Analyzes self service configuration"""
    
    def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze self service configuration"""
        self_service = profile_data.get("self_service", {})
        
        return {
            "Self Service Enabled": bool(self_service.get("self_service_display_name")),
            "Self Service Name": self_service.get("self_service_display_name", ""),
            "Install Button Text": self_service.get("install_button_text", ""),
            "User Licensed": self_service.get("user_licensed", False),
            "Feature on Main Page": self_service.get("feature_on_main_page", False),
            "Self Service Description": self_service.get("self_service_description", ""),
            "Self Service Icon": self_service.get("self_service_icon", {}).get("filename", ""),
            "Self Service Category": self_service.get("self_service_category", {}).get("name", ""),
        }


class ProfileAnalyzerFactory:
    """Factory for creating profile analyzers"""
    
    @staticmethod
    def create_analyzers() -> List[ProfileAnalyzer]:
        """Create all available analyzers"""
        return [
            PayloadAnalyzer(),
            ScopeAnalyzer(),
            SecurityAnalyzer(),
            SelfServiceAnalyzer(),
        ]
    
    @staticmethod
    def analyze_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all analyzers on profile data"""
        analyzers = ProfileAnalyzerFactory.create_analyzers()
        results = {}
        
        for analyzer in analyzers:
            analyzer_name = analyzer.__class__.__name__.replace("Analyzer", "")
            analysis = analyzer.analyze(profile_data)
            results.update(analysis)
        
        return results
