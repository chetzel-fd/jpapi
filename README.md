# JPAPI - JAMF Pro API Toolkit

A powerful, user-friendly toolkit for JAMF Pro API management with enterprise-grade features and modern CLI design.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start (2 Minutes)

### 🎯 **Super Easy Installation**

#### **Option 1: One-Line Install (Recommended)**
```bash
curl -sSL https://raw.githubusercontent.com/chetzel-fd/jpapi/main/install.sh | bash
```

#### **Option 2: Manual Installation**
```bash
git clone https://github.com/chetzel-fd/jpapi.git
cd jpapi
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 2. Configure Authentication

```bash
# Run the interactive setup wizard
jpapi setup
```

✨ **JPAPI auto-detects existing credentials in your macOS Keychain!**  
If you've used JPAPI before, your credentials will be found automatically.

#### Quick Setup Options

**Option 1: Interactive Setup (Recommended)**
```bash
jpapi setup
# Follow the prompts to configure your JAMF Pro credentials
```

**Option 2: Setup for Specific Environment**
```bash
jpapi setup --env sandbox    # For sandbox/test environment
jpapi setup --env production # For production environment
```

**Option 3: OAuth Setup (Direct)**
```bash
jpapi setup oauth
# Paste the JSON from JAMF Pro when prompted
```

**Option 4: Basic Auth Setup**
```bash
jpapi setup basic
# Enter username and password when prompted
```

#### Getting OAuth Credentials from JAMF Pro

1. Log into your JAMF Pro server
2. Navigate to: **Settings → System Settings → API Roles and Clients**
3. Click **New** to create a new API Client
4. Configure the client with required privileges
5. **Copy the entire JSON response** that JAMF shows you (contains `client_id`, `client_secret`, and `url`)

💡 **Tip:** You can paste the entire JSON from JAMF Pro directly into the setup wizard - no need to copy fields separately!

#### Verify Your Setup

```bash
# Test your connection
jpapi setup test

# List saved credentials
jpapi setup list

# Check what's configured
jpapi list policies --limit 1
```

### 3. Start Using JPAPI

```bash
# List policies
jpapi list policies

# Export data to CSV
jpapi export policies --format csv

# Search for specific items
jpapi search policies --filter "*Chrome*"

