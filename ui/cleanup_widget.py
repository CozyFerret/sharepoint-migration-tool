from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QGridLayout, QGroupBox, QPushButton,
                           QRadioButton, QCheckBox, QButtonGroup, QFileDialog,
                           QTabWidget, QProgressBar, QComboBox, QSpinBox,
                           QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView,
                           QMessageBox, QSplitter, QScrollArea, QToolButton)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QThread, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

class CleanupWorker(QThread):
    """Worker thread for performing cleanup operations"""
    progress_updated = pyqtSignal(int, int)  # Signal for progress (current, total)
    cleanup_completed = pyqtSignal(dict)  # Signal for completion with results
    error_occurred = pyqtSignal(str)  # Signal for errors
    
    def __init__(self, options):
        super().__init__()
        self.options = options
    
    def run(self):
        """Main execution method"""
        try:
            # In a real implementation, this would call your cleanup methods
            # For now, we'll simulate progress
            total_files = self.options.get('total_files', 100)
            
            for i in range(total_files):
                # Simulate processing a file
                import time
                time.sleep(0.05)  # Simulate work
                
                # Update progress
                self.progress_updated.emit(i + 1, total_files)
                
                # Check for interruption
                if self.isInterruptionRequested():
                    self.cleanup_completed.emit({
                        'status': 'cancelled',
                        'processed_files': i + 1,
                        'total_files': total_files,
                        'fixed_issues': int(i * 0.7),  # 70% of processed files had fixes
                    })
                    return
            
            # Emit completion signal with results
            self.cleanup_completed.emit({
                'status': 'completed',
                'processed_files': total_files,
                'total_files': total_files,
                'fixed_issues': int(total_files * 0.7),  # 70% of files had fixes
            })
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class CleanupWidget(QWidget):
    """
    Widget for fixing issues and preparing files for SharePoint migration.
    Provides options for fixing different issue types and uploading to SharePoint.
    """
    
    # Define signals
    cleanup_requested = pyqtSignal(dict)  # Signal for cleanup request with options
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.scan_results = None
        self.cleanup_worker = None
        
    def init_ui(self):
        """Initialize the cleanup widget UI components"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tabs for different cleanup modes
        self.tabs = QTabWidget()
        
        # Create tabs for cleanup modes
        self.manual_tab = QWidget()
        self.automatic_tab = QWidget()
        self.advanced_tab = QWidget()
        
        # Setup tab contents
        self.setup_manual_tab()
        self.setup_automatic_tab()
        self.setup_advanced_tab()
        
        # Add tabs to tab widget
        self.tabs.addTab(self.manual_tab, "Manual Mode")
        self.tabs.addTab(self.automatic_tab, "Automatic Mode")
        self.tabs.addTab(self.advanced_tab, "Advanced Options")
        
        # Add tabs to main layout
        self.main_layout.addWidget(self.tabs)
        
        # Create progress section
        self.progress_group = QGroupBox("Cleanup Progress")
        progress_layout = QVBoxLayout(self.progress_group)
        
        # Add status label
        self.status_label = QLabel("Ready to start cleanup")
        progress_layout.addWidget(self.status_label)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # Add details label
        self.details_label = QLabel("No cleanup in progress")
        progress_layout.addWidget(self.details_label)
        
        # Add control buttons
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Cleanup")
        self.start_button.clicked.connect(self.start_cleanup)
        self.start_button.setEnabled(False)  # Disabled until we have scan results
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_cleanup)
        self.cancel_button.setEnabled(False)  # Disabled until cleanup starts
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.cancel_button)
        
        progress_layout.addLayout(buttons_layout)
        
        # Add progress group to main layout
        self.main_layout.addWidget(self.progress_group)
        
    def setup_manual_tab(self):
        """Setup the manual cleanup mode tab"""
        layout = QVBoxLayout(self.manual_tab)
        
        # Create description
        description = QLabel(
            "Manual mode allows you to fix issues and save cleaned files to a new location. "
            "Original files remain untouched."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create splitter for options and preview
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Options
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)
        
        # Fix options
        fix_group = QGroupBox("Fix Options")
        fix_layout = QVBoxLayout(fix_group)
        
        self.fix_path_length_check = QCheckBox("Fix Path Length Issues")
        self.fix_path_length_check.setChecked(True)
        
        self.fix_illegal_chars_check = QCheckBox("Fix Illegal Characters")
        self.fix_illegal_chars_check.setChecked(True)
        
        self.fix_reserved_names_check = QCheckBox("Fix Reserved Names")
        self.fix_reserved_names_check.setChecked(True)
        
        self.fix_duplicates_check = QCheckBox("Handle Duplicate Files")
        self.fix_duplicates_check.setChecked(True)
        
        fix_layout.addWidget(self.fix_path_length_check)
        fix_layout.addWidget(self.fix_illegal_chars_check)
        fix_layout.addWidget(self.fix_reserved_names_check)
        fix_layout.addWidget(self.fix_duplicates_check)
        
        options_layout.addWidget(fix_group)
        
        # Fix strategies
        strategy_group = QGroupBox("Fix Strategies")
        strategy_layout = QVBoxLayout(strategy_group)
        
        # Path length strategy
        path_strategy_layout = QHBoxLayout()
        path_strategy_layout.addWidget(QLabel("Path Length Strategy:"))
        
        self.path_strategy_combo = QComboBox()
        self.path_strategy_combo.addItems([
            "Shorten Folder Names",
            "Flatten Structure",
            "Smart Path Reduction"
        ])
        
        path_strategy_layout.addWidget(self.path_strategy_combo)
        strategy_layout.addLayout(path_strategy_layout)
        
        # Illegal characters strategy
        char_strategy_layout = QHBoxLayout()
        char_strategy_layout.addWidget(QLabel("Illegal Character Strategy:"))
        
        self.char_strategy_combo = QComboBox()
        self.char_strategy_combo.addItems([
            "Replace with Similar",
            "Remove Characters",
            "Replace with Underscore"
        ])
        
        char_strategy_layout.addWidget(self.char_strategy_combo)
        strategy_layout.addLayout(char_strategy_layout)
        
        # Duplicates strategy
        dup_strategy_layout = QHBoxLayout()
        dup_strategy_layout.addWidget(QLabel("Duplicates Strategy:"))
        
        self.dup_strategy_combo = QComboBox()
        self.dup_strategy_combo.addItems([
            "Keep First Occurrence",
            "Create Shortcuts",
            "Rename and Keep All"
        ])
        
        dup_strategy_layout.addWidget(self.dup_strategy_combo)
        strategy_layout.addLayout(dup_strategy_layout)
        
        options_layout.addWidget(strategy_group)
        
        # Target location
        target_group = QGroupBox("Target Location")
        target_layout = QHBoxLayout(target_group)
        
        self.target_path_label = QLabel("Not selected")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_target_folder)
        
        target_layout.addWidget(QLabel("Save to:"))
        target_layout.addWidget(self.target_path_label, 1)
        target_layout.addWidget(browse_button)
        
        options_layout.addWidget(target_group)
        
        # Add stretch to push everything to the top
        options_layout.addStretch()
        
        # Right side - Preview
        preview_group = QGroupBox("Cleanup Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Add tree widget for preview
        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderLabels(["Original Path", "New Path"])
        self.preview_tree.setColumnWidth(0, 300)
        self.preview_tree.setAlternatingRowColors(True)
        
        preview_layout.addWidget(self.preview_tree)
        
        # Add preview button
        preview_button = QPushButton("Generate Preview")
        preview_button.clicked.connect(self.generate_preview)
        preview_layout.addWidget(preview_button)
        
        # Add widgets to splitter
        splitter.addWidget(options_widget)
        splitter.addWidget(preview_group)
        
        # Set initial splitter sizes
        splitter.setSizes([400, 600])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
    def setup_automatic_tab(self):
        """Setup the automatic cleanup mode tab with SharePoint integration"""
        layout = QVBoxLayout(self.automatic_tab)
        
        # Create description
        description = QLabel(
            "Automatic mode fixes issues and uploads files directly to SharePoint Online. "
            "This requires SharePoint credentials and site information."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create splitter for connection and settings
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Connection
        connection_widget = QWidget()
        connection_layout = QVBoxLayout(connection_widget)
        
        # SharePoint connection group
        connection_group = QGroupBox("SharePoint Connection")
        connection_grid = QGridLayout(connection_group)
        
        # SharePoint URL
        connection_grid.addWidget(QLabel("SharePoint URL:"), 0, 0)
        self.sp_url_input = QLineEdit()
        self.sp_url_input.setPlaceholderText("https://contoso.sharepoint.com/sites/mysite")
        connection_grid.addWidget(self.sp_url_input, 0, 1)
        
        # Authentication Type
        connection_grid.addWidget(QLabel("Authentication:"), 1, 0)
        self.auth_combo = QComboBox()
        self.auth_combo.addItems([
            "Microsoft Account",
            "Office 365",
            "App Registration",
            "Certificate"
        ])
        connection_grid.addWidget(self.auth_combo, 1, 1)
        
        # Username/Client ID
        self.username_label = QLabel("Username:")
        connection_grid.addWidget(self.username_label, 2, 0)
        self.username_input = QLineEdit()
        connection_grid.addWidget(self.username_input, 2, 1)
        
        # Password/Client Secret
        self.password_label = QLabel("Password:")
        connection_grid.addWidget(self.password_label, 3, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        connection_grid.addWidget(self.password_input, 3, 1)
        
        # Connect button
        self.connect_button = QPushButton("Connect to SharePoint")
        self.connect_button.clicked.connect(self.connect_to_sharepoint)
        connection_grid.addWidget(self.connect_button, 4, 0, 1, 2)
        
        # Connection status
        self.connection_status = QLabel("Not connected")
        self.connection_status.setStyleSheet("color: red;")
        connection_grid.addWidget(self.connection_status, 5, 0, 1, 2)
        
        connection_layout.addWidget(connection_group)
        
        # Add a libraries selection group (initially disabled)
        libraries_group = QGroupBox("Target Library")
        libraries_group.setEnabled(False)
        self.libraries_group = libraries_group  # Store reference to enable later
        
        libraries_layout = QVBoxLayout(libraries_group)
        
        # Library selector
        library_layout = QHBoxLayout()
        library_layout.addWidget(QLabel("Document Library:"))
        
        self.library_combo = QComboBox()
        self.library_combo.setEnabled(False)
        library_layout.addWidget(self.library_combo)
        
        libraries_layout.addLayout(library_layout)
        
        # Folder selector
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Target Folder:"))
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Leave empty for root")
        self.folder_input.setEnabled(False)
        folder_layout.addWidget(self.folder_input)
        
        self.browse_sp_button = QPushButton("Browse...")
        self.browse_sp_button.setEnabled(False)
        self.browse_sp_button.clicked.connect(self.browse_sharepoint_folders)
        folder_layout.addWidget(self.browse_sp_button)
        
        libraries_layout.addLayout(folder_layout)
        
        connection_layout.addWidget(libraries_group)
        
        # Add stretch to push everything to the top
        connection_layout.addStretch()
        
        # Right side - Upload settings
        settings_group = QGroupBox("Upload Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Fix options (same as manual tab)
        fix_group = QGroupBox("Fix Options")
        fix_layout = QVBoxLayout(fix_group)
        
        self.auto_fix_path_length_check = QCheckBox("Fix Path Length Issues")
        self.auto_fix_path_length_check.setChecked(True)
        
        self.auto_fix_illegal_chars_check = QCheckBox("Fix Illegal Characters")
        self.auto_fix_illegal_chars_check.setChecked(True)
        
        self.auto_fix_reserved_names_check = QCheckBox("Fix Reserved Names")
        self.auto_fix_reserved_names_check.setChecked(True)
        
        self.auto_fix_duplicates_check = QCheckBox("Handle Duplicate Files")
        self.auto_fix_duplicates_check.setChecked(True)
        
        fix_layout.addWidget(self.auto_fix_path_length_check)
        fix_layout.addWidget(self.auto_fix_illegal_chars_check)
        fix_layout.addWidget(self.auto_fix_reserved_names_check)
        fix_layout.addWidget(self.auto_fix_duplicates_check)
        
        settings_layout.addWidget(fix_group)
        
        # Upload options
        upload_group = QGroupBox("Upload Options")
        upload_layout = QVBoxLayout(upload_group)
        
        self.preserve_timestamps_check = QCheckBox("Preserve Original Timestamps")
        self.preserve_timestamps_check.setChecked(True)
        
        self.preserve_user_check = QCheckBox("Preserve Created By/Modified By")
        self.preserve_user_check.setChecked(True)
        
        self.upload_only_fixed_check = QCheckBox("Upload Only Files with Issues")
        self.upload_only_fixed_check.setChecked(False)
        
        self.overwrite_existing_check = QCheckBox("Overwrite Existing Files")
        self.overwrite_existing_check.setChecked(False)
        
        upload_layout.addWidget(self.preserve_timestamps_check)
        upload_layout.addWidget(self.preserve_user_check)
        upload_layout.addWidget(self.upload_only_fixed_check)
        upload_layout.addWidget(self.overwrite_existing_check)
        
        settings_layout.addWidget(upload_group)
        
        # Throttling options
        throttle_group = QGroupBox("Throttling")
        throttle_layout = QGridLayout(throttle_group)
        
        throttle_layout.addWidget(QLabel("Concurrent Uploads:"), 0, 0)
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 10)
        self.concurrent_spin.setValue(3)
        throttle_layout.addWidget(self.concurrent_spin, 0, 1)
        
        throttle_layout.addWidget(QLabel("Retry Count:"), 1, 0)
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 5)
        self.retry_spin.setValue(3)
        throttle_layout.addWidget(self.retry_spin, 1, 1)
        
        settings_layout.addWidget(throttle_group)
        
        # Add stretch to push everything to the top
        settings_layout.addStretch()
        
        # Add widgets to splitter
        splitter.addWidget(connection_widget)
        splitter.addWidget(settings_group)
        
        # Set initial splitter sizes
        splitter.setSizes([500, 500])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
    def setup_advanced_tab(self):
        """Setup the advanced options tab for specialized configurations"""
        layout = QVBoxLayout(self.advanced_tab)
        
        # Create description
        description = QLabel(
            "Advanced options provide more control over specific fix strategies "
            "and customized replacement rules."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create scroll area for many options
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Path length options
        path_group = QGroupBox("Path Length Options")
        path_layout = QVBoxLayout(path_group)
        
        # Maximum path length
        max_path_layout = QHBoxLayout()
        max_path_layout.addWidget(QLabel("Max Path Length:"))
        
        self.max_path_spin = QSpinBox()
        self.max_path_spin.setRange(100, 400)
        self.max_path_spin.setValue(256)  # SharePoint's default limit
        self.max_path_spin.setSuffix(" characters")
        
        max_path_layout.addWidget(self.max_path_spin)
        max_path_layout.addStretch()
        
        path_layout.addLayout(max_path_layout)
        
        # Path shortening strategy options
        self.shorten_folder_names_check = QCheckBox("Shorten Folder Names to Maximum Length")
        self.shorten_folder_names_check.setChecked(True)
        
        folder_length_layout = QHBoxLayout()
        folder_length_layout.addWidget(QLabel("    Maximum Folder Name Length:"))
        
        self.max_folder_spin = QSpinBox()
        self.max_folder_spin.setRange(8, 64)
        self.max_folder_spin.setValue(32)
        self.max_folder_spin.setSuffix(" characters")
        
        folder_length_layout.addWidget(self.max_folder_spin)
        folder_length_layout.addStretch()
        
        self.truncate_middle_check = QCheckBox("Truncate Middle of Names Instead of End")
        
        self.flatten_deep_check = QCheckBox("Flatten Excessively Deep Folder Structures")
        self.flatten_deep_check.setChecked(True)
        
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("    Maximum Folder Depth:"))
        
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(3, 15)
        self.max_depth_spin.setValue(8)
        self.max_depth_spin.setSuffix(" levels")
        
        depth_layout.addWidget(self.max_depth_spin)
        depth_layout.addStretch()
        
        # Add all path options
        path_layout.addWidget(self.shorten_folder_names_check)
        path_layout.addLayout(folder_length_layout)
        path_layout.addWidget(self.truncate_middle_check)
        path_layout.addWidget(self.flatten_deep_check)
        path_layout.addLayout(depth_layout)
        
        scroll_layout.addWidget(path_group)
        
        # Character replacement options
        char_group = QGroupBox("Character Replacement Rules")
        char_layout = QVBoxLayout(char_group)
        
        # Replacement table
        self.replacement_tree = QTreeWidget()
        self.replacement_tree.setHeaderLabels(["Illegal Character", "Replacement"])
        self.replacement_tree.setColumnWidth(0, 150)
        
        # Add default replacements
        replacements = [
            ["?", "-"],
            ["*", "×"],
            [":", "."],
            ["/", "-"],
            ["\\", "-"],
            ["|", "l"],
            ["<", "("],
            [">", ")"],
            ["\"", "'"],
            ["%", "pct"]
        ]
        
        for chars in replacements:
            item = QTreeWidgetItem(self.replacement_tree)
            item.setText(0, chars[0])
            item.setText(1, chars[1])
        
        char_layout.addWidget(self.replacement_tree)
        
        # Add buttons for managing replacements
        replacement_buttons = QHBoxLayout()
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_replacement)
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_replacements)
        
        replacement_buttons.addWidget(edit_button)
        replacement_buttons.addStretch()
        replacement_buttons.addWidget(reset_button)
        
        char_layout.addLayout(replacement_buttons)
        
        scroll_layout.addWidget(char_group)
        
        # Duplicate handling options
        dup_group = QGroupBox("Duplicate File Handling")
        dup_layout = QVBoxLayout(dup_group)
        
        self.keep_newest_check = QCheckBox("Keep Newest Version of Duplicates")
        
        self.consider_name_check = QCheckBox("Consider Filename When Detecting Duplicates")
        self.consider_name_check.setChecked(True)
        
        self.ignore_empty_check = QCheckBox("Ignore Empty Files")
        self.ignore_empty_check.setChecked(True)
        
        # Similarity threshold for fuzzy matching
        similarity_layout = QHBoxLayout()
        similarity_layout.addWidget(QLabel("Similarity Threshold:"))
        
        self.similarity_spin = QSpinBox()
        self.similarity_spin.setRange(80, 100)
        self.similarity_spin.setValue(95)
        self.similarity_spin.setSuffix("%")
        
        similarity_layout.addWidget(self.similarity_spin)
        similarity_layout.addStretch()
        
        # Add all duplicate options
        dup_layout.addWidget(self.keep_newest_check)
        dup_layout.addWidget(self.consider_name_check)
        dup_layout.addWidget(self.ignore_empty_check)
        dup_layout.addLayout(similarity_layout)
        
        scroll_layout.addWidget(dup_group)
        
        # Logging options
        log_group = QGroupBox("Logging Options")
        log_layout = QVBoxLayout(log_group)
        
        self.enable_logging_check = QCheckBox("Enable Detailed Logging")
        self.enable_logging_check.setChecked(True)
        
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(QLabel("Log File:"))
        
        self.log_path_input = QLineEdit()
        self.log_path_input.setPlaceholderText("cleanup_log.txt in output directory")
        
        log_path_button = QPushButton("Browse...")
        log_path_button.clicked.connect(self.browse_log_file)
        
        log_path_layout.addWidget(self.log_path_input, 1)
        log_path_layout.addWidget(log_path_button)
        
        log_layout.addWidget(self.enable_logging_check)
        log_layout.addLayout(log_path_layout)
        
        scroll_layout.addWidget(log_group)
        
        # Add stretch to bottom
        scroll_layout.addStretch()
        
        # Set the scroll widget
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
    
    def browse_target_folder(self):
        """Open a folder dialog to select the target folder"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Target Folder", 
            "", 
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.target_path_label.setText(folder)
            
            # Enable start button if we have scan results
            if self.scan_results:
                self.start_button.setEnabled(True)
    
    def browse_log_file(self):
        """Open a file dialog to select the log file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Log File",
            "",
            "Text Files (*.txt);;Log Files (*.log)"
        )
        if file_path:
            self.log_path_input.setText(file_path)
    
    def generate_preview(self):
        """Generate a preview of the cleanup changes"""
        if not self.scan_results:
            return
        
        # Clear preview tree
        self.preview_tree.clear()
        
        # Mock data for preview (would be generated from actual fix strategies)
        preview_data = [
            # Path length issues
            {"original": "C:/very/long/path/to/some/deeply/nested/folder/structure/with/many/levels/file.txt",
             "new": "C:/cleaned/path/.../file.txt",
             "issue": "Path Length"},
            
            # Illegal character issues
            {"original": "C:/path/to/file-with-illegal*character?.txt",
             "new": "C:/path/to/file-with-illegal×character-.txt",
             "issue": "Illegal Characters"},
            
            # Reserved name issues
            {"original": "C:/path/to/CON.txt",
             "new": "C:/path/to/CON_.txt",
             "issue": "Reserved Name"},
            
            # Duplicate issues
            {"original": "C:/path/to/duplicate.txt",
             "new": "C:/path/to/duplicate_1.txt",
             "issue": "Duplicate"}
        ]
        
        # Add items to tree
        for item_data in preview_data:
            tree_item = QTreeWidgetItem(self.preview_tree)
            tree_item.setText(0, item_data["original"])
            tree_item.setText(1, item_data["new"])
            
            # Set color based on issue type
            if item_data["issue"] == "Path Length":
                tree_item.setBackground(0, QColor(255, 230, 230))  # Light red
            elif item_data["issue"] == "Illegal Characters":
                tree_item.setBackground(0, QColor(230, 255, 230))  # Light green
            elif item_data["issue"] == "Reserved Name":
                tree_item.setBackground(0, QColor(230, 230, 255))  # Light blue
            else:  # Duplicate
                tree_item.setBackground(0, QColor(255, 255, 230))  # Light yellow
        
        # Enable start button if we have a target path
        if self.target_path_label.text() != "Not selected":
            self.start_button.setEnabled(True)
    
    def edit_replacement(self):
        """Edit the selected character replacement rule"""
        selected_items = self.replacement_tree.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        
        # Get current values
        illegal_char = item.text(0)
        replacement = item.text(1)
        
        # Create a simple dialog for editing
        from PyQt5.QtWidgets import QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Replacement Rule")
        dialog_layout = QVBoxLayout(dialog)
        
        # Add input fields
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("Illegal Character:"), 0, 0)
        char_input = QLineEdit(illegal_char)
        char_input.setMaxLength(1)
        form_layout.addWidget(char_input, 0, 1)
        
        form_layout.addWidget(QLabel("Replacement:"), 1, 0)
        replacement_input = QLineEdit(replacement)
        form_layout.addWidget(replacement_input, 1, 1)
        
        dialog_layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)
        
        # Show dialog and update if accepted
        if dialog.exec_() == QDialog.Accepted:
            new_char = char_input.text()
            new_replacement = replacement_input.text()
            
            if new_char:
                item.setText(0, new_char[0])  # Only use the first character
                item.setText(1, new_replacement)
    
    def reset_replacements(self):
        """Reset character replacements to defaults"""
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            "Reset Replacements",
            "Are you sure you want to reset all replacement rules to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Clear the tree
            self.replacement_tree.clear()
            
            # Add default replacements
            replacements = [
                ["?", "-"],
                ["*", "×"],
                [":", "."],
                ["/", "-"],
                ["\\", "-"],
                ["|", "l"],
                ["<", "("],
                [">", ")"],
                ["\"", "'"],
                ["%", "pct"]
            ]
            
            for chars in replacements:
                item = QTreeWidgetItem(self.replacement_tree)
                item.setText(0, chars[0])
                item.setText(1, chars[1])
    
    def connect_to_sharepoint(self):
        """Connects to SharePoint with the given credentials"""
        # In a real implementation, this would make an actual connection
        # For now, simulate connection with a delay
        
        # Disable the connect button during "connection"
        self.connect_button.setEnabled(False)
        self.connection_status.setText("Connecting...")
        
        # Use QThread to avoid blocking the UI
        class ConnectThread(QThread):
            connection_complete = pyqtSignal(bool, str)
            
            def run(self):
                # Simulate connection
                import time
                time.sleep(2)  # Simulate work
                
                # Simulate successful connection
                success = True
                message = "Connected successfully"
                
                self.connection_complete.emit(success, message)
        
        # Create and run thread
        self.connect_thread = ConnectThread()
        self.connect_thread.connection_complete.connect(self.on_sharepoint_connected)
        self.connect_thread.start()
    
    @pyqtSlot(bool, str)
    def on_sharepoint_connected(self, success, message):
        """Handle SharePoint connection result"""
        if success:
            # Update status
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
            
            # Enable library group
            self.libraries_group.setEnabled(True)
            
            # Populate libraries combo with mock data
            self.library_combo.clear()
            self.library_combo.addItems([
                "Documents",
                "Shared Documents",
                "Site Assets",
                "Form Templates"
            ])
            self.library_combo.setEnabled(True)
            
            # Enable folder input and browse button
            self.folder_input.setEnabled(True)
            self.browse_sp_button.setEnabled(True)
            
            # Enable start button if we have scan results
            if self.scan_results:
                self.start_button.setEnabled(True)
        else:
            # Update status with error
            self.connection_status.setText(f"Error: {message}")
            self.connection_status.setStyleSheet("color: red;")
        
        # Re-enable connect button
        self.connect_button.setEnabled(True)
    
    def browse_sharepoint_folders(self):
        """Browse SharePoint folders"""
        # In a real implementation, this would show a tree view of SharePoint folders
        # For now, just show a message
        QMessageBox.information(
            self,
            "SharePoint Browser",
            "In a real implementation, this would show a tree view of SharePoint folders."
        )
    
    def update_with_results(self, results):
        """Update the cleanup widget with scan results"""
        self.scan_results = results
        
        if results:
            # Update preview tree
            self.generate_preview()
            
            # Enable start button if we have a target path for manual mode
            if self.target_path_label.text() != "Not selected":
                self.start_button.setEnabled(True)
            
            # Enable start button for automatic mode if connected to SharePoint
            if self.connection_status.text() == "Connected":
                self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
    
    def start_cleanup(self):
        """Start the cleanup process"""
        # Get current tab to determine mode
        current_tab_index = self.tabs.currentIndex()
        tab_text = self.tabs.tabText(current_tab_index)
        
        # Create options dictionary
        options = {
            'mode': tab_text,
            'total_files': self.scan_results.get('total_files', 0)
        }
        
        if tab_text == "Manual Mode":
            # Check for target path
            target_path = self.target_path_label.text()
            if target_path == "Not selected":
                QMessageBox.warning(
                    self,
                    "Missing Target",
                    "Please select a target folder first."
                )
                return
            
            # Add manual mode options
            options.update({
                'target_path': target_path,
                'fix_options': {
                    'path_length': self.fix_path_length_check.isChecked(),
                    'illegal_chars': self.fix_illegal_chars_check.isChecked(),
                    'reserved_names': self.fix_reserved_names_check.isChecked(),
                    'duplicates': self.fix_duplicates_check.isChecked()
                },
                'strategies': {
                    'path_length': self.path_strategy_combo.currentText(),
                    'illegal_chars': self.char_strategy_combo.currentText(),
                    'duplicates': self.dup_strategy_combo.currentText()
                }
            })
            
        elif tab_text == "Automatic Mode":
            # Check for SharePoint connection
            if self.connection_status.text() != "Connected":
                QMessageBox.warning(
                    self,
                    "Not Connected",
                    "Please connect to SharePoint first."
                )
                return
            
            # Add automatic mode options
            options.update({
                'sharepoint_url': self.sp_url_input.text(),
                'library': self.library_combo.currentText(),
                'folder': self.folder_input.text(),
                'fix_options': {
                    'path_length': self.auto_fix_path_length_check.isChecked(),
                    'illegal_chars': self.auto_fix_illegal_chars_check.isChecked(),
                    'reserved_names': self.auto_fix_reserved_names_check.isChecked(),
                    'duplicates': self.auto_fix_duplicates_check.isChecked()
                },
                'upload_options': {
                    'preserve_timestamps': self.preserve_timestamps_check.isChecked(),
                    'preserve_user': self.preserve_user_check.isChecked(),
                    'upload_only_fixed': self.upload_only_fixed_check.isChecked(),
                    'overwrite_existing': self.overwrite_existing_check.isChecked()
                },
                'throttling': {
                    'concurrent': self.concurrent_spin.value(),
                    'retry_count': self.retry_spin.value()
                }
            })
            
        else:  # Advanced Options
            # Get target path based on current tab
            if self.tabs.currentIndex() == 0:  # Manual Mode is selected
                target_path = self.target_path_label.text()
            else:  # Automatic Mode is selected
                target_path = f"SharePoint: {self.library_combo.currentText()}/{self.folder_input.text()}"
            
            # Check for target path
            if target_path == "Not selected":
                QMessageBox.warning(
                    self,
                    "Missing Target",
                    "Please select a target folder first."
                )
                return
            
            # Add advanced options
            options.update({
                'target_path': target_path,
                'advanced_options': {
                    'max_path_length': self.max_path_spin.value(),
                    'shorten_folder_names': self.shorten_folder_names_check.isChecked(),
                    'max_folder_length': self.max_folder_spin.value(),
                    'truncate_middle': self.truncate_middle_check.isChecked(),
                    'flatten_deep': self.flatten_deep_check.isChecked(),
                    'max_depth': self.max_depth_spin.value(),
                    
                    'keep_newest': self.keep_newest_check.isChecked(),
                    'consider_name': self.consider_name_check.isChecked(),
                    'ignore_empty': self.ignore_empty_check.isChecked(),
                    'similarity': self.similarity_spin.value()
                },
                'logging': {
                    'enable': self.enable_logging_check.isChecked(),
                    'path': self.log_path_input.text()
                }
            })
        
        # Start the cleanup worker
        self.start_cleanup_worker(options)
    
    def start_cleanup_worker(self, options):
        """Start the cleanup worker thread"""
        # Update UI for cleanup in progress
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Cleanup in progress...")
        self.details_label.setText("Preparing cleanup...")
        
        # Create and start worker
        self.cleanup_worker = CleanupWorker(options)
        self.cleanup_worker.progress_updated.connect(self.update_progress)
        self.cleanup_worker.cleanup_completed.connect(self.cleanup_completed)
        self.cleanup_worker.error_occurred.connect(self.cleanup_error)
        self.cleanup_worker.start()
    
    def cancel_cleanup(self):
        """Cancel the current cleanup operation"""
        if self.cleanup_worker and self.cleanup_worker.isRunning():
            # Request interruption
            self.cleanup_worker.requestInterruption()
            self.status_label.setText("Cancelling cleanup...")
            self.cancel_button.setEnabled(False)
    
    @pyqtSlot(int, int)
    def update_progress(self, current, total):
        """Update the progress bar and details label"""
        percentage = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percentage)
        self.details_label.setText(f"Processing file {current} of {total}")
    
    @pyqtSlot(dict)
    def cleanup_completed(self, results):
        """Handle cleanup completion"""
        # Update UI
        status = results.get('status', '')
        processed = results.get('processed_files', 0)
        total = results.get('total_files', 0)
        fixed = results.get('fixed_issues', 0)
        
        if status == 'completed':
            self.status_label.setText("Cleanup completed successfully")
            self.details_label.setText(f"Processed {processed} files, fixed {fixed} issues")
            self.progress_bar.setValue(100)
            
            # Show success message
            QMessageBox.information(
                self,
                "Cleanup Completed",
                f"Cleanup completed successfully.\nProcessed {processed} files, fixed {fixed} issues."
            )
        elif status == 'cancelled':
            self.status_label.setText("Cleanup cancelled")
            self.details_label.setText(f"Processed {processed} of {total} files before cancellation")
            
            # Show cancelled message
            QMessageBox.information(
                self,
                "Cleanup Cancelled",
                f"Cleanup was cancelled.\nProcessed {processed} of {total} files, fixed {fixed} issues."
            )
        
        # Reset UI
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
    
    @pyqtSlot(str)
    def cleanup_error(self, error_message):
        """Handle cleanup error"""
        # Update UI
        self.status_label.setText("Cleanup failed")
        self.details_label.setText(f"Error: {error_message}")
        
        # Show error message
        QMessageBox.critical(
            self,
            "Cleanup Error",
            f"An error occurred during cleanup:\n{error_message}"
        )
        
        # Reset UI
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)