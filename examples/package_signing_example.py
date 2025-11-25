#!/usr/bin/env python3
"""
Example script demonstrating JPAPI package signing functionality
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli.commands.certificate_command import CertificateCommand
from lib.utils.package_signer import PackageSigner


def demo_package_signing():
    """Demonstrate package signing functionality"""
    print("📦 JPAPI Package Signing Demo")
    print("=" * 50)

    # Example package path
    package_path = "/Users/charles.hetzel/Desktop/onboardingBundle-chetzel-20250914.pkg"

    print(f"\n🎯 Target Package: {package_path}")

    if os.path.exists(package_path):
        print("✅ Package found!")

        # Get package info
        signer = PackageSigner()
        pkg_info = signer.get_package_info(package_path)

        if pkg_info:
            print(f"\n📊 Package Information:")
            print(f"   📁 Size: {pkg_info['size']:,} bytes")
            print(f"   📅 Modified: {pkg_info['modified']}")
            print(f"   ✅ Currently Signed: {pkg_info['signed']}")

            if pkg_info.get("package_id"):
                print(f"   🆔 Package ID: {pkg_info['package_id']}")
            if pkg_info.get("version"):
                print(f"   📋 Version: {pkg_info['version']}")
    else:
        print("❌ Package not found at specified path")
        print("💡 Update the package_path variable with your actual package location")

    print("\n🔧 Available Commands:")
    print("=" * 30)

    print("\n1. Generate CSR for package signing:")
    print(
        "   jpapi certificate csr --common-name 'Package Signing Certificate' --organization 'Your Company'"
    )

    print("\n2. List available code signing identities:")
    print("   jpapi certificate manage --identities")

    print("\n3. Sign package with existing identity:")
    print(
        f"   jpapi certificate sign --package '{package_path}' --identity 'Developer ID Application: Your Name (ABC1234567)'"
    )

    print("\n4. Sign package with Jamf Pro certificate:")
    print(
        f"   jpapi certificate sign --package '{package_path}' --certificate-id '123'"
    )

    print("\n5. List certificates in Jamf Pro:")
    print("   jpapi certificate manage --list")

    print("\n6. Get certificate details:")
    print("   jpapi certificate manage --info '123'")


def demo_workflow():
    """Demonstrate complete package signing workflow"""
    print("\n🔄 Complete Package Signing Workflow")
    print("=" * 40)

    package_path = "/Users/charles.hetzel/Desktop/onboardingBundle-chetzel-20250914.pkg"

    print("\nStep 1: Check available signing identities")
    print("   jpapi certificate manage --identities")

    print("\nStep 2: Sign the package")
    print(
        f"   jpapi certificate sign --package '{package_path}' --identity 'Your Code Signing Identity'"
    )

    print("\nStep 3: Verify the signature")
    print("   codesign --verify --verbose /path/to/signed/package.pkg")

    print("\nStep 4: Upload to Jamf Pro (if needed)")
    print("   # Use existing JPAPI commands to upload the signed package")


if __name__ == "__main__":
    demo_package_signing()
    demo_workflow()

    print("\n" + "=" * 60)
    print("🎉 JPAPI Package Signing Integration Complete!")
    print("=" * 60)
    print("\nKey Features:")
    print("✅ CSR generation for Jamf Pro's built-in CA")
    print("✅ Package signing with code signing identities")
    print("✅ Package signing with Jamf Pro certificates")
    print("✅ Package information and verification")
    print("✅ Integration with existing JPAPI architecture")

    print("\nNext Steps:")
    print("1. Check available identities: jpapi certificate manage --identities")
    print(
        "2. Sign your package: jpapi certificate sign --package '/path/to/your.pkg' --identity 'Your Identity'"
    )
    print(
        "3. Verify signature: codesign --verify --verbose /path/to/signed/package.pkg"
    )


