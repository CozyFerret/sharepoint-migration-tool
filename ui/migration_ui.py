"""
Integration UI for SharePoint Migration Tool
This module provides the UI components for data view and migration options
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
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

# Import custom modules
from ui.enhanced_data_view import EnhancedDataView
from core.scanner import FileScanner
from core.data_processor import DataProcessor
from infrastructure.sharepoint import SharePointIntegration

logger = logging.getLogger(__name__)

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


class MigrationWorker(QThread):
    """Worker thread for data migration operations"""
    
    progress_update = pyqtSignal(int, str)
    finished = pyqtSignal(bool, list, dict)
    
    def __init__(self, mode, source_dir, target, sp_integration=None, options=None):
        super(MigrationWorker, self).__init__()
        self.mode = mode  # "clean" or "upload"
        self.source_dir = source_dir
        self.target = target  # Target directory or SharePoint library
        self.sp_integration = sp_integration
        self.options = options or {}
        
    def run(self):
        try:
            if self.mode == "clean":
                # Clean data and export to target directory
                self.progress_update.emit(10, "Starting data cleaning...")
                success, target_dir, issues = self.sp_integration.clean_and_export_data(
                    self.source_dir, 
                    self.target,
                    fix_names=self.options.get("fix_names", True),
                    fix_paths=self.options.get("fix_paths", True),
                    remove_duplicates=self.options.get("remove_duplicates", False)
                )
                
                self.progress_update.emit(100, "Cleaning completed")
                stats = {
                    "target_dir": target_dir,
                    "issues_count": len(issues)
                }
                self.finished.emit(success, issues, stats)
                
            elif self.mode == "upload":
                # Clean and upload to SharePoint
                self.progress_update.emit(10, "Starting data cleaning and preparing for upload...")
                
                success, issues, stats = self.sp_integration.clean_and_upload(
                    self.source_dir,
                    self.target,
                    fix_names=self.options.get("fix_names", True),
                    fix_paths=self.options.get("fix_paths", True),
                    remove_duplicates=self.options.get("remove_duplicates", False)
                )
                
                self.progress_update.emit(100, "Upload completed")
                self.finished.emit(success, issues, stats)
                
        except Exception as e:
            logger.error(f"Migration error: {str(e)}")
            self.progress_update.emit(100, f"Error: {str(e)}")
            self.finished.emit(False, [f"Critical error: {str(e)}"], {})


class ScanWorker(QThread):
    """Worker thread for scanning file systems"""
    
    progress_update = pyqtSignal(int, str)
    finished = pyqtSignal(bool, pd.DataFrame)
    
    def __init__(self, source_dir, analyzers=None):
        super(ScanWorker, self).__init__()
        self.source_dir = source_dir
        self.analyzers = analyzers or []
        
    def run(self):
        try:
            # Create scanner
            scanner = FileScanner(self.source_dir)
            
            # Set up processor with analyzers
            processor = DataProcessor()
            for analyzer in self.analyzers:
                processor.add_analyzer(analyzer)
                
            # Scan files
            self.progress_update.emit(10, "Scanning files...")
            file_list = scanner.scan()
            total_files = len(file_list)
            self.progress_update.emit(30, f"Analyzing {total_files} files...")
            
            # Process files through analyzers
            results = processor.process(file_list)
            
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            
            self.progress_update.emit(100, f"Scan completed. Found {len(df)} items.")
            self.finished.emit(True, df)
            
        except Exception as e:
            logger.error(f"Scan error: {str(e)}")
            self.progress_update.emit(100, f"Error: {str(e)}")
            self.finished.emit(False, pd.DataFrame())


class MigrationTab(QWidget):
    """Tab for data migration options and execution"""
    
    def __init__(self, parent=None):
        super(MigrationTab, self).__init__(parent)
        
        self.sp_integration = SharePointIntegration()
        self.is_authenticated = False
        self.document_libraries = []
        
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
        
        # Migration modes
        mode_group = QGroupBox("Migration Mode")
        mode_layout = QVBoxLayout()
        
        # Clean only mode
        self.clean_radio = QRadioButton("Clean Data Only")
        self.clean_radio.setChecked(True)
        self.clean_radio.toggled.connect(self.toggle_mode)
        mode_layout.addWidget(self.clean_radio)
        
        # Clean and target selection
        clean_layout = QHBoxLayout()
        self.target_edit = QLineEdit()
        self.target_edit.setReadOnly(True)
        clean_layout.addWidget(self.target_edit)
        
        self.target_btn = QPushButton("Select Target...")
        self.target_btn.clicked.connect(self.select_target)
        clean_layout.addWidget(self.target_btn)
        mode_layout.addLayout(clean_layout)
        
        # SharePoint upload mode
        self.upload_radio = QRadioButton("Clean and Upload to SharePoint")
        self.upload_radio.toggled.connect(self.toggle_mode)
        mode_layout.addWidget(self.upload_radio)
        
        # SharePoint connection
        sp_layout = QHBoxLayout()
        self.login_status = QLabel("Not connected")
        sp_layout.addWidget(self.login_status)
        
        self.login_btn = QPushButton("Sign In")
        self.login_btn.clicked.connect(self.show_login_dialog)
        sp_layout.addWidget(self.login_btn)
        
        self.target_lib_combo = QComboBox()
        self.target_lib_combo.setEnabled(False)
        sp_layout.addWidget(self.target_lib_combo)
        
        self.refresh_libs_btn = QPushButton("Refresh")
        self.refresh_libs_btn.clicked.connect(self.refresh_libraries)
        self.refresh_libs_btn.setEnabled(False)
        sp_layout.addWidget(self.refresh_libs_btn)
        
        mode_layout.addLayout(sp_layout)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)
        
        # Cleaning options
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
        
    def select_source(self):
        """Select source directory"""
        source_dir = QFileDialog.getExistingDirectory(
            self, "Select Source Directory", "", QFileDialog.ShowDirsOnly
        )
        
        if source_dir:
            self.source_edit.setText(source_dir)
            self.update_start_button()
            
    def select_target(self):
        """Select target directory for clean only mode"""
        target_dir = QFileDialog.getExistingDirectory(
            self, "Select Target Directory", "", QFileDialog.ShowDirsOnly
        )
        
        if target_dir:
            self.target_edit.setText(target_dir)
            self.update_start_button()
            
    def toggle_mode(self, checked):
        """Toggle between clean only and upload modes"""
        # Enable/disable target selection
        self.target_edit.setEnabled(self.clean_radio.isChecked())
        self.target_btn.setEnabled(self.clean_radio.isChecked())
        
        # Enable/disable SharePoint controls
        sp_enabled = self.upload_radio.isChecked()
        self.login_btn.setEnabled(sp_enabled)
        self.target_lib_combo.setEnabled(sp_enabled and self.is_authenticated)
        self.refresh_libs_btn.setEnabled(sp_enabled and self.is_authenticated)
        
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
                success = self.sp_integration.authenticate_modern(
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
        
        if self.clean_radio.isChecked():
            target_valid = bool(self.target_edit.text())
        else:  # Upload mode
            target_valid = self.is_authenticated and self.target_lib_combo.count() > 0
            
        self.start_btn.setEnabled(source_valid and target_valid)
        
    def start_migration(self):
        """Start the migration process"""
        # Validate source and target
        source_dir = self.source_edit.text()
        if not os.path.isdir(source_dir):
            QMessageBox.warning(self, "Error", "Invalid source directory.")
            return
            
        # Get migration options
        options = {
            "fix_names": self.fix_names_cb.isChecked(),
            "fix_paths": self.fix_paths_cb.isChecked(),
            "remove_duplicates": self.remove_dupes_cb.isChecked()
        }
        
        # Set up worker thread based on mode
        if self.clean_radio.isChecked():
            # Clean only mode
            target_dir = self.target_edit.text()
            if not os.path.isdir(target_dir):
                try:
                    os.makedirs(target_dir, exist_ok=True)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not create target directory: {str(e)}")
                    return
                    
            worker = MigrationWorker(
                "clean", source_dir, target_dir, 
                sp_integration=self.sp_integration, options=options
            )
        else:
            # Upload mode
            if not self.is_authenticated:
                QMessageBox.warning(self, "Error", "Not authenticated to SharePoint.")
                return
                
            target_lib = self.target_lib_combo.currentText()
            if not target_lib:
                QMessageBox.warning(self, "Error", "No target document library selected.")
                return
                
            worker = MigrationWorker(
                "upload", source_dir, target_lib,
                sp_integration=self.sp_integration, options=options
            )
        
        # Connect signals
        worker.progress_update.connect(self.update_progress)
        worker.finished.connect(self.migration_finished)
        
        # Disable UI during migration
        self.setEnabled(False)
        
        # Start worker
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting migration...")
        worker.start()
        
    def update_progress(self, value, message):
        """Update progress bar and status message"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
    def migration_finished(self, success, issues, stats):
        """Handle migration completion"""
        # Re-enable UI
        self.setEnabled(True)
        
        if success:
            mode = "cleaning" if self.clean_radio.isChecked() else "migration"
            message = f"{mode.capitalize()} completed successfully."
            
            if issues:
                message += f" {len(issues)} issues were detected and fixed."
                
            QMessageBox.information(self, "Success", message)
            
            # Show detailed statistics
            if "target_dir" in stats:
                self.status_label.setText(f"Files cleaned and saved to {stats['target_dir']}")
            elif "uploaded_files" in stats:
                self.status_label.setText(
                    f"Uploaded {stats['uploaded_files']} of {stats['total_files']} files "
                    f"({stats['failed_files']} failed)"
                )
        else:
            QMessageBox.critical(
                self, "Error", 
                f"Migration failed with {len(issues)} errors. See log for details."
            )
            self.status_label.setText("Migration failed")


