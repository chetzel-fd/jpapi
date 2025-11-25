#!/bin/zsh

# Jamf Pro Extension Attribute: Default Browser Detection
# Improved version with better error handling and reliability
# Inspired by: https://github.com/palantir/jamf-pro-scripts/blob/main/extension-attributes/Default%20Browser.sh

# Set strict error handling
set -euo pipefail

# Function to log errors (useful for debugging)
log_error() {
    echo "ERROR: $1" >&2
}

# Function to get logged-in user safely
get_logged_in_user() {
    local user
    if ! user=$(/usr/bin/stat -f%Su "/dev/console" 2>/dev/null); then
        log_error "Failed to get logged-in user"
        return 1
    fi
    
    # Validate user exists
    if ! /usr/bin/dscl . -read "/Users/${user}" NFSHomeDirectory >/dev/null 2>&1; then
        log_error "User '${user}' not found in directory services"
        return 1
    fi
    
    echo "$user"
}

# Function to get user home directory safely
get_user_home() {
    local user="$1"
    local home_dir
    
    if ! home_dir=$(/usr/bin/dscl . -read "/Users/${user}" NFSHomeDirectory 2>/dev/null | /usr/bin/awk '{print $NF}'); then
        log_error "Failed to get home directory for user '${user}'"
        return 1
    fi
    
    # Validate home directory exists
    if [[ ! -d "$home_dir" ]]; then
        log_error "Home directory '${home_dir}' does not exist"
        return 1
    fi
    
    echo "$home_dir"
}

# Function to get default browser
get_default_browser() {
    local home_dir="$1"
    local plist_file="${home_dir}/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist"
    
    # Check if plist file exists
    if [[ ! -f "$plist_file" ]]; then
        log_error "LaunchServices plist file not found: ${plist_file}"
        return 1
    fi
    
    # Get default browser handling https/http schemes
    local browser
    if browser=$(/usr/bin/defaults read "$plist_file" LSHandlers 2>/dev/null | \
                 /usr/bin/grep -A1 -B1 -E "(https|http)" | \
                 /usr/bin/grep "LSHandlerRoleAll" | \
                 /usr/bin/sed 's/.*"\([^"]*\)".*/\1/' | \
                 /usr/bin/head -1); then
        [[ -n "$browser" ]] && echo "$browser" && return 0
    fi
    
    log_error "Could not determine default browser"
    return 1
}

# Main execution
main() {
    local logged_in_user
    local user_home
    local default_browser
    
    # Get logged-in user
    if ! logged_in_user=$(get_logged_in_user); then
        echo "<result>ERROR: Could not determine logged-in user</result>"
        exit 1
    fi
    
    # Get user home directory
    if ! user_home=$(get_user_home "$logged_in_user"); then
        echo "<result>ERROR: Could not determine user home directory</result>"
        exit 1
    fi
    
    # Get default browser
    if ! default_browser=$(get_default_browser "$user_home"); then
        echo "<result>Unknown</result>"
        exit 0
    fi
    
    # Report result
    echo "<result>${default_browser}</result>"
    exit 0
}

# Run main function
main "$@"
