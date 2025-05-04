# SharePoint Data Migration Cleanup Tool

A Python desktop application that helps prepare file systems for SharePoint migration by identifying and fixing common issues.

## Overview

SharePoint has several limitations that can cause migration failures, including:
- Character restrictions in filenames
- Maximum path length limitations (256 characters)
- Issues with duplicate files
- Potential exposure of sensitive information (PII)

This tool scans file systems before migration, identifies potential issues, and provides automated or manual fixes to ensure smooth SharePoint migrations.

## Key Features

- **SharePoint Naming Compliance**: Detects and fixes illegal characters in filenames
- **Path Length Analysis**: Identifies paths exceeding SharePoint's 256 character limit
- **Duplicate File Detection**: Finds identical files with different names or locations
- **PII Detection**: Framework for scanning sensitive information (placeholder for future implementation)
- **Manual Mode**: Non-destructive cleaning by copying fixed files to a new location
- **Automatic Mode**: Option to upload directly to SharePoint after cleaning
- **Visual Dashboard**: Graphical analysis of file system issues

## Project Structure

```
sharepoint_migration_tool/
├── core/                      - Core functionality
│   ├── scanner.py             - File system scanning
│   ├── data_cleaner.py        - Cleaning operations
│   ├── data_processor.py      - Process orchestration
│   ├── analyzers/             - Analysis modules
│   │   ├── name_validator.py
│   │   ├── path_analyzer.py
│   │   ├── duplicate_finder.py
│   │   └── pii_detector.py    - PLACEHOLDER - No actual detection yet
│   └── fixers/                - Issue correction modules
│       ├── path_shortener.py
│       ├── name_fixer.py
│       └── deduplicator.py
├── infrastructure/            - SharePoint connectivity
├── ui/                        - User interface components
├── utils/                     - Utility functions
├── tests/                     - Test suite
├── .mcp/                      - Model Context Protocol files
├── main.py                    - Application entry point
└── README.md                  - This file
```

## Installation

### Prerequisites
- Python 3.8+
- PyQt5 (UI framework)
- Other dependencies listed in requirements.txt

### Setup
1. Clone the repository:
```
git clone https://github.com/CozyFerret/sharepoint-migration-tool.git
cd sharepoint-migration-tool
```

2. Create a virtual environment and activate it:
```
# Create environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Launch the application:
```
python main.py
```

## Usage

1. Select the source directory to analyze using the "Browse" button
2. Configure which features you want to use (Name Validation, Path Length, etc.)
3. Click "Start Scan" to begin analysis
4. View results in the Dashboard tab
5. Explore detailed findings in the Analysis and Results tabs
6. Choose from two cleaning modes:
   - **Manual Mode**: Select a target folder for cleaned files
   - **Automatic Mode**: Connect to SharePoint and upload directly

## Testing

The project includes a comprehensive test suite to ensure robust functionality:

```
# Run tests
pytest
```

For generating test data:
```
python create_test_dir.py
```

This will create a test directory structure with various SharePoint migration challenges, including illegal characters, long paths, duplicate files, and more.

## Features Status

- ✅ SharePoint naming compliance validation and fixing
- ✅ Path length detection and shortening
- ✅ Duplicate file detection and management
- ✅ Manual cleaning mode (copy to new location)
- ✅ Automatic SharePoint upload mode
- ✅ Data export functionality
- ✅ Comprehensive test suite
- ❌ PII Detection (placeholder only - framework exists but no actual detection yet)

## Roadmap

- Implement actual PII detection functionality using NLP techniques
- Enhance dashboard visualizations
- Implement more sophisticated path shortening algorithms
- Improve error handling throughout the application
- Create a basic installer for distribution

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