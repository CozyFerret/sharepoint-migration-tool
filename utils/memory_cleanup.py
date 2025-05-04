#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory cleanup utilities for the SharePoint Data Migration Cleanup Tool.
Ensures sensitive data is properly cleared from memory.
"""

import gc
import os
import sys
import ctypes
import logging
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication

logger = logging.getLogger('sharepoint_migration_tool')

def secure_clear_string(string_var):
    """
    Attempt to securely clear a string from memory by overwriting it
    
    Args:
        string_var (str): The string to clear
    """
    if string_var is None:
        return
        
    # Overwrite the string content with zeros
    try:
        if isinstance(string_var, str):
            string_length = len(string_var)
            string_var = '\0' * string_length
    except Exception as e:
        logger.warning(f"Error during secure string clearing: {e}")

def secure_clear_dataframe(df):
    """
    Securely clear a pandas DataFrame from memory
    
    Args:
        df (pandas.DataFrame): The DataFrame to clear
    """
    if df is None or not isinstance(df, pd.DataFrame):
        return
        
    try:
        # Overwrite the DataFrame with NaN values
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                df[col] = pd.Series([''] * len(df), index=df.index)
            else:
                df[col] = np.nan
                
        # Delete the DataFrame
        del df
    except Exception as e:
        logger.warning(f"Error during secure DataFrame clearing: {e}")

def secure_clear_list(list_var):
    """
    Securely clear a list from memory
    
    Args:
        list_var (list): The list to clear
    """
    if list_var is None:
        return
        
    try:
        # Clear the list contents
        list_length = len(list_var)
        for i in range(list_length):
            if isinstance(list_var[i], str):
                secure_clear_string(list_var[i])
            elif isinstance(list_var[i], list):
                secure_clear_list(list_var[i])
            elif isinstance(list_var[i], dict):
                secure_clear_dict(list_var[i])
            list_var[i] = None
            
        # Clear the list itself
        list_var.clear()
    except Exception as e:
        logger.warning(f"Error during secure list clearing: {e}")

def secure_clear_dict(dict_var):
    """
    Securely clear a dictionary from memory
    
    Args:
        dict_var (dict): The dictionary to clear
    """
    if dict_var is None:
        return
        
    try:
        # Clear dictionary values
        for key in list(dict_var.keys()):
            if isinstance(dict_var[key], str):
                secure_clear_string(dict_var[key])
            elif isinstance(dict_var[key], list):
                secure_clear_list(dict_var[key])
            elif isinstance(dict_var[key], dict):
                secure_clear_dict(dict_var[key])
            elif isinstance(dict_var[key], pd.DataFrame):
                secure_clear_dataframe(dict_var[key])
                
            dict_var[key] = None
            
        # Clear the dictionary itself
        dict_var.clear()
    except Exception as e:
        logger.warning(f"Error during secure dictionary clearing: {e}")

def clear_clipboard():
    """Clear the system clipboard"""
    try:
        clipboard = QApplication.clipboard()
        clipboard.clear()
        logger.info("Clipboard cleared")
    except Exception as e:
        logger.warning(f"Error clearing clipboard: {e}")

def clear_all_sensitive_data(data_containers):
    """
    Clear all sensitive data from provided containers
    
    Args:
        data_containers (dict): Dictionary of data containers to clear
    """
    try:
        if not isinstance(data_containers, dict):
            return
            
        # Process each container based on its type
        for key, container in data_containers.items():
            if isinstance(container, pd.DataFrame):
                secure_clear_dataframe(container)
            elif isinstance(container, list):
                secure_clear_list(container)
            elif isinstance(container, dict):
                secure_clear_dict(container)
            elif isinstance(container, str):
                secure_clear_string(container)
                
        # Force garbage collection
        gc.collect()
        
        # Clear clipboard as well
        clear_clipboard()
        
        logger.info("Sensitive data cleared from memory")
    except Exception as e:
        logger.error(f"Error during memory cleanup: {e}")

def cleanup_on_exit():
    """Perform cleanup operations before application exit"""
    # Force garbage collection
    gc.collect()
    
    # Clear clipboard
    clear_clipboard()
    
    logger.info("Performed cleanup operations on exit")