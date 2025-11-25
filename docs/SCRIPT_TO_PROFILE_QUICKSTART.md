# Script to Profile - Quick Start

## 🎯 **What You Asked For**

> "using jpapi, can we download script 199 in prod and then create the install script as a config profile using this tool?"

## ✅ **Yes! Here's How:**

### **Simple Command**
```bash
# Download script 199 from production and create config profile
jpapi software-install script-to-profile --script-id 199 --env production
```

## 🚀 **What Happens**

1. **Downloads script 199** from Jamf Pro production
2. **Creates a Jamf Pro policy** that runs the script (named "Run [Script Name]")
3. **Creates a config profile** that installs the script file to devices

## 📋 **Full Command Options**

```bash
jpapi software-install script-to-profile \
    --script-id 199              # Script ID (required)
    --env production             # Environment: production or sandbox
    --profile-name "Custom Name" # Optional: Custom profile name
    --description "Description"  # Optional: Profile description
    --no-deploy                  # Optional: Save locally only (no Jamf deployment)
```

## 📊 **Examples**

### **Download Script 199 from Production**
```bash
jpapi software-install script-to-profile --script-id 199 --env production
```

### **Download from Sandbox**
```bash
jpapi software-install script-to-profile --script-id 199 --env sandbox
```

### **Save Locally (No Deployment)**
```bash
jpapi software-install script-to-profile --script-id 199 \
    --no-deploy \
    --env production
```

### **Custom Name**
```bash
jpapi software-install script-to-profile --script-id 199 \
    --profile-name "App Installation Script" \
    --env production
```

## ✨ **How It Works**

The config profile automatically:
1. **Installs** the script file to `/usr/local/bin/`
2. **Executes** the script via LaunchDaemon when profile is installed
3. **Runs once** by default (or on every boot/login if you use `--execution-trigger always`)

## 📁 **What Gets Created**

**Config Profile** in Jamf Pro:
- Name: "[Script Name] Script Profile"
- Contains: Script file + Executor + LaunchDaemon
- **Auto-executes** when installed on devices

## 🎉 **That's It!**

You can now download any script from Jamf Pro and create it as a config profile (plus policy) with a single command!

For more details, see `SCRIPT_TO_PROFILE_GUIDE.md`
