"""
Enhanced Data View for SharePoint Migration Tool
This module provides an interactive data view with sorting, filtering, 
searching, and multi-format export capabilities.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableView, QLineEdit, QComboBox, 
                             QPushButton, QLabel, QFileDialog, 
                             QHeaderView, QMessageBox, QApplication,
                             QMenu, QAction)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import os
import json
import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedDataView(QWidget):
    """
    A widget that provides an enhanced view for file migration data
    with sorting, filtering, searching, and export capabilities.
    """
    
    def __init__(self, parent=None):
        super(EnhancedDataView, self).__init__(parent)
        self.df = None  # DataFrame to hold the data
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Search and filter controls
        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)
        
        # Search box
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter search term...")
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
        
        # Export button with dropdown
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.show_export_menu)
        controls_layout.addWidget(self.export_btn)
        
        # Table view
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setSectionsMovable(True)
        self.table_view.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table_view)
        
        # Create model and proxy model for sorting/filtering
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(self.proxy_model)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
    def set_data(self, data_frame):
        """
        Set the data to be displayed in the table view.
        
        Args:
            data_frame (pandas.DataFrame): The data to display
        """
        if data_frame is None or data_frame.empty:
            logger.warning("Attempted to set empty data to enhanced view")
            return
            
        self.df = data_frame
        
        # Clear existing model
        self.model.clear()
        
        # Set headers
        headers = data_frame.columns.tolist()
        self.model.setHorizontalHeaderLabels(headers)
        
        # Populate the model with data
        for row_idx, row in data_frame.iterrows():
            items = [QStandardItem(str(value)) for value in row]
            self.model.appendRow(items)
        
        # Update column filter combo box
        self.column_combo.clear()
        self.column_combo.addItem("All Columns")
        self.column_combo.addItems(headers)
        
        # Update status
        self.status_label.setText(f"Displaying {len(data_frame)} items")
        logger.info(f"Enhanced view populated with {len(data_frame)} items")
        
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
        """Apply filtering based on search box and filter combo."""
        if self.df is None:
            return
            
        search_text = self.search_box.text()
        column_idx = self.column_combo.currentIndex() - 1  # -1 because of "All Columns"
        filter_value = self.filter_combo.currentText()
        
        # Reset the proxy model's filter
        self.proxy_model.setFilterRegExp(QRegExp("", Qt.CaseInsensitive, QRegExp.FixedString))
        
        # If we have a search term, apply it as a filter
        if search_text:
            if column_idx >= 0:  # Filter on specific column
                self.proxy_model.setFilterKeyColumn(column_idx)
                self.proxy_model.setFilterRegExp(QRegExp(search_text, Qt.CaseInsensitive, QRegExp.FixedString))
            else:  # Filter on all columns
                # We need to create a custom filter for "all columns" search
                self.proxy_model.setFilterKeyColumn(-1)  # -1 means all columns
                pattern = ".*" + ".*".join(search_text.split()) + ".*"
                self.proxy_model.setFilterRegExp(QRegExp(pattern, Qt.CaseInsensitive, QRegExp.RegExp))
        
        # If we have a filter value, apply additional filtering
        if filter_value and column_idx >= 0:
            # Create a temp proxy model just for this filter
            temp_proxy = QSortFilterProxyModel()
            temp_proxy.setSourceModel(self.proxy_model)
            temp_proxy.setFilterKeyColumn(column_idx)
            temp_proxy.setFilterRegExp(QRegExp("^" + filter_value + "$", Qt.CaseInsensitive, QRegExp.RegExp))
            self.table_view.setModel(temp_proxy)
        else:
            # Just use the main proxy model
            self.table_view.setModel(self.proxy_model)
        
        # Update status
        visible_rows = self.table_view.model().rowCount()
        total_rows = len(self.df) if self.df is not None else 0
        self.status_label.setText(f"Displaying {visible_rows} of {total_rows} items")
        
    def clear_filters(self):
        """Clear all filters and search terms."""
        self.search_box.clear()
        self.column_combo.setCurrentIndex(0)
        self.filter_combo.clear()
        
        # Reset proxy model
        self.proxy_model.setFilterRegExp(QRegExp("", Qt.CaseInsensitive, QRegExp.FixedString))
        self.table_view.setModel(self.proxy_model)
        
        # Update status
        total_rows = len(self.df) if self.df is not None else 0
        self.status_label.setText(f"Displaying {total_rows} of {total_rows} items")
        
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
        
        # Show the menu at the button's position
        menu.exec_(self.export_btn.mapToGlobal(self.export_btn.rect().bottomLeft()))
        
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
            
    def copy_to_clipboard(self):
        """Copy selected data to clipboard."""
        selection_model = self.table_view.selectionModel()
        if not selection_model.hasSelection():
            return
            
        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return
            
        # Sort by row, then column
        selected_indexes.sort(key=lambda x: (x.row(), x.column()))
        
        # Group by rows
        rows = {}
        for index in selected_indexes:
            if index.row() not in rows:
                rows[index.row()] = []
            rows[index.row()].append(index.data())
            
        # Create a string with tab-separated values and newlines for rows
        text = '\n'.join('\t'.join(str(cell) for cell in row) for row in rows.values())
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        self.status_label.setText("Selection copied to clipboard")