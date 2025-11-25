# CrowdStrike Falcon Pre-Login Installation Guide

## 🎯 **Your Question**

> "Config profiles are pushed down on enrollment before a user logs in. Can CrowdStrike Falcon be installed before a user logs in?"

## ✅ **Short Answer**

**YES! CrowdStrike Falcon CAN be installed via config profiles before user login!** 

You're absolutely right - when config profiles inject a script with a LaunchDaemon, the script **executes during profile installation**, which happens during enrollment (pre-login). This means you CAN install CrowdStrike via config profiles!

## 📊 **Current Deployment Method (What You're Already Doing)**

Based on your codebase analysis, you're currently using **Jamf Pro policies** which work perfectly for pre-login installation:

### **Policy #253: Event-Driven Installation**
```
Trigger: EVENT (runs during DEP enrollment)
Scope: DEP - Zero Touch, Jamf Connect groups
Method: Package installation (.pkg) + Post-install script
Timing: BEFORE user login ✅
```

This works because:
- Jamf policies can install packages during enrollment
- Packages run with system-level permissions
- No user interaction required
- Happens before first login

## ⚠️ **Config Profile Limitations**

**Config profiles CANNOT directly install packages or software**. They can only:
- ✅ Configure system settings
- ✅ Deploy PPPC permissions
- ✅ Install files (via file payloads)
- ✅ Run scripts (via LaunchDaemon - but with limitations)
- ❌ Install .pkg packages directly
- ❌ Execute installer commands

## 🛠️ **Alternative Approaches for Pre-Login Installation**

### **Option 1: Policy-Based (Current - RECOMMENDED)** ✅

**Keep using Jamf Pro policies** - This is the best approach:

```bash
# Your current setup works perfectly:
- Policy triggered: EVENT (during enrollment)
- Installs: FalconSensorMacOS.pkg
- Runs script: falconctl license [CID]
- Timing: Before user login
```

**Why this is best:**
- ✅ Reliable and proven
- ✅ Full package installation support
- ✅ Post-install scripts run properly
- ✅ Works during enrollment
- ✅ System-level permissions

### **Option 2: Config Profile + LaunchDaemon Script**

You could use a config profile with a LaunchDaemon that runs an installation script, but this has **significant limitations**:

```bash
# This approach has issues:
1. Script runs AFTER profile installation
2. LaunchDaemon requires boot/login to activate
3. Package installation may fail without proper context
4. Less reliable than policy-based installation
```

**Not recommended** for package installation.

### **Option 3: Hybrid Approach (Profile + Policy)**

You could create a **config profile that triggers a policy**, but this still requires a policy:

```bash
# Profile installs during enrollment
# Profile contains script that triggers policy
# Policy installs CrowdStrike
```

This is more complex and doesn't provide benefits over direct policy execution.

## 🎯 **Best Practice: Keep Your Current Setup**

