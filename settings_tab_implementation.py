def create_settings_tab(self):
    """Create the settings tab"""
    try:
        # Create tab widget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create sections for different settings
        # 1. SharePoint Settings
        sp_group = QGroupBox("SharePoint Settings")
        sp_layout = QGridLayout(sp_group)
        
        # SharePoint URL
        sp_layout.addWidget(QLabel("SharePoint URL:"), 0, 0)
        self.sp_url_edit = QLineEdit()
        self.sp_url_edit.setPlaceholderText("https://contoso.sharepoint.com/sites/mysite")
        sp_layout.addWidget(self.sp_url_edit, 0, 1)
        
        # Authentication Type
        sp_layout.addWidget(QLabel("Authentication:"), 1, 0)
        self.auth_combo = QComboBox()
        self.auth_combo.addItems([
            "Modern Authentication (OAuth)",
            "Username and Password",
            "App-Only Authentication"
        ])
        self.auth_combo.currentIndexChanged.connect(self.auth_type_changed)
        sp_layout.addWidget(self.auth_combo, 1, 1)
        
        # Username
        sp_layout.addWidget(QLabel("Username:"), 2, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("user@example.com")
        sp_layout.addWidget(self.username_edit, 2, 1)
        
        # Password
        sp_layout.addWidget(QLabel("Password:"), 3, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        sp_layout.addWidget(self.password_edit, 3, 1)
        
        # Client ID
        self.client_id_label = QLabel("Client ID:")
        sp_layout.addWidget(self.client_id_label, 4, 0)
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setEnabled(False)
        sp_layout.addWidget(self.client_id_edit, 4, 1)
        
        # Client Secret
        self.client_secret_label = QLabel("Client Secret:")
        sp_layout.addWidget(self.client_secret_label, 5, 0)
        self.client_secret_edit = QLineEdit()
        self.client_secret_edit.setEchoMode(QLineEdit.Password)
        self.client_secret_edit.setEnabled(False)
        sp_layout.addWidget(self.client_secret_edit, 5, 1)
        
        # Test Connection
        sp_layout.addWidget(QLabel(""), 6, 0)  # Empty row
        self.test_connection_btn = QPushButton("Test Connection")
        self.test_connection_btn.clicked.connect(self.test_sharepoint_connection)
        sp_layout.addWidget(self.test_connection_btn, 7, 0, 1, 2)
        
        # Add group to layout
        layout.addWidget(sp_group)
        
        # 2. Scanning Options
        scan_group = QGroupBox("Scanning Options")
        scan_layout = QVBoxLayout(scan_group)
        
        # Thread Count
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Max Threads:"))
        self.thread_spinner = QSpinBox()
        self.thread_spinner.setRange(1, 16)
        self.thread_spinner.setValue(4)
        thread_layout.addWidget(self.thread_spinner)
        thread_layout.addStretch()
        scan_layout.addLayout(thread_layout)
        
        # File Size Limit
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Max File Size to Hash:"))
        self.max_file_size_spinner = QSpinBox()
        self.max_file_size_spinner.setRange(1, 1000)
        self.max_file_size_spinner.setValue(50)
        self.max_file_size_spinner.setSuffix(" MB")
        size_layout.addWidget(self.max_file_size_spinner)
        size_layout.addStretch()
        scan_layout.addLayout(size_layout)
        
        # Scan Options
        self.scan_hidden_check = QCheckBox("Scan Hidden Files and Folders")
        scan_layout.addWidget(self.scan_hidden_check)
        
        self.scan_system_check = QCheckBox("Scan System Files")
        scan_layout.addWidget(self.scan_system_check)
        
        self.follow_symlinks_check = QCheckBox("Follow Symbolic Links")
        scan_layout.addWidget(self.follow_symlinks_check)
        
        # Add group to layout
        layout.addWidget(scan_group)
        
        # 3. SharePoint Limits
        limits_group = QGroupBox("SharePoint Limits")
        limits_layout = QGridLayout(limits_group)
        
        # Max Path Length
        limits_layout.addWidget(QLabel("Max Path Length:"), 0, 0)
        self.max_path_spinner = QSpinBox()
        self.max_path_spinner.setRange(100, 400)
        self.max_path_spinner.setValue(256)
        self.max_path_spinner.setSuffix(" characters")
        limits_layout.addWidget(self.max_path_spinner, 0, 1)
        
        # Max Filename Length
        limits_layout.addWidget(QLabel("Max Filename Length:"), 1, 0)
        self.max_filename_spinner = QSpinBox()
        self.max_filename_spinner.setRange(50, 250)
        self.max_filename_spinner.setValue(128)
        self.max_filename_spinner.setSuffix(" characters")
        limits_layout.addWidget(self.max_filename_spinner, 1, 1)
        
        # Add group to layout
        layout.addWidget(limits_group)
        
        # 4. Logging Options
        log_group = QGroupBox("Logging Options")
        log_layout = QVBoxLayout(log_group)
        
        # Log Level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Log Level:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        level_layout.addWidget(self.log_level_combo)
        level_layout.addStretch()
        log_layout.addLayout(level_layout)
        
        # Log File Location
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(QLabel("Log File:"))
        self.log_path_edit = QLineEdit()
        self.log_path_edit.setReadOnly(True)
        log_path_layout.addWidget(self.log_path_edit)
        
        self.log_path_btn = QPushButton("Browse...")
        self.log_path_btn.clicked.connect(self.select_log_path)
        log_path_layout.addWidget(self.log_path_btn)
        
        log_layout.addLayout(log_path_layout)
        
        # Log Options
        self.console_log_check = QCheckBox("Log to Console")
        self.console_log_check.setChecked(True)
        log_layout.addWidget(self.console_log_check)
        
        self.file_log_check = QCheckBox("Log to File")
        self.file_log_check.setChecked(True)
        log_layout.addWidget(self.file_log_check)
        
        # Add group to layout
        layout.addWidget(log_group)
        
        # Save/Reset Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_btn)
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # Load settings
        self.load_settings()
        
        return tab
    except Exception as e:
        logger.error(f"Error creating settings tab: {e}")
        # Create an error tab
        error_tab = QWidget()
        error_layout = QVBoxLayout(error_tab)
        error_layout.addWidget(QLabel(f"Error creating settings tab: {str(e)}"))
        return error_tab

def auth_type_changed(self, index):
    """Handle authentication type change"""
    try:
        auth_type = self.auth_combo.currentText()
        
        # Show/hide appropriate fields based on auth type
        if "App-Only" in auth_type:
            # App-Only Auth - show client credentials, hide username/password
            self.username_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.client_id_edit.setEnabled(True)
            self.client_secret_edit.setEnabled(True)
        else:
            # Username/Password Auth - show username/password, hide client credentials
            self.username_edit.setEnabled(True)
            self.password_edit.setEnabled(True)
            self.client_id_edit.setEnabled(False)
            self.client_secret_edit.setEnabled(False)
    except Exception as e:
        logger.error(f"Error handling auth type change: {e}")

def select_log_path(self):
    """Select log file path"""
    try:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Log File",
            "",
            "Log Files (*.log);;Text Files (*.txt)"
        )
        
        if file_path:
            self.log_path_edit.setText(file_path)
    except Exception as e:
        logger.error(f"Error selecting log path: {e}")
        QMessageBox.critical(self, "File Selection Error", 
                           f"Error selecting log file: {str(e)}")

def test_sharepoint_connection(self):
    """Test the SharePoint connection with the provided credentials"""
    try:
        # Get credentials from UI
        site_url = self.sp_url_edit.text()
        auth_type = self.auth_combo.currentText()
        
        # Validate URL
        if not site_url:
            QMessageBox.warning(self, "Missing Information", 
                               "Please enter a SharePoint site URL")
            return
        
        # Show progress during connection test
        self.test_connection_btn.setEnabled(False)
        self.test_connection_btn.setText("Testing...")
        
        # Import SharePoint integration
        try:
            from infrastructure.sharepoint import SharePointIntegration
            sp_integration = SharePointIntegration()
            
            success = False
            
            # Connect based on auth type
            if "App-Only" in auth_type:
                client_id = self.client_id_edit.text()
                client_secret = self.client_secret_edit.text()
                
                # Validate credentials
                if not client_id or not client_secret:
                    QMessageBox.warning(self, "Missing Information", 
                                      "Please enter client ID and client secret")
                    return
                
                success = sp_integration.authenticate_modern(site_url, client_id, client_secret)
            else:
                username = self.username_edit.text()
                password = self.password_edit.text()
                
                # Validate credentials
                if not username or not password:
                    QMessageBox.warning(self, "Missing Information", 
                                      "Please enter username and password")
                    return
                
                success = sp_integration.authenticate(site_url, username, password)
            
            # Reset the button
            self.test_connection_btn.setEnabled(True)
            self.test_connection_btn.setText("Test Connection")
            
            # Show result
            if success:
                QMessageBox.information(self, "Connection Successful", 
                                      "Successfully connected to SharePoint")
            else:
                QMessageBox.critical(self, "Connection Failed", 
                                   "Failed to connect to SharePoint. Please check your credentials.")
        except ImportError as e:
            logger.error(f"Error importing SharePoint integration: {e}")
            QMessageBox.critical(self, "Module Error", 
                               "SharePoint integration module not available")
            self.test_connection_btn.setEnabled(True)
            self.test_connection_btn.setText("Test Connection")
    except Exception as e:
        logger.error(f"Error testing SharePoint connection: {e}")
        QMessageBox.critical(self, "Connection Error", 
                           f"Error testing connection: {str(e)}")
        self.test_connection_btn.setEnabled(True)
        self.test_connection_btn.setText("Test Connection")

def load_settings(self):
    """Load settings from QSettings"""
    try:
        from PyQt5.QtCore import QSettings
        settings = QSettings()
        
        # SharePoint Settings
        self.sp_url_edit.setText(settings.value("sharepoint/url", ""))
        auth_type = settings.value("sharepoint/auth_type", "Modern Authentication (OAuth)")
        self.auth_combo.setCurrentText(auth_type)
        self.username_edit.setText(settings.value("sharepoint/username", ""))
        self.password_edit.setText(settings.value("sharepoint/password", ""))
        self.client_id_edit.setText(settings.value("sharepoint/client_id", ""))
        self.client_secret_edit.setText(settings.value("sharepoint/client_secret", ""))
        
        # Scanning Options
        self.thread_spinner.setValue(int(settings.value("scanning/threads", 4)))
        self.max_file_size_spinner.setValue(int(settings.value("scanning/max_file_size", 50)))
        self.scan_hidden_check.setChecked(settings.value("scanning/scan_hidden", False) == "true")
        self.scan_system_check.setChecked(settings.value("scanning/scan_system", False) == "true")
        self.follow_symlinks_check.setChecked(settings.value("scanning/follow_symlinks", False) == "true")
        
        # SharePoint Limits
        self.max_path_spinner.setValue(int(settings.value("limits/max_path", 256)))
        self.max_filename_spinner.setValue(int(settings.value("limits/max_filename", 128)))
        
        # Logging Options
        self.log_level_combo.setCurrentText(settings.value("logging/level", "INFO"))
        self.log_path_edit.setText(settings.value("logging/path", ""))
        self.console_log_check.setChecked(settings.value("logging/console", True) == "true")
        self.file_log_check.setChecked(settings.value("logging/file", True) == "true")
        
        # Update UI based on loaded settings
        self.auth_type_changed(self.auth_combo.currentIndex())
    except Exception as e:
        logger.error(f"Error loading settings: {e}")

def save_settings(self):
    """Save settings to QSettings"""
    try:
        from PyQt5.QtCore import QSettings
        settings = QSettings()
        
        # SharePoint Settings
        settings.setValue("sharepoint/url", self.sp_url_edit.text())
        settings.setValue("sharepoint/auth_type", self.auth_combo.currentText())
        settings.setValue("sharepoint/username", self.username_edit.text())
        
        # For security, we might not want to store passwords in plain text
        # One option is to use a secure keyring or credential vault
        # For simplicity, we're storing it here, but in a real app you'd want to secure it
        settings.setValue("sharepoint/password", self.password_edit.text())
        
        settings.setValue("sharepoint/client_id", self.client_id_edit.text())
        settings.setValue("sharepoint/client_secret", self.client_secret_edit.text())
        
        # Scanning Options
        settings.setValue("scanning/threads", self.thread_spinner.value())
        settings.setValue("scanning/max_file_size", self.max_file_size_spinner.value())
        settings.setValue("scanning/scan_hidden", self.scan_hidden_check.isChecked())
        settings.setValue("scanning/scan_system", self.scan_system_check.isChecked())
        settings.setValue("scanning/follow_symlinks", self.follow_symlinks_check.isChecked())
        
        # SharePoint Limits
        settings.setValue("limits/max_path", self.max_path_spinner.value())
        settings.setValue("limits/max_filename", self.max_filename_spinner.value())
        
        # Logging Options
        settings.setValue("logging/level", self.log_level_combo.currentText())
        settings.setValue("logging/path", self.log_path_edit.text())
        settings.setValue("logging/console", self.console_log_check.isChecked())
        settings.setValue("logging/file", self.file_log_check.isChecked())
        
        # Apply logging settings immediately
        self.apply_logging_settings()
        
        # Show confirmation
        QMessageBox.information(self, "Settings Saved", 
                              "Settings have been saved successfully.")
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        QMessageBox.critical(self, "Save Error", 
                           f"Error saving settings: {str(e)}")

def reset_settings(self):
    """Reset settings to defaults"""
    try:
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.No:
            return
        
        # SharePoint Settings
        self.sp_url_edit.setText("")
        self.auth_combo.setCurrentText("Modern Authentication (OAuth)")
        self.username_edit.setText("")
        self.password_edit.setText("")
        self.client_id_edit.setText("")
        self.client_secret_edit.setText("")
        
        # Scanning Options
        self.thread_spinner.setValue(4)
        self.max_file_size_spinner.setValue(50)
        self.scan_hidden_check.setChecked(False)
        self.scan_system_check.setChecked(False)
        self.follow_symlinks_check.setChecked(False)
        
        # SharePoint Limits
        self.max_path_spinner.setValue(256)
        self.max_filename_spinner.setValue(128)
        
        # Logging Options
        self.log_level_combo.setCurrentText("INFO")
        self.log_path_edit.setText("")
        self.console_log_check.setChecked(True)
        self.file_log_check.setChecked(True)
        
        # Update UI
        self.auth_type_changed(self.auth_combo.currentIndex())
        
        # Show confirmation
        QMessageBox.information(self, "Settings Reset", 
                              "Settings have been reset to defaults.")
    except Exception as e:
        logger.error(f"Error resetting settings: {e}")
        QMessageBox.critical(self, "Reset Error", 
                           f"Error resetting settings: {str(e)}")

def apply_logging_settings(self):
    """Apply the current logging settings"""
    try:
        # Get logging settings
        log_level = self.log_level_combo.currentText()
        log_path = self.log_path_edit.text()
        console_log = self.console_log_check.isChecked()
        file_log = self.file_log_check.isChecked()
        
        # Convert string level to logging level
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        level = level_map.get(log_level, logging.INFO)
        
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Remove all handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set level
        root_logger.setLevel(level)
        
        # Add console handler if enabled
        if console_log:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # Add file handler if enabled and path is set
        if file_log and log_path:
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        logger.info(f"Applied logging settings: level={log_level}, console={console_log}, file={file_log}")
    except Exception as e:
        logger.error(f"Error applying logging settings: {e}")