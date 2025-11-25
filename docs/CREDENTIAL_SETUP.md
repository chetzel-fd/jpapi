# 🔐 JPAPI Credential Setup Guide

Complete guide for setting up authentication with JPAPI.

---

## 🚀 Quick Start

```bash
# Run the interactive setup wizard
jpapi setup
```

The wizard will guide you through the entire process!

---

## 📋 Setup Methods

### Method 1: Interactive Setup (Recommended)

```bash
jpapi setup
```

**What happens:**
1. Auto-detects existing credentials in macOS Keychain (if any)
2. Prompts you to choose from existing credentials or create new ones
3. Guides you through OAuth or Basic Auth setup
4. Tests the connection automatically
5. Saves credentials securely to macOS Keychain

### Method 2: OAuth Setup (Direct)

```bash
jpapi setup oauth
```

**Steps:**
1. Get OAuth credentials from JAMF Pro (see below)
2. Paste the JSON when prompted
3. Credentials are automatically parsed and saved

### Method 3: Basic Auth Setup

```bash
jpapi setup basic
```

**Steps:**
1. Enter JAMF Pro server URL
2. Enter username
3. Enter password (hidden input)
4. Credentials saved securely

### Method 4: Environment-Specific Setup

```bash
jpapi setup --env sandbox     # For test/sandbox environment
jpapi setup --env production  # For production environment
```

---

## 🔑 Getting OAuth Credentials from JAMF Pro

### Step-by-Step Instructions

1. **Log into JAMF Pro**
   - Open your JAMF Pro admin console
   - Navigate to: **Settings → System Settings → API Roles and Clients**

2. **Create API Client**
   - Click **New** or **+** button
   - Fill in the required information:
     - **Display Name**: e.g., "JPAPI CLI Access"
     - **Description**: Optional description
     - **Access Token Lifetime**: Set as needed (default is fine)

3. **Configure Privileges**
   - Select the privileges your API client needs
   - For read-only access: Select only "Read" privileges
   - For full access: Select all required privileges
   - **Tip**: Start with minimal privileges and add more as needed

4. **Save and Copy JSON**
   - Click **Save** or **Create**
   - JAMF Pro will display a JSON response like:
     ```json
     {
       "client_id": "abc123-def456-...",
       "client_secret": "xyz789-...",
       "url": "https://your-company.jamfcloud.com"
     }
     ```
   - **⚠️ IMPORTANT**: Copy this entire JSON - you won't be able to see the secret again!

5. **Paste into JPAPI Setup**
   - Run `jpapi setup oauth`
   - Paste the entire JSON when prompted
   - JPAPI will automatically parse and save it

---

## ✅ Verifying Your Setup

### Test Your Connection

```bash
# Test authentication
jpapi setup test

# Or test with a simple command
jpapi list policies --limit 1
```

### List Saved Credentials

```bash
# See what credentials are saved
jpapi setup list
```

### Check Authentication Status

```bash
# Try a command that requires authentication
jpapi list policies
```

If you see data, authentication is working! ✅

---

## 🔄 Managing Multiple Environments

JPAPI supports multiple environments (sandbox, production, etc.):

```bash
# Set up sandbox credentials
jpapi setup --env sandbox

# Set up production credentials  
jpapi setup --env production

# Use specific environment
jpapi --env sandbox list policies
jpapi --env production list policies
```

---

## 🛠️ Troubleshooting

### "Authentication not configured"

**Solution:**
```bash
jpapi setup
```

### "Authentication failed" or 401 errors

**Possible causes:**
- Incorrect credentials
- Expired OAuth token
- Insufficient privileges

**Solutions:**
```bash
# Test current credentials
jpapi setup test

# Re-configure credentials
jpapi setup

# Or re-setup OAuth
jpapi setup oauth
```

### "Command not found: auth"

**Note:** The command is `jpapi setup`, not `jpapi auth`

**Correct usage:**
```bash
jpapi setup          # ✅ Correct
jpapi setup test     # ✅ Test credentials
jpapi setup list     # ✅ List credentials
```

### Credentials not saving

**Check:**
- macOS Keychain access permissions
- File permissions on config directory
- Disk space available

**Solution:**
```bash
# Try setup again
jpapi setup

# Check keychain manually
security find-generic-password -s jpapi
```

---

## 🔒 Security Best Practices

### ✅ Do:
- Use OAuth 2.0 (preferred over Basic Auth)
- Store credentials in macOS Keychain (automatic)
- Use environment-specific credentials
- Test credentials before using in production
- Use read-only credentials when possible

### ❌ Don't:
- Share credentials between team members
- Commit credentials to version control
- Use production credentials for testing
- Store credentials in plain text files
- Use overly permissive API roles

---

## 📚 Additional Resources

- [JAMF Pro API Documentation](https://developer.jamf.com/jamf-pro/reference)
- [OAuth 2.0 Guide](https://developer.jamf.com/jamf-pro/docs/authentication)
- [JPAPI Troubleshooting Guide](docs/troubleshooting.md)

---

## 💡 Pro Tips

1. **Use OAuth over Basic Auth** - More secure and supports token refresh
2. **Start with Read-Only** - Test with minimal privileges first
3. **Environment Variables** - You can also set `JPAPI_SANDBOX_URL` and `JPAPI_PROD_URL`
4. **Multiple Users** - Each user should have their own API client in JAMF Pro
5. **Regular Testing** - Run `jpapi setup test` periodically to verify credentials

---

**Need Help?** Run `jpapi setup --help` or check the [main README](README.md)

