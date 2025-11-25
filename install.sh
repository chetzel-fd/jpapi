#!/bin/bash
# =============================================================================
# JPAPI Easy Installer Script
# =============================================================================
# One-command installation for JPAPI from GitHub
# Usage: curl -sSL https://raw.githubusercontent.com/chetzel-fd/jpapi/main/install.sh | bash
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REPO_URL="https://github.com/chetzel-fd/jpapi.git"

# Detect actual user (handle sudo/root cases)
if [ "$EUID" -eq 0 ] && [ -n "${SUDO_USER:-}" ]; then
    # Running as root via sudo - use the original user
    ACTUAL_USER="$SUDO_USER"
    ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)
    print_warning "Running as root via sudo. Installing for user: $ACTUAL_USER"
elif [ "$EUID" -eq 0 ]; then
    # Running as root directly - warn
    print_error "Running as root is not recommended!"
    print_error "Please run this script as a regular user, or use sudo -u <user>"
    print_error "If you continue, JPAPI will be installed in /root/.jpapi"
    ACTUAL_USER="root"
    ACTUAL_HOME="$HOME"
else
    # Running as regular user
    ACTUAL_USER="$USER"
    ACTUAL_HOME="$HOME"
fi

INSTALL_DIR="$ACTUAL_HOME/.jpapi"
VENV_DIR="$INSTALL_DIR/venv"

print_header() {
    echo -e "${BLUE}🚀 JPAPI Easy Installer${NC}"
    echo "================================"
    echo -e "${YELLOW}Installing JPAPI from GitHub...${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check permissions
check_permissions() {
    echo -e "${BLUE}ℹ️  Checking permissions...${NC}"
    
    # Check if we can write to actual home directory
    if [ ! -w "$ACTUAL_HOME" ]; then
        echo -e "${RED}❌ Cannot write to home directory: $ACTUAL_HOME${NC}"
        echo -e "${RED}❌ Please check file ownership and permissions${NC}"
        exit 1
    fi
    
    # Check if we can create .local/bin directory
    if [ ! -w "$ACTUAL_HOME" ] && [ ! -d "$ACTUAL_HOME/.local" ]; then
        echo -e "${RED}❌ Cannot create ~/.local directory${NC}"
        exit 1
    fi
    
    # If running as root for another user, fix ownership of existing installation
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ] && [ -d "$INSTALL_DIR" ]; then
        print_warning "Fixing ownership of existing installation for user: $ACTUAL_USER"
        chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Permissions look good${NC}"
}

# Check if Python 3 is available and version is compatible
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
        
        # Check if version is >= 3.8
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
            print_error "Python 3.8+ is required, but found Python $PYTHON_VERSION"
            echo "Please install Python 3.8+ from https://python.org"
            exit 1
        fi
        
        print_success "Python $PYTHON_VERSION found (compatible)"
        return 0
    else
        print_error "Python 3 is required but not found"
        echo "Please install Python 3.8+ from https://python.org"
        exit 1
    fi
}

# Check if pip is available
check_pip() {
    if command -v pip3 >/dev/null 2>&1; then
        print_success "pip3 found"
        return 0
    elif python3 -m pip --version >/dev/null 2>&1; then
        print_success "pip found via python3 -m pip"
        return 0
    else
        print_error "pip is required but not found"
        echo "Please install pip: https://pip.pypa.io/en/stable/installation/"
        exit 1
    fi
}

# Install system dependencies
install_dependencies() {
    print_warning "Checking system dependencies..."
    
    # Check for jq
    if ! command -v jq >/dev/null 2>&1; then
        print_warning "jq not found, installing..."
        if command -v brew >/dev/null 2>&1; then
            brew install jq
        elif command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update && sudo apt-get install -y jq
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y jq
        else
            print_warning "Please install jq manually: https://stedolan.github.io/jq/"
        fi
    else
        print_success "jq found"
    fi
    
    # Check for curl
    if ! command -v curl >/dev/null 2>&1; then
        print_error "curl is required but not found"
        exit 1
    else
        print_success "curl found"
    fi
}

# Clone or update repository
setup_repository() {
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "JPAPI directory exists, updating..."
        cd "$INSTALL_DIR"
        git pull origin main
    else
        print_warning "Cloning JPAPI repository..."
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    
    # Fix ownership if running as root for another user
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
        print_warning "Fixing ownership of repository for user: $ACTUAL_USER"
        chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR" 2>/dev/null || true
    fi
    
    print_success "Repository ready"
}

