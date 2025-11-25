#!/bin/bash
# Setup Super Update Service Account
# Based on: https://github.com/Macjutsu/super/wiki/Apple-Silicon-Local-Credentials
# Creates a local service account for software update authentication on Apple Silicon Macs

set -e

# Function to create/setup Super Update Service account
setup_super_update_service() {
    local admin_account="${1:-}"
    local admin_password="${2:-}"
    local service_account="${3:-super}"
    local service_password="${4:-}"
    
    echo "🔧 Setting up Super Update Service account..."
    echo "============================================================"
    
    # Check if account already exists
    if dscl . -read "/Users/$service_account" >/dev/null 2>&1; then
        echo "✅ Super Update Service account '$service_account' already exists"
        return 0
    fi
    
    # Generate password if not provided
    if [ -z "$service_password" ]; then
        service_password=$(uuidgen)
    fi
    
    # If admin credentials provided, use them to create the account
    if [ -n "$admin_account" ] && [ -n "$admin_password" ]; then
        echo "🔧 Creating Super Update Service account via admin credentials..."
        
        # Create the service account using sysadminctl (requires admin credentials)
        # Note: This requires PPPC for SystemPolicySysAdminFiles
        if sysadminctl -addUser "$service_account" \
            -fullName "Super Update Service" \
            -password "$service_password" \
            -adminUser "$admin_account" \
            -adminPassword "$admin_password" \
            -hint "" \
            -picture /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/UserIcon.icns \
            >/dev/null 2>&1; then
            
            # Configure the account properties
            # Remove admin privileges (if any were added)
            dseditgroup -o edit -d "$service_account" -t user admin 2>/dev/null || true
            
            # Hide from login window
            defaults write /Library/Preferences/com.apple.loginwindow HiddenUsersList -array-add "$service_account" 2>/dev/null || true
            
            # Set shell to /usr/bin/false (no login)
            dscl . -create "/Users/$service_account" UserShell /usr/bin/false
            
            # Set home directory to /var/empty (no home folder)
            dscl . -create "/Users/$service_account" NFSHomeDirectory /var/empty
            
            # Grant volume ownership (required for software updates)
            diskutil resetUserPermissions / "$service_account" >/dev/null 2>&1 || true
            
            echo "✅ Super Update Service account created successfully"
            echo "   Account: $service_account"
            echo "   Full Name: Super Update Service"
            echo "   Password: (auto-generated)"
            return 0
        else
            echo "⚠️  Failed to create account via sysadminctl. Trying dscl method..."
        fi
    fi
    
    # Fallback: Try direct dscl method (requires root)
    if [ "$(id -u)" -eq 0 ]; then
        echo "🔧 Creating Super Update Service account via dscl (root method)..."
        
        # Create the user account
        dscl . -create "/Users/$service_account"
        dscl . -create "/Users/$service_account" UserShell /usr/bin/false
        dscl . -create "/Users/$service_account" RealName "Super Update Service"
        dscl . -create "/Users/$service_account" UniqueID $(($(dscl . -list /Users UniqueID | awk '{print $2}' | sort -n | tail -1) + 1))
        dscl . -create "/Users/$service_account" PrimaryGroupID 20
        dscl . -create "/Users/$service_account" NFSHomeDirectory /var/empty
        
        # Set password
        dscl . -passwd "/Users/$service_account" "$service_password"
        
        # Hide from login window
        defaults write /Library/Preferences/com.apple.loginwindow HiddenUsersList -array-add "$service_account" 2>/dev/null || true
        
        # Grant volume ownership
        diskutil resetUserPermissions / "$service_account" >/dev/null 2>&1 || true
        
        echo "✅ Super Update Service account created successfully"
        echo "   Account: $service_account"
        echo "   Full Name: Super Update Service"
        echo "   Password: (auto-generated)"
        return 0
    else
        echo "❌ Cannot create Super Update Service account:"
        echo "   - Not running as root"
        echo "   - No admin credentials provided"
        echo ""
        echo "   To create the account, either:"
        echo "   1. Run this script as root/sudo:"
        echo "      sudo $0"
        echo ""
        echo "   2. Provide admin credentials:"
        echo "      ADMIN_USER='admin_account' ADMIN_PASS='admin_password' $0"
        echo ""
        echo "   3. Use the 'super' tool with --auth-service-add-via-admin-account"
        return 1
    fi
}

# Main execution
ADMIN_USER="${ADMIN_USER:-}"
ADMIN_PASS="${ADMIN_PASS:-}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-super}"
SERVICE_PASSWORD="${SERVICE_PASSWORD:-}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --admin-user)
            ADMIN_USER="$2"
            shift 2
            ;;
        --admin-password)
            ADMIN_PASS="$2"
            shift 2
            ;;
        --service-account)
            SERVICE_ACCOUNT="$2"
            shift 2
            ;;
        --service-password)
            SERVICE_PASSWORD="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --admin-user USER        Admin account to use for creation"
            echo "  --admin-password PASS    Admin password"
            echo "  --service-account USER   Service account name (default: super)"
            echo "  --service-password PASS  Service account password (default: auto-generated)"
            echo "  --help, -h               Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  ADMIN_USER              Admin account name"
            echo "  ADMIN_PASS              Admin password"
            echo "  SERVICE_ACCOUNT         Service account name (default: super)"
            echo "  SERVICE_PASSWORD        Service account password (default: auto-generated)"
            echo ""
            echo "Examples:"
            echo "  sudo $0"
            echo "  ADMIN_USER='admin' ADMIN_PASS='pass' $0"
            echo "  $0 --admin-user admin --admin-password pass"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

setup_super_update_service "$ADMIN_USER" "$ADMIN_PASS" "$SERVICE_ACCOUNT" "$SERVICE_PASSWORD"







