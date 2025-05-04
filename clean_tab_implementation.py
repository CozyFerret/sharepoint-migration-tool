def create_clean_tab(self):
    """Create the clean and migrate tab"""
    try:
        # Create tab widget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Import cleanup widget
        try:
            from ui.cleanup_widget import CleanupWidget
            self.cleanup_widget = CleanupWidget()
            layout.addWidget(self.cleanup_widget)
            logger.info("Cleanup widget loaded successfully")
            
            # Connect signals
            if hasattr(self.cleanup_widget, 'fix_completed'):
                self.cleanup_widget.fix_completed.connect(self.on_fix_completed)
        except ImportError as e:
            logger.error(f"Error importing CleanupWidget: {e}")
            # Fallback to simpler implementation if custom widget not available
            self._create_fallback_clean_tab(layout)
        
        return tab
    except Exception as e:
        logger.error(f"Error creating clean tab: {e}")
        # Create an error tab
        error_tab = QWidget()
        error_layout = QVBoxLayout(error_tab)
        error_layout.addWidget(QLabel(f"Error creating clean tab: {str(e)}"))
        return error_tab

def _create_fallback_clean_tab(self, layout):
    """Create a fallback clean tab if CleanupWidget is not available"""
    # Create a splitter for resizable sections
    splitter = QSplitter(Qt.Vertical)
    
    # --- Options section ---
    options_group = QGroupBox("Cleaning Options")
    options_layout = QVBoxLayout(options_group)
    
    # Path length options
    path_group = QGroupBox("Path Length Fixing")
    path_layout = QVBoxLayout(path_group)
    
    self.fix_path_check = QCheckBox("Fix path length issues")
    self.fix_path_check.setChecked(True)
    path_layout.addWidget(self.fix_path_check)
    
    path_strategy_layout = QHBoxLayout()
    path_strategy_layout.addWidget(QLabel("Strategy:"))
    
    self.path_strategy_combo = QComboBox()
    self.path_strategy_combo.addItems([
        "Abbreviate Directories", 
        "Remove Middle Directories",
        "Truncate Names",
        "Minimal Path"
    ])
    path_strategy_layout.addWidget(self.path_strategy_combo)
    path_layout.addLayout(path_strategy_layout)
    
    # Add to options layout
    options_layout.addWidget(path_group)
    
    # Name fixing options
    name_group = QGroupBox("Name Fixing")
    name_layout = QVBoxLayout(name_group)
    
    self.fix_name_check = QCheckBox("Fix illegal characters and reserved names")
    self.fix_name_check.setChecked(True)
    name_layout.addWidget(self.fix_name_check)
    
    name_strategy_layout = QHBoxLayout()
    name_strategy_layout.addWidget(QLabel("Strategy:"))
    
    self.name_strategy_combo = QComboBox()
    self.name_strategy_combo.addItems([
        "Replace with Underscore",
        "Remove Characters",
        "Replace with ASCII Equivalents"
    ])
    name_strategy_layout.addWidget(self.name_strategy_combo)
    name_layout.addLayout(name_strategy_layout)
    
    # Add to options layout
    options_layout.addWidget(name_group)
    
    # Duplicate options
    dup_group = QGroupBox("Duplicate Handling")
    dup_layout = QVBoxLayout(dup_group)
    
    self.fix_duplicates_check = QCheckBox("Handle duplicate files")
    self.fix_duplicates_check.setChecked(True)
    dup_layout.addWidget(self.fix_duplicates_check)
    
    dup_strategy_layout = QHBoxLayout()
    dup_strategy_layout.addWidget(QLabel("Strategy:"))
    
    self.dup_strategy_combo = QComboBox()
    self.dup_strategy_combo.addItems([
        "Keep First Occurrence",
        "Keep Newest Version",
        "Keep Oldest Version",
        "Keep Largest Version",
        "Keep Smallest Version",
        "Rename All Duplicates"
    ])
    dup_strategy_layout.addWidget(self.dup_strategy_combo)
    dup_layout.addLayout(dup_strategy_layout)
    
    # Add to options layout
    options_layout.addWidget(dup_group)
    
    # Target selection
    target_group = QGroupBox("Target Location")
    target_layout = QHBoxLayout(target_group)
    
    self.target_path_edit = QLineEdit()
    self.target_path_edit.setReadOnly(True)
    self.target_path_edit.setPlaceholderText("Select output directory...")
    
    target_browse_btn = QPushButton("Browse...")
    target_browse_btn.clicked.connect(self.select_target_folder)
    
    target_layout.addWidget(self.target_path_edit)
    target_layout.addWidget(target_browse_btn)
    
    # Add to options layout
    options_layout.addWidget(target_group)
    
    # Add options group to splitter
    splitter.addWidget(options_group)
    
    # --- Preview section ---
    preview_group = QGroupBox("Fix Preview")
    preview_layout = QVBoxLayout(preview_group)
    
    self.preview_table = QTableView()
    self.preview_model = QStandardItemModel()
    self.preview_model.setHorizontalHeaderLabels(["Original Path", "New Path", "Issues Fixed"])
    self.preview_table.setModel(self.preview_model)
    self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    self.preview_table.horizontalHeader().setStretchLastSection(True)
    
    preview_layout.addWidget(self.preview_table)
    
    # Preview button
    self.preview_button = QPushButton("Generate Preview")
    self.preview_button.clicked.connect(self.generate_fix_preview)
    preview_layout.addWidget(self.preview_button)
    
    # Add preview group to splitter
    splitter.addWidget(preview_group)
    
    # Add splitter to layout
    layout.addWidget(splitter)
    
    # --- Progress section ---
    progress_group = QGroupBox("Fix Progress")
    progress_layout = QVBoxLayout(progress_group)
    
    self.clean_progress_bar = QProgressBar()
    progress_layout.addWidget(self.clean_progress_bar)
    
    # Status label
    self.clean_status_label = QLabel("Ready to start fixing issues")
    progress_layout.addWidget(self.clean_status_label)
    
    # Add to layout
    layout.addWidget(progress_group)
    
    # --- Control buttons ---
    button_layout = QHBoxLayout()
    
    self.start_fix_button = QPushButton("Start Fixing Issues")
    self.start_fix_button.clicked.connect(self.start_fixing_issues)
    self.start_fix_button.setEnabled(False)
    
    self.cancel_fix_button = QPushButton("Cancel")
    self.cancel_fix_button.clicked.connect(self.cancel_fixing_issues)
    self.cancel_fix_button.setEnabled(False)
    
    button_layout.addStretch()
    button_layout.addWidget(self.start_fix_button)
    button_layout.addWidget(self.cancel_fix_button)
    button_layout.addStretch()
    
    # Add to layout
    layout.addLayout(button_layout)

