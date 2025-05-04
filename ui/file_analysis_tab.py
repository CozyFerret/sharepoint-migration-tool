"""
File Analysis Tab for SharePoint Migration Tool

This module provides a tab for detailed file-level analysis in the SharePoint Migration Tool.
"""

import os
import logging
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFileDialog,
                             QProgressBar, QMessageBox, QLineEdit,
                             QSplitter, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt, QSettings

# Import the file analysis view
from ui.file_analysis_view import FileAnalysisView

# Import the file system scanner
from core.file_scanner import FileSystemScanner

logger = logging.getLogger(__name__)

class FileAnalysisTab(QWidget):
    """
    Tab for detailed file-level analysis in the SharePoint Migration Tool.
    """
    
    def __init__(self, parent=None):
        super(FileAnalysisTab, self).__init__(parent)
        
        # Initialize scanner
        self.scanner = FileSystemScanner()
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Source selection area
        source_layout = QHBoxLayout()
        
        source_label = QLabel("Source Directory:")
        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(True)
        self.source_edit.setPlaceholderText("Select a directory to scan...")
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.select_source)
        
        scan_btn = QPushButton("Start Scan")
        scan_btn.clicked.connect(self.start_scan)
        
        # Scan options checkboxes
        check_naming = QCheckBox("Check Naming")
        check_naming.setChecked(True)
        check_naming.setToolTip("Verify filenames against SharePoint naming rules")
        
        check_path_length = QCheckBox("Check Path Length")
        check_path_length.setChecked(True)
        check_path_length.setToolTip("Verify file paths against SharePoint path length limits")
        
        check_duplicates = QCheckBox("Find Duplicates")
        check_duplicates.setChecked(True)
        check_duplicates.setToolTip("Identify duplicate files based on content")
        
        # Add widgets to source layout
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_edit, 1)  # 1 = stretch factor
        source_layout.addWidget(browse_btn)
        source_layout.addWidget(check_naming)
        source_layout.addWidget(check_path_length)
        source_layout.addWidget(check_duplicates)
        source_layout.addWidget(scan_btn)
        
        main_layout.addLayout(source_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # File analysis view
        self.file_analysis_view = FileAnalysisView()
        main_layout.addWidget(self.file_analysis_view, 1)  # 1 = stretch factor
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Export button in the status bar
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        status_layout.addWidget(export_btn)
        
        main_layout.addLayout(status_layout)
    
    def select_source(self):
        """Select source directory for scanning."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Source Directory", "", QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.source_edit.setText(folder)
    
    def start_scan(self):
        """Start scanning the selected directory."""
        source_dir = self.source_edit.text()
        if not source_dir:
            QMessageBox.warning(self, "Error", "Please select a source directory first.")
            return
        
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Scanning files...")
        
        # Define callbacks
        def progress_callback(current, total):
            if total > 0:
                percentage = int((current / total) * 100)
                self.progress_bar.setValue(percentage)
        
        def scan_completed_callback(results):
            self.progress_bar.setVisible(False)
            
            if not results:
                self.status_label.setText("Scan failed or no results")
                return
            
            # Get DataFrames from scanner
            files_df, issues_df = self.scanner.get_results_as_dataframes()
            
            # Update the file analysis view
            self.file_analysis_view.set_data(files_df, issues_df)
            
            # Update status with scan summary
            total_files = results.get('total_files', 0)
            total_issues = results.get('total_issues', 0)
            self.status_label.setText(
                f"Scan complete: {total_files} files scanned, {total_issues} issues found"
            )
        
        def error_callback(error_message):
            self.progress_bar.setVisible(False)
            self.status_label.setText("Scan failed")
            QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning: {error_message}")
        
        # Start scan with callbacks
        try:
            self.scanner.scan_directory(
                source_dir,
                callbacks={
                    'progress': progress_callback,
                    'scan_completed': scan_completed_callback,
                    'error': error_callback
                }
            )
        except Exception as e:
            error_callback(str(e))
    
    def export_results(self):
        """Export the scan results."""
        # Use the export functionality in the file analysis view
        self.file_analysis_view.show_export_menu()
    
    def update_with_results(self, results):
        """
        Update the tab with scan results from another tab.
        
        Args:
            results (dict): Scan results dictionary
        """
        if not results:
            return
        
        # Convert results to DataFrames if needed
        files_df = None
        issues_df = None
        
        if 'files_df' in results:
            files_df = results['files_df']
        elif 'files' in results and isinstance(results['files'], list):
            files_df = pd.DataFrame(results['files'])
        
        if 'issues_df' in results:
            issues_df = results['issues_df']
        elif 'issues' in results and isinstance(results['issues'], list):
            issues_df = pd.DataFrame(results['issues'])
        
        # Update the file analysis view
        if files_df is not None:
            self.file_analysis_view.set_data(files_df, issues_df)
            
            # Update status with scan summary
            total_files = len(files_df)
            total_issues = len(issues_df) if issues_df is not None else 0
            self.status_label.setText(
                f"Data loaded: {total_files} files, {total_issues} issues"
            )