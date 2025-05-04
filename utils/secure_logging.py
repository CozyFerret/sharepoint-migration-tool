#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Secure logging utility for the SharePoint Data Migration Cleanup Tool.
Implements privacy-preserving logging with no persistent storage.
"""

import logging
import sys
import re
from io import StringIO

class PIIFilter(logging.Filter):
    """Filter to remove PII from log messages"""
    
    def __init__(self):
        super().__init__()
        # Patterns for common PII
        self.patterns = [
            # SSN
            (r'\b\d{3}[-\.\s]?\d{2}[-\.\s]?\d{4}\b', '[SSN REDACTED]'),
            # Credit card number
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CC REDACTED]'),
            # Email
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REDACTED]'),
            # Phone number (simplified)
            (r'\b\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}\b', '[PHONE REDACTED]'),
        ]
    
    def filter(self, record):
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern, replacement in self.patterns:
                msg = re.sub(pattern, replacement, msg)
            record.msg = msg
        return True

class MemoryLogHandler(logging.Handler):
    """A log handler that keeps logs in memory only"""
    
    def __init__(self, capacity=1000):
        """
        Initialize the handler with a buffer
        
        Args:
            capacity (int): Maximum number of log entries to keep
        """
        super().__init__()
        self.capacity = capacity
        self.buffer = []
        
    def emit(self, record):
        """Add the log record to the buffer"""
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)  # Remove the oldest log entry
        self.buffer.append(self.format(record))
    
    def get_logs(self):
        """Return all logs as a list"""
        return self.buffer
    
    def export_logs(self):
        """Export logs to a string"""
        return '\n'.join(self.buffer)
    
    def clear(self):
        """Clear all logs"""
        self.buffer = []

def setup_logging():
    """
    Set up the logging configuration for the application
    
    Returns:
        logging.Logger: The configured logger
    """
    logger = logging.getLogger('sharepoint_migration_tool')
    logger.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a memory handler for the application
    memory_handler = MemoryLogHandler()
    memory_handler.setFormatter(formatter)
    
    # Create a console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Add the PII filter to both handlers
    pii_filter = PIIFilter()
    memory_handler.addFilter(pii_filter)
    console_handler.addFilter(pii_filter)
    
    # Add the handlers to the logger
    logger.addHandler(memory_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_memory_handler():
    """
    Get the memory log handler for exporting logs
    
    Returns:
        MemoryLogHandler: The memory log handler
    """
    logger = logging.getLogger('sharepoint_migration_tool')
    for handler in logger.handlers:
        if isinstance(handler, MemoryLogHandler):
            return handler
    return None

def export_logs():
    """
    Export logs as a string
    
    Returns:
        str: The logs as a formatted string
    """
    handler = get_memory_handler()
    if handler:
        return handler.export_logs()
    return "No logs available"

def clear_logs():
    """Clear all logs from memory"""
    handler = get_memory_handler()
    if handler:
        handler.clear()