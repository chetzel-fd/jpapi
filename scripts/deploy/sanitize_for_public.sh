#!/bin/bash

# =============================================================================
# Sanitization Script for Public Repository
# =============================================================================
# This script removes sensitive information before pushing to public GitHub
# Usage: ./scripts/sanitize_for_public.sh [target_directory]
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
TARGET_DIR="${1:-.}"
BACKUP_DIR="${TARGET_DIR}/.sanitize_backup_$(date +%Y%m%d_%H%M%S)"
DRY_RUN="${DRY_RUN:-false}"

print_header() {
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE}🧹 JPAPI Sanitization Script for Public Repository${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
    echo
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ SUCCESS:${NC} $1"
}

print_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
}

# Create backup if not dry run
create_backup() {
    if [[ "$DRY_RUN" == "false" ]]; then
        print_info "Creating backup in $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
        cp -r "$TARGET_DIR" "$BACKUP_DIR/"
        print_success "Backup created"
    else
        print_info "DRY RUN: Would create backup in $BACKUP_DIR"
    fi
}

# Remove sensitive directories
remove_sensitive_directories() {
    print_info "Removing sensitive directories..."
    
    local dirs_to_remove=(
        "exports"
        "tmp"
        "temp"
        "cache"
        "logs"
        "learning_balance"
        "experimental"
        "sandbox"
        "analytics"
        "monitoring"
        "performance"
    )
    
    for dir in "${dirs_to_remove[@]}"; do
        if [[ -d "$TARGET_DIR/$dir" ]]; then
            if [[ "$DRY_RUN" == "false" ]]; then
                rm -rf "$TARGET_DIR/$dir"
                print_success "Removed directory: $dir"
            else
                print_info "DRY RUN: Would remove directory: $dir"
            fi
        fi
    done
}

# Remove sensitive files
remove_sensitive_files() {
    print_info "Removing sensitive files..."
    
    local files_to_remove=(
        "jpapi.config"
        "get_auth_token.py"
        "upload_to_production.py"
        "setup_auth.py"
        "*.log"
        "*.cache"
        "*.db"
        "*.sqlite"
        "*.sqlite3"
        "*credentials*"
        "*secret*"
        "*auth*"
        "*token*"
        "*_prod.*"
        "*_production.*"
        "*_fanduel*"
        "*fanduel*"
        "*FanDuel*"
        "*internal*"
        "*test*"
        "*TEST*"
    )
    
    for pattern in "${files_to_remove[@]}"; do
        if [[ "$DRY_RUN" == "false" ]]; then
            find "$TARGET_DIR" -name "$pattern" -type f -delete 2>/dev/null || true
            print_success "Removed files matching: $pattern"
        else
            print_info "DRY RUN: Would remove files matching: $pattern"
        fi
    done
}

