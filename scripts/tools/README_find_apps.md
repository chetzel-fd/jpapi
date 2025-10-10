# General-Purpose Application Finder Tool

A comprehensive Python script for finding and analyzing any application on macOS systems with flexible search patterns and detailed analysis capabilities.

## Features

- **🔍 Flexible Search**: Find applications by name, pattern, or bundle ID
- **📊 Multiple Output Formats**: Text, JSON, and CSV output options
- **🔧 Advanced Filtering**: Filter by type, size, version, running status, and more
- **📱 Comprehensive Analysis**: Extract version, bundle info, architecture, and more
- **🏃‍♂️ Process Detection**: Check if applications are currently running
- **📁 Multiple Search Paths**: Search in Applications, System directories, and custom paths

## Installation

The script is a standalone Python 3 script with no external dependencies beyond the standard library.

```bash
# Make the script executable
chmod +x scripts/tools/find_apps.py
```

## Usage Examples

### Basic Usage

```bash
# Find all applications
python3 scripts/tools/find_apps.py

# Find applications matching a pattern
python3 scripts/tools/find_apps.py -p "Chrome"

# Find all .app bundles
python3 scripts/tools/find_apps.py -p "*.app"

# Find applications in specific directories
python3 scripts/tools/find_apps.py -s /Applications /System/Applications
```

### Advanced Filtering

```bash
# Find only running applications
python3 scripts/tools/find_apps.py --running-only

# Find applications by bundle ID
python3 scripts/tools/find_apps.py --bundle-id "com.apple"

# Find large applications (> 100MB)
python3 scripts/tools/find_apps.py --min-size 104857600

# Find specific application type
python3 scripts/tools/find_apps.py --type "app_bundle"
```

### Output Formats

```bash
# JSON output
python3 scripts/tools/find_apps.py -p "Safari" -f json

# CSV output
python3 scripts/tools/find_apps.py -p "*.app" -f csv -o apps.csv

# Save to file
python3 scripts/tools/find_apps.py -p "Remote" -o remote_apps.txt
```

### Verbose Output

```bash
# Enable debug information
python3 scripts/tools/find_apps.py -p "Chrome" -v
```

## Command Line Options

### Search Options
- `-p, --pattern`: Search pattern (default: *)
- `-s, --search-paths`: Additional search paths
- `-v, --verbose`: Enable verbose output with debug information

### Output Options
- `-f, --format`: Output format (text, json, csv)
- `-o, --output`: Output file path
- `--no-details`: Exclude detailed information

### Filter Options
- `--name`: Filter by application name
- `--bundle-id`: Filter by bundle identifier
- `--version`: Filter by version
- `--type`: Filter by application type
- `--running-only`: Show only running applications
- `--min-size`: Minimum size in bytes
- `--max-size`: Maximum size in bytes

## Output Formats

### Text Format
Human-readable report with sections for different application types:
```
================================================================================
APPLICATION FINDER REPORT
================================================================================
Generated: 2025-10-08 11:46:00
Applications Found: 1

APP BUNDLE APPLICATIONS (1)
------------------------------------------------------------
Name: Safari.app
Path: /Applications/Safari.app
Version: 17.0
Bundle ID: com.apple.Safari
Executable: /Applications/Safari.app/Contents/MacOS/Safari
Size: 45,234,567 bytes
Architecture: universal
Status: Running

SUMMARY
----------------------------------------
Total Applications: 1
Running Applications: 1
Total Size: 45,234,567 bytes (43.1 MB)
```

### JSON Format
Machine-readable JSON with structured data:
```json
[
  {
    "name": "Safari.app",
    "path": "/Applications/Safari.app",
    "type": "app_bundle",
    "version": "17.0",
    "bundle_id": "com.apple.Safari",
    "executable": "/Applications/Safari.app/Contents/MacOS/Safari",
    "size": 45234567,
    "is_running": true,
    "architecture": "universal"
  }
]
```

