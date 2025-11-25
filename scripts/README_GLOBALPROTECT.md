# GlobalProtect Downloader with Okta Authentication

This script automates downloading the GlobalProtect macOS installer from the FanDuel portal after authenticating through Okta.

## 🎯 Recommended: User-Friendly Version (For End Users)

### **`download_globalprotect_app.py`** - Native macOS App (Best for End Users)

This version is designed for end users with minimal technical knowledge:
- ✅ **Automatically checks macOS Keychain** for existing credentials
- ✅ **Uses native macOS dialogs** (no command line needed)
- ✅ **Stores credentials securely** in Keychain for future use
- ✅ **Can be packaged as a .app bundle** for easy distribution

#### Installation

```bash
pip install oktaloginwrapper requests
```

#### Usage

**Option 1: Run as Python script**
```bash
python scripts/download_globalprotect_app.py
```

**Option 2: Package as macOS App**
```bash
# Create the app bundle
./scripts/create_globalprotect_app.sh

# Then double-click "GlobalProtect Downloader.app" or:
open "scripts/GlobalProtect Downloader.app"
```

#### Features

- **Keychain Integration**: Automatically finds and uses existing Okta/FanDuel credentials from macOS Keychain
- **Native Dialogs**: Uses macOS native dialog boxes (no terminal required)
- **Credential Storage**: Saves credentials securely in Keychain for future downloads
- **Zero Configuration**: Works out of the box for most users

---

### Alternative: GUI Version with Tkinter

**`download_globalprotect_gui.py`** - Simple GUI version (if tkinter is available)

```bash
pip install oktaloginwrapper requests
python scripts/download_globalprotect_gui.py
```

---

## 🔧 Advanced Options (For IT/Developers)

### Option 1: Using Selenium (Automated Browser)

```bash
pip install selenium requests
brew install chromedriver
python scripts/download_globalprotect.py --method selenium
```

### Option 2: Command Line with oktaloginwrapper

```bash
pip install oktaloginwrapper requests
python scripts/download_globalprotect_simple.py --username your.email@fanduel.com
```

## 📋 How It Works

### For End Users (Recommended)

1. **First Time**: Run the app, enter your Okta username and password when prompted
2. **Credentials Saved**: Your credentials are securely stored in macOS Keychain
3. **Next Time**: The app automatically finds and uses your saved credentials - no typing needed!
4. **Download**: GlobalProtect.pkg is downloaded to your Downloads folder

### Keychain Integration

The app automatically searches for existing credentials in macOS Keychain:
- Looks for FanDuel/Okta internet passwords
- Checks for previously saved GlobalProtect credentials
- Uses the same password if your Okta password matches your keychain password

This means most users won't need to enter credentials at all if they've logged into Okta before!

### Authentication Methods

#### Method 1: Selenium (Automated Browser)

```bash
python scripts/download_globalprotect.py --method selenium
```

- Opens a headless Chrome browser
- Handles Okta login form automatically
- Supports MFA (you'll need to complete MFA in the browser)
- Best for automation

#### Method 2: Manual Cookie Input

```bash
python scripts/download_globalprotect.py --method manual
```

- Guides you through manual authentication
- You login in your regular browser
- Copy cookies from browser developer tools
- Paste into the script
- Best if Selenium doesn't work or you prefer manual control

## Manual Cookie Method Steps

1. Open your browser and navigate to the Okta login page
2. Complete login (including MFA if required)
3. Navigate to: `https://secure.fanduel.com/global-protect/getmsi.esp?version=none&platform=mac`
4. Open Developer Tools (F12 or Cmd+Option+I)
5. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
6. Find **Cookies** for `secure.fanduel.com`
7. Copy the cookie values or use a browser extension to export cookies
8. Paste into the script when prompted

## Troubleshooting

### Selenium Issues

If Selenium fails:
- Make sure ChromeDriver is installed and in PATH
- Try the manual method instead: `--method manual`
- Check that Chrome/Chromium is installed

### Authentication Failures

- Verify your Okta URL is correct
- Ensure you have access to the GlobalProtect portal
- Check that MFA is completed if required
- Try the manual cookie method

### Download Failures

- Verify the download URL is correct
- Check that your session hasn't expired
- Ensure you have network access to `secure.fanduel.com`

## Security Notes

- ✅ **Keychain Storage**: Credentials are stored securely in macOS Keychain (encrypted by macOS)
- ✅ **No Plain Text**: Passwords are never stored in plain text files
- ✅ **Native Security**: Uses macOS native security APIs
- ✅ **User Control**: Users can delete stored credentials from Keychain Access app if needed
- ✅ **MFA Support**: Works with Okta MFA (handled automatically by oktaloginwrapper)

## Deployment for End Users

### Option 1: Distribute as .app Bundle

```bash
# Create the app
./scripts/create_globalprotect_app.sh

# Distribute "GlobalProtect Downloader.app" to users
# Users just double-click to run
```

### Option 2: Distribute as Python Script

Package with dependencies:
```bash
# Create a simple installer script that:
# 1. Checks for Python 3
# 2. Installs oktaloginwrapper if needed
# 3. Runs the downloader
```

### Option 3: Deploy via MDM

- Package the .app bundle
- Deploy via Jamf/Intune/etc.
- Users run it once, credentials are saved for future use

## Example Output

```
🔐 GlobalProtect Downloader with Okta Authentication
============================================================
Okta Username: user@fanduel.com
Okta Password: 
🌐 Opening browser for Okta authentication...
📝 Please complete authentication in the browser...
⏳ Waiting for authentication to complete...
✅ Authentication successful!

📥 Downloading GlobalProtect.pkg to /Users/username/Downloads/GlobalProtect.pkg...
🔄 Following redirect to: https://secure.fanduel.com/global-protect/msi/GlobalProtect.pkg
📥 Progress: 100.0% (45234567/45234567 bytes)
✅ Successfully downloaded: /Users/username/Downloads/GlobalProtect.pkg
   File size: 45,234,567 bytes
```