# Sanitize file contents
sanitize_file_contents() {
    print_info "Sanitizing file contents..."
    
    # Find all text files
    local text_files
    text_files=$(find "$TARGET_DIR" -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.txt" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) 2>/dev/null || true)
    
    for file in $text_files; do
        if [[ -f "$file" ]]; then
            sanitize_single_file "$file"
        fi
    done
}

# Sanitize a single file
sanitize_single_file() {
    local file="$1"
    local temp_file="${file}.tmp"
    local modified=false
    
    # Create a copy for processing
    cp "$file" "$temp_file"
    
    # Replace sensitive patterns
    local patterns=(
        # JWT tokens
        's/eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*/[REDACTED_JWT_TOKEN]/g'
        # Bearer tokens
        's/Bearer [A-Za-z0-9_-]{20,}/Bearer [REDACTED_TOKEN]/g'
        's/Authorization: Bearer [A-Za-z0-9_-]{20,}/Authorization: Bearer [REDACTED_TOKEN]/g'
        # API credentials
        's/client_secret[[:space:]]*=[[:space:]]*[A-Za-z0-9_-]{20,}/client_secret = [REDACTED_SECRET]/g'
        's/client_id[[:space:]]*=[[:space:]]*[A-Za-z0-9_-]{20,}/client_id = [REDACTED_CLIENT_ID]/g'
        's/api_key[[:space:]]*=[[:space:]]*[A-Za-z0-9_-]{20,}/api_key = [REDACTED_API_KEY]/g'
        # FanDuel URLs
        's|https://fanduelgroup.*\.jamfcloud\.com|https://example-company.jamfcloud.com|g'
        's|https://fanduel.*\.jamfcloud\.com|https://example-company.jamfcloud.com|g'
        # Company references
        's/FanDuel Group/Example Company/g'
        's/FanDuel/Example Company/g'
        's/fanduelgroup/example-company/g'
        's/fanduel/example-company/g'
        's/Internal toolkit for FanDuel Group/Internal toolkit for Example Company/g'
        's/charles\.hetzel@fanduel\.com/developer@example.com/g'
        's/clezteh/example-user/g'
        # Curl commands with auth
        's/curl -s -w %{http_code} -m 30 -H Authorization: Bearer [A-Za-z0-9_-]*/curl -s -w %{http_code} -m 30 -H Authorization: Bearer [REDACTED_TOKEN]/g'
        # File paths with sensitive info
        's|/Users/charles\.hetzel/|/Users/developer/|g'
        's|charles\.hetzel|developer|g'
    )
    
    for pattern in "${patterns[@]}"; do
        if sed -i.bak "$pattern" "$temp_file" 2>/dev/null; then
            modified=true
        fi
    done
    
    # Check if file was modified
    if [[ "$modified" == "true" ]] && ! diff -q "$file" "$temp_file" >/dev/null 2>&1; then
        if [[ "$DRY_RUN" == "false" ]]; then
            mv "$temp_file" "$file"
            rm -f "${file}.bak"
            print_success "Sanitized: $file"
        else
            print_info "DRY RUN: Would sanitize: $file"
            rm -f "$temp_file"
        fi
    else
        rm -f "$temp_file"
    fi
}

# Create public-safe README
create_public_readme() {
    print_info "Creating public-safe README..."
    
    local readme_file="$TARGET_DIR/README.md"
    local public_readme="$TARGET_DIR/README_PUBLIC.md"
    
    if [[ -f "$readme_file" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            # Create a sanitized version
            cp "$readme_file" "$public_readme"
            sanitize_single_file "$public_readme"
            
            # Replace the original
            mv "$public_readme" "$readme_file"
            print_success "Created public-safe README"
        else
            print_info "DRY RUN: Would create public-safe README"
        fi
    fi
}

# Create public-safe setup.py
create_public_setup() {
    print_info "Creating public-safe setup.py..."
    
    local setup_file="$TARGET_DIR/setup.py"
    
    if [[ -f "$setup_file" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            # Update the setup.py to be public-safe
            sed -i.bak 's|https://github.com/jpapi/jpapi|https://github.com/clezteh/jamf-toolkit|g' "$setup_file"
            sed -i.bak 's|maintainers@jpapi.dev|charles.hetzel@example.com|g' "$setup_file"
            rm -f "${setup_file}.bak"
            print_success "Updated setup.py for public repository"
        else
            print_info "DRY RUN: Would update setup.py for public repository"
        fi
    fi
}

# Verify sanitization
verify_sanitization() {
    print_info "Verifying sanitization..."
    
    local issues=0
    
    # Check for remaining sensitive patterns
    local sensitive_patterns=(
        'fanduel'
        'FanDuel'
        'charles\.hetzel'
        'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'
        'client_secret.*[A-Za-z0-9_-]{20,}'
        'Bearer [A-Za-z0-9_-]{20,}'
    )
    
    for pattern in "${sensitive_patterns[@]}"; do
        if find "$TARGET_DIR" -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.txt" -o -name "*.json" \) -exec grep -l "$pattern" {} \; 2>/dev/null | grep -v ".git" | head -5; then
            print_warning "Found potential sensitive data matching: $pattern"
            issues=$((issues + 1))
        fi
    done
    
    if [[ $issues -eq 0 ]]; then
        print_success "Sanitization verification passed"
    else
        print_warning "Found $issues potential issues. Please review manually."
    fi
}

# Main execution
main() {
    print_header
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "Running in DRY RUN mode - no changes will be made"
        echo
    fi
    
    # Create backup
    create_backup
    
    # Remove sensitive directories
    remove_sensitive_directories
    
    # Remove sensitive files
    remove_sensitive_files
    
    # Sanitize file contents
    sanitize_file_contents
    
    # Create public-safe files
    create_public_readme
    create_public_setup
    
    # Verify sanitization
    verify_sanitization
    
    echo
    print_success "Sanitization complete!"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        echo
        print_info "Next steps:"
        echo "1. Review the changes: git diff"
        echo "2. Test the sanitized code"
        echo "3. Commit and push to public repository"
        echo "4. Backup is available in: $BACKUP_DIR"
    else
        echo
        print_info "To apply changes, run without DRY_RUN=true"
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [target_directory] [options]"
    echo
    echo "Options:"
    echo "  DRY_RUN=true    Run in dry-run mode (no changes made)"
    echo
    echo "Examples:"
    echo "  $0                    # Sanitize current directory"
    echo "  $0 ./my-project       # Sanitize specific directory"
    echo "  DRY_RUN=true $0       # Dry run mode"
    echo
}

# Check for help flag
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    show_help
    exit 0
fi

# Run main function
main "$@"
