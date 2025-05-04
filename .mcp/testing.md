# Testing Framework

## Overview
The SharePoint Data Migration Cleanup Tool includes a comprehensive testing framework to ensure reliability and robustness. The testing approach combines unit tests, integration tests, and test data generation to validate all aspects of the application.

## Test Structure
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Test Data Generation**: Create realistic test scenarios

## Updated Test Directory Structure
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_scanner.py          # Tests for scanner.py
├── test_file_scanner.py     # Tests for the enhanced file scanner
├── test_data_cleaner.py     # Tests for data_cleaner.py
├── test_data_processor.py   # Tests for data_processor.py
├── ui/                      # Tests for UI components
│   ├── __init__.py
│   ├── test_enhanced_data_view.py
│   ├── test_file_analysis_view.py
│   └── test_file_analysis_tab.py
├── analyzers/               # Tests for analyzer modules
│   ├── __init__.py
│   ├── test_name_validator.py
│   ├── test_path_analyzer.py
│   └── test_duplicate_finder.py
├── fixers/                  # Tests for fixer modules
│   ├── __init__.py
│   ├── test_path_fixer.py
│   └── test_name_fixer.py
└── create_test_dir.py       # Test data generation script
```

## Key Testing Components

### Test Fixtures
The `conftest.py` file contains shared fixtures used across tests:
- `test_dir`: Points to the test data directory
- `output_dir`: Creates a temporary directory for test output
- `normal_files_dir`, `illegal_chars_dir`, etc.: Point to specific test directories
- Mock implementations of core classes for isolated testing

### Added Test Fixtures
- `mock_file_scanner`: Mock implementation of the enhanced file scanner
- `file_analysis_view`: Test instance of the file analysis view
- `test_file_data`: Sample file metadata for testing
- `test_issue_data`: Sample issue data for testing

### Test Data Generation
The `create_test_dir.py` script creates a comprehensive test environment with:
1. **Normal files** - Simple files that should migrate without issues
2. **Files with illegal characters** - Files containing characters not allowed in SharePoint
3. **Files with long paths** - Deeply nested structures exceeding the 256-character limit
4. **Duplicate files** - Files with identical content in different locations
5. **Files with PII data** - Mock files containing sensitive information patterns
6. **Files with spaces/special characters** - Files with names that might cause issues
7. **Complex mixed structure** - A combination of all the above for thorough testing

### Enhanced Test Data
The test data now includes additional test cases:
- Files with illegal prefixes (.~, _vti_)
- Files with illegal suffixes (.files, _files, -Dateien, .data)
- Read-only files to test permission issue detection
- Hidden files to test hidden file detection
- Zero-byte files to test empty file detection

### Mock Classes
Mock implementations of core classes allow for testing components in isolation:
- `MockFileSystemScanner`: Simulates file system scanning
- `MockSharePointNameValidator`: Validates filenames without external dependencies
- `MockPathShortener`: Implements path shortening logic for testing
- `MockDuplicateDetector`: Simulates duplicate file detection
- `MockDataProcessor`: Orchestrates mock components for integration testing
- `MockSharePointConnector`: Simulates SharePoint connectivity

### Additional Mock Classes
- `MockFileAnalysisView`: Simulates the file analysis view for testing
- `MockFileIssueMapper`: Maps files to their issues for testing
- `MockQtModel`: Simulates PyQt models for UI testing
- `MockFileSystemScanner`: Enhanced version that provides detailed file metadata

### Running Tests
Execute tests using pytest:
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=core

# Run a specific test file
pytest tests/test_scanner.py

# Run UI component tests
pytest tests/ui/
```

## Coverage Reporting
Test coverage is reported using pytest-cov:
```bash
pytest --cov=core --cov=ui --cov-report=html
```
This generates an HTML report in the `htmlcov` directory showing which lines of code are covered by tests.

## UI Testing
For testing UI components, the framework uses:
- `QtTest` for simulating user interactions
- Mock models and views for isolating UI components
- Event simulation for testing UI responsiveness

## Performance Testing
Special test cases for performance:
- Large file systems (10,000+ files)
- Very deep directory structures
- Files with extremely long paths
- Large number of issues to test UI responsiveness

## Continuous Integration
Tests are automatically run on each pull request to ensure code quality:
- All tests must pass before merging
- Coverage should remain above target threshold
- No regressions in existing functionality