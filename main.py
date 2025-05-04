#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SharePoint Data Migration Cleanup Tool
A utility for cleaning and preparing file systems for SharePoint migration.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.config import load_config
from utils.secure_logging import setup_logging
from utils.memory_cleanup import cleanup_on_exit
from core.data_processor import DataProcessor

def main():
    """Main entry point for the application"""
    # Setup secure logging
    logger = setup_logging()
    logger.info("Starting SharePoint Data Migration Cleanup Tool")
    
    # Load configuration
    config = load_config()
    
    # Initialize data processor
    data_processor = DataProcessor(config)
    
    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("SharePoint Data Migration Cleanup Tool")
    
    # Create and show the main window
    window = MainWindow(config, data_processor)
    window.show()
    
    # Run the application
    exit_code = app.exec_()
    
    # Clean up resources on exit
    cleanup_on_exit()
    logger.info("Application shutting down")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())