class AnalysisTab(QWidget):
    """Tab for analyzing file systems and viewing results"""
    
    def __init__(self, parent=None):
        super(AnalysisTab, self).__init__(parent)
        
        from core.analyzers.name_validator import NameValidator
        from core.analyzers.path_analyzer import PathAnalyzer
        from core.analyzers.duplicate_finder import DuplicateFinder
        
        # Set up analyzers
        self.analyzers = [
            NameValidator(),
            PathAnalyzer(),
            DuplicateFinder()
        ]
        
        self.scan_results = None
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Source selection
        source_layout = QHBoxLayout()
        source_label = QLabel("Source Directory:")
        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.select_source)
        
        scan_btn = QPushButton("Start Scan")
        scan_btn.clicked.connect(self.start_scan)
        
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_edit)
        source_layout.addWidget(browse_btn)
        source_layout.addWidget(scan_btn)
        main_layout.addLayout(source_layout)
        
        # Analysis options
        options_group = QGroupBox("Analysis Options")
        options_layout = QVBoxLayout()
        
        self.name_check = QCheckBox("Check for invalid SharePoint names")
        self.name_check.setChecked(True)
        options_layout.addWidget(self.name_check)
        
        self.path_check = QCheckBox("Check for path length issues")
        self.path_check.setChecked(True)
        options_layout.addWidget(self.path_check)
        
        self.dupes_check = QCheckBox("Find duplicate files")
        self.dupes_check.setChecked(True)
        options_layout.addWidget(self.dupes_check)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Progress indicator
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        main_layout.addLayout(progress_layout)
        
        # Results view
        results_label = QLabel("Scan Results:")
        main_layout.addWidget(results_label)
        
        self.enhanced_view = EnhancedDataView()
        main_layout.addWidget(self.enhanced_view)
        
    def select_source(self):
        """Select source directory for analysis"""
        source_dir = QFileDialog.getExistingDirectory(
            self, "Select Source Directory", "", QFileDialog.ShowDirsOnly
        )
        
        if source_dir:
            self.source_edit.setText(source_dir)
            
    def start_scan(self):
        """Start scanning the selected directory"""
        source_dir = self.source_edit.text()
        if not source_dir or not os.path.isdir(source_dir):
            QMessageBox.warning(self, "Error", "Please select a valid source directory.")
            return
            
        # Prepare list of active analyzers
        active_analyzers = []
        if self.name_check.isChecked():
            active_analyzers.append(self.analyzers[0])  # NameValidator
        if self.path_check.isChecked():
            active_analyzers.append(self.analyzers[1])  # PathAnalyzer
        if self.dupes_check.isChecked():
            active_analyzers.append(self.analyzers[2])  # DuplicateFinder
            
        if not active_analyzers:
            QMessageBox.warning(self, "Error", "Please select at least one analysis option.")
            return
            
        # Create and start worker thread
        worker = ScanWorker(source_dir, active_analyzers)
        worker.progress_update.connect(self.update_progress)
        worker.finished.connect(self.scan_finished)
        
        # Disable UI during scan
        self.setEnabled(False)
        
        # Start worker
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting scan...")
        worker.start()
        
    def update_progress(self, value, message):
        """Update progress bar and status message"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
    def scan_finished(self, success, results_df):
        """Handle scan completion"""
        # Re-enable UI
        self.setEnabled(True)
        
        if success and not results_df.empty:
            self.scan_results = results_df
            self.enhanced_view.set_data(results_df)
            
            # Update status
            self.status_label.setText(f"Scan completed. Found {len(results_df)} items.")
        else:
            QMessageBox.warning(
                self, "Scan Error", 
                "Failed to complete the scan or no results found."
            )
            self.status_label.setText("Scan failed")


class MigrationToolUI(QWidget):
    """Main UI for the SharePoint Migration Tool"""
    
    def __init__(self, parent=None):
        super(MigrationToolUI, self).__init__(parent)
        self.setWindowTitle("SharePoint Migration Tool")
        self.resize(900, 700)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("SharePoint Migration Tool")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Add version info
        version_label = QLabel("v1.1.0")
        version_font = QFont()
        version_font.setItalic(True)
        version_label.setFont(version_font)
        header_layout.addWidget(version_label)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Add tabs
        self.analysis_tab = AnalysisTab()
        tab_widget.addTab(self.analysis_tab, "Analysis")
        
        self.migration_tab = MigrationTab()
        tab_widget.addTab(self.migration_tab, "Migration")
        
        main_layout.addWidget(tab_widget)
        
        # Footer
        footer_layout = QHBoxLayout()
        footer_label = QLabel("© 2025 SharePoint Migration Tool")
        footer_layout.addWidget(footer_label)
        footer_layout.addStretch()
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_label = QLabel(f"Date: {current_date}")
        footer_layout.addWidget(date_label)
        
        main_layout.addLayout(footer_layout)


# For testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MigrationToolUI()
    window.show()
    sys.exit(app.exec_())