# Software Installation via Jamf Pro Config Profiles

This directory contains comprehensive tools for software installation using Jamf Pro configuration profiles, policies, and packages.

## 🎯 Overview

While **config profiles cannot directly install software**, they are excellent for:
- **Browser extension installation** (Chrome, Firefox, Safari, Edge)
- **Application configuration** (preferences, settings)
- **PPPC permissions** (privacy preferences)
- **System configuration** (managed preferences)

For actual software installation, we use a **hybrid approach**:
1. **Config profiles** for configuration and permissions
2. **Jamf Pro policies** for software installation (via Installomator, packages, or scripts)

## 📁 Files

### Main Scripts
- `software_install_via_config_profile.py` - Main installation script
- `deploy_software_installation.py` - Deployment manager with templates
- `templates/` - Mobileconfig and policy templates

### Templates
- `chrome_extension_template.mobileconfig` - Chrome extension installation
- `app_pppc_template.mobileconfig` - PPPC permissions profile
- `app_preferences_template.mobileconfig` - Application preferences
- `installomator_policy_template.json` - Installomator policy template

## 🚀 Quick Start

### 1. Install Browser Extension

```bash
# Install Chrome extension
python software_install_via_config_profile.py install-extension \
    --app Chrome \
    --extension-id abc123def456 \
    --extension-url https://example.com/manifest.json

# Install Firefox extension
python software_install_via_config_profile.py install-extension \
    --app Firefox \
    --extension-id xyz789 \
    --extension-name "My Extension"
```

### 2. Install Application with Installomator

```bash
# Install app using Installomator
python software_install_via_config_profile.py install-app \
    --app-name "Slack" \
    --method installomator \
    --label slack

# Create custom policy
python software_install_via_config_profile.py create-policy \
    --app-name "Zoom" \
    --package-id 123 \
    --script-id 456
```

### 3. Create PPPC Permissions Profile

```bash
# Create PPPC profile for app permissions
python software_install_via_config_profile.py create-pppc \
    --app-name "Chrome" \
    --bundle-id com.google.Chrome \
    --permissions full_disk_access,camera,microphone
```

## 🔧 Advanced Usage

### Template-Based Deployment

```bash
# Deploy using templates
python deploy_software_installation.py deploy-extension \
    --template chrome \
    --extension-id abc123def456 \
    --extension-url https://example.com/manifest.json

# Deploy app with Installomator
python deploy_software_installation.py deploy-app \
    --app-name "Slack" \
    --method installomator \
    --category "Productivity"
```

### Batch Deployment

Create a configuration file `deployment_config.json`:

```json
{
  "extensions": [
    {
      "template": "chrome",
      "extension_id": "abc123def456",
      "extension_url": "https://example.com/manifest.json",
      "extension_name": "My Chrome Extension"
    },
    {
      "template": "firefox",
      "extension_id": "xyz789",
      "extension_name": "My Firefox Extension"
    }
  ],
  "apps": [
    {
      "app_name": "Slack",
      "label": "slack",
      "category": "Productivity"
    },
    {
      "app_name": "Zoom",
      "label": "zoom",
      "category": "Communication"
    }
  ],
  "pppc_profiles": [
    {
      "app_name": "Chrome",
      "bundle_id": "com.google.Chrome",
      "permissions": ["full_disk_access", "camera", "microphone"]
    }
  ]
}
```

Then deploy:

```bash
python deploy_software_installation.py batch-deploy --config deployment_config.json
```

## 📋 Installation Methods

### 1. Config Profile Approach (Configuration Only)

**Use for:**
- Browser extensions
- Application preferences
- PPPC permissions
- System configuration

**Limitations:**
- Cannot install actual software
- Only configures existing applications

**Example:**
```bash
# Install Chrome extension
python software_install_via_config_profile.py install-extension \
    --app Chrome \
    --extension-id abc123def456
```

### 2. Hybrid Approach (Recommended)

**Use for:**
- Complete software installation with configuration
- Applications that need both installation and setup

**Components:**
- Installomator policy for software installation
- Config profile for permissions and preferences

**Example:**
```bash
# Install app with full configuration
python software_install_via_config_profile.py install-app \
    --app-name "Slack" \
    --method installomator
```

### 3. Pure Policy Approach

**Use for:**
- Direct package installation
- Custom installation scripts
- Legacy software deployment

**Example:**
```bash
# Create installation policy
python software_install_via_config_profile.py create-policy \
    --app-name "Custom App" \
    --package-id 123 \
    --script-id 456
```

## 🔒 PPPC Permissions

