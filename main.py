#!/usr/bin/env python
"""
SharePoint Migration Tool - Main Application

A Python tool for cleaning and preparing file systems for SharePoint migration.
This tool helps identify and fix common issues encountered during SharePoint migrations,
ensuring a smooth transition to SharePoint Online or on-premises environments.

Features:
- Non-Destructive Operation: All changes are made to copies of original files
- In-Memory Processing: No permanent data storage for enhanced security
- Comprehensive Analysis:
  - SharePoint Naming Compliance: Detects and fixes illegal characters
  - Path Length Reduction: Identifies paths exceeding SharePoint's 256 character limit
  - Duplicate File Detection: Finds exact and similar duplicates
  - Detailed File Analysis: Examines individual files for SharePoint compatibility
- Flexible Cleanup Options:
  - Manual Mode: Non-destructively copies cleaned data to a new folder
  - Automatic Mode: Cleans data and uploads directly to SharePoint
- Visual Analysis: Dashboard with insights about your file structure
- Export Capabilities: Generate detailed reports in various formats
"""

import sys
import os
import logging
import traceback
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

# Set up logging
def setup_logging():
    """Configure logging for the application"""
    try:
        log_dir = Path.home() / ".sharepoint_migration_tool" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"migration_tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return log_file
    except Exception as e:
        print(f"Error setting up logging: {e}")
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return None

def show_error_dialog(title, message, details=None):
    """Show error dialog with optional details"""
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setWindowTitle(title)
    error_dialog.setText(message)
    if details:
        error_dialog.setDetailedText(details)
    error_dialog.setStandardButtons(QMessageBox.Ok)
    error_dialog.exec_()

def main():
    """Main application entry point"""
    # Set up logging
    log_file = setup_logging()
    logging.info("Application started")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("SharePoint Migration Tool")
    app.setOrganizationName("CozyFerret")
    
    try:
        # Set application stylesheet if available
        style_path = os.path.join(os.path.dirname(__file__), "resources", "styles", "app_style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as style_file:
                app.setStyleSheet(style_file.read())
        
        # Ensure resource directories exist
        resources_dir = os.path.join(os.path.dirname(__file__), "resources")
        os.makedirs(os.path.join(resources_dir, "icons"), exist_ok=True)
        os.makedirs(os.path.join(resources_dir, "styles"), exist_ok=True)
        
        # Try to import the main window with error handling
        try:
            # Import the main window class
            from ui.main_window import MainWindow
            logging.info("MainWindow class imported successfully")
            
            # Create and show main window
            main_window = MainWindow()
            logging.info("Main window created successfully")
            main_window.show()
            
            # Start the application event loop
            exit_code = app.exec_()
            
            # Clean up and exit
            logging.info(f"Application exited with code {exit_code}")
            return exit_code
            
        except ImportError as e:
            logging.critical(f"Could not import MainWindow: {e}")
            show_error_dialog(
                "Import Error", 
                "Could not import the main application window.",
                f"Error details:\n{str(e)}\n\nThis may be caused by missing dependencies or installation issues."
            )
            return 1
        except Exception as e:
            logging.critical(f"Error creating main window: {e}")
            show_error_dialog(
                "Initialization Error", 
                "Could not initialize the application.",
                f"Error details:\n{str(e)}"
            )
            return 1
            
    except Exception as e:
        # Get full traceback
        exc_info = traceback.format_exc()
        logging.critical(f"Critical application error: {e}\n{exc_info}")
        
        # Show error dialog if possible
        try:
            show_error_dialog(
                "Critical Error", 
                "A critical error occurred during application startup.",
                f"Error details:\n{str(e)}\n\n{exc_info}"
            )
        except:
            # Last resort: print to console
            print(f"CRITICAL ERROR: {e}")
            print(exc_info)
        
        return 1

if __name__ == "__main__":
    sys.exit(main())