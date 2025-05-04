#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main window for the SharePoint Data Migration Cleanup Tool.
Implements the primary user interface.
"""

import os
import sys
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QFileDialog, QTabWidget,
                           QCheckBox, QProgressBar, QStatusBar, QMessageBox,
                           QSplitter, QApplication)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from utils.memory_cleanup import cleanup_on_exit, clear_all_sensitive_data
from ui.dashboard import DashboardWidget
from ui.analyzer_widget import AnalyzerWidget
from ui.results_widget import ResultsWidget
from ui.export_widget import ExportWidget
from ui.cleanup_widget import CleanupWidget

logger = logging.getLogger('sharepoint_migration_tool')

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config=None, data_processor=None):
        """
        Initialize the main window
        
        Args:
            config (dict): Application configuration
            data_processor (DataProcessor): Data processor instance
        """
        super().__init__()
        
        self.config = config or {}
        self.data_processor = data_processor
        
        # Set up the UI
        self.init_ui()
        
        logger.info("Main window initialized")
        
    def init_ui(self):
        """Set up the user interface"""
        # Configure window
        self.setWindowTitle("SharePoint Data Migration Cleanup Tool")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create header section with scan controls
        header_layout = QHBoxLayout()
        
        # Folder selection
        self.path_label = QLabel("Select folder to analyze:")
        header_layout.addWidget(self.path_label)
        
        self.path_display = QLabel("No folder selected")
        self.path_display.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        header_layout.addWidget(self.path_display, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_folder)
        header_layout.addWidget(self.browse_button)
        
        # Add header to main layout
        main_layout.addLayout(header_layout)
        
        # Feature toggle section
        feature_layout = QHBoxLayout()
        feature_layout.setContentsMargins(0, 10, 0, 10)
        
        # Create checkboxes for each feature
        self.name_check = QCheckBox("Name Validation")
        self.name_check.setChecked(self.config.get('features', {}).get('name_validation', True))
        feature_layout.addWidget(self.name_check)
        
        self.path_check = QCheckBox("Path Length")
        self.path_check.setChecked(self.config.get('features', {}).get('path_length', True))
        feature_layout.addWidget(self.path_check)
        
        self.duplicate_check = QCheckBox("Duplicate Detection")
        self.duplicate_check.setChecked(self.config.get('features', {}).get('duplicate_detection', True))
        feature_layout.addWidget(self.duplicate_check)
        
        self.pii_check = QCheckBox("PII Detection (Placeholder - Coming Soon)")
        self.pii_check.setChecked(self.config.get('features', {}).get('pii_detection', True))
        self.pii_check.setEnabled(True)  # Keep enabled to pass to analyzer
        feature_layout.addWidget(self.pii_check)
        
        # Add scan button
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setEnabled(False)  # Disabled until a folder is selected
        self.scan_button.clicked.connect(self.start_scan)
        feature_layout.addWidget(self.scan_button)
        
        # Add stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scan)
        feature_layout.addWidget(self.stop_button)
        
        # Add feature layout to main layout
        main_layout.addLayout(feature_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Create tab widget for different views
        self.tabs = QTabWidget()
        
        # Create and add tab widgets
        self.dashboard_widget = DashboardWidget()
        self.tabs.addTab(self.dashboard_widget, "Dashboard")
        
        self.analyzer_widget = AnalyzerWidget(self.config)
        self.tabs.addTab(self.analyzer_widget, "Analysis")
        
        self.results_widget = ResultsWidget()
        self.tabs.addTab(self.results_widget, "Results")
        
        self.export_widget = ExportWidget()
        self.tabs.addTab(self.export_widget, "Export")
        
        self.cleanup_widget = CleanupWidget(self.config)
        self.tabs.addTab(self.cleanup_widget, "Cleanup")
        
        # Add tabs to main layout
        main_layout.addWidget(self.tabs, 1)  # 1 = stretch factor
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def browse_folder(self):
        """Open file dialog to select a folder to scan"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Analyze")
        if folder:
            self.path_display.setText(folder)
            self.scan_button.setEnabled(True)
            logger.info(f"Selected folder: {folder}")
            
    def start_scan(self):
        """Start the scanning process"""
        folder_path = self.path_display.text()
        if not folder_path or folder_path == "No folder selected":
            QMessageBox.warning(self, "Error", "Please select a folder to scan.")
            return
            
        # Update UI state
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Scanning...")
        
        # Get selected features
        scan_options = {
            'calculate_hashes': self.duplicate_check.isChecked(),
            'calculate_total_files': True,
            'features': {
                'name_validation': self.name_check.isChecked(),
                'path_length': self.path_check.isChecked(),
                'duplicate_detection': self.duplicate_check.isChecked(),
                'pii_detection': self.pii_check.isChecked()
            }
        }
        
        # Set up callbacks
        callbacks = {
            'progress': self.update_progress,
            'status': self.update_status,
            'error': self.handle_error,
            'scan_completed': self.scan_completed
        }
        
        # Start the scan
        logger.info(f"Starting scan of {folder_path} with options: {scan_options}")
        self.data_processor.start_scan(folder_path, scan_options, callbacks)
        
    def stop_scan(self):
        """Stop the current scan"""
        self.data_processor.stop_scanning()
        self.status_bar.showMessage("Stopping scan...")
        self.stop_button.setEnabled(False)
        
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Update the status bar"""
        self.status_bar.showMessage(message)
        
    def handle_error(self, error_message):
        """Handle errors during scanning"""
        QMessageBox.critical(self, "Error", error_message)
        self.status_bar.showMessage("Error: " + error_message)
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def scan_completed(self, results):
        """Handle scan completion"""
        # Update UI state
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Scan complete")
        
        # Analyze the data
        feature_flags = {
            'name_validation': self.name_check.isChecked(),
            'path_length': self.path_check.isChecked(),
            'duplicate_detection': self.duplicate_check.isChecked(),
            'pii_detection': self.pii_check.isChecked()
        }
        
        callbacks = {
            'analysis_completed': self.analysis_completed
        }
        
        # Start the analysis
        self.data_processor.analyze_data(feature_flags, callbacks)
        
    def analysis_completed(self, analysis_results):
        """Handle analysis completion"""
        # Update tabs with the results
        self.dashboard_widget.update_data(self.data_processor.get_scan_data())
        self.results_widget.update_data(analysis_results)
        self.export_widget.set_data(analysis_results)
        self.cleanup_widget.set_analysis_results(analysis_results)
        
        # Switch to dashboard tab
        self.tabs.setCurrentIndex(0)
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Clean up resources
        scan_data = self.data_processor.get_scan_data()
        analysis_results = self.data_processor.get_analysis_results()
        
        if scan_data is not None:
            clear_all_sensitive_data({'scan_data': scan_data})
            
        if analysis_results:
            clear_all_sensitive_data({'analysis_results': analysis_results})
            
        cleanup_on_exit()
        logger.info("Application closed")
        event.accept()