from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal
import logging
import pandas as pd

# Configure logger
logger = logging.getLogger('sharepoint_migration_tool')

class DataFlowFixes:
    """
    This class contains methods to be added to MainWindow to fix data flow issues
    """
    
    @staticmethod
    def improved_scan_completed(self, scan_data):
        """
        Enhanced scan completion handler that ensures data is properly passed to UI components
        
        Args:
            scan_data: The scan results data
        """
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
        """
        Enhanced analysis completion handler that ensures results are 
        properly passed to UI components
        
        Args:
            analysis_results: The analysis results
        """
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
        """
        Enhanced method to update all UI components with analysis results.
        Properly handles data conversion for each component.
        """
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
        """
        Apply all fixes to the provided MainWindow instance
        
        Args:
            main_window: The MainWindow instance to modify
        
        Returns:
            bool: True if fixes were applied successfully
        """
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
    """
    Modify the main window to fix data flow issues.
    Should be called in main.py right after creating the main window.
    
    Args:
        main_window: The MainWindow instance to modify
        
    Returns:
        bool: True if modifications were successful
    """
    return DataFlowFixes.apply_fixes_to_main_window(main_window)