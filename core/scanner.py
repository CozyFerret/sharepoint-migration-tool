from PyQt5.QtCore import QThread, pyqtSignal
import os
import pandas as pd
import time
import hashlib

class Scanner(QThread):
    """
    Thread for scanning file system and detecting potential SharePoint migration issues.
    """
    # Define signals
    progress_updated = pyqtSignal(int, int)  # current, total
    scan_completed = pyqtSignal(dict)        # results
    error_occurred = pyqtSignal(str)         # error message
    
    def __init__(self, source_folder):
        super().__init__()
        self.source_folder = source_folder
        
    def run(self):
        """Main scanning method that runs in a separate thread"""
        try:
            # Initialize results structure
            results = {
                'root_directory': self.source_folder,
                'total_files': 0,
                'total_folders': 0,
                'total_size': 0,
                'total_issues': 0,
                'file_structure': {},
                'path_length_issues': {},
                'illegal_characters': {},
                'reserved_names': {},
                'duplicates': {},
                'avg_path_length': 0,
                'max_path_length': 0,
                'file_types': {}
            }
            
            # Scan directory recursively
            self._scan_directory(self.source_folder, results)
            
            # Analyze results
            self._analyze_results(results)
            
            # Convert file information to DataFrame for easier handling in UI
            self._prepare_dataframe(results)
            
            # Emit completion signal with results
            self.scan_completed.emit(results)
            
        except Exception as e:
            # Emit error signal
            self.error_occurred.emit(str(e))
    
    def _scan_directory(self, directory, results):
        """Recursively scan a directory and collect file/folder information"""
        try:
            # Keep track of files in this directory
            results['file_structure'][directory] = {
                'files': [],
                'folders': []
            }
            
            # Count files and folders
            file_count = 0
            path_lengths = []
            
            for root, dirs, files in os.walk(directory):
                # Process folders
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    results['total_folders'] += 1
                    path_len = len(dir_path)
                    path_lengths.append(path_len)
                    
                    # Check path length
                    if path_len > 256:  # SharePoint path length limit
                        if path_len not in results['path_length_issues']:
                            results['path_length_issues'][path_len] = []
                        results['path_length_issues'][path_len].append({
                            'path': dir_path,
                            'name': dir_name,
                            'type': 'folder'
                        })
                        results['total_issues'] += 1
                    
                    # Add to file structure
                    parent_dir = os.path.dirname(dir_path)
                    if parent_dir in results['file_structure']:
                        folder_info = {
                            'path': dir_path,
                            'name': dir_name,
                            'path_length': path_len
                        }
                        results['file_structure'][parent_dir]['folders'].append(folder_info)
                
                # Process files
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    
                    # Get basic file info
                    try:
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file_name)[1].lower()
                    except:
                        file_size = 0
                        file_ext = ""
                    
                    # Track file types
                    if file_ext not in results['file_types']:
                        results['file_types'][file_ext] = 0
                    results['file_types'][file_ext] += 1
                    
                    # Update path length stats
                    path_len = len(file_path)
                    path_lengths.append(path_len)
                    
                    # Check path length
                    file_has_issues = False
                    if path_len > 256:  # SharePoint path length limit
                        if path_len not in results['path_length_issues']:
                            results['path_length_issues'][path_len] = []
                        results['path_length_issues'][path_len].append({
                            'path': file_path,
                            'name': file_name,
                            'type': 'file'
                        })
                        file_has_issues = True
                        results['total_issues'] += 1
                    
                    # Update totals
                    results['total_files'] += 1
                    results['total_size'] += file_size
                    
                    # Add to file structure
                    parent_dir = os.path.dirname(file_path)
                    if parent_dir in results['file_structure']:
                        file_info = {
                            'path': file_path,
                            'name': file_name,
                            'size': file_size,
                            'extension': file_ext,
                            'path_length': path_len,
                            'has_issues': file_has_issues,
                            'issue_count': 1 if file_has_issues else 0
                        }
                        results['file_structure'][parent_dir]['files'].append(file_info)
                    
                    # Update progress
                    file_count += 1
                    if file_count % 10 == 0:  # Update every 10 files
                        self.progress_updated.emit(file_count, 1000)  # Estimate 1000 files
                
                # Check for interruption
                if self.isInterruptionRequested():
                    return
            
            # Calculate path length statistics
            if path_lengths:
                results['avg_path_length'] = sum(path_lengths) // len(path_lengths)
                results['max_path_length'] = max(path_lengths)
            
            # Create path length distribution
            distribution = {50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0}
            for length in path_lengths:
                for bin_val in sorted(distribution.keys()):
                    if length <= bin_val:
                        distribution[bin_val] += 1
                        break
            results['path_length_distribution'] = distribution
            
            # Final progress update
            self.progress_updated.emit(file_count, file_count)
            
        except Exception as e:
            self.error_occurred.emit(f"Error scanning directory {directory}: {str(e)}")
    
    def _analyze_results(self, results):
        """Analyze scan results to detect potential issues"""
        # This is where we would call various analyzers to detect issues
        # For now, we've already collected path length issues during scanning
        
        # Count total issues
        total_issues = 0
        for length, files in results['path_length_issues'].items():
            total_issues += len(files)
        for char, files in results['illegal_characters'].items():
            total_issues += len(files)
        for name, files in results['reserved_names'].items():
            total_issues += len(files)
        for hash_val, files in results['duplicates'].items():
            total_issues += len(files) - 1  # Count all but the first file
            
        results['total_issues'] = total_issues
    
    def _prepare_dataframe(self, results):
        """Prepare a DataFrame from the file information for easier UI display"""
        # Collect all files into a flat list
        files = []
        for dir_path, dir_data in results['file_structure'].items():
            for file_info in dir_data['files']:
                files.append(file_info)
        
        # Convert to DataFrame
        if files:
            df = pd.DataFrame(files)
            
            # Add path_length column if not present
            if 'path_length' not in df.columns:
                df['path_length'] = df['path'].apply(len)
                
            # Add has_issues column if not present
            if 'has_issues' not in df.columns:
                df['has_issues'] = False
                for _, path_issues in results['path_length_issues'].items():
                    for issue in path_issues:
                        if 'path' in issue:
                            df.loc[df['path'] == issue['path'], 'has_issues'] = True
                
            # Add issue_count column if not present
            if 'issue_count' not in df.columns:
                df['issue_count'] = 0
                for _, path_issues in results['path_length_issues'].items():
                    for issue in path_issues:
                        if 'path' in issue:
                            df.loc[df['path'] == issue['path'], 'issue_count'] += 1
            
            # Store DataFrame in results
            results['files_df'] = df
            
            # Store common column names for compatibility
            results['scan_data'] = df
            
            # Convert issues to DataFrame for UI components
            issues = []
            for length, path_issues in results['path_length_issues'].items():
                for issue in path_issues:
                    issues.append({
                        'file_path': issue['path'],
                        'issue_type': 'Path Too Long',
                        'severity': 'Critical' if length > 250 else 'Warning',
                        'description': f'Path exceeds SharePoint limit of 256 characters (current: {length})'
                    })
            
            if issues:
                results['issues'] = issues
                results['issues_df'] = pd.DataFrame(issues)