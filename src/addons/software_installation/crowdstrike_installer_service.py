#!/usr/bin/env python3
"""
CrowdStrike Installer Service
Creates config profiles that install and execute CrowdStrike Falcon during enrollment
"""

import uuid
import base64
from typing import Optional, Dict, Any
from core.auth.login_types import AuthInterface
from .script_profile_service import ScriptProfileService


class CrowdStrikeInstallerService:
    """Service for creating CrowdStrike installation config profiles"""
    
    def __init__(self, auth: Optional[AuthInterface] = None):
        self.auth = auth
        self.script_service = ScriptProfileService(auth=auth)
    
    def create_crowdstrike_installation_profile(self,
                                                policy_event: str = "crowdstrikefalcon",
                                                use_policy: bool = True,
                                                customer_id: str = None,
                                                package_name: str = None,
                                                package_id: int = None,
                                                hide_app: bool = True,
                                                profile_name: str = None,
                                                description: str = None) -> Dict[str, Any]:
        """
        Create a config profile that installs CrowdStrike Falcon during enrollment
        
        Args:
            customer_id: CrowdStrike Customer ID (CID)
            package_name: Package name in Jamf Pro
            package_id: Package ID in Jamf Pro (optional, will be looked up if not provided)
            hide_app: Hide Falcon.app from users after installation
            profile_name: Custom profile name
            description: Profile description
        """
        
        if not profile_name:
            profile_name = "CrowdStrike Falcon - Pre-Login Installation"
        
        if not description:
            if use_policy:
                description = f"Triggers Jamf policy '{policy_event}' to install CrowdStrike Falcon during enrollment (pre-login)"
            else:
                description = "Installs and configures CrowdStrike Falcon during enrollment (pre-login)"
        
        # Create script - prefer policy trigger approach (more scalable)
        if use_policy:
            installation_script = self.create_policy_trigger_script(
                policy_event=policy_event,
                policy_description="CrowdStrike Falcon installation",
                verify_installation=True
            )
        else:
            # Fallback: direct installation script (less scalable)
            if not customer_id:
                raise ValueError("customer_id required when use_policy=False")
            installation_script = self._create_installation_script(
                customer_id=customer_id,
                package_name=package_name or "FalconSensorMacOS.MaverickGyr-1124.pkg",
                package_id=package_id,
                hide_app=hide_app
            )
        
        # Create script data structure (matching Jamf Pro format)
        script_name = f"CrowdStrike Falcon Policy Trigger - {policy_event}" if use_policy else "CrowdStrike Falcon Installation"
        script_data = {
            'name': script_name,
            'id': f'crowdstrike-{policy_event}',
            'script_contents': installation_script,
            'category': 'Security'
        }
        
        # Use script profile service to create profile with auto-execution
        mobileconfig = self.script_service.create_script_profile(
            script_data=script_data,
            profile_name=profile_name,
            description=description,
            auto_execute=True,
            execution_trigger="once"  # Run once during profile installation
        )
        
        return mobileconfig
    
    def create_policy_trigger_script(self,
                                    policy_event: str,
                                    policy_description: str = None,
                                    verify_installation: bool = True) -> str:
        """
        Create a simple script that triggers a Jamf policy
        
        This is the RECOMMENDED approach:
        - More scalable (one policy, multiple profiles can call it)
        - More maintainable (update policy once, all profiles benefit)
        - Better separation of concerns (profile triggers, policy executes)
        - Consistent with existing infrastructure
        
        Args:
            policy_event: Policy event name (e.g., "crowdstrikefalcon")
            policy_description: Human-readable description
            verify_installation: Verify installation after policy runs
        """
        
        if not policy_description:
            policy_description = policy_event.replace("-", " ").title()
        
        # Build script base
        script = f"""#!/bin/bash

###############################################################################
# Policy Trigger Script - {policy_description}
# This script triggers a Jamf Pro policy for installation
# Created by JPAPI
###############################################################################

set -e  # Exit on error

# Configuration
POLICY_EVENT="{policy_event}"
JAMFBIN="/usr/local/bin/jamf"
LOG_FILE="/var/log/policy_trigger_{policy_event}.log"
ERROR_LOG="/var/log/policy_trigger_{policy_event}_error.log"

logMessage() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}}

logError() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$ERROR_LOG" >&2
}}

logMessage "🚀 Triggering Jamf policy: $POLICY_EVENT"

# Check if jamf binary exists
if [ ! -f "$JAMFBIN" ]; then
    logError "❌ Jamf binary not found: $JAMFBIN"
    logError "   Policy cannot be triggered without Jamf binary"
    exit 1
fi

# Trigger the policy
logMessage "📞 Calling: jamf policy -event $POLICY_EVENT"
if "$JAMFBIN" policy -event "$POLICY_EVENT"; then
    logMessage "✅ Policy executed successfully: $POLICY_EVENT"
    
    # Wait a moment for installation to complete
    sleep 2
"""
        
        # Add verification code conditionally
        if verify_installation and "crowdstrike" in policy_event.lower():
            script += """    
    # Verify CrowdStrike installation
    if [ -d "/Applications/Falcon.app" ]; then
        logMessage "✅ CrowdStrike Falcon installation verified"
        if [ -f "/Applications/Falcon.app/Contents/Resources/falconctl" ]; then
            if /Applications/Falcon.app/Contents/Resources/falconctl stats > /dev/null 2>&1; then
                logMessage "✅ CrowdStrike Falcon is properly licensed and running"
            else
                logMessage "⚠️  CrowdStrike Falcon installed but not yet licensed"
            fi
        fi
    fi
"""
        else:
            script += """    
    # Installation verification skipped
"""
        
        script += """
    exit 0
else
    logError "❌ Policy execution failed: $POLICY_EVENT"
    exit 1
fi
"""
        
        return script
    
    def _create_installation_script(self,
                                   customer_id: str,
                                   package_name: str,
                                   package_id: int = None,
                                   hide_app: bool = True) -> str:
        """
        Create a comprehensive CrowdStrike installation script
        
        This script:
        1. Downloads package from Jamf Pro (or uses cached location)
        2. Installs the package
        3. Runs falconctl license
        4. Hides Falcon.app (optional)
        5. Verifies installation
        """
        
        # Build script
        script = f"""#!/bin/bash

###############################################################################
# CrowdStrike Falcon Pre-Login Installation Script
# This script installs CrowdStrike Falcon during enrollment (before user login)
# Created by JPAPI
###############################################################################

set -e  # Exit on error

# Configuration
CUSTOMER_ID="{customer_id}"
PACKAGE_NAME="{package_name}"
PACKAGE_ID="{package_id or 'auto-detect'}"
HIDE_APP={"true" if hide_app else "false"}

# Logging
LOG_FILE="/var/log/crowdstrike_install.log"
ERROR_LOG="/var/log/crowdstrike_install_error.log"

logMessage() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}}

logError() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$ERROR_LOG" >&2
}}

logMessage "🚀 Starting CrowdStrike Falcon installation..."

# Check if already installed
if [ -d "/Applications/Falcon.app" ]; then
    logMessage "✅ CrowdStrike Falcon already installed"
    
    # Verify license
    if [ -f "/Applications/Falcon.app/Contents/Resources/falconctl" ]; then
        /Applications/Falcon.app/Contents/Resources/falconctl stats > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            logMessage "✅ CrowdStrike Falcon is properly licensed and running"
            exit 0
        fi
    fi
fi

# Determine package location
PACKAGE_PATH=""
CACHED_LOCATION="/Library/Caches/JSS/$PACKAGE_NAME"

# Check Jamf Pro cached location first
if [ -f "$CACHED_LOCATION" ]; then
    PACKAGE_PATH="$CACHED_LOCATION"
    logMessage "📦 Found package in Jamf cache: $PACKAGE_PATH"
else
    # Try to download from Jamf Pro if package_id is provided
    if [ -n "$PACKAGE_ID" ] && [ "$PACKAGE_ID" != "auto-detect" ]; then
        logMessage "📥 Downloading package from Jamf Pro (ID: $PACKAGE_ID)..."
        # This would use jamf CLI if available, or curl to Jamf Pro API
        # For now, we'll use cached location or manual download
        if command -v jamf >/dev/null 2>&1; then
            jamf downloadInstallPackage -packageID "$PACKAGE_ID" -destination "/tmp/$PACKAGE_NAME"
            if [ -f "/tmp/$PACKAGE_NAME" ]; then
                PACKAGE_PATH="/tmp/$PACKAGE_NAME"
                logMessage "✅ Package downloaded to: $PACKAGE_PATH"
            fi
        fi
    fi
    
    # Fallback: check if package exists in common locations
    for location in "/tmp/$PACKAGE_NAME" "/var/folders/*/$PACKAGE_NAME"; do
        if [ -f "$location" ]; then
            PACKAGE_PATH="$location"
            logMessage "📦 Found package at: $PACKAGE_PATH"
            break
        fi
    done
fi

# Verify package exists
if [ -z "$PACKAGE_PATH" ] || [ ! -f "$PACKAGE_PATH" ]; then
    logError "❌ Package not found: $PACKAGE_NAME"
    logError "   Checked locations:"
    logError "     - $CACHED_LOCATION"
    logError "     - /tmp/$PACKAGE_NAME"
    logError "   Please ensure package is available before profile installation"
    exit 1
fi

# Verify package integrity
logMessage "🔍 Verifying package integrity..."
if ! installer -pkg "$PACKAGE_PATH" -tgt /tmp -dumplog > /dev/null 2>&1; then
    logError "❌ Package verification failed: $PACKAGE_PATH"
    exit 1
fi
logMessage "✅ Package verification passed"

# Install the package
logMessage "📦 Installing CrowdStrike Falcon package..."
if ! installer -verboseR -pkg "$PACKAGE_PATH" -target /; then
    logError "❌ Package installation failed"
    exit 1
fi
logMessage "✅ Package installed successfully"

# Wait for Falcon.app to be available
logMessage "⏳ Waiting for Falcon.app to be available..."
MAX_WAIT=30
WAIT_COUNT=0
while [ ! -f "/Applications/Falcon.app/Contents/Resources/falconctl" ] && [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

if [ ! -f "/Applications/Falcon.app/Contents/Resources/falconctl" ]; then
    logError "❌ falconctl not found after installation"
    exit 1
fi
logMessage "✅ Falcon.app is available"

# Apply license
logMessage "🔑 Applying CrowdStrike license (CID: $CUSTOMER_ID)..."
if ! /Applications/Falcon.app/Contents/Resources/falconctl license "$CUSTOMER_ID"; then
    logError "❌ License application failed"
    exit 1
fi
logMessage "✅ License applied successfully"

# Hide Falcon.app from users (optional)
if [ "$HIDE_APP" = "true" ]; then
    logMessage "👁️  Hiding Falcon.app from users..."
    chflags hidden /Applications/Falcon.app 2>/dev/null || true
    logMessage "✅ Falcon.app hidden"
fi

# Verify installation and license
logMessage "🔍 Verifying installation..."
sleep 2  # Give Falcon a moment to initialize
if /Applications/Falcon.app/Contents/Resources/falconctl stats > /dev/null 2>&1; then
    logMessage "✅ CrowdStrike Falcon is properly installed and licensed"
    logMessage "📊 Falcon Status:"
    /Applications/Falcon.app/Contents/Resources/falconctl stats | head -5 | while read line; do
        logMessage "   $line"
    done
else
    logError "⚠️  Installation complete but verification failed"
    logError "   Falcon may need a moment to initialize"
fi

# Cleanup
if [ -f "/tmp/$PACKAGE_NAME" ] && [ "$PACKAGE_PATH" != "$CACHED_LOCATION" ]; then
    rm -f "/tmp/$PACKAGE_NAME"
    logMessage "🧹 Cleaned up temporary package file"
fi

logMessage "🎉 CrowdStrike Falcon installation complete!"
exit 0
"""
        
        return script
    
    def download_script_and_create_profile(self,
                                         script_id: int,
                                         customer_id: str = None,
                                         package_name: str = None,
                                         profile_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Download existing CrowdStrike installation script and enhance it for config profile deployment
        
        Args:
            script_id: Jamf Pro script ID (e.g., 50)
            customer_id: CrowdStrike Customer ID (overrides script if provided)
            package_name: Package name (overrides script if provided)
            profile_name: Custom profile name
        """
        
        # Download script
        script_data = self.script_service.download_script(script_id)
        if not script_data:
            return None
        
        # Extract customer ID from script if not provided
        script_content = script_data.get('script_contents', '')
        if not customer_id:
            # Try to extract from script
            import re
            cid_match = re.search(r'customerID\s*=\s*["\']([^"\']+)["\']', script_content)
            if cid_match:
                customer_id = cid_match.group(1)
            else:
                print("❌ Customer ID not found in script and not provided")
                return None
        
        # Extract package name if not provided
        if not package_name:
            pkg_match = re.search(r'FalconSensorMacOS[^"\']+\.pkg', script_content)
            if pkg_match:
                package_name = pkg_match.group(0)
            else:
                package_name = "FalconSensorMacOS.MaverickGyr-1124.pkg"
        
        # Create enhanced installation script
        enhanced_script_data = script_data.copy()
        enhanced_script_data['script_contents'] = self._create_installation_script(
            customer_id=customer_id,
            package_name=package_name,
            hide_app=True
        )
        
        # Create profile
        if not profile_name:
            profile_name = f"{script_data.get('name', 'CrowdStrike Installation')} Profile"
        
        mobileconfig = self.script_service.create_script_profile(
            script_data=enhanced_script_data,
            profile_name=profile_name,
            description="CrowdStrike Falcon installation via config profile (pre-login)",
            auto_execute=True,
            execution_trigger="once"
        )
        
        return mobileconfig
    
    def deploy_crowdstrike_profile(self,
                                 policy_event: str = "crowdstrikefalcon",
                                 use_policy: bool = True,
                                 customer_id: str = None,
                                 package_name: str = None,
                                 package_id: int = None,
                                 deploy: bool = True,
                                 profile_name: str = None) -> bool:
        """
        Create and deploy CrowdStrike installation profile
        
        Args:
            customer_id: CrowdStrike Customer ID
            package_name: Package name in Jamf Pro
            package_id: Package ID (optional)
            deploy: Deploy to Jamf Pro (True) or save locally (False)
            profile_name: Custom profile name
        """
        
        try:
            # Create profile
            mobileconfig = self.create_crowdstrike_installation_profile(
                policy_event=policy_event or "crowdstrikefalcon",
                use_policy=use_policy,
                customer_id=customer_id,
                package_name=package_name,
                package_id=package_id,
                profile_name=profile_name
            )
            
            # Deploy or save
            if deploy:
                return self.script_service._deploy_mobileconfig(
                    mobileconfig,
                    profile_name or "CrowdStrike Falcon - Pre-Login Installation"
                )
            else:
                return self.script_service._save_mobileconfig_locally(
                    mobileconfig,
                    profile_name or "CrowdStrike Falcon - Pre-Login Installation"
                )
                
        except Exception as e:
            print(f"❌ Error creating CrowdStrike profile: {e}")
            return False
