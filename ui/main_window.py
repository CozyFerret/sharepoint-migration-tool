#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main window implementation for SharePoint Migration Tool.
Contains the main application window and controller logic.

This implementation includes robust error handling to avoid crashes
and gracefully degrade when components are unavailable.
"""

import os
import sys
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QFileDialog, QLabel, 
    QProgressBar, QMessageBox, QComboBox, QCheckBox,
    QGroupBox, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal

# Configure logger
logger = logging.getLogger('sharepoint_migration_tool')

class MainWindow(QMainWindow):
    """
    Main application window for SharePoint Migration Tool.
    Integrates scanning, analysis, and cleaning operations.
    """
    
    def __init__(self):
        """Initialize the main window and UI components"""
        super().__init__()
        logger.info("Initializing MainWindow")
        
        # Set basic window properties
        self.setWindowTitle("SharePoint Migration Tool")
        self.setMinimumSize(1000, 700)
        
        # Initialize core components with proper error handling
        try:
            self._init_core_components()
        except Exception as e:
            logger.error(f"Error initializing core components: {e}")
            self._show_critical_error("Error initializing application", str(e))
            
            # Create fallback components to prevent further crashes
            self._create_fallback_components()
        
        # Initialize state variables
        self.source_folder = None
        self.output_folder = None
        self.is_scanning = False
        self.is_cleaning = False
        
        # Set up the UI with proper error handling
        try:
            self._setup_ui()
            logger.info("MainWindow UI setup complete")
        except Exception as e:
            logger.error(f"Error setting up UI: {e}")
            self._show_critical_error("Error setting up UI", str(e))
            
            # Create a minimal UI to avoid crashes
            self._create_minimal_ui()
    
    def _init_core_components(self):
        """Initialize core components with proper error handling"""
        logger.info("Initializing core components")
        
        # Import core components with error handling
        try:
            from core.data_processor import DataProcessor
            self.data_processor = DataProcessor()
            logger.info("DataProcessor initialized")
        except Exception as e:
            logger.error(f"Error initializing DataProcessor: {e}")
            raise
        
        # Connect to the progress signal with error handling
        try:
            self.data_processor.progress_updated.connect(self._update_progress)
            logger.info("Progress signal connected")
        except Exception as e:
            logger.error(f"Error connecting to progress signal: {e}")
    
    def _create_fallback_components(self):
        """Create fallback components to prevent crashes"""
        logger.info("Creating fallback components")
        
        # Create a dummy data processor
        class DummyDataProcessor:
            def __init__(self):
                self.progress_updated = DummySignal()
                
            def start_scan(self, *args, **kwargs):
                logger.warning("Using dummy start_scan")
                if 'callbacks' in kwargs and 'error' in kwargs['callbacks']:
                    kwargs['callbacks']['error']("Core components unavailable")
                    
            def analyze_data(self, *args, **kwargs):
                logger.warning("Using dummy analyze_data")
                if 'callbacks' in kwargs and 'error' in kwargs['callbacks']:
                    kwargs['callbacks']['error']("Core components unavailable")
                    
            def start_cleaning(self, *args, **kwargs):
                logger.warning("Using dummy start_cleaning")
                if 'callbacks' in kwargs and 'error' in kwargs['callbacks']:
                    kwargs['callbacks']['error']("Core components unavailable")
                    
            def get_scan_data(self):
                return None
                
            def get_analysis_results(self):
                return {}
                
            def stop_scanning(self):
                pass
                
            def stop_cleaning(self):
                pass
        
        class DummySignal:
            def connect(self, *args, **kwargs):
                pass
                
            def disconnect(self, *args, **kwargs):
                pass
                
            def emit(self, *args, **kwargs):
                pass
        
        self.data_processor = DummyDataProcessor()
        logger.info("Fallback components created")
    
    def _setup_ui(self):
        """Set up the user interface with error handling for each component"""
        logger.info("Setting up UI")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(central_widget)
        
        # Add toolbar
        self._create_toolbar()
        
        # Add tabs with error handling
        self._create_tabs()
        
        # Add status bar
        self.statusBar().showMessage("Ready")
    
    def _create_minimal_ui(self):
        """Create a minimal UI to avoid crashes"""
        logger.info("Creating minimal UI")
        
        # Clear existing widgets if any
        if hasattr(self, 'main_layout'):
            # Clear the layout
            while self.main_layout.count():
                item = self.main_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(central_widget)
        
        # Add error message
        error_label = QLabel("An error occurred during application initialization. Some features may be unavailable.")
        error_label.setStyleSheet("color: red; font-weight: bold;")
        self.main_layout.addWidget(error_label)
        
        # Add minimal controls
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_source)
        self.main_layout.addWidget(browse_button)
        
        # Add status bar
        self.statusBar().showMessage("Application initialized with errors")
    
    def _create_toolbar(self):
        """Create the application toolbar"""
        logger.info("Creating toolbar")
        
        try:
            # Toolbar layout
            toolbar_layout = QHBoxLayout()
            
            # Source folder selection
            self.source_label = QLabel("Source: Not selected")
            toolbar_layout.addWidget(self.source_label)
            
            # Browse button
            self.browse_button = QPushButton("Browse...")
            self.browse_button.clicked.connect(self._browse_source)
            toolbar_layout.addWidget(self.browse_button)
            
            # Scan button
            self.scan_button = QPushButton("Scan")
            self.scan_button.clicked.connect(self._start_scan)
            self.scan_button.setEnabled(False)
            toolbar_layout.addWidget(self.scan_button)
            
            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            toolbar_layout.addWidget(self.progress_bar)
            
            # Stop button
            self.stop_button = QPushButton("Stop")
            self.stop_button.clicked.connect(self._stop_operations)
            self.stop_button.setVisible(False)
            toolbar_layout.addWidget(self.stop_button)
            
            # Add to main layout
            self.main_layout.addLayout(toolbar_layout)
            
            logger.info("Toolbar created successfully")
        except Exception as e:
            logger.error(f"Error creating toolbar: {e}")
            # Create a minimal fallback toolbar
            fallback_layout = QHBoxLayout()
            fallback_layout.addWidget(QLabel("Error creating toolbar"))
            self.main_layout.addLayout(fallback_layout)
    
    def _create_tabs(self):
        """Create the application tabs with proper error handling"""
        logger.info("Creating tabs")
        
        try:
            # Create tab widget
            self.tabs = QTabWidget()
            
            # Add each tab with individual error handling
            self._add_dashboard_tab()
            self._add_analysis_tab()
            self._add_file_analysis_tab()
            self._add_migrate_tab()
            
            # Add to main layout
            self.main_layout.addWidget(self.tabs)
            
            logger.info("Tabs created successfully")
        except Exception as e:
            logger.error(f"Error creating tabs: {e}")
            # Create a minimal fallback tab
            fallback_tab = QWidget()
            fallback_layout = QVBoxLayout(fallback_tab)
            fallback_layout.addWidget(QLabel("Error creating application tabs"))
            
            self.tabs = QTabWidget()
            self.tabs.addTab(fallback_tab, "Error")
            self.main_layout.addWidget(self.tabs)
    
    def _add_dashboard_tab(self):
        """Add the Dashboard tab with error handling"""
        logger.info("Adding dashboard tab")
        
        try:
            # Try to import the dashboard widget
            try:
                from ui.dashboard import DashboardWidget
                self.dashboard_tab = DashboardWidget()
                logger.info("DashboardWidget created successfully")
            except Exception as e:
                logger.error(f"Error creating DashboardWidget: {e}")
                # Create a fallback dashboard
                self.dashboard_tab = QWidget()
                dashboard_layout = QVBoxLayout(self.dashboard_tab)
                dashboard_layout.addWidget(QLabel("Dashboard component unavailable"))
                dashboard_layout.addWidget(QLabel(f"Error: {str(e)}"))
            
            # Add to tabs
            self.tabs.addTab(self.dashboard_tab, "Dashboard")
            
        except Exception as e:
            logger.error(f"Error adding dashboard tab: {e}")
            # Create an empty tab on failure
            empty_tab = QWidget()
            empty_layout = QVBoxLayout(empty_tab)
            empty_layout.addWidget(QLabel("Dashboard unavailable"))
            self.tabs.addTab(empty_tab, "Dashboard")
    
    def _add_analysis_tab(self):
        """Add the Analysis tab with error handling"""
        logger.info("Adding analysis tab")
        
        try:
            # Create analysis tab
            self.analysis_tab = QWidget()
            analysis_layout = QVBoxLayout(self.analysis_tab)
            
            # Try to import the enhanced data view
            try:
                from ui.enhanced_data_view import EnhancedDataView
                self.analysis_view = EnhancedDataView()
                analysis_layout.addWidget(self.analysis_view)
                logger.info("EnhancedDataView created successfully")
            except Exception as e:
                logger.error(f"Error creating EnhancedDataView: {e}")
                # Create a fallback view
                analysis_layout.addWidget(QLabel("Enhanced data view unavailable"))
                analysis_layout.addWidget(QLabel(f"Error: {str(e)}"))
            
            # Add a row of buttons for actions
            button_layout = QHBoxLayout()
            
            # Export button
            try:
                self.export_button = QPushButton("Export Results...")
                self.export_button.clicked.connect(self._export_results)
                self.export_button.setEnabled(False)
                button_layout.addWidget(self.export_button)
            except Exception as e:
                logger.error(f"Error creating export button: {e}")
            
            # Clean button
            try:
                self.clean_button = QPushButton("Clean Files...")
                self.clean_button.clicked.connect(self._show_clean_dialog)
                self.clean_button.setEnabled(False)
                button_layout.addWidget(self.clean_button)
            except Exception as e:
                logger.error(f"Error creating clean button: {e}")
            
            # Add the button layout
            analysis_layout.addLayout(button_layout)
            
            # Add to tabs
            self.tabs.addTab(self.analysis_tab, "Analysis")
            
            logger.info("Analysis tab created successfully")
        except Exception as e:
            logger.error(f"Error adding analysis tab: {e}")
            # Create an empty tab on failure
            empty_tab = QWidget()
            empty_layout = QVBoxLayout(empty_tab)
            empty_layout.addWidget(QLabel("Analysis unavailable"))
            self.tabs.addTab(empty_tab, "Analysis")
    
    def _add_file_analysis_tab(self):
        """Add the File Analysis tab with error handling"""
        logger.info("Adding file analysis tab")
        
        try:
            # Try to import the file analysis tab
            try:
                from ui.file_analysis_tab import FileAnalysisTab
                self.file_analysis_tab = FileAnalysisTab()
                logger.info("FileAnalysisTab created successfully")
            except Exception as e:
                logger.error(f"Error creating FileAnalysisTab: {e}")
                # Create a fallback tab
                self.file_analysis_tab = QWidget()
                file_analysis_layout = QVBoxLayout(self.file_analysis_tab)
                file_analysis_layout.addWidget(QLabel("File Analysis component unavailable"))
                file_analysis_layout.addWidget(QLabel(f"Error: {str(e)}"))
            
            # Add to tabs
            self.tabs.addTab(self.file_analysis_tab, "File Analysis")
            
            logger.info("File analysis tab created successfully")
        except Exception as e:
            logger.error(f"Error adding file analysis tab: {e}")
            # Create an empty tab on failure
            empty_tab = QWidget()
            empty_layout = QVBoxLayout(empty_tab)
            empty_layout.addWidget(QLabel("File Analysis unavailable"))
            self.tabs.addTab(empty_tab, "File Analysis")
    
    def _add_migrate_tab(self):
        """Add the Migration tab with error handling"""
        logger.info("Adding migrate tab")
        
        try:
            # Create migrate tab
            self.migrate_tab = QWidget()
            migrate_layout = QVBoxLayout(self.migrate_tab)
            
            # Add migration options
            options_group = QGroupBox("Migration Options")
            options_layout = QGridLayout()
            
            # Mode selection
            mode_label = QLabel("Migration Mode:")
            self.mode_combo = QComboBox()
            self.mode_combo.addItems(["Manual (Copy to Folder)", "Automatic (Upload to SharePoint)"])
            self.mode_combo.currentIndexChanged.connect(self._migration_mode_changed)
            options_layout.addWidget(mode_label, 0, 0)
            options_layout.addWidget(self.mode_combo, 0, 1)
            
            # Target folder selection (for manual mode)
            target_label = QLabel("Target Folder:")
            self.target_path = QLabel("Not selected")
            self.target_browse = QPushButton("Browse...")
            self.target_browse.clicked.connect(self._browse_target)
            target_layout = QHBoxLayout()
            target_layout.addWidget(self.target_path)
            target_layout.addWidget(self.target_browse)
            options_layout.addWidget(target_label, 1, 0)
            options_layout.addLayout(target_layout, 1, 1)
            
            # SharePoint options (for automatic mode)
            self.sharepoint_group = QGroupBox("SharePoint Connection")
            sharepoint_layout = QGridLayout()
            
            site_label = QLabel("SharePoint Site URL:")
            self.site_url = QLabel("Not connected")
            self.connect_button = QPushButton("Connect...")
            self.connect_button.clicked.connect(self._connect_to_sharepoint)
            sharepoint_layout.addWidget(site_label, 0, 0)
            sharepoint_layout.addWidget(self.site_url, 0, 1)
            sharepoint_layout.addWidget(self.connect_button, 0, 2)
            
            library_label = QLabel("Document Library:")
            self.library_combo = QComboBox()
            self.library_combo.setEnabled(False)
            sharepoint_layout.addWidget(library_label, 1, 0)
            sharepoint_layout.addWidget(self.library_combo, 1, 1, 1, 2)
            
            self.sharepoint_group.setLayout(sharepoint_layout)
            self.sharepoint_group.setVisible(False)  # Initially hidden
            
            # Feature options
            feature_group = QGroupBox("Fix Options")
            feature_layout = QVBoxLayout()
            
            self.fix_names = QCheckBox("Fix illegal characters and reserved names")
            self.fix_names.setChecked(True)
            feature_layout.addWidget(self.fix_names)
            
            self.fix_paths = QCheckBox("Fix path length issues")
            self.fix_paths.setChecked(True)
            feature_layout.addWidget(self.fix_paths)
            
            self.remove_duplicates = QCheckBox("Remove duplicate files")
            self.remove_duplicates.setChecked(False)
            feature_layout.addWidget(self.remove_duplicates)
            
            feature_group.setLayout(feature_layout)
            
            # Add all groups to the layout
            options_group.setLayout(options_layout)
            migrate_layout.addWidget(options_group)
            migrate_layout.addWidget(self.sharepoint_group)
            migrate_layout.addWidget(feature_group)
            
            # Add spacer
            migrate_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
            # Add start button
            self.start_migration_button = QPushButton("Start Migration")
            self.start_migration_button.clicked.connect(self._start_migration)
            self.start_migration_button.setEnabled(False)
            migrate_layout.addWidget(self.start_migration_button)
            
            # Add to tabs
            self.tabs.addTab(self.migrate_tab, "Migrate")
            
            logger.info("Migrate tab created successfully")
        except Exception as e:
            logger.error(f"Error adding migrate tab: {e}")
            # Create an empty tab on failure
            empty_tab = QWidget()
            empty_layout = QVBoxLayout(empty_tab)
            empty_layout.addWidget(QLabel("Migration unavailable"))
            self.tabs.addTab(empty_tab, "Migrate")
    
    def _browse_source(self):
        """Open file dialog to select source folder"""
        logger.info("Browsing for source folder")
        
        try:
            folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
            if folder:
                self.source_folder = folder
                self.source_label.setText(f"Source: {folder}")
                self.scan_button.setEnabled(True)
                self.statusBar().showMessage(f"Selected source folder: {folder}")
                logger.info(f"Selected source folder: {folder}")
        except Exception as e:
            logger.error(f"Error browsing for source folder: {e}")
            self._show_error("Error", f"Could not select folder: {str(e)}")
    
    def _browse_target(self):
        """Open file dialog to select target folder"""
        logger.info("Browsing for target folder")
        
        try:
            folder = QFileDialog.getExistingDirectory(self, "Select Target Folder")
            if folder:
                self.output_folder = folder
                self.target_path.setText(folder)
                self._update_migration_button()
                self.statusBar().showMessage(f"Selected target folder: {folder}")
                logger.info(f"Selected target folder: {folder}")
        except Exception as e:
            logger.error(f"Error browsing for target folder: {e}")
            self._show_error("Error", f"Could not select folder: {str(e)}")
    
    def _migration_mode_changed(self, index):
        """Handle migration mode change"""
        logger.info(f"Migration mode changed to index {index}")
        
        try:
            # Show/hide SharePoint options based on mode
            if index == 0:  # Manual mode
                self.sharepoint_group.setVisible(False)
                self.target_browse.setEnabled(True)
                self.target_path.setEnabled(True)
                # Update button state based on target folder
                self._update_migration_button()
            else:  # Automatic mode
                self.sharepoint_group.setVisible(True)
                self.target_browse.setEnabled(False)
                self.target_path.setEnabled(False)
                # Update button state based on SharePoint connection
                self._update_migration_button()
        except Exception as e:
            logger.error(f"Error handling migration mode change: {e}")
    
    def _connect_to_sharepoint(self):
        """Connect to SharePoint"""
        logger.info("Connecting to SharePoint")
        
        try:
            # This is a placeholder - in a real implementation, you would show a dialog
            # to collect the SharePoint credentials and establish a connection
            self._show_info("SharePoint Connection", "SharePoint integration is not implemented in this version")
            
            # Update UI as if connected
            self.site_url.setText("https://example.sharepoint.com")
            self.library_combo.clear()
            self.library_combo.addItems(["Documents", "Shared Documents"])
            self.library_combo.setEnabled(True)
            self.connect_button.setText("Disconnect")
            
            # Update migration button state
            self._update_migration_button()
        except Exception as e:
            logger.error(f"Error connecting to SharePoint: {e}")
            self._show_error("Connection Error", f"Could not connect to SharePoint: {str(e)}")
    
    def _update_migration_button(self):
        """Update the state of the migration button based on current settings"""
        logger.info("Updating migration button state")
        
        try:
            # Check if scan has been completed
            have_results = hasattr(self, 'data_processor') and self.data_processor.get_analysis_results()
            
            if not have_results:
                self.start_migration_button.setEnabled(False)
                return
                
            # Check mode-specific requirements
            mode_index = self.mode_combo.currentIndex()
            
            if mode_index == 0:  # Manual mode
                # Need a target folder
                self.start_migration_button.setEnabled(bool(self.output_folder))
            else:  # Automatic mode
                # Need SharePoint connection and selected library
                has_connection = self.site_url.text() != "Not connected"
                has_library = self.library_combo.currentIndex() >= 0
                self.start_migration_button.setEnabled(has_connection and has_library)
        except Exception as e:
            logger.error(f"Error updating migration button: {e}")
            self.start_migration_button.setEnabled(False)
    
    def _start_scan(self):
        """Start scanning the selected folder"""
        logger.info("Starting scan")
        
        try:
            if not self.source_folder:
                self._show_error("Error", "No source folder selected")
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
            callbacks = {
                'progress': self._scan_progress,
                'scan_completed': self._scan_completed,
                'error': self._scan_error
            }
            
            # Start the scan
            self.data_processor.start_scan(self.source_folder, None, callbacks)
            
            logger.info(f"Scan started for {self.source_folder}")
        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            self._show_error("Scan Error", f"Could not start scan: {str(e)}")
            
            # Reset UI
            self._reset_ui_after_operation()
    
    def _scan_progress(self, current, total):
        """Update scan progress"""
        try:
            progress = int((current / max(total, 1)) * 100)
            self.progress_bar.setValue(progress)
            self.statusBar().showMessage(f"Scanning... {current}/{total} files ({progress}%)")
        except Exception as e:
            logger.error(f"Error updating scan progress: {e}")
    
    def _scan_completed(self, scan_data):
        """Handle scan completion"""
        logger.info("Scan completed")
        
        try:
            # Update UI
            self._reset_ui_after_operation()
            self.statusBar().showMessage("Scan completed. Analyzing data...")
            
            # Start analysis
            self._analyze_data()
        except Exception as e:
            logger.error(f"Error handling scan completion: {e}")
            self._show_error("Error", f"Error processing scan results: {str(e)}")
            self._reset_ui_after_operation()
    
    def _scan_error(self, error_message):
        """Handle scan error"""
        logger.error(f"Scan error: {error_message}")
        
        # Update UI
        self._reset_ui_after_operation()
        self.statusBar().showMessage("Scan failed")
        
        # Show error message
        self._show_error("Scan Error", error_message)
    
    def _analyze_data(self):
        """Analyze scanned data"""
        logger.info("Starting data analysis")
        
        try:
            # Update UI
            self.statusBar().showMessage("Analyzing data...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Define callbacks
            callbacks = {
                'progress': self._update_progress,
                'analysis_completed': self._analysis_completed,
                'error': self._analysis_error
            }
            
            # Start analysis
            self.data_processor.analyze_data(None, callbacks)
        except Exception as e:
            logger.error(f"Error starting analysis: {e}")
            self._show_error("Analysis Error", f"Could not start analysis: {str(e)}")
            self._reset_ui_after_operation()
    
    def _update_progress(self, progress):
        """Update progress bar for any operation"""
        try:
            self.progress_bar.setValue(progress)
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
    
    def _analysis_completed(self, analysis_results):
        """Handle analysis completion"""
        logger.info("Analysis completed")
        
        try:
            # Update UI
            self._reset_ui_after_operation()
            self.statusBar().showMessage("Analysis completed")
            
            # Enable buttons that depend on analysis results
            self.export_button.setEnabled(True)
            self.clean_button.setEnabled(True)
            self._update_migration_button()
            
            # Update results displays
            self._update_results()
        except Exception as e:
            logger.error(f"Error handling analysis completion: {e}")
            self._show_error("Error", f"Error processing analysis results: {str(e)}")
    
    def _analysis_error(self, error_message):
        """Handle analysis error"""
        logger.error(f"Analysis error: {error_message}")
        
        # Update UI
        self._reset_ui_after_operation()
        self.statusBar().showMessage("Analysis failed")
        
        # Show error message
        self._show_error("Analysis Error", error_message)
    
    def _update_results(self):
        """Update all UI components with analysis results"""
        logger.info("Updating UI with results")
        
        try:
            # Get results
            analysis_results = self.data_processor.get_analysis_results()
            
            # Update dashboard
            try:
                if hasattr(self, 'dashboard_tab') and hasattr(self.dashboard_tab, 'update_results'):
                    self.dashboard_tab.update_results(analysis_results)
                    logger.info("Dashboard updated")
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
            
            # Update analysis view
            try:
                if hasattr(self, 'analysis_view') and hasattr(self.analysis_view, 'update_data'):
                    self.analysis_view.update_data(analysis_results)
                    logger.info("Analysis view updated")
            except Exception as e:
                logger.error(f"Error updating analysis view: {e}")
            
            # Update file analysis tab
            try:
                if hasattr(self, 'file_analysis_tab') and hasattr(self.file_analysis_tab, 'update_data'):
                    self.file_analysis_tab.update_data(analysis_results)
                    logger.info("File analysis tab updated")
            except Exception as e:
                logger.error(f"Error updating file analysis tab: {e}")
            
            # Update tab index to show the analysis tab
            self.tabs.setCurrentIndex(1)  # Switch to Analysis tab
        except Exception as e:
            logger.error(f"Error updating results: {e}")
            self._show_error("Error", f"Error updating results: {str(e)}")
    
    def _export_results(self):
        """Export analysis results"""
        logger.info("Exporting results")
        
        try:
            # Check if we have an enhanced data view
            if hasattr(self, 'analysis_view') and hasattr(self.analysis_view, 'export_data'):
                # Let the enhanced data view handle exporting
                self.analysis_view.export_data()
                logger.info("Export handled by EnhancedDataView")
                return
                
            # Fallback: handle export manually
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self, "Export Results", "", "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not file_path:
                return
                
            self.statusBar().showMessage(f"Exported results to {file_path}")
            logger.info(f"Results exported to {file_path}")
            
            # Show confirmation
            self._show_info("Export Complete", f"Results exported to:\n{file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            self._show_error("Export Error", f"Could not export results: {str(e)}")
    
    def _show_clean_dialog(self):
        """Show dialog for cleaning options"""
        logger.info("Showing clean dialog")
        
        try:
            # Just use the folder dialog directly for simplicity
            target_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder for Cleaned Files")
            
            if not target_folder:
                return
                
            # Start cleaning
            self._start_cleaning(target_folder)
            
        except Exception as e:
            logger.error(f"Error showing clean dialog: {e}")
            self._show_error("Error", f"Could not show clean dialog: {str(e)}")
    
    def _start_cleaning(self, target_folder):
        """Start the cleaning process"""
        logger.info(f"Starting cleaning to {target_folder}")
        
        try:
            # Update UI
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.stop_button.setVisible(True)
            self.is_cleaning = True
            self.scan_button.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.clean_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.statusBar().showMessage("Cleaning files...")
            
            # Prepare clean options
            clean_options = {
                'fix_names': self.fix_names.isChecked(),
                'fix_paths': self.fix_paths.isChecked(),
                'remove_duplicates': self.remove_duplicates.isChecked(),
                'source_folder': self.source_folder
            }
            
            # Define callbacks
            callbacks = {
                'progress': self._update_progress,
                'status': self._update_status,
                'error': self._clean_error,
                'file_processed': self._file_processed,
                'cleaning_completed': self._cleaning_completed
            }
            
            # Start cleaning
            self.data_processor.start_cleaning(target_folder, clean_options, callbacks)
            
        except Exception as e:
            logger.error(f"Error starting cleaning: {e}")
            self._show_error("Cleaning Error", f"Could not start cleaning: {str(e)}")
            self._reset_ui_after_operation()
    
    def _update_status(self, status_message):
        """Update status bar with a message"""
        try:
            self.statusBar().showMessage(status_message)
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    def _file_processed(self, source_path, target_path):
        """Handle processed file notification"""
        # This method can be implemented if needed to track individual file progress
        pass
    
    def _cleaning_completed(self, cleaned_files):
        """Handle cleaning completion"""
        logger.info("Cleaning completed")
        
        try:
            # Update UI
            self._reset_ui_after_operation()
            self.statusBar().showMessage("Cleaning completed")
            
            # Get count of cleaned files
            cleaned_count = len(cleaned_files)
            
            # Show completion message
            self._show_info("Cleaning Complete", 
                          f"Cleaning completed successfully.\n\n"
                          f"{cleaned_count} files were processed.")
            
        except Exception as e:
            logger.error(f"Error handling cleaning completion: {e}")
            self._show_error("Error", f"Error completing cleaning: {str(e)}")
    
    def _clean_error(self, error_message):
        """Handle cleaning error"""
        logger.error(f"Cleaning error: {error_message}")
        
        # Update UI
        self._reset_ui_after_operation()
        self.statusBar().showMessage("Cleaning failed")
        
        # Show error message
        self._show_error("Cleaning Error", error_message)
    
    def _start_migration(self):
        """Start the migration process"""
        logger.info("Starting migration")
        
        try:
            # Check migration mode
            mode_index = self.mode_combo.currentIndex()
            
            if mode_index == 0:  # Manual mode
                # Just use the regular cleaning process
                if self.output_folder:
                    self._start_cleaning(self.output_folder)
                else:
                    self._show_error("Error", "No target folder selected")
            else:  # Automatic mode
                # This is a placeholder - in a real implementation, you would
                # use the SharePoint integration to upload to SharePoint
                self._show_info("SharePoint Upload", 
                              "SharePoint upload is not implemented in this version.\n\n"
                              "Please use manual mode to clean files.")
                
        except Exception as e:
            logger.error(f"Error starting migration: {e}")
            self._show_error("Migration Error", f"Could not start migration: {str(e)}")
    
    def _stop_operations(self):
        """Stop any ongoing operations"""
        logger.info("Stopping operations")
        
        try:
            if self.is_scanning:
                # Stop scanning
                self.data_processor.stop_scanning()
                self.is_scanning = False
                logger.info("Scan stopped")
                
            if self.is_cleaning:
                # Stop cleaning
                self.data_processor.stop_cleaning()
                self.is_cleaning = False
                logger.info("Cleaning stopped")
                
            # Reset UI
            self._reset_ui_after_operation()
            self.statusBar().showMessage("Operation stopped")
            
        except Exception as e:
            logger.error(f"Error stopping operations: {e}")
            self._show_error("Error", f"Error stopping operations: {str(e)}")
    
    def _reset_ui_after_operation(self):
        """Reset UI elements after an operation completes or is stopped"""
        try:
            # Update button states
            self.scan_button.setEnabled(bool(self.source_folder))
            self.browse_button.setEnabled(True)
            
            # Hide progress indicators
            self.progress_bar.setVisible(False)
            self.stop_button.setVisible(False)
            
            # Reset flags
            self.is_scanning = False
            self.is_cleaning = False
            
        except Exception as e:
            logger.error(f"Error resetting UI: {e}")
    
    def _show_error(self, title, message):
        """Show an error message dialog"""
        try:
            QMessageBox.warning(self, title, message)
        except Exception as e:
            logger.error(f"Error showing error message: {e}")
            # Last resort: print to console
            print(f"ERROR: {title} - {message}")
    
    def _show_info(self, title, message):
        """Show an information message dialog"""
        try:
            QMessageBox.information(self, title, message)
        except Exception as e:
            logger.error(f"Error showing info message: {e}")
            # Last resort: print to console
            print(f"INFO: {title} - {message}")
    
    def _show_critical_error(self, title, message):
        """Show a critical error message dialog"""
        try:
            QMessageBox.critical(self, title, message)
        except Exception as e:
            logger.error(f"Error showing critical error message: {e}")
            # Last resort: print to console
            print(f"CRITICAL ERROR: {title} - {message}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Stop any ongoing operations
            self._stop_operations()
            
            # Accept the event
            logger.info("Application closed")
            event.accept()
        except Exception as e:
            logger.error(f"Error during application close: {e}")
            event.accept()  # Accept anyway to ensure the application closes