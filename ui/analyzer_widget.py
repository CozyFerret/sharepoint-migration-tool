#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyzer widget for SharePoint Data Migration Cleanup Tool.
Handles analysis of scanned files for various issues.
"""

import os
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QProgressBar, QTabWidget, QTextEdit, QTableWidget,
                           QTableWidgetItem, QHeaderView, QPushButton)
from PyQt5.QtCore import Qt

from core.analyzers.name_validator import SharePointNameValidator
from core.analyzers.path_analyzer import PathAnalyzer
from core.analyzers.duplicate_finder import DuplicateFinder
from core.analyzers.pii_detector import PIIDetector

logger = logging.getLogger('sharepoint_migration_tool')

class AnalyzerWidget(QWidget):
    """Widget for analyzing scanned files"""
    
    def __init__(self, config=None):
        """
        Initialize the analyzer widget
        
        Args:
            config (dict): Application configuration
        """
        super().__init__()
        
        self.config = config or {}
        self.scan_data = None
        self.analysis_results = {}
        
        # Initialize analyzers
        self.name_validator = SharePointNameValidator(self.config)
        self.path_analyzer = PathAnalyzer(self.config)
        self.duplicate_finder = DuplicateFinder(self.config)
        self.pii_detector = PIIDetector(self.config)
        
        # Set up the UI
        self.init_ui()
        
    def init_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Analysis progress
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Analysis Progress:"))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar, 1)
        
        main_layout.addLayout(progress_layout)
        
        # Tab widget for different analyses
        self.tabs = QTabWidget()
        
        # Name issues tab
        self.name_issues_tab = QWidget()
        name_issues_layout = QVBoxLayout(self.name_issues_tab)
        
        self.name_issues_table = QTableWidget()
        self.name_issues_table.setColumnCount(4)
        self.name_issues_table.setHorizontalHeaderLabels(["Path", "Name", "Issues", "Suggested Name"])
        self.name_issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.name_issues_table.setAlternatingRowColors(True)
        
        name_issues_layout.addWidget(self.name_issues_table)
        self.tabs.addTab(self.name_issues_tab, "Name Issues")
        
        # Path issues tab
        self.path_issues_tab = QWidget()
        path_issues_layout = QVBoxLayout(self.path_issues_tab)
        
        self.path_issues_table = QTableWidget()
        self.path_issues_table.setColumnCount(4)
        self.path_issues_table.setHorizontalHeaderLabels(["Path", "Length", "Too Long", "Suggested Path"])
        self.path_issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.path_issues_table.setAlternatingRowColors(True)
        
        path_issues_layout.addWidget(self.path_issues_table)
        self.tabs.addTab(self.path_issues_tab, "Path Issues")
        
        # Duplicates tab
        self.duplicates_tab = QWidget()
        duplicates_layout = QVBoxLayout(self.duplicates_tab)
        
        self.duplicates_table = QTableWidget()
        self.duplicates_table.setColumnCount(4)
        self.duplicates_table.setHorizontalHeaderLabels(["Path", "Size", "Original", "Original Path"])
        self.duplicates_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.duplicates_table.setAlternatingRowColors(True)
        
        duplicates_layout.addWidget(self.duplicates_table)
        self.tabs.addTab(self.duplicates_tab, "Duplicates")
        
        # PII tab
        self.pii_tab = QWidget()
        pii_layout = QVBoxLayout(self.pii_tab)
        
        # Add a note that PII detection is a placeholder
        self.pii_note = QLabel("PII Detection is a placeholder in this version. Full functionality coming soon.")
        self.pii_note.setStyleSheet("color: red; font-weight: bold;")
        self.pii_note.setAlignment(Qt.AlignCenter)
        pii_layout.addWidget(self.pii_note)
        
        self.pii_table = QTableWidget()
        self.pii_table.setColumnCount(3)
        self.pii_table.setHorizontalHeaderLabels(["Path", "PII Detected", "PII Types"])
        self.pii_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pii_table.setAlternatingRowColors(True)
        
        pii_layout.addWidget(self.pii_table)
        self.tabs.addTab(self.pii_tab, "PII (Coming Soon)")
        
        # Add tabs to main layout
        main_layout.addWidget(self.tabs)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        main_layout.addWidget(self.status_text)
        
    def analyze_data(self, data, feature_flags=None):
        """
        Analyze scanned file data
        
        Args:
            data (pandas.DataFrame): DataFrame with scanned file data
            feature_flags (dict): Dictionary of feature flags
        """
        self.scan_data = data
        self.analysis_results = {}
        
        if data is None or len(data) == 0:
            self.status_text.append("No data to analyze")
            self.progress_bar.setValue(0)
            return
            
        self.status_text.append(f"Analyzing {len(data)} files...")
        
        # Reset tables
        self.name_issues_table.setRowCount(0)
        self.path_issues_table.setRowCount(0)
        self.duplicates_table.setRowCount(0)
        self.pii_table.setRowCount(0)
        
        # Progress tracking
        total_steps = 0
        completed_steps = 0
        
        if feature_flags is None:
            feature_flags = {
                'name_validation': True, 
                'path_length': True,
                'duplicate_detection': True,
                'pii_detection': True
            }
            
        # Count total steps
        if feature_flags.get('name_validation', True):
            total_steps += 1
        if feature_flags.get('path_length', True):
            total_steps += 1
        if feature_flags.get('duplicate_detection', True):
            total_steps += 1
        if feature_flags.get('pii_detection', True):
            total_steps += 1
            
        # Analyze name issues
        if feature_flags.get('name_validation', True):
            self.status_text.append("Analyzing file names...")
            
            try:
                name_results = self.name_validator.analyze_dataframe(data)
                self.analysis_results['name_issues'] = name_results[name_results['name_valid'] == False]
                self._populate_name_issues_table()
                
                completed_steps += 1
                self.progress_bar.setValue(int(completed_steps / total_steps * 100))
                
                self.status_text.append(f"Found {len(self.analysis_results['name_issues'])} files with name issues")
            except Exception as e:
                logger.error(f"Error analyzing names: {e}")
                self.status_text.append(f"Error analyzing names: {e}")
                
        # Analyze path issues
        if feature_flags.get('path_length', True):
            self.status_text.append("Analyzing path lengths...")
            
            try:
                path_results = self.path_analyzer.analyze_dataframe(data)
                self.analysis_results['path_issues'] = path_results[path_results['path_too_long'] == True]
                self._populate_path_issues_table()
                
                completed_steps += 1
                self.progress_bar.setValue(int(completed_steps / total_steps * 100))
                
                self.status_text.append(f"Found {len(self.analysis_results['path_issues'])} files with path issues")
            except Exception as e:
                logger.error(f"Error analyzing paths: {e}")
                self.status_text.append(f"Error analyzing paths: {e}")
                
        # Analyze duplicates
        if feature_flags.get('duplicate_detection', True):
            self.status_text.append("Analyzing duplicate files...")
            
            try:
                duplicate_results = self.duplicate_finder.analyze_dataframe(data)
                self.analysis_results['duplicates'] = duplicate_results[duplicate_results['is_duplicate'] == True]
                self._populate_duplicates_table()
                
                completed_steps += 1
                self.progress_bar.setValue(int(completed_steps / total_steps * 100))
                
                self.status_text.append(f"Found {len(self.analysis_results['duplicates'])} files in duplicate groups")
            except Exception as e:
                logger.error(f"Error analyzing duplicates: {e}")
                self.status_text.append(f"Error analyzing duplicates: {e}")
                
        # Analyze PII (placeholder)
        if feature_flags.get('pii_detection', True):
            self.status_text.append("PII detection is a placeholder in this version...")
            
            try:
                pii_results = self.pii_detector.analyze_dataframe(data)
                self.analysis_results['pii'] = pii_results[pii_results['potential_pii'] == True]
                self._populate_pii_table()
                
                completed_steps += 1
                self.progress_bar.setValue(int(completed_steps / total_steps * 100))
                
                self.status_text.append(f"Found {len(self.analysis_results['pii'])} files with potential PII")
                self.status_text.append("Note: PII detection is a placeholder in this version")
            except Exception as e:
                logger.error(f"Error analyzing PII: {e}")
                self.status_text.append(f"Error analyzing PII: {e}")
                
        self.status_text.append("Analysis complete")
        
    def _populate_name_issues_table(self):
        """Populate the name issues table with analysis results"""
        if 'name_issues' not in self.analysis_results:
            return
            
        table = self.name_issues_table
        table.setRowCount(0)
        
        for index, row in self.analysis_results['name_issues'].iterrows():
            table_row = table.rowCount()
            table.insertRow(table_row)
            
            table.setItem(table_row, 0, QTableWidgetItem(row['path']))
            table.setItem(table_row, 1, QTableWidgetItem(row['name']))
            table.setItem(table_row, 2, QTableWidgetItem(row['name_issues']))
            table.setItem(table_row, 3, QTableWidgetItem(row['suggested_name']))
            
    def _populate_path_issues_table(self):
        """Populate the path issues table with analysis results"""
        if 'path_issues' not in self.analysis_results:
            return
            
        table = self.path_issues_table
        table.setRowCount(0)
        
        for index, row in self.analysis_results['path_issues'].iterrows():
            table_row = table.rowCount()
            table.insertRow(table_row)
            
            table.setItem(table_row, 0, QTableWidgetItem(row['path']))
            table.setItem(table_row, 1, QTableWidgetItem(str(row['path_length'])))
            table.setItem(table_row, 2, QTableWidgetItem("Yes" if row['path_too_long'] else "No"))
            table.setItem(table_row, 3, QTableWidgetItem(row['suggested_path']))
            
    def _populate_duplicates_table(self):
        """Populate the duplicates table with analysis results"""
        if 'duplicates' not in self.analysis_results:
            return
            
        table = self.duplicates_table
        table.setRowCount(0)
        
        for index, row in self.analysis_results['duplicates'].iterrows():
            table_row = table.rowCount()
            table.insertRow(table_row)
            
            # Format file size
            size_str = str(row['size'])
            if 'size' in row:
                size_bytes = row['size']
                if size_bytes < 1024:
                    size_str = f"{size_bytes} bytes"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.2f} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            
            table.setItem(table_row, 0, QTableWidgetItem(row['path']))
            table.setItem(table_row, 1, QTableWidgetItem(size_str))
            table.setItem(table_row, 2, QTableWidgetItem("Yes" if row['is_original'] else "No"))
            
            if not row['is_original'] and 'original_path' in row and row['original_path']:
                table.setItem(table_row, 3, QTableWidgetItem(row['original_path']))
            else:
                table.setItem(table_row, 3, QTableWidgetItem("N/A"))
                
    def _populate_pii_table(self):
        """Populate the PII table with analysis results"""
        if 'pii' not in self.analysis_results:
            return
            
        table = self.pii_table
        table.setRowCount(0)
        
        for index, row in self.analysis_results['pii'].iterrows():
            table_row = table.rowCount()
            table.insertRow(table_row)
            
            table.setItem(table_row, 0, QTableWidgetItem(row['path']))
            table.setItem(table_row, 1, QTableWidgetItem("Yes" if row['potential_pii'] else "No"))
            
            if 'pii_types' in row and row['pii_types']:
                table.setItem(table_row, 2, QTableWidgetItem(row['pii_types']))
            else:
                table.setItem(table_row, 2, QTableWidgetItem("Placeholder Only"))
                
    def get_analysis_results(self):
        """
        Get the analysis results
        
        Returns:
            dict: Analysis results for each feature
        """
        return self.analysis_results