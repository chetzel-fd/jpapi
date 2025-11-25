# CrowdStrike Falcon Installation via Config Profile (Pre-Login)

## 🎯 **Yes, You're Right!**

When a config profile injects a script with a LaunchDaemon, the script **executes during profile installation**, which happens **during enrollment (before user login)**.

## 🚀 **How It Works**

### **The Flow:**

```
1. Device enrolls via DEP/ADE
   ↓
2. Config profiles are pushed (including your CrowdStrike installation profile)
   ↓
3. Profile installs script file payload
   ↓
4. Profile installs LaunchDaemon payload
   ↓
5. LaunchDaemon executes immediately (RunAtLoad)
   ↓
6. Script runs BEFORE user login:
   - Downloads/installs CrowdStrike package
   - Applies license
   - Hides Falcon.app
   ↓
7. User logs in → CrowdStrike is already installed! ✅
```

## 📋 **Usage**

### **Create CrowdStrike Installation Profile**

```bash
# Using your existing script (script ID 50) and enhancing it
jpapi software-install crowdstrike \
    --customer-id "C4F6F774753D4D079EB7705FD13B9465-AC" \
    --script-id 50 \
    --package-name "FalconSensorMacOS.MaverickGyr-1124.pkg" \
    --env production
```

### **Create New Installation Profile**

```bash
# Create a new installation profile from scratch
jpapi software-install crowdstrike \
    --customer-id "C4F6F774753D4D079EB7705FD13B9465-AC" \
    --package-name "FalconSensorMacOS.MaverickGyr-1124.pkg" \
    --package-id 345 \
    --env production
```

### **Save Locally First (Test)**

```bash
# Create profile locally to review before deploying
jpapi software-install crowdstrike \
    --customer-id "C4F6F774753D4D079EB7705FD13B9465-AC" \
    --package-name "FalconSensorMacOS.MaverickGyr-1124.pkg" \
    --no-deploy \
    --env production
```

## 🔧 **What the Profile Does**

The config profile creates **three payloads**:

### **1. Installation Script Payload**
- Installs comprehensive CrowdStrike installation script
- Location: `/usr/local/bin/crowdstrike_falcon_installation.sh`
- Script includes:
  - Package download/verification
  - Package installation
  - License application
  - Verification
  - Error handling and logging

### **2. Executor Script Payload**
- Wrapper script that ensures proper execution
- Makes main script executable
- Handles cleanup
- Location: `/usr/local/bin/crowdstrike_falcon_installation_executor.sh`

### **3. LaunchDaemon Payload**
- Creates LaunchDaemon plist at `/Library/LaunchDaemons/`
- Executes immediately when profile is installed (`RunAtLoad: true`)
- Runs **before user login** during enrollment
- For "once" mode: Unloads after execution

## 📊 **Complete Installation Script**

The profile includes a comprehensive installation script that:

1. ✅ **Checks if already installed** (idempotent)
2. ✅ **Locates package** (Jamf cache, downloaded, or manual location)
3. ✅ **Verifies package integrity**
4. ✅ **Installs package** using macOS installer
5. ✅ **Applies license** via falconctl
6. ✅ **Hides Falcon.app** from users (optional)
7. ✅ **Verifies installation** and logs status
8. ✅ **Comprehensive logging** to `/var/log/crowdstrike_install.log`

## 🎯 **Key Features**

### **Pre-Login Execution**
- ✅ Runs during enrollment (before first user login)
- ✅ System-level permissions
- ✅ No user interaction required
- ✅ Automatic execution via LaunchDaemon

### **Package Handling**
- ✅ Checks multiple locations for package
- ✅ Can download from Jamf Pro if package_id provided
- ✅ Verifies package before installation
- ✅ Handles installation errors gracefully

### **License Management**
- ✅ Applies CrowdStrike Customer ID automatically
- ✅ Verifies license after application
- ✅ Logs license status

### **Robust Error Handling**
- ✅ Comprehensive logging
- ✅ Error detection and reporting
- ✅ Idempotent (safe to run multiple times)
- ✅ Cleanup on failure

## 📁 **Profile Structure**

```xml
Configuration Profile
├── Payload 1: Installation Script
│   └── /usr/local/bin/crowdstrike_falcon_installation.sh
├── Payload 2: Executor Script  
│   └── /usr/local/bin/crowdstrike_falcon_installation_executor.sh
└── Payload 3: LaunchDaemon
    └── /Library/LaunchDaemons/com.jamf.crowdstrike.falcon.installation.plist
```

