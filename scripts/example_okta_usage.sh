#!/bin/bash
# Example: Using Okta Authentication in a Jamf Script
# 
# This demonstrates how to use okta_auth_embedded.sh in your own Jamf scripts
# to access Okta-protected resources.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the Okta authentication script (embedded implementation)
source "$SCRIPT_DIR/okta_auth_embedded.sh"

echo "🔐 Okta Authentication Example"
echo "=============================="
echo ""

# Configuration
OKTA_INSTANCE="${OKTA_INSTANCE:-fanduel}"
USERNAME="${USERNAME:-}"  # Will be auto-detected from keychain if empty

# Get username if not provided
if [ -z "$USERNAME" ]; then
    USERNAME=$(get_username_from_keychain)
    echo "📋 Detected username: $USERNAME"
fi

# Authenticate to Okta
echo ""
echo "🔐 Authenticating to Okta..."
if okta_auth_embedded "$OKTA_INSTANCE" "$USERNAME" ""; then
    echo "✅ Authentication successful!"
    echo ""
    
    # Example 1: List available apps
    echo "📱 Listing available Okta apps..."
    echo "-------------------------------"
    okta_list_apps | while IFS='|' read -r label url; do
        echo "  • $label"
    done
    echo ""
    
    # Example 2: Make an authenticated request
    # Uncomment and modify the URL to test:
    # echo "📥 Making authenticated request..."
    # okta_request "https://protected-resource.example.com/api/data" "GET" "/tmp/response.json"
    # if [ $? -eq 0 ]; then
    #     echo "✅ Request successful"
    #     cat /tmp/response.json
    # fi
    
    # Example 3: Connect to a specific app
    # Uncomment and modify the app URL to test:
    # echo "🔗 Connecting to Okta app..."
    # okta_connect_to_app "https://app.example.com/launch"
    # if [ $? -eq 0 ]; then
    #     echo "✅ Connected to app successfully"
    # fi
    
    echo ""
    echo "🎉 Example completed successfully!"
else
    echo "❌ Authentication failed"
    exit 1
fi

