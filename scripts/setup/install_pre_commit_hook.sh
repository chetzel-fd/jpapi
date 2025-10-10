#!/bin/bash

# =============================================================================
# Pre-commit Hook Installation Script
# =============================================================================
# This script installs a comprehensive pre-commit hook to prevent sensitive
# data from being committed to version control
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
    echo -e "${BLUE}🔒 Installing Pre-commit Security Hook${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
    echo
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ SUCCESS:${NC} $1"
}

print_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository. Please run this from the root of your git repository."
        exit 1
    fi
    print_success "Git repository detected"
}

# Create hooks directory if it doesn't exist
create_hooks_directory() {
    local hooks_dir=".git/hooks"
    if [[ ! -d "$hooks_dir" ]]; then
        mkdir -p "$hooks_dir"
        print_info "Created hooks directory"
    fi
}

# Install pre-commit hook
install_pre_commit_hook() {
    local hook_file=".git/hooks/pre-commit"
    local script_file="scripts/pre_commit_sanitize.sh"
    
    if [[ ! -f "$script_file" ]]; then
        print_error "Pre-commit script not found: $script_file"
        exit 1
    fi
    
    # Make the script executable
    chmod +x "$script_file"
    
    # Create the pre-commit hook
    cat > "$hook_file" << 'EOF'
#!/bin/bash

# =============================================================================
# Pre-commit Hook for JPAPI
# =============================================================================
# This hook runs security checks before allowing commits
# =============================================================================

set -euo pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Run the sanitization script
if [[ -f "$PROJECT_ROOT/scripts/pre_commit_sanitize.sh" ]]; then
    "$PROJECT_ROOT/scripts/pre_commit_sanitize.sh"
else
    echo "❌ Pre-commit sanitization script not found"
    exit 1
fi
EOF

    # Make the hook executable
    chmod +x "$hook_file"
    
    print_success "Pre-commit hook installed"
}

# Install commit-msg hook for additional security
install_commit_msg_hook() {
    local hook_file=".git/hooks/commit-msg"
    
    cat > "$hook_file" << 'EOF'
#!/bin/bash

# =============================================================================
# Commit Message Hook for JPAPI
# =============================================================================
# This hook validates commit messages for security
# =============================================================================

set -euo pipefail

# Check commit message for sensitive patterns
check_commit_message() {
    local commit_msg="$1"
    
    # Patterns to check for in commit messages
    local sensitive_patterns=(
        'fanduel'
        'FanDuel'
        'charles\.hetzel'
        'client_secret'
        'api_key'
        'token'
        'password'
        'credential'
    )
    
    for pattern in "${sensitive_patterns[@]}"; do
        if echo "$commit_msg" | grep -qi "$pattern"; then
            echo "❌ COMMIT MESSAGE BLOCKED: Contains sensitive information: $pattern"
            echo "   Please remove sensitive information from your commit message"
            exit 1
        fi
    done
}

# Read commit message from file
if [[ -f "$1" ]]; then
    commit_msg=$(cat "$1")
    check_commit_message "$commit_msg"
fi

exit 0
EOF

    # Make the hook executable
    chmod +x "$hook_file"
    
    print_success "Commit message hook installed"
}

# Test the installation
test_installation() {
    print_info "Testing installation..."
    
    # Test pre-commit hook
    if [[ -x ".git/hooks/pre-commit" ]]; then
        print_success "Pre-commit hook is executable"
    else
        print_error "Pre-commit hook is not executable"
        exit 1
    fi
    
    # Test commit-msg hook
    if [[ -x ".git/hooks/commit-msg" ]]; then
        print_success "Commit message hook is executable"
    else
        print_error "Commit message hook is not executable"
        exit 1
    fi
    
    print_success "Installation test passed"
}

# Main execution
main() {
    print_header
    
    # Check if we're in a git repository
    check_git_repo
    
    # Create hooks directory
    create_hooks_directory
    
    # Install hooks
    install_pre_commit_hook
    install_commit_msg_hook
    
    # Test installation
    test_installation
    
    echo
    print_success "Pre-commit hooks installed successfully!"
    echo
    print_info "The following security measures are now active:"
    echo "  • Pre-commit hook checks for sensitive data in staged files"
    echo "  • Commit message hook prevents sensitive info in commit messages"
    echo "  • Automatic blocking of commits containing sensitive patterns"
    echo
    print_info "To test the hooks:"
    echo "  git add ."
    echo "  git commit -m 'Test commit'"
    echo
    print_info "To disable hooks temporarily:"
    echo "  git commit --no-verify"
    echo
    print_warning "Remember: Hooks can be bypassed with --no-verify, but this is not recommended"
}

# Run main function
main "$@"