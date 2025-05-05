"""
Enhanced File System Scanner for SharePoint Migration Tool

This module provides comprehensive file system scanning capabilities with
detailed file analysis for SharePoint migration preparation, including
extensive metadata collection.
"""

import os
import sys
import time
import hashlib
import logging
import pandas as pd
import concurrent.futures
from datetime import datetime
import stat
import re
import platform
from pathlib import Path

logger = logging.getLogger(__name__)

# Define SharePoint constraints
SHAREPOINT_PATH_LIMIT = 256  # characters
SHAREPOINT_ILLEGAL_CHARS = r'[~#%&*{}\\:<>?/|"]'
SHAREPOINT_ILLEGAL_NAMES = [
    'CON', 'PRN', 'AUX', 'NUL', 
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
]
SHAREPOINT_ILLEGAL_PREFIXES = ['.~', '_vti_']
SHAREPOINT_ILLEGAL_SUFFIXES = ['.files', '_files', '-Dateien', '.data']
SHAREPOINT_MAX_FILENAME_LENGTH = 128  # characters

# Define MIME types for common file extensions
MIME_TYPES = {
    '.txt': 'text/plain',
    '.csv': 'text/csv',
    '.log': 'text/plain',
    '.html': 'text/html',
    '.htm': 'text/html',
    '.xml': 'text/xml',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.zip': 'application/zip',
    '.rar': 'application/x-rar-compressed',
    '.tar': 'application/x-tar',
    '.gz': 'application/gzip',
    '.7z': 'application/x-7z-compressed',
    '.mp3': 'audio/mpeg',
    '.mp4': 'video/mp4',
    '.avi': 'video/x-msvideo',
    '.mov': 'video/quicktime',
    '.wmv': 'video/x-ms-wmv',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.ico': 'image/x-icon',
    '.eml': 'message/rfc822',
    '.msg': 'application/vnd.ms-outlook',
    '.exe': 'application/x-msdownload',
    '.dll': 'application/x-msdownload',
}

