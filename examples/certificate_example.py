#!/usr/bin/env python3
"""
Example script demonstrating JPAPI certificate management functionality
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli.commands.certificate_command import CertificateCommand
from cli.commands.crowdstrike_command import CrowdStrikeCommand


def demo_certificate_management():
    """Demonstrate certificate management functionality"""
    print("🔐 JPAPI Certificate Management Demo")
    print("=" * 50)

    # Create command instances
    cert_cmd = CertificateCommand()
    cs_cmd = CrowdStrikeCommand()

    print("\n1. Certificate Command Available Actions:")
    print(
        "   - jpapi certificate csr --common-name 'My Cert' --organization 'My Company'"
    )
    print("   - jpapi certificate manage --list")
    print("   - jpapi certificate sign --profile 'profile.mobileconfig'")

    print("\n2. CrowdStrike Command Available Actions:")
    print("   - jpapi crowdstrike create --type fda --name 'CrowdStrike FDA'")
    print("   - jpapi crowdstrike create --type pppc --name 'CrowdStrike PPPC'")
    print("   - jpapi crowdstrike sign --profile 'crowdstrike_fda.mobileconfig'")
    print("   - jpapi crowdstrike deploy --profile 'crowdstrike_fda.mobileconfig'")

    print("\n3. Integration with Jamf Pro's Built-in CA:")
    print("   - Generate CSR locally")
    print("   - Upload CSR to Jamf Pro for signing")
    print("   - Download signed certificate")
    print("   - Use certificate to sign configuration profiles")
    print("   - Deploy signed profiles to devices")

    print("\n4. CrowdStrike-Specific Features:")
    print("   - Pre-configured FDA profiles with proper code requirements")
    print("   - PPPC profiles for privacy preferences")
    print("   - Automated deployment to Jamf Pro")
    print("   - Integration with existing CrowdStrike infrastructure")

    print("\n✅ Demo completed! The certificate management functionality")
    print("   is now integrated into JPAPI and ready for use.")


def demo_crowdstrike_profile_creation():
    """Demonstrate CrowdStrike profile creation"""
    print("\n🛡️ CrowdStrike Profile Creation Demo")
    print("=" * 40)

    # This would normally create actual profile files
    print("Creating CrowdStrike FDA profile...")
    print("✅ Profile would be created with:")
    print("   - Proper code requirements for CrowdStrike Falcon")
    print("   - Full Disk Access permissions")
    print("   - System-level deployment scope")
    print("   - Automatic installation")

    print("\nCreating CrowdStrike PPPC profile...")
    print("✅ Profile would be created with:")
    print("   - Privacy preferences for CrowdStrike")
    print("   - Proper bundle identifier")
    print("   - Allow authorization")
    print("   - System-level deployment")


if __name__ == "__main__":
    demo_certificate_management()
    demo_crowdstrike_profile_creation()

    print("\n" + "=" * 60)
    print("🎉 JPAPI Certificate Management Integration Complete!")
    print("=" * 60)
    print("\nKey Features Added:")
    print("✅ CSR generation for Jamf Pro's built-in CA")
    print("✅ Certificate management and listing")
    print("✅ Profile signing with Jamf Pro certificates")
    print("✅ CrowdStrike-specific profile creation")
    print("✅ Automated profile deployment")
    print("✅ Integration with existing JPAPI architecture")

    print("\nNext Steps:")
    print("1. Install cryptography library: pip install cryptography")
    print("2. Configure Jamf Pro authentication: jpapi setup")
    print("3. Generate CSR: jpapi certificate csr --common-name 'My Cert'")
    print("4. Create CrowdStrike profile: jpapi crowdstrike create --type fda")
    print("5. Sign and deploy: jpapi crowdstrike sign --profile 'profile.mobileconfig'")


