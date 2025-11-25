#!/bin/bash
# GlobalProtect Downloader - Shell Script Version
# Uses osascript for dialogs and keychain for credentials
# SECURITY: Passwords are handled securely and never exposed in logs or process lists

set -e

# Security: Disable command history for this script
set +H
unset HISTFILE

# Security: Clear sensitive variables and temp files on exit
cleanup() {
    # Clear password from memory
    if [ -n "${PASSWORD:-}" ]; then
        PASSWORD=""
        export PASSWORD=""
        unset PASSWORD
    fi
    # Clean up password file if it exists
    if [ -n "${PASSWORD_FILE:-}" ] && [ -f "$PASSWORD_FILE" ]; then
        # Overwrite with random data before deleting (best effort)
        head -c 1024 /dev/urandom > "$PASSWORD_FILE" 2>/dev/null || true
        rm -f "$PASSWORD_FILE" 2>/dev/null || true
    fi
    # Clean up temp directory (pkg file)
    if [ -n "${TEMP_DIR:-}" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OKTA_INSTANCE="${OKTA_INSTANCE:-fanduel}"
DOWNLOAD_URL="${DOWNLOAD_URL:-https://secure.fanduel.com/global-protect/getmsi.esp?version=none&platform=mac}"

# Use temp directory for download (will be installed, not saved to Downloads)
TEMP_DIR=$(mktemp -d /tmp/globalprotect_XXXXXX)
OUTPUT_PATH="${TEMP_DIR}/GlobalProtect.pkg"

# Security: Control auto-installation of dependencies
# Set GP_NO_AUTO_INSTALL=1 to disable automatic installation
# Recommended for enterprise: Pre-install oktaloginwrapper via Jamf policy
GP_NO_AUTO_INSTALL="${GP_NO_AUTO_INSTALL:-0}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔐 GlobalProtect Downloader"
echo "============================================================"

# Function to get logged-in user (not the user running the script)
get_logged_in_user() {
    # Get the user currently logged into the console (works even when script runs as root)
    local logged_in_user
    
    # Method 1: Get console user (most reliable for GUI sessions)
    logged_in_user=$(/usr/bin/stat -f%Su /dev/console 2>/dev/null)
    if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
        echo "$logged_in_user"
        return 0
    fi
    
    # Method 2: Get from scutil
    logged_in_user=$(scutil <<< "show State:/Users/ConsoleUser" | awk '/Name :/ { print $3 }' 2>/dev/null)
    if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
        echo "$logged_in_user"
        return 0
    fi
    
    # Method 3: Get from who command (last logged in user)
    logged_in_user=$(who | grep "console" | awk '{print $1}' | head -1)
    if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
        echo "$logged_in_user"
        return 0
    fi
    
    # Fallback: Use current user (may be root/system when run via Jamf)
    echo "$(whoami)"
}

# Function to get username from keychain
# Note: For "Super Update Service", the account name may be "super_auth_user_password" or similar,
# so we don't use it for username. We generate username from system info instead.
get_username_from_keychain() {
    # Try to find username from various keychain entries
    local username
    local logged_in_user=$(get_logged_in_user)
    
    # Check for "Super Update Service" - but don't use its account name for username
    # The account name in Super Update Service may be "super_auth_user_password" or similar
    # Instead, we'll check if Super Update Service exists, and if so, generate username from system
    local has_super_update=false
    
    # Check logged-in user's keychain first
    if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
        if sudo -u "$logged_in_user" security find-generic-password -l "Super Update Service" -g >/dev/null 2>&1; then
            has_super_update=true
        fi
    fi
    
    # Check current user's keychain
    if [ "$has_super_update" = false ]; then
        if security find-generic-password -l "Super Update Service" -g >/dev/null 2>&1; then
            has_super_update=true
        fi
    fi
    
    # If Super Update Service exists, generate username from system (don't use its account name)
    # Otherwise, try to find username from other keychain entries
    if [ "$has_super_update" = false ]; then
        # Try other keychain entries for username
        for term in "fanduel.com" "okta.com" "fanduel" "okta"; do
            if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
                local entry=$(sudo -u "$logged_in_user" security find-internet-password -s "$term" -g 2>/dev/null | grep -i "acct" | head -1)
                if [ -n "$entry" ]; then
                    username=$(echo "$entry" | sed -n 's/.*"acct"<blob>="\([^"]*\)".*/\1/p')
                    if [ -n "$username" ] && [[ "$username" == *"@fanduel.com" ]]; then
                        echo "$username"
                        return 0
                    fi
                fi
            fi
            
            local entry=$(security find-internet-password -s "$term" -g 2>/dev/null | grep -i "acct" | head -1)
            if [ -n "$entry" ]; then
                username=$(echo "$entry" | sed -n 's/.*"acct"<blob>="\([^"]*\)".*/\1/p')
                if [ -n "$username" ] && [[ "$username" == *"@fanduel.com" ]]; then
                    echo "$username"
                    return 0
                fi
            fi
        done
    fi
    
    # Generate from logged-in user's system info
    local system_user="$logged_in_user"
    local full_name
    
    # Get full name for logged-in user
    if [ -n "$system_user" ] && [ "$system_user" != "root" ] && [ "$system_user" != "system.administrator" ]; then
        # Try to get full name from dscl
        full_name=$(dscl . -read "/Users/$system_user" RealName 2>/dev/null | tail -1 | sed 's/^[[:space:]]*RealName:[[:space:]]*//')
        if [ -z "$full_name" ]; then
            # Fallback to id -F for logged-in user
            full_name=$(id -F "$system_user" 2>/dev/null || echo "$system_user")
        fi
    else
        # Fallback if we can't get logged-in user
        system_user=$(whoami)
        full_name=$(id -F 2>/dev/null || echo "$system_user")
    fi
    
    # Convert to firstname.lastname@fanduel.com format
    if [[ "$full_name" == *" "* ]]; then
        # "First Last" -> "first.last"
        local first=$(echo "$full_name" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')
        local last=$(echo "$full_name" | awk '{print $NF}' | tr '[:upper:]' '[:lower:]')
        echo "${first}.${last}@fanduel.com"
    else
        echo "${system_user}@fanduel.com"
    fi
}

# Function to get password from keychain
# SECURITY: Writes password directly to temp file to avoid stdout logging
# Never echoes password to stdout - this prevents password exposure in Jamf logs
get_password_from_keychain() {
    local username="$1"
    local output_file="$2"  # Temp file to write password to (required)
    local logged_in_user=$(get_logged_in_user)
    
    # SECURITY: Require output file to prevent accidental stdout exposure
    if [ -z "$output_file" ]; then
        echo "Error: output_file required for security" >&2
        return 1
    fi
    
    # Try logged-in user's keychain first (if not root/system)
    if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
        # Try Super Update Service - get ANY entry (account name may be "super_auth_user_password" or anything else)
        # We search by label/service name only, not by account name
        if sudo -u "$logged_in_user" security find-generic-password -l "Super Update Service" -g >/dev/null 2>&1; then
            local password=$(sudo -u "$logged_in_user" security find-generic-password -l "Super Update Service" -w 2>/dev/null | head -1)
            if [ -n "$password" ]; then
                # SECURITY: Write directly to file, never to stdout
                echo -n "$password" > "$output_file" 2>/dev/null
                password=""  # Clear local variable
                return 0
            fi
        fi
        
        # Try other keychain entries for logged-in user
        for term in "fanduel.com" "okta.com" "fanduel" "okta"; do
            if sudo -u "$logged_in_user" security find-internet-password -s "$term" -a "$username" -g >/dev/null 2>&1; then
                password=$(sudo -u "$logged_in_user" security find-internet-password -s "$term" -a "$username" -w 2>/dev/null)
                if [ -n "$password" ]; then
                    # SECURITY: Write directly to file, never to stdout
                    echo -n "$password" > "$output_file" 2>/dev/null
                    password=""  # Clear local variable
                    return 0
                fi
            fi
        done
    fi
    
    # Fallback: Try current user's keychain (may be system keychain)
    # Try Super Update Service - get ANY entry (account name may be "super_auth_user_password" or anything else)
    # We search by label/service name only, not by account name
    if security find-generic-password -l "Super Update Service" -g >/dev/null 2>&1; then
        local password=$(security find-generic-password -l "Super Update Service" -w 2>/dev/null | head -1)
        if [ -n "$password" ]; then
            # SECURITY: Write directly to file, never to stdout
            echo -n "$password" > "$output_file" 2>/dev/null
            password=""  # Clear local variable
            return 0
        fi
    fi
    
    # Try other keychain entries
    for term in "fanduel.com" "okta.com" "fanduel" "okta"; do
        if security find-internet-password -s "$term" -a "$username" -g >/dev/null 2>&1; then
            password=$(security find-internet-password -s "$term" -a "$username" -w 2>/dev/null)
            if [ -n "$password" ]; then
                # SECURITY: Write directly to file, never to stdout
                echo -n "$password" > "$output_file" 2>/dev/null
                password=""  # Clear local variable
                return 0
            fi
        fi
    done
    
    return 1
}

# Function to get password via dialog
get_password_dialog() {
    local username="$1"
    local message="Enter your Okta password for ${username}:"
    
    # Use a simple, single-line osascript command that we know works
    # This is the format that works when tested directly
    local result=$(osascript -e "display dialog \"$message\" default answer \"\" with title \"GlobalProtect Downloader\" buttons {\"OK\", \"Cancel\"} default button \"OK\" with hidden answer" 2>&1)
    
    # Parse the result - format is "button returned:OK, text returned:password"
    if [[ "$result" == *"text returned:"* ]]; then
        echo "$result" | sed -n 's/.*text returned:\(.*\)/\1/p' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//'
    elif [[ "$result" == *"error"* ]]; then
        # Error occurred (user cancelled)
        echo ""
    else
        echo ""
    fi
}

# Function to show info dialog
show_info() {
    local title="$1"
    local message="$2"
    osascript -e "display dialog \"$message\" buttons {\"OK\"} default button \"OK\" with title \"$title\" with icon note" >/dev/null 2>&1
}

# Function to show error dialog
show_error() {
    local title="$1"
    local message="$2"
    osascript -e "display dialog \"$message\" buttons {\"OK\"} default button \"OK\" with title \"$title\" with icon stop" >/dev/null 2>&1
}

# Get credentials
echo "🔍 Checking for credentials..."

USERNAME=$(get_username_from_keychain)
echo "✅ Username: $USERNAME"

echo "🔍 Checking keychain for password..."
# SECURITY: Create temp file first, then read password into it (avoids stdout logging)
PASSWORD_FILE=$(mktemp /tmp/gp_password_XXXXXX)
chmod 600 "$PASSWORD_FILE"
# Try to get password quickly, don't wait if it prompts
# SECURITY: Write password directly to file to avoid stdout exposure
if get_password_from_keychain "$USERNAME" "$PASSWORD_FILE" 2>/dev/null; then
    PASSWORD=$(cat "$PASSWORD_FILE" 2>/dev/null)
    # Clear temp file immediately after reading
    head -c 1024 /dev/urandom > "$PASSWORD_FILE" 2>/dev/null || true
    rm -f "$PASSWORD_FILE" 2>/dev/null || true
else
    PASSWORD=""
    rm -f "$PASSWORD_FILE" 2>/dev/null || true
fi

if [ -z "$PASSWORD" ]; then
    echo "📋 Password not found in keychain."
    echo "📋 Showing password dialog..."
    PASSWORD=$(get_password_dialog "$USERNAME")
    
    if [ -z "$PASSWORD" ]; then
        echo "❌ No password provided or dialog cancelled. Exiting."
        PASSWORD=""
        unset PASSWORD
        exit 1
    fi
    echo "✅ Password received from dialog"
else
    echo "✅ Password found in keychain"
fi

# SECURITY: Create a secure temporary file for password passing to Python
# This avoids exposing password in process list or command line
# (PASSWORD_FILE may have been created above, but we need a fresh one for Python)
PASSWORD_FILE=$(mktemp /tmp/gp_password_XXXXXX)
chmod 600 "$PASSWORD_FILE"
echo -n "$PASSWORD" > "$PASSWORD_FILE"
# Clear password from shell variable immediately
PASSWORD=""
unset PASSWORD

# Source the embedded Okta authentication script
# Try multiple locations where the script might be available
OKTA_AUTH_SCRIPT=""
OKTA_SCRIPT_LOCATIONS=(
    "$SCRIPT_DIR/okta_auth_embedded.sh"
    "/usr/local/bin/okta_auth_embedded.sh"
    "/tmp/okta_auth_embedded.sh"
    "$(dirname "$0")/okta_auth_embedded.sh"
)

for location in "${OKTA_SCRIPT_LOCATIONS[@]}"; do
    if [ -f "$location" ] && [ -s "$location" ]; then
        OKTA_AUTH_SCRIPT="$location"
        break
    fi
done

# If not found, try to download from Jamf Pro using jamf binary
if [ -z "$OKTA_AUTH_SCRIPT" ] && [ -f "/usr/local/bin/jamf" ]; then
    echo "📥 Downloading Okta authentication script from Jamf Pro (ID: 210)..."
    OKTA_AUTH_SCRIPT="/tmp/okta_auth_embedded_$$.sh"
    
    # Use jamf binary to download script 210
    # Note: This requires the script to be accessible via jamf binary
    # Alternative: Run script 210 as a separate script in the policy before this one
    if /usr/local/bin/jamf runScript -id 210 -path "$OKTA_AUTH_SCRIPT" >/dev/null 2>&1; then
        if [ -f "$OKTA_AUTH_SCRIPT" ] && [ -s "$OKTA_AUTH_SCRIPT" ]; then
            chmod +x "$OKTA_AUTH_SCRIPT" 2>/dev/null || true
        fi
    fi
fi

# If still not found, provide helpful error
if [ -z "$OKTA_AUTH_SCRIPT" ] || [ ! -f "$OKTA_AUTH_SCRIPT" ] || [ ! -s "$OKTA_AUTH_SCRIPT" ]; then
    echo "❌ okta_auth_embedded.sh not found"
    echo ""
    echo "   The Okta authentication script (ID: 210) must be available."
    echo "   Options:"
    echo "   1. Run script ID 210 (Okta Authentication Embedded) before this script in your policy"
    echo "   2. Ensure both scripts are in the same policy and run in sequence"
    echo "   3. Install okta_auth_embedded.sh to /usr/local/bin/okta_auth_embedded.sh"
    echo ""
    exit 1
fi

# Source the Okta authentication script
source "$OKTA_AUTH_SCRIPT" || {
    echo "❌ Failed to load okta_auth_embedded.sh from $OKTA_AUTH_SCRIPT"
    exit 1
}

# Authenticate to Okta using embedded implementation
echo "🔐 Authenticating with Okta (this may take 30-60 seconds with MFA)..."

# Ensure variables are set
if [ -z "$OKTA_INSTANCE" ]; then
    OKTA_INSTANCE="fanduel"
fi

if [ -z "$USERNAME" ]; then
    echo "❌ Username is required but not set"
    exit 1
fi

# Debug: Show what we're about to pass (without exposing sensitive data)
if [ "${GP_DEBUG:-}" = "1" ]; then
    echo "DEBUG: OKTA_INSTANCE='$OKTA_INSTANCE'"
    echo "DEBUG: USERNAME='$USERNAME'"
fi

# Verify the function exists
if ! type okta_auth_embedded >/dev/null 2>&1; then
    echo "❌ okta_auth_embedded function not found after sourcing script"
    echo "   Script location: $OKTA_AUTH_SCRIPT"
    exit 1
fi

# Check if we already have a valid session from script 210
# Script 210 creates a session file at /tmp/okta_cookies_<instance>_<username>.json
SESSION_FILE_PATTERN="/tmp/okta_cookies_${OKTA_INSTANCE}_${USERNAME//[^a-zA-Z0-9]/_}.json"
if [ -f "$SESSION_FILE_PATTERN" ] && [ -s "$SESSION_FILE_PATTERN" ]; then
    echo "✅ Using existing Okta session from previous authentication"
    export OKTA_SESSION_COOKIES_FILE="$SESSION_FILE_PATTERN"
else
    # Authenticate using embedded OktaLoginWrapper code (no external dependency)
    # Pass variables explicitly to avoid scope issues
    echo "🔐 Starting new Okta authentication..."
    if ! okta_auth_embedded "$OKTA_INSTANCE" "$USERNAME" ""; then
        echo "❌ Okta authentication failed"
        exit 1
    fi
    # Get the session file path that was created
    if [ -z "${OKTA_SESSION_COOKIES_FILE:-}" ]; then
        OKTA_SESSION_COOKIES_FILE="$SESSION_FILE_PATTERN"
    fi
    export OKTA_SESSION_COOKIES_FILE
fi

# Use Python for the download with authenticated session
PYTHON_CMD="python3"
if [ -f "$SCRIPT_DIR/../venv/bin/python3" ]; then
    PYTHON_CMD="$SCRIPT_DIR/../venv/bin/python3"
elif [ -f "$SCRIPT_DIR/../../venv/bin/python3" ]; then
    PYTHON_CMD="$SCRIPT_DIR/../../venv/bin/python3"
fi

# Check if requests library is available (standard library, should be available)
if ! $PYTHON_CMD -c "import requests" 2>/dev/null; then
    echo "📦 Installing requests library..."
    if ! $PYTHON_CMD -m pip install --quiet --user requests 2>/dev/null && \
       ! $PYTHON_CMD -m pip install --quiet requests 2>/dev/null; then
        show_error "Error" "requests library is required but could not be installed.\n\nPlease install manually:\npip3 install requests"
        echo "❌ Failed to install requests library"
        exit 1
    fi
fi

# Download using authenticated session
$PYTHON_CMD <<PYTHON_SCRIPT
import sys
import re
import os
import json
import requests
from pathlib import Path

try:
    # Check if running in interactive terminal (for progress updates)
    # In Jamf, we want minimal logging to avoid log truncation
    # Check for Jamf-specific indicators
    jamf_indicators = [
        os.environ.get("JAMF_SERVER"),
        os.environ.get("JAMF_PRO_URL"),
        os.path.exists("/Library/Application Support/JAMF"),
        os.path.exists("/usr/local/jamf")
    ]
    is_jamf = any(jamf_indicators)
    is_interactive = sys.stdout.isatty() and not is_jamf
    
    if is_jamf:
        print("📥 Downloading GlobalProtect.pkg (this may take a few minutes)...")
    else:
        print("📥 Downloading GlobalProtect.pkg...")
    
    # Load session cookies from native authentication
    cookies_file = "${OKTA_SESSION_COOKIES_FILE}"
    if not os.path.exists(cookies_file):
        print("❌ Session file not found. Authentication may have failed.")
        sys.exit(1)
    
    with open(cookies_file, 'r') as f:
        session_data = json.load(f)
    
    cookies = session_data.get('cookies', {})
    
    # Create session and restore cookies
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    # Make authenticated request
    response = session.get("${DOWNLOAD_URL}", timeout=60, stream=True)
    
    if response.status_code == 200:
        # Handle redirects
        if 'text/html' in response.headers.get('Content-Type', ''):
            content = response.text
            if 'GlobalProtect.pkg' in content:
                match = re.search(r'["\']([^"\']*GlobalProtect\.pkg[^"\']*)["\']', content)
                if match:
                    pkg_url = match.group(1)
                    if not pkg_url.startswith('http'):
                        pkg_url = f"https://secure.fanduel.com/global-protect/{pkg_url.lstrip('/')}"
                    if is_interactive:
                        print(f"🔗 Following redirect...")
                    response = session.get(pkg_url, timeout=60, stream=True)
        
        # Save file
        output_path = Path("${OUTPUT_PATH}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        last_percent = -1
        last_mb = -1
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Only update progress periodically to reduce log verbosity
                    # In Jamf mode, suppress all progress output to avoid log truncation
                    if is_jamf:
                        # In Jamf: No progress output at all, just download silently
                        pass
                    elif is_interactive:
                        # Interactive: Update every 5%
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            current_percent_int = int(percent // 5)
                            last_percent_int = int(last_percent // 5) if last_percent >= 0 else -1
                            if current_percent_int > last_percent_int:
                                print(f"📥 Downloading: {percent:.1f}% ({downloaded:,}/{total_size:,} bytes)")
                                last_percent = percent
                        else:
                            # Unknown size: every 5MB
                            current_mb = downloaded // 5242880
                            if current_mb > last_mb:
                                print(f"📥 Downloading: {downloaded:,} bytes...")
                                last_mb = current_mb
                    else:
                        # Non-interactive (but not Jamf): Only major milestones
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            milestone_percents = [25, 50, 75, 100]
                            for milestone in milestone_percents:
                                if last_percent < milestone <= percent:
                                    print(f"📥 Downloading: {milestone}% ({int(total_size * milestone / 100):,}/{total_size:,} bytes)")
                                    last_percent = milestone
                                    break
                        else:
                            # Unknown size: every 25MB
                            current_mb = downloaded // 26214400
                            if current_mb > last_mb:
                                print(f"📥 Downloading: {downloaded:,} bytes ({downloaded / 1024 / 1024:.1f} MB)...")
                                last_mb = current_mb
        
        file_size = output_path.stat().st_size
        print(f"✅ Successfully downloaded: {output_path.name}")
        print(f"   File size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")
        
        # SECURITY: Store credentials in keychain for next time
        # Read password from a new secure temp file if we need to store it
        # (Password was already cleared, so we'd need to re-prompt or skip storage)
        # For now, skip storing password to avoid re-exposure
        # Users can enter password again next time, or it will be in Super Update Service
        pass
        
        # Installation will be handled by shell script after Python exits
        sys.exit(0)
    else:
        print(f"❌ Download failed. Status: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    # SECURITY: Sanitize error messages to avoid password exposure
    error_msg = str(e)
    # Remove any potential sensitive data from error messages
    if "password" in error_msg.lower() or "credential" in error_msg.lower():
        error_msg = "An authentication or connection error occurred"
    print(f"❌ Error: {error_msg}")
    # Don't print full traceback in production to avoid exposing sensitive info
    import traceback
    # Only print traceback if debugging is enabled
    if os.environ.get("GP_DEBUG") == "1":
        traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

EXIT_CODE=$?

# SECURITY: Cleanup is handled by trap, but ensure it's done here too
# (The trap will handle it, but this is a double-check)

if [ $EXIT_CODE -eq 0 ]; then
    # Install GlobalProtect.pkg
    if [ -f "$OUTPUT_PATH" ]; then
        echo "📦 Installing GlobalProtect..."
        
        # Install the package
        # Use a temp file to capture installer output and exit code
        INSTALL_LOG=$(mktemp /tmp/gp_install_XXXXXX.log)
        if installer -pkg "$OUTPUT_PATH" -target / > "$INSTALL_LOG" 2>&1; then
            INSTALL_EXIT=0
        else
            INSTALL_EXIT=$?
        fi
        
        # Show installer output (filter out verbose installer: lines, but show errors)
        if [ -f "$INSTALL_LOG" ]; then
            # Show any error messages
            if [ $INSTALL_EXIT -ne 0 ]; then
                echo "   Installer output:"
                cat "$INSTALL_LOG" | grep -v "^installer:" | head -20
            fi
            rm -f "$INSTALL_LOG"
        fi
        
        if [ $INSTALL_EXIT -eq 0 ]; then
            echo "✅ GlobalProtect installed successfully!"
            show_info "Success" "GlobalProtect has been downloaded and installed successfully!\n\nYou can now use GlobalProtect from your Applications folder."
        else
            echo "❌ Installation failed (exit code: $INSTALL_EXIT)"
            show_error "Installation Failed" "GlobalProtect downloaded but installation failed.\n\nExit code: $INSTALL_EXIT\n\nYou can try installing manually:\nopen ${OUTPUT_PATH}"
            exit 1
        fi
    else
        echo "❌ Downloaded file not found: $OUTPUT_PATH"
        show_error "Error" "Downloaded file not found.\n\nDownload may have failed."
        exit 1
    fi
else
    echo "❌ Download failed"
    echo "Possible issues:"
    echo "  - Authentication failed (check credentials)"
    echo "  - MFA challenge not completed"
    echo "  - Network connectivity issues"
    echo "  - Okta authentication error"
    echo ""
    # SECURITY: Don't mention "password" in error dialogs
    show_error "Error" "Failed to download GlobalProtect.\n\nPlease check the terminal output for details.\n\nCommon issues:\n- Authentication failed\n- MFA not completed\n- Network issues"
    exit 1
fi

