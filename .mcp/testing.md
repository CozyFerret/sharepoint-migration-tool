# Testing Framework

## Overview
The SharePoint Data Migration Cleanup Tool includes a comprehensive testing framework to ensure reliability and robustness. The testing approach combines unit tests, integration tests, and test data generation to validate all aspects of the application.

## Test Structure
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Test Data Generation**: Create realistic test scenarios

## Test Directory Structure
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_scanner.py          # Tests for scanner.py
├── test_data_cleaner.py     # Tests for data_cleaner.py
├── test_data_processor.py   # Tests for data_processor.py
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

### Test Data Generation
The `create_test_dir.py` script creates a comprehensive test environment with:
1. **Normal files** - Simple files that should migrate without issues
2. **Files with illegal characters** - Files containing characters not allowed in SharePoint
3. **Files with long paths** - Deeply nested structures exceeding the 256-character limit
4. **Duplicate files** - Files with identical content in different locations
5. **Files with PII data** - Mock files containing sensitive information patterns
6. **Files with spaces/special characters** - Files with names that might cause issues
7. **Complex mixed structure** - A combination of all the above for thorough testing

The script can be run with different complexity levels:
```bash
# Create a default test structure with normal complexity
python create_test_dir.py

# Create a simpler test structure
python create_test_dir.py --complexity simple

# Create a complex test structure with many edge cases
python create_test_dir.py --complexity complex

# Specify a custom directory
python create_test_dir.py --dir my_custom_test_data
```

### Mock Classes
Mock implementations of core classes allow for testing components in isolation:
- `MockFileSystemScanner`: Simulates file system scanning
- `MockSharePointNameValidator`: Validates filenames without external dependencies
- `MockPathShortener`: Implements path shortening logic for testing
- `MockDuplicateDetector`: Simulates duplicate file detection
- `MockDataProcessor`: Orchestrates mock components for integration testing
- `MockSharePointConnector`: Simulates SharePoint connectivity

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
```

## Coverage Reporting
Test coverage is reported using pytest-cov:
```bash
pytest --cov=core --cov-report=html
```
This generates an HTML report in the `htmlcov` directory showing which lines of code are covered by tests.

## Continuous Integration
Tests are automatically run on each pull request to ensure code quality:
- All tests must pass before merging
- Coverage should remain above target threshold
- No regressions in existing functionality