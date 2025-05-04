# Code Structure

## Main Modules

### Core
- `scanner.py` - File system scanning with multithreading support
- `data_cleaner.py` - Implements file cleaning operations
- `data_processor.py` - Orchestrates scanning, analysis, and cleaning

### Analyzers
- `name_validator.py` - Validates file/folder names against SharePoint rules
- `path_analyzer.py` - Analyzes path lengths against SharePoint limitations
- `duplicate_finder.py` - Identifies duplicate files based on content hash
- `pii_detector.py` - Placeholder for PII detection (future enhancement)

### Fixers
- `name_fixer.py` - Corrects illegal characters and reserved names
- `path_shortener.py` - Implements strategies to reduce path lengths
- `deduplicator.py` - Manages duplicate files with various strategies

### Infrastructure
- `sharepoint.py` - SharePoint connectivity and upload functionality

### UI
- `main_window.py` - Main application window and controller
- `dashboard.py` - Summary visualization of scan results
- `analyzer_widget.py` - Detailed issue analysis interface
- `results_widget.py` - Results viewing interface
- `export_widget.py` - Export functionality
- `cleanup_widget.py` - Cleanup and upload interface

### Utils
- `config.py` - Configuration management
- `secure_logging.py` - Privacy-preserving logging
- `memory_cleanup.py` - Secure memory wiping utilities

### Tests
- `conftest.py` - Shared test fixtures and configuration
- `test_scanner.py` - Tests for file system scanner
- `test_data_cleaner.py` - Tests for data cleaning operations
- `test_data_processor.py` - Tests for process orchestration
- `create_test_dir.py` - Script to generate test data with various SharePoint migration challenges

## File Hierarchy
```
sharepoint_migration_tool/
├── core/                   # Core scanning and analysis logic
│   ├── scanner.py
│   ├── data_cleaner.py
│   ├── data_processor.py
│   ├── analyzers/
│   │   ├── name_validator.py
│   │   ├── path_analyzer.py
│   │   ├── duplicate_finder.py
│   │   └── pii_detector.py
│   └── fixers/
│       ├── path_shortener.py
│       ├── name_fixer.py
│       └── deduplicator.py
├── infrastructure/
│   └── sharepoint.py       # SharePoint connectivity
├── ui/                     # User interface components
│   ├── main_window.py
│   ├── dashboard.py
│   ├── analyzer_widget.py
│   ├── results_widget.py
│   ├── export_widget.py
│   └── cleanup_widget.py
├── utils/                  # Utility functions
│   ├── config.py
│   ├── secure_logging.py
│   └── memory_cleanup.py
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_scanner.py
│   ├── test_data_cleaner.py
│   ├── test_data_processor.py
│   ├── analyzers/
│   │   ├── test_name_validator.py
│   │   ├── test_path_analyzer.py
│   │   └── test_duplicate_finder.py
│   ├── fixers/
│   │   ├── test_path_shortener.py
│   │   └── test_name_fixer.py
│   └── create_test_dir.py
├── main.py                 # Application entry point
└── README.md               # Project documentation
```

## Module Dependencies

- The UI layer uses the Data Processor for operations
- Data Processor coordinates Analyzers, Fixers, and Scanner
- Scanner provides raw file data to Analyzers
- Fixers apply changes based on Analyzer results
- SharePoint module integrates with the Data Cleaner for uploads
- Test modules use mock classes to isolate components for unit testing

## Data Flow

1. Main Window initiates file scan via Data Processor
2. Scanner collects file metadata
3. Analyzers process file metadata and identify issues
4. UI displays results to user
5. User initiates cleanup via Data Cleaner
6. Fixers apply fixes to files based on analysis
7. Data Cleaner copies fixed files or uploads to SharePoint

## Testing Flow

1. Test fixtures create controlled test environments
2. Unit tests validate individual component functionality
3. Integration tests verify component interactions
4. Test data generator creates realistic test scenarios
5. Coverage reporting ensures comprehensive testing