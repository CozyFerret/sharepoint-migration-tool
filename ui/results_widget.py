#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Results widget for SharePoint Data Migration Cleanup Tool.
Displays detailed results of analysis.
"""

import os
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem, QHeaderView, 
                           QTabWidget, QComboBox, QPushButton)
from PyQt5.QtCore import Qt

logger = logging.getLogger('sharepoint_migration_tool')

class ResultsWidget(QWidget):
    """Widget for displaying detailed analysis results"""
    
    def __init__(self):
        """Initialize the results widget"""
        super().__init__()
        
        self.analysis_results = None
        
        # Set up the UI
        self.init_ui()
        
    def init_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(["All Issues", "Name Issues", "Path Issues", "Duplicates", "PII (Coming Soon)"])
        self.filter_type.currentIndexChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.filter_type)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["Path", "Issue Type", "Details", "Fixed In Cleanup", "Original Value", "Suggested Value"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel("No analysis results available")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
    def update_data(self, analysis_results):
        """
        Update the results with new analysis data
        
        Args:
            analysis_results (dict): Dictionary of analysis results
        """
        self.analysis_results = analysis_results
        
        if not analysis_results:
            self.status_label.setText("No analysis results available")
            self.results_table.setRowCount(0)
            return
            
        # Reset filter to show all issues
        self.filter_type.setCurrentIndex(0)
        
        # Apply the filter (which will populate the table)
        self._apply_filter(0)
        
    def _apply_filter(self, index):
        """
        Apply the selected filter to the results
        
        Args:
            index (int): Index of the selected filter
        """
        if not self.analysis_results:
            return
            
        # Clear the table
        self.results_table.setRowCount(0)
        
        # Get the selected filter type
        filter_type = self.filter_type.currentText()
        
        # Apply the filter
        if filter_type == "All Issues":
            self._populate_all_issues()
        elif filter_type == "Name Issues":
            self._populate_name_issues()
        elif filter_type == "Path Issues":
            self._populate_path_issues()
        elif filter_type == "Duplicates":
            self._populate_duplicates()
        elif filter_type.startswith("PII"):
            self._populate_pii()
            
    def _populate_all_issues(self):
        """Populate the table with all issues"""
        # Add name issues
        if 'name_issues' in self.analysis_results:
            for index, row in self.analysis_results['name_issues'].iterrows():
                self._add_row('Name Issue', row['name_issues'], row['path'], row['name'], row['suggested_name'])
                
        # Add path issues
        if 'path_issues' in self.analysis_results:
            for index, row in self.analysis_results['path_issues'].iterrows():
                self._add_row('Path Too Long', f"Path length: {row['path_length']} (max: {256})", 
                             row['path'], row['path'], row['suggested_path'])
                
        # Add duplicates
        if 'duplicates' in self.analysis_results:
            for index, row in self.analysis_results['duplicates'].iterrows():
                if not row['is_original']:
                    self._add_row('Duplicate File', f"Duplicate of {row['original_path']}", 
                                 row['path'], row['path'], 'Remove')
                    
        # Add PII
        if 'pii' in self.analysis_results:
            for index, row in self.analysis_results['pii'].iterrows():
                self._add_row('Potential PII', row['pii_types'] if 'pii_types' in row and row['pii_types'] else 'Placeholder', 
                             row['path'], row['path'], 'Flag for Review')
                
        # Update status
        total_issues = self.results_table.rowCount()
        self.status_label.setText(f"Found {total_issues} total issues")
        
    def _populate_name_issues(self):
        """Populate the table with name issues"""
        if 'name_issues' not in self.analysis_results:
            self.status_label.setText("No name issues found")
            return
            
        # Add name issues
        for index, row in self.analysis_results['name_issues'].iterrows():
            self._add_row('Name Issue', row['name_issues'], row['path'], row['name'], row['suggested_name'])
            
        # Update status
        total_issues = self.results_table.rowCount()
        self.status_label.setText(f"Found {total_issues} name issues")
        
    def _populate_path_issues(self):
        """Populate the table with path issues"""
        if 'path_issues' not in self.analysis_results:
            self.status_label.setText("No path issues found")
            return
            
        # Add path issues
        for index, row in self.analysis_results['path_issues'].iterrows():
            self._add_row('Path Too Long', f"Path length: {row['path_length']} (max: {256})", 
                         row['path'], row['path'], row['suggested_path'])
            
        # Update status
        total_issues = self.results_table.rowCount()
        self.status_label.setText(f"Found {total_issues} path issues")
        
    def _populate_duplicates(self):
        """Populate the table with duplicates"""
        if 'duplicates' not in self.analysis_results:
            self.status_label.setText("No duplicates found")
            return
            
        # Add duplicates
        for index, row in self.analysis_results['duplicates'].iterrows():
            if not row['is_original']:
                self._add_row('Duplicate File', f"Duplicate of {row['original_path']}", 
                             row['path'], row['path'], 'Remove')
            
    def _populate_pii(self):
        """Populate the table with PII issues (placeholder)"""
        if 'pii' not in self.analysis_results:
            self.status_label.setText("No PII detected (placeholder functionality)")
            return
            
        # Add PII issues
        for index, row in self.analysis_results['pii'].iterrows():
            self._add_row('Potential PII', row['pii_types'] if 'pii_types' in row and row['pii_types'] else 'Placeholder', 
                         row['path'], row['path'], 'Flag for Review')
            
        # Update status
        total_issues = self.results_table.rowCount()
        self.status_label.setText(f"Found {total_issues} potential PII issues (placeholder functionality)")
        
    def _add_row(self, issue_type, details, path, original, suggested):
        """
        Add a row to the results table
        
        Args:
            issue_type (str): Type of issue
            details (str): Details about the issue
            path (str): Path to the file
            original (str): Original value
            suggested (str): Suggested value
        """
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Add cells
        self.results_table.setItem(row, 0, QTableWidgetItem(path))
        self.results_table.setItem(row, 1, QTableWidgetItem(issue_type))
        self.results_table.setItem(row, 2, QTableWidgetItem(str(details)))
        self.results_table.setItem(row, 3, QTableWidgetItem("Yes"))  # Assume all issues are fixed in cleanup
        self.results_table.setItem(row, 4, QTableWidgetItem(str(original)))
        self.results_table.setItem(row, 5, QTableWidgetItem(str(suggested)))