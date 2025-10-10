#!/bin/bash

# =============================================================================
# Production Deployment Script for Public Repository
# =============================================================================
# This script safely deploys sanitized code to a public GitHub repository
# Usage: ./scripts/deploy_to_public.sh [version]
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
VERSION="${1:-$(date +%Y%m%d_%H%M%S)}"
SOURCE_DIR="$(pwd)"
PUBLIC_DIR="../jamf-toolkit-public"
BACKUP_DIR=".deploy_backup_$(date +%Y%m%d_%H%M%S)"
DRY_RUN="${DRY_RUN:-false}"

print_header() {
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE}🚀 JPAPI Public Repository Deployment${NC}"
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

# Safety checks
safety_checks() {
    print_info "Running safety checks..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes. Please commit or stash them first."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check for sensitive data
    if find . -name "*.py" -o -name "*.sh" -o -name "*.md" | xargs grep -l "fanduel\|FanDuel\|charles\.hetzel" 2>/dev/null | head -5; then
        print_warning "Found potential sensitive data. Running sanitization first..."
        if [[ "$DRY_RUN" == "false" ]]; then
            ./scripts/sanitize_for_public.sh
        else
            print_info "DRY RUN: Would run sanitization"
        fi
    fi
    
    print_success "Safety checks passed"
}

# Create public directory structure
setup_public_directory() {
    print_info "Setting up public directory structure..."
    
    if [[ "$DRY_RUN" == "false" ]]; then
        # Create public directory if it doesn't exist
        mkdir -p "$PUBLIC_DIR"
        
        # Initialize git repository if needed
        if [[ ! -d "$PUBLIC_DIR/.git" ]]; then
            cd "$PUBLIC_DIR"
            git init
            git remote add origin https://github.com/clezteh/jamf-toolkit.git
            cd "$SOURCE_DIR"
            print_success "Initialized public repository"
        fi
        
        # Create backup
        mkdir -p "$BACKUP_DIR"
        cp -r "$PUBLIC_DIR" "$BACKUP_DIR/"
        print_success "Created backup in $BACKUP_DIR"
    else
        print_info "DRY RUN: Would setup public directory at $PUBLIC_DIR"
    fi
}

# Copy sanitized files
copy_sanitized_files() {
    print_info "Copying sanitized files to public directory..."
    
    if [[ "$DRY_RUN" == "false" ]]; then
        # Clear public directory (except .git)
        find "$PUBLIC_DIR" -mindepth 1 -not -path "*/.git*" -delete 2>/dev/null || true
        
        # Copy files, excluding sensitive directories
        rsync -av --exclude='.git' \
              --exclude='exports' \
              --exclude='tmp' \
              --exclude='temp' \
              --exclude='cache' \
              --exclude='logs' \
              --exclude='learning_balance' \
              --exclude='experimental' \
              --exclude='sandbox' \
              --exclude='analytics' \
              --exclude='monitoring' \
              --exclude='performance' \
              --exclude='*.log' \
              --exclude='*.cache' \
              --exclude='*.db' \
              --exclude='*.sqlite' \
              --exclude='*.sqlite3' \
              --exclude='*credentials*' \
              --exclude='*secret*' \
              --exclude='*auth*' \
              --exclude='*token*' \
              --exclude='*_prod.*' \
              --exclude='*_production.*' \
              --exclude='*_fanduel*' \
              --exclude='*fanduel*' \
              --exclude='*FanDuel*' \
              --exclude='*internal*' \
              --exclude='*test*' \
              --exclude='*TEST*' \
              --exclude='jpapi.config' \
              --exclude='get_auth_token.py' \
              --exclude='upload_to_production.py' \
              --exclude='setup_auth.py' \
              . "$PUBLIC_DIR/"
        
        print_success "Files copied to public directory"
    else
        print_info "DRY RUN: Would copy files to $PUBLIC_DIR"
    fi
}