class FileSystemScanner:
    """
    Scans file systems for SharePoint migration preparation, providing
    detailed file analysis and issue identification with extensive metadata.
    """
    
    def __init__(self, max_workers=None):
        """
        Initialize the file system scanner.
        
        Args:
            max_workers (int, optional): Maximum number of worker threads. If None,
                                        it will use the default based on CPU count.
        """
        self.max_workers = max_workers
        self.scan_results = {
            'total_files': 0,
            'total_folders': 0,
            'total_size': 0,
            'total_issues': 0,
            'file_types': {},
            'path_length_distribution': {
                50: 0, 100: 0, 150: 0, 
                200: 0, 250: 0, 300: 0
            },
            'avg_path_length': 0,
            'max_path_length': 0,
            'files': [],  # Detailed file info
            'issues': []  # Detailed issue info
        }
        
        # Mapping to track unique files by hash
        self.file_hashes = {}
    
    def scan_directory(self, root_path, callbacks=None):
        """
        Scan a directory and its subdirectories for detailed file analysis.
        
        Args:
            root_path (str): The root directory to scan
            callbacks (dict, optional): Dictionary of callback functions:
                - progress(current, total): Called with progress updates
                - scan_completed(results): Called when scan is complete
        
        Returns:
            dict: The scan results, including file and issue details
        """
        start_time = time.time()
        logger.info(f"Starting scan of {root_path}")
        
        # Reset results
        self._reset_results()
        
        # Normalize the root path
        root_path = os.path.abspath(root_path)
        
        try:
            # First, count the total number of files for progress tracking
            total_files = sum(len(files) for _, _, files in os.walk(root_path))
            self.scan_results['total_files'] = total_files
            
            logger.info(f"Found {total_files} files to scan")
            
            # Process files with thread pool for performance
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                current_file = 0
                
                # Walk the directory tree
                for dirpath, dirnames, filenames in os.walk(root_path):
                    # Count folders
                    self.scan_results['total_folders'] += len(dirnames)
                    
                    # Process each file in this directory
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        futures.append(executor.submit(self._process_file, file_path, root_path))
                    
                    # Update progress
                    if callbacks and 'progress' in callbacks:
                        current_file += len(filenames)
                        callbacks['progress'](current_file, total_files)
                
                # Wait for all tasks to complete and collect results
                for future in concurrent.futures.as_completed(futures):
                    try:
                        file_data, issues = future.result()
                        if file_data:
                            self.scan_results['files'].append(file_data)
                            # Update total size
                            if 'size_bytes' in file_data:
                                self.scan_results['total_size'] += file_data['size_bytes']
                        if issues:
                            self.scan_results['issues'].extend(issues)
                            self.scan_results['total_issues'] += len(issues)
                    except Exception as e:
                        logger.error(f"Error processing file: {str(e)}")
            
            # Process the results for summary statistics
            self._process_results()
            
            # Return or callback with results
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Scan completed in {execution_time:.2f} seconds")
            
            if callbacks and 'scan_completed' in callbacks:
                callbacks['scan_completed'](self.scan_results)
            
            return self.scan_results
            
        except Exception as e:
            logger.error(f"Error during directory scan: {str(e)}")
            if callbacks and 'error' in callbacks:
                callbacks['error'](str(e))
            return None
    
    def _reset_results(self):
        """Reset the scan results."""
        self.scan_results = {
            'total_files': 0,
            'total_folders': 0,
            'total_size': 0,
            'total_issues': 0,
            'file_types': {},
            'path_length_distribution': {
                50: 0, 100: 0, 150: 0, 
                200: 0, 250: 0, 300: 0
            },
            'avg_path_length': 0,
            'max_path_length': 0,
            'files': [],
            'issues': []
        }
        self.file_hashes = {}
    
    def _process_file(self, file_path, root_path):
        """
        Process a single file, collecting detailed information and identifying issues.
        
        Args:
            file_path (str): Path to the file
            root_path (str): Root directory being scanned
        
        Returns:
            tuple: (file_data, issues) where
                file_data (dict): Detailed file information
                issues (list): List of issues identified with this file
        """
        try:
            # Skip if not a file
            if not os.path.isfile(file_path):
                return None, None
            
            # Get file info
            file_info = self._get_file_info(file_path, root_path)
            
            # Explicitly add extension and path_length if missing
            if 'extension' not in file_info:
                file_info['extension'] = os.path.splitext(file_path)[1].lower()
            if 'path_length' not in file_info:
                file_info['path_length'] = len(file_path)
            
            # Check for issues
            issues = self._check_for_issues(file_path, file_info)
            
            # Update file data if issues were found
            if issues:
                file_info['has_issues'] = True
                file_info['issue_count'] = len(issues)
                file_info['issue_types'] = ', '.join(set(issue['issue_type'] for issue in issues))
            
            return file_info, issues
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return None, None
    
    def _get_file_info(self, file_path, root_path):
        """
        Get detailed file information including permissions, dates, and more.
        
        Args:
            file_path (str): Path to the file
            root_path (str): Root directory being scanned
            
        Returns:
            dict: Detailed file information
        """
        # Basic file info
        filename = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        rel_path = os.path.relpath(file_path, root_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Get file stats
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size
        
        # Convert timestamps to datetime objects
        create_time = datetime.fromtimestamp(file_stat.st_ctime)
        mod_time = datetime.fromtimestamp(file_stat.st_mtime)
        access_time = datetime.fromtimestamp(file_stat.st_atime)
        
        # Get path length
        path_length = len(file_path)
        
        # Get MIME type based on extension
        mime_type = MIME_TYPES.get(file_ext, 'application/octet-stream')
        
        # Get permissions
        permissions = self._get_permissions(file_stat.st_mode)
        
        # Get owner (if possible)
        owner = self._get_owner(file_path)
        
        # Calculate hash for smaller files
        file_hash = None
        if file_size < 50 * 1024 * 1024:  # Only hash files smaller than 50MB
            try:
                file_hash = self._calculate_file_hash(file_path)
            except Exception as e:
                logger.warning(f"Could not calculate hash for {file_path}: {str(e)}")
        
        # Create the file info dictionary
        file_info = {
            'filename': filename,
            'directory': directory,
            'relative_path': rel_path,
            'full_path': file_path,
            'size_bytes': file_size,
            'size_formatted': self._format_size(file_size),
            'extension': file_ext,
            'mime_type': mime_type,
            'created': create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'modified': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
            'accessed': access_time.strftime('%Y-%m-%d %H:%M:%S'),
            'path_length': path_length,
            'permissions': permissions,
            'owner': owner,
            'read_only': not os.access(file_path, os.W_OK),
            'hidden': self._is_hidden(file_path),
            'has_issues': False  # Will be updated if issues are found
        }
        
        # Add hash if available
        if file_hash:
            file_info['hash'] = file_hash
        
        return file_info
    
    def _check_for_issues(self, file_path, file_info):
        """
        Check for issues with the file based on SharePoint requirements.
        
        Args:
            file_path (str): Path to the file
            file_info (dict): File information dictionary
            
        Returns:
            list: List of issues identified with this file
        """
        issues = []
        
        # Check file path length
        path_length = file_info['path_length']
        if path_length > SHAREPOINT_PATH_LIMIT:
            issues.append({
                'file_path': file_path,
                'issue_type': 'Path Too Long',
                'description': f'Path exceeds SharePoint limit of {SHAREPOINT_PATH_LIMIT} characters',
                'severity': 'Critical',
                'current_value': path_length,
                'limit': SHAREPOINT_PATH_LIMIT
            })
        
        # Check filename length
        filename = file_info['filename']
        if len(filename) > SHAREPOINT_MAX_FILENAME_LENGTH:
            issues.append({
                'file_path': file_path,
                'issue_type': 'Filename Too Long',
                'description': f'Filename exceeds SharePoint limit of {SHAREPOINT_MAX_FILENAME_LENGTH} characters',
                'severity': 'Critical',
                'current_value': len(filename),
                'limit': SHAREPOINT_MAX_FILENAME_LENGTH
            })
        
        # Check for illegal characters
        if re.search(SHAREPOINT_ILLEGAL_CHARS, filename):
            issues.append({
                'file_path': file_path,
                'issue_type': 'Illegal Characters',
                'description': 'Filename contains characters not allowed in SharePoint',
                'severity': 'Critical',
                'current_value': filename,
                'illegal_pattern': SHAREPOINT_ILLEGAL_CHARS
            })
        
        # Check for reserved names
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in SHAREPOINT_ILLEGAL_NAMES:
            issues.append({
                'file_path': file_path,
                'issue_type': 'Reserved Name',
                'description': 'Filename is a reserved system name',
                'severity': 'Critical',
                'current_value': filename,
                'reserved_name': name_without_ext
            })
        
        # Check for illegal prefixes
        for prefix in SHAREPOINT_ILLEGAL_PREFIXES:
            if filename.startswith(prefix):
                issues.append({
                    'file_path': file_path,
                    'issue_type': 'Illegal Prefix',
                    'description': f'Filename starts with illegal prefix',
                    'severity': 'Critical',
                    'current_value': filename,
                    'illegal_prefix': prefix
                })
                break
        
        # Check for illegal suffixes
        for suffix in SHAREPOINT_ILLEGAL_SUFFIXES:
            if name_without_ext.endswith(suffix):
                issues.append({
                    'file_path': file_path,
                    'issue_type': 'Illegal Suffix',
                    'description': f'Filename ends with illegal suffix',
                    'severity': 'Critical',
                    'current_value': filename,
                    'illegal_suffix': suffix
                })
                break
        
        # Check for duplicate files - if hash is available
        if 'hash' in file_info:
            file_hash = file_info['hash']
            if file_hash in self.file_hashes:
                duplicate_path = self.file_hashes[file_hash]
                issues.append({
                    'file_path': file_path,
                    'issue_type': 'Duplicate File',
                    'description': 'File content is identical to another file',
                    'severity': 'Warning',
                    'duplicate_of': duplicate_path
                })
            else:
                self.file_hashes[file_hash] = file_path
        
        # Check for read-only files (warning for SharePoint upload)
        if file_info.get('read_only', False):
            issues.append({
                'file_path': file_path,
                'issue_type': 'Read-Only File',
                'description': 'File is read-only which might affect migration',
                'severity': 'Warning',
                'current_value': 'Read-Only'
            })
        
        # Check for zero-byte files (potential issues)
        if file_info.get('size_bytes', 0) == 0:
            issues.append({
                'file_path': file_path,
                'issue_type': 'Zero-Byte File',
                'description': 'File has no content',
                'severity': 'Warning',
                'current_value': '0 bytes'
            })
        
        return issues
    
    def _get_permissions(self, mode):
        """
        Get file permissions in readable format.
        
        Args:
            mode (int): File mode bits
            
        Returns:
            str: String representation of permissions
        """
        if platform.system() == 'Windows':
            perms = []
            if mode & stat.S_IRUSR: perms.append('r')
            else: perms.append('-')
            if mode & stat.S_IWUSR: perms.append('w')
            else: perms.append('-')
            if mode & stat.S_IXUSR: perms.append('x')
            else: perms.append('-')
            return ''.join(perms)
        else:
            # Unix-style permissions
            perms = []
            for who in ('USR', 'GRP', 'OTH'):
                for what in ('R', 'W', 'X'):
                    if mode & getattr(stat, 'S_I'+what+who):
                        perms.append(what.lower())
                    else:
                        perms.append('-')
            return ''.join(perms)
    
    def _get_owner(self, file_path):
        """
        Get file owner if possible.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Owner name or unknown
        """
        try:
            if platform.system() == 'Windows':
                import win32security
                sd = win32security.GetFileSecurity(file_path, win32security.OWNER_SECURITY_INFORMATION)
                owner_sid = sd.GetSecurityDescriptorOwner()
                name, domain, type = win32security.LookupAccountSid(None, owner_sid)
                return f"{domain}\\{name}"
            else:
                import pwd
                stat_info = os.stat(file_path)
                uid = stat_info.st_uid
                user = pwd.getpwuid(uid)[0]
                return user
        except:
            return "Unknown"
    
    def _is_hidden(self, file_path):
        """
        Check if a file is hidden.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if the file is hidden, False otherwise
        """
        try:
            if platform.system() == 'Windows':
                import win32api
                import win32con
                attributes = win32api.GetFileAttributes(file_path)
                return attributes & win32con.FILE_ATTRIBUTE_HIDDEN
            else:
                return os.path.basename(file_path).startswith('.')
        except:
            return False
    
    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path (str): Path to the file
            chunk_size (int): Size of chunks to read
        
        Returns:
            str: Hexadecimal hash string
        """
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5.update(chunk)
        return md5.hexdigest()
    
    def _format_size(self, size_bytes):
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes (int): Size in bytes
        
        Returns:
            str: Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
    
    def _process_results(self):
        """Process raw scan results to calculate summary statistics."""
        if not self.scan_results['files']:
            return
                
        # Convert to DataFrame for easier processing
        files_df = pd.DataFrame(self.scan_results['files'])
        
        # Calculate file type distribution - make sure this happens
        if 'extension' in files_df.columns:
            self.scan_results['file_types'] = files_df['extension'].value_counts().to_dict()
        else:
            # If no extension column, create a file type distribution from filenames
            self.scan_results['file_types'] = {}
            for file_info in self.scan_results['files']:
                # Get extension from filename
                filename = file_info.get('filename', '')
                ext = os.path.splitext(filename)[1].lower() or 'no extension'
                if ext not in self.scan_results['file_types']:
                    self.scan_results['file_types'][ext] = 0
                self.scan_results['file_types'][ext] += 1
        
        # Calculate path length distribution - ensure this works
        if 'path_length' in files_df.columns:
            # Get actual distribution
            path_lengths = files_df['path_length'].value_counts().to_dict()
            # Create bins for the visualization
            bins = {50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0}
            for length, count in path_lengths.items():
                for bin_val in sorted(bins.keys()):
                    if length <= bin_val:
                        bins[bin_val] += count
                        break
            self.scan_results['path_length_distribution'] = bins
        else:
            # If no path_length column, estimate from full_path
            self.scan_results['path_length_distribution'] = {50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0}
            if 'full_path' in files_df.columns:
                for _, row in files_df.iterrows():
                    path_length = len(row['full_path'])
                    for bin_val in sorted(self.scan_results['path_length_distribution'].keys()):
                        if path_length <= bin_val:
                            self.scan_results['path_length_distribution'][bin_val] += 1
                            break
        
        # Calculate average and max path length
        if 'path_length' in files_df.columns:
            self.scan_results['avg_path_length'] = int(files_df['path_length'].mean())
            self.scan_results['max_path_length'] = int(files_df['path_length'].max())
        elif 'full_path' in files_df.columns:
            path_lengths = files_df['full_path'].str.len()
            self.scan_results['avg_path_length'] = int(path_lengths.mean())
            self.scan_results['max_path_length'] = int(path_lengths.max())
        
        # Convert files list to DataFrame for the UI
        self.scan_results['files_df'] = files_df
        
        # Convert issues list to DataFrame for the UI
        if self.scan_results['issues']:
            self.scan_results['issues_df'] = pd.DataFrame(self.scan_results['issues'])
    
    def get_results_as_dataframes(self):
        """
        Get the scan results as pandas DataFrames for easier UI integration.
        
        Returns:
            tuple: (files_df, issues_df) where
                files_df (pandas.DataFrame): DataFrame of file information
                issues_df (pandas.DataFrame): DataFrame of identified issues
        """
        if 'files_df' not in self.scan_results:
            if self.scan_results['files']:
                self.scan_results['files_df'] = pd.DataFrame(self.scan_results['files'])
            else:
                self.scan_results['files_df'] = pd.DataFrame()
        
        if 'issues_df' not in self.scan_results:
            if self.scan_results['issues']:
                self.scan_results['issues_df'] = pd.DataFrame(self.scan_results['issues'])
            else:
                self.scan_results['issues_df'] = pd.DataFrame()
        
        return self.scan_results['files_df'], self.scan_results['issues_df']