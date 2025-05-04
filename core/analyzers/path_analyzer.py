#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Path length analyzer for SharePoint Data Migration Cleanup Tool.
Identifies paths that exceed SharePoint's length limitations.
"""

import os
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger('sharepoint_migration_tool')

class PathAnalyzer:
    """Analyzes path lengths against SharePoint limitations"""
    
    def __init__(self, config=None):
        """
        Initialize the path analyzer
        
        Args:
            config (dict): Configuration settings
        """
        self.config = config or {}
        self.max_path_length = self.config.get('sharepoint', {}).get('max_path_length', 256)
        
    def analyze_dataframe(self, df):
        """
        Analyze a DataFrame of files to identify path length issues
        
        Args:
            df (pandas.DataFrame): DataFrame containing file information
            
        Returns:
            pandas.DataFrame: DataFrame with added columns for path length analysis
        """
        logger.info(f"Analyzing path lengths (max allowed: {self.max_path_length} characters)")
        
        # Create a copy to avoid modifying the original
        result_df = df.copy()
        
        # Ensure path_length column exists
        if 'path_length' not in result_df.columns:
            result_df['path_length'] = result_df['path'].apply(len)
            
        # Add path analysis columns
        result_df['path_too_long'] = result_df['path_length'] > self.max_path_length
        result_df['suggested_path'] = None
        
        # Generate suggested paths for long paths
        for index, row in result_df.iterrows():
            if row['path_too_long']:
                result_df.at[index, 'suggested_path'] = self._suggest_shorter_path(row['path'])
        
        # Summary statistics
        long_paths_count = len(result_df[result_df['path_too_long'] == True])
        total_count = len(result_df)
        logger.info(f"Found {long_paths_count} of {total_count} files with paths exceeding {self.max_path_length} characters")
        
        return result_df
        
    def _suggest_shorter_path(self, original_path):
        """
        Suggest a shorter path that complies with SharePoint's length limitation
        
        Args:
            original_path (str): Original path to shorten
            
        Returns:
            str: Suggested shorter path
        """
        # Basic path shortening strategy:
        # 1. Get the file name and extension
        # 2. Preserve as much of the original path structure as possible
        
        path_obj = Path(original_path)
        file_name = path_obj.name
        
        # Strategy 1: Keep the filename and shorten parent directories
        if len(file_name) < self.max_path_length - 30:  # Allow some room for shortened path
            # Get the drive or root
            drive = os.path.splitdrive(original_path)[0]
            
            # Create a shorter path by abbreviating directories
            parts = path_obj.parts
            
            # Keep the first two directory levels (after drive) and the filename
            if len(parts) > 3:
                shortened_parts = list(parts[:3])  # Drive + first two directory levels
                
                # Add placeholder for skipped directories
                if len(parts) > 4:
                    shortened_parts.append("...")
                    
                # Add the last directory and filename
                shortened_parts.extend(parts[-2:])
                
                # Join the parts
                shortened_path = os.path.join(*shortened_parts)
                
                # Check if it's short enough
                if len(shortened_path) <= self.max_path_length:
                    return shortened_path
            
        # Strategy 2: If still too long, create a more drastically shortened path
        if len(file_name) < self.max_path_length - 10:
            drive = os.path.splitdrive(original_path)[0]
            shortened_path = os.path.join(drive, "ShortenedPath", file_name)
            
            # Check if it's short enough
            if len(shortened_path) <= self.max_path_length:
                return shortened_path
        
        # Strategy 3: If filename itself is very long, truncate it
        name, ext = os.path.splitext(file_name)
        if len(name) > 30:
            shortened_name = name[:27] + "..."
            shortened_file = shortened_name + ext
            
            drive = os.path.splitdrive(original_path)[0]
            shortened_path = os.path.join(drive, "ShortenedPath", shortened_file)
            
            # Check if it's short enough
            if len(shortened_path) <= self.max_path_length:
                return shortened_path
        
        # Final fallback: Create a minimal path if all else fails
        drive = os.path.splitdrive(original_path)[0]
        name, ext = os.path.splitext(file_name)
        name = name[:20] if len(name) > 20 else name  # Ensure name isn't too long
        shortened_path = os.path.join(drive, "SP", name + ext)
        
        return shortened_path
        
    def get_path_stats(self, df):
        """
        Get statistics about path length analysis
        
        Args:
            df (pandas.DataFrame): DataFrame with path length analysis
            
        Returns:
            dict: Statistics about path lengths
        """
        if 'path_too_long' not in df.columns:
            return {
                'total_files': len(df),
                'long_paths': 0,
                'average_length': 0,
                'max_length': 0,
                'long_path_percentage': 0
            }
            
        total_files = len(df)
        long_paths = len(df[df['path_too_long'] == True])
        
        return {
            'total_files': total_files,
            'long_paths': long_paths,
            'average_length': df['path_length'].mean(),
            'max_length': df['path_length'].max(),
            'long_path_percentage': (long_paths / total_files * 100) if total_files > 0 else 0
        }