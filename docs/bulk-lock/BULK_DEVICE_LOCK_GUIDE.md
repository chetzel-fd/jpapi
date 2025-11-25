# Bulk Device Lock Guide

## Overview

The bulk device lock feature allows you to lock multiple devices at once by providing a CSV file with usernames or email addresses. Each device will be locked with a randomly generated 6-digit PIN, and all results (including passcodes) will be exported to a CSV file for your records.

## CSV Format

Your CSV file should have one of these column headers:
- `username` - Just the username (e.g., `jdoe`)
- `email` - Full email address (e.g., `jdoe@company.com`)

You can have both columns, and the system will use whichever is available.

### Sample CSV (`sample_bulk_lock.csv`):

```csv
username,email
jdoe,jdoe@company.com
asmith,alice.smith@company.com
bwilson,bob.wilson@company.com
```

## Usage Examples

### Dry-run mode (recommended first):
```bash
jpapi --env production devices bulk lock sample_bulk_lock.csv --dry-run
```

### Actual bulk lock:
```bash
jpapi --env production devices bulk lock sample_bulk_lock.csv
```

### With force flag (skip confirmations):
```bash
jpapi --env production devices bulk lock sample_bulk_lock.csv --force
```

## How It Works

1. **Read CSV**: Reads usernames/emails from the provided CSV file
2. **Find Devices**: Searches all computers in JAMF Pro for devices assigned to those users
3. **Generate PINs**: Creates a unique random 6-digit PIN for each device
4. **Production Safety**: Shows detailed summary and requires confirmation (unless `--force` is used)
5. **Lock Devices**: Sends lock commands to each device via JAMF Pro API
6. **Export Results**: Saves all device info and passcodes to a timestamped CSV file

## Output

The command generates a CSV file named `device_lock_results_YYYYMMDD_HHMMSS.csv` with:

- **Username**: The user from your input CSV
- **Device ID**: JAMF Pro device ID
- **Device Name**: Computer name
- **Serial Number**: Device serial number
- **Passcode**: The 6-digit PIN assigned to this device
- **Status**: Success or failure reason
- **Timestamp**: When the lock command was sent

### Example Output CSV:

```csv
Username,Device ID,Device Name,Serial Number,Passcode,Status,Timestamp
jdoe@company.com,8112,FDG-Y3RQ9XGHC9,Y3RQ9XGHC9,478258,Success,2025-11-07 11:34:06
asmith@company.com,8113,FDG-A1B2C3D4E5,A1B2C3D4E5,923847,Success,2025-11-07 11:34:12
bwilson@company.com,8114,FDG-F6G7H8I9J0,F6G7H8I9J0,156432,Success,2025-11-07 11:34:18
```

## Production Safety Features

✅ **Pre-flight checks**:
- Validates CSV file exists and is readable
- Shows how many users/devices will be affected
- Lists users without devices found
- Shows preview of devices to be locked

✅ **Production environment protection**:
- Detailed summary of what will be locked
- Risk level assessment
- Explicit confirmation required
- Support for `--dry-run` to test without executing
- Support for `--force` to skip confirmations

✅ **Bulk operation safeguards**:
- Shows total device count before proceeding
- Lists all devices that will be affected
- Requires explicit "yes" confirmation
- Exports complete audit trail with timestamps

## Device Matching Logic

The system matches devices to users by:
1. Comparing the username from CSV to the computer's assigned username in JAMF
2. Comparing the email from CSV to the computer's email address in JAMF
3. Handles partial matching (e.g., username `jdoe` will match `jdoe@company.com`)
4. Case-insensitive matching

## Error Handling

- **User not found**: Users without devices are reported but don't stop the process
- **API errors**: Individual device failures are recorded in the output CSV with error messages
- **Network issues**: Retries are attempted automatically by the API layer
- **Permission errors**: Clear error messages indicate missing API permissions

## Security Notes

1. **Passcode Security**:
   - Random 6-digit PINs are generated for each device
   - Passcodes are saved to the output CSV - **KEEP THIS FILE SECURE**
   - Different passcode for each device (no reuse)

2. **Audit Trail**:
   - Complete CSV export with all actions taken
   - Timestamps for each lock command
   - Success/failure status for accountability

3. **Production Safety**:
   - Requires explicit confirmation in production
   - Shows detailed summary before execution
   - Dry-run mode available for testing

## Required JAMF Pro API Permissions

Same as single device lock:
- **Read** privilege on **Computers**
- **Create** privilege on **Computer Remote Commands**

## Troubleshooting

### "No devices found for any users"
- Verify usernames/emails in CSV match JAMF Pro records
- Check that users are assigned to computers in JAMF
- Try exporting a computer list to see actual usernames
- Use case-insensitive matching (system handles this automatically)

### "Permission Denied" errors
- Verify API role includes "Send Computer Remote Commands"
- Check API client has "Create" privilege for Computer Remote Commands
- Ensure you're using correct environment (prod vs sandbox)

### CSV parsing errors
- Ensure CSV has `username` or `email` column header
- Check for proper CSV formatting (no extra commas, proper quotes)
- Verify file encoding is UTF-8

## Best Practices

1. **Always test first**:
   ```bash
   jpapi --env production devices bulk lock users.csv --dry-run
   ```

2. **Start small**:
   - Test with a CSV containing 1-2 users first
   - Verify the process works as expected
   - Then scale up to larger batches

3. **Keep records**:
   - Save the output CSV in a secure location
   - Document when and why devices were locked
   - Keep track of passcodes for support requests

4. **Communicate**:
   - Notify affected users before locking
   - Have support ready to provide passcodes
   - Document the process for your team

5. **Verify results**:
   - Check the output CSV for any failures
   - Retry failed devices if needed
   - Verify devices are actually locked in JAMF Pro

## Example Workflow

```bash
# 1. Create CSV with users
cat > users_to_lock.csv << EOF
username,email
jdoe,jdoe@company.com
asmith,asmith@company.com
EOF

# 2. Test with dry-run
jpapi --env production devices bulk lock users_to_lock.csv --dry-run

# 3. Review the dry-run output, then execute
jpapi --env production devices bulk lock users_to_lock.csv

# 4. Secure the output CSV
mv device_lock_results_*.csv ~/secure_location/
chmod 600 ~/secure_location/device_lock_results_*.csv

# 5. Distribute passcodes to IT support for user assistance
```

## Related Commands

- Single device lock: `jpapi devices mac lock <device_id> <passcode>`
- List computers: `jpapi list computers`
- Export computers: `jpapi export computers --format csv`

## Support

For issues or questions:
1. Check `DEVICE_LOCK_PERMISSIONS.md` for API permission requirements
2. Verify your API credentials are configured correctly
3. Review the output CSV for specific error messages
4. Check JAMF Pro logs for command delivery status

