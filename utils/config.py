#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration loader for the SharePoint Data Migration Cleanup Tool.
Handles runtime configuration with no permanent storage.
"""

import os
import json
from pathlib import Path

# Default configuration settings
DEFAULT_CONFIG = {
    "features": {
        "name_validation": True,
        "path_length": True,
        "duplicate_detection": True,
        "pii_detection": True
    },
    "sharepoint": {
        "max_path_length": 256,
        "illegal_chars": ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '#', '%', '&', '{', '}', '+', 
                          '~', '='],
        "reserved_names": ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
                           "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", 
                           "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
    },
    "pii_detection": {
        "sensitivity": "medium",  # low, medium, high
        "scan_file_content": True,
        "detect_types": ["SSN", "CREDIT_CARD", "EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "ADDRESS"]
    },
    "ui": {
        "theme": "light",
        "max_results_per_page": 100
    }
}

def load_config():
    """
    Load configuration - in a real app, this might look for a config file, 
    but for our non-persistent approach, we just use defaults or environment vars
    """
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables if present
    if os.environ.get("SP_FEATURE_NAME_VALIDATION"):
        config["features"]["name_validation"] = os.environ.get("SP_FEATURE_NAME_VALIDATION").lower() == "true"
    
    if os.environ.get("SP_FEATURE_PATH_LENGTH"):
        config["features"]["path_length"] = os.environ.get("SP_FEATURE_PATH_LENGTH").lower() == "true"
    
    if os.environ.get("SP_FEATURE_DUPLICATE_DETECTION"):
        config["features"]["duplicate_detection"] = os.environ.get("SP_FEATURE_DUPLICATE_DETECTION").lower() == "true"
    
    if os.environ.get("SP_FEATURE_PII_DETECTION"):
        config["features"]["pii_detection"] = os.environ.get("SP_FEATURE_PII_DETECTION").lower() == "true"
    
    # More environment variable overrides could be added here
    
    return config

def save_runtime_config(config):
    """
    Save configuration for the current session only.
    This doesn't persist between runs - just keeps current settings in memory.
    
    Args:
        config (dict): The configuration dictionary to save
    """
    # In a non-persistent app, we would just keep this in memory
    # This function is a placeholder for updating runtime configuration
    return config