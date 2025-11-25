# Device Lock API Permissions

## Required JAMF Pro API Permissions

To use the device lock functionality (`jpapi devices mac lock` / `jpapi devices ios lock`), your JAMF Pro API user needs the following permissions:

### For Computers (macOS Devices)

1. **Read Computers** - Required to lookup and verify the device exists
   - Privilege: `Read`
   - Object: `Computers`
   - API Endpoint: `/JSSResource/computers/id/{id}`

2. **Send Computer Remote Commands** - Required to send the lock command
   - Privilege: `Create` 
   - Object: `Computer Remote Commands`
   - API Endpoint: `/JSSResource/computercommands/command/DeviceLock/passcode/{passcode}/id/{id}`

### For Mobile Devices (iOS/iPadOS)

1. **Read Mobile Devices** - Required to lookup and verify the device exists
   - Privilege: `Read`
   - Object: `Mobile Devices`
   - API Endpoint: `/JSSResource/mobiledevices/id/{id}`

2. **Send Mobile Device Remote Commands** - Required to send the lock command
   - Privilege: `Create`
   - Object: `Mobile Device Remote Commands`
   - API Endpoint: `/JSSResource/mobiledevicecommands/command/DeviceLock/passcode/{passcode}/id/{id}`

## Setting Up API Permissions in JAMF Pro

1. **Navigate to Settings > System > API Roles and Clients** (JAMF Pro 10.49+)
   - Or: **Settings > Global Management > API Integrations** (older versions)

2. **Create a new API Role** (if needed):
   - Name: `Device Lock Role` (or similar)
   - Add the following privileges:
     - **Computers**: Read
     - **Computer Remote Commands**: Create
     - **Mobile Devices**: Read
     - **Mobile Device Remote Commands**: Create

3. **Create or update API Client**:
   - Assign the role created above
   - Note the Client ID and Client Secret

## Setting Up Authentication in jpapi

Once you have your API credentials:

```bash
# Set environment variables
export JAMF_URL="https://your-instance.jamfcloud.com"
export JAMF_CLIENT_ID="your-client-id"
export JAMF_CLIENT_SECRET="your-client-secret"

# Or configure via jpapi (if auth setup is available)
jpapi setup --env prod
```

## Usage Examples

### Dry-run mode (recommended first):
```bash
jpapi devices mac lock 8112 478258 --dry-run
```

### Actual lock command:
```bash
jpapi devices mac lock 8112 478258
```

### Lock with force flag (skip production confirmations):
```bash
jpapi devices mac lock 8112 478258 --force
```

### Mobile device lock:
```bash
jpapi devices ios lock 1234 123456
```

## Troubleshooting

### "Computer not found" Error
- Verify the computer ID exists in JAMF Pro
- Check that your API user has Read access to Computers
- Try querying the device first: `jpapi list computers --filter "8112"`

### "Authentication not configured" Error
- Set up authentication as shown above
- Verify your credentials are correct
- Check that the JAMF_URL includes the full URL with protocol (https://)

### "Permission Denied" Error
- Verify your API role includes "Send Computer Remote Commands"
- Check that the API client is assigned the correct role
- Ensure the role has "Create" privilege for Computer Remote Commands

## Security Notes

1. **Passcode Security**: The passcode is masked in all output but is sent to JAMF Pro in plain text via the API
2. **Production Safety**: In production environments, jpapi will:
   - Require explicit confirmation before locking
   - Show a detailed summary of what will be locked
   - Support `--dry-run` mode to preview without executing
3. **Scope**: The lock command only affects the specific device ID provided - no bulk operations

## API Documentation References

- JAMF Pro API Documentation: https://developer.jamf.com/jamf-pro/reference
- Computer Commands: https://developer.jamf.com/jamf-pro/reference/post_computercommands-command-command-id-id
- Mobile Device Commands: https://developer.jamf.com/jamf-pro/reference/post_mobiledevicecommands-command-command-id-id

