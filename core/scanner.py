# core/scanner.py

from PyQt5.QtCore import QThread, pyqtSignal
import os
import sys
import logging
import traceback

# Configure logger
logger = logging.getLogger('sharepoint_migration_tool')

class Scanner(QThread):
    """
    Thread for scanning file system and detecting potential SharePoint migration issues.
    """
    # Define signals
    progress_updated = pyqtSignal(int, int)  # current, total
    scan_completed = pyqtSignal(dict)        # results
    error_occurred = pyqtSignal(str)         # error message
    
    def __init__(self, source_folder):
        """Initialize the scanner with the source folder to scan"""
        super().__init__()
        self.source_folder = source_folder
        self.is_interrupted = False
        logger.info(f"Scanner initialized with source folder: {source_folder}")
        
    def scan(self):
        """
        Start the scanning process by starting the thread.
        This method provides compatibility with non-threaded scanner implementations.
        
        Returns:
            dict: Empty dictionary as a placeholder since the actual results 
                will be emitted via the scan_completed signal
        """
        try:
            logger.info(f"Starting scan thread for {self.source_folder}")
            
            # Verify source folder exists
            if not self.source_folder or not os.path.exists(self.source_folder):
                error_msg = f"Invalid source folder: {self.source_folder}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return {}
                
            # Check if thread is already running
            if self.isRunning():
                logger.warning("Scan thread is already running")
                return {}
                
            # Start the thread which will run the 'run' method
            self.start()
            return {}
        
        except Exception as e:
            logger.error(f"Error in scan method: {str(e)}")
            # Try to emit the error signal
            try:
                self.error_occurred.emit(f"Error starting scan: {str(e)}")
            except:
                pass  # Ignore if signal emission fails
            return {}
        
    def run(self):
        """Main scanning method that runs in a separate thread"""
        try:
            logger.info(f"Scan thread started for {self.source_folder}")
            
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
            
            # Verify source folder exists before scanning
            if not self.source_folder or not os.path.exists(self.source_folder):
                error_msg = f"Source folder not found or invalid: {self.source_folder}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            # Scan directory recursively
            self._scan_directory(self.source_folder, results)
            
            # Only analyze and emit results if not interrupted
            if not self.is_interrupted:
                # Analyze results
                self._analyze_results(results)
                
                # Emit completion signal with results
                logger.info("Scan completed successfully, emitting results")
                self.scan_completed.emit(results)
            else:
                logger.info("Scan was interrupted")
                
        except Exception as e:
            # Get detailed exception info
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_msg = f"Error during scan: {str(e)}\n{''.join(traceback_details)}"
            
            # Log the detailed error
            logger.error(error_msg)
            
            # Emit a simplified error for the UI
            self.error_occurred.emit(f"Error during scan: {str(e)}")
    
    def _scan_directory(self, directory, results):
        """Recursively scan a directory and collect file/folder information"""
        try:
            # Check for interruption
            if self.is_interrupted:
                return
                
            logger.debug(f"Scanning directory: {directory}")
                
            # Keep track of files in this directory
            results['file_structure'][directory] = {
                'files': [],
                'folders': []
            }
            
            # Count files and folders
            file_count = 0
            total_count = 0
            
            # Pre-count files to provide better progress updates
            try:
                total_count = sum(len(files) for _, _, files in os.walk(directory))
            except Exception as e:
                logger.warning(f"Error counting files: {e}")
                total_count = 0
                
            if total_count == 0:
                total_count = 1  # Avoid division by zero
            
            try:
                # Now do the actual scan
                for root, dirs, files in os.walk(directory):
                    # Check for interruption
                    if self.is_interrupted:
                        return
                        
                    # Process folders
                    for dir_name in dirs:
                        # Check for interruption
                        if self.is_interrupted:
                            return
                            
                        dir_path = os.path.join(root, dir_name)
                        results['total_folders'] += 1
                        
                        # Add to file structure
                        parent_dir = os.path.dirname(dir_path)
                        if parent_dir in results['file_structure']:
                            try:
                                folder_info = {
                                    'path': dir_path,
                                    'name': dir_name
                                }
                                results['file_structure'][parent_dir]['folders'].append(folder_info)
                            except Exception as e:
                                logger.warning(f"Error adding folder {dir_path} to structure: {e}")
                    
                    # Process files
                    for file_name in files:
                        # Check for interruption
                        if self.is_interrupted:
                            return
                            
                        file_path = os.path.join(root, file_name)
                        
                        try:
                            file_size = os.path.getsize(file_path)
                        except Exception as e:
                            logger.warning(f"Could not get size for {file_path}: {e}")
                            file_size = 0
                        
                        # Update totals
                        results['total_files'] += 1
                        results['total_size'] += file_size
                        
                        # Add to file structure
                        parent_dir = os.path.dirname(file_path)
                        if parent_dir in results['file_structure']:
                            try:
                                file_info = {
                                    'path': file_path,
                                    'name': file_name,
                                    'size': file_size,
                                    'extension': os.path.splitext(file_name)[1],
                                    'issues': []
                                }
                                results['file_structure'][parent_dir]['files'].append(file_info)
                            except Exception as e:
                                logger.warning(f"Error adding file {file_path} to structure: {e}")
                        
                        # Update progress
                        file_count += 1
                        progress_percent = int((file_count / total_count) * 100)
                        self.progress_updated.emit(file_count, total_count)
                        
                        # Log progress at intervals
                        if file_count % 100 == 0:
                            logger.debug(f"Scanned {file_count} of {total_count} files ({progress_percent}%)")
                
                # Final progress update
                self.progress_updated.emit(file_count, total_count)
                logger.info(f"Directory scan complete: {file_count} files in {results['total_folders']} folders")
            except Exception as e:
                logger.error(f"Error during directory walk: {e}")
                error_msg = f"Error scanning directory {directory}: {str(e)}"
                self.error_occurred.emit(error_msg)
            
        except Exception as e:
            error_msg = f"Error scanning directory {directory}: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _analyze_results(self, results):
        """Analyze scan results to detect potential issues"""
        try:
            logger.info("Analyzing scan results...")
            
            # Import analyzers here to avoid circular imports
            try:
                from core.analyzers.name_validator import SharePointNameValidator
                from core.analyzers.path_analyzer import PathAnalyzer
                from core.analyzers.duplicate_finder import DuplicateFinder
                
                # Initialize analyzers
                name_validator = SharePointNameValidator()
                path_analyzer = PathAnalyzer()
                duplicate_finder = DuplicateFinder()
                
                # TODO: Implement actual analysis using the analyzers
                # This is where you would analyze the files and populate the issues
                
                # For now, just log a placeholder message
                logger.info("Analysis is a placeholder in this version")
                
            except ImportError as e:
                logger.warning(f"Could not import analyzer modules: {e}")
                logger.warning("Skipping detailed analysis")
                
            # Even if detailed analysis fails, basic issue detection can be done
            # Add basic path length detection example
            for dir_path, dir_data in results.get('file_structure', {}).items():
                for file_info in dir_data.get('files', []):
                    file_path = file_info.get('path', '')
                    # Detect path length issues (SharePoint limit is 256)
                    if len(file_path) > 256:
                        if 'path_length_issues' not in results:
                            results['path_length_issues'] = {}
                        results['path_length_issues'][file_path] = len(file_path)
                        results['total_issues'] += 1
            
            logger.info(f"Analysis completed with {results['total_issues']} issues detected")
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            # Don't emit error, we still want to return the scanned files
            # Just log it and continue with the raw scan results
    
    def requestInterruption(self):
        """Override to set our own flag and call the parent method"""
        logger.info("Scan interruption requested")
        self.is_interrupted = True
        super().requestInterruption()


# Create alias for compatibility with existing code
FileSystemScanner = Scanner