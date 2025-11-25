# 🚀 JPAPI Quick Start Guide

Get up and running with JPAPI in under 2 minutes!

---

## 🎯 **Super Easy Installation**

Choose your preferred method:

### **Option 1: One-Line Install (Recommended)**
```bash
# Install JPAPI in one command
curl -sSL https://raw.githubusercontent.com/chetzel-fd/jpapi/main/install.sh | bash
```

### **Option 2: Homebrew (macOS)**
```bash
# Clone and install
git clone https://github.com/chetzel-fd/jpapi.git
cd jpapi && ./install.sh
```

### **Option 3: Docker**
```bash
# Verify installation
jpapi --version
```

### **Option 4: Manual Installation**
```bash
# Clone and install manually
git clone https://github.com/chetzel-fd/jpapi.git
cd jpapi
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

💡 **Why a virtual environment?** It keeps JPAPI's dependencies isolated from your system Python.

---

## Step 2: Configure Authentication (2 minutes)

### Run the Setup Wizard

```bash
jpapi setup
```

The wizard will walk you through:

1. **JAMF Server URL** - Enter your JAMF cloud URL
   ```
   Example: company.jamfcloud.com
   ```

2. **Authentication Method** - Choose OAuth (recommended) or Basic Auth
   ```
   1) OAuth (Recommended)
   2) Basic Authentication
   ```

3. **Credentials** - Enter your API credentials
   ```
   For OAuth:
   - Client ID
   - Client Secret
   
   For Basic Auth:
   - Username
   - Password
   ```

4. **Connection Test** - Automatically verifies your setup

### Getting OAuth Credentials

Don't have OAuth credentials yet? Here's how to get them:

1. **Log into JAMF Pro** - Go to your JAMF server
2. **Navigate to API Clients**
   - Settings → System Settings → API Roles and Clients
3. **Create New API Client**
   - Click "New"
   - Give it a descriptive name (e.g., "JPAPI CLI")
4. **Set Privileges**
   - Assign appropriate privileges (Read/Write based on your needs)
   - For full access: Select "Full Access" role
5. **Copy Credentials**
   - Copy the Client ID
   - Copy the Client Secret
   - Keep these secure!

---

## Step 3: Verify Installation (1 minute)

### Test Basic Commands

```bash
# Check version
jpapi --version

# List available commands
jpapi --help

# Test a simple list operation
jpapi list policies --limit 5
```

### Expected Output

If everything is working, you should see:

```
✅ Connection successful!
✅ Authentication working
✅ Found X policies
```

---

## Step 4: Try Common Operations

### List Resources

```bash
# List all policies
jpapi list policies

# List mobile devices
jpapi list "mobile devices"

# List computers
jpapi list computers

# List scripts
jpapi list scripts
```

### Export Data

```bash
# Export policies to CSV
jpapi export policies --format csv

# Export to specific file
jpapi export policies --output ~/Desktop/policies.csv

# Export mobile devices to JSON
jpapi export "mobile devices" --format json
```

### Search and Filter

```bash
# Search policies containing "Chrome"
jpapi search policies --filter "*Chrome*"

# List only enabled policies
jpapi list policies --status enabled

# Export filtered results
jpapi export policies --filter "*Update*" --format csv
```

---

## 🎯 What's Next?

### Learn More Commands

```bash
# Get help on any command
jpapi list --help
jpapi export --help
jpapi search --help

# See all available commands
jpapi --help
```

### Launch Web Dashboard (Optional)

If you installed UI features:

```bash
jpapi dashboard
```

This launches an interactive web interface at http://localhost:8501

### Work with Multiple Environments

```bash
# Use development environment (default)
jpapi list policies

# Use production environment
jpapi --env prod list policies

# Configure additional environments
jpapi setup --env staging
```

---

## 🆘 Troubleshooting

### Command Not Found

**Problem:** `jpapi: command not found`

**Solution:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall
pip install -e .
```

### Authentication Errors

**Problem:** "Authentication not configured" or "401 Unauthorized"

**Solution:**
```bash
# Check authentication status
jpapi auth status

# Re-run setup if needed
jpapi setup
```

### Import Errors

**Problem:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
# Ensure all dependencies are installed
pip install -e .

# Or reinstall with --force
pip install -e . --force-reinstall
```

### Connection Issues

**Problem:** "Connection timeout" or "Cannot reach server"

**Solution:**
1. Verify your JAMF server URL is correct
2. Check your network connection
3. Verify firewall settings
4. Test URL in browser: `https://your-server.jamfcloud.com`

### Still Stuck?

```bash
# Run the diagnostic tool
jpapi doctor

# This checks:
# - Python version
# - Dependencies
# - Configuration
# - JAMF connection
# - Credentials
```

---

## 📚 Additional Resources

- **[README](README.md)** - Overview and features
- **[Installation Guide](INSTALLATION_GUIDE.md)** - Advanced installation options
- **[CLI Reference](docs/cli-reference.md)** - Complete command documentation
- **[Troubleshooting](docs/troubleshooting.md)** - Detailed troubleshooting guide

---

## 💡 Pro Tips

### Tip 1: Use Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias jp="jpapi"
alias jpl="jpapi list"
alias jpe="jpapi export"
```

Now you can use:
```bash
jp list policies
jpl computers
jpe policies --format csv
```

### Tip 2: Environment Variables

Set default environment:

```bash
export JPAPI_ENV=dev
```

### Tip 3: Output Formatting

```bash
# CSV (great for Excel)
jpapi export policies --format csv

# JSON (great for APIs)
jpapi export policies --format json

# Table (great for terminal)
jpapi list policies --format table
```

### Tip 4: Use Filters Effectively

```bash
# Wildcard search
jpapi search policies --filter "*Chrome*"

# Regex search
jpapi search policies --filter-type regex --filter "^Install.*"

# Exact match
jpapi search policies --filter-type exact --filter "Install Chrome"
```

---

## 🎉 You're All Set!

You now have JPAPI installed and configured. Happy automating!

**Questions?** Run `jpapi --help` or check the [documentation](docs/).

**Found a bug?** Please [open an issue](https://github.com/your-org/jpapi/issues).

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md).

---

**Made with ❤️ for JAMF administrators**