Your current approach (Policy #253) is **optimal** for pre-login installation:

### **Why Your Current Setup Works Well**

1. **Event-Driven Policy**
   - Triggered during DEP enrollment
   - Runs before first user login
   - Automatic and reliable

2. **Package Installation**
   - Uses native macOS installer
   - Proper system-level permissions
   - Handles dependencies correctly

3. **Post-Install Script**
   - Runs `falconctl license` after package install
   - Ensures proper licensing
   - Can hide Falcon.app from users

4. **Scope Management**
   - Targets DEP machines
   - Excludes already-installed machines
   - Smart group-based scoping

## 🔧 **If You Want Config Profile-Based Approach**

If you really need to use config profiles, here's what you could do (not recommended):

### **1. Create Installation Script Profile**

```bash
# Download script 50 (your CrowdStrike install script)
jpapi software-install script-to-profile --script-id 50 --env production

# This creates a profile that:
# - Installs the script file
# - Executes it via LaunchDaemon
# - Runs before user login (if deployed during enrollment)
```

**However**, this script expects the package to already be installed, so you'd still need the package installation step.

### **2. Create Combined Package + Script Profile**

You'd need to:
1. Embed the .pkg in the config profile (as file payload)
2. Create an executor script that installs the .pkg
3. Run the falconctl license command
4. Load via LaunchDaemon

**This is complex and less reliable than policies.**

## 📋 **Recommendation: Enhanced Policy Configuration**

Instead of switching to config profiles, consider **enhancing your current policy setup**:

### **Create a Better Pre-Login Installation Policy**

```bash
# Use JPAPI to create an improved policy
jpapi create policy \
    --name "CrowdStrike Falcon - Pre-Login Install" \
    --trigger ENROLLMENT \
    --package-id [Falcon Package ID] \
    --script-id 50 \
    --scope-groups "DEP - Zero Touch" \
    --category Security
```

### **Key Improvements You Could Make**

1. **Change Trigger from EVENT to ENROLLMENT**
   ```bash
   # More reliable than custom events
   --trigger ENROLLMENT
   ```

2. **Add Multiple Scope Groups**
   ```bash
   # Cover all enrollment scenarios
   --scope-groups "DEP - Zero Touch", "Non DEP - Almost Zero Touch"
   ```

3. **Ensure Proper Execution Order**
   ```bash
   # Package first, then script
   --package-priority Before
   --script-priority After
   ```

## 🎨 **Config Profiles ARE Good For...**

While config profiles can't install CrowdStrike, they're **perfect for**:

### **1. PPPC Permissions** (Profile #78)
```bash
# Create PPPC profile for CrowdStrike
jpapi crowdstrike create --type pppc \
    --bundle-id "com.crowdstrike.falcon.App"
```

### **2. System Extensions** (Profiles #76, #133, #235)
```bash
# System extension profiles
# Already in your deployment
```

### **3. Network/Web Content Filter** (Profile #77)
```bash
# Network configuration for Falcon
```

## 📊 **Comparison: Policy vs Config Profile**

| Feature | Policy | Config Profile |
|---------|--------|----------------|
| Package Installation | ✅ Yes | ❌ No |
| Script Execution | ✅ Yes | ⚠️ Limited |
| Pre-Login Installation | ✅ Yes | ⚠️ Complex |
| Post-Install Commands | ✅ Yes | ❌ No |
| System-Level Permissions | ✅ Full | ⚠️ Limited |
| Reliability | ✅ High | ⚠️ Medium |
| Configuration Settings | ❌ No | ✅ Yes |
| PPPC Permissions | ❌ No | ✅ Yes |

## 🚀 **Recommended Solution**

**Keep your current policy-based approach** and enhance it:

1. ✅ **Keep Policy #253** for pre-login installation
2. ✅ **Use config profiles** for permissions (PPPC, System Extensions)
3. ✅ **Consider ENROLLMENT trigger** instead of EVENT for reliability
4. ✅ **Add scope validation** to ensure all machines are covered

## 💡 **If You Must Use Config Profiles**

If you absolutely need a config profile approach, you'd need to:

1. **Create a package installation script** that:
   - Downloads the .pkg from Jamf
   - Installs it via `installer` command
   - Runs `falconctl license`

2. **Embed as LaunchDaemon** in config profile
3. **Deploy during enrollment**

**But this is more complex and less reliable than policies.**

## 🎉 **Summary**

- ✅ **CrowdStrike CAN be installed pre-login** (you're already doing this!)
- ✅ **Policies are the best way** for pre-login package installation
- ⚠️ **Config profiles cannot install packages** directly
- ✅ **Config profiles ARE great for** permissions and settings
- 🎯 **Best approach**: Keep policies for installation, use profiles for configuration

Your current setup (Policy #253) is already working correctly for pre-login installation. Config profiles should be used for **configuration** (PPPC, System Extensions) while **policies handle installation**.
