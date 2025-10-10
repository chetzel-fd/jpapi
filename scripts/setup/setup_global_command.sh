#!/bin/bash

# =============================================================================
# Setup Global JPAPI Command
# =============================================================================
# This script sets up jpapi to be executable from anywhere in the terminal
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE}🌐 Setting up Global JPAPI Command${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
    echo
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ SUCCESS:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
}

# Get the current directory (should be jpapi project root)
JPAPI_DIR="$(pwd)"

print_header

# Create the global command script
print_info "Creating global command script..."
cat > jpapi-global << 'EOF'
#!/bin/bash

# =============================================================================
# JPAPI - JAMF Pro API Toolkit - Global Command
# =============================================================================
# This script allows you to run jpapi from anywhere in the terminal
# =============================================================================

# JPAPI project directory
JPAPI_DIR="/Users/charles.hetzel/cursor/jpapi"

# Check if JPAPI directory exists
if [[ ! -d "$JPAPI_DIR" ]]; then
    echo "❌ Error: JPAPI directory not found at $JPAPI_DIR"
    echo "Please check that the jpapi project is in the correct location."
    exit 1
fi

# Change to JPAPI directory
cd "$JPAPI_DIR"

# Check if jpapi script exists
if [[ -f "jpapi" ]]; then
    # Run the jpapi script
    exec ./jpapi "$@"
elif [[ -f "src/cli/main.py" ]]; then
    # Run the Python CLI
    exec python3 src/cli/main.py "$@"
else
    echo "❌ Error: No JPAPI executable found"
    echo "Expected files: jpapi or src/cli/main.py"
    exit 1
fi
EOF

# Make it executable
chmod +x jpapi-global
print_success "Created jpapi-global script"

# Create symlink in home directory
print_info "Creating symlink in home directory..."
ln -sf "$JPAPI_DIR/jpapi-global" ~/jpapi
print_success "Created symlink: ~/jpapi"

# Add home directory to PATH if not already there
print_info "Adding home directory to PATH..."
if ! grep -q 'export PATH="$HOME:$PATH"' ~/.zshrc 2>/dev/null; then
    echo 'export PATH="$HOME:$PATH"' >> ~/.zshrc
    print_success "Added ~/jpapi to PATH in ~/.zshrc"
else
    print_info "PATH already configured"
fi

# Test the setup
print_info "Testing the setup..."
if [[ -x ~/jpapi ]]; then
    print_success "Global command is executable"
else
    print_error "Global command is not executable"
    exit 1
fi

echo
print_success "Global JPAPI command setup complete!"
echo
print_info "You can now run 'jpapi' from anywhere in the terminal:"
echo "  jpapi --help"
echo "  jpapi list policies"
echo "  jpapi export devices"
echo
print_info "To reload your shell configuration:"
echo "  source ~/.zshrc"
echo "  # or just open a new terminal"
echo
print_warning "Note: The jpapi command will always run from the project directory:"
echo "  $JPAPI_DIR"
