#!/bin/bash

# =============================================================================
# Simple Public Push - The EASY Way
# =============================================================================
# This script simply removes sensitive directories and pushes clean code.
# No sanitization needed - just ignore the bad stuff!
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
    echo -e "${BLUE}🚀 Simple Public Push - The EASY Way${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
    echo
    echo -e "${YELLOW}This approach:${NC}"
    echo -e "  • Removes sensitive directories (exports, etc.)"
    echo -e "  • Pushes only the clean source code"
    echo -e "  • No complex sanitization needed"
    echo -e "  • Fast and simple"
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

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
    print_success "Git repository detected"
}

# Remove sensitive directories
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

# Remove sensitive files
remove_sensitive_files() {
    print_info "Removing sensitive files..."
    
    local files_to_remove=(
        "jpapi.config"
        "get_auth_token.py"
        "upload_to_production.py"
        "setup_auth.py"
        "scripts/fanduel_proxy_server.py"
    )
    
    for file in "${files_to_remove[@]}"; do
        if [[ -f "$file" ]]; then
            rm -f "$file"
            print_success "Removed: $file"
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

# Commit and push
commit_and_push() {
    print_info "Committing and pushing to public repository..."
    
    # Add all files
    git add .
    
    # Commit
    git commit -m "🚀 Release v1.2.0: Clean public repository

- Removed sensitive data directories (exports, etc.)
- Clean source code ready for public use
- No company-specific information
- Ready for open source community"
    
    # Push to public repository
    git push origin main
    
    print_success "Pushed to public repository"
}

# Main execution
main() {
    print_header
    
    # Check if we're in a git repository
    check_git_repo
    
    # Remove sensitive directories
    remove_sensitive_dirs
    
    # Remove sensitive files
    remove_sensitive_files
    
    # Create public-safe files
    create_public_readme
    create_public_setup
    
    # Commit and push
    commit_and_push
    
    echo
    print_success "Simple public push complete!"
    echo
    print_info "What happened:"
    echo "  • Removed sensitive directories (exports, etc.)"
    echo "  • Removed sensitive files (configs, auth scripts, etc.)"
    echo "  • Created public-safe README and setup.py"
    echo "  • Pushed clean code to GitHub"
    echo
    print_info "Benefits of this approach:"
    echo "  ✅ Super fast (no complex sanitization)"
    echo "  ✅ No risk of exposing sensitive data"
    echo "  ✅ Simple and easy to understand"
    echo "  ✅ You keep your private data locally"
    echo
    print_info "Your sensitive data is still safe locally:"
    echo "  • exports/ - Your policy/profile data"
    echo "  • jpapi.config - Your config"
    echo "  • All other sensitive files"
    echo
    print_warning "Remember: Never commit sensitive data to any repository!"
}

# Run main function
main "$@"