# Creating Extension Attributes with jpapi

## Overview

The `jpapi create extension-attribute` command now supports creating script-based extension attributes directly from the command line.

## Basic Usage

```bash
jpapi create extension-attribute <type> "<name>" [options]
```

### Parameters

- `<type>`: Extension attribute type
  - `computer` - Computer extension attributes
  - `mobile` - Mobile device extension attributes  
  - `user` - User extension attributes

- `<name>`: Name of the extension attribute (use quotes if it contains spaces)

### Options

- `--description "text"` - Description of what the EA does
- `--data-type TYPE` - Data type for the attribute
  - `String` (default)
  - `Integer`
  - `Date`
  - `Boolean`
- `--input-type TYPE` - Input method
  - `Text Field` (default)
  - `Script` (auto-set when using --script-file)
  - `Pop-up Menu`
  - `LDAP Mapping`
- `--script-file PATH` - Path to script file (automatically sets input-type to Script)
- `--inventory-display "section"` - Inventory display section (default: "Extension Attributes")
- `--env ENV` - Target environment (sandbox, staging, production, etc.)
- `--enabled` - Enable the attribute immediately (default: true)

## Examples

### Example 1: Simple Text Field EA

```bash
jpapi create extension-attribute computer "Department Code" \
  --description "Department identifier code" \
  --data-type String \
  --env sandbox
```

### Example 2: Script-Based EA

```bash
jpapi create extension-attribute computer "CrowdStrike Status" \
  --description "Checks CrowdStrike Falcon installation and health" \
  --script-file ~/scripts/check_crowdstrike.zsh \
  --env sandbox
```

### Example 3: Integer Data Type

```bash
jpapi create extension-attribute computer "Days Since Last Backup" \
  --description "Number of days since last Time Machine backup" \
  --data-type Integer \
  --script-file ~/scripts/check_backup_age.sh \
  --env production
```

## Script Requirements

When using `--script-file`:

1. **Script Output**: Must output XML in the format:
   ```xml
   <result>Your value here</result>
   ```

2. **Platform**: Automatically set to "Mac" for computer EAs

3. **Permissions**: Script runs with user permissions unless specifically elevated within the script

4. **Exit Codes**: Exit 0 for success

## Example Script Template

```bash
#!/bin/zsh

# Your logic here
VALUE="Some result"

# Output in required format
echo "<result>${VALUE}</result>"
exit 0
```

## Real-World Example: CrowdStrike Falcon EAs

The two-EA CrowdStrike monitoring solution was created using this feature:

```bash
# Create Health EA
jpapi create extension-attribute computer "Crowdstrike Falcon - Health" \
  --description "Comprehensive health status including version, running state, and registration" \
  --script-file extension_attributes_consolidated/ea_falcon_health.zsh \
  --env sandbox

# Create Protection EA
jpapi create extension-attribute computer "Crowdstrike Falcon - Protection" \
  --description "Protection status including Full Disk Access, System Extension, and configuration" \
  --script-file extension_attributes_consolidated/ea_falcon_protection.zsh \
  --env sandbox
```

### Output Format

**Health EA**: `v7.29 | Running | Active`
- Version | Agent Status | Registration State

**Protection EA**: `FDA:Granted | SysExt:Loaded | Protection:Full`
- Full Disk Access | System Extension | Protection Level

## Tips

1. **Test Locally First**: Run your script locally to verify it works before creating the EA
2. **Start in Sandbox**: Always create in sandbox/dev first, then promote to production
3. **Clear Output**: Use pipe-delimited format for multi-value results (easier to read in Jamf)
4. **Label Fields**: Prefix values with labels for clarity (e.g., `FDA:Granted` instead of just `Granted`)

## Verification

After creating an EA, verify it exists:

```bash
jpapi extension-attributes computer --env sandbox | grep "YourEAName"
```

## Technical Details

- Uses Jamf Classic API (JSSResource)
- Sends XML-formatted payloads
- Requires valid authentication token
- Created EAs are enabled by default
- Scripts are embedded directly in the EA definition

## Error Handling

Common errors and solutions:

1. **"Platform is required"**: Script-based EAs need platform specification (automatically handled)
2. **"Unsupported Media Type"**: API requires XML format (automatically handled)
3. **"Problem with inventory_display"**: Use standard sections like "Extension Attributes" or "General"
4. **"Script file not found"**: Check path and use `~/` for home directory

## Related Commands

- `jpapi extension-attributes computer` - List all computer EAs
- `jpapi extension-attributes mobile` - List mobile device EAs
- `jpapi extension-attributes user` - List user EAs
- `jpapi update extension-attribute` - Update existing EA (future feature)

---

**Created**: 2025-10-14
**Feature Version**: jpapi v1.1.0+







