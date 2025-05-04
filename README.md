# SharePoint Data Migration Cleanup Tool

A Python-based desktop application for cleaning and preparing file systems for SharePoint migration. This tool helps identify and fix common issues encountered during SharePoint migrations, such as illegal characters in file names, overly long paths, duplicate files, and potentially sensitive information.

## Key Features

- **No Permanent Storage**: Runs in-memory only, with no data persistence to eliminate security concerns
- **SharePoint Naming Compliance**: Detects and fixes illegal characters and reserved names
- **Path Length Reduction**: Identifies paths exceeding SharePoint's 256 character limit and suggests fixes
- **Duplicate File Detection**: Finds exact and similar duplicates using hash comparison
- **PII Detection**: *(Coming Soon)* Placeholder for future functionality to identify files containing sensitive information
- **Data Insights**: Visualizes file system structure and issues
- **Customizable Reports**: Exports insights in various formats
- **Dual Cleanup Modes**:
  - **Manual Mode**: Non-destructively copies cleaned data to a new folder
  - **Automatic Mode**: Cleans data and uploads directly to SharePoint

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sharepoint-migration-tool.git
   cd sharepoint-migration-tool
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

### Basic Workflow

1. Select the folder you want to analyze using the "Browse" button
2. Configure which features you want to use (Name Validation, Path Length, etc.)
3. Click "Start Scan" to begin analysis
4. View results in the Dashboard tab
5. Explore detailed findings in the Analysis and Results tabs
6. Export reports as needed from the Export tab
7. Clean and prepare data using either:
   - **Manual Mode**: Select a target folder for the cleaned files
   - **Automatic Mode**: Connect to SharePoint and upload directly

## Security Features

- No permanent data storage
- Memory is securely cleared after use
- PII detection without extraction
- Clipboard clearing after sensitive operations

## Requirements

- Python 3.8+
- PyQt5
- pandas
- pathlib
- python-magic
- spacy (for PII detection)
- matplotlib/seaborn (for visualizations)
- jinja2 (for report templates)
- weasyprint (for PDF export)
- openpyxl (for Excel export)
- Office365-REST-Python-Client (for SharePoint integration)
- msal (for Microsoft authentication)
- requests (for API calls)

## Development

### Project Structure

```
sharepoint_migration_tool/
├── core/               # Core functionality
│   ├── scanner.py      # File system scanning
│   ├── analyzers/      # Analysis modules
│   └── fixers/         # Issue correction modules
├── ui/                 # User interface
├── utils/              # Utility functions
├── resources/          # UI resources
├── reports/            # Report templates
├── main.py             # Application entry point
└── README.md           # This file
```

### Adding New Features

1. For new analyzers, add a module in `core/analyzers/`
2. For new fixers, add a module in `core/fixers/`
3. Update the UI components in `ui/` to expose the new functionality

## License

[MIT License](LICENSE)

## Disclaimer

This tool is provided as-is without warranty. Always test thoroughly before using in production environments.