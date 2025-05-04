#!/usr/bin/env python
"""
Integration script to apply fixes to the SharePoint Migration Tool
This will modify the main.py file to incorporate the enhancements
"""

import sys
import os
import logging
import importlib.util
import tempfile
import shutil

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('integration')

def backup_original_file(file_path):
    """Create a backup of the original file"""
    backup_path = file_path + '.bak'
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup of {file_path} at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False

def load_module_from_file(file_path, module_name):
    """Dynamically load a module from a file path"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Failed to load module from {file_path}: {e}")
        return None

def modify_main_py(project_dir):
    """Modify main.py to incorporate the enhancements"""
    main_py_path = os.path.join(project_dir, 'main.py')
    
    if not os.path.exists(main_py_path):
        logger.error(f"main.py not found at {main_py_path}")
        return False
    
    # Backup the original file
    if not backup_original_file(main_py_path):
        return False
    
    try:
        # Load the original main.py content
        with open(main_py_path, 'r') as f:
            main_py_content = f.read()
        
        # Find the section where MainWindow is created and shown
        target_section = "main_window = MainWindow()"
        
        if target_section not in main_py_content:
            logger.error(f"Target section '{target_section}' not found in main.py")
            return False
        
        # Generate the new code to insert
        enhancement_code = """
            # Apply data flow fixes from the DataFlowFixes module
            try:
                from data_flow_fixes import modify_main_window
                modify_main_window(main_window)
                logging.info("Applied data flow fixes to MainWindow")
            except Exception as e:
                logging.error(f"Failed to apply data flow fixes: {e}")
            
            # Apply view enhancements
            try:
                from file_analysis_enhancements import apply_view_enhancements
                apply_view_enhancements(main_window)
                logging.info("Applied view enhancements")
            except Exception as e:
                logging.error(f"Failed to apply view enhancements: {e}")
        """
        
        # Replace the target section with the enhanced version
        modified_content = main_py_content.replace(
            target_section, 
            target_section + enhancement_code
        )
        
        # Write the modified content back to main.py
        with open(main_py_path, 'w') as f:
            f.write(modified_content)
        
        logger.info(f"Successfully modified {main_py_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error modifying main.py: {e}")
        return False

def create_fix_modules(project_dir):
    """Create the necessary module files for the fixes"""
    try:
        # Create data_flow_fixes.py
        data_flow_fixes_path = os.path.join(project_dir, 'data_flow_fixes.py')
        with open(data_flow_fixes_path, 'w') as f:
            f.write("""from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal
import logging
import pandas as pd

# Configure logger
logger = logging.getLogger('sharepoint_migration_tool')

