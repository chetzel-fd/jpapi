#!/usr/bin/env python3
"""
Download GlobalProtect installer from FanDuel portal with Okta authentication.

This script authenticates to Okta and downloads the GlobalProtect.pkg file.
Supports interactive login and MFA.
"""

import os
import sys
import argparse
import getpass
from pathlib import Path
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class OktaAuthenticator:
    """Handle Okta authentication and session management."""

    def __init__(self, okta_url: str, download_url: str):
        self.okta_url = okta_url
        self.download_url = download_url
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set user agent
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

    def authenticate_with_selenium(self, username: str, password: str) -> bool:
        """Authenticate using Selenium for browser-based Okta login."""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available. Install with: pip install selenium")
            return False

        print("🌐 Opening browser for Okta authentication...")

        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")  # Use new headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        try:
            driver = webdriver.Chrome(options=options)
            driver.get(self.okta_url)

            print("📝 Please complete authentication in the browser...")
            print(
                "   (If headless mode doesn't work, the script will prompt for manual cookie input)"
            )

            # Wait for login form
            try:
                username_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "okta-signin-username"))
                )
                username_field.send_keys(username)

                password_field = driver.find_element(By.ID, "okta-signin-password")
                password_field.send_keys(password)

                submit_button = driver.find_element(By.ID, "okta-signin-submit")
                submit_button.click()

                # Wait for MFA or redirect
                print("⏳ Waiting for authentication to complete...")
                WebDriverWait(driver, 60).until(
                    lambda d: "okta" not in d.current_url.lower()
                    or "mfa" in d.current_url.lower()
                    or "verify" in d.current_url.lower()
                )

                # Handle MFA if needed
                if (
                    "mfa" in driver.current_url.lower()
                    or "verify" in driver.current_url.lower()
                ):
                    print("🔐 MFA required. Please complete MFA in the browser...")
                    input("Press Enter after completing MFA...")

                # Wait for final redirect
                WebDriverWait(driver, 30).until(
                    lambda d: "secure.fanduel.com" in d.current_url.lower()
                )

                # Extract cookies
                cookies = driver.get_cookies()
                for cookie in cookies:
                    self.session.cookies.set(
                        cookie["name"], cookie["value"], domain=cookie.get("domain")
                    )

                print("✅ Authentication successful!")
                driver.quit()
                return True

            except TimeoutException:
                print(
                    "⏱️  Timeout waiting for authentication. Trying manual cookie method..."
                )
                driver.quit()
                return False

        except Exception as e:
            print(f"❌ Selenium authentication failed: {e}")
            return False

    def authenticate_manual(self) -> bool:
        """Manual authentication - user provides cookies or session info."""
        print("\n📋 Manual Authentication Method")
        print("=" * 50)
        print("1. Open your browser and navigate to:")
        print(f"   {self.okta_url}")
        print("\n2. Complete the Okta login (including MFA if required)")
        print("\n3. After successful login, open browser developer tools (F12)")
        print("4. Go to Application/Storage > Cookies")
        print("5. Find cookies for 'secure.fanduel.com'")
        print("\nAlternatively, you can:")
        print("   - Copy the 'Cookie' header from a successful request")
        print("   - Or use browser extension to export cookies")
        print("\n" + "=" * 50)

        cookie_string = input(
            "\nPaste the Cookie header value (or press Enter to skip): "
        ).strip()

        if cookie_string:
            # Parse cookie string
            for item in cookie_string.split(";"):
                item = item.strip()
                if "=" in item:
                    name, value = item.split("=", 1)
                    self.session.cookies.set(
                        name.strip(), value.strip(), domain="secure.fanduel.com"
                    )
            return True

        return False

    def download_globalprotect(self, output_path: Optional[Path] = None) -> bool:
        """Download GlobalProtect.pkg using authenticated session."""
        if output_path is None:
            output_path = Path.home() / "Downloads" / "GlobalProtect.pkg"

        print(f"\n📥 Downloading GlobalProtect.pkg to {output_path}...")

        try:
            # First, try to get the redirect URL
            response = self.session.get(
                self.download_url, allow_redirects=False, timeout=30
            )

            # Check if we need to follow redirects
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get("Location")
                if redirect_url:
                    if not redirect_url.startswith("http"):
                        redirect_url = f"https://secure.fanduel.com{redirect_url}"
                    print(f"🔄 Following redirect to: {redirect_url}")
                    response = self.session.get(redirect_url, timeout=30)

            # Handle JavaScript redirect in HTML
            if response.status_code == 200 and "text/html" in response.headers.get(
                "Content-Type", ""
            ):
                content = response.text
                if "GlobalProtect.pkg" in content or "window.location" in content:
                    # Try to extract the actual download URL
                    import re

                    match = re.search(
                        r'["\']([^"\']*GlobalProtect\.pkg[^"\']*)["\']', content
                    )
                    if match:
                        pkg_url = match.group(1)
                        if not pkg_url.startswith("http"):
                            pkg_url = f"https://secure.fanduel.com/global-protect/{pkg_url.lstrip('/')}"
                        print(f"🔗 Found package URL: {pkg_url}")
                        response = self.session.get(pkg_url, timeout=60, stream=True)

            # Download the file
            if response.status_code == 200:
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "wb") as f:
                    if total_size == 0:
                        # No content-length header, download normally
                        f.write(response.content)
                    else:
                        # Stream download with progress
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    print(
                                        f"\r📥 Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)",
                                        end="",
                                        flush=True,
                                    )

                print(f"\n✅ Successfully downloaded: {output_path}")
                print(f"   File size: {output_path.stat().st_size:,} bytes")
                return True
            else:
                print(f"❌ Download failed. Status code: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Download error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Download GlobalProtect installer with Okta authentication"
    )
    parser.add_argument(
        "--okta-url",
        default="https://fanduel.okta.com",
        help="Okta login URL (default: https://fanduel.okta.com)",
    )
    parser.add_argument(
        "--download-url",
        default="https://secure.fanduel.com/global-protect/getmsi.esp?version=none&platform=mac",
        help="GlobalProtect download URL",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path for downloaded .pkg file (default: ~/Downloads/GlobalProtect.pkg)",
    )
    parser.add_argument(
        "--username", "-u", help="Okta username (will prompt if not provided)"
    )
    parser.add_argument(
        "--password",
        "-p",
        help="Okta password (will prompt if not provided - not recommended)",
    )
    parser.add_argument(
        "--method",
        choices=["selenium", "manual"],
        default="selenium" if SELENIUM_AVAILABLE else "manual",
        help="Authentication method (default: selenium if available, else manual)",
    )

    args = parser.parse_args()

    print("🔐 GlobalProtect Downloader with Okta Authentication")
    print("=" * 60)

    # Get credentials
    username = args.username or input("Okta Username: ")
    password = args.password or getpass.getpass("Okta Password: ")

    # Initialize authenticator
    authenticator = OktaAuthenticator(args.okta_url, args.download_url)

    # Authenticate
    authenticated = False
    if args.method == "selenium" and SELENIUM_AVAILABLE:
        authenticated = authenticator.authenticate_with_selenium(username, password)

    if not authenticated:
        authenticated = authenticator.authenticate_manual()

    if not authenticated:
        print("❌ Authentication failed. Cannot proceed with download.")
        return 1

    # Download
    success = authenticator.download_globalprotect(args.output)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
