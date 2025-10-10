#!/bin/bash
# =============================================================================
# JPAPI Quick Install - One Line Installation
# =============================================================================
# Usage: curl -sSL https://raw.githubusercontent.com/fanduel/jpapi/main/quick-install.sh | bash
# =============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 JPAPI Quick Install${NC}"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 required. Install from https://python.org"
    exit 1
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone repository
echo "📥 Downloading JPAPI..."
git clone https://github.com/fanduel/jpapi.git jpapi
cd jpapi

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install JPAPI
echo "📦 Installing JPAPI..."
pip install --upgrade pip
pip install -e .

# Create global symlink
echo "🔗 Creating global access..."
sudo ln -sf "$(pwd)/venv/bin/jpapi" /usr/local/bin/jpapi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ JPAPI installed successfully!${NC}"
echo "Run: jpapi setup"
