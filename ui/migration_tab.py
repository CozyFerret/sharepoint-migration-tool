"""
Migration Tab for SharePoint Migration Tool

This module provides a revised migration tab with settings options integration.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QTabWidget, QPushButton, QLabel, 
                           QLineEdit, QComboBox, QCheckBox,
                           QFileDialog, QMessageBox, QGroupBox,
                           QRadioButton, QProgressBar, QSpacerItem,
                           QSizePolicy, QGridLayout, QDialog,
                           QDialogButtonBox, QStackedWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont

import os
import logging
from datetime import datetime

# Import other necessary modules
from core.scanner import Scanner
from core.data_processor import DataProcessor
from infrastructure.sharepoint import SharePointIntegration

logger = logging.getLogger(__name__)

# Import the login dialog (can be moved to this file later if circular imports are an issue)
class LoginDialog(QDialog):
    """Dialog for SharePoint login credentials"""
    
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("SharePoint Login")
        self.resize(400, 200)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Site URL
        url_layout = QHBoxLayout()
        url_label = QLabel("SharePoint Site URL:")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://contoso.sharepoint.com/sites/mysite")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)
        
        # Authentication options
        auth_group = QGroupBox("Authentication Method")
        auth_layout = QVBoxLayout()
        
        # Modern auth (username + password)
        self.modern_auth_radio = QRadioButton("Username and Password")
        self.modern_auth_radio.setChecked(True)
        self.modern_auth_radio.toggled.connect(self.toggle_auth_method)
        auth_layout.addWidget(self.modern_auth_radio)
        
        # Username/password inputs
        cred_layout = QGridLayout()
        user_label = QLabel("Username:")
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("email@domain.com")
        
        pass_label = QLabel("Password:")
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        
        cred_layout.addWidget(user_label, 0, 0)
        cred_layout.addWidget(self.user_edit, 0, 1)
        cred_layout.addWidget(pass_label, 1, 0)
        cred_layout.addWidget(self.pass_edit, 1, 1)
        auth_layout.addLayout(cred_layout)
        
        # App-only auth
        self.app_auth_radio = QRadioButton("App-Only Authentication")
        auth_layout.addWidget(self.app_auth_radio)
        
        # Client ID/Secret inputs
        app_layout = QGridLayout()
        client_id_label = QLabel("Client ID:")
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setEnabled(False)
        
        client_secret_label = QLabel("Client Secret:")
        self.client_secret_edit = QLineEdit()
        self.client_secret_edit.setEchoMode(QLineEdit.Password)
        self.client_secret_edit.setEnabled(False)
        
        app_layout.addWidget(client_id_label, 0, 0)
        app_layout.addWidget(self.client_id_edit, 0, 1)
        app_layout.addWidget(client_secret_label, 1, 0)
        app_layout.addWidget(self.client_secret_edit, 1, 1)
        auth_layout.addLayout(app_layout)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def toggle_auth_method(self, checked):
        """Toggle between authentication methods"""
        # Enable/disable username/password fields
        self.user_edit.setEnabled(checked)
        self.pass_edit.setEnabled(checked)
        
        # Enable/disable client ID/secret fields
        self.client_id_edit.setEnabled(not checked)
        self.client_secret_edit.setEnabled(not checked)
        
    def get_credentials(self):
        """Get the entered credentials"""
        creds = {
            "site_url": self.url_edit.text().strip(),
            "auth_type": "modern" if self.modern_auth_radio.isChecked() else "app",
            "username": self.user_edit.text().strip(),
            "password": self.pass_edit.text(),
            "client_id": self.client_id_edit.text().strip(),
            "client_secret": self.client_secret_edit.text()
        }
        return creds


class MigrationTab(QWidget):
    """Tab for migration options with integrated settings."""
    
    def __init__(self, parent=None):
        super(MigrationTab, self).__init__(parent)
        
        self.sp_integration = SharePointIntegration()
        self.is_authenticated = False
        self.document_libraries = []
        self.settings = {
            'upload_to_sharepoint': False,
            'destructive_mode': False,
            'preserve_timestamps': True,
            'ignore_hidden': True
        }  # Default settings
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Source selection
        source_group = QGroupBox("Source")
        source_layout = QHBoxLayout()
        
        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(True)
        source_layout.addWidget(self.source_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.select_source)
        source_layout.addWidget(browse_btn)
        
        source_group.setLayout(source_layout)
        main_layout.addWidget(source_group)
        
        # Create a horizontal splitter for settings and options
        options_layout = QHBoxLayout()
        
        # Target Options (using a stacked widget to switch between SharePoint and local targets)
        self.target_stack = QStackedWidget()
        
        # Stack page 1: SharePoint target
        sharepoint_widget = QWidget()
        sharepoint_layout = QVBoxLayout(sharepoint_widget)
        
        # SharePoint connection
        sp_connection_group = QGroupBox("SharePoint Connection")
        sp_layout = QVBoxLayout(sp_connection_group)
        
        # Status and login
        status_layout = QHBoxLayout()
        self.login_status = QLabel("Not connected")
        status_layout.addWidget(self.login_status)
        
        self.login_btn = QPushButton("Sign In")
        self.login_btn.clicked.connect(self.show_login_dialog)
        status_layout.addWidget(self.login_btn)
        
        sp_layout.addLayout(status_layout)
        
        # Library selection
        library_layout = QHBoxLayout()
        library_layout.addWidget(QLabel("Target Library:"))
        
        self.target_lib_combo = QComboBox()
        self.target_lib_combo.setEnabled(False)
        library_layout.addWidget(self.target_lib_combo)
        
        self.refresh_libs_btn = QPushButton("Refresh")
        self.refresh_libs_btn.clicked.connect(self.refresh_libraries)
        self.refresh_libs_btn.setEnabled(False)
        library_layout.addWidget(self.refresh_libs_btn)
        
        sp_layout.addLayout(library_layout)
        
        # Add to SharePoint widget
        sharepoint_layout.addWidget(sp_connection_group)
        sharepoint_layout.addStretch()
        
        # Stack page 2: Local target
        local_widget = QWidget()
        local_layout = QVBoxLayout(local_widget)
        
        local_group = QGroupBox("Local Target")
        local_target_layout = QHBoxLayout(local_group)
        
        self.target_edit = QLineEdit()
        self.target_edit.setReadOnly(True)
        local_target_layout.addWidget(self.target_edit)
        
        self.target_btn = QPushButton("Select Target...")
        self.target_btn.clicked.connect(self.select_target)
        local_target_layout.addWidget(self.target_btn)
        
        local_layout.addWidget(local_group)
        local_layout.addStretch()
        
        # Add both pages to stack
        self.target_stack.addWidget(sharepoint_widget)  # Index 0 - SharePoint
        self.target_stack.addWidget(local_widget)       # Index 1 - Local
        
        # Start with local target (this will be updated when settings are loaded)
        self.target_stack.setCurrentIndex(1)
        
        options_layout.addWidget(self.target_stack)
        
        # Add options layout to main layout
        main_layout.addLayout(options_layout)
        
        # Cleaning options (now separate from migration mode)
        options_group = QGroupBox("Cleaning Options")
        options_layout = QVBoxLayout()
        
        self.fix_names_cb = QCheckBox("Fix invalid SharePoint names")
        self.fix_names_cb.setChecked(True)
        options_layout.addWidget(self.fix_names_cb)
        
        self.fix_paths_cb = QCheckBox("Shorten paths exceeding SharePoint limits")
        self.fix_paths_cb.setChecked(True)
        options_layout.addWidget(self.fix_paths_cb)
        
        self.remove_dupes_cb = QCheckBox("Remove duplicate files")
        options_layout.addWidget(self.remove_dupes_cb)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Progress
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        main_layout.addLayout(progress_layout)
        
        # Start button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton("Start Migration")
        self.start_btn.clicked.connect(self.start_migration)
        self.start_btn.setFixedSize(QSize(200, 40))
        self.start_btn.setEnabled(False)
        button_layout.addWidget(self.start_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Add spacer at the bottom
        main_layout.addStretch()
        
        # Initialize UI based on default settings
        self.update_ui_for_settings()
    
    def select_source(self):
        """Select source directory"""
        source_dir = QFileDialog.getExistingDirectory(
            self, "Select Source Directory", "", QFileDialog.ShowDirsOnly
        )
        
        if source_dir:
            self.source_edit.setText(source_dir)
            self.update_start_button()
            
    def select_target(self):
        """Select target directory for local mode"""
        target_dir = QFileDialog.getExistingDirectory(
            self, "Select Target Directory", "", QFileDialog.ShowDirsOnly
        )
        
        if target_dir:
            self.target_edit.setText(target_dir)
            self.update_start_button()
    
    def on_settings_changed(self, settings):
        """Handle settings changes"""
        self.settings = settings
        self.update_ui_for_settings()
    
    def update_ui_for_settings(self):
        """Update the UI based on current settings"""
        # Update the target stack
        if self.settings['upload_to_sharepoint']:
            self.target_stack.setCurrentIndex(0)  # Show SharePoint options
        else:
            self.target_stack.setCurrentIndex(1)  # Show local target options
        
        # Update button state
        self.update_start_button()
    
    def show_login_dialog(self):
        """Show SharePoint login dialog"""
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            creds = dialog.get_credentials()
            
            # Validate URL
            if not creds["site_url"]:
                QMessageBox.warning(self, "Login Error", "SharePoint site URL is required.")
                return
                
            # Show progress during login
            self.status_label.setText("Authenticating...")
            self.progress_bar.setRange(0, 0)  # Indeterminate mode
            
            # Attempt authentication
            success = False
            if creds["auth_type"] == "modern":
                success = self.sp_integration.authenticate(
                    creds["site_url"], creds["username"], creds["password"]
                )
            else:
                success = self.sp_integration.authenticate_app_only(
                    creds["site_url"], creds["client_id"], creds["client_secret"]
                )
                
            # Reset progress
            self.progress_bar.setRange(0, 100)
            
            if success:
                self.is_authenticated = True
                self.login_status.setText(f"Connected to {creds['site_url']}")
                self.refresh_libraries()
                
                # Enable controls
                self.target_lib_combo.setEnabled(True)
                self.refresh_libs_btn.setEnabled(True)
                self.login_btn.setText("Sign Out")
                self.login_btn.clicked.disconnect()
                self.login_btn.clicked.connect(self.sign_out)
                
                self.update_start_button()
            else:
                QMessageBox.critical(self, "Authentication Failed", 
                                   "Failed to authenticate with SharePoint. Please check your credentials.")
                self.status_label.setText("Authentication failed")
    
    def sign_out(self):
        """Sign out from SharePoint"""
        if self.is_authenticated:
            self.sp_integration.disconnect()
            self.is_authenticated = False
            
            # Reset UI
            self.login_status.setText("Not connected")
            self.target_lib_combo.clear()
            self.target_lib_combo.setEnabled(False)
            self.refresh_libs_btn.setEnabled(False)
            self.login_btn.setText("Sign In")
            self.login_btn.clicked.disconnect()
            self.login_btn.clicked.connect(self.show_login_dialog)
            
            self.update_start_button()
    
    def refresh_libraries(self):
        """Refresh the list of document libraries"""
        if not self.is_authenticated:
            return
            
        # Set status
        self.status_label.setText("Loading document libraries...")
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        
        # Get libraries
        self.document_libraries = self.sp_integration.get_document_libraries()
        
        # Update combo box
        self.target_lib_combo.clear()
        if self.document_libraries:
            self.target_lib_combo.addItems(self.document_libraries)
            self.status_label.setText(f"Found {len(self.document_libraries)} document libraries")
        else:
            self.status_label.setText("No document libraries found")
            
        # Reset progress
        self.progress_bar.setRange(0, 100)
    
    def update_start_button(self):
        """Update the enabled state of the start button"""
        source_valid = bool(self.source_edit.text())
        
        if self.settings['upload_to_sharepoint']:
            # For SharePoint mode
            target_valid = self.is_authenticated and self.target_lib_combo.count() > 0
        else:
            # For local mode
            target_valid = bool(self.target_edit.text())
        
        self.start_btn.setEnabled(source_valid and target_valid)
    
    def start_migration(self):
        """Start the migration process"""
        # Validate source and target
        source_dir = self.source_edit.text()
        if not os.path.isdir(source_dir):
            QMessageBox.warning(self, "Error", "Invalid source directory.")
            return
        
        # Get migration options from settings and UI
        options = {
            'fix_names': self.fix_names_cb.isChecked(),
            'fix_paths': self.fix_paths_cb.isChecked(),
            'remove_duplicates': self.remove_dupes_cb.isChecked(),
            'destructive_mode': self.settings['destructive_mode'],
            'preserve_timestamps': self.settings['preserve_timestamps'],
            'ignore_hidden': self.settings['ignore_hidden']
        }
        
        # Create a data processor
        data_processor = DataProcessor()
        
        # Determine operation based on settings
        if self.settings['upload_to_sharepoint']:
            # SharePoint upload mode
            if not self.is_authenticated:
                QMessageBox.warning(self, "Error", "Not authenticated to SharePoint.")
                return
            
            target_lib = self.target_lib_combo.currentText()
            if not target_lib:
                QMessageBox.warning(self, "Error", "No target document library selected.")
                return
            
            # Set up process
            self.status_label.setText("Starting migration to SharePoint...")
            self.progress_bar.setValue(0)
            self.start_btn.setEnabled(False)
            
            # Define callbacks for the process
            def progress_callback(current, total):
                if total > 0:
                    percentage = int((current / total) * 100)
                    self.progress_bar.setValue(percentage)
                    self.status_label.setText(f"Processing file {current} of {total}...")
            
            def completion_callback(result):
                self.progress_bar.setValue(100)
                self.start_btn.setEnabled(True)
                
                if result.get('success', False):
                    self.status_label.setText("Migration completed successfully")
                    QMessageBox.information(
                        self, 
                        "Migration Complete", 
                        f"Migration to SharePoint completed successfully.\n"
                        f"Processed {result.get('total_processed', 0)} files with "
                        f"{result.get('issues_fixed', 0)} issues fixed."
                    )
                else:
                    self.status_label.setText("Migration failed")
                    QMessageBox.critical(
                        self,
                        "Migration Failed",
                        f"Migration to SharePoint failed: {result.get('error', 'Unknown error')}"
                    )
            
            def error_callback(error_message):
                self.status_label.setText("Migration failed")
                self.start_btn.setEnabled(True)
                QMessageBox.critical(
                    self,
                    "Migration Error",
                    f"An error occurred during migration: {error_message}"
                )
            
            # Start the migration
            data_processor.clean_and_upload(
                source_dir=source_dir,
                sharepoint_config={
                    'integration': self.sp_integration,
                    'library': target_lib
                },
                clean_options=options,
                callbacks={
                    'progress': progress_callback,
                    'cleaning_completed': completion_callback,
                    'error': error_callback
                }
            )
            
        else:
            # Local mode
            target_dir = self.target_edit.text()
            if not target_dir:
                QMessageBox.warning(self, "Error", "Please select a target directory.")
                return
            
            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)
            
            # Set up process
            self.status_label.setText("Starting local migration...")
            self.progress_bar.setValue(0)
            self.start_btn.setEnabled(False)
            
            # Define callbacks for the process
            def progress_callback(current, total):
                if total > 0:
                    percentage = int((current / total) * 100)
                    self.progress_bar.setValue(percentage)
                    self.status_label.setText(f"Processing file {current} of {total}...")
            
            def completion_callback(result):
                self.progress_bar.setValue(100)
                self.start_btn.setEnabled(True)
                
                if result.get('success', False):
                    self.status_label.setText("Migration completed successfully")
                    QMessageBox.information(
                        self, 
                        "Migration Complete", 
                        f"Files processed and saved to {target_dir}.\n"
                        f"Processed {result.get('total_processed', 0)} files with "
                        f"{result.get('issues_fixed', 0)} issues fixed."
                    )
                else:
                    self.status_label.setText("Migration failed")
                    QMessageBox.critical(
                        self,
                        "Migration Failed",
                        f"Migration failed: {result.get('error', 'Unknown error')}"
                    )
            
            def error_callback(error_message):
                self.status_label.setText("Migration failed")
                self.start_btn.setEnabled(True)
                QMessageBox.critical(
                    self,
                    "Migration Error",
                    f"An error occurred during migration: {error_message}"
                )
            
            # Start the migration
            data_processor.start_cleaning(
                source_dir=source_dir,
                target_dir=target_dir,
                clean_options=options,
                callbacks={
                    'progress': progress_callback,
                    'cleaning_completed': completion_callback,
                    'error': error_callback
                }
            )