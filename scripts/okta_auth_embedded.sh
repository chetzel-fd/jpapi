#!/bin/bash
# Okta Authentication - Embedded OktaLoginWrapper Code
# Embeds the OktaLoginWrapper functionality directly (no external package dependency)
# Based on: https://github.com/B-Souty/OktaLoginWrapper
#
# Usage:
#   source okta_auth_embedded.sh
#   okta_auth_embedded "fanduel" "username@fanduel.com" "password"

set -e

# Security: Disable command history
set +H
unset HISTFILE

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Global variables
OKTA_SESSION_COOKIES_FILE=""
OKTA_INSTANCE=""
OKTA_USERNAME=""

# Cleanup function
cleanup() {
    if [ -n "${PASSWORD_FILE:-}" ] && [ -f "$PASSWORD_FILE" ]; then
        head -c 1024 /dev/urandom > "$PASSWORD_FILE" 2>/dev/null || true
        rm -f "$PASSWORD_FILE" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# Function to get logged-in user
get_logged_in_user() {
    local logged_in_user
    
    logged_in_user=$(/usr/bin/stat -f%Su /dev/console 2>/dev/null)
    if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
        echo "$logged_in_user"
        return 0
    fi
    
    logged_in_user=$(scutil <<< "show State:/Users/ConsoleUser" | awk '/Name :/ { print $3 }' 2>/dev/null)
    if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
        echo "$logged_in_user"
        return 0
    fi
    
    echo "$(whoami)"
}

# Function to get username from keychain
get_username_from_keychain() {
    local username
    local logged_in_user=$(get_logged_in_user)
    
    for term in "fanduel.com" "okta.com" "fanduel" "okta"; do
        if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
            local entry=$(sudo -u "$logged_in_user" security find-internet-password -s "$term" -g 2>/dev/null | grep -i "acct" | head -1)
            if [ -n "$entry" ]; then
                username=$(echo "$entry" | sed -n 's/.*"acct"<blob>="\([^"]*\)".*/\1/p')
                if [ -n "$username" ] && [[ "$username" == *"@"* ]]; then
                    echo "$username"
                    return 0
                fi
            fi
        fi
        
        local entry=$(security find-internet-password -s "$term" -g 2>/dev/null | grep -i "acct" | head -1)
        if [ -n "$entry" ]; then
            username=$(echo "$entry" | sed -n 's/.*"acct"<blob>="\([^"]*\)".*/\1/p')
            if [ -n "$username" ] && [[ "$username" == *"@"* ]]; then
                echo "$username"
                return 0
            fi
        fi
    done
    
    # Generate from system user
    local system_user="$logged_in_user"
    local full_name
    
    if [ -n "$system_user" ] && [ "$system_user" != "root" ] && [ "$system_user" != "system.administrator" ]; then
        full_name=$(dscl . -read "/Users/$system_user" RealName 2>/dev/null | tail -1 | sed 's/^[[:space:]]*RealName:[[:space:]]*//')
        if [ -z "$full_name" ]; then
            full_name=$(id -F "$system_user" 2>/dev/null || echo "$system_user")
        fi
    else
        system_user=$(whoami)
        full_name=$(id -F 2>/dev/null || echo "$system_user")
    fi
    
    if [[ "$full_name" == *" "* ]]; then
        local first=$(echo "$full_name" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')
        local last=$(echo "$full_name" | awk '{print $NF}' | tr '[:upper:]' '[:lower:]')
        echo "${first}.${last}@fanduel.com"
    else
        echo "${system_user}@fanduel.com"
    fi
}

# Function to get password from keychain
get_password_from_keychain() {
    local username="$1"
    local output_file="$2"
    local logged_in_user=$(get_logged_in_user)
    
    if [ -z "$output_file" ]; then
        echo "Error: output_file required" >&2
        return 1
    fi
    
    if [ -n "$logged_in_user" ] && [ "$logged_in_user" != "root" ] && [ "$logged_in_user" != "system.administrator" ]; then
        if sudo -u "$logged_in_user" security find-generic-password -l "Super Update Service" -g >/dev/null 2>&1; then
            local password=$(sudo -u "$logged_in_user" security find-generic-password -l "Super Update Service" -w 2>/dev/null | head -1)
            if [ -n "$password" ]; then
                echo -n "$password" > "$output_file" 2>/dev/null
                password=""
                return 0
            fi
        fi
        
        for term in "fanduel.com" "okta.com" "fanduel" "okta"; do
            if sudo -u "$logged_in_user" security find-internet-password -s "$term" -a "$username" -g >/dev/null 2>&1; then
                password=$(sudo -u "$logged_in_user" security find-internet-password -s "$term" -a "$username" -w 2>/dev/null)
                if [ -n "$password" ]; then
                    echo -n "$password" > "$output_file" 2>/dev/null
                    password=""
                    return 0
                fi
            fi
        done
    fi
    
    if security find-generic-password -l "Super Update Service" -g >/dev/null 2>&1; then
        local password=$(security find-generic-password -l "Super Update Service" -w 2>/dev/null | head -1)
        if [ -n "$password" ]; then
            echo -n "$password" > "$output_file" 2>/dev/null
            password=""
            return 0
        fi
    fi
    
    for term in "fanduel.com" "okta.com" "fanduel" "okta"; do
        if security find-internet-password -s "$term" -a "$username" -g >/dev/null 2>&1; then
            password=$(security find-internet-password -s "$term" -a "$username" -w 2>/dev/null)
            if [ -n "$password" ]; then
                echo -n "$password" > "$output_file" 2>/dev/null
                password=""
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
    
    local result=$(osascript -e "display dialog \"$message\" default answer \"\" with title \"Okta Authentication\" buttons {\"OK\", \"Cancel\"} default button \"OK\" with hidden answer" 2>&1)
    
    if [[ "$result" == *"text returned:"* ]]; then
        echo "$result" | sed -n 's/.*text returned:\(.*\)/\1/p' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//'
    else
        echo ""
    fi
}

# Check for Python and required libraries
check_python_deps() {
    local python_cmd="python3"
    
    # Try venv first
    if [ -f "$SCRIPT_DIR/../venv/bin/python3" ]; then
        python_cmd="$SCRIPT_DIR/../venv/bin/python3"
    elif [ -f "$SCRIPT_DIR/../../venv/bin/python3" ]; then
        python_cmd="$SCRIPT_DIR/../../venv/bin/python3"
    fi
    
    # Check for requests (required)
    if ! $python_cmd -c "import requests" 2>/dev/null; then
        echo "⚠️  requests library not found. Installing..." >&2
        if $python_cmd -m pip install --quiet --user requests 2>/dev/null || \
           $python_cmd -m pip install --quiet requests 2>/dev/null; then
            echo "✅ requests installed successfully" >&2
        else
            echo "❌ Failed to install requests library" >&2
            echo "   Please install manually: pip3 install requests" >&2
            return 1
        fi
    fi
    
    # Check for lxml (optional, but used by OktaLoginWrapper for HTML parsing)
    if ! $python_cmd -c "import lxml" 2>/dev/null; then
        echo "⚠️  lxml library not found. Installing..." >&2
        if $python_cmd -m pip install --quiet --user lxml 2>/dev/null || \
           $python_cmd -m pip install --quiet lxml 2>/dev/null; then
            echo "✅ lxml installed successfully" >&2
        else
            echo "⚠️  lxml installation failed, will use regex parsing instead" >&2
        fi
    fi
    
    echo "$python_cmd"
    return 0
}

# Embedded OktaLoginWrapper functionality
# Usage: okta_auth_embedded <okta_instance> <username> <password> [factor_type] [mfa_value]
okta_auth_embedded() {
    local okta_instance="$1"
    local username="$2"
    local password="$3"
    local factor_type="${4:-}"  # "push", "token", "question"
    local mfa_value="${5:-}"     # passcode or answer
    
    # Debug output if enabled
    if [ "${OKTA_DEBUG:-}" = "1" ]; then
        echo "DEBUG: okta_auth_embedded called with:" >&2
        echo "  okta_instance='$okta_instance'" >&2
        echo "  username='$username'" >&2
        echo "  password set: $([ -n "$password" ] && echo 'yes' || echo 'no')" >&2
    fi
    
    if [ -z "$okta_instance" ] || [ -z "$username" ]; then
        echo "Error: okta_auth_embedded requires okta_instance and username" >&2
        echo "  Received: okta_instance='$okta_instance', username='$username'" >&2
        return 1
    fi
    
    # Check for Python and dependencies
    local python_cmd=$(check_python_deps)
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    # Create session file with unique name
    # Use a consistent location so other scripts can find it
    OKTA_SESSION_COOKIES_FILE="/tmp/okta_cookies_${okta_instance}_${username//[^a-zA-Z0-9]/_}.json"
    # Clean up any old session files for this user/instance
    rm -f "/tmp/okta_cookies_${okta_instance}_"*.json 2>/dev/null || true
    touch "$OKTA_SESSION_COOKIES_FILE"
    chmod 600 "$OKTA_SESSION_COOKIES_FILE" 2>/dev/null || true
    export OKTA_SESSION_COOKIES_FILE
    OKTA_INSTANCE="$okta_instance"
    OKTA_USERNAME="$username"
    export OKTA_INSTANCE OKTA_USERNAME
    
    # Create secure temp file for password
    local password_file=$(mktemp /tmp/okta_password_XXXXXX 2>/dev/null)
    if [ -z "$password_file" ] || [ ! -f "$password_file" ]; then
        # Fallback if mktemp fails
        password_file="/tmp/okta_password_$$_$(date +%s)"
        touch "$password_file"
    fi
    chmod 600 "$password_file" 2>/dev/null || true
    
    if [ -z "$password" ]; then
        if ! get_password_from_keychain "$username" "$password_file" 2>/dev/null; then
            password=$(get_password_dialog "$username")
            if [ -z "$password" ]; then
                echo "❌ No password provided" >&2
                rm -f "$password_file"
                return 1
            fi
            echo -n "$password" > "$password_file"
            password=""
        fi
    else
        echo -n "$password" > "$password_file"
        password=""
    fi
    
    # Authenticate using embedded OktaLoginWrapper code
    local auth_result=$($python_cmd <<PYTHON_SCRIPT
import sys
import os
import json
import time
import re
import requests
from urllib.parse import urlparse, urljoin

# Embedded OktaLoginWrapper class (based on https://github.com/B-Souty/OktaLoginWrapper)
class OktaSession:
    def __init__(self, okta_instance):
        self.okta_instance = okta_instance
        self.okta_url = f"https://{okta_instance}.okta.com"
        self.okta_session = requests.Session()
        self.okta_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def okta_auth(self, username, password, passCode=None, answer=None, factor_type=None):
        """Authenticate to Okta with username and password, handle MFA"""
        
        # Step 1: Get the Okta login page
        login_url = f"{self.okta_url}/"
        response = self.okta_session.get(login_url)
        
        # Step 2: Extract form action and token from login page
        # Look for the sign-in form
        form_action = None
        token = None
        
        # Try to find form with regex (works without lxml)
        content = response.text
        # Use character class for quotes to avoid bash parsing issues
        form_match = re.search(r'<form[^>]*action=["'"'"']([^"'"'"']+)["'"'"']', content, re.IGNORECASE)
        if form_match:
            form_action = form_match.group(1)
            if not form_action.startswith('http'):
                form_action = urljoin(self.okta_url, form_action)
        
        # Look for CSRF token or state token
        token_match = re.search(r'name=["'"'"'](token|_token|csrfToken)["'"'"']\s+value=["'"'"']([^"'"'"']+)["'"'"']', content, re.IGNORECASE)
        if token_match:
            token = token_match.group(2)
        
        # Step 3: Submit login form
        login_data = {
            'username': username,
            'password': password
        }
        if token:
            login_data['token'] = token
        
        # Try the standard Okta sign-in endpoint
        signin_url = f"{self.okta_url}/api/v1/authn"
        auth_response = self.okta_session.post(
            signin_url,
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        )
        
        if auth_response.status_code != 200:
            # Fallback to HTML form submission
            if form_action:
                auth_response = self.okta_session.post(form_action, data=login_data)
            else:
                raise Exception(f"Authentication failed: HTTP {auth_response.status_code}")
        
        # Step 4: Handle MFA if required
        if auth_response.headers.get('Content-Type', '').startswith('application/json'):
            auth_data = auth_response.json()
            status = auth_data.get('status', '')
            
            if status == 'MFA_REQUIRED' or status == 'MFA_CHALLENGE':
                factors = auth_data.get('_embedded', {}).get('factors', [])
                state_token = auth_data.get('stateToken')
                
                # Find appropriate factor
                factor = None
                if factor_type == 'token' and passCode:
                    # Look for TOTP factor
                    for f in factors:
                        if f.get('factorType') in ['token:software:totp', 'token']:
                            factor = f
                            break
                elif factor_type == 'question' and answer:
                    # Look for question factor
                    for f in factors:
                        if f.get('factorType') == 'question':
                            factor = f
                            break
                else:
                    # Default: look for push factor
                    for f in factors:
                        if f.get('factorType') == 'push':
                            factor = f
                            break
                
                if not factor:
                    raise Exception("No supported MFA factor found")
                
                factor_id = factor['id']
                factor_type_actual = factor.get('factorType', '')
                
                # Verify factor
                if factor_type_actual == 'push':
                    # Push notification - poll for approval
                    verify_url = f"{self.okta_url}/api/v1/authn/factors/{factor_id}/verify"
                    print("📱 Push notification sent. Waiting for approval...", file=sys.stderr)
                    
                    for attempt in range(60):  # 60 seconds max
                        verify_response = self.okta_session.post(
                            verify_url,
                            json={'stateToken': state_token},
                            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
                        )
                        
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            verify_status = verify_data.get('status', '')
                            
                            if verify_status == 'SUCCESS':
                                session_token = verify_data.get('sessionToken')
                                # Exchange session token for session cookie
                                self._get_session_cookie(session_token)
                                return
                            elif verify_status == 'WAITING':
                                time.sleep(1)
                                continue
                            else:
                                raise Exception(f"MFA verification failed: {verify_status}")
                        else:
                            raise Exception(f"MFA verification failed: HTTP {verify_response.status_code}")
                    else:
                        raise Exception("MFA push notification timeout")
                
                elif factor_type_actual in ['token:software:totp', 'token'] and passCode:
                    # TOTP token
                    verify_url = f"{self.okta_url}/api/v1/authn/factors/{factor_id}/verify"
                    verify_response = self.okta_session.post(
                        verify_url,
                        json={'stateToken': state_token, 'passCode': passCode},
                        headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
                    )
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get('status') == 'SUCCESS':
                            session_token = verify_data.get('sessionToken')
                            self._get_session_cookie(session_token)
                            return
                    
                    raise Exception("TOTP verification failed")
                
                elif factor_type_actual == 'question' and answer:
                    # Security question
                    verify_url = f"{self.okta_url}/api/v1/authn/factors/{factor_id}/verify"
                    verify_response = self.okta_session.post(
                        verify_url,
                        json={'stateToken': state_token, 'answer': answer},
                        headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
                    )
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get('status') == 'SUCCESS':
                            session_token = verify_data.get('sessionToken')
                            self._get_session_cookie(session_token)
                            return
                    
                    raise Exception("Security question verification failed")
                else:
                    raise Exception(f"Unsupported MFA factor type: {factor_type_actual}")
            
            elif status == 'SUCCESS':
                # No MFA required
                session_token = auth_data.get('sessionToken')
                self._get_session_cookie(session_token)
                return
            else:
                error_summary = auth_data.get('errorSummary', f'Authentication failed: {status}')
                raise Exception(error_summary)
        else:
            # HTML response - check if we're logged in
            if 'okta-signin' not in auth_response.text.lower() and 'sign in' not in auth_response.text.lower():
                # Likely successful - we're past the login page
                return
            else:
                raise Exception("Authentication failed - still on login page")
    
    def _get_session_cookie(self, session_token):
        """Exchange session token for session cookie"""
        cookie_url = f"{self.okta_url}/login/sessionCookieRedirect"
        params = {
            'token': session_token,
            'redirectUrl': f"{self.okta_url}/"
        }
        self.okta_session.get(cookie_url, params=params, allow_redirects=True)
    
    def app_list(self):
        """Get list of available Okta apps"""
        apps_url = f"{self.okta_url}/user/home"
        response = self.okta_session.get(apps_url)
        
        apps = []
        # Parse HTML to find apps (simplified - OktaLoginWrapper uses lxml)
        # Use regex as fallback
        app_pattern = r'<a[^>]*href=["'"'"']([^"'"'"']*app/[^"'"'"']+)["'"'"'][^>]*>.*?<span[^>]*>([^<]+)</span>'
        matches = re.finditer(app_pattern, response.text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            link_url = match.group(1)
            label = match.group(2).strip()
            if not link_url.startswith('http'):
                link_url = urljoin(self.okta_url, link_url)
            apps.append({'label': label, 'linkUrl': link_url})
        
        return apps
    
    def connect_to(self, app_url):
        """Connect to an Okta app and return session"""
        response = self.okta_session.get(app_url, allow_redirects=True)
        return self.okta_session

try:
    # Read password from secure temp file
    password_file = "${password_file}"
    with open(password_file, 'r') as f:
        password = f.read().strip()
    
    # Delete password file immediately
    try:
        os.unlink(password_file)
    except:
        pass
    
    okta_instance = "${okta_instance}"
    username = "${username}"
    factor_type = "${factor_type}"
    mfa_value = "${mfa_value}"
    cookies_file = "${OKTA_SESSION_COOKIES_FILE}"
    
    # Create Okta session
    session = OktaSession(okta_instance)
    
    # Authenticate
    try:
        if factor_type == "token" and mfa_value:
            session.okta_auth(username=username, password=password, passCode=mfa_value, factor_type='token')
        elif factor_type == "question" and mfa_value:
            session.okta_auth(username=username, password=password, answer=mfa_value, factor_type='question')
        else:
            # Default: push notification
            session.okta_auth(username=username, password=password)
        
        # Clear password from memory
        password = None
        del password
        
        # Save session cookies to file
        cookies_dict = {}
        for cookie in session.okta_session.cookies:
            cookies_dict[cookie.name] = cookie.value
        
        session_data = {
            'cookies': cookies_dict,
            'okta_instance': okta_instance,
            'username': username,
            'okta_url': session.okta_url
        }
        
        with open(cookies_file, 'w') as f:
            json.dump(session_data, f)
        
        print("SUCCESS")
        sys.exit(0)
        
    except Exception as e:
        error_msg = str(e)
        if "password" in error_msg.lower() or "credential" in error_msg.lower():
            error_msg = "Authentication failed - please check your credentials"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        sys.exit(1)
        
except Exception as e:
    error_msg = str(e)
    if "password" in error_msg.lower():
        error_msg = "Authentication error occurred"
    print(f"ERROR: {error_msg}", file=sys.stderr)
    import traceback
    if os.environ.get("OKTA_DEBUG") == "1":
        traceback.print_exc(file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
)
    
    if [ $? -eq 0 ] && [[ "$auth_result" == *"SUCCESS"* ]]; then
        echo "✅ Okta authentication successful"
        return 0
    else
        echo "❌ Authentication failed: ${auth_result#ERROR: }" >&2
        rm -f "$OKTA_SESSION_COOKIES_FILE"
        OKTA_SESSION_COOKIES_FILE=""
        return 1
    fi
}

# Function to make authenticated request
okta_request_embedded() {
    local url="$1"
    local method="${2:-GET}"
    local output_file="${3:-}"
    
    if [ -z "$url" ]; then
        echo "Error: url required" >&2
        return 1
    fi
    
    if [ -z "$OKTA_SESSION_COOKIES_FILE" ] || [ ! -f "$OKTA_SESSION_COOKIES_FILE" ]; then
        echo "Error: Not authenticated. Call okta_auth_embedded first." >&2
        return 1
    fi
    
    local python_cmd=$(check_python_deps)
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    # Make request using stored cookies
    if [ -n "$output_file" ]; then
        $python_cmd <<PYTHON_SCRIPT
import sys
import json
import requests

try:
    with open("${OKTA_SESSION_COOKIES_FILE}", 'r') as f:
        session_data = json.load(f)
    
    cookies = session_data.get('cookies', {})
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    response = session.request("${method}", "${url}", timeout=60, stream=True)
    
    with open("${output_file}", 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print(f"SUCCESS: {response.status_code}")
    sys.exit(0)
    
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
    else
        $python_cmd <<PYTHON_SCRIPT
import sys
import json
import requests

try:
    with open("${OKTA_SESSION_COOKIES_FILE}", 'r') as f:
        session_data = json.load(f)
    
    cookies = session_data.get('cookies', {})
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    response = session.request("${method}", "${url}", timeout=60)
    
    print(response.text)
    print(f"\nSTATUS: {response.status_code}", file=sys.stderr)
    sys.exit(0)
    
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
    fi
}

# When this script is sourced or run, save a copy to /tmp for other scripts to use
if [ -n "${BASH_SOURCE[0]}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
    SCRIPT_SOURCE="${BASH_SOURCE[0]}"
    # Save to /tmp so other scripts can find it
    if [ "$SCRIPT_SOURCE" != "/tmp/okta_auth_embedded.sh" ]; then
        cp "$SCRIPT_SOURCE" "/tmp/okta_auth_embedded.sh" 2>/dev/null || true
        chmod +x "/tmp/okta_auth_embedded.sh" 2>/dev/null || true
    fi
fi

# Main execution (if run standalone)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    OKTA_INSTANCE="${OKTA_INSTANCE:-fanduel}"
    USERNAME="${USERNAME:-}"
    PASSWORD="${PASSWORD:-}"
    
    if [ -z "$USERNAME" ]; then
        USERNAME=$(get_username_from_keychain)
    fi
    
    if okta_auth_embedded "$OKTA_INSTANCE" "$USERNAME" "$PASSWORD"; then
        echo "✅ Authentication successful"
    else
        exit 1
    fi
fi

