# JPAPI Scripts Directory

This directory contains supporting scripts for the JPAPI toolkit, organized to complement the main `src/` functionality.

## 📁 Directory Structure

```
scripts/
├── setup/          # Installation and configuration scripts
├── dev/            # Development utilities and helpers
├── deploy/         # Deployment and distribution scripts
├── launchers/      # Application launcher scripts
└── tools/          # Operational utilities and maintenance tools
```

## 🚀 Quick Reference

### Setup Scripts
- `setup/setup_auth.py` - Interactive authentication setup
- `setup/setup_global_command.sh` - Global command installation
- `setup/update_credentials.py` - Credential management and keychain updates
- `setup/install_pre_commit_hook.sh` - Git pre-commit hooks

### Development Tools
- `dev/cursor_jpapi_helper.sh` - Cursor IDE integration
- `dev/README.md` - Development guidelines

### Deployment Scripts
- `deploy/deploy_to_public.sh` - Public repository deployment
- `deploy/sanitize_for_public.sh` - Data sanitization
- `deploy/upload_to_production.py` - Production uploads

### Application Launchers
- `launchers/launch-dashboard.py` - Main dashboard launcher
- `launchers/launch-mobile-manager.py` - Mobile manager launcher
- `launchers/launch-api-matrix.py` - API matrix launcher

### Operational Tools
- `tools/performance_monitor.py` - Performance tracking
- `tools/start_redis.sh` - Redis server startup
- `tools/utils.sh` - Common utility functions
- `tools/fanduel_proxy_server.py` - Proxy server utility

## 🏗️ Architecture Alignment

This scripts directory follows the JPAPI hybrid architecture:
- **20% Bash**: Simple setup and deployment scripts
- **80% Python**: Complex utilities and monitoring tools

## 📚 Usage

Most scripts are designed to be run from the project root:

```bash
# Setup (use main installer instead)
curl -sSL https://raw.githubusercontent.com/fanduel/jpapi/main/install.sh | bash

# Development
./scripts/dev/cursor_jpapi_helper.sh

# Deployment
./scripts/deploy/deploy_to_public.sh

# Launchers
python3 scripts/launchers/launch-dashboard.py

# Tools
python3 scripts/tools/performance_monitor.py
```

## 🔧 Maintenance

- Keep scripts focused and simple
- Follow the hybrid architecture principles
- Update documentation when adding new scripts
- Test scripts before committing changes
