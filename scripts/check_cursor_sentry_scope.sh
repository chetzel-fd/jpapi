#!/bin/zsh

# Cursor Sentry Scope File Checker
# This script checks all users who have used Cursor and displays their sentry scope file contents
# Based on the extension attribute logic for finding users
# Compatible with Jamf Pro (runs as root)

# Check if Cursor is installed first
if [ ! -d "/Applications/Cursor.app" ]; then
    echo "❌ Cursor is not installed"
    exit 1
fi

# Determine if we're running as root (Jamf execution)
if [ "$(id -u)" -eq 0 ]; then
    # Running as root - sudo -u will work fine
    RUN_AS_ROOT=true
else
    # Running as regular user
    RUN_AS_ROOT=false
fi

# Function to check if a user has ever used Cursor
check_cursor_usage() {
    local user="$1"
    local userDir="/Users/$user"
    
    # Check for various indicators that Cursor has been used
    local indicators=(
        "$userDir/Library/Application Support/Cursor"
        "$userDir/Library/Preferences/com.todesktop.230313mzl4w4u92.plist"
        "$userDir/Library/Logs/Cursor"
        "$userDir/Library/Caches/com.todesktop.230313mzl4w4u92"
    )
    
    for indicator in "${indicators[@]}"; do
        if [ -e "$indicator" ]; then
            return 0  # User has used Cursor
        fi
    done
    
    return 1  # User has not used Cursor
}

