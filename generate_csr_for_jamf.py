#!/usr/bin/env python3
"""
Generate a proper CSR for Jamf Pro's built-in CA
Following the directions from: https://learn.jamf.com/en-US/bundle/technical-articles/page/Creating_a_Signing_Certificate_Using_Jamf_Pros_Built-in_CA_to_Use_for_Signing_Configuration_Profiles_and_Packages.html
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime


def generate_csr_for_jamf():
    """Generate a proper CSR for Jamf Pro's built-in CA"""

    print("🔐 Generating CSR for Jamf Pro's Built-in CA")
    print("=" * 50)

    # Certificate details - UPDATE THESE FOR YOUR ORGANIZATION
    common_name = "Code Signing Certificate"
    organization = "Your Organization"
    organizational_unit = "IT Department"
    country = "US"
    state = "Your State"
    city = "Your City"
    email = "admin@example.com"

    # File paths
    csr_file = "Code_Signing_Certificate_csr.pem"
    key_file = "Code_Signing_Certificate_private_key.pem"

    print(f"📋 Certificate Details:")
    print(f"   Common Name: {common_name}")
    print(f"   Organization: {organization}")
    print(f"   Organizational Unit: {organizational_unit}")
    print(f"   Country: {country}")
    print(f"   State: {state}")
    print(f"   City: {city}")
    print(f"   Email: {email}")
    print()

    # Create the CSR using openssl
    try:
        # Generate private key
        print("🔑 Generating private key...")
        key_cmd = ["openssl", "genrsa", "-out", key_file, "2048"]
        result = subprocess.run(key_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Error generating private key: {result.stderr}")
            return False

        print(f"✅ Private key generated: {key_file}")

        # Generate CSR
        print("📝 Generating Certificate Signing Request...")

        # Create subject string
        subject = f"/C={country}/ST={state}/L={city}/O={organization}/OU={organizational_unit}/CN={common_name}/emailAddress={email}"

        csr_cmd = [
            "openssl",
            "req",
            "-new",
            "-key",
            key_file,
            "-out",
            csr_file,
            "-subj",
            subject,
        ]

        result = subprocess.run(csr_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Error generating CSR: {result.stderr}")
            return False

        print(f"✅ CSR generated: {csr_file}")

        # Verify the CSR
        print("🔍 Verifying CSR...")
        verify_cmd = ["openssl", "req", "-in", csr_file, "-text", "-noout"]
        result = subprocess.run(verify_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ CSR verification successful")

            # Show CSR details
            print("\n📄 CSR Details:")
            print("-" * 30)
            subject_line = None
            for line in result.stdout.split("\n"):
                if "Subject:" in line:
                    subject_line = line.strip()
                    break

            if subject_line:
                print(subject_line)
            else:
                print("Subject information not found")
        else:
            print(f"⚠️ CSR verification failed: {result.stderr}")

        print(f"\n📁 Generated Files:")
        print(f"   📄 CSR: {csr_file}")
        print(f"   🔑 Private Key: {key_file}")

        print(f"\n📋 Next Steps:")
        print(f"1. Upload {csr_file} to Jamf Pro's built-in CA")
        print(f"2. Download the signed certificate from Jamf Pro")
        print(f"3. Import both the certificate and private key into your keychain")
        print(f"4. Use the certificate for package signing")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = generate_csr_for_jamf()
    if success:
        print("\n🎉 CSR generation completed successfully!")
    else:
        print("\n❌ CSR generation failed!")