# Sanitize copied files
sanitize_copied_files() {
    print_info "Sanitizing copied files..."
    
    if [[ "$DRY_RUN" == "false" ]]; then
        cd "$PUBLIC_DIR"
        ../jamf-toolkit/scripts/sanitize_for_public.sh .
        cd "$SOURCE_DIR"
        print_success "Files sanitized"
    else
        print_info "DRY RUN: Would sanitize files in $PUBLIC_DIR"
    fi
}

# Create deployment-specific files
create_deployment_files() {
    print_info "Creating deployment-specific files..."
    
    if [[ "$DRY_RUN" == "false" ]]; then
        # Create public-safe README
        cat > "$PUBLIC_DIR/README.md" << 'EOF'
# JPAPI - JAMF Pro API Toolkit

A comprehensive toolkit for JAMF Pro API management with hybrid bash/Python architecture, enterprise framework, and modern UI components.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- JAMF Pro instance with API access
- OAuth credentials (Client ID and Secret)

### Installation
```bash
# Clone the repository
git clone https://github.com/clezteh/jamf-toolkit.git
cd jamf-toolkit

# Install dependencies
pip install -e .

# Setup authentication
python3 src/cli/main.py auth setup
```

### Basic Usage
```bash
# List JAMF objects
python3 src/cli/main.py list policies
python3 src/cli/main.py list devices

# Export data
python3 src/cli/main.py export policies --format csv

# Search objects
python3 src/cli/main.py search devices --model "MacBook Pro"
```

## 🏗️ Architecture

### Hybrid Design
- **Bash Operations** (~0.015s): Fast API calls for simple operations
- **Python Operations** (~0.169s): Complex data processing and analysis

### Core Components
- **Unified Authentication**: Single `SimpleAuth` class for all JAMF API access
- **Unified Caching**: 3-tier cache system (Memory → SQLite → API)
- **Modular CLI**: Command-based architecture with extensible design
- **Enterprise Framework**: Multi-tenant support with centralized configuration

## 📱 Features

### CLI Commands
- `list` - List JAMF objects (policies, devices, groups, etc.)
- `export` - Export data to CSV, JSON, or other formats
- `search` - Advanced search with criteria-based filtering
- `devices` - Device management operations
- `tools` - Utility tools and health checks
- `create` - Create new JAMF objects
- `move` - Move objects between categories
- `update` - Update objects from CSV files

### UI Components
- **Streamlit Apps**: 7 modern web applications
- **Dash Components**: Enterprise-grade dashboards
- **Apple-Style Design**: Consistent, professional interfaces

### Backend Services
- **Fast Backend** (Port 8600): Optimized for dashboard performance
- **Enhanced Backend** (Port 8900): Full-featured with relationship analysis
- **Task Manager** (Port 8901): Background processing and analytics

## 🔧 Configuration

### Authentication Setup
```bash
# Interactive setup
python3 src/cli/main.py auth setup

# Manual configuration
# Credentials are stored in ~/.jpapi_dev.json
```

### Environment Variables
```bash
export JAMF_ENV=dev  # or 'prod'
export JAMF_URL=https://your-company.jamfcloud.com
export JAMF_CLIENT_ID=your_client_id
export JAMF_CLIENT_SECRET=your_client_secret
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html
```

## 📚 Documentation

- [CLI Reference](docs/cli-reference.md)
- [API Documentation](docs/api-reference.md)
- [Architecture Guide](docs/architecture.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## 🚀 Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/
```

### Running Backend Services
```bash
# Fast backend
python3 src/services/backend_fast.py

# Enhanced backend
python3 src/services/backend_enhanced.py

# Task manager
python3 src/services/backend_task_manager.py
```

### Running UI Applications
```bash
# Streamlit apps
streamlit run src/apps/streamlit/mobile_jamf_manager_streamlit.py

# Dash apps
python3 src/jamf_dash_frontend.py
```

## 🔒 Security

### Credential Management
- Credentials stored in `~/.jpapi_<env>.json`
- File permissions set to 600 (owner read/write only)
- No hardcoded credentials in source code
- Environment-specific credential files

### Security Best Practices
- OAuth 2.0 client credentials flow
- Token caching with expiration
- Secure credential storage
- Input validation and sanitization

## 📊 Performance

### Benchmarks
- **Bash Operations**: ~0.015s average response time
- **Python Operations**: ~0.169s average response time
- **Cache Hit Rate**: 85%+ for frequently accessed data
- **Memory Usage**: <100MB for typical workloads

### Optimization Features
- 3-tier caching system
- Intelligent cache promotion/demotion
- Background data processing
- Connection pooling for API calls

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- Check the [documentation](docs/)
- Search [existing issues](https://github.com/clezteh/jamf-toolkit/issues)
- Create a [new issue](https://github.com/clezteh/jamf-toolkit/issues/new)

### Common Issues
- **Authentication errors**: Run `python3 src/cli/main.py auth setup`
- **Import errors**: Ensure you're in the correct directory
- **Permission errors**: Check file permissions on credential files

## 🗺️ Roadmap

### Short-term (1-3 months)
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline
- [ ] Performance optimizations
- [ ] Enhanced documentation

### Medium-term (3-6 months)
- [ ] Advanced analytics features
- [ ] Multi-tenant improvements
- [ ] Plugin system enhancements
- [ ] Monitoring and observability

### Long-term (6+ months)
- [ ] Cloud deployment options
- [ ] Advanced security features
- [ ] Enterprise integrations
- [ ] Machine learning capabilities

---

**JPAPI** - Making JAMF Pro API management simple, fast, and powerful.
EOF

        # Create public-safe setup.py
        cat > "$PUBLIC_DIR/setup.py" << 'EOF'
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
        # Core dependencies - always required
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "pandas>=1.3.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "keyring>=23.0.0",  # For credential storage
        "python-dateutil>=2.8.0",
        "pyjwt>=2.4.0",
    ],
    extras_require={
        "ui": [
            # EXPERIMENTAL UI FEATURES - Optional and potentially unstable
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
            "jpapi=utilities.jpapi_core:main",  # Backward compatibility
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

        print_success "Created deployment-specific files"
    else
        print_info "DRY RUN: Would create deployment-specific files"
    fi
}

# Commit and push to public repository
commit_and_push() {
    print_info "Committing and pushing to public repository..."
    
    if [[ "$DRY_RUN" == "false" ]]; then
        cd "$PUBLIC_DIR"
        
        # Add all files
        git add .
        
        # Commit with version
        git commit -m "🚀 Release v$VERSION: Sanitized for public repository
        
        - Removed sensitive data and company-specific information
        - Sanitized all configuration files
        - Updated documentation for public use
        - Maintained core functionality while ensuring security"
        
        # Push to public repository
        git push origin main
        
        cd "$SOURCE_DIR"
        print_success "Pushed to public repository"
    else
        print_info "DRY RUN: Would commit and push to public repository"
    fi
}

# Main execution
main() {
    print_header
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "Running in DRY RUN mode - no changes will be made"
        echo
    fi
    
    # Run safety checks
    safety_checks
    
    # Setup public directory
    setup_public_directory
    
    # Copy sanitized files
    copy_sanitized_files
    
    # Sanitize copied files
    sanitize_copied_files
    
    # Create deployment files
    create_deployment_files
    
    # Commit and push
    commit_and_push
    
    echo
    print_success "Deployment complete!"
    print_info "Public repository updated with version: $VERSION"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        echo
        print_info "Next steps:"
        echo "1. Verify the public repository: https://github.com/clezteh/jamf-toolkit"
        echo "2. Test the public version"
        echo "3. Update documentation if needed"
        echo "4. Backup is available in: $BACKUP_DIR"
    else
        echo
        print_info "To apply changes, run without DRY_RUN=true"
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [version] [options]"
    echo
    echo "Arguments:"
    echo "  version         Version tag for the release (default: timestamp)"
    echo
    echo "Options:"
    echo "  DRY_RUN=true    Run in dry-run mode (no changes made)"
    echo
    echo "Examples:"
    echo "  $0                    # Deploy with timestamp version"
    echo "  $0 v1.2.0            # Deploy with specific version"
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
