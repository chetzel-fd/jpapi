#!/bin/bash
# Quick Deploy Script for Software Installation via Jamf Pro Config Profiles
# This script provides easy commands for common deployment scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default environment
ENVIRONMENT="sandbox"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Quick Deploy Script for Software Installation via Jamf Pro Config Profiles

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    chrome-ext EXTENSION_ID [URL]           Install Chrome extension
    firefox-ext EXTENSION_ID [NAME]         Install Firefox extension
    safari-ext EXTENSION_ID [NAME]          Install Safari extension
    edge-ext EXTENSION_ID [URL]             Install Microsoft Edge extension
    
    install-app APP_NAME [LABEL]            Install app with Installomator
    pppc APP_NAME BUNDLE_ID PERMISSIONS     Create PPPC permissions profile
    
    batch-deploy CONFIG_FILE                Deploy from configuration file
    list-apps                               List available Installomator apps
    
    help                                    Show this help message

EXAMPLES:
    # Install Chrome extension
    $0 chrome-ext abc123def456 https://example.com/manifest.json
    
    # Install Firefox extension
    $0 firefox-ext xyz789 "My Extension"
    
    # Install app with Installomator
    $0 install-app "Slack" slack
    
    # Create PPPC profile
    $0 pppc "Chrome" com.google.Chrome "full_disk_access,camera,microphone"
    
    # Batch deploy
    $0 batch-deploy deployment_config.json
    
    # List available apps
    $0 list-apps

OPTIONS:
    --environment, -e ENV    Jamf Pro environment (sandbox|production) [default: sandbox]
    --help, -h               Show this help message

EOF
}

# Function to check if Python script exists
check_script() {
    local script_path="$PROJECT_DIR/software_install_via_config_profile.py"
    if [[ ! -f "$script_path" ]]; then
        print_error "Main script not found: $script_path"
        exit 1
    fi
}

# Function to run Python script
run_script() {
    local script_path="$PROJECT_DIR/software_install_via_config_profile.py"
    python3 "$script_path" --environment "$ENVIRONMENT" "$@"
}

# Function to run deployment script
run_deploy_script() {
    local script_path="$PROJECT_DIR/deploy_software_installation.py"
    if [[ ! -f "$script_path" ]]; then
        print_error "Deployment script not found: $script_path"
        exit 1
    fi
    python3 "$script_path" --environment "$ENVIRONMENT" "$@"
}

# Function to install Chrome extension
install_chrome_extension() {
    local extension_id="$1"
    local extension_url="$2"
    
    print_status "Installing Chrome extension: $extension_id"
    
    if [[ -n "$extension_url" ]]; then
        run_script install-extension --app Chrome --extension-id "$extension_id" --extension-url "$extension_url"
    else
        run_script install-extension --app Chrome --extension-id "$extension_id"
    fi
}

# Function to install Firefox extension
install_firefox_extension() {
    local extension_id="$1"
    local extension_name="$2"
    
    print_status "Installing Firefox extension: $extension_id"
    
    if [[ -n "$extension_name" ]]; then
        run_script install-extension --app Firefox --extension-id "$extension_id" --extension-name "$extension_name"
    else
        run_script install-extension --app Firefox --extension-id "$extension_id"
    fi
}

# Function to install Safari extension
install_safari_extension() {
    local extension_id="$1"
    local extension_name="$2"
    
    print_status "Installing Safari extension: $extension_id"
    
    if [[ -n "$extension_name" ]]; then
        run_script install-extension --app Safari --extension-id "$extension_id" --extension-name "$extension_name"
    else
        run_script install-extension --app Safari --extension-id "$extension_id"
    fi
}

# Function to install Edge extension
install_edge_extension() {
    local extension_id="$1"
    local extension_url="$2"
    
    print_status "Installing Edge extension: $extension_id"
    
    if [[ -n "$extension_url" ]]; then
        run_script install-extension --app Edge --extension-id "$extension_id" --extension-url "$extension_url"
    else
        run_script install-extension --app Edge --extension-id "$extension_id"
    fi
}

# Function to install app with Installomator
install_app() {
    local app_name="$1"
    local label="$2"
    
    print_status "Installing app with Installomator: $app_name"
    
    if [[ -n "$label" ]]; then
        run_script install-app --app-name "$app_name" --method installomator --label "$label"
    else
        run_script install-app --app-name "$app_name" --method installomator
    fi
}

# Function to create PPPC profile
create_pppc_profile() {
    local app_name="$1"
    local bundle_id="$2"
    local permissions="$3"
    
    print_status "Creating PPPC profile: $app_name"
    
    run_script create-pppc --app-name "$app_name" --bundle-id "$bundle_id" --permissions "$permissions"
}

# Function to batch deploy
batch_deploy() {
    local config_file="$1"
    
    if [[ ! -f "$config_file" ]]; then
        print_error "Configuration file not found: $config_file"
        exit 1
    fi
    
    print_status "Batch deploying from: $config_file"
    run_deploy_script batch-deploy --config "$config_file"
}

# Function to list available apps
list_apps() {
    print_status "Available Installomator apps:"
    echo ""
    echo "Popular Apps:"
    echo "  - Slack (label: slack)"
    echo "  - Zoom (label: zoom)"
    echo "  - Google Chrome (label: googlechrome)"
    echo "  - Firefox (label: firefox)"
    echo "  - Microsoft Edge (label: microsoftedge)"
    echo "  - Microsoft Teams (label: microsoftteams)"
    echo "  - Adobe Acrobat Reader (label: adobeacrobatreader)"
    echo "  - Microsoft Office (label: microsoftoffice)"
    echo ""
    echo "For a complete list, visit: https://github.com/Installomator/Installomator"
}

# Main script logic
main() {
    # Check if main script exists
    check_script
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment|-e)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            chrome-ext)
                install_chrome_extension "$2" "$3"
                exit $?
                ;;
            firefox-ext)
                install_firefox_extension "$2" "$3"
                exit $?
                ;;
            safari-ext)
                install_safari_extension "$2" "$3"
                exit $?
                ;;
            edge-ext)
                install_edge_extension "$2" "$3"
                exit $?
                ;;
            install-app)
                install_app "$2" "$3"
                exit $?
                ;;
            pppc)
                create_pppc_profile "$2" "$3" "$4"
                exit $?
                ;;
            batch-deploy)
                batch_deploy "$2"
                exit $?
                ;;
            list-apps)
                list_apps
                exit 0
                ;;
            help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown command: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # If no command provided, show usage
    show_usage
    exit 1
}

# Run main function with all arguments
main "$@"













