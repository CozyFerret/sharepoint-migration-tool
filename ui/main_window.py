"""
Main Window for SharePoint Migration Tool

This module provides the main application window with integrated settings.
"""

import sys
import os
import logging
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QStatusBar, 
                           QProgressBar, QMessageBox, QTabWidget,
                           QAction, QMenu, QMenuBar, QLineEdit)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QIcon

# Import UI components
from ui.dashboard import DashboardWidget
from ui.enhanced_data_view import EnhancedDataView
from ui.file_analysis_tab import FileAnalysisTab
from ui.migration_tab import MigrationTab
from ui.settings_widget import SettingsWidget

# Import core components
from core.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main window for SharePoint Data Migration Cleanup Tool with integrated settings."""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("SharePoint Migration Tool")
        self.setMinimumSize(1000, 700)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.layout = QVBoxLayout(self.central_widget)
        
        # Initialize data processor
        self.data_processor = DataProcessor()
        
        # Create menus
        self.create_menus()
        
        # Add header section
        self.add_header()
        
        # Setup tabs
        self.setup_tabs()
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progress_bar)
        self.statusBar.showMessage("Ready")
        
        # Initialize scan results
        self.scan_results = None
        
        # Load settings
        self.load_settings()
    
    def add_header(self):
        """Add header section with title and controls"""
        header_layout = QHBoxLayout()
        
        # Add title
        title = QLabel("SharePoint Migration Tool")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Add version info
        version_label = QLabel("v1.2.0")
        version_font = QFont()
        version_font.setItalic(True)
        version_label.setFont(version_font)
        
        # Add source selection
        source_label = QLabel("Source:")
        self.source_path = QLabel("Not selected")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_source)
        
        # Add scan button
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setEnabled(False)
        self.scan_button.clicked.connect(self.start_scan)
        
        # Add widgets to layout
        header_layout.addWidget(title)
        header_layout.addWidget(version_label)
        header_layout.addStretch()
        header_layout.addWidget(source_label)
        header_layout.addWidget(self.source_path)
        header_layout.addWidget(browse_button)
        header_layout.addWidget(self.scan_button)
        
        # Add to main layout
        self.layout.addLayout(header_layout)
        
    def setup_tabs(self):
        """Set up the tab widget with various tabs including settings"""
        self.tabs = QTabWidget()
        
        # Create and add the Dashboard tab
        self.dashboard_tab = DashboardWidget()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Add Analysis tab with enhanced data view
        self.analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(self.analysis_tab)
        self.enhanced_view = EnhancedDataView()
        analysis_layout.addWidget(self.enhanced_view)
        self.tabs.addTab(self.analysis_tab, "Analysis")
        
        # Add File Analysis tab
        self.file_analysis_tab = FileAnalysisTab()
        self.tabs.addTab(self.file_analysis_tab, "File Analysis")
        
        # Add Migration tab with updated version
        self.migration_tab = MigrationTab()
        self.tabs.addTab(self.migration_tab, "Migration")
        
        # Add Settings tab
        self.settings_tab = QWidget()
        settings_layout = QVBoxLayout(self.settings_tab)
        self.settings_widget = SettingsWidget()
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        settings_layout.addWidget(self.settings_widget)
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Add tabs to main layout
        self.layout.addWidget(self.tabs, 1)  # 1 = stretch factor
        
    def create_menus(self):
        """Create application menus"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open Source Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.browse_source)
        file_menu.addAction(open_action)
        
        export_action = QAction("&Export Report...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")
        
        scan_action = QAction("&Scan Files", self)
        scan_action.triggered.connect(self.start_scan)
        tools_menu.addAction(scan_action)
        
        clean_action = QAction("&Clean Files", self)
        clean_action.triggered.connect(self.go_to_migration)
        tools_menu.addAction(clean_action)
        
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.go_to_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def browse_source(self):
        """Browse for source folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Source Folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.source_path.setText(folder)
            self.scan_button.setEnabled(True)
            
            # Update source in other tabs
            if hasattr(self.file_analysis_tab, 'source_edit'):
                self.file_analysis_tab.source_edit.setText(folder)
            
            if hasattr(self.migration_tab, 'source_edit'):
                self.migration_tab.source_edit.setText(folder)
    
    def start_scan(self):
        """Start scanning process"""
        source = self.source_path.text()
        if source == "Not selected":
            QMessageBox.warning(self, "Error", "Please select a source directory first.")
            return
        
        # Update UI
        self.scan_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.statusBar.showMessage(f"Scanning {source}...")
        
        # Define callbacks
        def progress_callback(current, total):
            if total > 0:
                percentage = int((current / total) * 100)
                self.progress_bar.setValue(percentage)
        
        def completion_callback(results):
            self.scan_results = results
            self.progress_bar.setVisible(False)
            self.scan_button.setEnabled(True)
            self.statusBar.showMessage("Scan completed")
            
            # Processing results to ensure consistent format for all UI components
            try:
                # Convert results to dictionary if it's a DataFrame
                if isinstance(results, pd.DataFrame):
                    processed_results = {
                        'total_files': len(results),
                        'total_folders': 0,  # Can't determine from just the DataFrame
                        'total_size': results['size'].sum() if 'size' in results.columns else 0,
                        'scan_data': results,
                        'files_df': results  # Add this for components that expect this key
                    }
                    
                    # Extract file types from extensions
                    if 'extension' in results.columns:
                        processed_results['file_types'] = results['extension'].value_counts().to_dict()
                    else:
                        # Create file types from filenames
                        file_types = {}
                        for _, row in results.iterrows():
                            filename = row.get('filename', '') or row.get('name', '')
                            ext = os.path.splitext(filename)[1].lower() or ''
                            if ext not in file_types:
                                file_types[ext] = 0
                            file_types[ext] += 1
                        processed_results['file_types'] = file_types
                    
                    # Create path length distribution
                    if 'path_length' in results.columns:
                        bins = {50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0}
                        for length in results['path_length']:
                            for bin_val in sorted(bins.keys()):
                                if length <= bin_val:
                                    bins[bin_val] += 1
                                    break
                        processed_results['path_length_distribution'] = bins
                    else:
                        processed_results['path_length_distribution'] = {50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0}
                else:
                    processed_results = results
                    # Make sure we have scan_data and files_df keys for consistency
                    if 'scan_data' not in processed_results and 'files_df' in processed_results:
                        processed_results['scan_data'] = processed_results['files_df']
                    elif 'files_df' not in processed_results and 'scan_data' in processed_results:
                        processed_results['files_df'] = processed_results['scan_data']
                
                # Update the dashboard with the processed results
                self.dashboard_tab.update_with_results(processed_results)
                
                # Update analysis tab
                if hasattr(self.analysis_tab, 'update_data_view'):
                    self.analysis_tab.update_data_view(processed_results)
                
                # Update File Analysis tab
                if hasattr(self.file_analysis_tab, 'update_with_results'):
                    self.file_analysis_tab.update_with_results(processed_results)
                
                # Switch to dashboard tab
                self.tabs.setCurrentIndex(0)
            
            except Exception as e:
                logging.error(f"Error processing scan results: {str(e)}")
                QMessageBox.warning(self, "Error", f"Error processing scan results: {str(e)}")
        
        def error_callback(error_msg):
            self.progress_bar.setVisible(False)
            self.scan_button.setEnabled(True)
            self.statusBar.showMessage("Scan failed")
            QMessageBox.critical(self, "Error", f"Failed to start scan: {error_msg}")
        
        # Start scan with callbacks
        try:
            self.data_processor.start_scan(
                source,
                callbacks={
                    'progress': progress_callback,
                    'scan_completed': completion_callback,
                    'error': error_callback
                }
            )
            
        except Exception as e:
            error_callback(str(e))
    
    def export_report(self):
        """Export the current scan results"""
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 1 and hasattr(self, 'enhanced_view'):
            # Analysis tab export
            self.enhanced_view.export_data()
        elif current_tab == 2 and hasattr(self.file_analysis_tab, 'export_results'):
            # File Analysis tab export
            self.file_analysis_tab.export_results()
        else:
            QMessageBox.information(self, "Export", "No data available to export or export not supported in this tab.")
    
    def go_to_settings(self):
        """Switch to the Settings tab"""
        self.tabs.setCurrentIndex(4)  # Assuming Settings is the fifth tab
    
    def go_to_migration(self):
        """Switch to the Migration tab"""
        self.tabs.setCurrentIndex(3)  # Assuming Migration is the fourth tab
    
    def on_settings_changed(self, settings):
        """Handle settings changes from settings widget"""
        # Pass settings to the migration tab
        if hasattr(self.migration_tab, 'on_settings_changed'):
            self.migration_tab.on_settings_changed(settings)
        
        # Store settings
        self.current_settings = settings
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About SharePoint Migration Tool",
            "<h2>SharePoint Migration Tool</h2>"
            "<p>Version 1.2.0</p>"
            "<p>A tool for cleaning and preparing file systems for SharePoint migration.</p>"
            "<p>Added new features:</p>"
            "<ul>"
            "<li>Destructive/Non-destructive operation modes</li>"
            "<li>Direct SharePoint upload option</li>"
            "<li>Advanced settings management</li>"
            "</ul>"
            "<p>© 2025 Shareit</p>"
        )
    
    def load_settings(self):
        """Load application settings"""
        settings = QSettings()
        geometry = settings.value("MainWindow/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Get current settings from settings widget
        if hasattr(self, 'settings_widget'):
            self.current_settings = self.settings_widget.get_current_settings()
    
    def save_settings(self):
        """Save application settings"""
        settings = QSettings()
        settings.setValue("MainWindow/geometry", self.saveGeometry())
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, "Exit Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Save settings
            self.save_settings()
            event.accept()
        else:
            event.ignore()