# Technical Details

## Development Environment
- Python 3.8+
- PyQt5 UI framework
- pandas for data processing
- Office365-REST-Python-Client for SharePoint connectivity
- pytest for testing

## Key Data Structures
- File metadata stored in pandas DataFrames
- Analysis results stored as a dictionary of DataFrames by issue type
- All data kept in-memory only, no persistent storage

## Data Flow
1. **Scanning Phase**: 
   - Traverse file system collecting metadata (path, name, size, creation date, etc.)
   - Calculate file hashes for duplicate detection
   - Store all data in memory as pandas DataFrames

2. **Analysis Phase**: 
   - Apply analyzers to identify issues
   - Name validator checks for illegal characters and reserved names
   - Path analyzer checks for path length exceeding 256 characters
   - Duplicate finder identifies identical files using content hashes
   - PII detector (placeholder) flags potential sensitive information

3. **Cleaning Phase**: 
   - Apply selected fixes based on user preferences
   - Name fixer corrects illegal characters and reserved names
   - Path shortener reduces path length using various strategies
   - Deduplicator handles duplicate files according to selected strategy
   - All changes are non-destructive (copied to new location)

4. **Upload Phase** (optional): 
   - Connect to SharePoint using configured authentication
   - Upload cleaned files with proper folder structure
   - Provide progress and status feedback

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