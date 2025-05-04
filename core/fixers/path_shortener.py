#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Path shortener for SharePoint Data Migration Cleanup Tool.
Shortens paths that exceed SharePoint's path length limitations.
"""

import os
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger('sharepoint_migration_tool')

class PathShortener:
    """Shortens paths that exceed SharePoint's length limitations"""
    
    def __init__(self, config=None):
        """
        Initialize the path shortener
        
        Args:
            config (dict): Configuration settings
        """
        self.config = config or {}
        
        # Get SharePoint path limits from config
        self.sharepoint_config = self.config.get('sharepoint', {})
        self.max_path_length = self.sharepoint_config.get('max_path_length', 256)
        
        # Configure shortening strategies
        self.strategies = [
            self._strategy_abbreviate_dirs,
            self._strategy_remove_middle_dirs,
            self._strategy_truncate_names,
            self._strategy_minimal_path
        ]
        
    def shorten_path(self, original_path, target_root=None):
        """
        Shorten a path to comply with SharePoint's length limitation
        
        Args:
            original_path (str): Original path to shorten
            target_root (str, optional): Target root directory for the shortened path
            
        Returns:
            str: Shortened path that complies with SharePoint's length limitation
        """
        # If path is already short enough, return it as is
        if len(original_path) <= self.max_path_length:
            if target_root:
                # Convert to target root
                try:
                    rel_path = os.path.relpath(original_path, os.path.dirname(os.path.dirname(original_path)))
                    return os.path.join(target_root, rel_path)
                except:
                    # Fallback: just use the filename in the target root
                    return os.path.join(target_root, os.path.basename(original_path))
            else:
                return original_path
                
        # Try each strategy in order until one works
        for strategy in self.strategies:
            shortened_path = strategy(original_path, target_root)
            if len(shortened_path) <= self.max_path_length:
                return shortened_path
                
        # If all strategies fail, return a minimal path
        file_name = os.path.basename(original_path)
        if target_root:
            return os.path.join(target_root, file_name)
        else:
            drive = os.path.splitdrive(original_path)[0]
            return os.path.join(drive + os.sep if drive else "", file_name)
            
    def _strategy_abbreviate_dirs(self, original_path, target_root=None):
        """
        Strategy 1: Abbreviate directory names while preserving structure
        
        Args:
            original_path (str): Original path to shorten
            target_root (str, optional): Target root directory
            
        Returns:
            str: Shortened path with abbreviated directory names
        """
        path_obj = Path(original_path)
        file_name = path_obj.name
        
        # Preserve the drive or root
        drive = os.path.splitdrive(original_path)[0]
        
        # Get the directory parts (excluding drive and filename)
        if drive:
            # Windows-style path with drive letter
            parts = list(path_obj.parts)[1:-1]  # Exclude drive and filename
        else:
            # Unix-style path
            parts = list(path_obj.parts)[1:-1] if path_obj.parts[0] == '/' else list(path_obj.parts)[:-1]
            
        # Abbreviate directory names
        abbreviated_parts = []
        for part in parts:
            # Skip empty parts
            if not part:
                continue
                
            # Abbreviate long directory names (keep first 3 and last 3 characters)
            if len(part) > 8:
                abbreviated_parts.append(f"{part[:3]}~{part[-3:]}")
            else:
                abbreviated_parts.append(part)
                
        # Build the shortened path
        if target_root:
            # Use target root
            result_path = os.path.join(target_root, *abbreviated_parts, file_name)
        elif drive:
            # Windows-style path with drive letter
            result_path = os.path.join(drive + os.sep, *abbreviated_parts, file_name)
        elif path_obj.is_absolute():
            # Unix-style absolute path
            result_path = os.path.join(os.sep, *abbreviated_parts, file_name)
        else:
            # Relative path
            result_path = os.path.join(*abbreviated_parts, file_name)
            
        return result_path
        
    def _strategy_remove_middle_dirs(self, original_path, target_root=None):
        """
        Strategy 2: Remove middle directories while preserving key parts
        
        Args:
            original_path (str): Original path to shorten
            target_root (str, optional): Target root directory
            
        Returns:
            str: Shortened path with middle directories removed
        """
        path_obj = Path(original_path)
        file_name = path_obj.name
        
        # Preserve the drive or root
        drive = os.path.splitdrive(original_path)[0]
        
        # Get the directory parts (excluding drive and filename)
        if drive:
            # Windows-style path with drive letter
            parts = list(path_obj.parts)[1:-1]  # Exclude drive and filename
        else:
            # Unix-style path
            parts = list(path_obj.parts)[1:-1] if path_obj.parts[0] == '/' else list(path_obj.parts)[:-1]
            
        # Keep first and last directories, remove middle ones if there are more than 3 directories
        if len(parts) > 3:
            parts = [parts[0], "...", parts[-1]]
            
        # Build the shortened path
        if target_root:
            # Use target root
            result_path = os.path.join(target_root, *parts, file_name)
        elif drive:
            # Windows-style path with drive letter
            result_path = os.path.join(drive + os.sep, *parts, file_name)
        elif path_obj.is_absolute():
            # Unix-style absolute path
            result_path = os.path.join(os.sep, *parts, file_name)
        else:
            # Relative path
            result_path = os.path.join(*parts, file_name)
            
        return result_path
        
    def _strategy_truncate_names(self, original_path, target_root=None):
        """
        Strategy 3: Truncate all names to a maximum length
        
        Args:
            original_path (str): Original path to shorten
            target_root (str, optional): Target root directory
            
        Returns:
            str: Shortened path with truncated names
        """
        path_obj = Path(original_path)
        
        # Split into name and extension
        file_name = path_obj.name
        name, ext = os.path.splitext(file_name)
        
        # Truncate the filename if it's very long
        if len(name) > 30:
            file_name = f"{name[:27]}...{ext}"
            
        # Preserve the drive or root
        drive = os.path.splitdrive(original_path)[0]
        
        # Get the directory parts (excluding drive and filename)
        if drive:
            # Windows-style path with drive letter
            parts = list(path_obj.parts)[1:-1]  # Exclude drive and filename
        else:
            # Unix-style path
            parts = list(path_obj.parts)[1:-1] if path_obj.parts[0] == '/' else list(path_obj.parts)[:-1]
            
        # Truncate directory names (max 10 characters)
        truncated_parts = []
        for part in parts:
            # Skip empty parts
            if not part:
                continue
                
            # Truncate long directory names
            if len(part) > 10:
                truncated_parts.append(f"{part[:7]}...")
            else:
                truncated_parts.append(part)
                
        # Build the shortened path
        if target_root:
            # Use target root
            result_path = os.path.join(target_root, *truncated_parts, file_name)
        elif drive:
            # Windows-style path with drive letter
            result_path = os.path.join(drive + os.sep, *truncated_parts, file_name)
        elif path_obj.is_absolute():
            # Unix-style absolute path
            result_path = os.path.join(os.sep, *truncated_parts, file_name)
        else:
            # Relative path
            result_path = os.path.join(*truncated_parts, file_name)
            
        return result_path
        
    def _strategy_minimal_path(self, original_path, target_root=None):
        """
        Strategy 4: Create a minimal path with just the necessary components
        
        Args:
            original_path (str): Original path to shorten
            target_root (str, optional): Target root directory
            
        Returns:
            str: Minimal path with just the filename
        """
        # Get just the filename
        file_name = os.path.basename(original_path)
        
        # Preserve the drive or root
        drive = os.path.splitdrive(original_path)[0]
        
        # Create a minimal path
        if target_root:
            # Use target root
            result_path = os.path.join(target_root, "ShortPath", file_name)
        elif drive:
            # Windows-style path with drive letter
            result_path = os.path.join(drive + os.sep, "ShortPath", file_name)
        else:
            # Unix-style path
            result_path = os.path.join("ShortPath", file_name)
            
        return result_path
        
    def apply_fixes(self, issues_df, target_root=None):
        """
        Apply path shortening to a DataFrame of files with path issues
        
        Args:
            issues_df (pandas.DataFrame): DataFrame with path issues to fix
            target_root (str, optional): Target root directory for shortened paths
            
        Returns:
            pandas.DataFrame: DataFrame with shortened file paths
        """
        if issues_df is None or len(issues_df) == 0:
            logger.info("No path issues to fix")
            return pd.DataFrame()
            
        # Create a copy to avoid modifying the original
        result_df = issues_df.copy()
        
        # Add columns for the shortened path
        if 'shortened_path' not in result_df.columns:
            result_df['shortened_path'] = None
            
        # Apply fixes to each file
        for index, row in result_df.iterrows():
            original_path = row['path']
            
            # If a suggested path is already provided, use it
            if 'suggested_path' in row and row['suggested_path']:
                shortened_path = row['suggested_path']
                
                # If target_root is provided, adjust the path
                if target_root:
                    # Extract just the filename if we can't determine the relative path
                    file_name = os.path.basename(shortened_path)
                    shortened_path = os.path.join(target_root, file_name)
            else:
                # Otherwise, apply shortening strategy
                shortened_path = self.shorten_path(original_path, target_root)
                
            result_df.at[index, 'shortened_path'] = shortened_path
            
        logger.info(f"Shortened {len(result_df)} file paths")
        return result_df
        
    def preview_fixes(self, issues_df):
        """
        Generate a preview of path shortening without applying it
        
        Args:
            issues_df (pandas.DataFrame): DataFrame with path issues to fix
            
        Returns:
            pandas.DataFrame: DataFrame with original and shortened paths
        """
        # Create a preview DataFrame
        preview_df = pd.DataFrame(columns=['original_path', 'original_length', 'shortened_path', 'shortened_length'])
        
        if issues_df is None or len(issues_df) == 0:
            return preview_df
            
        # Generate preview for each file
        for index, row in issues_df.iterrows():
            original_path = row['path']
            original_length = len(original_path)
            
            # Get shortened path
            if 'suggested_path' in row and row['suggested_path']:
                shortened_path = row['suggested_path']
            else:
                shortened_path = self.shorten_path(original_path)
                
            shortened_length = len(shortened_path)
            
            # Add to preview
            preview_df = preview_df.append({
                'original_path': original_path,
                'original_length': original_length,
                'shortened_path': shortened_path,
                'shortened_length': shortened_length
            }, ignore_index=True)
            
        return preview_df