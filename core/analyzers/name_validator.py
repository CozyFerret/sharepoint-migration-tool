#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SharePoint naming rules validator for the SharePoint Data Migration Cleanup Tool.
Validates file and folder names against SharePoint's naming restrictions.
"""

import re
import os
import logging
import pandas as pd

logger = logging.getLogger('sharepoint_migration_tool')

class SharePointNameValidator:
    """Validates file and folder names against SharePoint naming rules"""
    
    def __init__(self, config=None):
        """
        Initialize the validator with SharePoint naming rules
        
        Args:
            config (dict): Configuration containing SharePoint naming rules
        """
        self.config = config or {}
        
        # Default SharePoint illegal characters if not provided in config
        self.illegal_chars = self.config.get('sharepoint', {}).get('illegal_chars', 
            ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '#', '%', '&', '{', '}', '+', '~', '='])
            
        # Default SharePoint reserved names if not provided in config
        self.reserved_names = self.config.get('sharepoint', {}).get('reserved_names', 
            ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
             "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", 
             "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"])
             
        # Additional SharePoint restrictions
        self.max_name_length = 128  # Maximum file name length
        self.leading_trailing_spaces = False  # Leading/trailing spaces not allowed
        self.leading_trailing_dots = False  # Leading/trailing dots not allowed
        
        # Compile regex patterns for performance
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile regex patterns for validation checks"""
        # Pattern for illegal characters
        escaped_chars = [re.escape(char) for char in self.illegal_chars]
        self.illegal_chars_pattern = re.compile(f"[{''.join(escaped_chars)}]")
        
        # Pattern for leading/trailing spaces
        self.leading_trailing_spaces_pattern = re.compile(r"(^\s+|\s+$)")
        
        # Pattern for leading/trailing dots
        self.leading_trailing_dots_pattern = re.compile(r"(^\.+|\.+$)")
        
    def validate_name(self, name):
        """
        Validate a single file or folder name against SharePoint rules
        
        Args:
            name (str): The file or folder name to validate
            
        Returns:
            tuple: (is_valid, issues)
                is_valid (bool): True if the name is valid
                issues (list): List of issues found
        """
        issues = []
        
        # Check if name is None or empty
        if not name:
            issues.append("Name is empty")
            return False, issues
            
        # Check name length
        if len(name) > self.max_name_length:
            issues.append(f"Name exceeds maximum length of {self.max_name_length} characters")
            
        # Check for reserved names
        name_without_ext = os.path.splitext(name)[0].upper()
        if name_without_ext in self.reserved_names:
            issues.append(f"'{name_without_ext}' is a reserved name in Windows/SharePoint")
            
        # Check for illegal characters
        illegal_chars_match = self.illegal_chars_pattern.search(name)
        if illegal_chars_match:
            char = illegal_chars_match.group(0)
            issues.append(f"Contains illegal character: '{char}'")
            
        # Check for leading/trailing spaces
        if not self.leading_trailing_spaces:
            if self.leading_trailing_spaces_pattern.search(name):
                issues.append("Contains leading or trailing spaces")
                
        # Check for leading/trailing dots
        if not self.leading_trailing_dots:
            if self.leading_trailing_dots_pattern.search(name):
                issues.append("Contains leading or trailing dots")
                
        return len(issues) == 0, issues
        
    def suggest_fixed_name(self, name):
        """
        Suggest a fixed name that complies with SharePoint rules
        
        Args:
            name (str): The original name to fix
            
        Returns:
            str: A suggested fixed name
        """
        if not name:
            return "unnamed"
            
        # Remove illegal characters
        fixed_name = name
        for char in self.illegal_chars:
            fixed_name = fixed_name.replace(char, "_")
            
        # Remove leading/trailing spaces
        fixed_name = fixed_name.strip()
        
        # Remove leading/trailing dots
        fixed_name = fixed_name.strip('.')
        
        # Check if it's a reserved name
        name_without_ext, ext = os.path.splitext(fixed_name)
        if name_without_ext.upper() in self.reserved_names:
            name_without_ext = f"{name_without_ext}_SP"
            fixed_name = f"{name_without_ext}{ext}"
            
        # Truncate if too long
        if len(fixed_name) > self.max_name_length:
            # Keep the extension if present
            if ext:
                # Leave room for the extension
                max_base_length = self.max_name_length - len(ext)
                fixed_name = f"{name_without_ext[:max_base_length]}{ext}"
            else:
                fixed_name = fixed_name[:self.max_name_length]
                
        # If name became empty after fixes, provide a default
        if not fixed_name:
            fixed_name = "unnamed"
            
        return fixed_name
        
    def analyze_dataframe(self, df):
        """
        Analyze a DataFrame of files and identify naming issues
        
        Args:
            df (pandas.DataFrame): DataFrame containing file information
            
        Returns:
            pandas.DataFrame: DataFrame with added columns for naming validation
        """
        logger.info("Analyzing file names for SharePoint compatibility")
        
        # Create a copy to avoid modifying the original
        result_df = df.copy()
        
        # Initialize new columns
        result_df['name_valid'] = True
        result_df['name_issues'] = None
        result_df['suggested_name'] = None
        
        # Validate each file name
        for index, row in result_df.iterrows():
            name = row['name']
            is_valid, issues = self.validate_name(name)
            
            result_df.at[index, 'name_valid'] = is_valid
            
            if not is_valid:
                # Store issues as a semicolon-separated string
                result_df.at[index, 'name_issues'] = '; '.join(issues)
                # Suggest a fixed name
                result_df.at[index, 'suggested_name'] = self.suggest_fixed_name(name)
        
        # Summary statistics
        invalid_count = len(result_df[result_df['name_valid'] == False])
        total_count = len(result_df)
        logger.info(f"Found {invalid_count} of {total_count} files with invalid names")
        
        return result_df