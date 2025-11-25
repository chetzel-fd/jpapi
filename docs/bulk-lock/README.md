# Bulk Device Lock Documentation

This directory contains all documentation related to the bulk device lock functionality.

## Documentation Files

- **[BULK_DEVICE_LOCK_GUIDE.md](./BULK_DEVICE_LOCK_GUIDE.md)** - General guide for bulk device locking operations
- **[SHAREPOINT_BULK_LOCK.md](./SHAREPOINT_BULK_LOCK.md)** - SharePoint integration guide with Excel files
- **[EXCEL_OUTPUT_FORMAT.md](./EXCEL_OUTPUT_FORMAT.md)** - Excel output format specification
- **[DEVICE_LOCK_PERMISSIONS.md](./DEVICE_LOCK_PERMISSIONS.md)** - Required JAMF Pro API permissions
- **[SOLID_REFACTORING.md](./SOLID_REFACTORING.md)** - SOLID principles refactoring documentation
- **[SOLID_REFACTORING_SUMMARY.md](./SOLID_REFACTORING_SUMMARY.md)** - SOLID refactoring summary
- **[BULK_LOCK_SUMMARY.md](./BULK_LOCK_SUMMARY.md)** - Implementation summary
- **[test_skip_existing.md](./test_skip_existing.md)** - Testing documentation for skip existing feature

## Quick Start

For basic usage:
```bash
jpapi --env production devices bulk lock /path/to/users.csv --force
```

For SharePoint Excel files:
```bash
jpapi --env production devices bulk lock "SHAREPOINT_URL" --force
```

## Features

- ✅ CSV and Excel file support
- ✅ SharePoint integration
- ✅ Automatic user-to-device matching
- ✅ Smart skip for already-locked devices
- ✅ Random 6-digit PIN generation
- ✅ Excel output with computer names and lock codes
- ✅ Production safety guardrails
- ✅ Dry-run mode for testing

## Related Documentation

- [Main README](../../README.md)
- [Quick Start Guide](../QUICK_START.md)

