#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File system scanner for SharePoint Data Migration Cleanup Tool.
Recursively scans directories and collects file metadata.
"""

import os
import hashlib
import time
import logging
import pathlib
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import pandas as pd

logger = logging.getLogger('sharepoint_migration_tool')

class ScannerWorker(QObject):
    """Worker thread for scanning the file system"""
    
    # Define signals
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal(object)
    
    def __init__(self, root_path, scan_options):
        """
        Initialize the scanner worker
        
        Args:
            root_path (str): The root path to scan
            scan_options (dict): Options controlling the scan behavior
        """
        super().__init__()
        self.root_path = root_path
        self.scan_options = scan_options
        self.should_stop = False
        
    def stop(self):
        """Signal the worker to stop scanning"""
        self.should_stop = True
        
    def calculate_file_hash(self, file_path):
        """
        Calculate SHA-256 hash of a file
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: The hexadecimal hash of the file
        """
        if not self.scan_options.get('calculate_hashes', False):
            return ""
            
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Read the file in chunks to avoid loading large files into memory
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Error calculating hash for {file_path}: {e}")
            return ""
        
    def scan(self):
        """
        Scan the file system starting from the root path
        
        Emits:
            progress: Percentage completion
            status: Current status message
            error: Error message if any
            finished: The scan results as a pandas DataFrame
        """
        try:
            start_time = time.time()
            self.status.emit(f"Starting scan at {self.root_path}")
            
            # Check if the root path exists
            if not os.path.exists(self.root_path):
                self.error.emit(f"Path does not exist: {self.root_path}")
                return
                
            # Count total number of files for progress reporting
            total_files = 0
            if self.scan_options.get('calculate_total_files', True):
                self.status.emit("Counting files...")
                for _, _, files in os.walk(self.root_path):
                    total_files += len(files)
                    # Check if we should stop
                    if self.should_stop:
                        self.status.emit("Scan cancelled")
                        return
                self.status.emit(f"Found {total_files} files to scan")
            
            # Initialize results list
            results = []
            processed_files = 0
            
            # Traverse the file system
            self.status.emit(f"Scanning files...")
            for root, dirs, files in os.walk(self.root_path):
                # Check if we should stop
                if self.should_stop:
                    self.status.emit("Scan cancelled")
                    break
                    
                # Process each file
                for file in files:
                    # Check if we should stop
                    if self.should_stop:
                        break
                        
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.root_path)
                    
                    try:
                        # Get file stats
                        stats = os.stat(full_path)
                        file_size = stats.st_size
                        created_time = datetime.fromtimestamp(stats.st_ctime)
                        modified_time = datetime.fromtimestamp(stats.st_mtime)
                        
                        # Get extension
                        _, extension = os.path.splitext(file)
                        extension = extension.lower()
                        
                        # Calculate hash if needed
                        file_hash = ""
                        if self.scan_options.get('calculate_hashes', False):
                            file_hash = self.calculate_file_hash(full_path)
                        
                        # Add file to results
                        results.append({
                            'path': full_path,
                            'relative_path': relative_path,
                            'parent_folder': os.path.basename(root),
                            'name': file,
                            'extension': extension,
                            'size': file_size,
                            'created': created_time,
                            'modified': modified_time,
                            'path_length': len(full_path),
                            'hash': file_hash
                        })
                        
                        # Update progress
                        processed_files += 1
                        if total_files > 0:
                            progress_percent = int((processed_files / total_files) * 100)
                            self.progress.emit(progress_percent)
                        
                        # Status update every 100 files
                        if processed_files % 100 == 0:
                            self.status.emit(f"Processed {processed_files} files...")
                            
                    except Exception as e:
                        logger.warning(f"Error processing file {full_path}: {e}")
            
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            
            # Scan completion
            end_time = time.time()
            scan_time = end_time - start_time
            self.status.emit(f"Scan complete. Processed {len(df)} files in {scan_time:.2f} seconds")
            
            # Emit the results
            self.finished.emit(df)
            
        except Exception as e:
            logger.error(f"Error during file scan: {e}")
            self.error.emit(f"Scan error: {str(e)}")

class FileSystemScanner:
    """Main scanner class that manages scanning operations"""
    
    def __init__(self):
        """Initialize the scanner"""
        self.worker = None
        self.thread = None
        self.results = None
        
    def start_scan(self, root_path, scan_options=None, progress_callback=None, 
                   status_callback=None, error_callback=None, finished_callback=None):
        """
        Start scanning a directory
        
        Args:
            root_path (str): The root path to scan
            scan_options (dict): Options controlling scan behavior
            progress_callback (function): Callback for progress updates
            status_callback (function): Callback for status messages
            error_callback (function): Callback for error messages
            finished_callback (function): Callback for scan completion
        """
        # Default scan options
        if scan_options is None:
            scan_options = {
                'calculate_hashes': True,
                'calculate_total_files': True
            }
            
        # Create worker thread
        self.thread = QThread()
        self.worker = ScannerWorker(root_path, scan_options)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.scan)
        
        if progress_callback:
            self.worker.progress.connect(progress_callback)
            
        if status_callback:
            self.worker.status.connect(status_callback)
            
        if error_callback:
            self.worker.error.connect(error_callback)
            
        # Connect the finished signal
        def on_finished(results):
            self.results = results
            self.thread.quit()
            if finished_callback:
                finished_callback(results)
                
        self.worker.finished.connect(on_finished)
        
        # Start the thread
        logger.info(f"Starting scan of {root_path}")
        self.thread.start()
        
    def stop_scan(self):
        """Stop an ongoing scan"""
        if self.worker and self.thread and self.thread.isRunning():
            logger.info("Stopping scan")
            self.worker.stop()
            
    def get_results(self):
        """
        Get the scan results
        
        Returns:
            pandas.DataFrame: The scan results
        """
        return self.results