# SharePoint Bulk Device Lock

## Overview

The bulk device lock feature now supports direct SharePoint Excel links! Simply provide a SharePoint sharing URL, and jpapi will:
1. Download the Excel file
2. Read usernames/emails from it
3. Lock devices
4. Write the generated passcodes back to column E
5. Save the updated Excel file locally

## Usage with SharePoint URL

```bash
jpapi --env production devices lock csv "https://sharepoint.com/.../file.xlsx?e=xxxxx"
```

### Your SharePoint Link Example:

```bash
jpapi --env production devices lock csv "https://yourcompany-my.sharepoint.com/:x:/g/personal/user_company_com/EXAMPLE_ID?e=XXXXX"
```

## Column E Passcode Writing

The system automatically:
- Finds the username/email column in your Excel file
- **Skips users who already have a code in column E** (already locked)
- Locks devices for remaining users
- Writes the 6-digit PIN to **column E** for each newly locked user
- Saves a new Excel file with the passcodes included

### Smart Skip Feature ✨

If you run the command multiple times, it will:
- Check column E for existing lock codes
- Skip users who already have a code (device already locked)
- Only process users without a lock code
- Preserve existing lock codes in the output file

This allows you to:
- Re-run the command safely without re-locking devices
- Process users in batches
- Add new users to the Excel file and re-run

### Excel File Format

Your Excel file should have a column with usernames or emails:
- Columns A, B, C: Your existing data
- **Column D**: Computer names will be written here
- **Column E**: Lock codes will be written here

Example Input:
```
| A: Name    | B: Email               | C: Department | D:          | E:        |
|-----------|------------------------|---------------|-------------|-----------|
| John Doe  | jdoe@company.com       | IT            |             |           |
| Alice S.  | asmith@company.com     | HR            |             |           |
```

Example Output:
```
| A: Name    | B: Email               | C: Department | D: Computer Name   | E: Lock Code |
|-----------|------------------------|---------------|--------------------|--------------|
| John Doe  | jdoe@company.com       | IT            | FDG-Y3RQ9XGHC9     | 478258       |
| Alice S.  | asmith@company.com     | HR            | FDG-A1B2C3D4E5     | 923847       |
```

## Features

✅ **Direct SharePoint Download**: No need to manually download files  
✅ **Automatic Column Detection**: Finds username/email columns automatically  
✅ **Column E Writing**: Passcodes automatically written to column E  
✅ **Excel Output**: Results saved as Excel file with formatting preserved  
✅ **Production Safety**: Full safety guardrails including dry-run mode  

## Commands

### Dry-run (test without locking):
```bash
jpapi --env production devices lock csv "SHAREPOINT_URL" --dry-run
```

### Actual lock operation:
```bash
jpapi --env production devices lock csv "SHAREPOINT_URL"
```

### With force flag (skip confirmations):
```bash
jpapi --env production devices lock csv "SHAREPOINT_URL" --force
```

## What Happens

1. **Download**: File downloaded from SharePoint to temporary location
2. **Read**: System reads usernames/emails from the Excel file
3. **Match**: Finds devices in JAMF Pro for each user
4. **Confirm**: Shows summary and asks for confirmation (unless --force)
5. **Lock**: Sends lock commands to each device
6. **Write**: Updates column E with the generated passcodes
7. **Save**: Saves new Excel file: `device_lock_results_TIMESTAMP.xlsx`

## Output File

The output Excel file includes:
- **Original columns**: All your original data preserved
- **Column E**: Lock codes for each device
- **Filename**: `device_lock_results_20251107_123456.xlsx`

## Requirements

```bash
# Install required packages
pip install pandas openpyxl
```

These are already included in jpapi's requirements.

## SharePoint Permissions

Ensure:
- The SharePoint link is accessible (not expired)
- You have permission to access the file
- The file is a valid Excel format (.xlsx)

## Troubleshooting

### "Error downloading from SharePoint"
- Verify the SharePoint URL is correct and accessible
- Check that the link hasn't expired
- Ensure you have network access to SharePoint
- Try downloading the file manually first to test access

### "Error reading Excel file"
- Ensure the file is a valid Excel format (.xlsx)
- Check that pandas and openpyxl are installed
- Verify the file has a username or email column

### "No usernames/emails found"
- Ensure the Excel file has a column with "username" or "email" in the header
- Check that the column has actual data (not empty)

## Security Notes

1. **SharePoint Access**: The file is downloaded temporarily and can be deleted after use
2. **Passcodes**: All passcodes are written to the output Excel file - **keep it secure**
3. **Audit Trail**: Full audit trail with timestamps in the output file

## Example Workflow

```bash
# 1. Get SharePoint link from your colleague
# 2. Test with dry-run first
jpapi --env production devices lock csv "SHAREPOINT_URL" --dry-run

# 3. Review the output, then execute
jpapi --env production devices lock csv "SHAREPOINT_URL"

# 4. Secure the output Excel file
mv device_lock_results_*.xlsx ~/secure_location/
chmod 600 ~/secure_location/device_lock_results_*.xlsx

# 5. Share the Excel file (with passcodes in column E) with IT support
```

## Related Documentation

- `BULK_DEVICE_LOCK_GUIDE.md` - General bulk lock documentation
- `DEVICE_LOCK_PERMISSIONS.md` - Required API permissions
- `sample_bulk_lock.csv` - Sample CSV format (for non-Excel files)

