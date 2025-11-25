# Script to Config Profile Guide

## 🎯 **Overview**

This guide explains how to download a script from Jamf Pro and create it as a config profile using JPAPI.

## ✨ **What It Does**

This functionality creates a config profile that:

1. **Downloads the script** from Jamf Pro (production or sandbox)
2. **Installs the script locally** via a file payload (to `/usr/local/bin/`)
3. **Executes the script automatically** via a LaunchDaemon payload (runs when profile is installed)
4. **Optionally creates a Jamf Pro policy** (if you want policy-based execution instead)

## 🚀 **Usage**

### **Basic Usage - Download Script 199 from Production**

```bash
# Download script 199 from production and create policy + config profile
jpapi software-install script-to-profile --script-id 199 --env production
```

### **With Custom Profile Name**

```bash
# Customize the profile/policy name
jpapi software-install script-to-profile --script-id 199 \
    --profile-name "App Installation Script" \
    --env production
```

### **Save Locally Only (No Deployment)**

```bash
# Download script and save profile locally without deploying
jpapi software-install script-to-profile --script-id 199 \
    --no-deploy \
    --env production
```

### **Auto-Execution Options**

```bash
# Install script file only (no auto-execution)
jpapi software-install script-to-profile --script-id 199 \
    --no-execute \
    --env production

# Execute once (default - runs once when profile is installed)
jpapi software-install script-to-profile --script-id 199 \
    --execution-trigger once \
    --env production

# Execute always (runs on every boot/login)
jpapi software-install script-to-profile --script-id 199 \
    --execution-trigger always \
    --env production
```

### **Download from Sandbox**

```bash
# Download from sandbox environment
jpapi software-install script-to-profile --script-id 199 --env sandbox
```

## 📋 **Command Options**

```
--script-id ID              (Required) Jamf Pro script ID to download
--profile-name NAME         Custom profile name (default: script name)
--description TEXT          Profile description
--no-deploy                 Don't deploy to Jamf Pro, just save locally
--no-execute                Don't auto-execute script, just install the file
--execution-trigger TRIGGER "once" (run once) or "always" (run on boot/login)
--env ENV                   Environment: production or sandbox
```

## 🔧 **What It Does**

### **1. Downloads the Script**
- Connects to Jamf Pro (production or sandbox)
- Downloads script 199 (or any script ID you specify)
- Retrieves script name, content, and metadata

### **2. Creates a Config Profile with Auto-Execution**
- Creates a config profile with **multiple payloads**:
  1. **File Payload** - Installs the script file to `/usr/local/bin/`
  2. **Executor Script** - Makes script executable and runs it
  3. **LaunchDaemon Payload** - Loads the executor to run the script automatically
- Script executes when profile is installed (if `--no-execute` is not used)
- Execution trigger can be "once" (default) or "always" (runs on boot/login)

## 📁 **Output**

### **When Deploying (`--env production`)**

**Config Profile Created** in Jamf Pro:
- Name: "[Script Name] Script Profile"
- **Installs** the script file to `/usr/local/bin/`
- **Executes** the script automatically via LaunchDaemon
- Script runs once when profile is installed (or on every boot/login if `--execution-trigger always`)

### **When Saving Locally (`--no-deploy`)**

**Mobileconfig File** saved to `generated_profiles/`:
- Contains the script file payload
- Contains executor script payload  
- Contains LaunchDaemon payload for auto-execution
- Can be manually installed or deployed later
- Script will execute when profile is installed

## 💡 **Use Cases**

### **1. Backup Script as Config Profile**
```bash
# Download script 199 and save as profile locally
jpapi software-install script-to-profile --script-id 199 \
    --no-deploy \
    --env production
```

### **2. Migrate Script to Different Environment**
```bash
# Download from production, deploy to sandbox
jpapi software-install script-to-profile --script-id 199 \
    --env production
# Then manually deploy to sandbox if needed
```