# Create virtual environment
setup_venv() {
    print_warning "Setting up Python virtual environment..."
    
    # Get system Python version
    SYSTEM_PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    
    if [[ -d "$VENV_DIR" ]]; then
        # Check if venv Python version matches system Python version
        if [[ -f "$VENV_DIR/bin/python3" ]]; then
            VENV_PYTHON_VERSION=$("$VENV_DIR/bin/python3" --version 2>/dev/null | cut -d' ' -f2)
            
            if [[ "$VENV_PYTHON_VERSION" != "$SYSTEM_PYTHON_VERSION" ]]; then
                print_warning "Python version mismatch detected!"
                print_warning "System Python: $SYSTEM_PYTHON_VERSION"
                print_warning "Venv Python: $VENV_PYTHON_VERSION"
                print_warning "Recreating virtual environment with system Python version..."
                
                # Remove old venv
                rm -rf "$VENV_DIR"
                
                # Create new venv with system Python
                python3 -m venv "$VENV_DIR"
            else
                print_warning "Virtual environment exists, updating..."
            fi
        else
            print_warning "Virtual environment exists but appears corrupted, recreating..."
            rm -rf "$VENV_DIR"
            python3 -m venv "$VENV_DIR"
        fi
    else
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Verify venv Python version matches system
    VENV_PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    if [[ "$VENV_PYTHON_VERSION" != "$SYSTEM_PYTHON_VERSION" ]]; then
        print_error "Virtual environment Python version ($VENV_PYTHON_VERSION) does not match system Python ($SYSTEM_PYTHON_VERSION)"
        exit 1
    fi
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Fix ownership if running as root for another user
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
        print_warning "Fixing ownership of virtual environment for user: $ACTUAL_USER"
        chown -R "$ACTUAL_USER:$ACTUAL_USER" "$VENV_DIR" 2>/dev/null || true
    fi
    
    print_success "Virtual environment ready (Python $VENV_PYTHON_VERSION)"
}

# Install JPAPI
install_jpapi() {
    print_warning "Installing JPAPI..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install in editable mode with error checking
    print_info "Running: pip install -e ."
    if ! pip install -e . 2>&1 | tee /tmp/jpapi-install.log; then
        print_error "pip install failed. Check /tmp/jpapi-install.log for details"
        echo ""
        print_error "Last 20 lines of install log:"
        tail -20 /tmp/jpapi-install.log
        exit 1
    fi
    
    # Verify entry point was created
    if [ ! -f "$VENV_DIR/bin/jpapi" ]; then
        print_error "jpapi entry point was not created in virtual environment"
        print_error "This usually indicates a setup.py configuration issue"
        print_error "Expected: $VENV_DIR/bin/jpapi"
        exit 1
    fi
    
    # Make executable if needed
    chmod +x "$VENV_DIR/bin/jpapi"
    
    # Fix ownership if running as root for another user
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
        print_warning "Fixing ownership of installation for user: $ACTUAL_USER"
        chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR" 2>/dev/null || true
    fi
    
    print_success "JPAPI installed successfully"
}