def select_target_folder(self):
    """Select target folder for cleaned files"""
    try:
        folder = QFileDialog.getExistingDirectory(
            self, "Select Target Folder", "", QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.target_path_edit.setText(folder)
            self.start_fix_button.setEnabled(True)
            
            # If we have a cleanup widget, update it too
            if hasattr(self, 'cleanup_widget'):
                # Assuming the cleanup widget has a method to set the target folder
                if hasattr(self.cleanup_widget, 'set_target_folder'):
                    self.cleanup_widget.set_target_folder(folder)
    except Exception as e:
        logger.error(f"Error selecting target folder: {e}")
        QMessageBox.critical(self, "Folder Selection Error", 
                           f"Error selecting folder: {str(e)}")

def generate_fix_preview(self):
    """Generate a preview of the fixes that will be applied"""
    try:
        # Check if we have scan data
        scan_data = self.data_processor.get_scan_data()
        if scan_data is None or len(scan_data) == 0:
            QMessageBox.warning(self, "No Data", 
                             "No scan data available. Please scan files first.")
            return
            
        # Get analysis results
        analysis_results = self.data_processor.get_analysis_results()
        if not analysis_results:
            QMessageBox.warning(self, "No Analysis", 
                             "No analysis results available. Please run analysis first.")
            return
            
        # Check if target folder is selected
        target_folder = self.target_path_edit.text()
        if not target_folder:
            QMessageBox.warning(self, "No Target", 
                             "Please select a target folder for the fixed files.")
            return
            
        # Get fix options
        fix_options = {
            'fix_path_issues': self.fix_path_check.isChecked(),
            'path_strategy': self.path_strategy_combo.currentText(),
            'fix_name_issues': self.fix_name_check.isChecked(),
            'name_strategy': self.name_strategy_combo.currentText(),
            'fix_duplicates': self.fix_duplicates_check.isChecked(),
            'duplicate_strategy': self.dup_strategy_combo.currentText()
        }
        
        # Create data cleaner
        from core.data_cleaner import DataCleaner
        cleaner = DataCleaner()
        
        # Generate preview
        preview = cleaner.preview_fixes(analysis_results, fix_options)
        
        # Update preview table
        self.preview_model.removeRows(0, self.preview_model.rowCount())
        
        # Add path fixes
        for fix in preview.get('path_fixes', []):
            original = fix.get('original', '')
            fixed = fix.get('fixed', '')
            
            row = [
                QStandardItem(original),
                QStandardItem(fixed),
                QStandardItem("Path Length")
            ]
            
            self.preview_model.appendRow(row)
        
        # Add name fixes
        for fix in preview.get('name_fixes', []):
            original = fix.get('original', '')
            fixed = fix.get('fixed', '')
            
            row = [
                QStandardItem(original),
                QStandardItem(fixed),
                QStandardItem("Naming Issues")
            ]
            
            self.preview_model.appendRow(row)
        
        # Add duplicate fixes
        for fix in preview.get('duplicate_fixes', []):
            original = fix.get('original', '')
            fixed = fix.get('fixed', '')
            reference = fix.get('reference', '')
            
            row = [
                QStandardItem(original),
                QStandardItem(fixed),
                QStandardItem(f"Duplicate of {os.path.basename(reference)}")
            ]
            
            self.preview_model.appendRow(row)
        
        # Enable start button
        self.start_fix_button.setEnabled(True)
        
        # Update status
        total_fixes = preview.get('total_fixes', 0)
        self.clean_status_label.setText(f"Preview generated: {total_fixes} fixes to apply")
        
    except Exception as e:
        logger.error(f"Error generating fix preview: {e}")
        QMessageBox.critical(self, "Preview Error", 
                           f"Error generating preview: {str(e)}")

def start_fixing_issues(self):
    """Start the fixing process"""
    try:
        # Check if we have scan data
        scan_data = self.data_processor.get_scan_data()
        if scan_data is None or len(scan_data) == 0:
            QMessageBox.warning(self, "No Data", 
                             "No scan data available. Please scan files first.")
            return
            
        # Get analysis results
        analysis_results = self.data_processor.get_analysis_results()
        if not analysis_results:
            QMessageBox.warning(self, "No Analysis", 
                             "No analysis results available. Please run analysis first.")
            return
            
        # Check if target folder is selected
        target_folder = self.target_path_edit.text()
        if not target_folder:
            QMessageBox.warning(self, "No Target", 
                             "Please select a target folder for the fixed files.")
            return
            
        # Get fix options
        clean_options = {
            'fix_path_issues': self.fix_path_check.isChecked(),
            'path_strategy': self.path_strategy_combo.currentText(),
            'fix_name_issues': self.fix_name_check.isChecked(),
            'name_strategy': self.name_strategy_combo.currentText(),
            'fix_duplicates': self.fix_duplicates_check.isChecked(),
            'duplicate_strategy': self.dup_strategy_combo.currentText(),
            'source_folder': self.source_folder_edit.text()
        }
        
        # Set up callbacks
        callbacks = {
            'progress': self.update_clean_progress,
            'status': self.update_clean_status,
            'error': self.clean_error,
            'file_processed': self.file_processed,
            'cleaning_completed': self.cleaning_completed
        }
        
        # Disable UI
        self.start_fix_button.setEnabled(False)
        self.cancel_fix_button.setEnabled(True)
        self.preview_button.setEnabled(False)
        
        # Reset progress
        self.clean_progress_bar.setValue(0)
        self.clean_status_label.setText("Starting cleanup...")
        
        # Start cleaning
        self.data_processor.start_cleaning(target_folder, clean_options, callbacks)
        
    except Exception as e:
        logger.error(f"Error starting cleanup: {e}")
        QMessageBox.critical(self, "Cleanup Error", 
                           f"Error starting cleanup: {str(e)}")
        
        # Re-enable UI
        self.start_fix_button.setEnabled(True)
        self.cancel_fix_button.setEnabled(False)
        self.preview_button.setEnabled(True)

def cancel_fixing_issues(self):
    """Cancel the fixing process"""
    try:
        # Stop cleaning
        self.data_processor.stop_cleaning()
        
        # Update status
        self.clean_status_label.setText("Cleanup cancelled")
        
        # Re-enable UI
        self.start_fix_button.setEnabled(True)
        self.cancel_fix_button.setEnabled(False)
        self.preview_button.setEnabled(True)
        
    except Exception as e:
        logger.error(f"Error cancelling cleanup: {e}")
        QMessageBox.critical(self, "Cancel Error", 
                           f"Error cancelling cleanup: {str(e)}")

def update_clean_progress(self, current, total):
    """Update the cleanup progress bar"""
    try:
        progress = int((current / max(total, 1)) * 100)
        self.clean_progress_bar.setValue(progress)
        
    except Exception as e:
        logger.error(f"Error updating cleanup progress: {e}")

def update_clean_status(self, status):
    """Update the cleanup status label"""
    try:
        self.clean_status_label.setText(status)
        
    except Exception as e:
        logger.error(f"Error updating cleanup status: {e}")

def clean_error(self, error_msg):
    """Handle cleanup error"""
    try:
        logger.error(f"Cleanup error: {error_msg}")
        
        # Update status
        self.clean_status_label.setText(f"Error: {error_msg}")
        
        # Re-enable UI
        self.start_fix_button.setEnabled(True)
        self.cancel_fix_button.setEnabled(False)
        self.preview_button.setEnabled(True)
        
        # Show error message
        QMessageBox.critical(self, "Cleanup Error", 
                           f"Error during cleanup: {error_msg}")
        
    except Exception as e:
        logger.error(f"Error handling cleanup error: {e}")

def file_processed(self, original_path, processed_path):
    """Handle file processed callback"""
    try:
        # Update status with latest file
        filename = os.path.basename(original_path)
        self.clean_status_label.setText(f"Processed: {filename}")
        
    except Exception as e:
        logger.error(f"Error handling file processed: {e}")

def cleaning_completed(self, cleaned_files):
    """Handle cleanup completion"""
    try:
        # Update status
        total_files = len(cleaned_files) if cleaned_files else 0
        self.clean_status_label.setText(f"Cleanup completed: {total_files} files processed")
        
        # Set progress to 100%
        self.clean_progress_bar.setValue(100)
        
        # Re-enable UI
        self.start_fix_button.setEnabled(True)
        self.cancel_fix_button.setEnabled(False)
        self.preview_button.setEnabled(True)
        
        # Show success message
        QMessageBox.information(self, "Cleanup Complete", 
                              f"Cleanup completed successfully. {total_files} files processed.")
        
    except Exception as e:
        logger.error(f"Error handling cleanup completion: {e}")

def on_fix_completed(self, results):
    """Handle fix completion from the cleanup widget"""
    try:
        # Update UI
        self.clean_progress_bar.setValue(100)
        
        # Show success message
        total_fixed = results.get('total_fixed', 0)
        QMessageBox.information(self, "Fixes Complete", 
                              f"Fixed {total_fixed} issues successfully.")
        
    except Exception as e:
        logger.error(f"Error handling fix completion: {e}")