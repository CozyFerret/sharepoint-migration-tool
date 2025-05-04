# SharePoint Migration Tool

A Python-based desktop application for cleaning and preparing file systems for SharePoint migration. This tool helps identify and fix common issues encountered during SharePoint migrations, ensuring a smooth transition to SharePoint Online or on-premises environments.

## Key Features

### Core Functionality
- **Non-Destructive Operation**: All changes are made to copies of original files, preserving your source data
- **In-Memory Processing**: No permanent data storage for enhanced security
- **Comprehensive Analysis**:
  - **SharePoint Naming Compliance**: Detects and fixes illegal characters and reserved names
  - **Path Length Reduction**: Identifies paths exceeding SharePoint's 256 character limit and suggests fixes
  - **Duplicate File Detection**: Finds exact and similar duplicates using hash comparison
  - **PII Detection**: PLACEHOLDER ONLY - Framework exists but no actual detection functionality yet

### Enhanced Data View (New)
- **Interactive Data Grid**:
  - **Sorting**: Click any column header to sort data
  - **Filtering**: Filter by specific column values
  - **Searching**: Full-text search across all or specific columns
- **Multi-Format Export**:
  - Export analyzed data as CSV, Excel, JSON, or text files
  - Export only filtered/selected data

### Flexible Cleanup Options
- **Manual Mode**: Non-destructively copies cleaned data to a new folder
- **Automatic Mode (Enhanced)**: Cleans data and uploads directly to SharePoint
  - **Authentication**: Support for modern username/password and app-only authentication
  - **Document Library Selection**: Browse and select target document libraries
  - **Automatic Folder Creation**: Creates folder structure in SharePoint matching source

### Visual Analysis
- **Dashboard with insights** about your file structure and issues
- **Detailed file reports** with specific issue identification

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
   python main.py
   ```

## Usage Guide

### Basic Workflow

1. **Select the folder** you want to analyze using the "Browse" button
2. **Configure which features** you want to use (Name Validation, Path Length, etc.)
3. **Click "Start Scan"** to begin analysis
4. **View results** in the Analysis tab with the enhanced data view
   - Use the search box to find specific files
   - Filter by column values to focus on specific issues
   - Sort by clicking column headers
5. **Export reports** as needed using the "Export" button
6. **Clean and prepare data** using either:
   - **Manual Mode**: Select a target folder for the cleaned files
   - **Automatic Mode**: Connect to SharePoint and upload directly

### Using Enhanced Data View

1. **Search**: Enter text in the search box to find matching files across all columns
2. **Filter**: Select a column and value from the dropdown menus
3. **Sort**: Click any column header to sort ascending/descending
4. **Export**: Click the Export button and select your preferred format
   - CSV: For spreadsheet applications
   - Excel: For Microsoft Excel
   - JSON: For programmatic access
   - Text: For plain text representation

### SharePoint Integration

1. **Select "Clean and Upload to SharePoint"** mode in the Migration tab
2. **Click "Sign In"** and enter your SharePoint credentials:
   - **Site URL**: Your SharePoint site URL
   - **Authentication Method**: Choose username/password or app-only
3. **Select target document library** from the dropdown
4. **Configure cleaning options** as needed
5. **Click "Start Migration"** to begin the process
6. **Monitor progress** in the status bar

## Security Features

- **No permanent storage**: All data processing happens in memory
- **Secure memory management**: Memory is wiped after sensitive operations
- **PII awareness**: Framework exists but actual PII detection is a placeholder for future development
- **Secure clipboard handling**: Clipboard is cleared after copy operations

## Project Structure

```
sharepoint_migration_tool/
├── core/                # Core functionality
│   ├── scanner.py       # File system scanning
│   ├── data_cleaner.py  # Cleaning operations
│   ├── data_processor.py # Process orchestration
│   ├── analyzers/       # Analysis modules
│   │   ├── name_validator.py
│   │   ├── path_analyzer.py
│   │   ├── duplicate_finder.py
│   │   └── pii_detector.py # PLACEHOLDER - No actual detection yet
│   └── fixers/          # Issue correction modules
│       ├── path_shortener.py
│       ├── name_fixer.py
│       └── deduplicator.py
├── infrastructure/
│   └── sharepoint.py    # SharePoint connectivity
├── ui/                  # User interface components
│   ├── enhanced_data_view.py  # New interactive data view
│   └── migration_ui.py        # Main migration interface
├── utils/               # Utility functions
├── resources/           # Application resources
│   ├── icons/
│   └── styles/
├── main.py              # Application entry point
└── README.md            # This file
```

## Implementation Status

- ✅ SharePoint naming compliance validation and fixing
- ✅ Path length detection and shortening
- ✅ Duplicate file detection and management
- ✅ Manual cleaning mode (copy to new location)
- ✅ Automatic SharePoint upload mode
- ✅ Enhanced data view with sorting, filtering, and searching
- ✅ Multi-format export functionality
- ❌ PII Detection (placeholder only - framework exists but no actual detection yet)

## Extensibility

The modular design makes it easy to extend the functionality:

- For new analyzers, add a module in `core/analyzers/`
- For new fixers, add a module in `core/fixers/`
- Update the UI components in `ui/` to expose the new functionality

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

This tool is provided as-is without warranty. Always test thoroughly before using in production environments.