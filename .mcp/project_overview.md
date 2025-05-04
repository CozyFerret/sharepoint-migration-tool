# SharePoint Data Migration Cleanup Tool

## Project Purpose
This desktop application prepares local file systems for SharePoint migration by identifying and fixing common issues:
- Detecting and fixing illegal characters in file/folder names
- Shortening paths exceeding SharePoint's 256-character limit
- Identifying and managing duplicate files
- Identifying potential files containing PII (marked as future enhancement)

## Key Features
- In-memory operation with no permanent data storage for enhanced security
- Dual mode operation: 
  - Manual Mode: Non-destructive cleaning (copies fixed files to new location)
  - Automatic Mode: Direct SharePoint upload after cleaning
- Comprehensive scanning and analysis with detailed reports
- User-friendly interface with visualization and detailed issue reporting
- Detailed file-level analysis with comprehensive metadata
- Interactive data grid with sorting, filtering, and export capabilities
- Export functionality in multiple formats (CSV, Excel, JSON, Text)
- Comprehensive testing suite for reliability

## Technical Details
- Python-based desktop application using PyQt5
- Modular architecture with separation of concerns
- Multithreaded design for responsive UI during long operations
- Optional SharePoint integration via the Office365 REST API
- Automated testing with pytest

## Security Considerations
- All operations performed in-memory
- Secure wiping of sensitive data
- No persistent data storage
- PII detection without extraction

## Architecture
The application follows a modular design with clear separation between:
- Core scanning and analysis
- Issue detection (analyzers)
- Issue resolution (fixers)
- UI components
- SharePoint integration
- Testing infrastructure

## New Features
- **Enhanced File Scanner**: Collects comprehensive metadata including permissions, dates, owner, MIME type
- **File Analysis View**: Interactive data grid for file-level analysis with sorting and filtering
- **File Analysis Tab**: Integration of detailed file analysis into the main window
- **Enhanced Issue Detection**: Detection of path issues, illegal characters, duplicates, and more
- **Issue Display**: Detailed view of issues associated with each file

## Development Goals
- Maintain clean, modular code structure
- Ensure high test coverage
- Keep security as a priority throughout development
- Make extensible design for future enhancements
- Create intuitive UI for non-technical users

## Testing Philosophy
- Comprehensive unit testing for all core components
- Test-driven development for new features
- Automatic generation of test data
- Mock implementations for external dependencies
- Continuous integration for each pull request