### CSV Format
Comma-separated values for spreadsheet import:
```csv
name,path,type,version,bundle_id,size,is_running,architecture
Safari.app,/Applications/Safari.app,app_bundle,17.0,com.apple.Safari,45234567,true,universal
```

## What It Detects

### Application Types
- **App Bundles** (`.app`): Standard macOS applications
- **App Extensions** (`.appex`): System extensions and plugins
- **Executables**: Command-line tools and scripts
- **Directories**: Application directories and frameworks

### Information Extracted
- **Basic Info**: Name, path, type, size, permissions
- **Bundle Info**: Version, bundle ID, display name, description
- **Technical Details**: Architecture, minimum OS version, category
- **Runtime Status**: Whether the application is currently running
- **File Details**: Creation/modification dates, executable paths

### Search Locations
- `/Applications` - User applications
- `/Applications/Utilities` - Utility applications
- `/System/Applications` - System applications
- `/System/Applications/Utilities` - System utilities
- `/System/Library/CoreServices` - Core system services
- `/usr/local/bin` - Local executables
- `/opt` - Optional software
- Custom paths specified with `-s`

## Use Cases

### IT Administration
```bash
# Find all remote access applications
python3 scripts/tools/find_apps.py -p "Remote" -p "Support" -p "TeamViewer"

# Find applications by vendor
python3 scripts/tools/find_apps.py --bundle-id "com.microsoft"

# Find large applications for cleanup
python3 scripts/tools/find_apps.py --min-size 1000000000 -f csv -o large_apps.csv
```

### Security Auditing
```bash
# Find all running applications
python3 scripts/tools/find_apps.py --running-only -f json

# Find applications with specific permissions
python3 scripts/tools/find_apps.py -p "*.app" --type "app_bundle"
```

### Asset Management
```bash
# Export all applications to CSV
python3 scripts/tools/find_apps.py -f csv -o all_apps.csv

# Find applications by version
python3 scripts/tools/find_apps.py --version "17.0"
```

### Development
```bash
# Find development tools
python3 scripts/tools/find_apps.py -p "Xcode" -p "Visual Studio" -p "IntelliJ"

# Find command-line tools
python3 scripts/tools/find_apps.py --type "executable"
```

## Advanced Examples

### Find and Export Running Applications
```bash
python3 scripts/tools/find_apps.py --running-only -f json -o running_apps.json
```

### Find Large Applications for Cleanup
```bash
python3 scripts/tools/find_apps.py --min-size 500000000 --type "app_bundle" -f csv -o large_apps.csv
```

### Find Applications by Multiple Criteria
```bash
python3 scripts/tools/find_apps.py --bundle-id "com.apple" --running-only --min-size 1000000
```

### Search in Custom Directories
```bash
python3 scripts/tools/find_apps.py -s /Users/username/Applications /opt/homebrew/Cellar
```

## Requirements

- macOS system
- Python 3.6 or higher
- No external dependencies

## Performance Notes

- Large searches may take time due to file system scanning
- Use specific patterns to improve performance
- Verbose mode provides detailed progress information
- Consider using filters to narrow results

## Troubleshooting

### No Results Found
1. Check if the search pattern is correct
2. Verify the search paths exist
3. Use verbose mode (`-v`) to see search progress
4. Try broader patterns (e.g., `*` instead of specific names)

### Permission Issues
1. Some system directories may require elevated privileges
2. Use `sudo` if needed for system directory access
3. Check file permissions on target directories

### Performance Issues
1. Use more specific search patterns
2. Limit search paths to necessary directories
3. Use filters to reduce result set
4. Consider running during off-peak hours for large scans

## Security Considerations

- The script only reads information and does not modify files
- No sensitive information is transmitted or logged
- All operations are read-only
- Consider running in secure environments for sensitive systems
- Be cautious with verbose output in shared environments