# Get help
jpapi --help
```

That's it! You're ready to go. 🎉

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Detailed getting started guide
- **[Installation Guide](INSTALLATION_GUIDE.md)** - Advanced installation options
- **[CLI Reference](docs/cli-reference.md)** - Complete command reference
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

---

## ✨ Features

### Core Features (Always Available)
- 🔐 **Secure Authentication** - OAuth 2.0 and Basic Auth support
- ✨ **Keychain Detection** - Auto-discovers existing credentials (macOS)
- 📊 **Data Export** - Export to CSV, JSON, and more
- 🔍 **Advanced Search** - Powerful filtering and querying
- 🎯 **Multiple Environments** - Dev, staging, production support
- 🛡️ **Production Guardrails** - Safety checks for destructive operations
- ⚡ **Fast Performance** - Optimized API calls and caching

### Optional Features
Install with `pip install -e ".[ui]"` or `pip install -e ".[enterprise]"`

- 📱 **Web Dashboards** - Streamlit and Dash interfaces
- 📈 **Analytics** - Advanced reporting and visualization
- 🌐 **API Backend** - FastAPI REST services
- 🔄 **Real-time Sync** - Live data synchronization

---

## 🎯 Common Commands

### List Resources
```bash
jpapi list policies                    # List all policies
jpapi list "mobile devices"            # List mobile devices
jpapi list computers                   # List computers
jpapi list scripts                     # List scripts
```

### Export Data
```bash
jpapi export policies --format csv     # Export to CSV
jpapi export devices --format json     # Export to JSON
jpapi export scripts --output ~/data/  # Export to specific directory
```

### Search and Filter
```bash
jpapi search policies --filter "*Update*"           # Wildcard search
jpapi list policies --status enabled                # Filter by status
jpapi export policies --filter "*Chrome*" --format csv
```

### Device Management
```bash
jpapi devices list                     # List all devices
jpapi devices search --name "macbook"  # Search devices
jpapi devices info <id>                # Get device details
```

### Multi-Environment Support
```bash
jpapi --env dev list policies          # Development environment
jpapi --env prod list policies         # Production environment
```

---

## 🔧 Installation Options

### Lightweight Installation (Core Only, ~50MB)
```bash
pip install -e .
```
Includes: CLI, authentication, data export, search

### With Web UI (~120MB)
```bash
pip install -e ".[ui]"
```
Adds: Streamlit dashboards, Dash apps, Plotly visualizations

### Full Development Environment (~150MB)
```bash
pip install -e ".[all,dev]"
```
Adds: All features + testing, linting, type checking tools

### Enterprise Features
```bash
pip install -e ".[enterprise]"
```
Adds: FastAPI backend, async operations, advanced analytics

---

## 🏗️ Architecture

### Hybrid Design
- **Python Core** - Full-featured CLI with rich functionality
- **Modular Commands** - Extensible command architecture
- **Plugin System** - Easy to add custom commands
- **SOLID Principles** - Clean, maintainable code

### Key Components
```
jpapi/
├── core/           # Framework core (auth, safety, interfaces)
├── src/
│   ├── cli/        # CLI commands and handlers
│   ├── apps/       # Web applications (Streamlit, Dash)
│   ├── services/   # Business logic services
│   └── lib/        # Shared utilities
├── lib/            # Additional libraries
├── resources/      # Configuration and resources
└── storage/        # Data storage and cache
```

---

## 🔒 Security

### Credential Storage
- Credentials stored securely in `~/.jpapi/config.json`
- File permissions automatically set to `600` (owner read/write only)
- No credentials in source code or version control
- Environment-specific credential files

### Best Practices
- ✅ Use OAuth 2.0 (preferred over Basic Auth)
- ✅ Token caching with automatic expiration
- ✅ Production guardrails for destructive operations
- ✅ Dry-run mode for testing changes
- ✅ Input validation and sanitization

---

## 🧪 Testing Your Installation

```bash
# Check installation
jpapi --version

# Verify authentication setup
jpapi setup test

# Run health check
jpapi doctor

# Test a simple command
jpapi list policies --limit 5
```

---

## 🆘 Troubleshooting

### Installation Issues

**Problem:** `jpapi: command not found`
```bash
# Solution: Reinstall in editable mode
pip install -e .
```

**Problem:** Import errors or module not found
```bash
# Solution: Ensure you're in the virtual environment
source venv/bin/activate
pip install -e .
```

### Authentication Issues

**Problem:** "Authentication not configured"
```bash
# Solution: Run the setup wizard
jpapi setup
```

**Problem:** "Authentication failed" or 401 errors
```bash
# Solution: Test and re-configure credentials
jpapi setup test      # Test current credentials
jpapi setup           # Re-configure if needed
jpapi setup oauth     # Or set up OAuth specifically
```

### Need More Help?
- Run `jpapi doctor` to diagnose common issues
- Check the [Troubleshooting Guide](docs/troubleshooting.md)
- Review error messages - they include helpful suggestions

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Clone and setup
git clone https://github.com/chetzel-fd/jpapi.git
cd jpapi
python3 -m venv venv
source venv/bin/activate

# Install with development tools
pip install -e ".[all,dev]"

# Run tests
pytest

# Format code
black src/

# Run linters
flake8 src/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🗺️ Roadmap

### Current Focus
- ✅ Core CLI functionality
- ✅ Secure authentication
- ✅ Data export and search
- ✅ Production guardrails

### Coming Soon
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline
- [ ] Plugin ecosystem
- [ ] Enhanced documentation

### Future Plans
- [ ] Cloud deployment options
- [ ] Advanced analytics
- [ ] Machine learning features
- [ ] Enterprise integrations

---

## 💡 Philosophy

JPAPI is built with these principles:

1. **User-Friendly** - Simple for beginners, powerful for experts
2. **Secure by Default** - Safety checks and production guardrails
3. **Fast and Efficient** - Optimized performance and caching
4. **Extensible** - Plugin architecture for custom needs
5. **Well-Documented** - Comprehensive guides and examples

---

**Built with ❤️ for JAMF administrators**

Need help? Run `jpapi --help` or visit our [documentation](docs/).
