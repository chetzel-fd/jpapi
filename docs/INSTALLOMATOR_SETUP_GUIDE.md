# 🚀 Installomator Setup Guide

This guide shows you how to easily set up Installomator objects for any app using jpapi.

## 📋 Quick Start

### Method 1: Using the Easy Script (Recommended)

The simplest way to add any app and create a policy:

```bash
# Add Adobe Creative Cloud Desktop
python3 scripts/add_installomator_app.py \
  "Adobe Creative Cloud Desktop" \
  "adobecreativeclouddesktop" \
  --description "Adobe Creative Cloud Desktop application" \
  --category "Productivity" \
  --policy-name "Install Adobe Creative Cloud Desktop" \
  --output-file "adobe_creative_cloud_policy.json"

# Add Microsoft Teams
python3 scripts/add_installomator_app.py \
  "Microsoft Teams" \
  "microsoftteams" \
  --category "Communication" \
  --policy-type "daily_update"

# Add Google Chrome
python3 scripts/add_installomator_app.py \
  "Google Chrome" \
  "googlechrome" \
  --category "Browsers" \
  --scope-groups "All Computers" "Marketing Team"
```

### Method 2: Using jpapi CLI Commands

```bash
# List all available apps
jpapi installomator list apps

# Search for specific apps
jpapi installomator search apps adobe

# Create a policy for an existing app
jpapi create-policy adobecreativeclouddesktop \
  --policy-name "Install Adobe Creative Cloud Desktop" \
  --category "Productivity" \
  --scope-groups "All Computers" \
  --output-file "adobe_policy.json"

# Add a new app and create policy
jpapi add-app "Microsoft Teams" "microsoftteams" \
  --description "Microsoft Teams communication platform" \
  --category "Communication" \
  --create-policy \
  --policy-type "daily_update"
```

## 🔧 Available Commands

### `jpapi installomator` - Main Installomator Commands
- `list apps` - List all available apps
- `search apps <term>` - Search for apps
- `create policy` - Interactive policy creation
- `create batch <file>` - Create policies from batch file

### `jpapi add-app` - Add New Apps
- `jpapi add-app "App Name" "label"` - Add a new app
- `--description` - App description
- `--category` - App category
- `--create-policy` - Create policy immediately
- `--policy-type` - Type of policy (install/daily_update/latest_version)
- `--scope-groups` - Computer groups to scope to
- `--dry-run` - Show what would be done

### `jpapi create-policy` - Create Policies
- `jpapi create-policy <label>` - Create policy for app
- `--policy-name` - Custom policy name
- `--policy-type` - Type of policy
- `--scope-groups` - Computer groups
- `--category` - Policy category
- `--output-file` - Save to file instead of creating
- `--dry-run` - Show what would be created

## 📝 Examples

### Example 1: Adobe Creative Cloud Desktop
```bash
# Using the easy script
python3 scripts/add_installomator_app.py \
  "Adobe Creative Cloud Desktop" \
  "adobecreativeclouddesktop" \
  --description "Adobe Creative Cloud Desktop application" \
  --category "Productivity" \
  --policy-name "Install Adobe Creative Cloud Desktop" \
  --scope-groups "All Computers" "Creative Team" \
  --output-file "adobe_policy.json"
```

### Example 2: Microsoft Office
```bash
# Using jpapi CLI
jpapi add-app "Microsoft Office" "microsoftoffice" \
  --description "Microsoft Office productivity suite" \
  --category "Productivity" \
  --create-policy \
  --policy-type "install" \
  --scope-groups "All Computers"
```

### Example 3: Daily Update Policy
```bash
# Create a daily update policy for Chrome
jpapi create-policy googlechrome \
  --policy-name "Update Google Chrome Daily" \
  --policy-type "daily_update" \
  --category "Browsers" \
  --scope-groups "All Computers" \
  --output-file "chrome_update_policy.json"
```

## 🎯 Policy Types

- **`install`** - One-time installation
- **`daily_update`** - Daily update checks
- **`latest_version`** - Always install latest version

## 🎛️ Triggers

- **`EVENT`** - Manual trigger or custom event
- **`ENROLLMENT_COMPLETE`** - Runs after device enrollment

## 📊 Scope Groups

- **`All Computers`** - All managed computers
- **`Marketing Team`** - Specific computer group
- **`Creative Team`** - Another computer group
- Multiple groups can be specified

## 🔍 Finding Installomator Labels

To find the correct Installomator label for any app:

1. Check the [Installomator GitHub repository](https://github.com/Installomator/Installomator)
2. Look in the `Labels.txt` file for available labels
3. Common labels include:
   - `googlechrome` - Google Chrome
   - `firefox` - Mozilla Firefox
   - `slack` - Slack
   - `zoom` - Zoom
   - `microsoftoffice` - Microsoft Office
   - `adobecreativeclouddesktop` - Adobe Creative Cloud Desktop
   - `1password` - 1Password
   - `dropbox` - Dropbox

## 📄 Output Files

When you use `--output-file`, the script creates a JSON file with the complete JAMF policy that can be:

1. **Imported into JAMF Pro** - Use the policy JSON directly
2. **Modified and customized** - Edit the JSON before importing
3. **Used as a template** - Copy and modify for similar apps

## 🚨 Troubleshooting

### App Not Found
```bash
# Check if app exists
jpapi installomator search apps "app name"

# List all apps
jpapi installomator list apps
```

### Policy Creation Fails
```bash
# Use dry-run to see what would be created
jpapi create-policy <label> --dry-run

# Check the policy configuration
jpapi create-policy <label> --output-file "debug_policy.json"
```

### Adding New Apps
```bash
# Add app first, then create policy
jpapi add-app "App Name" "label" --dry-run
jpapi create-policy "label" --dry-run
```

## 🎉 Success!

Once you've created a policy, you'll have:

1. ✅ **App added to Installomator service**
2. ✅ **JAMF policy JSON generated**
3. ✅ **Ready-to-deploy policy configuration**

The policy can be imported into JAMF Pro and will use Installomator to install/update the specified application on targeted computers.

## 🔄 Replication

To replicate this process for any app:

1. **Find the Installomator label** for your app
2. **Run the easy script** with the app details
3. **Import the generated JSON** into JAMF Pro
4. **Deploy and test** the policy

That's it! The process is now completely automated and replicable for any app supported by Installomator.
