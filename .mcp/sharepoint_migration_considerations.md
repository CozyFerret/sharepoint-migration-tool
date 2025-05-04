# SharePoint Migration Considerations

## SharePoint Limitations
- **Path Length**: Maximum 256 characters including the URL
- **Illegal Characters**: \ / : * ? " < > | # % & { } + ~ =
- **Reserved Names**: CON, PRN, AUX, NUL, COM1-COM9, LPT1-LPT9
- **Illegal Prefixes**: .~, _vti_
- **Illegal Suffixes**: .files, _files, -Dateien, .data
- **File Size**: Individual file size limitations
- **Filename Length**: Maximum 128 characters
- **Special Files**: Issues with temporary files and certain extensions

## Common Migration Issues
- Files with illegal characters fail to upload
- Long paths cause silent migration failures
- Duplicate files waste storage space and cause conflicts
- Files containing PII create potential compliance issues
- Permission issues when migrating access control lists
- Versioning conflicts
- Read-only files may cause upload issues
- Hidden files may be missed during migration
- Zero-byte files may indicate corruption

## File Metadata for Analysis
- **Basic Metadata**: filename, directory, path, extension
- **Size Information**: bytes, formatted size
- **Timestamps**: created, modified, accessed dates
- **Ownership**: file owner, permissions
- **Content Type**: MIME type
- **Status Flags**: read-only, hidden status
- **Hash**: MD5 hash for duplicate detection
- **Issue Indicators**: has_issues, issue_count, issue_types

## Path Shortening Strategies
1. **Abbreviate Directories**: Transform long directory names to shorter versions
   - Example: "Development Documentation" → "Dev~Doc"
   
2. **Remove Middle Directories**: Keep first and last, replace middle with "..."
   - Example: "/Dept/Team/Projects/2023/Q4/Reports/" → "/Dept/.../Reports/"
   
3. **Truncate Names**: Shorten all directory and file names
   - Example: "Quarterly Financial Analysis Report.xlsx" → "Quar Fin Analy Rep.xlsx"
   
4. **Minimal Path**: Keep only essential path components
   - Example: "C:/Very/Long/Path/To/File.docx" → "C:/ShortPath/File.docx"

## Duplicate Detection Methods
- **Hash-based**: Exact duplicate detection using MD5 content hash
  - Most accurate but more resource-intensive
  - Handles renamed but identical files
  - Limited to files under 50MB for performance
  
- **Name+Size**: Potential duplicate detection when hashing not available
  - Faster but less accurate
  - Good for quick initial scanning
  - Used for larger files automatically

## Duplicate Handling Strategies
- **Keep Oldest**: Preserve the oldest version of each file
  - Good for archival purposes
  
- **Keep Newest**: Preserve the newest version of each file
  - Assumes newer versions are more relevant
  
- **Keep Smallest**: Preserve the smallest version of each file
  - Optimizes for storage efficiency
  
- **Keep Largest**: Preserve the largest version of each file
  - Assumes larger files have more content

## Issue Resolution Options
- **Automatic**: Apply best-practice fixes automatically
- **Interactive**: User selects which issues to fix and how
- **Selective**: Fix only specific issue types
- **Per-File**: Apply different strategies to different files
- **Per-Issue Type**: Apply different strategies to different issue types

## SharePoint Authentication Methods
- **Modern Authentication (OAuth)**: 
  - More secure, supports MFA
  - Uses Microsoft Identity Platform
  
- **Legacy Authentication**:
  - Username/password based
  - Less secure but simpler

- **App-only Authentication**:
  - Uses application credentials
  - Good for automated processes

## Migration Best Practices
- Scan and fix issues before migration
- Test migration with a subset of data first
- Maintain folder structure where possible
- Document changes made during cleaning
- Create a rollback plan
- Perform post-migration validation

## Testing Migration Scenarios
- Create test data with various issues
- Verify file name fixing
- Verify path shortening
- Test duplicate detection accuracy
- Measure performance with large datasets
- Validate SharePoint compatibility of fixed content