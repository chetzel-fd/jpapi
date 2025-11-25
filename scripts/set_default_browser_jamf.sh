#!/bin/bash
#
# Set Default Browser for Jamf
# Installs macadmins/default-browser PKG when needed and sets default browser.
# Includes robust Island fallback by editing LSHandlers directly.
# Runs as the currently logged-in user.
#
# Parameters:
#   $4 = Browser name or bundle ID (e.g., "Island", "Chrome", "Safari", "io.island.Island")
#

set -e

VERSION="v1.0.18"
PKG_URL="https://github.com/macadmins/default-browser/releases/download/${VERSION}/default-browser.pkg"
TOOL_PATH="/opt/macadmins/bin/default-browser"

log_info() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >&2
}

# Logged-in user
CURRENT_USER=$(/usr/bin/stat -f "%Su" /dev/console)
if [ -z "$CURRENT_USER" ] || [ "$CURRENT_USER" = "root" ] || [ "$CURRENT_USER" = "loginwindow" ]; then
    CURRENT_USER=$(scutil <<< "show State:/Users/ConsoleUser" | awk '/Name :/ { print $3 }')
fi
if [ -z "$CURRENT_USER" ] || [ "$CURRENT_USER" = "root" ] || [ "$CURRENT_USER" = "loginwindow" ]; then
    log_error "No logged-in user found. Cannot set default browser."
    exit 1
fi
log_info "Running as user: $CURRENT_USER"

# Derive user home (handles mobile accounts)
USER_HOME=$(dscl . -read /Users/$CURRENT_USER NFSHomeDirectory 2>/dev/null | awk '{print $2}')
if [ -z "$USER_HOME" ]; then
    USER_HOME="/Users/$CURRENT_USER"
fi

# Map common names to bundle IDs
get_bundle_id() {
    local input="$1"
    case "$input" in
        Island|island)
            echo "io.island.Island";;
        Chrome|chrome|"Google Chrome"|GoogleChrome)
            echo "com.google.Chrome";;
        Safari|safari)
            echo "com.apple.Safari";;
        Edge|edge|"Microsoft Edge")
            echo "com.microsoft.edgemac";;
        Firefox|firefox)
            echo "org.mozilla.firefox";;
        Brave|brave|"Brave Browser")
            echo "com.brave.Browser";;
        *)
            # Assume it's already a bundle ID
            echo "$input";;
    esac
}

BROWSER_PARAM="${4:-Island}"
BROWSER_ID=$(get_bundle_id "$BROWSER_PARAM")
log_info "Setting default browser to: $BROWSER_PARAM ($BROWSER_ID)"

# Ensure the macadmins tool exists (used for non-Island)
if [ ! -f "$TOOL_PATH" ]; then
    log_info "Installing macadmins/default-browser tool..."
    TEMP_PKG=$(mktemp).pkg
    log_info "Downloading from: $PKG_URL"
    if ! curl -L "$PKG_URL" -o "$TEMP_PKG" 2>/dev/null; then
        log_error "Failed to download default-browser package"
        rm -f "$TEMP_PKG"
        exit 1
    fi
    log_info "Installing package..."
    installer -pkg "$TEMP_PKG" -target / >/dev/null 2>&1 || true
    rm -f "$TEMP_PKG"
    if [ -f "$TOOL_PATH" ]; then
        log_info "Tool installed successfully"
    else
        log_error "Installation did not place $TOOL_PATH; continuing without the tool"
    fi
fi

# Fallback setter via LSHandlers (robust for Island or when tool unavailable)
set_default_via_plist() {
    local bundle_id="$1"
    local plist_path="$USER_HOME/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist"
    local app_path="/Applications/Island.app"

    # Ensure app is registered with LaunchServices by launching once if Island
    if [ "$bundle_id" = "io.island.Island" ] && [ -d "$app_path" ]; then
        sudo -u "$CURRENT_USER" open -ga "$app_path" || true
        sleep 1
    fi

    /usr/bin/python3 <<PYCODE
import os, plistlib
plist_path = os.path.expanduser(r"$plist_path")
bundle_id = r"$bundle_id"

schemes = {"http", "https"}
ctypes_all = {"public.html", "public.xhtml"}
ctypes_viewer = {"public.url"}

handlers = []
if os.path.exists(plist_path):
    try:
        with open(plist_path, 'rb') as f:
            data = plistlib.load(f)
            handlers = data.get('LSHandlers', []) or []
    except Exception:
        handlers = []

filtered = []
for h in handlers:
    if h.get('LSHandlerURLScheme') in schemes:
        continue
    ct = h.get('LSHandlerContentType')
    if ct in ctypes_all or ct in ctypes_viewer:
        continue
    filtered.append(h)

new_handlers = []
for s in ("http", "https"):
    new_handlers.append({'LSHandlerURLScheme': s, 'LSHandlerRoleAll': bundle_id})
for ct in ("public.html", "public.xhtml"):
    new_handlers.append({'LSHandlerContentType': ct, 'LSHandlerRoleAll': bundle_id})
new_handlers.append({'LSHandlerContentType': 'public.url', 'LSHandlerRoleViewer': bundle_id})

result = {'LSHandlers': new_handlers + filtered}

os.makedirs(os.path.dirname(plist_path), exist_ok=True)
with open(plist_path, 'wb') as f:
    plistlib.dump(result, f)
PYCODE

    chown "$CURRENT_USER":"staff" "$plist_path" 2>/dev/null || true
    sudo -u "$CURRENT_USER" killall cfprefsd 2>/dev/null || true
    /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -kill -r -domain local -domain system -domain user >/dev/null 2>&1 || true
}

# Prefer the macadmins tool for mainstream browsers; use plist method for Island
if [ "$BROWSER_ID" = "io.island.Island" ]; then
    log_info "Applying Island via plist method"
    set_default_via_plist "$BROWSER_ID"
    log_info "Island default applied"
    exit 0
fi

# Use the macadmins tool with explicit flag for non-Island
if [ -x "$TOOL_PATH" ]; then
    log_info "Using macadmins tool for $BROWSER_ID"
    # The tool expects --identifier
    sudo -u "$CURRENT_USER" "$TOOL_PATH" --identifier "$BROWSER_ID" 2>&1 | while IFS= read -r line; do
        log_info "$line"
    done
    EXIT_CODE=${PIPESTATUS[0]}
    if [ $EXIT_CODE -ne 0 ]; then
        log_error "Tool failed (code $EXIT_CODE). Falling back to plist method."
        set_default_via_plist "$BROWSER_ID"
        exit 0
    fi
else
    log_warn "Tool not present; using plist method"
    set_default_via_plist "$BROWSER_ID"
fi

log_info "Default browser configuration complete"
exit 0