# Function to get cached email from database (like extension attribute does)
get_cached_email() {
    local user="$1"
    local userDir="/Users/$user"
    local email=""
    
    # Primary location: state.vscdb
    local dbPath="$userDir/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
    if [ -f "$dbPath" ]; then
        # When running as root (Jamf), use sudo -u to access user's files
        # When running as regular user, try direct access first, then sudo if needed
        if [ "$RUN_AS_ROOT" = true ]; then
            email=$(sudo -u "$user" sqlite3 "$dbPath" "SELECT value FROM ItemTable WHERE key = 'cursorAuth/cachedEmail';" 2>/dev/null)
        else
            # Try as current user first
            email=$(sqlite3 "$dbPath" "SELECT value FROM ItemTable WHERE key = 'cursorAuth/cachedEmail';" 2>/dev/null)
            if [ $? -ne 0 ] || [ -z "$email" ]; then
                # Fallback to sudo if direct access failed
                email=$(sudo -u "$user" sqlite3 "$dbPath" "SELECT value FROM ItemTable WHERE key = 'cursorAuth/cachedEmail';" 2>/dev/null)
            fi
        fi
        if [ $? -eq 0 ] && [ -n "$email" ]; then
            echo "$email"
            return 0
        fi
    fi
    
    # Alternative location: workspace storage
    local workspaceDbPath="$userDir/Library/Application Support/Cursor/User/workspaceStorage"
    if [ -d "$workspaceDbPath" ]; then
        for workspaceDb in "$workspaceDbPath"/*/state.vscdb; do
            if [ -f "$workspaceDb" ]; then
                if [ "$RUN_AS_ROOT" = true ]; then
                    email=$(sudo -u "$user" sqlite3 "$workspaceDb" "SELECT value FROM ItemTable WHERE key = 'cursorAuth/cachedEmail';" 2>/dev/null)
                else
                    email=$(sqlite3 "$workspaceDb" "SELECT value FROM ItemTable WHERE key = 'cursorAuth/cachedEmail';" 2>/dev/null)
                    if [ $? -ne 0 ] || [ -z "$email" ]; then
                        email=$(sudo -u "$user" sqlite3 "$workspaceDb" "SELECT value FROM ItemTable WHERE key = 'cursorAuth/cachedEmail';" 2>/dev/null)
                    fi
                fi
                if [ $? -eq 0 ] && [ -n "$email" ]; then
                    echo "$email"
                    return 0
                fi
            fi
        done
    fi
    
    # Check preferences file (must run as user, not root)
    local prefsPath="$userDir/Library/Preferences/com.todesktop.230313mzl4w4u92.plist"
    if [ -f "$prefsPath" ]; then
        # Run defaults as the user to access user preferences
        email=$(sudo -u "$user" defaults read "$prefsPath" "cachedEmail" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$email" ]; then
            echo "$email"
            return 0
        fi
    fi
    
    return 1
}

# Function to display database and sentry scope file for a user
display_cursor_files() {
    local user="$1"
    local userDir="/Users/$user"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "👤 User: $user"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check database for cached email (like extension attribute does)
    echo ""
    echo "📊 Database Email Check (Extension Attribute Method):"
    echo "────────────────────────────────────────────────────────────────────────────"
    cachedEmail=$(get_cached_email "$user")
    if [ -n "$cachedEmail" ]; then
        echo "✅ Cached Email found: $cachedEmail"
        if [[ "$cachedEmail" == *"@fanduel.com"* ]]; then
            echo "   Status: ✅ Compliant (company email)"
        else
            echo "   Status: ⚠️  Non-Compliant (personal email)"
        fi
    else
        echo "❌ No cached email found in database"
    fi
    
    # Display sentry scope file
    echo ""
    echo "📄 Sentry Scope File:"
    echo "────────────────────────────────────────────────────────────────────────────"
    local sentry_path="$userDir/Library/Application Support/Cursor/sentry/scope_v3.json"
    echo "📁 File path: $sentry_path"
    
    if [[ -f "$sentry_path" ]]; then
        echo "✅ File found!"
        echo ""
        echo "📄 File contents:"
        echo "────────────────────────────────────────────────────────────────────────────"
        # When running as root (Jamf), use sudo -u to access user's files
        if [ "$RUN_AS_ROOT" = true ]; then
            sudo -u "$user" cat "$sentry_path" 2>/dev/null
            cat_exit=$?
        else
            # Try as current user first
            cat "$sentry_path" 2>/dev/null
            cat_exit=$?
            if [ $cat_exit -ne 0 ]; then
                # Fallback to sudo if direct access failed
                sudo -u "$user" cat "$sentry_path" 2>/dev/null
                cat_exit=$?
            fi
        fi
        
        if [ $cat_exit -eq 0 ]; then
            echo "────────────────────────────────────────────────────────────────────────────"
            echo ""
            echo "📊 File size: $(stat -f%z "$sentry_path" 2>/dev/null || echo "unknown") bytes"
            echo "🕐 Last modified: $(stat -f%Sm "$sentry_path" 2>/dev/null || echo "unknown")"
            
            # Check if sentry file contains @fanduel.com
            if [ "$RUN_AS_ROOT" = true ]; then
                if sudo -u "$user" grep -qi "@fanduel\.com" "$sentry_path" 2>/dev/null; then
                    echo "✅ Sentry file contains @fanduel.com"
                else
                    echo "⚠️  Sentry file does not contain @fanduel.com"
                fi
            else
                if grep -qi "@fanduel\.com" "$sentry_path" 2>/dev/null || sudo -u "$user" grep -qi "@fanduel\.com" "$sentry_path" 2>/dev/null; then
                    echo "✅ Sentry file contains @fanduel.com"
                else
                    echo "⚠️  Sentry file does not contain @fanduel.com"
                fi
            fi
        else
            echo "❌ Error reading file (permission denied or file error)"
        fi
    else
        echo "❌ File not found: $sentry_path"
        echo ""
        echo "🔍 Checking if Cursor directory exists..."
        
        if [[ -d "$userDir/Library/Application Support/Cursor" ]]; then
            echo "✅ Cursor directory exists"
            echo "📂 Contents of Cursor directory:"
            ls -la "$userDir/Library/Application Support/Cursor/" 2>/dev/null | head -20
            
            if [[ -d "$userDir/Library/Application Support/Cursor/sentry" ]]; then
                echo ""
                echo "📂 Contents of sentry directory:"
                ls -la "$userDir/Library/Application Support/Cursor/sentry/" 2>/dev/null
            else
                echo "❌ Sentry directory not found"
            fi
        else
            echo "❌ Cursor directory not found"
        fi
    fi
}

# Get list of user directories
userDirs=$(ls /Users/ 2>/dev/null | grep -v '^\.' | grep -v 'Shared' | grep -v 'Guest')

# If no user directories found, exit
if [ -z "$userDirs" ]; then
    echo "❌ No user directories found"
    exit 1
fi

echo "🔍 Checking Cursor Sentry Scope files for all users"
echo "============================================================"

users_found=0
users_with_sentry=0

# Check each user directory
for user in $(ls /Users/ 2>/dev/null | grep -v '^\.' | grep -v 'Shared' | grep -v 'Guest'); do
    # Skip if user directory doesn't exist or isn't accessible
    if [ ! -d "/Users/$user" ]; then
        continue
    fi
    
    # Check if user has ever used Cursor
    if check_cursor_usage "$user"; then
        users_found=$((users_found + 1))
        sentryPath="/Users/$user/Library/Application Support/Cursor/sentry/scope_v3.json"
        
        if [ -f "$sentryPath" ]; then
            users_with_sentry=$((users_with_sentry + 1))
        fi
        
        # Display database and sentry scope file for this user
        display_cursor_files "$user"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "   Users who have used Cursor: $users_found"
echo "   Users with sentry scope file: $users_with_sentry"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $users_found -eq 0 ]; then
    echo "ℹ️  No users have used Cursor yet"
    exit 0
fi

exit 0

