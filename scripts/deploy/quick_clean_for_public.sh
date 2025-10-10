#!/bin/bash

# =============================================================================
# Quick Clean for Public Repository - FAST VERSION
# =============================================================================
# This script quickly removes sensitive data without the overhead of the full
# sanitization process. Much faster and more targeted.
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
    echo -e "${BLUE}⚡ Quick Clean for Public Repository${NC}"
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

# Create backup
create_backup() {
    local backup_dir=".quick_clean_backup_$(date +%Y%m%d_%H%M%S)"
    print_info "Creating backup in $backup_dir"
    mkdir -p "$backup_dir"
    cp -r . "$backup_dir/"
    print_success "Backup created: $backup_dir"
}

# Remove sensitive directories (FAST)
remove_sensitive_dirs() {
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
        ".mypy_cache"
        "src/.mypy_cache"
        "src/framework/.mypy_cache"
        "scripts/.mypy_cache"
    )
    
    for dir in "${dirs_to_remove[@]}"; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
            print_success "Removed: $dir"
        fi
    done
}

# Remove sensitive files (FAST)
remove_sensitive_files() {
    print_info "Removing sensitive files..."
    
    local files_to_remove=(
        "jpapi.config"
        "get_auth_token.py"
        "upload_to_production.py"
        "setup_auth.py"
        "scripts/fanduel_proxy_server.py"
        "*.log"
        "*.cache"
        "*.db"
        "*.sqlite"
        "*.sqlite3"
    )
    
    for pattern in "${files_to_remove[@]}"; do
        find . -name "$pattern" -type f -delete 2>/dev/null || true
        print_success "Removed files matching: $pattern"
    done
}

# Quick content cleanup (TARGETED)
quick_content_cleanup() {
    print_info "Quick content cleanup..."
    
    # Only process key files, not everything
    local key_files=(
        "README.md"
        "setup.py"
        "src/core/auth/unified_auth.py"
        "src/lib/url_utils.py"
        "scripts/setup_auth.py"
    )
    
    for file in "${key_files[@]}"; do
        if [[ -f "$file" ]]; then
            # Quick replacements
            sed -i.bak 's/fanduelgroup/example-company/g' "$file" 2>/dev/null || true
            sed -i.bak 's/fanduel/example-company/g' "$file" 2>/dev/null || true
            sed -i.bak 's/FanDuel/Example Company/g' "$file" 2>/dev/null || true
            sed -i.bak 's/charles\.hetzel/developer/g' "$file" 2>/dev/null || true
            sed -i.bak 's/clezteh/example-user/g' "$file" 2>/dev/null || true
            rm -f "${file}.bak" 2>/dev/null || true
            print_success "Cleaned: $file"
        fi
    done
}

# Create public-safe README
create_public_readme() {
    print_info "Creating public-safe README..."
    
    cat > README.md << 'EOF'
# JPAPI - JAMF Pro API Toolkit

A comprehensive toolkit for JAMF Pro API management with hybrid bash/Python architecture.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/clezteh/jamf-toolkit.git
cd jamf-toolkit

# Install dependencies
pip install -e .

# Setup authentication
python3 src/cli/main.py auth setup
```

## 📱 Features

- **CLI Commands**: List, export, search, and manage JAMF objects
- **UI Components**: Streamlit and Dash applications
- **Backend Services**: Fast and enhanced API backends
- **Enterprise Framework**: Multi-tenant support

## 🔧 Configuration

```bash
# Interactive setup
python3 src/cli/main.py auth setup

# Environment variables
export JAMF_ENV=dev
export JAMF_URL=https://your-company.jamfcloud.com
export JAMF_CLIENT_ID=your_client_id
export JAMF_CLIENT_SECRET=your_client_secret
```

## 📚 Documentation

- [CLI Reference](docs/cli-reference.md)
- [API Documentation](docs/api-reference.md)
- [Architecture Guide](docs/architecture.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**JPAPI** - Making JAMF Pro API management simple, fast, and powerful.
EOF

    print_success "Created public-safe README"
}

# Create public-safe setup.py
create_public_setup() {
    print_info "Creating public-safe setup.py..."
    
    cat > setup.py << 'EOF'
#!/usr/bin/env python3
"""
JPAPI - JAMF Pro API Toolkit
Distribution package with optional experimental UI features
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text()
else:
    long_description = "JAMF Pro API toolkit with optional experimental UI features"

setup(
    name="jpapi",
    version="1.2.0",
    author="JPAPI Contributors",
    author_email="charles.hetzel@example.com",
    description="JAMF Pro API toolkit with optional experimental UI features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clezteh/jamf-toolkit",
    packages=find_packages(include=['src*', 'utilities*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "pandas>=1.3.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "keyring>=23.0.0",
        "python-dateutil>=2.8.0",
        "pyjwt>=2.4.0",
    ],
    extras_require={
        "ui": [
            "streamlit>=1.20.0",
            "dash>=2.14.0",
            "plotly>=5.15.0",
            "dash-bootstrap-components>=1.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "enterprise": [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.20.0",
            "pydantic>=2.0.0",
            "sqlalchemy>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jpapi=utilities.jpapi_core:main",
            "jpapi=utilities.jpapi_core:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
        "src": ["**/*"],
    },
    zip_safe=False,
    keywords=[
        "jamf", "mdm", "device-management", "api", "cli",
        "experimental-ui", "optional-features", "streamlit", "dash",
    ],
)
EOF

    print_success "Created public-safe setup.py"
}

# Main execution
main() {
    print_header
    
    # Create backup first
    create_backup
    
    # Remove sensitive directories (fast)
    remove_sensitive_dirs
    
    # Remove sensitive files (fast)
    remove_sensitive_files
    
    # Quick content cleanup (targeted)
    quick_content_cleanup
    
    # Create public-safe files
    create_public_readme
    create_public_setup
    
    echo
    print_success "Quick clean complete!"
    print_info "This took much less time and focused on the essentials."
    echo
    print_info "Next steps:"
    echo "1. Review the changes: git diff"
    echo "2. Test the cleaned code"
    echo "3. Commit and push to public repository"
}

# Run main function
main "$@"
