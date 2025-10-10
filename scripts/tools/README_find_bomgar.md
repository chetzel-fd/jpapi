# Bomgar/BeyondTrust Remote Support Finder Tool

A comprehensive Python script for finding and analyzing Bomgar BeyondTrust Remote Support installations on macOS systems.

## Features

- **Application Detection**: Finds Bomgar/BeyondTrust applications in common installation locations
- **System File Analysis**: Locates configuration files, launch daemons, and system components
- **Process Monitoring**: Identifies running Bomgar/BeyondTrust processes and services
- **Launch Service Detection**: Checks for registered launch services
- **Multiple Output Formats**: Supports both human-readable text and machine-readable JSON output
- **Detailed Reporting**: Provides comprehensive information about installation status

## Installation

The script is a standalone Python 3 script with no external dependencies beyond the standard library.

```bash
# Make the script executable
chmod +x scripts/tools/find_bomgar.py
```

## Usage

### Basic Usage

```bash
# Basic scan with text output
python3 scripts/tools/find_bomgar.py

# Verbose output with debug information
python3 scripts/tools/find_bomgar.py -v

# JSON output to file
python3 scripts/tools/find_bomgar.py -f json -o report.json

# Text output to file
python3 scripts/tools/find_bomgar.py -f text -o report.txt
```

### Command Line Options

- `-v, --verbose`: Enable verbose output with debug information
- `-f, --format {text,json}`: Output format (default: text)
- `-o, --output`: Output file path (default: stdout)
- `-h, --help`: Show help message

## Output Formats

### Text Format
Human-readable report with sections for:
- Applications found
- System files
- Running processes
- Launch services
- Summary statistics

### JSON Format
Machine-readable JSON with structured data:
```json
{
  "installations": [...],
  "system_files": [...],
  "running_processes": [...],
  "launch_services": [...],
  "summary": {
    "total_installations": 1,
    "total_system_files": 3,
    "total_processes": 6,
    "total_services": 0
  }
}
```

## What It Detects

### Applications
- Bomgar/BeyondTrust application bundles in `/Applications`
- Hidden application directories (e.g., `.com.bomgar.scc.*`)
- Remote Support Client applications

### System Files
- Configuration files in `/Library/BeyondTrust`
- Launch daemon plists in `/Library/LaunchDaemons`
- Launch agent plists in `/Library/LaunchAgents`
- Helper scripts and executables

### Running Processes
- `sdcust` processes (Bomgar client)
- Service helper processes
- Elevated privilege processes
- Launch daemon processes

### Launch Services
- Registered launch daemons
- Launch agents
- Service management

## Example Output

```
============================================================
BOMGAR/BEYONDTRUST REMOTE SUPPORT FINDER REPORT
============================================================

APPLICATIONS FOUND: 1
----------------------------------------
Path: /Applications/.com.bomgar.scc.68CC106A/Remote Support Customer Client.app
Name: Remote Support Customer Client.app
Type: app_bundle
Version: 23.1.0
Bundle ID: com.bomgar.scc.68CC106A
Executable: /Applications/.com.bomgar.scc.68CC106A/Remote Support Customer Client.app/Contents/MacOS/sdcust
Size: 15,234,567 bytes

SYSTEM FILES FOUND: 3
----------------------------------------
Path: /Library/LaunchDaemons/com.bomgar.bomgar-ps-68CC106E-1759865476.plist
Size: 1,045 bytes

RUNNING PROCESSES: 4
----------------------------------------
PID: 38632 | User: root | CPU: 0.1% | Mem: 0.1%
Command: /Applications/.com.bomgar.scc.68CC106A/Remote Support Customer Client.app/Contents/MacOS/sdcust -pinned drone

SUMMARY
----------------------------------------
Total Applications: 1
Total System Files: 3
Running Processes: 4
Launch Services: 1

Bomgar/BeyondTrust Remote Support is installed on this system.
```

## Use Cases

- **IT Administration**: Quickly identify Bomgar installations across managed systems
- **Security Auditing**: Verify remote access software presence and status
- **Compliance**: Document remote support tool installations
- **Troubleshooting**: Diagnose Bomgar client issues
- **Asset Management**: Track remote support software deployments

## Requirements

- macOS system
- Python 3.6 or higher
- No external dependencies

## Notes

- The script requires appropriate permissions to access system directories
- Some system files may require root privileges to read
- The script is designed specifically for macOS systems
- Verbose mode provides detailed debugging information for troubleshooting

## Troubleshooting

If the script doesn't find expected installations:

1. Run with verbose mode (`-v`) to see detailed search information
2. Check file permissions - some directories may require elevated privileges
3. Verify the installation is actually present in expected locations
4. Check if the installation uses non-standard naming conventions

## Security Considerations

- The script only reads information and does not modify system files
- No sensitive information is logged or transmitted
- All operations are read-only
- Consider running in a secure environment for sensitive systems
