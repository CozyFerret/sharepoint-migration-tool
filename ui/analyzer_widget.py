from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QGridLayout, QSplitter, QTreeWidget, 
                           QTreeWidgetItem, QPushButton, QGroupBox, QComboBox,
                           QTabWidget, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QCheckBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

class AnalyzerWidget(QWidget):
    """
    Widget for displaying detailed analysis of scan results.
    Provides tools for exploring different issue types and filtering results.
    """
    # Define signals
    export_requested = pyqtSignal(str, str)  # Signal for exporting data (format, path)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.scan_results = None
        
    def init_ui(self):
        """Initialize the analyzer UI components"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create controls section
        self.controls_frame = self.create_controls_section()
        self.main_layout.addWidget(self.controls_frame)
        
        # Create splitter for flexible layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Create issue categories panel (left)
        self.categories_panel = self.create_categories_panel()
        splitter.addWidget(self.categories_panel)
        
        # Create issue details panel (right)
        self.details_panel = self.create_details_panel()
        splitter.addWidget(self.details_panel)
        
        # Set initial splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 600])
        
        self.main_layout.addWidget(splitter)
        
    def create_controls_section(self):
        """Create the controls section with filtering and export options"""
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.StyledPanel)
        controls_frame.setMaximumHeight(80)
        
        controls_layout = QHBoxLayout(controls_frame)
        
        # Issue type filter
        filter_group = QGroupBox("Filter")
        filter_layout = QHBoxLayout(filter_group)
        
        issue_type_label = QLabel("Issue Type:")
        self.issue_type_combo = QComboBox()
        self.issue_type_combo.addItem("All Issues")
        self.issue_type_combo.addItem("Path Length Issues")
        self.issue_type_combo.addItem("Illegal Characters")
        self.issue_type_combo.addItem("Reserved Names")
        self.issue_type_combo.addItem("Duplicate Files")
        
        filter_layout.addWidget(issue_type_label)
        filter_layout.addWidget(self.issue_type_combo)
        
        # Severity filter
        severity_label = QLabel("Severity:")
        self.severity_combo = QComboBox()
        self.severity_combo.addItem("All")
        self.severity_combo.addItem("Critical")
        self.severity_combo.addItem("Warning")
        self.severity_combo.addItem("Info")
        
        filter_layout.addWidget(severity_label)
        filter_layout.addWidget(self.severity_combo)
        
        # Export options
        export_group = QGroupBox("Export")
        export_layout = QHBoxLayout(export_group)
        
        export_format_label = QLabel("Format:")
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItem("CSV")
        self.export_format_combo.addItem("Excel")
        self.export_format_combo.addItem("JSON")
        self.export_format_combo.addItem("Text")
        
        self.export_button = QPushButton("Export Analysis")
        self.export_button.clicked.connect(self.export_analysis)
        
        export_layout.addWidget(export_format_label)
        export_layout.addWidget(self.export_format_combo)
        export_layout.addWidget(self.export_button)
        
        # Add to main controls layout
        controls_layout.addWidget(filter_group, 3)
        controls_layout.addWidget(export_group, 2)
        
        # Connect filter signals
        self.issue_type_combo.currentIndexChanged.connect(self.apply_filters)
        self.severity_combo.currentIndexChanged.connect(self.apply_filters)
        
        return controls_frame
    
    def create_categories_panel(self):
        """Create the issue categories panel with tree view"""
        categories_group = QGroupBox("Issue Categories")
        categories_layout = QVBoxLayout(categories_group)
        
        # Create tree widget for categories
        self.categories_tree = QTreeWidget()
        self.categories_tree.setHeaderLabels(["Category", "Count"])
        self.categories_tree.setColumnWidth(0, 200)
        self.categories_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.categories_tree.itemSelectionChanged.connect(self.on_category_selected)
        
        # Add tree widget to layout
        categories_layout.addWidget(self.categories_tree)
        
        # Add "Fix All" button at the bottom
        fix_all_button = QPushButton("Fix All Selected Issues")
        fix_all_button.setEnabled(False)  # Will be enabled when a category is selected
        categories_layout.addWidget(fix_all_button)
        
        return categories_group
    
    def create_details_panel(self):
        """Create the issue details panel with tabbed details"""
        details_group = QGroupBox("Issue Details")
        details_layout = QVBoxLayout(details_group)
        
        # Create tabbed widget for different views
        self.details_tabs = QTabWidget()
        
        # Create tabs
        self.list_tab = QWidget()
        self.preview_tab = QWidget()
        self.fixes_tab = QWidget()
        
        # Setup tab contents
        self.setup_list_tab()
        self.setup_preview_tab()
        self.setup_fixes_tab()
        
        # Add tabs
        self.details_tabs.addTab(self.list_tab, "List View")
        self.details_tabs.addTab(self.preview_tab, "Preview")
        self.details_tabs.addTab(self.fixes_tab, "Fix Options")
        
        # Add to layout
        details_layout.addWidget(self.details_tabs)
        
        return details_group
    
    def setup_list_tab(self):
        """Setup the list tab with table of issues"""
        layout = QVBoxLayout(self.list_tab)
        
        # Create table widget
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(5)
        self.issues_table.setHorizontalHeaderLabels(["File Path", "Issue", "Severity", "Details", "Fix"])
        
        # Adjust column widths
        header = self.issues_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Path takes most space
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Add to layout
        layout.addWidget(self.issues_table)
        
        # Add actions row
        actions_layout = QHBoxLayout()
        
        self.select_all_check = QCheckBox("Select All")
        self.select_all_check.stateChanged.connect(self.on_select_all_changed)
        
        self.fix_selected_button = QPushButton("Fix Selected")
        self.fix_selected_button.setEnabled(False)
        
        actions_layout.addWidget(self.select_all_check)
        actions_layout.addStretch()
        actions_layout.addWidget(self.fix_selected_button)
        
        layout.addLayout(actions_layout)
    
    def setup_preview_tab(self):
        """Setup the preview tab with path visualization"""
        layout = QVBoxLayout(self.preview_tab)
        
        preview_label = QLabel("File path visualization and preview will be shown here.")
        preview_label.setAlignment(Qt.AlignCenter)
        
        # This would typically be a custom visualization component
        # For example, showing a tree view of the path or a preview of the file
        # For now, we'll use a placeholder label
        
        layout.addWidget(preview_label)
    
    def setup_fixes_tab(self):
        """Setup the fixes tab with fix options"""
        layout = QVBoxLayout(self.fixes_tab)
        
        # Info label
        info_label = QLabel("Select fix options for the selected issue type")
        layout.addWidget(info_label)
        
        # Fix options
        options_group = QGroupBox("Fix Options")
        options_layout = QVBoxLayout(options_group)
        
        # These options would change based on the selected issue type
        self.auto_rename_check = QCheckBox("Auto-rename files with illegal characters")
        self.shorten_paths_check = QCheckBox("Shorten paths exceeding SharePoint limits")
        self.handle_duplicates_check = QCheckBox("Replace duplicates with shortcuts")
        
        options_layout.addWidget(self.auto_rename_check)
        options_layout.addWidget(self.shorten_paths_check)
        options_layout.addWidget(self.handle_duplicates_check)
        
        layout.addWidget(options_group)
        
        # Target options
        target_group = QGroupBox("Target Location")
        target_layout = QHBoxLayout(target_group)
        
        self.target_path_label = QLabel("Not selected")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_target_folder)
        
        target_layout.addWidget(QLabel("Output folder: "))
        target_layout.addWidget(self.target_path_label, 1)
        target_layout.addWidget(browse_button)
        
        layout.addWidget(target_group)
        
        # Apply button
        apply_button = QPushButton("Apply Fixes")
        apply_button.setEnabled(False)
        layout.addWidget(apply_button)
        
        layout.addStretch()
    
    def browse_target_folder(self):
        """Open a folder dialog to select the target folder for fixes"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Target Folder", 
            "", 
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.target_path_label.setText(folder)
    
    def export_analysis(self):
        """Export analysis results in the selected format"""
        if not self.scan_results:
            return
        
        # Get selected format
        format_str = self.export_format_combo.currentText().lower()
        
        # Ask for save location
        file_filter = ""
        if format_str == "csv":
            file_filter = "CSV Files (*.csv)"
        elif format_str == "excel":
            file_filter = "Excel Files (*.xlsx)"
        elif format_str == "json":
            file_filter = "JSON Files (*.json)"
        else:  # text
            file_filter = "Text Files (*.txt)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Analysis Export",
            "",
            file_filter
        )
        
        if file_path:
            # Emit signal to perform the export
            self.export_requested.emit(format_str, file_path)
    
    def on_category_selected(self):
        """Handle selection of an issue category"""
        selected_items = self.categories_tree.selectedItems()
        if not selected_items:
            return
        
        # Get selected category
        selected_item = selected_items[0]
        category_text = selected_item.text(0)
        
        # Update issue details based on selection
        self.update_issue_details(category_text)
    
    def on_select_all_changed(self, state):
        """Handle select all checkbox state change"""
        checked = (state == Qt.Checked)
        
        # Update all checkboxes in the table
        for row in range(self.issues_table.rowCount()):
            check_item = self.issues_table.item(row, 0)
            if check_item and hasattr(check_item, 'checkState'):
                check_item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        
        # Update fix selected button state
        self.fix_selected_button.setEnabled(checked and self.issues_table.rowCount() > 0)
    
    def apply_filters(self):
        """Apply selected filters to issue display"""
        if not self.scan_results:
            return
        
        # Get selected filters
        issue_type = self.issue_type_combo.currentText()
        severity = self.severity_combo.currentText()
        
        # Refresh the display with filters applied
        self.update_categories_tree(issue_type, severity)
    
    def update_with_results(self, results):
        """Update the analyzer widget with scan results"""
        self.scan_results = results
        if not results:
            self.clear_display()
            return
        
        # Update the categories tree
        self.update_categories_tree()
        
        # Clear the details view
        self.clear_issue_details()
    
    def update_categories_tree(self, issue_type_filter="All Issues", severity_filter="All"):
        """Update the categories tree with filtered results"""
        self.categories_tree.clear()
        
        if not self.scan_results:
            return
        
        # Create top-level categories
        path_length_item = QTreeWidgetItem(["Path Length Issues", "0"])
        illegal_chars_item = QTreeWidgetItem(["Illegal Characters", "0"])
        reserved_names_item = QTreeWidgetItem(["Reserved Names", "0"])
        duplicates_item = QTreeWidgetItem(["Duplicate Files", "0"])
        
        # Only add relevant categories based on filter
        if issue_type_filter in ["All Issues", "Path Length Issues"]:
            self.categories_tree.addTopLevelItem(path_length_item)
            
            # Add subcategories for path length issues
            path_length_issues = self.scan_results.get('path_length_issues', {})
            total_path_issues = 0
            
            for length, files in sorted(path_length_issues.items(), key=lambda x: int(x[0]), reverse=True):
                if severity_filter == "All" or (severity_filter == "Critical" and int(length) > 250) or \
                   (severity_filter == "Warning" and 200 <= int(length) <= 250) or \
                   (severity_filter == "Info" and int(length) < 200):
                    child = QTreeWidgetItem([f"> {length} characters", str(len(files))])
                    path_length_item.addChild(child)
                    total_path_issues += len(files)
            
            path_length_item.setText(1, str(total_path_issues))
        
        if issue_type_filter in ["All Issues", "Illegal Characters"]:
            self.categories_tree.addTopLevelItem(illegal_chars_item)
            
            # Add subcategories for illegal characters
            illegal_chars = self.scan_results.get('illegal_characters', {})
            total_illegal_chars = 0
            
            for char, files in sorted(illegal_chars.items(), key=lambda x: len(x[1]), reverse=True):
                if severity_filter == "All" or (severity_filter == "Critical" and char in ['?', '*', ':']) or \
                   (severity_filter == "Warning" and char in ['/', '\\', '|']) or \
                   (severity_filter == "Info"):
                    display_char = char if char != ' ' else 'Space'
                    child = QTreeWidgetItem([f"Character: '{display_char}'", str(len(files))])
                    illegal_chars_item.addChild(child)
                    total_illegal_chars += len(files)
            
            illegal_chars_item.setText(1, str(total_illegal_chars))
        
        if issue_type_filter in ["All Issues", "Reserved Names"]:
            self.categories_tree.addTopLevelItem(reserved_names_item)
            
            # Add subcategories for reserved names
            reserved_names = self.scan_results.get('reserved_names', {})
            total_reserved = 0
            
            for name, files in sorted(reserved_names.items(), key=lambda x: len(x[1]), reverse=True):
                if severity_filter == "All" or severity_filter == "Critical":  # All reserved names are critical
                    child = QTreeWidgetItem([f"Name: '{name}'", str(len(files))])
                    reserved_names_item.addChild(child)
                    total_reserved += len(files)
            
            reserved_names_item.setText(1, str(total_reserved))
        
        if issue_type_filter in ["All Issues", "Duplicate Files"]:
            self.categories_tree.addTopLevelItem(duplicates_item)
            
            # Add subcategories for duplicates
            duplicates = self.scan_results.get('duplicates', {})
            total_duplicates = 0
            
            # Group by file size ranges
            size_ranges = {
                "< 1 MB": 0,
                "1-10 MB": 0,
                "10-100 MB": 0,
                "> 100 MB": 0
            }
            
            for hash_val, files in duplicates.items():
                file_size = files[0].get('size', 0) if len(files) > 0 else 0
                dup_count = len(files) - 1  # Original + duplicates
                
                if severity_filter == "All" or \
                   (severity_filter == "Critical" and file_size > 100*1024*1024) or \
                   (severity_filter == "Warning" and 10*1024*1024 <= file_size <= 100*1024*1024) or \
                   (severity_filter == "Info" and file_size < 10*1024*1024):
                    if file_size < 1024*1024:
                        size_ranges["< 1 MB"] += dup_count
                    elif file_size < 10*1024*1024:
                        size_ranges["1-10 MB"] += dup_count
                    elif file_size < 100*1024*1024:
                        size_ranges["10-100 MB"] += dup_count
                    else:
                        size_ranges["> 100 MB"] += dup_count
                    
                    total_duplicates += dup_count
            
            # Add size range children
            for size_range, count in size_ranges.items():
                if count > 0:
                    child = QTreeWidgetItem([f"Size: {size_range}", str(count)])
                    duplicates_item.addChild(child)
            
            duplicates_item.setText(1, str(total_duplicates))
        
        # Expand top-level items
        for i in range(self.categories_tree.topLevelItemCount()):
            self.categories_tree.topLevelItem(i).setExpanded(True)
    
    def update_issue_details(self, category):
        """Update issue details based on selected category"""
        self.clear_issue_details()
        
        if not self.scan_results:
            return
        
        # Parse the category and subcategory
        parts = category.split(':')
        main_category = parts[0].strip()
        subcategory = parts[1].strip() if len(parts) > 1 else None
        
        # Prepare table data based on category
        if "Path Length" in main_category:
            self.update_path_length_issues(subcategory)
        elif "Character" in main_category:
            self.update_illegal_character_issues(subcategory)
        elif "Name" in main_category:
            self.update_reserved_name_issues(subcategory)
        elif "Size" in main_category:
            self.update_duplicate_issues(subcategory)
    
    def update_path_length_issues(self, length_str):
        """Update table with path length issues"""
        if not length_str or not self.scan_results:
            return
        
        # Extract length value
        length = length_str.replace('>', '').replace('characters', '').strip()
        
        # Get files exceeding this length
        path_length_issues = self.scan_results.get('path_length_issues', {})
        files = path_length_issues.get(length, [])
        
        # Populate table
        self.issues_table.setRowCount(len(files))
        
        for i, file_info in enumerate(files):
            # Create checkbox item for selection
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            check_item.setText(file_info.get('path', ''))
            
            # Create other items
            issue_item = QTableWidgetItem("Path Too Long")
            
            # Determine severity
            severity = "Critical" if int(length) > 250 else "Warning" if int(length) > 200 else "Info"
            severity_item = QTableWidgetItem(severity)
            
            # Add color based on severity
            if severity == "Critical":
                severity_item.setBackground(QColor(255, 200, 200))
            elif severity == "Warning":
                severity_item.setBackground(QColor(255, 255, 200))
            
            details_item = QTableWidgetItem(f"Length: {length} characters (SharePoint max: 256)")
            fix_button = QPushButton("Fix")
            
            # Add items to row
            self.issues_table.setItem(i, 0, check_item)
            self.issues_table.setItem(i, 1, issue_item)
            self.issues_table.setItem(i, 2, severity_item)
            self.issues_table.setItem(i, 3, details_item)
            self.issues_table.setCellWidget(i, 4, fix_button)
    
    def update_illegal_character_issues(self, char_str):
        """Update table with illegal character issues"""
        if not char_str or not self.scan_results:
            return
        
        # Extract character
        char = char_str.replace("'", "")
        if char == "Space":
            char = " "
        
        # Get files with this illegal character
        illegal_chars = self.scan_results.get('illegal_characters', {})
        files = illegal_chars.get(char, [])
        
        # Populate table
        self.issues_table.setRowCount(len(files))
        
        for i, file_info in enumerate(files):
            # Create checkbox item for selection
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            check_item.setText(file_info.get('path', ''))
            
            # Create other items
            display_char = char if char != ' ' else 'Space'
            issue_item = QTableWidgetItem(f"Illegal Character '{display_char}'")
            
            # Determine severity
            severity = "Critical" if char in ['?', '*', ':'] else "Warning"
            severity_item = QTableWidgetItem(severity)
            
            # Add color based on severity
            if severity == "Critical":
                severity_item.setBackground(QColor(255, 200, 200))
            elif severity == "Warning":
                severity_item.setBackground(QColor(255, 255, 200))
            
            details_item = QTableWidgetItem(f"Character '{display_char}' not allowed in SharePoint")
            fix_button = QPushButton("Fix")
            
            # Add items to row
            self.issues_table.setItem(i, 0, check_item)
            self.issues_table.setItem(i, 1, issue_item)
            self.issues_table.setItem(i, 2, severity_item)
            self.issues_table.setItem(i, 3, details_item)
            self.issues_table.setCellWidget(i, 4, fix_button)
    
    def update_reserved_name_issues(self, name_str):
        """Update table with reserved name issues"""
        if not name_str or not self.scan_results:
            return
        
        # Extract name
        name = name_str.replace("'", "")
        
        # Get files with this reserved name
        reserved_names = self.scan_results.get('reserved_names', {})
        files = reserved_names.get(name, [])
        
        # Populate table
        self.issues_table.setRowCount(len(files))
        
        for i, file_info in enumerate(files):
            # Create checkbox item for selection
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            check_item.setText(file_info.get('path', ''))
            
            # Create other items
            issue_item = QTableWidgetItem(f"Reserved Name '{name}'")
            
            # All reserved names are critical
            severity_item = QTableWidgetItem("Critical")
            severity_item.setBackground(QColor(255, 200, 200))
            
            details_item = QTableWidgetItem(f"'{name}' is a reserved name in SharePoint")
            fix_button = QPushButton("Fix")
            
            # Add items to row
            self.issues_table.setItem(i, 0, check_item)
            self.issues_table.setItem(i, 1, issue_item)
            self.issues_table.setItem(i, 2, severity_item)
            self.issues_table.setItem(i, 3, details_item)
            self.issues_table.setCellWidget(i, 4, fix_button)
    
    def update_duplicate_issues(self, size_range):
        """Update table with duplicate file issues"""
        if not size_range or not self.scan_results:
            return
        
        # Get all duplicates
        duplicates = self.scan_results.get('duplicates', {})
        
        # Determine size range limits
        min_size = 0
        max_size = float('inf')
        
        if size_range == "< 1 MB":
            max_size = 1024*1024
        elif size_range == "1-10 MB":
            min_size = 1024*1024
            max_size = 10*1024*1024
        elif size_range == "10-100 MB":
            min_size = 10*1024*1024
            max_size = 100*1024*1024
        elif size_range == "> 100 MB":
            min_size = 100*1024*1024
        
        # Collect files in this size range
        matching_files = []
        
        for hash_val, files in duplicates.items():
            if not files:
                continue
                
            file_size = files[0].get('size', 0)
            
            if min_size <= file_size < max_size:
                # First file is original, rest are duplicates
                original = files[0]
                for duplicate in files[1:]:
                    matching_files.append({
                        'path': duplicate.get('path', ''),
                        'original': original.get('path', ''),
                        'size': file_size
                    })
        
        # Populate table
        self.issues_table.setRowCount(len(matching_files))
        
        for i, file_info in enumerate(matching_files):
            # Create checkbox item for selection
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            check_item.setText(file_info.get('path', ''))
            
            # Create other items
            issue_item = QTableWidgetItem("Duplicate File")
            
            # Determine severity based on size
            size = file_info.get('size', 0)
            severity = "Critical" if size > 100*1024*1024 else "Warning" if size > 10*1024*1024 else "Info"
            severity_item = QTableWidgetItem(severity)
            
            # Add color based on severity
            if severity == "Critical":
                severity_item.setBackground(QColor(255, 200, 200))
            elif severity == "Warning":
                severity_item.setBackground(QColor(255, 255, 200))
            
            # Format size for display
            if size < 1024:
                size_str = f"{size} bytes"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f} KB"
            elif size < 1024*1024*1024:
                size_str = f"{size/(1024*1024):.1f} MB"
            else:
                size_str = f"{size/(1024*1024*1024):.2f} GB"
            
            details_item = QTableWidgetItem(f"Size: {size_str}, Original: {file_info.get('original', '')}")
            fix_button = QPushButton("Fix")
            
            # Add items to row
            self.issues_table.setItem(i, 0, check_item)
            self.issues_table.setItem(i, 1, issue_item)
            self.issues_table.setItem(i, 2, severity_item)
            self.issues_table.setItem(i, 3, details_item)
            self.issues_table.setCellWidget(i, 4, fix_button)
    
    def clear_issue_details(self):
        """Clear the issue details display"""
        self.issues_table.setRowCount(0)
        self.select_all_check.setChecked(False)
        self.fix_selected_button.setEnabled(False)
    
    def clear_display(self):
        """Clear all display elements"""
        self.categories_tree.clear()
        self.clear_issue_details()