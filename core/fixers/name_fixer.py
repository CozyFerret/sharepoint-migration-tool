#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Name fixer for SharePoint Data Migration Cleanup Tool.
Fixes illegal characters and reserved names in files and folders.
"""

import os
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger('sharepoint_migration_tool')

class NameFixer:
    """Fixes file and folder names to comply with SharePoint rules"""
    
    def __init__(self, config=None):
        """
        Initialize the name fixer
        
        Args:
            config (dict): Configuration settings
        """
        self.config = config or {}
        
        # Get SharePoint naming rules from config
        self.sharepoint_config = self.config.get('sharepoint', {})
        self.illegal_chars = self.sharepoint_config.get('illegal_chars', 
            ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '#', '%', '&', '{', '}', '+', '~', '='])
            
        self.reserved_names = self.sharepoint_config.get('reserved_names', 
            ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
             "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", 
             "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"])
             
        self.max_name_length = self.sharepoint_config.get('max_name_length', 128)
        
    def fix_name(self, original_name):
        """
        Fix a file or folder name to comply with SharePoint rules
        
        Args:
            original_name (str): Original name to fix
            
        Returns:
            str: Fixed name that complies with SharePoint rules
        """
        if not original_name:
            return "unnamed"
            
        # Remove illegal characters
        fixed_name = original_name
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
        
    def fix_file_path(self, original_path, target_root=None):
        """
        Fix a file path to comply with SharePoint rules
        
        Args:
            original_path (str): Original file path to fix
            target_root (str, optional): Target root directory for the fixed path
            
        Returns:
            str: Fixed file path that complies with SharePoint rules
        """
        original_path_obj = Path(original_path)
        
        # Get the parts of the path
        parts = list(original_path_obj.parts)
        
        # Fix each part of the path
        fixed_parts = []
        for i, part in enumerate(parts):
            # Skip drive letter on Windows
            if i == 0 and len(part) == 2 and part[1] == ':':
                fixed_parts.append(part)
            else:
                fixed_parts.append(self.fix_name(part))
                
        # Create the fixed path
        if target_root:
            # If target root is provided, replace the original root with the target root
            target_path_obj = Path(target_root)
            for part in fixed_parts[1:]:  # Skip the original root
                target_path_obj = target_path_obj / part
            fixed_path = str(target_path_obj)
        else:
            # Otherwise, just join the fixed parts
            fixed_path = str(Path(*fixed_parts))
            
        return fixed_path
        
    def apply_fixes(self, issues_df, target_root=None):
        """
        Apply name fixes to a DataFrame of files with name issues
        
        Args:
            issues_df (pandas.DataFrame): DataFrame with name issues to fix
            target_root (str, optional): Target root directory for fixed paths
            
        Returns:
            pandas.DataFrame: DataFrame with fixed file paths
        """
        if issues_df is None or len(issues_df) == 0:
            logger.info("No name issues to fix")
            return pd.DataFrame()
            
        # Create a copy to avoid modifying the original
        result_df = issues_df.copy()
        
        # Add columns for the fixed path
        if 'fixed_path' not in result_df.columns:
            result_df['fixed_path'] = None
            
        # Apply fixes to each file
        for index, row in result_df.iterrows():
            original_path = row['path']
            
            # If a suggested name is already provided, use it
            if 'suggested_name' in row and row['suggested_name']:
                file_name = row['suggested_name']
                dir_path = os.path.dirname(original_path)
                
                # Create the fixed path
                if target_root:
                    # Convert to relative path from original root
                    try:
                        rel_path = os.path.relpath(dir_path, os.path.dirname(dir_path))
                        fixed_dir = os.path.join(target_root, rel_path)
                    except:
                        # Fallback: put the file directly in the target root
                        fixed_dir = target_root
                else:
                    fixed_dir = dir_path
                    
                fixed_path = os.path.join(fixed_dir, file_name)
                
            else:
                # Otherwise, apply fixes to the entire path
                fixed_path = self.fix_file_path(original_path, target_root)
                
            result_df.at[index, 'fixed_path'] = fixed_path
            
        logger.info(f"Fixed {len(result_df)} file names")
        return result_df
        
    def preview_fixes(self, issues_df):
        """
        Generate a preview of name fixes without applying them
        
        Args:
            issues_df (pandas.DataFrame): DataFrame with name issues to fix
            
        Returns:
            pandas.DataFrame: DataFrame with original and fixed names
        """
        # Create a preview DataFrame
        preview_df = pd.DataFrame(columns=['original_path', 'fixed_name', 'fixed_path'])
        
        if issues_df is None or len(issues_df) == 0:
            return preview_df
            
        # Generate preview for each file
        for index, row in issues_df.iterrows():
            original_path = row['path']
            original_name = row['name'] if 'name' in row else os.path.basename(original_path)
            
            # Get fixed name
            if 'suggested_name' in row and row['suggested_name']:
                fixed_name = row['suggested_name']
            else:
                fixed_name = self.fix_name(original_name)
                
            # Get fixed path (in place, without a target root)
            fixed_path = self.fix_file_path(original_path)
            
            # Add to preview
            preview_df = preview_df.append({
                'original_path': original_path,
                'fixed_name': fixed_name,
                'fixed_path': fixed_path
            }, ignore_index=True)
            
        return preview_df