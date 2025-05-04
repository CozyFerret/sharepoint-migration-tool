# SharePoint Migration Considerations

## SharePoint Limitations
- **Path Length**: Maximum 256 characters including the URL
- **Illegal Characters**: \ / : * ? " < > | # % & { } + ~ =
- **Reserved Names**: CON, PRN, AUX, NUL, COM1-COM9, LPT1-LPT9
- **File Size**: Individual file size limitations
- **Special Files**: Issues with temporary files and certain extensions

## Common Migration Issues
- Files with illegal characters fail to upload
- Long paths cause silent migration failures
- Duplicate files waste storage space and cause conflicts
- Files containing PII create potential compliance issues
- Permission issues when migrating access control lists
- Versioning conflicts

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
- **Hash-based**: Exact duplicate detection using SHA-256 content hash
  - Most accurate but more resource-intensive
  - Handles renamed but identical files
  
- **Name+Size**: Potential duplicate detection when hashing not available
  - Faster but less accurate
  - Good for quick initial scanning

## Duplicate Handling Strategies
- **Keep Oldest**: Preserve the oldest version of each file
  - Good for archival purposes
  
- **Keep Newest**: Preserve the newest version of each file
  - Assumes newer versions are more relevant
  
- **Keep Smallest**: Preserve the smallest version of each file
  - Optimizes for storage efficiency
  
- **Keep Largest**: Preserve the largest version of each file
  - Assumes larger files have more content

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