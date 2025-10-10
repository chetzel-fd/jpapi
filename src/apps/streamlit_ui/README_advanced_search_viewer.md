# Advanced Search Viewer

A comprehensive Streamlit application for visually reviewing and managing JAMF Pro advanced searches with bulk deletion capabilities.

## Features

### 🔍 Visual Review
- **Interactive Cards**: Each advanced search is displayed in an attractive card format
- **Detailed Information**: View search criteria, display fields, and matching devices/computers
- **Real-time Filtering**: Filter by search type, name, site, and smart search status
- **Statistics Overview**: Quick stats on total searches, types, and marked items

### 🗑️ Deletion Management
- **Mark for Deletion**: Click to mark individual searches for deletion
- **Bulk Operations**: Mark multiple searches at once
- **Export Deletion List**: Download CSV file with marked searches
- **Visual Indicators**: Marked searches are highlighted with red border

### 📊 Search Types Supported
- **Computer Searches**: Advanced computer searches
- **Mobile Searches**: iOS/iPadOS device searches  
- **User Searches**: User account searches
- **All Types**: View all search types together

## Quick Start

### Option 1: Python Launcher
```bash
python3 scripts/launchers/launch_advanced_search_viewer.py
```

### Option 2: Shell Script
```bash
./scripts/launchers/launch_advanced_search_viewer.sh
```

### Option 3: Direct Streamlit
```bash
cd /path/to/jpapi
streamlit run apps/streamlit/advanced_search_viewer.py --server.port 8502
```

## Usage Guide

### 1. Viewing Searches
- The app loads all advanced searches from your JAMF Pro instance
- Use the sidebar filters to narrow down results
- Click "View Details" to see comprehensive information about each search

### 2. Marking for Deletion
- Click the "🗑️ Mark for Deletion" button on any search card
- Marked searches will be highlighted with a red border
- Use "🔄 Clear All Marks" to unmark all searches

### 3. Exporting Deletion List
- Once you've marked searches, scroll to the "Deletion Management" section
- Click "📥 Download Deletion List (CSV)" to get a CSV file
- The CSV includes all marked searches with deletion metadata

### 4. Bulk Deletion
- The exported CSV can be used with jpapi's existing bulk delete functionality
- Use: `jpapi advanced-searches delete --csv-file your_deletion_list.csv`

## Data Structure

### Search Card Information
Each search card displays:
- **Name & ID**: Search name and unique identifier
- **Type**: Computer, Mobile, or User search
- **Site**: Associated JAMF Pro site
- **Criteria**: Search criteria with AND/OR logic
- **Display Fields**: Fields shown in search results
- **Device Count**: Number of matching devices/computers

### Deletion Export Format
The exported CSV includes:
- `ID`: Search ID
- `Name`: Search name
- `Type`: Search type (Computer/Mobile/User)
- `Site`: Associated site
- `Smart Search`: Boolean indicating if it's a smart search
- `delete`: "DELETE" marker
- `delete_reason`: Timestamp and reason for deletion

## Integration with jpapi

This viewer integrates seamlessly with jpapi's existing functionality:

1. **Export Data**: Use `jpapi export advanced-searches --format json` to get raw data
2. **Review & Mark**: Use this viewer to visually review and mark items
3. **Export Deletion List**: Download the CSV with marked items
4. **Execute Deletion**: Use `jpapi advanced-searches delete --csv-file` to delete

## Technical Details

### Dependencies
- Streamlit
- Pandas
- jpapi authentication libraries (optional - runs in demo mode if not available)

### Demo Mode
If JAMF authentication libraries are not available, the app runs in demo mode with mock data to demonstrate functionality.

### Port Configuration
- Default port: 8502
- Can be changed in launcher scripts
- Access via: http://localhost:8502

## Troubleshooting

### Common Issues
1. **Port already in use**: Change the port in the launcher script
2. **Authentication errors**: Ensure jpapi is properly configured
3. **No data showing**: Check JAMF Pro connectivity and permissions

### Debug Mode
Run with debug output:
```bash
streamlit run apps/streamlit/advanced_search_viewer.py --logger.level debug
```

## Future Enhancements

- [ ] Real-time JAMF Pro integration
- [ ] Advanced filtering options
- [ ] Search criteria editor
- [ ] Bulk edit capabilities
- [ ] Search performance analytics
- [ ] Export to multiple formats (JSON, Excel)