## 🔍 **How LaunchDaemon Works During Enrollment**

When the config profile is installed during enrollment:

1. **Profile Installation** (MDM framework)
   - Installs all three payloads
   - Creates script files
   - Creates LaunchDaemon plist

2. **LaunchDaemon Activation**
   - macOS automatically loads LaunchDaemons when plist is created
   - `RunAtLoad: true` executes immediately
   - Script runs with root permissions

3. **Script Execution**
   - Executor script runs
   - Makes main script executable
   - Executes main installation script
   - Installation happens **before user login**

4. **Cleanup** (for "once" mode)
   - LaunchDaemon unloads itself
   - Plist is removed
   - Only scripts remain for reference

## ⚠️ **Important Considerations**

### **Package Availability**

The script needs access to the CrowdStrike package. It checks:

1. **Jamf Pro Cache**: `/Library/Caches/JSS/[package-name]`
2. **Jamf CLI Download**: If `package_id` provided and `jamf` command available
3. **Manual Locations**: `/tmp/`, common cache locations

**Best Practice**: Ensure package is available in Jamf cache or provide `package_id` for automatic download.

### **Network Requirements**

- ✅ Package download requires network (if not cached)
- ✅ License application requires network
- ✅ Enrollment typically has network access

### **Execution Timing**

- ✅ Runs during enrollment (pre-login)
- ✅ System-level permissions available
- ✅ No user interaction needed
- ⚠️ May run before network is fully ready (script handles retries)

## 🎨 **Comparison: Policy vs Config Profile**

| Feature | Policy | Config Profile (This) |
|---------|--------|----------------------|
| Pre-Login Installation | ✅ Yes | ✅ Yes |
| Package Installation | ✅ Yes | ✅ Yes (via script) |
| Automatic Execution | ✅ Yes | ✅ Yes (LaunchDaemon) |
| Deployment Method | Policy | Config Profile |
| Scope Management | Policy scope | Profile scope |
| Execution Timing | Policy trigger | Profile installation |
| Reliability | ✅ High | ✅ High |
| Flexibility | ⚠️ Policy-specific | ✅ Profile-based |

## 🚀 **Best Practices**

### **1. Test First**
```bash
# Create locally and review
jpapi software-install crowdstrike \
    --customer-id "YOUR_CID" \
    --no-deploy \
    --env production

# Review the generated profile
open generated_profiles/*.mobileconfig
```

### **2. Use Existing Script**
```bash
# Enhance your existing script 50
jpapi software-install crowdstrike \
    --customer-id "YOUR_CID" \
    --script-id 50 \
    --env production
```

### **3. Provide Package ID**
```bash
# For automatic package download
jpapi software-install crowdstrike \
    --customer-id "YOUR_CID" \
    --package-id 345 \
    --env production
```

### **4. Scope Appropriately**
- Deploy to DEP enrollment groups
- Exclude already-installed machines
- Use smart groups for targeting

## 📋 **Complete Example**

```bash
# Download your existing script 50, enhance it, and deploy as config profile
jpapi software-install crowdstrike \
    --customer-id "C4F6F774753D4D079EB7705FD13B9465-AC" \
    --script-id 50 \
    --package-name "FalconSensorMacOS.MaverickGyr-1124.pkg" \
    --package-id 345 \
    --profile-name "CrowdStrike Falcon - Enrollment Install" \
    --env production

# Output:
# 📥 Downloading script 50 and enhancing for config profile...
# ✅ Successfully downloaded script: Crowdstrike Falcon install
# 🚀 Deploying profile to Jamf Pro: CrowdStrike Falcon - Enrollment Install
# ✅ Profile deployed successfully: CrowdStrike Falcon - Enrollment Install
# ✅ Successfully created and deployed CrowdStrike installation profile
#    Profile will install CrowdStrike during enrollment (pre-login)
```

## 🎉 **Summary**

**You were absolutely right!** Config profiles **CAN** install CrowdStrike before user login by:

1. ✅ **Installing the script** via file payload
2. ✅ **Executing via LaunchDaemon** immediately when profile installs
3. ✅ **Running during enrollment** (pre-login)
4. ✅ **Installing package and applying license** automatically

This approach gives you:
- **Profile-based deployment** (consistent with your config profile strategy)
- **Pre-login installation** (during enrollment)
- **Automatic execution** (via LaunchDaemon)
- **Comprehensive logging** (for troubleshooting)

**Perfect for DEP/ADE enrollment workflows!** 🚀



