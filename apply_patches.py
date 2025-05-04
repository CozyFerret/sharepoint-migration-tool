#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
App patch for SharePoint Migration Tool
This script applies patches to fix common crashes in the application.
"""

import os
import sys
import logging
import importlib
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('app_patch')

def patch_main_window():
    """Patch the MainWindow class to fix signal-slot issues"""
    try:
        from ui.main_window import MainWindow
        
        # Store original methods
        original_scan_completed = MainWindow._scan_completed
        original_browse_source = MainWindow._browse_source
        original_start_scan = MainWindow._start_scan
        
        # Patch the methods
        def patched_scan_completed(self, scan_data):
            """Patched method with additional error handling"""
            try:
                logger.info("Running patched _scan_completed")
                if scan_data is None:
                    logger.warning("Scan data is None, creating empty dict")
                    scan_data = {}
                
                # Call original method
                return original_scan_completed(self, scan_data)
            except Exception as e:
                logger.error(f"Error in _scan_completed: {e}")
                logger.error(traceback.format_exc())
                self.statusBar().showMessage("Error processing scan results")
                self._reset_ui_after_operation()
        
        def patched_browse_source(self):
            """Patched method with additional validation"""
            try:
                logger.info("Running patched _browse_source")
                folder = None
                try:
                    from PyQt5.QtWidgets import QFileDialog
                    folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
                except Exception as dialog_error:
                    logger.error(f"Error in file dialog: {dialog_error}")
                    return
                
                if folder:
                    # Verify folder exists and is accessible
                    if not os.path.exists(folder):
                        self._show_error("Error", f"Selected folder does not exist: {folder}")
                        return
                    
                    if not os.path.isdir(folder):
                        self._show_error("Error", f"Selected path is not a directory: {folder}")
                        return
                    
                    if not os.access(folder, os.R_OK):
                        self._show_error("Error", f"No read permission for folder: {folder}")
                        return
                    
                    # Update UI with validated folder
                    self.source_folder = folder
                    self.source_label.setText(f"Source: {folder}")
                    self.scan_button.setEnabled(True)
                    self.statusBar().showMessage(f"Selected source folder: {folder}")
                    logger.info(f"Selected source folder: {folder}")
            except Exception as e:
                logger.error(f"Error in _browse_source: {e}")
                logger.error(traceback.format_exc())
        
        def patched_start_scan(self):
            """Patched method with additional error handling"""
            try:
                logger.info("Running patched _start_scan")
                
                if not self.source_folder:
                    self._show_error("Error", "No source folder selected")
                    return
                
                # Validate folder one more time
                if not os.path.exists(self.source_folder) or not os.path.isdir(self.source_folder):
                    self._show_error("Error", f"Invalid source folder: {self.source_folder}")
                    return
                
                # Update UI state
                self.scan_button.setEnabled(False)
                self.browse_button.setEnabled(False)
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                self.stop_button.setVisible(True)
                self.is_scanning = True
                self.statusBar().showMessage("Scanning...")
                
                # Define callbacks
                def safe_scan_progress(current, total):
                    try:
                        self._scan_progress(current, total)
                    except Exception as progress_error:
                        logger.error(f"Error in scan progress callback: {progress_error}")
                
                def safe_scan_completed(scan_data):
                    try:
                        self._scan_completed(scan_data)
                    except Exception as complete_error:
                        logger.error(f"Error in scan completed callback: {complete_error}")
                        self._reset_ui_after_operation()
                        self.statusBar().showMessage("Error processing scan results")
                
                def safe_scan_error(error_message):
                    try:
                        self._scan_error(error_message)
                    except Exception as error_handler_error:
                        logger.error(f"Error in scan error callback: {error_handler_error}")
                        self._reset_ui_after_operation()
                        self.statusBar().showMessage("Scan failed")
                
                callbacks = {
                    'progress': safe_scan_progress,
                    'scan_completed': safe_scan_completed,
                    'error': safe_scan_error
                }
                
                # Start the scan with protection
                try:
                    self.data_processor.start_scan(self.source_folder, None, callbacks)
                    logger.info(f"Scan started for {self.source_folder}")
                except Exception as start_error:
                    logger.error(f"Error starting scan: {start_error}")
                    logger.error(traceback.format_exc())
                    self._show_error("Scan Error", f"Could not start scan: {str(start_error)}")
                    self._reset_ui_after_operation()
                
            except Exception as e:
                logger.error(f"Error in _start_scan: {e}")
                logger.error(traceback.format_exc())
                try:
                    self._show_error("Error", f"Error starting scan: {str(e)}")
                    self._reset_ui_after_operation()
                except:
                    # Last resort
                    pass
        
        # Apply the patches
        MainWindow._scan_completed = patched_scan_completed
        MainWindow._browse_source = patched_browse_source
        MainWindow._start_scan = patched_start_scan
        
        logger.info("Successfully patched MainWindow")
        return True
    except ImportError as ie:
        logger.error(f"Could not import MainWindow: {ie}")
        return False
    except Exception as e:
        logger.error(f"Error patching MainWindow: {e}")
        logger.error(traceback.format_exc())
        return False

def patch_scanner():
    """Patch the Scanner class to fix scanning issues"""
    try:
        from core.scanner import Scanner, FileSystemScanner
        
        # Store original methods
        original_scan = Scanner.scan
        original_run = Scanner.run
        
        # Patch the methods
        def patched_scan(self):
            """Patched method with additional error handling"""
            try:
                logger.info(f"Running patched scan method for {self.source_folder}")
                
                # Verify source folder exists
                if not self.source_folder or not os.path.exists(self.source_folder):
                    error_msg = f"Invalid source folder: {self.source_folder}"
                    logger.error(error_msg)
                    self.error_occurred.emit(error_msg)
                    return {}
                
                # Don't start if already running
                if self.isRunning():
                    logger.warning("Scanner thread is already running")
                    return {}
                
                # Start the thread which will run the 'run' method
                self.start()
                return {}
            except Exception as e:
                logger.error(f"Error in scanner.scan: {e}")
                logger.error(traceback.format_exc())
                try:
                    self.error_occurred.emit(f"Error starting scan: {str(e)}")
                except:
                    logger.error("Could not emit error signal")
                return {}
        
        def patched_run(self):
            """Patched method with additional error handling"""
            try:
                logger.info(f"Scanner thread started for {self.source_folder}")
                
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
                
                # Scan with error handling
                try:
                    # Scan directory recursively
                    self._scan_directory(self.source_folder, results)
                except Exception as scan_error:
                    logger.error(f"Error in _scan_directory: {scan_error}")
                    logger.error(traceback.format_exc())
                    error_msg = f"Error during folder scan: {str(scan_error)}"
                    self.error_occurred.emit(error_msg)
                    return
                
                # Only analyze and emit results if not interrupted
                if not self.is_interrupted:
                    try:
                        # Analyze results
                        self._analyze_results(results)
                    except Exception as analyze_error:
                        logger.error(f"Error in _analyze_results: {analyze_error}")
                        logger.error(traceback.format_exc())
                        # Continue with unanalyzed results
                    
                    # Emit completion signal with results
                    logger.info("Scan completed successfully, emitting results")
                    try:
                        self.scan_completed.emit(results)
                    except Exception as emit_error:
                        logger.error(f"Error emitting scan_completed signal: {emit_error}")
                        logger.error(traceback.format_exc())
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
                try:
                    self.error_occurred.emit(f"Error during scan: {str(e)}")
                except Exception as signal_error:
                    logger.error(f"Error emitting error signal: {signal_error}")
        
        # Apply the patches
        Scanner.scan = patched_scan
        Scanner.run = patched_run
        
        logger.info("Successfully patched Scanner")
        return True
    except ImportError as ie:
        logger.error(f"Could not import Scanner: {ie}")
        return False
    except Exception as e:
        logger.error(f"Error patching Scanner: {e}")
        logger.error(traceback.format_exc())
        return False

def apply_patches():
    """Apply all patches"""
    results = []
    
    # Patch MainWindow
    results.append(("MainWindow", patch_main_window()))
    
    # Patch Scanner
    results.append(("Scanner", patch_scanner()))
    
    # TODO: Add more patches as needed
    
    # Print results
    logger.info("Patch application results:")
    for component, success in results:
        logger.info(f"  {component}: {'Success' if success else 'Failed'}")
    
    return all(success for _, success in results)

if __name__ == "__main__":
    print("Applying patches to SharePoint Migration Tool...")
    success = apply_patches()
    
    if success:
        print("Patches applied successfully!")
        print("Run main.py to start the application with the fixes.")
    else:
        print("Some patches failed to apply. Check the logs for details.")
        print("You may still try running main.py, but the application might still crash.")