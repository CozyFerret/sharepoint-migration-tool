#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for SharePoint Data Migration Cleanup Tool.
"""

import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox

def main():
    """Main entry point"""
    try:
        app = QApplication(sys.argv)
        
        # Set app style
        app.setStyle("Fusion")
        
        # Try to import and create the main window
        from ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        
        # Run application
        return app.exec_()
    except Exception as e:
        # Show the error in a message box
        error_message = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        print(error_message)
        
        if QApplication.instance():
            QMessageBox.critical(None, "Application Error", error_message)
        
        return 1

if __name__ == "__main__":
    sys.exit(main())