# GlobalProtect Downloader - Deployment Guide

## Overview

This solution provides multiple ways to download GlobalProtect for macOS with Okta authentication, optimized for end-user deployment.

## 🎯 Recommended Solution: `download_globalprotect_app.py`

**Best for**: End users who need a simple, no-command-line solution

### Key Features

1. **Zero Command Line**: Uses native macOS dialogs (osascript)
2. **Keychain Integration**: Automatically finds existing Okta/FanDuel credentials
3. **Credential Persistence**: Saves credentials securely in Keychain for future use
4. **Packagable**: Can be bundled as a .app for easy distribution

### How It Works

```
User runs app
    ↓
Checks macOS Keychain for existing credentials
    ↓
If found → Use them automatically
If not found → Show native macOS dialog for username/password
    ↓
Authenticate with Okta (handles MFA automatically)
    ↓
Download GlobalProtect.pkg
    ↓
Save credentials to Keychain for next time
```

### Deployment Options

#### Option 1: Distribute as .app Bundle (Recommended)

```bash
# Create the app bundle
./scripts/create_globalprotect_app.sh

# The app will be created at:
# scripts/GlobalProtect Downloader.app

# Users can:
# - Double-click to run
# - No terminal needed
# - No command line knowledge required
```

#### Option 2: Deploy via MDM (Jamf/Intune)

1. Create the .app bundle using `create_globalprotect_app.sh`
2. Package the .app (create .pkg or .dmg)
3. Deploy via your MDM solution
4. Users run it once, credentials are saved

#### Option 3: Self-Service Portal

1. Host the .app bundle on a web server or file share
2. Provide download link to users
3. Users download and run
4. First run prompts for credentials, subsequent runs are automatic

### User Experience

**First Run:**
1. User double-clicks "GlobalProtect Downloader.app"
2. Native macOS dialog appears: "Enter your Okta username"
3. User enters username (may be pre-filled from Keychain)
4. Native macOS dialog appears: "Enter your Okta password"
5. User enters password
6. App authenticates and downloads GlobalProtect.pkg
7. Success dialog shows download location

**Subsequent Runs:**
1. User double-clicks "GlobalProtect Downloader.app"
2. App finds credentials in Keychain automatically
3. Downloads GlobalProtect.pkg (no prompts!)
4. Success dialog shows download location

### Keychain Search Strategy

The app searches for credentials in this order:

1. **GlobalProtect-specific keychain entry** (if previously saved by the app)
2. **Internet passwords** for:
   - `fanduel.com`
   - `okta.com`
   - `fanduel`
   - `okta`
3. If username found but password not found, prompts for password only
4. If nothing found, prompts for both username and password

### Security Considerations

- ✅ Credentials stored in macOS Keychain (encrypted by macOS)
- ✅ Uses macOS native security APIs
- ✅ No plain text storage
- ✅ Users can view/delete credentials in Keychain Access app
- ✅ MFA handled automatically by oktaloginwrapper

### Requirements

- macOS 10.13 or later
- Python 3 (usually pre-installed on macOS)
- `oktaloginwrapper` package (installed automatically or via requirements)

### Installation for End Users

**If distributing as .app:**
- No installation needed - just double-click

**If distributing as Python script:**
```bash
# One-time setup (can be automated)
pip3 install oktaloginwrapper requests

# Then run
python3 download_globalprotect_app.py
```

## Alternative Solutions

### `download_globalprotect_gui.py`
- Uses tkinter for GUI (if available)
- Similar keychain integration
- Good fallback if native dialogs don't work

### `download_globalprotect_simple.py`
- Command-line version
- Still uses keychain for username detection
- Good for IT/automation use cases

### `download_globalprotect.py`
- Selenium-based (browser automation)
- Most complex but most flexible
- Good for advanced use cases

## Troubleshooting

### "oktaloginwrapper not found"
```bash
pip3 install oktaloginwrapper
```

### Keychain Access Issues
- User may need to allow access in System Preferences > Security & Privacy
- Check Keychain Access app for stored credentials

### MFA Issues
- oktaloginwrapper handles MFA automatically
- If MFA fails, user may need to use push notification or TOTP

### Download Fails
- Verify user has access to GlobalProtect portal
- Check network connectivity
- Verify Okta credentials are correct

## Support

For issues or questions:
1. Check README_GLOBALPROTECT.md for detailed documentation
2. Verify keychain has credentials: `security find-generic-password -a fanduel_okta -s GlobalProtect_Okta -w`
3. Test with command-line version first to isolate issues

