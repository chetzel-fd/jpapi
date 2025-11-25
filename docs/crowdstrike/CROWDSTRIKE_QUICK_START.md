# CrowdStrike Config Profile Installation - Quick Start

## ✅ **You Were Right!**

Config profiles **CAN** install CrowdStrike before user login by injecting a script with a LaunchDaemon that executes during enrollment!

## 🚀 **Quick Command**

### **Using Your Existing Script (Recommended)**

```bash
# Download script 50, enhance it, deploy as config profile
jpapi software-install crowdstrike \
    --customer-id "C4F6F774753D4D079EB7705FD13B9465-AC" \
    --script-id 50 \
    --package-name "FalconSensorMacOS.MaverickGyr-1124.pkg" \
    --env production
```

### **Create New Installation Profile**

```bash
# Create from scratch with package ID
jpapi software-install crowdstrike \
    --customer-id "C4F6F774753D4D079EB7705FD13B9465-AC" \
    --package-name "FalconSensorMacOS.MaverickGyr-1124.pkg" \
    --package-id 345 \
    --env production
```

## 🎯 **What Happens**

1. **Profile is deployed** to Jamf Pro
2. **During enrollment** (pre-login), profile installs:
   - Installation script → `/usr/local/bin/`
   - Executor script → `/usr/local/bin/`
   - LaunchDaemon → `/Library/LaunchDaemons/`
3. **LaunchDaemon executes immediately** (RunAtLoad)
4. **Script runs before user login**:
   - Installs CrowdStrike package
   - Applies license
   - Hides Falcon.app
   - Verifies installation
5. **User logs in** → CrowdStrike already installed! ✅

## 📋 **Command Options**

```
--customer-id ID     (Required) CrowdStrike Customer ID (CID)
--script-id ID       Use existing script (e.g., 50) and enhance it
--package-name NAME  Package name (default: FalconSensorMacOS.MaverickGyr-1124.pkg)
--package-id ID      Package ID for auto-download (optional)
--profile-name NAME  Custom profile name
--no-deploy          Save locally only (test first)
--env ENV            Environment: production or sandbox
```

## 💡 **Examples**

### **Test First (Save Locally)**
```bash
jpapi software-install crowdstrike \
    --customer-id "C4F6F774753D4D079EB7705FD13B9465-AC" \
    --script-id 50 \
    --no-deploy \
    --env production
```

### **Production Deployment**
```bash
jpapi software-install crowdstrike \
    --customer-id "C4F6F774753D4D079EB7705FD13B9465-AC" \
    --script-id 50 \
    --package-name "FalconSensorMacOS.MaverickGyr-1124.pkg" \
    --package-id 345 \
    --profile-name "CrowdStrike Falcon - Enrollment Install" \
    --env production
```

## ✨ **Key Benefits**

- ✅ **Pre-Login Installation** - Runs during enrollment
- ✅ **Profile-Based** - Consistent with your config profile strategy
- ✅ **Automatic Execution** - Via LaunchDaemon (no user interaction)
- ✅ **Comprehensive Logging** - `/var/log/crowdstrike_install.log`
- ✅ **Idempotent** - Safe to run multiple times
- ✅ **Error Handling** - Graceful failure handling

## 🎉 **That's It!**

The config profile will install CrowdStrike automatically during enrollment, before any user logs in. Perfect for DEP/ADE workflows!

For complete details, see `CROWDSTRIKE_CONFIG_PROFILE_INSTALLATION.md`



