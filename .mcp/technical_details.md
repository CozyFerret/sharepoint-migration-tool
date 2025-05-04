# Technical Details

## Development Environment
- Python 3.8+
- PyQt5 UI framework
- pandas for data processing
- Office365-REST-Python-Client for SharePoint connectivity
- pytest for testing

## Key Components
- **FileSystemScanner**: Enhanced scanner that collects comprehensive file metadata
- **FileAnalysisView**: Interactive UI component for detailed file analysis
- **FileAnalysisTab**: Tab component integrating file analysis into the main window
- **EnhancedDataView**: Basic data grid with sorting and filtering capabilities

## Key Data Structures
- File metadata stored in pandas DataFrames
- Analysis results stored as a dictionary of DataFrames by issue type
- File-to-issues mapping for efficient issue lookup
- All data kept in-memory only, no persistent storage

## Data Flow
1. **Scanning Phase**: 
   - Traverse file system collecting metadata (path, name, size, creation date, etc.)
   - Calculate file hashes for duplicate detection
   - Store all data in memory as pandas DataFrames
   - FileSystemScanner collects comprehensive metadata for each file

2. **Analysis Phase**: 
   - Apply analyzers to identify issues
   - Name validator checks for illegal characters and reserved names
   - Path analyzer checks for path length exceeding 256 characters
   - Duplicate finder identifies identical files using content hashes
   - PII detector (placeholder) flags potential sensitive information

3. **Display Phase**:
   - Dashboard provides summary visualization
   - Analysis tab shows issue-based analysis
   - File Analysis tab shows detailed file-level information
   - Files with issues are highlighted with a light red background
   - Issues are displayed in the details panel when a file is selected

4. **Cleaning Phase**: 
   - Apply selected fixes based on user preferences
   - Name fixer corrects illegal characters and reserved names
   - Path shortener reduces path length using various strategies
   - Deduplicator handles duplicate files according to selected strategy
   - All changes are non-destructive (copied to new location)

5. **Upload Phase** (optional): 
   - Connect to SharePoint using configured authentication
   - Upload cleaned files with proper folder structure
   - Provide progress and status feedback

## User Interface Components
- **Main Window**: The application's primary window with tabs
- **Dashboard**: Summary view of scan results
- **Analysis Tab**: Issue-focused analysis
- **File Analysis Tab**: File-focused detailed analysis
- **Migration Tab**: Controls for cleaning and uploading

## File Analysis Features
- **Comprehensive Metadata Display**: View all metadata for each file
- **Issue Highlighting**: Files with issues are visually highlighted
- **Interactive Filtering**: Filter files by various criteria including issue types
- **Detailed Issue View**: See specific issues for each selected file
- **Export Options**: Export analysis in various formats (CSV, Excel, JSON, Text)
- **Context Menu**: Right-click options for common operations

## Multithreading Architecture
- Scanner runs in its own thread to keep UI responsive
- Data cleaner runs in its own thread
- SharePoint uploader runs in its own thread
- UI remains responsive during long-running operations
- Progress updates and status messages communicated via signals

## Error Handling Strategy
- Granular error handling at component level
- Each module catches and logs its own exceptions
- Operations continue even if individual files fail
- Secure logging with PII filtering
- Detailed error reporting to the user

## Security Measures
- No data persistence between runs
- Memory wiping after sensitive operations
- Secure clipboard management
- PII detection without extraction
- Temporary files securely deleted

## Feature Toggles
- Each analyzer and fixer can be enabled/disabled
- PII detection marked as placeholder for future enhancement
- Default configuration provided but runtime configurable
- Configuration stored only in memory during runtime

## Testing Approach
- Unit tests for each module
- Integration tests for end-to-end workflows
- Performance testing with large datasets
- Security testing to ensure proper data handling
- Mock classes for external dependencies
- Test fixtures for controlled environments
- Test data generation for realistic scenarios