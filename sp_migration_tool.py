#!/usr/bin/env python3
"""
SharePoint Migration Tool - Enhanced Edition

A Python-based desktop application for cleaning and preparing file systems for 
SharePoint migration with options for destructive/non-destructive operations
and direct SharePoint upload.

Run this script to launch the application.
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings

# Import the main window class
from ui.main_window_updated import MainWindow

# Set up logging
def setup_logging():
    """Configure logging for the application"""
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

def main():
    """Main application entry point"""
    # Set up logging
    log_file = setup_logging()
    logging.info("Application started")
    
    # Configure application settings
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setOrganizationName("SharePoint Migration Tool")
    QSettings.setApplicationName("SP Migration")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("SharePoint Migration Tool")
    
    # Set application stylesheet if available
    style_path = os.path.join(os.path.dirname(__file__), "resources", "styles", "app_style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as style_file:
            app.setStyleSheet(style_file.read())
    
    # Ensure resource directories exist
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")
    os.makedirs(os.path.join(resources_dir, "icons"), exist_ok=True)
    os.makedirs(os.path.join(resources_dir, "styles"), exist_ok=True)
    
    # Create and show main window
    main_window = MainWindow()
    logging.info("Main window created successfully")
    main_window.show()
    
    # Start the application event loop
    exit_code = app.exec_()
    
    # Clean up and exit
    logging.info(f"Application exited with code {exit_code}")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())