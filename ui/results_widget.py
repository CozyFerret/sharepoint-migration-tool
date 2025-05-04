from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QGridLayout, QSplitter, QTreeView,
                           QPushButton, QGroupBox, QComboBox, QTableWidget,
                           QTableWidgetItem, QHeaderView, QCheckBox, QLineEdit,
                           QRadioButton, QButtonGroup, QFileDialog, QMenu)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QColor, QIcon
import os
import re

class ResultsWidget(QWidget):
    """
    Widget for displaying comprehensive scan results in various formats.
    Provides filtering, searching, and detailed information viewing.
    """
    
    # Define signals
    item_selected = pyqtSignal(dict)  # Signal when item is selected
    view_file_requested = pyqtSignal(str)  # Signal to view file details
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.scan_results = None
        self.file_model = None
        self.proxy_model = None
        
    def init_ui(self):
        """Initialize the results UI components"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create filter section
        self.filter_frame = self.create_filter_section()
        self.main_layout.addWidget(self.filter_frame)
        
        # Create splitter for flexible layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Create file tree panel (left)
        self.file_tree_panel = self.create_file_tree_panel()
        splitter.addWidget(self.file_tree_panel)
        
        # Create details panel (right)
        self.details_panel = self.create_details_panel()
        splitter.addWidget(self.details_panel)
        
        # Set initial splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 600])
        
        self.main_layout.addWidget(splitter)
        
        # Create status bar
        self.status_bar = QLabel("No scan results loaded")
        self.main_layout.addWidget(self.status_bar)
        
    def create_filter_section(self):
        """Create the filter section with search and type filters"""
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_frame.setMaximumHeight(100)
        
        filter_layout = QGridLayout(filter_frame)
        
        # Search box
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for files or folders...")
        self.search_input.textChanged.connect(self.apply_search_filter)
        
        # Type filter
        type_label = QLabel("Filter by Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItem("All Types")
        self.type_combo.addItem("Files Only")
        self.type_combo.addItem("Folders Only")
        self.type_combo.addItem("Problem Items Only")
        self.type_combo.currentIndexChanged.connect(self.apply_type_filter)
        
        # Issue filter
        issue_label = QLabel("Filter by Issue:")
        self.issue_combo = QComboBox()
        self.issue_combo.addItem("All Items")
        self.issue_combo.addItem("Path Length Issues")
        self.issue_combo.addItem("Naming Issues")
        self.issue_combo.addItem("Duplicates")
        self.issue_combo.currentIndexChanged.connect(self.apply_issue_filter)
        
        # View type selection
        view_label = QLabel("View As:")
        self.tree_radio = QRadioButton("Tree View")
        self.tree_radio.setChecked(True)
        self.list_radio = QRadioButton("List View")
        
        view_group = QButtonGroup(self)
        view_group.addButton(self.tree_radio)
        view_group.addButton(self.list_radio)
        view_group.buttonClicked.connect(self.toggle_view_type)
        
        view_layout = QHBoxLayout()
        view_layout.addWidget(self.tree_radio)
        view_layout.addWidget(self.list_radio)
        
        # Add widgets to layout
        filter_layout.addWidget(search_label, 0, 0)
        filter_layout.addWidget(self.search_input, 0, 1)
        filter_layout.addWidget(type_label, 0, 2)
        filter_layout.addWidget(self.type_combo, 0, 3)
        
        filter_layout.addWidget(issue_label, 1, 0)
        filter_layout.addWidget(self.issue_combo, 1, 1)
        filter_layout.addWidget(view_label, 1, 2)
        filter_layout.addLayout(view_layout, 1, 3)
        
        return filter_frame
    
    def create_file_tree_panel(self):
        """Create the file tree panel with hierarchical view"""
        tree_group = QGroupBox("File System")
        tree_layout = QVBoxLayout(tree_group)
        
        # Create tree view
        self.file_tree_view = QTreeView()
        self.file_tree_view.setAlternatingRowColors(True)
        self.file_tree_view.setSortingEnabled(True)
        self.file_tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.file_tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.file_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # Create and set model
        self.file_model = QStandardItemModel()
        self.file_model.setHorizontalHeaderLabels(["Name", "Size", "Status"])
        
        # Create proxy model for filtering
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.file_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(0)  # Filter on name column
        
        self.file_tree_view.setModel(self.proxy_model)
        
        # Connect selection change
        self.file_tree_view.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)
        
        # Add tree view to layout
        tree_layout.addWidget(self.file_tree_view)
        
        # Add actions row
        actions_layout = QHBoxLayout()
        
        self.expand_all_button = QPushButton("Expand All")
        self.expand_all_button.clicked.connect(self.file_tree_view.expandAll)
        
        self.collapse_all_button = QPushButton("Collapse All")
        self.collapse_all_button.clicked.connect(self.file_tree_view.collapseAll)
        
        actions_layout.addWidget(self.expand_all_button)
        actions_layout.addWidget(self.collapse_all_button)
        
        tree_layout.addLayout(actions_layout)
        
        return tree_group
    
    def create_details_panel(self):
        """Create the details panel showing selected item information"""
        details_group = QGroupBox("Item Details")
        details_layout = QVBoxLayout(details_group)
        
        # File information grid
        info_grid = QGridLayout()
        
        # Basic information
        info_grid.addWidget(QLabel("<b>Name:</b>"), 0, 0)
        self.name_label = QLabel()
        info_grid.addWidget(self.name_label, 0, 1)
        
        info_grid.addWidget(QLabel("<b>Path:</b>"), 1, 0)
        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        info_grid.addWidget(self.path_label, 1, 1)
        
        info_grid.addWidget(QLabel("<b>Type:</b>"), 2, 0)
        self.type_label = QLabel()
        info_grid.addWidget(self.type_label, 2, 1)
        
        info_grid.addWidget(QLabel("<b>Size:</b>"), 3, 0)
        self.size_label = QLabel()
        info_grid.addWidget(self.size_label, 3, 1)
        
        # Issue information
        info_grid.addWidget(QLabel("<b>Status:</b>"), 4, 0)
        self.status_label = QLabel()
        info_grid.addWidget(self.status_label, 4, 1)
        
        info_grid.addWidget(QLabel("<b>Issues:</b>"), 5, 0)
        self.issues_label = QLabel()
        self.issues_label.setWordWrap(True)
        info_grid.addWidget(self.issues_label, 5, 1)
        
        # Add grid to layout
        details_layout.addLayout(info_grid)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        details_layout.addWidget(separator)
        
        # Add issues table for listing specific issues
        issues_label = QLabel("Issue Details:")
        details_layout.addWidget(issues_label)
        
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(3)
        self.issues_table.setHorizontalHeaderLabels(["Issue Type", "Severity", "Details"])
        
        # Adjust column widths
        header = self.issues_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        details_layout.addWidget(self.issues_table)
        
        # Add actions row
        actions_layout = QHBoxLayout()
        
        self.view_button = QPushButton("View File")
        self.view_button.clicked.connect(self.on_view_button_clicked)
        self.view_button.setEnabled(False)
        
        self.fix_button = QPushButton("Fix Issues")
        self.fix_button.setEnabled(False)
        
        actions_layout.addWidget(self.view_button)
        actions_layout.addWidget(self.fix_button)
        
        details_layout.addLayout(actions_layout)
        
        return details_group
    
    def update_with_results(self, results):
        """Update the results widget with scan results"""
        self.scan_results = results
        if not results:
            self.clear_display()
            return
        
        # Update model with file tree data
        self.populate_file_tree(results)
        
        # Update status bar
        total_files = results.get('total_files', 0)
        total_folders = results.get('total_folders', 0)
        total_issues = results.get('total_issues', 0)
        
        self.status_bar.setText(f"Scan Results: {total_files} files, {total_folders} folders, {total_issues} issues found")
        
        # Ensure buttons are enabled
        self.expand_all_button.setEnabled(True)
        self.collapse_all_button.setEnabled(True)
        
        # Clear the details panel
        self.clear_details_panel()
    
    def populate_file_tree(self, results):
        """Populate the file tree with scan results"""
        self.file_model.clear()
        self.file_model.setHorizontalHeaderLabels(["Name", "Size", "Status"])
        
        # Get the root directory from results
        root_dir = results.get('root_directory', '')
        if not root_dir:
            return
        
        # Get the file structure data
        file_structure = results.get('file_structure', {})
        
        # Create root item
        root_name = os.path.basename(root_dir)
        root_item = QStandardItem(root_name)
        root_item.setData(root_dir, Qt.UserRole)  # Store full path
        
        # Set icon for root folder
        root_item.setIcon(QIcon.fromTheme("folder"))
        
        # Add size column
        root_size_item = QStandardItem("--")
        
        # Add status column
        root_status_item = QStandardItem("Root Folder")
        
        # Add columns to the row
        self.file_model.appendRow([root_item, root_size_item, root_status_item])
        
        # Recursively add children
        self._add_children(root_item, file_structure, results)
        
        # Expand the root item
        root_index = self.proxy_model.mapFromSource(self.file_model.indexFromItem(root_item))
        self.file_tree_view.expand(root_index)
        
        # Adjust column widths
        self.file_tree_view.setColumnWidth(0, 300)  # Name column
        self.file_tree_view.setColumnWidth(1, 100)  # Size column
        self.file_tree_view.setColumnWidth(2, 150)  # Status column
    
    def _add_children(self, parent_item, file_structure, results):
        """Recursively add children to the file tree"""
        parent_path = parent_item.data(Qt.UserRole)
        
        if not parent_path or parent_path not in file_structure:
            return
        
        # Get children of this parent
        children = file_structure[parent_path]
        
        # Process folder children first, then files
        for item_type in ['folders', 'files']:
            if item_type not in children:
                continue
                
            for item in children[item_type]:
                # Create item name
                name = os.path.basename(item['path'])
                item_path = item['path']
                
                # Create item for name column
                name_item = QStandardItem(name)
                name_item.setData(item_path, Qt.UserRole)  # Store full path
                
                # Set icon based on type
                if item_type == 'folders':
                    name_item.setIcon(QIcon.fromTheme("folder"))
                else:
                    # Could set different icons based on file extension
                    name_item.setIcon(QIcon.fromTheme("text-x-generic"))
                
                # Create item for size column
                size_text = "--"
                if item_type == 'files' and 'size' in item:
                    size = item['size']
                    if size < 1024:
                        size_text = f"{size} bytes"
                    elif size < 1024*1024:
                        size_text = f"{size/1024:.1f} KB"
                    elif size < 1024*1024*1024:
                        size_text = f"{size/(1024*1024):.1f} MB"
                    else:
                        size_text = f"{size/(1024*1024*1024):.2f} GB"
                
                size_item = QStandardItem(size_text)
                
                # Create item for status column
                status_text = "Folder" if item_type == 'folders' else "File"
                has_issues = False
                
                # Check for issues
                if 'issues' in item and item['issues']:
                    has_issues = True
                    status_text = f"Issues: {len(item['issues'])}"
                
                status_item = QStandardItem(status_text)
                
                # If has issues, highlight with color
                if has_issues:
                    # Add warning color
                    status_item.setBackground(QColor(255, 255, 200))  # Light yellow
                    status_item.setForeground(QColor(200, 0, 0))  # Dark red text
                
                # Add row to parent
                parent_item.appendRow([name_item, size_item, status_item])
                
                # If it's a folder, recursively add its children
                if item_type == 'folders':
                    self._add_children(name_item, file_structure, results)
    
    def on_tree_selection_changed(self, selected, deselected):
        """Handle selection change in the tree view"""
        indexes = selected.indexes()
        if not indexes:
            self.clear_details_panel()
            return
        
        # Get the selected item's path
        index = self.proxy_model.mapToSource(indexes[0])
        item = self.file_model.itemFromIndex(index)
        
        if not item:
            return
            
        item_path = item.data(Qt.UserRole)
        
        # Find the item in the scan results
        self.update_details_panel(item_path)
    
    def update_details_panel(self, item_path):
        """Update the details panel with selected item information"""
        if not self.scan_results or not item_path:
            return
            
        # Find item in file structure
        file_structure = self.scan_results.get('file_structure', {})
        
        # Get parent directory
        parent_dir = os.path.dirname(item_path)
        
        if parent_dir not in file_structure:
            return
            
        # Find the item in the parent's children
        item_info = None
        item_name = os.path.basename(item_path)
        
        # Check in folders
        if 'folders' in file_structure[parent_dir]:
            for folder in file_structure[parent_dir]['folders']:
                if folder['path'] == item_path:
                    item_info = folder
                    break
        
        # Check in files
        if not item_info and 'files' in file_structure[parent_dir]:
            for file in file_structure[parent_dir]['files']:
                if file['path'] == item_path:
                    item_info = file
                    break
        
        if not item_info:
            return
            
        # Update basic information
        self.name_label.setText(item_name)
        self.path_label.setText(item_path)
        
        # Set type information
        is_folder = 'children' in item_info or ('type' in item_info and item_info['type'] == 'folder')
        self.type_label.setText("Folder" if is_folder else "File")
        
        # Set size information
        if not is_folder and 'size' in item_info:
            size = item_info['size']
            if size < 1024:
                size_text = f"{size} bytes"
            elif size < 1024*1024:
                size_text = f"{size/1024:.1f} KB"
            elif size < 1024*1024*1024:
                size_text = f"{size/(1024*1024):.1f} MB"
            else:
                size_text = f"{size/(1024*1024*1024):.2f} GB"
            
            self.size_label.setText(size_text)
        else:
            self.size_label.setText("--")
        
        # Set status and issues information
        has_issues = 'issues' in item_info and item_info['issues']
        
        if has_issues:
            self.status_label.setText("Has Issues")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
            # Format issues text
            issues_text = ", ".join([issue['type'] for issue in item_info['issues']])
            self.issues_label.setText(issues_text)
            
            # Populate issues table
            self.issues_table.setRowCount(len(item_info['issues']))
            
            for i, issue in enumerate(item_info['issues']):
                # Issue type
                type_item = QTableWidgetItem(issue['type'])
                
                # Severity
                severity = issue.get('severity', 'Warning')
                severity_item = QTableWidgetItem(severity)
                
                # Add color based on severity
                if severity == "Critical":
                    severity_item.setBackground(QColor(255, 200, 200))
                elif severity == "Warning":
                    severity_item.setBackground(QColor(255, 255, 200))
                
                # Details
                details_item = QTableWidgetItem(issue.get('description', ''))
                
                # Add items to row
                self.issues_table.setItem(i, 0, type_item)
                self.issues_table.setItem(i, 1, severity_item)
                self.issues_table.setItem(i, 2, details_item)
            
            # Enable fix button
            self.fix_button.setEnabled(True)
        else:
            self.status_label.setText("No Issues")
            self.status_label.setStyleSheet("color: green;")
            self.issues_label.setText("No issues found")
            self.issues_table.setRowCount(0)
            self.fix_button.setEnabled(False)
        
        # Enable view button for files only
        self.view_button.setEnabled(not is_folder)
        
        # Emit selected item signal
        self.item_selected.emit(item_info)
    
    def clear_details_panel(self):
        """Clear the details panel"""
        self.name_label.clear()
        self.path_label.clear()
        self.type_label.clear()
        self.size_label.clear()
        self.status_label.clear()
        self.status_label.setStyleSheet("")
        self.issues_label.clear()
        self.issues_table.setRowCount(0)
        self.view_button.setEnabled(False)
        self.fix_button.setEnabled(False)
    
    def clear_display(self):
        """Clear all display elements"""
        self.file_model.clear()
        self.file_model.setHorizontalHeaderLabels(["Name", "Size", "Status"])
        self.clear_details_panel()
        self.status_bar.setText("No scan results loaded")
        self.expand_all_button.setEnabled(False)
        self.collapse_all_button.setEnabled(False)
    
    def apply_search_filter(self):
        """Apply search filter to the tree view"""
        search_text = self.search_input.text()
        self.proxy_model.setFilterFixedString(search_text)
    
    def apply_type_filter(self):
        """Apply type filter to the tree view"""
        # This would be implemented with a custom filter in the proxy model
        # For brevity, this implementation is simplified
        self.apply_filters()
    
    def apply_issue_filter(self):
        """Apply issue filter to the tree view"""
        # This would be implemented with a custom filter in the proxy model
        # For brevity, this implementation is simplified
        self.apply_filters()
    
    def apply_filters(self):
        """Apply all filters to the tree view"""
        # This would implement the actual filtering logic
        # In a full implementation, you would create a custom proxy model
        # that can filter based on item type and issue presence
        pass
    
    def toggle_view_type(self, button):
        """Toggle between tree and list view"""
        is_tree_view = button.text() == "Tree View"
        
        # In a full implementation, this would switch between tree and list models
        # For brevity, this implementation just prints the change
        view_type = "Tree View" if is_tree_view else "List View"
        print(f"Switched to {view_type}")
    
    def on_view_button_clicked(self):
        """Handle view button click"""
        indexes = self.file_tree_view.selectedIndexes()
        if not indexes:
            return
            
        # Get the selected item's path
        index = self.proxy_model.mapToSource(indexes[0])
        item = self.file_model.itemFromIndex(index)
        
        if not item:
            return
            
        item_path = item.data(Qt.UserRole)
        
        # Emit signal to view file
        self.view_file_requested.emit(item_path)
    
    def show_context_menu(self, position):
        """Show context menu for tree view items"""
        indexes = self.file_tree_view.selectedIndexes()
        if not indexes:
            return
            
        # Get the selected item's path
        index = self.proxy_model.mapToSource(indexes[0])
        item = self.file_model.itemFromIndex(index)
        
        if not item:
            return
            
        item_path = item.data(Qt.UserRole)
        
        # Create context menu
        menu = QMenu()
        
        # Find item info to determine actions
        is_folder = False
        has_issues = False
        
        # Find item in file structure
        if self.scan_results:
            file_structure = self.scan_results.get('file_structure', {})
            parent_dir = os.path.dirname(item_path)
            
            if parent_dir in file_structure:
                # Check in folders
                if 'folders' in file_structure[parent_dir]:
                    for folder in file_structure[parent_dir]['folders']:
                        if folder['path'] == item_path:
                            is_folder = True
                            has_issues = 'issues' in folder and folder['issues']
                            break
                
                # Check in files
                if not is_folder and 'files' in file_structure[parent_dir]:
                    for file in file_structure[parent_dir]['files']:
                        if file['path'] == item_path:
                            has_issues = 'issues' in file and file['issues']
                            break
        
        # Add actions based on item type
        if is_folder:
            menu.addAction("Expand All", lambda: self.expand_subtree(index))
            menu.addAction("Collapse All", lambda: self.collapse_subtree(index))
            menu.addSeparator()
        else:
            menu.addAction("View File", lambda: self.view_file_requested.emit(item_path))
        
        if has_issues:
            menu.addAction("Fix Issues", lambda: print(f"Fix issues for {item_path}"))
        
        # Add common actions
        menu.addSeparator()
        menu.addAction("Copy Path", lambda: self.copy_to_clipboard(item_path))
        
        # Show menu
        menu.exec_(self.file_tree_view.viewport().mapToGlobal(position))
    
    def expand_subtree(self, index):
        """Expand the subtree of the given index"""
        proxy_index = self.proxy_model.mapFromSource(index)
        self.file_tree_view.expand(proxy_index)
        
        # Recursively expand all children
        model = index.model()
        for row in range(model.rowCount(index)):
            child_index = model.index(row, 0, index)
            self.expand_subtree(child_index)
    
    def collapse_subtree(self, index):
        """Collapse the subtree of the given index"""
        proxy_index = self.proxy_model.mapFromSource(index)
        self.file_tree_view.collapse(proxy_index)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(text)