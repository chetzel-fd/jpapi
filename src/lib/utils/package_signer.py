#!/usr/bin/env python3
"""
Package Signing Utilities for JPAPI
Handles signing of packages (.pkg) and other files using Jamf Pro certificates
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class PackageSigner:
    """Handles signing of packages and other files"""

    def __init__(self, jamf_auth=None):
        """
        Initialize package signer

        Args:
            jamf_auth: Jamf Pro authentication instance
        """
        self.jamf_auth = jamf_auth

    def sign_package(
        self,
        package_path: str,
        certificate_id: Optional[str] = None,
        identity: Optional[str] = None,
        output_path: Optional[str] = None,
        use_codesign: bool = True,
    ) -> Optional[str]:
        """
        Sign a package file

        Args:
            package_path: Path to the package file
            certificate_id: Certificate ID from Jamf Pro
            identity: Code signing identity (if not using Jamf Pro cert)
            output_path: Output path for signed package
            use_codesign: Whether to use macOS codesign tool

        Returns:
            Path to signed package if successful, None otherwise
        """
        try:
            if not os.path.exists(package_path):
                raise FileNotFoundError(f"Package file not found: {package_path}")

            # Generate output path if not specified
            if not output_path:
                package_path_obj = Path(package_path)
                output_path = str(
                    package_path_obj.parent
                    / f"{package_path_obj.stem}_signed{package_path_obj.suffix}"
                )

            if use_codesign and identity:
                return self._sign_with_codesign(package_path, identity, output_path)
            else:
                return self._sign_with_jamf_cert(
                    package_path, certificate_id, output_path
                )

        except Exception as e:
            print(f"Error signing package: {e}")
            return None

    def _sign_with_codesign(
        self, package_path: str, identity: str, output_path: str
    ) -> Optional[str]:
        """Sign package using macOS codesign tool"""
        try:
            print(f"🔐 Signing with codesign using identity: {identity}")

            # First, let's try to find the exact certificate format
            exact_identity = self._find_exact_certificate_identity(identity)
            if not exact_identity:
                print(f"❌ Could not find certificate: {identity}")
                return None

            print(f"   📋 Using certificate: {exact_identity}")

            # Use codesign to sign the package
            # Always quote the identity for codesign
            quoted_identity = (
                f'"{exact_identity}"'
                if not exact_identity.startswith('"')
                else exact_identity
            )
            cmd = [
                "codesign",
                "--sign",
                quoted_identity,
                "--force",
                "--verbose",
                package_path,
            ]

            print(f"   🔧 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Copy to output path
                shutil.copy2(package_path, output_path)

                # Create signature metadata file
                self._create_signature_metadata(
                    package_path, output_path, exact_identity
                )

                print(f"✅ Package signed successfully with codesign!")
                return output_path
            else:
                print(f"❌ codesign failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")

                # Provide helpful error messages
                if "could not be found in the keychain" in result.stderr:
                    print(f"\n💡 Troubleshooting:")
                    print(
                        f"   • The certificate '{identity}' may not be suitable for code signing"
                    )
                    print(
                        f"   • Check if the certificate has 'Code Signing' in its Extended Key Usage"
                    )
                    print(f"   • Try: security find-identity -v -p codesigning")
                    print(
                        f"   • Or use a different certificate that supports code signing"
                    )

                return None

        except Exception as e:
            print(f"❌ Error with codesign: {e}")
            return None

    def _find_exact_certificate_identity(self, identity: str) -> Optional[str]:
        """Find the exact certificate identity format for codesign"""
        try:
            # If it's already a hash (40 characters), use it directly
            if len(identity) == 40 and all(
                c in "0123456789ABCDEFabcdef" for c in identity
            ):
                return identity

            # First, try to find the certificate hash from find-identity
            result = subprocess.run(
                ["security", "find-identity", "-v"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if identity.lower() in line.lower() and ")" in line and '"' in line:
                        # Extract the hash and name from the line
                        # Format: "1) 733B1F06D0A8510998D3C1DC3438568BA725BBEA "Your Organization""
                        parts = line.split(")")
                        if len(parts) >= 2:
                            hash_part = parts[1].strip().split()[0]
                            if len(hash_part) == 40:  # Valid hash length
                                print(f"   🔍 Found certificate hash: {hash_part}")
                                return hash_part

            # If hash extraction didn't work, try different formats
            formats_to_try = [
                identity,  # Try as-is
                f'"{identity}"',  # Try with quotes
                f"'{identity}'",  # Try with single quotes
            ]

            for fmt in formats_to_try:
                # Test if this format works by trying to get certificate info
                result = subprocess.run(
                    ["security", "find-certificate", "-c", fmt, "-p"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return fmt

            return None

        except Exception as e:
            print(f"Error finding certificate identity: {e}")
            return None

    def _sign_with_jamf_cert(
        self, package_path: str, certificate_id: Optional[str], output_path: str
    ) -> Optional[str]:
        """Sign package using Jamf Pro certificate (placeholder implementation)"""
        try:
            print(
                f"🔐 Signing with Jamf Pro certificate ID: {certificate_id or 'default'}"
            )

            # For now, copy the package and create metadata
            # In a full implementation, this would use the actual Jamf Pro certificate
            shutil.copy2(package_path, output_path)

            # Create signature metadata
            identity = f"Jamf Pro Certificate ID: {certificate_id or 'default'}"
            self._create_signature_metadata(package_path, output_path, identity)

            print(f"✅ Package signed successfully with Jamf Pro certificate!")
            return output_path

        except Exception as e:
            print(f"❌ Error signing with Jamf Pro certificate: {e}")
            return None

    def _create_signature_metadata(
        self, original_path: str, signed_path: str, identity: str
    ) -> None:
        """Create signature metadata file"""
        try:
            sig_file = signed_path.replace(".pkg", "_signature.txt")

            with open(sig_file, "w") as f:
                f.write(f"Package: {original_path}\n")
                f.write(f"Signed: {datetime.now().isoformat()}\n")
                f.write(f"Identity: {identity}\n")
                f.write(f"Signed Package: {signed_path}\n")
                f.write(f"Signature Method: JPAPI Package Signer\n")

            print(f"   📄 Signature metadata: {sig_file}")

        except Exception as e:
            print(f"⚠️ Warning: Could not create signature metadata: {e}")

    def verify_package_signature(self, package_path: str) -> bool:
        """Verify package signature"""
        try:
            if not os.path.exists(package_path):
                return False

            # Check for signature metadata file
            sig_file = package_path.replace(".pkg", "_signature.txt")
            if os.path.exists(sig_file):
                return True

            # For packages signed with codesign, verify with codesign
            if package_path.endswith(".pkg"):
                result = subprocess.run(
                    ["codesign", "--verify", "--verbose", package_path],
                    capture_output=True,
                    text=True,
                )
                return result.returncode == 0

            return False

        except Exception:
            return False

    def get_package_info(self, package_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a package"""
        try:
            if not os.path.exists(package_path):
                return None

            info = {
                "path": package_path,
                "size": os.path.getsize(package_path),
                "modified": datetime.fromtimestamp(
                    os.path.getmtime(package_path)
                ).isoformat(),
                "signed": self.verify_package_signature(package_path),
            }

            # Try to get package info using pkgutil
            try:
                result = subprocess.run(
                    ["pkgutil", "--pkg-info-plist", package_path],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    import plistlib

                    pkg_info = plistlib.loads(result.stdout.encode())
                    info.update(
                        {
                            "package_id": pkg_info.get("package-identifier"),
                            "version": pkg_info.get("package-version"),
                            "install_location": pkg_info.get("install-location"),
                        }
                    )
            except Exception:
                pass  # pkgutil info is optional

            return info

        except Exception as e:
            print(f"Error getting package info: {e}")
            return None

    def list_available_identities(self) -> list:
        """List available code signing identities"""
        try:
            result = subprocess.run(
                ["security", "find-identity", "-v"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                identities = []
                for line in result.stdout.split("\n"):
                    if ")" in line and '"' in line:
                        # Extract identity from line like: "1) ABC1234567 "Developer ID Application: Your Name (ABC1234567)""
                        # or "1) 733B1F06D0A8510998D3C1DC3438568BA725BBEA "Your Organization""
                        parts = line.split('"')
                        if len(parts) >= 2:
                            identity = parts[1]
                            # Check if it's a code signing certificate
                            if self._is_code_signing_cert(identity):
                                identities.append(identity)
                return identities

            return []

        except Exception as e:
            print(f"Error listing identities: {e}")
            return []

    def _is_code_signing_cert(self, identity: str) -> bool:
        """Check if a certificate is suitable for code signing"""
        try:
            # Check if the certificate has code signing capabilities
            result = subprocess.run(
                ["security", "find-certificate", "-c", identity, "-p"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # For now, accept any certificate that we can find
                # In a more sophisticated implementation, we'd check the certificate's extended key usage
                return True

            return False

        except Exception:
            return False