### **3. Create Policy to Run Script**
```bash
# Creates policy that can be triggered to run the script
jpapi software-install script-to-profile --script-id 199 \
    --profile-name "Run App Installation" \
    --env production
```

## 🔍 **Example: Script 199**

### **Download Script 199 from Production**

```bash
jpapi software-install script-to-profile --script-id 199 --env production
```

**Output:**
```
📥 Downloading script 199 from Jamf Pro...
✅ Successfully downloaded script: App Installation Script
📦 Creating policy to run script: App Installation Script
✅ Successfully created policy: Run App Installation Script
🚀 Deploying profile to Jamf Pro: App Installation Script Script File Profile
✅ Profile deployed successfully: App Installation Script Script File Profile
✅ Successfully downloaded script 199 and deployed as config profile
```

## 📊 **What Gets Created**

### **1. Jamf Pro Policy**
- **Name:** "Run [Script Name]"
- **Type:** Policy
- **Action:** Runs script when triggered
- **Trigger:** EVENT (can be changed in Jamf Pro UI)

### **2. Config Profile**
- **Name:** "[Script Name] Script File Profile"
- **Type:** Configuration Profile
- **Payload:** File payload
- **Action:** Installs script file to `/usr/local/bin/[script-name].sh`

## 🎨 **How It Works Internally**

1. **Script Download**
   ```python
   response = auth.api_request("GET", f"/JSSResource/scripts/id/{script_id}")
   script_data = response['script']
   ```

2. **Policy Creation**
   - Creates XML policy structure
   - Includes script ID in scripts array
   - Deploys via Jamf Pro API

3. **Profile Creation**
   - Encodes script content as base64
   - Creates mobileconfig with file payload
   - Deploys via Jamf Pro API

## ✨ **How Auto-Execution Works**

### **Profile Structure**
The config profile contains three payloads:

1. **Script File Payload**
   - Installs your script to `/usr/local/bin/[script-name].sh`
   - Contains the actual script content from Jamf Pro

2. **Executor Script Payload**
   - Creates an executor wrapper at `/usr/local/bin/[script-name]_executor.sh`
   - Makes the main script executable
   - Executes the main script
   - Handles cleanup for "once" execution

3. **LaunchDaemon Payload**
   - Creates a LaunchDaemon plist at `/Library/LaunchDaemons/`
   - Loads the executor script automatically
   - Runs when profile is installed
   - For "once" mode: Executes script once, then unloads LaunchDaemon
   - For "always" mode: Executes script on every boot/login

## 🔧 **Advanced Usage**

### **Programmatic Usage**

```python
from addons.software_installation import SoftwareInstallationFactory

factory = SoftwareInstallationFactory(auth=your_auth)
service = factory.create_software_installation_service()

# Download script and create profile
success = service.download_script_and_create_profile(
    script_id=199,
    profile_name="My Custom Profile",
    description="Custom description",
    deploy=True
)
```

### **Direct Service Usage**

```python
from addons.software_installation import ScriptProfileService

service = ScriptProfileService(auth=your_auth)

# Download script
script_data = service.download_script(199)

# Create profile
profile = service.create_script_profile(script_data)

# Deploy
service.deploy_script_profile(199, deploy=True)
```

## 📝 **File Locations**

### **Local Files (when using --no-deploy)**
```
generated_profiles/
└── Script_Name_Script_File_Profile_20240101_120000.mobileconfig
```

### **Jamf Pro Objects Created (when deploying)**
- **Policy:** `/policies/` - "Run [Script Name]"
- **Profile:** `/configuration_profiles/` - "[Script Name] Script File Profile"

## 🎯 **Summary**

The `script-to-profile` command provides a convenient way to:

1. ✅ **Download scripts** from Jamf Pro
2. ✅ **Create policies** to run those scripts
3. ✅ **Create config profiles** to install script files
4. ✅ **Work with both** production and sandbox environments

**Perfect for:** Script backup, migration, and creating executable policies!
