# Payload Type Issue - com.apple.system.extension.file

## 🐛 **Problem**

Profiles created with `com.apple.system.extension.file` payloads only show the General tab in Jamf Pro UI, even though the payloads are stored in the API.

## 🔍 **Root Cause**

`com.apple.system.extension.file` is **NOT a standard macOS configuration profile payload type** supported by Jamf Pro's UI/API.

### Standard Payload Types (That Work):
- `com.apple.TCC.configuration-profile-policy` (PPPC)
- `com.apple.webcontent-filter`
- `com.apple.system-extension-policy`
- `com.apple.ManagedClient.preferences` (Custom Settings)

### Non-Standard (Not Supported):
- `com.apple.system.extension.file` ❌

## ✅ **Solution Options**

### Option 1: Use Packages via Policies (RECOMMENDED)
Install scripts via Jamf Pro policies (as we already support with `--policy-event`). This is the standard, supported approach.

### Option 2: Use Custom Settings Payload
Embed script content in a Custom Settings payload (`com.apple.ManagedClient.preferences`), though this won't install files directly.

### Option 3: Accept Limitation
Acknowledge that file installation via config profiles requires:
- Manual upload via Jamf Pro UI (not API)
- Or use policies/scripts instead

## 📋 **Current Status**

- ✅ Profile creation works
- ✅ Payloads are stored in API (3 payloads present)
- ❌ Jamf Pro UI doesn't recognize/display `com.apple.system.extension.file`
- ❌ Files won't install from these profiles

## 🎯 **Recommendation**

Use the **policy trigger approach** (`--policy-event`) instead of embedding file payloads directly in config profiles. This is:
- ✅ Supported by Jamf Pro
- ✅ More scalable
- ✅ More maintainable
- ✅ Actually works

The config profile should trigger a policy, and the policy should install the script via package or script execution.




