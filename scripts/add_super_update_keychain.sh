#!/bin/bash
# Add Okta credentials to "Super Update Service" keychain entry
# This allows the GlobalProtect downloader to use these credentials automatically

set -e

# Get logged-in user
LOGGED_IN_USER=$(/usr/bin/stat -f%Su /dev/console 2>/dev/null || echo "$(whoami)")

# Generate username from system info
FULL_NAME=$(id -F "$LOGGED_IN_USER" 2>/dev/null || echo "$LOGGED_IN_USER")
if [[ "$FULL_NAME" == *" "* ]]; then
    FIRST=$(echo "$FULL_NAME" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')
    LAST=$(echo "$FULL_NAME" | awk '{print $NF}' | tr '[:upper:]' '[:lower:]')
    USERNAME="${FIRST}.${LAST}@${JPAPI_EMAIL_DOMAIN:-example.com}"
else
    USERNAME="${LOGGED_IN_USER}@${JPAPI_EMAIL_DOMAIN:-example.com}"
fi

# Allow username override
if [ -n "${1:-}" ]; then
    USERNAME="$1"
fi

echo "🔐 Adding credentials to Super Update Service keychain"
echo "============================================================"
echo "Username: $USERNAME"
echo ""

# Check if entry already exists
if security find-generic-password -l "Super Update Service" -a "$USERNAME" -g >/dev/null 2>&1; then
    echo "⚠️  Keychain entry already exists for $USERNAME"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
    # Delete existing entry
    security delete-generic-password -l "Super Update Service" -a "$USERNAME" 2>/dev/null || true
fi

# Prompt for password securely
echo "Enter your Okta password:"
PASSWORD=$(osascript <<APPLESCRIPT
tell application "System Events"
    display dialog "Enter your Okta password for ${USERNAME}:" default answer "" with title "Super Update Service Keychain" buttons {"Cancel", "OK"} default button "OK" with hidden answer
    set theAnswer to text returned of result
    return theAnswer
end tell
APPLESCRIPT
)

if [ -z "$PASSWORD" ]; then
    echo "❌ No password provided. Cancelled."
    exit 1
fi

# Add to keychain
echo ""
echo "💾 Adding to keychain..."
security add-generic-password \
    -a "$USERNAME" \
    -s "Super Update Service" \
    -l "Super Update Service" \
    -w "$PASSWORD" \
    -U

# Clear password from memory
PASSWORD=""
unset PASSWORD

echo "✅ Credentials added to keychain successfully!"
echo ""
echo "The GlobalProtect downloader will now use these credentials automatically."

