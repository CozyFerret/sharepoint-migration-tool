#!/usr/bin/env python
"""
SharePoint Migration Tool - Main Application

A Python tool for cleaning and preparing file systems for SharePoint migration.
"""

import sys
import os

# Set up error logging first, before any other imports
from utils.error_logging import setup_error_logging
log_file = setup_error_logging()

# Now import other modules
import logging
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

# Import the main window class
from ui.main_window import MainWindow

logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    # Log application start
    logger.info("Application started")
    
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("SharePoint Migration Tool")
        app.setOrganizationName("CozyFerret")
        
        # Set application stylesheet if available
        style_path = os.path.join(os.path.dirname(__file__), "resources", "styles", "app_style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as style_file:
                app.setStyleSheet(style_file.read())
        
        # Create and show main window
        main_window = MainWindow()
        logger.info("Main window created successfully")
        main_window.show()
        
        # Start the application event loop
        exit_code = app.exec_()
        
        # Clean up and exit
        logger.info(f"Application exited with code {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        # Log the error
        logger.critical(f"Critical error during startup: {e}", exc_info=True)
        
        # Show error message to user
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Critical)
        error_message.setWindowTitle("Application Error")
        error_message.setText("A critical error occurred during startup.")
        error_message.setInformativeText(f"Error: {str(e)}")
        error_message.setDetailedText(f"Please check the log file for details:\n{log_file}")
        error_message.exec_()
        
        sys.exit(1)

if __name__ == "__main__":
    main()