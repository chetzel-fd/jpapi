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
INSTALL_DIR="$HOME/.jpapi"
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
    
    # Check if we can write to home directory
    if [ ! -w "$HOME" ]; then
        echo -e "${RED}❌ Cannot write to home directory: $HOME${NC}"
        echo -e "${RED}❌ Please check file ownership and permissions${NC}"
        exit 1
    fi
    
    # Check if we can create .local/bin directory
    if [ ! -w "$HOME" ] && [ ! -d "$HOME/.local" ]; then
        echo -e "${RED}❌ Cannot create ~/.local directory${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Permissions look good${NC}"
}

# Check if Python 3 is available
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
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
    print_success "Repository ready"
}

# Create virtual environment
setup_venv() {
    print_warning "Setting up Python virtual environment..."
    
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment exists, updating..."
    else
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment ready"
}

# Install JPAPI
install_jpapi() {
    print_warning "Installing JPAPI..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install in editable mode
    pip install -e .
    
    print_success "JPAPI installed successfully"
}

# Create symlink for easy access
create_symlink() {
    print_warning "Creating symlink for easy access..."
    
    # Create ~/.local/bin if it doesn't exist
    mkdir -p "$HOME/.local/bin"
    
    # Create symlink
    ln -sf "$VENV_DIR/bin/jpapi" "$HOME/.local/bin/jpapi"
    
    # Add to PATH if not already there
    if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
        # Try to add to bashrc (with error handling)
        if [ -w "$HOME/.bashrc" ] || [ ! -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            print_success "Added ~/.local/bin to PATH in ~/.bashrc"
        else
            print_warning "Cannot write to ~/.bashrc (permission denied)"
        fi
        
        # Try to add to zshrc (with error handling)
        if [ -w "$HOME/.zshrc" ] || [ ! -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
            print_success "Added ~/.local/bin to PATH in ~/.zshrc"
        else
            print_warning "Cannot write to ~/.zshrc (permission denied)"
        fi
        
        print_warning "Please run: source ~/.bashrc (or restart your terminal)"
        print_warning "If you got permission errors, manually add this to your shell config:"
        print_warning "export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    
    print_success "Symlink created"
}

# Test installation
test_installation() {
    print_warning "Testing installation..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Test jpapi command
    if "$VENV_DIR/bin/jpapi" --version >/dev/null 2>&1; then
        print_success "JPAPI is working correctly"
    else
        print_error "JPAPI installation test failed"
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
    echo "Next steps:"
    echo "1. Run: jpapi setup"
    echo "2. Configure your JAMF Pro credentials"
    echo "3. Test with: jpapi --help"
    echo
    echo "JPAPI is installed in: $INSTALL_DIR"
    echo "Virtual environment: $VENV_DIR"
    echo
    print_warning "If 'jpapi' command not found, run: source ~/.bashrc"
}

# Run main function
main "$@"
