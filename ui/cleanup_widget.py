#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup widget for SharePoint Data Migration Cleanup Tool.
Implements UI for both manual and automatic cleanup modes.
"""

import os
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QRadioButton, QButtonGroup, QGroupBox, QFileDialog, 
                            QLineEdit, QCheckBox, QProgressBar, QTabWidget, 
                            QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QFormLayout, QComboBox, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from core.data_cleaner import DataCleaner
from infrastructure.sharepoint import SharePointUploadManager

logger = logging.getLogger('sharepoint_migration_tool')

class CleanupWidget(QWidget):
    """Widget for cleaning and uploading data"""
    
    # Define signals
    cleanup_completed = pyqtSignal(dict)  # Dictionary of cleaned files
    upload_completed = pyqtSignal()
    
    def __init__(self, config=None):
        """
        Initialize the cleanup widget
        
        Args:
            config (dict): Application configuration
        """
        super().__init__()
        
        self.config = config or {}
        self.data_cleaner = DataCleaner()
        self.upload_manager = SharePointUploadManager()
        self.analysis_results = None
        self.cleaned_files = None
        
        # Set up the UI
        self.init_ui()
        
    def init_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Mode selection
        mode_group = QGroupBox("Cleanup Mode")
        mode_layout = QHBoxLayout()
        
        self.manual_mode_radio = QRadioButton("Manual (Copy to New Folder)")
        self.manual_mode_radio.setChecked(True)
        self.auto_mode_radio = QRadioButton("Automatic (Upload to SharePoint)")
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.manual_mode_radio, 1)
        self.mode_group.addButton(self.auto_mode_radio, 2)
        self.mode_group.buttonClicked.connect(self.mode_changed)
        
        mode_layout.addWidget(self.manual_mode_radio)
        mode_layout.addWidget(self.auto_mode_radio)
        mode_group.setLayout(mode_layout)
        
        main_layout.addWidget(mode_group)
        
        # Stacked widgets for different modes
        self.tabs = QTabWidget()
        
        # Manual mode tab
        self.manual_tab = QWidget()
        manual_layout = QVBoxLayout(self.manual_tab)
        
        # Target folder selection
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target Folder:"))
        
        self.target_folder_path = QLineEdit()
        self.target_folder_path.setReadOnly(True)
        self.target_folder_path.setPlaceholderText("Select target folder for cleaned files")
        target_layout.addWidget(self.target_folder_path, 1)
        
        self.browse_target_button = QPushButton("Browse...")
        self.browse_target_button.clicked.connect(self.browse_target_folder)
        target_layout.addWidget(self.browse_target_button)
        
        manual_layout.addLayout(target_layout)
        
        # Cleaning options
        clean_options_group = QGroupBox("Cleaning Options")
        clean_options_layout = QVBoxLayout()
        
        self.fix_names_check = QCheckBox("Fix illegal SharePoint characters in names")
        self.fix_names_check.setChecked(True)
        clean_options_layout.addWidget(self.fix_names_check)
        
        self.fix_paths_check = QCheckBox("Shorten paths exceeding 256 character limit")
        self.fix_paths_check.setChecked(True)
        clean_options_layout.addWidget(self.fix_paths_check)
        
        self.remove_duplicates_check = QCheckBox("Remove duplicate files")
        self.remove_duplicates_check.setChecked(False)
        clean_options_layout.addWidget(self.remove_duplicates_check)
        
        self.flag_pii_check = QCheckBox("Flag files with potential PII (placeholder - coming in future version)")
        self.flag_pii_check.setChecked(True)
        self.flag_pii_check.setEnabled(False)  # Disable since it's a placeholder
        clean_options_layout.addWidget(self.flag_pii_check)
        
        clean_options_group.setLayout(clean_options_layout)
        manual_layout.addWidget(clean_options_group)
        
        # Actions
        manual_actions_layout = QHBoxLayout()
        self.start_clean_button = QPushButton("Start Cleaning")
        self.start_clean_button.clicked.connect(self.start_cleaning)
        self.start_clean_button.setEnabled(False)
        manual_actions_layout.addWidget(self.start_clean_button)
        
        self.stop_clean_button = QPushButton("Stop")
        self.stop_clean_button.clicked.connect(self.stop_cleaning)
        self.stop_clean_button.setEnabled(False)
        manual_actions_layout.addWidget(self.stop_clean_button)
        
        manual_layout.addLayout(manual_actions_layout)
        
        # Progress
        self.clean_progress_bar = QProgressBar()
        self.clean_progress_bar.setRange(0, 100)
        self.clean_progress_bar.setValue(0)
        manual_layout.addWidget(self.clean_progress_bar)
        
        # Status
        self.clean_status_text = QTextEdit()
        self.clean_status_text.setReadOnly(True)
        self.clean_status_text.setMaximumHeight(150)
        manual_layout.addWidget(self.clean_status_text)
        
        # Add manual tab
        self.tabs.addTab(self.manual_tab, "Manual Cleanup")
        
        # Automatic mode tab
        self.auto_tab = QWidget()
        auto_layout = QVBoxLayout(self.auto_tab)
        
        # SharePoint configuration
        sp_config_group = QGroupBox("SharePoint Configuration")
        sp_config_layout = QFormLayout()
        
        self.sp_site_url = QLineEdit()
        self.sp_site_url.setPlaceholderText("https://contoso.sharepoint.com/sites/migration")
        sp_config_layout.addRow("SharePoint Site URL:", self.sp_site_url)
        
        self.sp_auth_method = QComboBox()
        self.sp_auth_method.addItems(["Modern Authentication", "Username/Password", "App-only Authentication"])
        self.sp_auth_method.currentIndexChanged.connect(self.auth_method_changed)
        sp_config_layout.addRow("Authentication Method:", self.sp_auth_method)
        
        # Username/password fields (initially hidden)
        self.sp_username_widget = QWidget()
        username_layout = QHBoxLayout(self.sp_username_widget)
        username_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sp_username = QLineEdit()
        username_layout.addWidget(self.sp_username)
        sp_config_layout.addRow("Username:", self.sp_username_widget)
        
        self.sp_password_widget = QWidget()
        password_layout = QHBoxLayout(self.sp_password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sp_password = QLineEdit()
        self.sp_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.sp_password)
        sp_config_layout.addRow("Password:", self.sp_password_widget)
        
        # Hide username/password by default
        self.sp_username_widget.setVisible(False)
        self.sp_password_widget.setVisible(False)
        
        self.sp_target_library = QLineEdit()
        self.sp_target_library.setPlaceholderText("Documents")
        sp_config_layout.addRow("Target Document Library:", self.sp_target_library)
        
        self.sp_create_folders = QCheckBox("Create folder structure in SharePoint")
        self.sp_create_folders.setChecked(True)
        sp_config_layout.addRow("", self.sp_create_folders)
        
        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self.test_sharepoint_connection)
        sp_config_layout.addRow("", self.test_connection_button)
        
        sp_config_group.setLayout(sp_config_layout)
        auto_layout.addWidget(sp_config_group)
        
        # Reuse the same cleaning options for automatic mode
        auto_clean_options_group = QGroupBox("Cleaning Options")
        auto_clean_options_layout = QVBoxLayout()
        
        self.auto_fix_names_check = QCheckBox("Fix illegal SharePoint characters in names")
        self.auto_fix_names_check.setChecked(True)
        auto_clean_options_layout.addWidget(self.auto_fix_names_check)
        
        self.auto_fix_paths_check = QCheckBox("Shorten paths exceeding 256 character limit")
        self.auto_fix_paths_check.setChecked(True)
        auto_clean_options_layout.addWidget(self.auto_fix_paths_check)
        
        self.auto_remove_duplicates_check = QCheckBox("Remove duplicate files")
        self.auto_remove_duplicates_check.setChecked(False)
        auto_clean_options_layout.addWidget(self.auto_remove_duplicates_check)
        
        self.auto_flag_pii_check = QCheckBox("Flag files with potential PII (placeholder - coming in future version)")
        self.auto_flag_pii_check.setChecked(True)
        self.auto_flag_pii_check.setEnabled(False)  # Disable since it's a placeholder
        auto_clean_options_layout.addWidget(self.auto_flag_pii_check)
        
        auto_clean_options_group.setLayout(auto_clean_options_layout)
        auto_layout.addWidget(auto_clean_options_group)
        
        # Actions
        auto_actions_layout = QHBoxLayout()
        self.start_auto_button = QPushButton("Clean and Upload")
        self.start_auto_button.clicked.connect(self.start_auto_clean_upload)
        self.start_auto_button.setEnabled(False)
        auto_actions_layout.addWidget(self.start_auto_button)
        
        self.stop_auto_button = QPushButton("Stop")
        self.stop_auto_button.clicked.connect(self.stop_auto_clean_upload)
        self.stop_auto_button.setEnabled(False)
        auto_actions_layout.addWidget(self.stop_auto_button)
        
        auto_layout.addLayout(auto_actions_layout)
        
        # Progress
        self.auto_progress_bar = QProgressBar()
        self.auto_progress_bar.setRange(0, 100)
        self.auto_progress_bar.setValue(0)
        auto_layout.addWidget(self.auto_progress_bar)
        
        # Status
        self.auto_status_text = QTextEdit()
        self.auto_status_text.setReadOnly(True)
        self.auto_status_text.setMaximumHeight(150)
        auto_layout.addWidget(self.auto_status_text)
        
        # Add automatic tab
        self.tabs.addTab(self.auto_tab, "Automatic Upload")
        
        # Initially disable the automatic tab
        self.tabs.setTabEnabled(1, False)
        
        # Add tabs to main layout
        main_layout.addWidget(self.tabs)
        
        # Results section
        results_group = QGroupBox("Processing Results")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Original Path", "Action", "New Path"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
    def mode_changed(self, button):
        """
        Handle mode selection change
        
        Args:
            button (QRadioButton): The selected radio button
        """
        # Enable/disable tabs based on mode
        if button == self.manual_mode_radio:
            self.tabs.setCurrentIndex(0)
            self.tabs.setTabEnabled(1, False)
        else:
            self.tabs.setCurrentIndex(1)
            self.tabs.setTabEnabled(1, True)
        
    def auth_method_changed(self, index):
        """
        Handle authentication method change
        
        Args:
            index (int): Index of selected auth method
        """
        # Show/hide username/password fields based on auth method
        if index == 1:  # Username/Password
            self.sp_username_widget.setVisible(True)
            self.sp_password_widget.setVisible(True)
        else:
            self.sp_username_widget.setVisible(False)
            self.sp_password_widget.setVisible(False)
        
    def browse_target_folder(self):
        """Open file dialog to select target folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Target Folder for Cleaned Files")
        if folder:
            self.target_folder_path.setText(folder)
            self.start_clean_button.setEnabled(True)
        
    def test_sharepoint_connection(self):
        """Test the SharePoint connection with provided credentials"""
        site_url = self.sp_site_url.text().strip()
        if not site_url:
            QMessageBox.warning(self, "Error", "Please enter SharePoint site URL.")
            return
            
        # Get auth method
        auth_method_index = self.sp_auth_method.currentIndex()
        auth_method = "modern"
        if auth_method_index == 1:
            auth_method = "legacy"
        elif auth_method_index == 2:
            auth_method = "app"
            
        # Get credentials if needed
        username = None
        password = None
        if auth_method == "legacy":
            username = self.sp_username.text().strip()
            password = self.sp_password.text()
            
            if not username or not password:
                QMessageBox.warning(self, "Error", "Please enter username and password.")
                return
        
        # Test connection
        self.test_connection_button.setEnabled(False)
        self.test_connection_button.setText("Testing...")
        
        # Configure SharePoint
        success = self.upload_manager.configure(
            site_url=site_url,
            auth_method=auth_method,
            username=username,
            password=password
        )
        
        # Reset button
        self.test_connection_button.setEnabled(True)
        self.test_connection_button.setText("Test Connection")
        
        # Show result
        if success:
            QMessageBox.information(self, "Success", "SharePoint connection successful!")
            self.start_auto_button.setEnabled(True)
        else:
            QMessageBox.critical(self, "Error", "SharePoint connection failed. Please check your settings.")
            
    def set_analysis_results(self, results):
        """
        Set the analysis results to process
        
        Args:
            results (dict): Analysis results
        """
        self.analysis_results = results
        
        # Enable buttons if we have results and target folder
        if self.analysis_results:
            # Enable manual button if target folder is set
            if self.target_folder_path.text().strip():
                self.start_clean_button.setEnabled(True)
                
            # Enable auto button if SharePoint is configured
            if self.sp_site_url.text().strip():
                self.start_auto_button.setEnabled(True)
                
    def start_cleaning(self):
        """Start the manual cleaning process"""
        if not self.analysis_results:
            QMessageBox.warning(self, "Error", "No analysis results to process.")
            return
            
        target_folder = self.target_folder_path.text().strip()
        if not target_folder:
            QMessageBox.warning(self, "Error", "Please select a target folder.")
            return
            
        # Update UI state
        self.start_clean_button.setEnabled(False)
        self.stop_clean_button.setEnabled(True)
        self.clean_progress_bar.setValue(0)
        self.add_clean_status("Starting cleaning process...")
        
        # Get cleaning options
        clean_options = {
            'fix_names': self.fix_names_check.isChecked(),
            'fix_paths': self.fix_paths_check.isChecked(),
            'remove_duplicates': self.remove_duplicates_check.isChecked(),
            'flag_pii': self.flag_pii_check.isChecked()
        }
        
        # Clear results table
        self.results_table.setRowCount(0)
        
        # Start the cleaning process
        self.data_cleaner.start_cleaning(
            self.analysis_results,
            target_folder,
            clean_options,
            progress_callback=self.update_clean_progress,
            status_callback=self.add_clean_status,
            error_callback=self.handle_clean_error,
            file_processed_callback=self.add_clean_result,
            finished_callback=self.cleaning_completed
        )
        
    def stop_cleaning(self):
        """Stop the cleaning process"""
        self.data_cleaner.stop_cleaning()
        self.add_clean_status("Stopping cleaning process...")
        self.stop_clean_button.setEnabled(False)
        
    def update_clean_progress(self, value):
        """
        Update the cleaning progress bar
        
        Args:
            value (int): Progress percentage
        """
        self.clean_progress_bar.setValue(value)
        
    def add_clean_status(self, message):
        """
        Add message to cleaning status text
        
        Args:
            message (str): Status message
        """
        self.clean_status_text.append(message)
        
    def handle_clean_error(self, error_message):
        """
        Handle errors during cleaning
        
        Args:
            error_message (str): Error message
        """
        QMessageBox.critical(self, "Error", error_message)
        self.add_clean_status(f"Error: {error_message}")
        self.start_clean_button.setEnabled(True)
        self.stop_clean_button.setEnabled(False)
        
    def add_clean_result(self, original_path, new_path):
        """
        Add a processed file to the results table
        
        Args:
            original_path (str): Original file path
            new_path (str): New file path
        """
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        self.results_table.setItem(row, 0, QTableWidgetItem(original_path))
        self.results_table.setItem(row, 1, QTableWidgetItem("Copied with fixes"))
        self.results_table.setItem(row, 2, QTableWidgetItem(new_path))
        
    def cleaning_completed(self, cleaned_files):
        """
        Handle cleaning completion
        
        Args:
            cleaned_files (dict): Dictionary mapping original paths to new paths
        """
        # Update UI state
        self.start_clean_button.setEnabled(True)
        self.stop_clean_button.setEnabled(False)
        self.add_clean_status("Cleaning complete")
        
        # Store results
        self.cleaned_files = cleaned_files
        
        # Emit signal
        self.cleanup_completed.emit(cleaned_files)
        
    def start_auto_clean_upload(self):
        """Start the automatic cleaning and upload process"""
        if not self.analysis_results:
            QMessageBox.warning(self, "Error", "No analysis results to process.")
            return
            
        site_url = self.sp_site_url.text().strip()
        target_library = self.sp_target_library.text().strip()
        
        if not site_url:
            QMessageBox.warning(self, "Error", "Please enter SharePoint site URL.")
            return
            
        if not target_library:
            QMessageBox.warning(self, "Error", "Please enter target document library.")
            return
            
        # Update UI state
        self.start_auto_button.setEnabled(False)
        self.stop_auto_button.setEnabled(True)
        self.auto_progress_bar.setValue(0)
        self.add_auto_status("Starting automatic cleaning and upload process...")
        
        # Get auth method
        auth_method_index = self.sp_auth_method.currentIndex()
        auth_method = "modern"
        if auth_method_index == 1:
            auth_method = "legacy"
        elif auth_method_index == 2:
            auth_method = "app"
            
        # Get credentials if needed
        username = None
        password = None
        if auth_method == "legacy":
            username = self.sp_username.text().strip()
            password = self.sp_password.text()
            
            if not username or not password:
                QMessageBox.warning(self, "Error", "Please enter username and password.")
                self.start_auto_button.setEnabled(True)
                self.stop_auto_button.setEnabled(False)
                return
        
        # Configure SharePoint
        success = self.upload_manager.configure(
            site_url=site_url,
            auth_method=auth_method,
            username=username,
            password=password
        )
        
        if not success:
            QMessageBox.critical(self, "Error", "SharePoint connection failed. Please check your settings.")
            self.start_auto_button.setEnabled(True)
            self.stop_auto_button.setEnabled(False)
            return
            
        # Get cleaning options
        clean_options = {
            'fix_names': self.auto_fix_names_check.isChecked(),
            'fix_paths': self.auto_fix_paths_check.isChecked(),
            'remove_duplicates': self.auto_remove_duplicates_check.isChecked(),
            'flag_pii': self.auto_flag_pii_check.isChecked()
        }
        
        # Clear results table
        self.results_table.setRowCount(0)
        
        # Create a temporary folder for cleaned files
        import tempfile
        temp_folder = tempfile.mkdtemp(prefix="sharepoint_migration_")
        self.add_auto_status(f"Created temporary folder: {temp_folder}")
        
        # Start the cleaning process
        self.data_cleaner.start_cleaning(
            self.analysis_results,
            temp_folder,
            clean_options,
            progress_callback=self.update_auto_progress,
            status_callback=self.add_auto_status,
            error_callback=self.handle_auto_error,
            file_processed_callback=self.add_auto_result,
            finished_callback=lambda cleaned_files: self.auto_cleaning_completed(
                cleaned_files, target_library, self.sp_create_folders.isChecked())
        )
        
    def stop_auto_clean_upload(self):
        """Stop the automatic cleaning and upload process"""
        self.data_cleaner.stop_cleaning()
        self.upload_manager.stop_upload()
        self.add_auto_status("Stopping process...")
        self.stop_auto_button.setEnabled(False)
        
    def update_auto_progress(self, value):
        """
        Update the automatic process progress bar
        
        Args:
            value (int): Progress percentage
        """
        self.auto_progress_bar.setValue(value)
        
    def add_auto_status(self, message):
        """
        Add message to automatic process status text
        
        Args:
            message (str): Status message
        """
        self.auto_status_text.append(message)
        
    def handle_auto_error(self, error_message):
        """
        Handle errors during automatic process
        
        Args:
            error_message (str): Error message
        """
        QMessageBox.critical(self, "Error", error_message)
        self.add_auto_status(f"Error: {error_message}")
        self.start_auto_button.setEnabled(True)
        self.stop_auto_button.setEnabled(False)
        
    def add_auto_result(self, original_path, new_path):
        """
        Add a processed file to the results table
        
        Args:
            original_path (str): Original file path
            new_path (str): New file path
        """
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        self.results_table.setItem(row, 0, QTableWidgetItem(original_path))
        self.results_table.setItem(row, 1, QTableWidgetItem("Preparing for upload"))
        self.results_table.setItem(row, 2, QTableWidgetItem(new_path))
        
    def auto_cleaning_completed(self, cleaned_files, target_library, create_folders):
        """
        Handle automatic cleaning completion and start upload
        
        Args:
            cleaned_files (dict): Dictionary mapping original paths to new paths
            target_library (str): Target SharePoint document library
            create_folders (bool): Whether to create folder structure in SharePoint
        """
        # Store results
        self.cleaned_files = cleaned_files
        
        if not cleaned_files:
            self.add_auto_status("No files were cleaned/prepared for upload.")
            self.start_auto_button.setEnabled(True)
            self.stop_auto_button.setEnabled(False)
            return
            
        # Start upload process
        self.add_auto_status(f"Cleaning complete. Starting upload to SharePoint...")
        
        # Update progress to show we're in the next phase
        self.auto_progress_bar.setValue(0)
        
        # Prepare upload mapping
        # For simplicity, we'll just use the same paths in SharePoint
        # In a real implementation, you would make this more configurable
        files_to_upload = {}
        for source_path, cleaned_path in cleaned_files.items():
            # Target path in SharePoint
            # Extract relative path from cleaned_path
            rel_path = os.path.basename(cleaned_path)  # Simplified for now
            target_path = f"{target_library}/{rel_path}"
            
            files_to_upload[cleaned_path] = target_path
            
        # Start the upload
        self.upload_manager.start_upload(
            files_to_upload,
            target_library,
            create_folders,
            progress_callback=self.update_auto_progress,
            status_callback=self.add_auto_status,
            error_callback=self.handle_auto_error,
            file_uploaded_callback=self.file_uploaded,
            finished_callback=self.upload_completed_handler
        )
        
    def file_uploaded(self, file_path):
        """
        Handle file uploaded event
        
        Args:
            file_path (str): Path of uploaded file
        """
        # Find the row in results table
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 2)
            if item and item.text() == file_path:
                # Update the action
                self.results_table.setItem(row, 1, QTableWidgetItem("Uploaded to SharePoint"))
                break
                
    def upload_completed_handler(self):
        """Handle upload completion"""
        # Update UI state
        self.start_auto_button.setEnabled(True)
        self.stop_auto_button.setEnabled(False)
        self.add_auto_status("Upload complete")
        
        # Delete temporary files if needed
        # ...
        
        # Emit signal
        self.upload_completed.emit()