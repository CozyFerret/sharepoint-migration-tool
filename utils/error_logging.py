"""
Error logging utility for SharePoint Migration Tool
Ensures all errors are properly logged to file
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path

def setup_error_logging():
    """
    Set up error logging to ensure all crashes are captured
    
    Returns:
        str: Path to the log file
    """
    # Create logs directory in user's home folder
    log_dir = Path.home() / ".sharepoint_migration_tool" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    log_file = log_dir / f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Add global exception handler
    sys.excepthook = global_exception_handler
    
    logging.info(f"Error logging configured. Log file: {log_file}")
    return str(log_file)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to catch and log unhandled exceptions
    """
    # Skip KeyboardInterrupt exceptions
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    # Log the exception
    logger = logging.getLogger("error_logger")
    logger.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Format the traceback as a string
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)
    
    # Log the full traceback
    logger.critical(f"Traceback:\n{tb_text}")
    
    # Print to stderr as well
    print(f"Critical error: {exc_value}", file=sys.stderr)
    print(f"See log file for details.", file=sys.stderr)