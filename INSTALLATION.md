# 📦 JPAPI Installation Guide

Multiple easy ways to install JPAPI - choose what works best for you!

---

## 🎯 **Recommended: One-Line Install**

The easiest way to get started:

```bash
curl -sSL https://raw.githubusercontent.com/fanduel/jpapi/main/install.sh | bash
```

This script will:
- ✅ Check for Python 3.8+
- ✅ Install system dependencies (jq, curl)
- ✅ Clone the repository
- ✅ Create a virtual environment
- ✅ Install JPAPI and dependencies
- ✅ Create a global `jpapi` command
- ✅ Test the installation

---

## 🍺 **Homebrew (macOS)**

For macOS users who prefer Homebrew:

```bash
# Add the FanDuel tap
brew tap fanduel/jpapi

# Install JPAPI
brew install jpapi
```

---

## 🐳 **Docker**

Perfect for isolated environments or CI/CD:

### Quick Run
```bash
# Run JPAPI in a container
docker run -it --rm fanduel/jpapi:latest
```

### With Docker Compose
```bash
# Clone the repository
git clone https://github.com/fanduel/jpapi.git
cd jpapi

# Start with Docker Compose
docker-compose up jpapi
```

### Persistent Configuration
```bash
# Mount config directory for persistence
docker run -it --rm \
  -v ~/.jpapi:/home/jpapi/.jpapi \
  fanduel/jpapi:latest
```

---

## 🐍 **Python Package Manager**

### pip (Global Install)
```bash
# Install globally (not recommended)
pip install git+https://github.com/fanduel/jpapi.git
```

### pipx (Recommended for CLI tools)
```bash
# Install with pipx (isolated environment)
pipx install git+https://github.com/fanduel/jpapi.git
```

---

## 🔧 **Manual Installation**

For development or custom setups:

### 1. Clone Repository
```bash
git clone https://github.com/fanduel/jpapi.git
cd jpapi
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install system dependencies
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq curl

# CentOS/RHEL
sudo yum install jq curl
```

### 4. Install JPAPI
```bash
pip install -e .
```

### 5. Create Global Access (Optional)
```bash
# Create symlink for global access
sudo ln -sf $(pwd)/venv/bin/jpapi /usr/local/bin/jpapi
```

---

## 🧪 **Verify Installation**

After installation, test that everything works:

```bash
# Check version
jpapi --version

# Check help
jpapi --help

# Run diagnostics
jpapi doctor
```

---

## 🆘 **Troubleshooting**

### Command Not Found
```bash
# If 'jpapi' command not found:
source ~/.bashrc  # or restart terminal
# OR
export PATH="$HOME/.local/bin:$PATH"
```

### Python Issues
```bash
# Ensure Python 3.8+
python3 --version

# Reinstall if needed
pip install -e . --force-reinstall
```

### Permission Issues
```bash
# Fix permissions
chmod +x ~/.local/bin/jpapi
```

---

## 🔄 **Updating JPAPI**

### One-Line Install
```bash
# Re-run the installer (it will update)
curl -sSL https://raw.githubusercontent.com/fanduel/jpapi/main/install.sh | bash
```

### Homebrew
```bash
brew upgrade jpapi
```

### Manual
```bash
cd jpapi
git pull origin main
pip install -e . --upgrade
```

---

## 🗑️ **Uninstalling JPAPI**

### One-Line Install
```bash
rm -rf ~/.jpapi
rm -f ~/.local/bin/jpapi
```

### Homebrew
```bash
brew uninstall jpapi
```

### Manual
```bash
rm -rf jpapi/
# Remove from PATH if added manually
```

---

## 💡 **Pro Tips**

### Multiple Versions
```bash
# Use different virtual environments
python3 -m venv jpapi-dev
python3 -m venv jpapi-prod
```

### Development Mode
```bash
# Install in development mode
pip install -e ".[dev,all]"
```

### Offline Installation
```bash
# Download and install offline
wget https://github.com/fanduel/jpapi/archive/main.zip
unzip main.zip
cd jpapi-main
pip install -e .
```

---

## 🎯 **What's Next?**

After installation:

1. **Configure Authentication**: `jpapi setup`
2. **Test Connection**: `jpapi list policies --limit 5`
3. **Explore Commands**: `jpapi --help`
4. **Read Documentation**: Check the [Quick Start Guide](QUICK_START.md)

---

**Need Help?** 
- Run `jpapi doctor` for diagnostics
- Check the [Troubleshooting Guide](docs/troubleshooting.md)
- Open an [issue on GitHub](https://github.com/fanduel/jpapi/issues)
