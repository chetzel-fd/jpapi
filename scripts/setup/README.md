# 📦 JPAPI Setup Scripts

This directory contains specialized setup scripts for different JPAPI installation scenarios.

## 🎯 **For End Users**

**Don't use these scripts directly!** Instead, use the easy installation methods:

- **One-line install**: `curl -sSL https://raw.githubusercontent.com/chetzel-fd/jpapi/main/install.sh | bash`
- **Git clone**: `git clone https://github.com/chetzel-fd/jpapi.git && cd jpapi && ./install.sh`

## 🔧 **For Developers**

These scripts are used internally by the main installation methods:

### Core Setup Scripts

| Script | Purpose | Used By |
|--------|---------|---------|
| `setup_auth.py` | Interactive authentication setup | `jpapi setup` command |
| `setup_global_command.sh` | Creates global `jpapi` command | Main installer |
| `install_pre_commit_hook.sh` | Git pre-commit hooks | Development setup |
| `pre_commit_sanitize.sh` | Pre-commit sanitization | Git hooks |

### Server Management Scripts

| Script | Purpose | Used By |
|--------|---------|---------|
| `server_setup.py` | Server configuration management | Advanced users |
| `server_setup_tool.py` | Server setup utilities | Internal tools |
| `update_credentials.py` | Credential management | `jpapi auth` commands |

## 🚀 **Quick Start for Users**

Just run the one-line installer:

```bash
curl -sSL https://raw.githubusercontent.com/chetzel-fd/jpapi/main/install.sh | bash
```

This handles everything automatically!

## 🔧 **Development Setup**

For developers working on JPAPI:

```bash
# Clone repository
git clone https://github.com/chetzel-fd/jpapi.git
cd jpapi

# Install development dependencies
pip install -e ".[all,dev]"

# Install pre-commit hooks
./scripts/setup/install_pre_commit_hook.sh
```

## 📚 **Documentation**

- **[Main Installation Guide](../../INSTALLATION.md)** - Complete installation options
- **[Quick Start Guide](../../docs/QUICK_START.md)** - Get started in 2 minutes
- **[README](../../README.md)** - Project overview and features

---

**Note**: These scripts are internal tools. End users should use the main installation methods described in the documentation.