class DataFlowFixes:
    \"\"\"
    This class contains methods to be added to MainWindow to fix data flow issues
    \"\"\"
    
    @staticmethod
    def improved_scan_completed(self, scan_data):
        \"\"\"
        Enhanced scan completion handler that ensures data is properly passed to UI components
        
        Args:
            scan_data: The scan results data
        \"\"\"
        logger.info("Scan completed - improved handler")
        
        try:
            # Store scan data for later use
            self.scan_data = scan_data
            
            # Convert to DataFrame if it's not already
            if not isinstance(scan_data, pd.DataFrame):
                # Handle conversion based on data structure
                if hasattr(scan_data, 'items') and callable(getattr(scan_data, 'items')):
                    # It's a dict-like object, extract file info
                    file_list = []
                    
                    # Process file structure (nested file data)
                    if 'file_structure' in scan_data:
                        for dir_path, dir_data in scan_data['file_structure'].items():
                            # Add files
                            if 'files' in dir_data:
                                file_list.extend(dir_data['files'])
                    
                    # Create DataFrame
                    if file_list:
                        # Make a copy to avoid modifying original data
                        self.scan_df = pd.DataFrame(file_list)
                    else:
                        # Empty DataFrame as fallback
                        self.scan_df = pd.DataFrame()
                else:
                    # Create empty DataFrame as fallback
                    self.scan_df = pd.DataFrame()
            else:
                # It's already a DataFrame
                self.scan_df = scan_data
            
            # Update UI
            self._reset_ui_after_operation()
            self.statusBar().showMessage("Scan completed. Analyzing data...")
            
            # Start analysis
            self._analyze_data()
            
        except Exception as e:
            logger.error(f"Error handling scan completion: {e}")
            self._show_error("Error", f"Error processing scan results: {str(e)}")
            self._reset_ui_after_operation()
    
    @staticmethod
    def improved_analysis_completed(self, analysis_results):
        \"\"\"
        Enhanced analysis completion handler that ensures results are 
        properly passed to UI components
        
        Args:
            analysis_results: The analysis results
        \"\"\"
        logger.info("Analysis completed - improved handler")
        
        try:
            # Store analysis results
            self.analysis_results = analysis_results
            
            # Update UI
            self._reset_ui_after_operation()
            self.statusBar().showMessage("Analysis completed")
            
            # Enable buttons that depend on analysis results
            self.export_button.setEnabled(True)
            self.clean_button.setEnabled(True)
            self._update_migration_button()
            
            # Update results displays
            self._update_results_improved()
            
        except Exception as e:
            logger.error(f"Error handling analysis completion: {e}")
            self._show_error("Error", f"Error processing analysis results: {str(e)}")
    
    @staticmethod
    def update_results_improved(self):
        \"\"\"
        Enhanced method to update all UI components with analysis results.
        Properly handles data conversion for each component.
        \"\"\"
        logger.info("Updating UI with results - improved method")
        
        try:
            # Get results
            analysis_results = self.analysis_results
            
            # Make sure we have results
            if not analysis_results:
                logger.warning("No analysis results to display")
                return
            
            # Dashboard needs summary stats
            try:
                if hasattr(self, 'dashboard_tab') and hasattr(self.dashboard_tab, 'update_with_results'):
                    # Call the proper method on the dashboard
                    self.dashboard_tab.update_with_results(analysis_results)
                    logger.info("Dashboard updated successfully")
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
            
            # Analysis view needs structured data
            try:
                if hasattr(self, 'analysis_view') and hasattr(self.analysis_view, 'set_data'):
                    # Get DataFrames for file data and issues
                    files_df = None
                    issues_df = None
                    
                    # Extract file data
                    if 'files_df' in analysis_results:
                        files_df = analysis_results['files_df']
                    elif 'all_files' in analysis_results:
                        files_df = analysis_results['all_files']
                    
                    # Extract issues data
                    if 'issues_df' in analysis_results:
                        issues_df = analysis_results['issues_df']
                    elif 'issues' in analysis_results and isinstance(analysis_results['issues'], list):
                        issues_df = pd.DataFrame(analysis_results['issues'])
                    
                    # Set data on the view
                    if files_df is not None:
                        self.analysis_view.set_data(files_df)
                        logger.info("Analysis view updated successfully")
            except Exception as e:
                logger.error(f"Error updating analysis view: {e}")
            
            # File Analysis tab needs detailed file info
            try:
                if hasattr(self, 'file_analysis_tab') and hasattr(self.file_analysis_tab, 'update_with_results'):
                    # Create a structure expected by FileAnalysisTab
                    file_analysis_data = {
                        'files_df': None,
                        'issues_df': None
                    }
                    
                    # Extract file data
                    if 'files_df' in analysis_results:
                        file_analysis_data['files_df'] = analysis_results['files_df']
                    elif 'all_files' in analysis_results:
                        file_analysis_data['files_df'] = analysis_results['all_files']
                    
                    # Extract issues data
                    if 'issues_df' in analysis_results:
                        file_analysis_data['issues_df'] = analysis_results['issues_df']
                    elif 'issues' in analysis_results and isinstance(analysis_results['issues'], list):
                        file_analysis_data['issues_df'] = pd.DataFrame(analysis_results['issues'])
                    
                    # Update the tab
                    self.file_analysis_tab.update_with_results(file_analysis_data)
                    logger.info("File analysis tab updated successfully")
            except Exception as e:
                logger.error(f"Error updating file analysis tab: {e}")
            
            # Update tab index to show the analysis tab
            self.tabs.setCurrentIndex(1)  # Switch to Analysis tab
            
        except Exception as e:
            logger.error(f"Error updating results: {e}")
            self._show_error("Error", f"Error updating results: {str(e)}")
    
    @staticmethod
    def apply_fixes_to_main_window(main_window):
        \"\"\"
        Apply all fixes to the provided MainWindow instance
        
        Args:
            main_window: The MainWindow instance to modify
        
        Returns:
            bool: True if fixes were applied successfully
        \"\"\"
        try:
            # Replace/add methods
            main_window._scan_completed = lambda scan_data: DataFlowFixes.improved_scan_completed(main_window, scan_data)
            main_window._analysis_completed = lambda analysis_results: DataFlowFixes.improved_analysis_completed(main_window, analysis_results)
            main_window._update_results_improved = lambda: DataFlowFixes.update_results_improved(main_window, )
            
            # Make sure the window has a reference to itself
            main_window.analysis_results = {}
            main_window.scan_data = {}
            main_window.scan_df = pd.DataFrame()
            
            # Override _update_results to use improved version
            main_window._update_results = main_window._update_results_improved
            
            # Log success
            logger.info("Applied data flow fixes to MainWindow")
            return True
            
        except Exception as e:
            logger.error(f"Error applying data flow fixes: {e}")
            return False

