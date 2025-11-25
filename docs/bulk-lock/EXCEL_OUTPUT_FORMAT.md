# Excel Output Format

## Overview

When using the bulk lock feature with Excel files, the system preserves your original spreadsheet format and adds:
- **Column D**: Computer Name(s)
- **Column E**: Lock Code (6-digit PIN)

## Input Format

Your Excel file can have any format, but should include a column with usernames or emails:

### Example Input:

| A: Name       | B: Email                 | C: Department | D: (empty) | E: (empty or existing codes) |
|--------------|--------------------------|---------------|------------|------------------------------|
| John Doe     | jdoe@company.com         | IT            |            |                              |
| Alice Smith  | alice.smith@company.com  | HR            |            |                              |
| Bob Wilson   | bob.wilson@company.com   | IT            |            | 478258                       |

## Output Format

After running the bulk lock command:

### Example Output:

| A: Name       | B: Email                 | C: Department | D: Computer Name   | E: Lock Code |
|--------------|--------------------------|---------------|--------------------|--------------|
| John Doe     | jdoe@company.com         | IT            | FDG-Y3RQ9XGHC9     | 923847       |
| Alice Smith  | alice.smith@company.com  | HR            | FDG-A1B2C3D4E5     | 156432       |
| Bob Wilson   | bob.wilson@company.com   | IT            | FDG-F6G7H8I9J0     | 478258       |

## Column Details

### Column D - Computer Name
- Automatically populated with the device name from JAMF Pro
- Shows the actual computer name assigned to that user
- Format: Typically your organization's naming convention (e.g., FDG-SERIALNUMBER)

### Column E - Lock Code
- 6-digit randomly generated PIN
- Unique per device
- **Existing codes are preserved** - if a user already has a code, it won't be changed
- Only new users without codes will get new PINs

## Features

✅ **Original Format Preserved**: All your existing columns (A, B, C, etc.) remain unchanged
✅ **Computer Names Added**: Column D shows which computer belongs to each user
✅ **Lock Codes Added**: Column E shows the unlock PIN for each device
✅ **Skip Existing**: Users with codes in column E are automatically skipped
✅ **Multiple Devices**: If a user has multiple computers, only the first is shown

## File Output

### Output Filename Format:
```
device_lock_results_YYYYMMDD_HHMMSS.xlsx
```

Example: `device_lock_results_20251107_143022.xlsx`

### What's Included:
- All original data from your input file
- Computer names in column D
- Lock codes in column E
- Proper Excel formatting
- Ready to share with IT support team

## Usage Example

### 1. Download from SharePoint:
```bash
jpapi --env production devices lock csv "SHAREPOINT_URL" --dry-run
```

### 2. Review output, then run:
```bash
jpapi --env production devices lock csv "SHAREPOINT_URL"
```

### 3. Get output file:
```
📊 Bulk Lock Summary:
   ✅ Successful: 10
   ❌ Failed: 0
   📄 Results exported to: device_lock_results_20251107_143022.xlsx
   📊 Format: Excel
   📝 Computer names and lock codes added to spreadsheet
   ✅ Computer names written to column D
   ✅ Lock codes written to column E
```

### 4. Share the file:
The output Excel file now contains:
- Original user information (columns A, B, C)
- Computer names (column D)
- Lock codes (column E)

Perfect for:
- Sharing with IT support
- User communication
- Audit records
- Password distribution

## Important Notes

⚠️ **Security**: The output file contains plaintext passcodes - store securely!

✅ **Re-runnable**: Run the command again with the output file as input to:
- Add newly added users
- Skip users who already have codes in column E
- Process any previously failed devices

✅ **Audit Trail**: Keep the output file for:
- Password recovery requests
- Compliance documentation
- Incident response

## Multiple Devices per User

If a user has multiple computers:
- The first device found is locked
- Computer name shown is for the first device
- To lock additional devices, you may need to:
  - Run separate commands per device
  - Or manually specify device IDs

## Troubleshooting

### "Column not found" errors
- Ensure your Excel file has a column with "username" or "email" in the header
- Column names are case-insensitive

### Missing computer names
- User may not be assigned to any computers in JAMF Pro
- Check spelling of username/email
- Verify user has active devices

### Lock codes not written
- Check that pandas and openpyxl are installed
- Verify the file isn't open in Excel while running
- Check file permissions

## Example Workflow

```bash
# 1. Test first
jpapi --env production devices lock csv "sharepoint_url" --dry-run --force

# 2. Execute
jpapi --env production devices lock csv "sharepoint_url" --force

# 3. Secure the file
chmod 600 device_lock_results_*.xlsx

# 4. Share with IT support team
# File now contains:
#   - User names and emails (your original data)
#   - Computer names (column D)
#   - Lock codes (column E)
```

## Related Documentation

- `BULK_DEVICE_LOCK_GUIDE.md` - General bulk lock guide
- `SHAREPOINT_BULK_LOCK.md` - SharePoint integration
- `test_skip_existing.md` - Skip feature documentation

