"""
Simplified Enhanced Data View for SharePoint Migration Tool
This module provides a data view with basic sorting, filtering, and export capabilities.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableView, QLineEdit, QComboBox, 
                             QPushButton, QLabel, QFileDialog, 
                             QHeaderView, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class EnhancedDataView(QWidget):
    """
    A widget that provides an enhanced view for data with
    sorting, filtering, and export capabilities.
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
        
        # Search box
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter search term...")
        self.search_box.textChanged.connect(self.filter_data)
        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.search_box)
        
        # Export button
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_data)
        controls_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Table view
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
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
            items = []
            for value in row:
                item = QStandardItem(str(value))
                items.append(item)
            self.model.appendRow(items)
        
        # Update status
        self.status_label.setText(f"Displaying {len(data_frame)} items")
        
    def filter_data(self):
        """Apply filtering based on search box."""
        if self.df is None:
            return
            
        search_text = self.search_box.text()
        
        # Reset the proxy model's filter
        self.proxy_model.setFilterRegExp(QRegExp("", Qt.CaseInsensitive, QRegExp.FixedString))
        
        # If we have a search term, apply it as a filter
        if search_text:
            # Create a regex pattern for "contains" search
            pattern = ".*" + ".*".join(search_text.split()) + ".*"
            self.proxy_model.setFilterRegExp(QRegExp(pattern, Qt.CaseInsensitive, QRegExp.RegExp))
        
        # Update status
        visible_rows = self.proxy_model.rowCount()
        total_rows = len(self.df) if self.df is not None else 0
        self.status_label.setText(f"Displaying {visible_rows} of {total_rows} items")
        
    def export_data(self):
        """Export the data to CSV."""
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
            
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            "",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        # Ensure file has the correct extension
        if not file_path.endswith('.csv'):
            file_path += '.csv'
            
        try:
            # Export to CSV
            self.df.to_csv(file_path, index=False)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Data successfully exported to {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export data: {str(e)}"
            )
    
    def show_export_menu(self):
        """Show the export menu (simplified to just call export)."""
        self.export_data()