from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableView, QLabel, QPushButton, 
                             QHeaderView, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush
import pandas as pd
import os
import logging

# Configure logger
logger = logging.getLogger('sharepoint_migration_tool')

class FileAnalysisViewHelper:
    """
    Helper class to implement missing functionality in the FileAnalysisView
    or extend existing functionality.
    """
    
    @staticmethod
    def set_data_enhanced(self, files_df, issues_df=None):
        """
        Enhanced set_data method to properly display file data
        
        Args:
            files_df (pandas.DataFrame): DataFrame containing file data
            issues_df (pandas.DataFrame): DataFrame containing issue data
        """
        logger.info("Setting data on FileAnalysisView (enhanced)")
        
        try:
            if files_df is None or files_df.empty:
                logger.warning("Empty file data provided to file analysis view")
                return
                
            # Store references to the data
            self.df = files_df
            self.issue_df = issues_df
            
            # Clear existing model
            self.model.clear()
            
            # Create headers based on DataFrame columns
            headers = files_df.columns.tolist()
            self.model.setHorizontalHeaderLabels(headers)
            
            # Populate the model with data and colorize based on issues
            for row_idx, row in files_df.iterrows():
                items = []
                
                # Determine if this file has issues
                has_issue = False
                if 'has_issues' in row:
                    has_issue = row['has_issues']
                elif hasattr(row, 'issue_count') and row.issue_count > 0:
                    has_issue = True
                elif issues_df is not None and 'file_path' in issues_df.columns:
                    # Check if this file has any issues in the issues DataFrame
                    file_path = row.get('full_path', row.get('path', ''))
                    if not pd.isna(file_path) and len(file_path) > 0:
                        has_issue = issues_df['file_path'].str.contains(file_path).any()
                
                # Create items for each column
                for col_idx, value in enumerate(row):
                    # Convert value to string and handle None/NaN
                    if pd.isna(value):
                        value_str = ""
                    else:
                        value_str = str(value)
                    
                    item = QStandardItem(value_str)
                    
                    # Apply color based on issue status
                    if has_issue:
                        # Add background color for rows with issues
                        item.setBackground(QBrush(QColor(255, 240, 240)))  # Light red
                        
                        # If this is an issue type column, make it red text
                        if headers[col_idx] in ['issue_type', 'issue_types'] and value_str:
                            item.setForeground(QBrush(QColor(200, 0, 0)))  # Red text
                    
                    items.append(item)
                
                self.model.appendRow(items)
            
            # Resize columns to content
            self.table_view.resizeColumnsToContents()
            
            # Update status
            self.status_label.setText(f"Displaying {len(files_df)} files")
            logger.info(f"File analysis view populated with {len(files_df)} files")
            
            # Update column filter combo box if it exists
            if hasattr(self, 'column_combo'):
                self.column_combo.clear()
                self.column_combo.addItem("All Columns")
                self.column_combo.addItems(headers)
        
        except Exception as e:
            logger.error(f"Error setting data on file analysis view: {e}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Error displaying data: {str(e)}")
    
    @staticmethod
    def enhance_file_analysis_tab(file_analysis_tab):
        """
        Enhance the FileAnalysisTab to properly handle data updates
        
        Args:
            file_analysis_tab: The FileAnalysisTab instance to enhance
            
        Returns:
            bool: True if enhancements were applied successfully
        """
        try:
            # First check if it has the required file_analysis_view attribute
            if not hasattr(file_analysis_tab, 'file_analysis_view'):
                logger.error("FileAnalysisTab missing file_analysis_view attribute")
                return False
            
            # Check if the view has a set_data method
            if not hasattr(file_analysis_tab.file_analysis_view, 'set_data'):
                logger.error("FileAnalysisView missing set_data method")
                return False
                
            # Create update_with_results method if it doesn't exist
            if not hasattr(file_analysis_tab, 'update_with_results'):
                def update_with_results(self, results):
                    """
                    Update the tab with scan results
                    
                    Args:
                        results (dict): Scan results dictionary
                    """
                    logger.info("Updating FileAnalysisTab with results")
                    
                    if not results:
                        return
                        
                    # Get DataFrames
                    files_df = None
                    issues_df = None
                    
                    if 'files_df' in results:
                        files_df = results['files_df']
                    elif 'all_files' in results:
                        files_df = results['all_files']
                    
                    if 'issues_df' in results:
                        issues_df = results['issues_df']
                        
                    # Update view if we have file data
                    if files_df is not None and not files_df.empty:
                        self.file_analysis_view.set_data(files_df, issues_df)
                        
                        # Update status with scan summary
                        total_files = len(files_df)
                        total_issues = len(issues_df) if issues_df is not None else 0
                        self.status_label.setText(
                            f"Data loaded: {total_files} files, {total_issues} issues"
                        )
                
                # Add the method to the instance
                file_analysis_tab.update_with_results = lambda results: update_with_results(file_analysis_tab, results)
                logger.info("Added update_with_results method to FileAnalysisTab")
            
            # Enhance the view's set_data method
            view = file_analysis_tab.file_analysis_view
            original_set_data = getattr(view, 'set_data', None)
            
            # Only replace if the original method exists
            if original_set_data:
                view.original_set_data = original_set_data
                view.set_data = lambda files_df, issues_df=None: FileAnalysisViewHelper.set_data_enhanced(view, files_df, issues_df)
                logger.info("Enhanced set_data method in FileAnalysisView")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enhancing FileAnalysisTab: {e}")
            return False
    
    @staticmethod
    def enhance_enhanced_data_view(enhanced_data_view):
        """
        Enhance the EnhancedDataView to properly handle data updates
        
        Args:
            enhanced_data_view: The EnhancedDataView instance to enhance
            
        Returns:
            bool: True if enhancements were applied successfully
        """
        try:
            # Add update_data method if it doesn't exist
            if not hasattr(enhanced_data_view, 'update_data'):
                def update_data(self, results):
                    """
                    Update the view with analysis results
                    
                    Args:
                        results (dict): Analysis results dictionary
                    """
                    logger.info("Updating EnhancedDataView with results")
                    
                    if not results:
                        return
                        
                    # Try to extract file data from the results
                    file_data = None
                    
                    if 'files_df' in results:
                        file_data = results['files_df']
                    elif 'all_files' in results:
                        file_data = results['all_files']
                    
                    # Set data if available
                    if file_data is not None and not (hasattr(file_data, 'empty') and file_data.empty):
                        self.set_data(file_data)
                
                # Add the method to the instance
                enhanced_data_view.update_data = lambda results: update_data(enhanced_data_view, results)
                logger.info("Added update_data method to EnhancedDataView")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enhancing EnhancedDataView: {e}")
            return False

# Function to apply all enhancements
def apply_view_enhancements(main_window):
    """
    Apply all view enhancements to the main window components
    
    Args:
        main_window: The MainWindow instance containing the views
        
    Returns:
        bool: True if enhancements were applied successfully
    """
    success = True
    
    try:
        # Enhance FileAnalysisTab if it exists
        if hasattr(main_window, 'file_analysis_tab'):
            success = success and FileAnalysisViewHelper.enhance_file_analysis_tab(main_window.file_analysis_tab)
        
        # Enhance EnhancedDataView if it exists
        if hasattr(main_window, 'analysis_view'):
            success = success and FileAnalysisViewHelper.enhance_enhanced_data_view(main_window.analysis_view)
        
        return success
        
    except Exception as e:
        logger.error(f"Error applying view enhancements: {e}")
        return False