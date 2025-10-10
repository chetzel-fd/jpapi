#!/bin/bash
# =============================================================================
# JPAPI Quick Install - One Line Installation
# =============================================================================
# Usage: curl -sSL https://raw.githubusercontent.com/chetzel-fd/jpapi/main/quick-install.sh | bash
# =============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 JPAPI Quick Install${NC}"
echo "================================"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 required. Install from https://python.org"
    exit 1
fi

# Install to user's home directory for persistence
INSTALL_DIR="$HOME/.jpapi"
echo "📁 Installing to: $INSTALL_DIR"

# Clone or update repository
if [[ -d "$INSTALL_DIR" ]]; then
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        echo "📥 Updating existing JPAPI installation..."
        cd "$INSTALL_DIR"
        git pull origin main
    else
        echo "📥 Existing directory is not a git repository, removing and cloning fresh..."
        rm -rf "$INSTALL_DIR"
        git clone https://github.com/chetzel-fd/jpapi.git "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
else
    echo "📥 Downloading JPAPI..."
    git clone https://github.com/chetzel-fd/jpapi.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create virtual environment
echo "🐍 Setting up Python environment..."
if [[ -d "venv" ]]; then
    echo "🔄 Updating existing virtual environment..."
else
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies (CLI only - no web UI)
echo "📦 Installing dependencies (CLI only)..."
pip install --upgrade pip
pip install requests psutil pandas click rich keyring python-dateutil pyjwt

# Create a simple wrapper script
echo "🔧 Creating wrapper script..."
cat > venv/bin/jpapi << 'EOF'
#!/bin/bash
# JPAPI wrapper script
cd "$(dirname "$0")/../.."
export PYTHONPATH="$(pwd)"
exec "$(dirname "$0")/python" src/jpapi_main.py "$@"
EOF

chmod +x venv/bin/jpapi

# Create global symlink
echo "🔗 Creating global access..."
sudo ln -sf "$(pwd)/venv/bin/jpapi" /usr/local/bin/jpapi

echo -e "${GREEN}✅ JPAPI installed successfully!${NC}"
echo
echo "Next steps:"
echo "1. Run: jpapi setup"
echo "2. Configure your JAMF Pro credentials"
echo "3. Test with: jpapi --help"
echo
echo "Installation location: $INSTALL_DIR"