# Function to use in main.py
def modify_main_window(main_window):
    \"\"\"
    Modify the main window to fix data flow issues.
    Should be called in main.py right after creating the main window.
    
    Args:
        main_window: The MainWindow instance to modify
        
    Returns:
        bool: True if modifications were successful
    \"\"\"
    return DataFlowFixes.apply_fixes_to_main_window(main_window)
""")
        
        # Create file_analysis_enhancements.py
        file_analysis_enhancements_path = os.path.join(project_dir, 'file_analysis_enhancements.py')
        with open(file_analysis_enhancements_path, 'w') as f:
            f.write("""from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
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
    \"\"\"
    Helper class to implement missing functionality in the FileAnalysisView
    or extend existing functionality.
    \"\"\"
    
    @staticmethod
    def set_data_enhanced(self, files_df, issues_df=None):
        \"\"\"
        Enhanced set_data method to properly display file data
        
        Args:
            files_df (pandas.DataFrame): DataFrame containing file data
            issues_df (pandas.DataFrame): DataFrame containing issue data
        \"\"\"
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
        \"\"\"
        Enhance the FileAnalysisTab to properly handle data updates
        
        Args:
            file_analysis_tab: The FileAnalysisTab instance to enhance
            
        Returns:
            bool: True if enhancements were applied successfully
        \"\"\"
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
                    \"\"\"
                    Update the tab with scan results
                    
                    Args:
                        results (dict): Scan results dictionary
                    \"\"\"
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
        \"\"\"
        Enhance the EnhancedDataView to properly handle data updates
        
        Args:
            enhanced_data_view: The EnhancedDataView instance to enhance
            
        Returns:
            bool: True if enhancements were applied successfully
        \"\"\"
        try:
            # Add update_data method if it doesn't exist
            if not hasattr(enhanced_data_view, 'update_data'):
                def update_data(self, results):
                    \"\"\"
                    Update the view with analysis results
                    
                    Args:
                        results (dict): Analysis results dictionary
                    \"\"\"
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
    \"\"\"
    Apply all view enhancements to the main window components
    
    Args:
        main_window: The MainWindow instance containing the views
        
    Returns:
        bool: True if enhancements were applied successfully
    \"\"\"
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
""")
            
        logger.info("Successfully created fix module files")
        return True
        
    except Exception as e:
        logger.error(f"Error creating fix modules: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python apply_fixes.py [project_directory]")
        return 1
    
    project_dir = sys.argv[1]
    
    if not os.path.isdir(project_dir):
        logger.error(f"Invalid project directory: {project_dir}")
        return 1
    
    # Create fix modules
    if not create_fix_modules(project_dir):
        return 1
    
    # Modify main.py
    if not modify_main_py(project_dir):
        return 1
    
    logger.info("Successfully applied fixes to SharePoint Migration Tool")
    logger.info("Please run the application to see the changes")
    return 0

if __name__ == "__main__":
    sys.exit(main())