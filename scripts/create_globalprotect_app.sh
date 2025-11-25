#!/bin/bash
# Create a macOS .app bundle for GlobalProtect downloader

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="GlobalProtect Downloader"
APP_BUNDLE="${SCRIPT_DIR}/${APP_NAME}.app"
CONTENTS_DIR="${APP_BUNDLE}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "📦 Creating macOS app bundle: ${APP_NAME}.app"

# Create app bundle structure
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Copy the Python script
cp "${SCRIPT_DIR}/download_globalprotect_app.py" "${MACOS_DIR}/main.py"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.fanduel.globalprotect-downloader</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create launcher script
cat > "${MACOS_DIR}/launcher" <<'EOF'
#!/bin/bash
# Launcher script for GlobalProtect Downloader

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/main.py"

# Try to use Python from virtual environment if available
if [ -f "${SCRIPT_DIR}/../../venv/bin/python3" ]; then
    PYTHON="${SCRIPT_DIR}/../../venv/bin/python3"
elif command -v python3 &> /dev/null; then
    PYTHON=python3
else
    osascript -e 'display dialog "Python 3 is required but not found." buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Check for required packages
if ! "${PYTHON}" -c "import oktaloginwrapper" 2>/dev/null; then
    osascript -e 'display dialog "Missing required package: oktaloginwrapper\n\nPlease install it with: pip3 install oktaloginwrapper" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Run the script
exec "${PYTHON}" "${PYTHON_SCRIPT}"
EOF

chmod +x "${MACOS_DIR}/launcher"

# Create a simple app icon (optional - you can replace this with a real icon)
# For now, we'll skip the icon creation

echo "✅ App bundle created: ${APP_BUNDLE}"
echo ""
echo "To use the app:"
echo "  1. Double-click '${APP_NAME}.app'"
echo "  2. Or run: open '${APP_BUNDLE}'"
echo ""
echo "Note: Make sure oktaloginwrapper is installed:"
echo "  pip3 install oktaloginwrapper"