# Create symlink for easy access
create_symlink() {
    print_warning "Creating symlink for easy access..."
    
    # Use actual user's home directory
    LOCAL_BIN_DIR="$ACTUAL_HOME/.local/bin"
    
    # Create ~/.local/bin if it doesn't exist
    mkdir -p "$LOCAL_BIN_DIR"
    
    # Fix permissions if running as root for another user
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
        chown -R "$ACTUAL_USER:$ACTUAL_USER" "$LOCAL_BIN_DIR" 2>/dev/null || true
    fi
    
    # Create symlink
    ln -sf "$VENV_DIR/bin/jpapi" "$LOCAL_BIN_DIR/jpapi"
    
    # Fix symlink ownership if needed
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
        chown -h "$ACTUAL_USER:$ACTUAL_USER" "$LOCAL_BIN_DIR/jpapi" 2>/dev/null || true
    fi
    
    # Add to PATH if not already there
    if ! echo "$PATH" | grep -q "$ACTUAL_HOME/.local/bin"; then
        # Determine which shell config files to update
        SHELL_CONFIGS=()
        if [ -f "$ACTUAL_HOME/.bashrc" ] || [ ! -f "$ACTUAL_HOME/.bashrc" ]; then
            SHELL_CONFIGS+=("$ACTUAL_HOME/.bashrc")
        fi
        if [ -f "$ACTUAL_HOME/.zshrc" ] || [ ! -f "$ACTUAL_HOME/.zshrc" ]; then
            SHELL_CONFIGS+=("$ACTUAL_HOME/.zshrc")
        fi
        
        # Add PATH export to shell configs
        for config_file in "${SHELL_CONFIGS[@]}"; do
            if [ -w "$config_file" ] || [ ! -f "$config_file" ]; then
                # Check if already added
                if ! grep -q '\.local/bin' "$config_file" 2>/dev/null; then
                    echo '' >> "$config_file"
                    echo '# JPAPI - Add to PATH' >> "$config_file"
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$config_file"
                    
                    # Fix ownership if running as root for another user
                    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
                        chown "$ACTUAL_USER:$ACTUAL_USER" "$config_file" 2>/dev/null || true
                    fi
                    
                    print_success "Added ~/.local/bin to PATH in $(basename "$config_file")"
                fi
            else
                print_warning "Cannot write to $config_file (permission denied)"
            fi
        done
        
        if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
            print_warning "Running as root - PATH updated for user: $ACTUAL_USER"
            print_warning "User $ACTUAL_USER should run: source ~/.bashrc (or restart terminal)"
        else
            print_warning "Please run: source ~/.bashrc (or restart your terminal)"
        fi
        
        print_warning "If PATH is not set, manually add this to your shell config:"
        print_warning "export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    
    print_success "Symlink created at $LOCAL_BIN_DIR/jpapi"
    
    # Show usage instructions
    echo
    print_info "Installation complete! To use jpapi:"
    echo
    echo "  Option 1: Use the full path:"
    echo "    $VENV_DIR/bin/jpapi --help"
    echo
    echo "  Option 2: Add to PATH and reload shell:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "    source ~/.bashrc  # or source ~/.zshrc"
    echo "    jpapi --help"
    echo
    echo "  Option 3: Create an alias:"
    echo "    alias jpapi=\"$VENV_DIR/bin/jpapi\""
    echo
}

# Test installation
test_installation() {
    print_warning "Testing installation..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # First, verify entry point exists
    if [ ! -f "$VENV_DIR/bin/jpapi" ]; then
        print_error "Entry point file not found: $VENV_DIR/bin/jpapi"
        print_error "Installation may have failed silently"
        exit 1
    fi
    
    # Test jpapi command and capture output
    print_info "Running: $VENV_DIR/bin/jpapi --version"
    OUTPUT=$("$VENV_DIR/bin/jpapi" --version 2>&1)
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        print_success "JPAPI is working correctly"
        echo "Version output: $OUTPUT"
    else
        print_error "JPAPI installation test failed (exit code: $EXIT_CODE)"
        echo
        print_error "Error output:"
        echo "$OUTPUT"
        echo
        print_info "Checking entry point script:"
        head -10 "$VENV_DIR/bin/jpapi"
        echo
        print_info "Attempting to import jpapi_main module directly:"
        python3 -c "import jpapi_main; print('Import successful')" 2>&1 || print_error "Direct import also failed"
        echo
        print_info "Checking Python path:"
        python3 -c "import sys; print('\n'.join(sys.path))" 2>&1
        exit 1
    fi
}

# Main installation function
main() {
    print_header
    
    # Check permissions first
    check_permissions
    
    # Check prerequisites
    check_python
    check_pip
    install_dependencies
    
    # Setup repository
    setup_repository
    
    # Setup virtual environment
    setup_venv
    
    # Install JPAPI
    install_jpapi
    
    # Create symlink
    create_symlink
    
    # Test installation
    test_installation
    
    echo
    print_success "🎉 JPAPI installed successfully!"
    echo
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
        echo "⚠️  Installed for user: $ACTUAL_USER"
        echo "⚠️  User $ACTUAL_USER should run the following commands (not as root):"
        echo
    fi
    echo "JPAPI is installed in: $INSTALL_DIR"
    echo "Virtual environment: $VENV_DIR"
    echo "Symlink location: $ACTUAL_HOME/.local/bin/jpapi"
    echo
    echo "Next steps:"
    echo "1. To use jpapi, either:"
    echo "   - Use full path: $VENV_DIR/bin/jpapi setup"
    echo "   - Or add to PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
        echo "   - Then user $ACTUAL_USER should reload shell: source ~/.bashrc (or source ~/.zshrc)"
    else
        echo "   - Then reload shell: source ~/.bashrc (or source ~/.zshrc)"
    fi
    echo
    echo "2. Run: jpapi setup (or $VENV_DIR/bin/jpapi setup)"
    echo "3. Configure your JAMF Pro credentials"
    echo "4. Test with: jpapi --help"
    echo
}

# Run main function
main "$@"
