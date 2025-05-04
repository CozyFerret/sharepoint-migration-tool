# SharePoint Data Migration Cleanup Tool

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/CozyFerret/sharepoint-migration-tool/ci.yml?branch=main)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/github/license/CozyFerret/sharepoint-migration-tool)

A Python-based desktop application for cleaning and preparing file systems for SharePoint migration. This tool helps identify and fix common issues encountered during SharePoint migrations, ensuring a smooth transition to SharePoint Online or on-premises environments.

## 🌟 Key Features

- **Non-Destructive Operation**: All changes are made to copies of original files, preserving your source data
- **In-Memory Processing**: No permanent data storage for enhanced security
- **Comprehensive Analysis**:
  - **SharePoint Naming Compliance**: Detects and fixes illegal characters and reserved names
  - **Path Length Reduction**: Identifies paths exceeding SharePoint's 256 character limit and suggests fixes
  - **Duplicate File Detection**: Finds exact and similar duplicates using hash comparison
  - **PII Detection**: **PLACEHOLDER ONLY** - Framework exists but no actual detection functionality yet
- **Flexible Cleanup Options**:
  - **Manual Mode**: Non-destructively copies cleaned data to a new folder
  - **Automatic Mode**: Cleans data and uploads directly to SharePoint
- **Visual Analysis**: Dashboard with insights about your file structure and issues
- **Export Capabilities**: Generate detailed reports in various formats (CSV, Excel, JSON, Text)

## 📋 Requirements

- Python 3.8+
- Dependencies:
  - PyQt5 (UI framework)
  - pandas (data processing)
  - pathlib (path manipulation)
  - Office365-REST-Python-Client (SharePoint integration)
  - See `requirements.txt` for full list

## 🚀 Getting Started

### Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/CozyFerret/sharepoint-migration-tool.git
   cd sharepoint-migration-tool
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   # Create environment
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. **Launch the application**:
   ```bash
   python main.py
   ```

2. **Basic workflow**:
   - Select the folder you want to analyze using the "Browse" button
   - Configure which features you want to use (Name Validation, Path Length, etc.)
   - Click "Start Scan" to begin analysis
   - View results in the Dashboard tab
   - Explore detailed findings in the Analysis and Results tabs
   - Export reports as needed from the Export tab
   - Clean and prepare data using either:
     - **Manual Mode**: Select a target folder for the cleaned files
     - **Automatic Mode**: Connect to SharePoint and upload directly

## 🔒 Security Features

- **No permanent storage**: All data processing happens in memory
- **Secure memory management**: Memory is wiped after sensitive operations
- **PII awareness**: Framework exists but actual PII detection is a placeholder for future development
- **Secure clipboard handling**: Clipboard is cleared after copy operations

## 🏗️ Project Structure

```
sharepoint_migration_tool/
├── core/                   # Core functionality
│   ├── scanner.py          # File system scanning
│   ├── data_cleaner.py     # Cleaning operations
│   ├── data_processor.py   # Process orchestration
│   ├── analyzers/          # Analysis modules
│   │   ├── name_validator.py
│   │   ├── path_analyzer.py
│   │   ├── duplicate_finder.py
│   │   └── pii_detector.py # PLACEHOLDER - No actual detection yet
│   └── fixers/             # Issue correction modules
│       ├── path_shortener.py
│       ├── name_fixer.py
│       └── deduplicator.py
├── infrastructure/
│   └── sharepoint.py       # SharePoint connectivity
├── ui/                     # User interface components
├── utils/                  # Utility functions
├── main.py                 # Application entry point
└── README.md               # This file
```

## ✅ Current Status

- ✅ SharePoint naming compliance validation and fixing
- ✅ Path length detection and shortening
- ✅ Duplicate file detection and management
- ✅ Manual cleaning mode (copy to new location)
- ✅ Automatic SharePoint upload mode
- ✅ Data export functionality
- ❌ PII Detection (placeholder only - framework exists but no actual detection yet)

## 🧩 Extending the Tool

The modular design makes it easy to extend the functionality:

- For new analyzers, add a module in `core/analyzers/`
- For new fixers, add a module in `core/fixers/`
- Update the UI components in `ui/` to expose the new functionality

## 🔮 Future Development Plans

- Implement actual PII detection functionality using NLP techniques
- Add automated testing with large datasets
- Enhance SharePoint connectivity with additional authentication methods
- Add visualization components for file system structure
- Implement more sophisticated path shortening algorithms

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is provided as-is without warranty. Always test thoroughly before using in production environments.