Privacy Preferences Policy Control (PPPC) profiles grant permissions to applications:

### Available Permissions
- `full_disk_access` - Full Disk Access
- `network_volumes` - Network Volumes
- `sys_admin_files` - System Administration Files
- `camera` - Camera
- `microphone` - Microphone
- `photos` - Photos
- `contacts` - Contacts
- `calendar` - Calendar
- `reminders` - Reminders
- `location` - Location Services

### Example
```bash
python software_install_via_config_profile.py create-pppc \
    --app-name "Zoom" \
    --bundle-id us.zoom.xos \
    --permissions camera,microphone,full_disk_access
```

## 🌐 Browser Extensions

### Supported Browsers
- **Chrome** - Uses `ExtensionInstallForcelist`
- **Firefox** - Uses managed preferences
- **Safari** - Uses Safari preferences
- **Edge** - Uses Edge preferences

### Chrome Extension Example
```bash
python software_install_via_config_profile.py install-extension \
    --app Chrome \
    --extension-id chlnagmkonfbonegilldifigaelbfcfe \
    --extension-url https://example.com/manifest.json
```

### Firefox Extension Example
```bash
python software_install_via_config_profile.py install-extension \
    --app Firefox \
    --extension-id xyz789 \
    --extension-name "My Extension"
```

## 📦 Installomator Integration

Installomator is a powerful tool for installing macOS applications:

### Supported Apps
- 400+ popular macOS applications
- Automatic version detection
- Silent installation
- Update management

### Example
```bash
python software_install_via_config_profile.py install-app \
    --app-name "Slack" \
    --method installomator \
    --label slack
```

## 🔧 Customization

### Template Modification

Templates are located in `templates/` directory:

1. **Chrome Extension Template** (`chrome_extension_template.mobileconfig`)
   - Replace `EXTENSION_ID` with actual extension ID
   - Replace `EXTENSION_URL` with manifest URL
   - Replace `EXTENSION_NAME` with human-readable name

2. **PPPC Template** (`app_pppc_template.mobileconfig`)
   - Replace `APP_NAME` with application name
   - Replace `APP_BUNDLE_ID` with bundle identifier
   - Modify permissions as needed

3. **Preferences Template** (`app_preferences_template.mobileconfig`)
   - Replace `APP_BUNDLE_ID` with bundle identifier
   - Add custom preference keys and values

### Custom Policies

Create custom installation policies:

```bash
python software_install_via_config_profile.py create-policy \
    --app-name "Custom App" \
    --package-id 123 \
    --script-id 456 \
    --policy-name "Install Custom App"
```

## 🚨 Important Notes

### Security Considerations
- Always test profiles in sandbox environment first
- Review PPPC permissions carefully
- Validate extension URLs and IDs
- Use signed profiles in production

### Limitations
- Config profiles cannot install software directly
- Some applications require specific installation methods
- Browser extensions may need additional configuration
- PPPC permissions are macOS-specific

### Best Practices
1. **Test First** - Always test in sandbox environment
2. **Document Changes** - Keep track of deployed profiles
3. **Version Control** - Store templates in version control
4. **Monitor Deployment** - Check deployment status regularly
5. **Clean Up** - Remove unused profiles and policies

## 🆘 Troubleshooting

### Common Issues

1. **Profile Not Deploying**
   - Check Jamf Pro connection
   - Verify profile syntax
   - Check scope settings

2. **Extension Not Installing**
   - Verify extension ID format
   - Check manifest URL accessibility
   - Ensure browser is managed

3. **PPPC Not Working**
   - Verify bundle ID format
   - Check code requirements
   - Ensure app is installed

4. **Installomator Failing**
   - Check app label exists
   - Verify network connectivity
   - Check script permissions

### Debug Mode

Enable debug logging:

```bash
export JPAPI_DEBUG=1
python software_install_via_config_profile.py install-extension --app Chrome --extension-id abc123
```

## 📚 Additional Resources

- [Jamf Pro Configuration Profiles](https://docs.jamf.com/configuration-profiles/)
- [Installomator Documentation](https://github.com/Installomator/Installomator)
- [macOS Privacy Preferences](https://developer.apple.com/documentation/devicemanagement/privacypreferencespolicycontrol)
- [Chrome Enterprise Policies](https://chromeenterprise.google/policies/)

## 🤝 Contributing

To add new templates or features:

1. Create template in `templates/` directory
2. Add support in deployment scripts
3. Update documentation
4. Test thoroughly
5. Submit pull request

## 📄 License

This software is part of the JPAPI project. See the main project license for details.













