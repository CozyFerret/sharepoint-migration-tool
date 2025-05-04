# core/scanner.py

from PyQt5.QtCore import QThread, pyqtSignal
import os

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
                'duplicates': {}
            }
            
            # Scan directory recursively
            self._scan_directory(self.source_folder, results)
            
            # Analyze results
            self._analyze_results(results)
            
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
            for root, dirs, files in os.walk(directory):
                # Process folders
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    results['total_folders'] += 1
                    
                    # Add to file structure
                    parent_dir = os.path.dirname(dir_path)
                    if parent_dir in results['file_structure']:
                        folder_info = {
                            'path': dir_path,
                            'name': dir_name
                        }
                        results['file_structure'][parent_dir]['folders'].append(folder_info)
                
                # Process files
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    file_size = os.path.getsize(file_path)
                    
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
                            'extension': os.path.splitext(file_name)[1],
                            'issues': []
                        }
                        results['file_structure'][parent_dir]['files'].append(file_info)
                    
                    # Update progress
                    file_count += 1
                    if file_count % 10 == 0:  # Update every 10 files
                        self.progress_updated.emit(file_count, 1000)  # Estimate 1000 files
                
                # Check for interruption
                if self.isInterruptionRequested():
                    return
            
            # Final progress update
            self.progress_updated.emit(file_count, file_count)
            
        except Exception as e:
            self.error_occurred.emit(f"Error scanning directory {directory}: {str(e)}")
    
    def _analyze_results(self, results):
        """Analyze scan results to detect potential issues"""
        # This would call various analyzers to detect issues
        from core.analyzers.name_validator import SharePointNameValidator
        from core.analyzers.path_analyzer import PathAnalyzer
        from core.analyzers.duplicate_finder import DuplicateFinder
        
        # Initialize analyzers
        name_validator = SharePointNameValidator()
        path_analyzer = PathAnalyzer()
        duplicate_finder = DuplicateFinder()
        
        # Apply analyzers to collected files
        # This would analyze all files and populate the issues in the results
        
        # Example (simplified):
        issue_count = 0
        
        # TODO: Implement actual analysis using your analyzers
        # For now, just add some mock issues for demonstration
        
        results['total_issues'] = issue_count


# Create alias for compatibility with existing code
FileSystemScanner = Scanner