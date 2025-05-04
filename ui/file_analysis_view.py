"""
File Analysis View for SharePoint Migration Tool
This module provides a detailed file-level view with advanced sorting, filtering,
searching, and multi-format export capabilities.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableView, QLineEdit, QComboBox, 
                             QPushButton, QLabel, QFileDialog, 
                             QHeaderView, QMessageBox, QApplication,
                             QMenu, QAction, QCheckBox, QToolBar,
                             QSplitter, QTreeView)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp, QDateTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush, QIcon
import pandas as pd
import os
import json
import csv
import logging
from pathlib import Path
import datetime
import hashlib

logger = logging.getLogger(__name__)

class FileAnalysisView(QWidget):
    """
    A specialized widget for detailed file-level analysis with advanced
    filtering, sorting, and visualization capabilities.
    """
    
    def __init__(self, parent=None):
        super(FileAnalysisView, self).__init__(parent)
        self.df = None  # DataFrame to hold the file data
        self.issue_df = None  # DataFrame to hold issue data
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create toolbar for common actions
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Add refresh action
        refresh_action = QAction(QIcon(), "Refresh", self)
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
        
        # Add export action
        export_action = QAction(QIcon(), "Export", self)
        export_action.triggered.connect(self.show_export_menu)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Add filter toggles
        self.show_issues_only = QCheckBox("Show Issues Only")
        self.show_issues_only.stateChanged.connect(self.filter_data)
        toolbar.addWidget(self.show_issues_only)
        
        # Add issue type filter
        issue_label = QLabel("Issue Type:")
        toolbar.addWidget(issue_label)
        self.issue_combo = QComboBox()
        self.issue_combo.addItem("All Issues")
        self.issue_combo.currentIndexChanged.connect(self.filter_data)
        toolbar.addWidget(self.issue_combo)
        
        main_layout.addWidget(toolbar)
        
        # Search and filter controls
        controls_layout = QHBoxLayout()
        
        # Search box
        search_label = QLabel("Search Files:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter file name, path or attribute...")
        self.search_box.textChanged.connect(self.filter_data)
        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.search_box)
        
        # Column filter
        filter_label = QLabel("Filter Column:")
        self.column_combo = QComboBox()
        self.column_combo.currentIndexChanged.connect(self.update_filter_combo)
        controls_layout.addWidget(filter_label)
        controls_layout.addWidget(self.column_combo)
        
        # Filter value
        value_label = QLabel("Value:")
        self.filter_combo = QComboBox()
        self.filter_combo.setEditable(True)
        self.filter_combo.currentTextChanged.connect(self.filter_data)
        controls_layout.addWidget(value_label)
        controls_layout.addWidget(self.filter_combo)
        
        # Clear filters button
        self.clear_btn = QPushButton("Clear Filters")
        self.clear_btn.clicked.connect(self.clear_filters)
        controls_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Create a splitter for file list and details
        splitter = QSplitter(Qt.Vertical)
        
        # Table view for files
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setSectionsMovable(True)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)
        self.table_view.doubleClicked.connect(self.show_file_details)
        splitter.addWidget(self.table_view)
        
        # Detail view for selected file
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        
        detail_title = QLabel("File Details")
        detail_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        detail_layout.addWidget(detail_title)
        
        self.detail_table = QTableView()
        self.detail_table.setAlternatingRowColors(True)
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detail_table.verticalHeader().setVisible(False)
        detail_layout.addWidget(self.detail_table)
        
        # Issue details for selected file
        issue_title = QLabel("Issues")
        issue_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        detail_layout.addWidget(issue_title)
        
        self.issue_table = QTableView()
        self.issue_table.setAlternatingRowColors(True)
        self.issue_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.issue_table.verticalHeader().setVisible(False)
        detail_layout.addWidget(self.issue_table)
        
        splitter.addWidget(self.detail_widget)
        
        # Set initial splitter sizes (70% files, 30% details)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter, 1)  # 1 = stretch factor
        
        # Create model and proxy model for sorting/filtering
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(self.proxy_model)
        
        # Detail view models
        self.detail_model = QStandardItemModel()
        self.detail_table.setModel(self.detail_model)
        
        self.issue_model = QStandardItemModel()
        self.issue_table.setModel(self.issue_model)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
    
    def set_data(self, file_data, issue_data=None):
        """
        Set the file data to be displayed in the table view.
        
        Args:
            file_data (pandas.DataFrame): The file data to display
            issue_data (pandas.DataFrame, optional): The issue data to display
        """
        if file_data is None or file_data.empty:
            logger.warning("Attempted to set empty data to file analysis view")
            return
            
        self.df = file_data
        self.issue_df = issue_data
        
        # Clear existing model
        self.model.clear()
        
        # Set headers
        headers = file_data.columns.tolist()
        self.model.setHorizontalHeaderLabels(headers)
        
        # Populate the model with data and colorize based on issues
        for row_idx, row in file_data.iterrows():
            items = []
            has_issue = False
            
            # Determine if this file has issues
            if 'has_issues' in row:
                has_issue = row['has_issues']
            elif issue_data is not None and 'file_path' in issue_data.columns:
                has_issue = issue_data['file_path'].str.contains(row['full_path']).any() if 'full_path' in row else False
            
            # Create items with appropriate colors based on issue status
            for col_idx, value in enumerate(row):
                item = QStandardItem(str(value))
                
                # Apply color based on issue status
                if has_issue:
                    # Add background color for rows with issues
                    item.setBackground(QBrush(QColor(255, 240, 240)))  # Light red
                    
                    # If this is an issue type column, make it red text
                    if headers[col_idx] == 'issue_type' and value:
                        item.setForeground(QBrush(QColor(200, 0, 0)))  # Red text
                
                # Set color for specific issue types in the issue column
                if headers[col_idx] == 'issue_type':
                    if 'critical' in str(value).lower():
                        item.setForeground(QBrush(QColor(200, 0, 0)))  # Red text
                    elif 'warning' in str(value).lower():
                        item.setForeground(QBrush(QColor(255, 140, 0)))  # Orange text
                
                items.append(item)
            
            self.model.appendRow(items)
        
        # Update column filter combo box
        self.column_combo.clear()
        self.column_combo.addItem("All Columns")
        self.column_combo.addItems(headers)
        
        # Update issue type filter
        self.update_issue_filter()
        
        # Update status
        self.status_label.setText(f"Displaying {len(file_data)} files")
        logger.info(f"File analysis view populated with {len(file_data)} files")
    
    def update_issue_filter(self):
        """Update the issue type filter with values from the issue data."""
        self.issue_combo.clear()
        self.issue_combo.addItem("All Issues")
        
        if self.issue_df is not None and 'issue_type' in self.issue_df.columns:
            issue_types = self.issue_df['issue_type'].dropna().unique()
            self.issue_combo.addItems(sorted([str(val) for val in issue_types]))
    
    def update_filter_combo(self):
        """Update the filter combo box with values from the selected column."""
        self.filter_combo.clear()
        
        column_idx = self.column_combo.currentIndex() - 1  # -1 because of "All Columns"
        if column_idx < 0 or self.df is None:
            return
            
        column_name = self.df.columns[column_idx]
        unique_values = self.df[column_name].dropna().unique()
        
        # Add an empty option at the top
        self.filter_combo.addItem("")
        
        # Add unique values sorted alphabetically
        sorted_values = sorted([str(val) for val in unique_values], key=lambda x: str(x).lower())
        self.filter_combo.addItems(sorted_values)
    
    def filter_data(self):
        """Apply filtering based on search box, filter combo, and issue filter."""
        if self.df is None:
            return
            
        search_text = self.search_box.text()
        column_idx = self.column_combo.currentIndex() - 1  # -1 because of "All Columns"
        filter_value = self.filter_combo.currentText()
        show_issues_only = self.show_issues_only.isChecked()
        issue_type = self.issue_combo.currentText() if self.issue_combo.currentText() != "All Issues" else ""
        
        # Reset the proxy model's filter
        self.proxy_model.setFilterRegExp(QRegExp("", Qt.CaseInsensitive, QRegExp.FixedString))
        
        # Combine all filters using a custom filtering function
        def custom_filter(source_row, source_parent):
            # First check issue filter
            if show_issues_only or issue_type:
                # If we're showing issues only, check if this row has an issue
                has_issue = False
                has_matching_issue_type = True
                
                if 'has_issues' in self.df.columns:
                    has_issue = self.df.iloc[source_row]['has_issues']
                elif self.issue_df is not None and 'file_path' in self.issue_df.columns:
                    file_path = self.model.index(source_row, self.df.columns.get_loc('full_path') if 'full_path' in self.df.columns else 0).data()
                    has_issue = self.issue_df['file_path'].str.contains(file_path).any()
                    
                    # If we're filtering by issue type, check if this row has that issue type
                    if issue_type and has_issue:
                        matching_issues = self.issue_df[self.issue_df['file_path'].str.contains(file_path)]
                        has_matching_issue_type = matching_issues['issue_type'].str.contains(issue_type).any() if not matching_issues.empty else False
                
                if show_issues_only and not has_issue:
                    return False
                
                if issue_type and not (has_issue and has_matching_issue_type):
                    return False
            
            # Then check search and column filters
            if search_text:
                # Search in specific column
                if column_idx >= 0:
                    model_index = self.model.index(source_row, column_idx)
                    cell_text = self.model.data(model_index)
                    return search_text.lower() in str(cell_text).lower()
                else:
                    # Search in all columns
                    for col in range(self.model.columnCount()):
                        model_index = self.model.index(source_row, col)
                        cell_text = self.model.data(model_index)
                        if search_text.lower() in str(cell_text).lower():
                            return True
                    return False
            
            # Then check specific column filter
            if filter_value and column_idx >= 0:
                model_index = self.model.index(source_row, column_idx)
                cell_text = self.model.data(model_index)
                return filter_value.lower() == str(cell_text).lower()
            
            # If we got here, all filters passed
            return True
        
        # Create a custom proxy model with our filter function
        class CustomFilterProxy(QSortFilterProxyModel):
            def filterAcceptsRow(self, source_row, source_parent):
                return custom_filter(source_row, source_parent)
        
        # Apply our custom proxy model
        custom_proxy = CustomFilterProxy()
        custom_proxy.setSourceModel(self.model)
        self.table_view.setModel(custom_proxy)
        
        # Update status
        visible_rows = self.table_view.model().rowCount()
        total_rows = len(self.df) if self.df is not None else 0
        self.status_label.setText(f"Displaying {visible_rows} of {total_rows} files")
    
    def clear_filters(self):
        """Clear all filters and search terms."""
        self.search_box.clear()
        self.column_combo.setCurrentIndex(0)
        self.filter_combo.clear()
        self.show_issues_only.setChecked(False)
        self.issue_combo.setCurrentIndex(0)
        
        # Reset proxy model
        self.proxy_model.setFilterRegExp(QRegExp("", Qt.CaseInsensitive, QRegExp.FixedString))
        self.table_view.setModel(self.proxy_model)
        
        # Update status
        total_rows = len(self.df) if self.df is not None else 0
        self.status_label.setText(f"Displaying {total_rows} of {total_rows} files")
    
    def show_file_details(self, index):
        """Show detailed information for the selected file."""
        # Get the source row from the proxy model
        proxy_model = self.table_view.model()
        source_row = proxy_model.mapToSource(index).row()
        
        # Get file path from the data model
        file_path_col = self.df.columns.get_loc('full_path') if 'full_path' in self.df.columns else 0
        file_path = self.model.index(source_row, file_path_col).data()
        
        # Clear existing detail models
        self.detail_model.clear()
        self.issue_model.clear()
        
        # Set up the detail model
        self.detail_model.setHorizontalHeaderLabels(['Property', 'Value'])
        
        # Get all the properties for this file
        row_data = self.df.iloc[source_row].to_dict()
        
        # Add each property to the detail model
        for prop, value in row_data.items():
            self.detail_model.appendRow([
                QStandardItem(prop),
                QStandardItem(str(value))
            ])
        
        # Find any issues for this file
        if self.issue_df is not None and 'file_path' in self.issue_df.columns:
            matching_issues = self.issue_df[self.issue_df['file_path'].str.contains(file_path)]
            
            if not matching_issues.empty:
                # Set up the issue model headers
                issue_headers = matching_issues.columns.tolist()
                self.issue_model.setHorizontalHeaderLabels(issue_headers)
                
                # Add each issue to the model
                for _, issue in matching_issues.iterrows():
                    items = []
                    for value in issue:
                        items.append(QStandardItem(str(value)))
                    self.issue_model.appendRow(items)
    
    def refresh_data(self):
        """Refresh the data view."""
        if self.df is not None:
            self.set_data(self.df, self.issue_df)
    
    def show_export_menu(self):
        """Show the export options menu."""
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
            
        menu = QMenu(self)
        
        # Export actions
        csv_action = QAction("Export as CSV", self)
        csv_action.triggered.connect(lambda: self.export_data("csv"))
        
        excel_action = QAction("Export as Excel", self)
        excel_action.triggered.connect(lambda: self.export_data("excel"))
        
        json_action = QAction("Export as JSON", self)
        json_action.triggered.connect(lambda: self.export_data("json"))
        
        text_action = QAction("Export as Text", self)
        text_action.triggered.connect(lambda: self.export_data("text"))
        
        # Add actions to menu
        menu.addAction(csv_action)
        menu.addAction(excel_action)
        menu.addAction(json_action)
        menu.addAction(text_action)
        
        # Show the menu
        menu.exec_(QCursor().pos())
    
    def export_data(self, format_type):
        """
        Export the data in the specified format.
        
        Args:
            format_type (str): The format to export ('csv', 'excel', 'json', or 'text')
        """
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
            
        # Get currently filtered data
        proxy_model = self.table_view.model()
        row_count = proxy_model.rowCount()
        col_count = proxy_model.columnCount()
        
        # Create a new DataFrame with the filtered data
        headers = [proxy_model.headerData(i, Qt.Horizontal) for i in range(col_count)]
        data = []
        
        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                index = proxy_model.index(row, col)
                row_data.append(proxy_model.data(index))
            data.append(row_data)
            
        export_df = pd.DataFrame(data, columns=headers)
        
        # Get file path from user
        file_types = {
            "csv": "CSV Files (*.csv)",
            "excel": "Excel Files (*.xlsx)",
            "json": "JSON Files (*.json)",
            "text": "Text Files (*.txt)"
        }
        
        file_extensions = {
            "csv": ".csv",
            "excel": ".xlsx",
            "json": ".json",
            "text": ".txt"
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            "",
            file_types.get(format_type, "All Files (*)")
        )
        
        if not file_path:
            return
            
        # Ensure file has the correct extension
        if not file_path.endswith(file_extensions[format_type]):
            file_path += file_extensions[format_type]
            
        try:
            # Export based on format
            if format_type == "csv":
                export_df.to_csv(file_path, index=False, quoting=csv.QUOTE_MINIMAL)
            elif format_type == "excel":
                export_df.to_excel(file_path, index=False)
            elif format_type == "json":
                export_df.to_json(file_path, orient="records", indent=4)
            elif format_type == "text":
                with open(file_path, 'w') as f:
                    # Write headers
                    f.write('\t'.join(headers) + '\n')
                    # Write data
                    for row in data:
                        f.write('\t'.join([str(cell) for cell in row]) + '\n')
                        
            QMessageBox.information(
                self,
                "Export Successful",
                f"Data successfully exported to {os.path.basename(file_path)}"
            )
            logger.info(f"Data exported to {file_path} in {format_type} format")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export data: {str(e)}"
            )
            logger.error(f"Export error: {str(e)}")