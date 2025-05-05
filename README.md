# SharePoint Migration Tool - Enhanced Edition

A Python-based desktop application for cleaning and preparing file systems for SharePoint migration. This tool helps identify and fix common issues encountered during SharePoint migrations, ensuring a smooth transition to SharePoint Online or on-premises environments.

## Key Features

### Core Functionality
- **Operational Mode Options**:
  - **Non-Destructive Operation**: Makes changes to copies of original files, preserving your source data
  - **Destructive Operation**: Modifies files in-place for more direct workflows when needed
- **Destination Options**:
  - **Local Saving**: Save cleaned files to a local directory
  - **Direct SharePoint Upload**: Upload directly to SharePoint after cleaning
- **In-Memory Processing**: No permanent data storage for enhanced security
- **Comprehensive Analysis**:
  - **SharePoint Naming Compliance**: Detects and fixes illegal characters and reserved names
  - **Path Length Reduction**: Identifies paths exceeding SharePoint's 256 character limit and suggests fixes
  - **Duplicate File Detection**: Finds exact and similar duplicates using hash comparison
  - **PII Detection**: PLACEHOLDER ONLY - Framework exists but no actual detection functionality yet

### Enhanced Data View
- **Interactive Data Grid**:
  - **Sorting**: Click any column header to sort data
  - **Filtering**: Filter by specific column values
  - **Searching**: Full-text search across all or specific columns
- **Multi-Format Export**:
  - Export analyzed data as CSV, Excel, JSON, or text files
  - Export only filtered/selected data

### Advanced Settings
- **Operation Mode Settings**:
  - Choose between destructive and non-destructive operations
  - Toggle preserving original timestamps during cleaning
  - Option to ignore hidden files during scanning
- **Destination Settings**:
  - Configure whether to save locally or upload to SharePoint
  - Persistent settings between application runs
  - Visual warnings for potentially destructive operations

### SharePoint Integration
- **Authentication**: Support for modern username/password and app-only authentication
- **Document Library Selection**: Browse and select target document libraries
- **Automatic Folder Creation**: Creates folder structure in SharePoint matching source

## Requirements

- Python 3.8+
- Dependencies:
  - PyQt5 (UI framework)
  - pandas (data processing)
  - pathlib (path manipulation)
  - Office365-REST-Python-Client (SharePoint integration)
  - See `requirements.txt` for full list

## Installation

1. **Clone this repository**:
   ```
   git clone https://github.com/CozyFerret/sharepoint-migration-tool.git
   cd sharepoint-migration-tool
   ```

2. **Create a virtual environment and activate it**:
   ```
   # Create environment
   python -m venv venv

   # Activate on Windows
   venv\Scripts\activate

   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Launch the application**:
   ```
   python sp_migration_tool.py
   ```

## Usage Guide

### Basic Workflow

1. **Select the folder** you want to analyze using the "Browse" button
2. **Click "Start Scan"** to begin analysis
3. **View results** in the Analysis tab with the enhanced data view
   - Use the search box to find specific files
   - Filter by column values to focus on specific issues
   - Sort by clicking column headers
4. **Configure settings** in the Settings tab
   - Choose between destructive and non-destructive operations
   - Select whether to save locally or upload to SharePoint
5. **Clean and prepare data** in the Migration tab
   - Configure cleaning options (Fix names, Fix paths, etc.)
   - Select destination (local folder or SharePoint library)
   - Click "Start Migration" to begin the cleaning process

### Operational Modes

1. **Non-Destructive Mode** (Default):
   - Creates copies of files with issues fixed
   - Original files remain untouched
   - Safer option for preserving original data

2. **Destructive Mode**:
   - Modifies files in-place
   - No extra disk space required for copies
   - Use with caution and make backups first

### Destination Options

1. **Save to Local Directory**:
   - Cleaned files are saved to a local folder
   - Choose any accessible directory as the target

2. **Upload to SharePoint**:
   - Cleaned files are uploaded directly to SharePoint
   - Requires SharePoint authentication
   - Select target document library from the dropdown

## Security Features

- **No permanent storage**: All data processing happens in memory
- **Secure memory management**: Memory is wiped after sensitive operations
- **PII awareness**: Framework exists but actual PII detection is a placeholder for future development
- **Secure clipboard handling**: Clipboard is cleared after copy operations

## Implementation Status

- ✅ SharePoint naming compliance validation and fixing
- ✅ Path length detection and shortening
- ✅ Duplicate file detection and management
- ✅ Destructive/Non-destructive operation modes
- ✅ Local saving and direct SharePoint upload options
- ✅ Enhanced data view with sorting, filtering, and searching
- ✅ Multi-format export functionality
- ✅ Advanced settings management
- ❌ PII Detection (placeholder only - framework exists but no actual detection yet)

## Future Enhancements

- Implement actual PII detection functionality using NLP techniques
- Add automated testing with large datasets
- Enhance SharePoint connectivity with additional authentication methods
- Add visualization components for file system structure
- Implement more sophisticated path shortening algorithms

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided as-is without warranty. Always test thoroughly before using in production environments. The destructive mode modifies files in-place, so always make backups before using this mode.