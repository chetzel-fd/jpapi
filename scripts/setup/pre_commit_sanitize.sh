#!/bin/bash

# =============================================================================
# Pre-commit Hook for Automatic Sanitization
# =============================================================================
# Prevents accidental commit of sensitive information
# Install: ln -s ../../scripts/pre_commit_sanitize.sh .git/hooks/pre-commit
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

print_error() {
    echo -e "${RED}🚫 COMMIT BLOCKED:${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1" >&2
}

print_success() {
    echo -e "${GREEN}✅ SECURITY CHECK:${NC} $1" >&2
}

# Check for sensitive patterns in staged files
check_sensitive_patterns() {
    local found_issues=0
    
    # Get list of staged files
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM)
    
    if [[ -z "$staged_files" ]]; then
        return 0
    fi
    
    # Patterns to check for
    local patterns=(
        # JWT tokens
        'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'
        # Bearer tokens
        'Bearer [A-Za-z0-9_-]{20,}'
        'Authorization: Bearer'
        # API credentials
        'client_secret.*[A-Za-z0-9_-]{20,}'
        'client_id.*[A-Za-z0-9_-]{20,}'
        'api_key.*[A-Za-z0-9_-]{20,}'
        # Internal URLs (customize for your organization)
        'yourcompany.*\.jamfcloud\.com'
        # Company references
        'Example Company'
        'Internal toolkit for ExampleCorp'
        # Curl with auth
        'curl.*-H.*Authorization.*Bearer'
    )
    
    echo "🔍 Scanning staged files for sensitive information..."
    
    for file in $staged_files; do
        # Skip binary files
        if file "$file" | grep -q "binary"; then
            continue
        fi
        
        # Check each pattern
        for pattern in "${patterns[@]}"; do
            if git show ":$file" | grep -qE "$pattern"; then
                print_error "Sensitive pattern found in $file: $pattern"
                found_issues=1
            fi
        done
    done
    
    return $found_issues
}

# Check for sensitive files
check_sensitive_files() {
    local found_issues=0
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM)
    
    # Sensitive file patterns
    local sensitive_patterns=(
        '.*credentials.*'
        '.*secret.*'
        '.*\.key$'
        '.*_prod\..*'
        '.*production.*'
        '.*\.log$'
        'jamf_auth_.*\.sh'
        'setup_credentials\.sh'
    )
    
    for file in $staged_files; do
        for pattern in "${sensitive_patterns[@]}"; do
            if [[ "$file" =~ $pattern ]]; then
                print_error "Sensitive file detected: $file"
                found_issues=1
            fi
        done
    done
    
    return $found_issues
}

# Main execution
main() {
    local issues=0
    
    echo "🔒 Running pre-commit security checks..."
    
    # Check for sensitive patterns
    if ! check_sensitive_patterns; then
        issues=1
    fi
    
    # Check for sensitive files
    if ! check_sensitive_files; then
        issues=1
    fi
    
    if [[ $issues -eq 1 ]]; then
        echo
        print_error "Commit blocked due to sensitive information detected!"
        echo
        echo "To fix this:"
        echo "1. Remove or sanitize the sensitive information"
        echo "2. Use the sanitization script: ./scripts/simple_public_push.sh"
        echo "3. Add sensitive files to .gitignore"
        echo "4. Use environment variables or secure credential storage"
        echo
        echo "To bypass this check (NOT RECOMMENDED):"
        echo "git commit --no-verify"
        echo
        exit 1
    fi
    
    print_success "No sensitive information detected"
    exit 0
}

main "$@"