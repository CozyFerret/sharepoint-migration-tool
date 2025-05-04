#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Duplicate file finder for SharePoint Data Migration Cleanup Tool.
Identifies duplicate files based on content hash or name.
"""

import os
import logging
import pandas as pd

logger = logging.getLogger('sharepoint_migration_tool')

class DuplicateFinder:
    """Finds duplicate files in the file system"""
    
    def __init__(self, config=None):
        """
        Initialize the duplicate finder
        
        Args:
            config (dict): Configuration settings
        """
        self.config = config or {}
        
    def analyze_dataframe(self, df):
        """
        Analyze a DataFrame of files to identify duplicates
        
        Args:
            df (pandas.DataFrame): DataFrame containing file information
            
        Returns:
            pandas.DataFrame: DataFrame with duplicates identified
        """
        logger.info("Analyzing files for duplicates")
        
        # Create a copy to avoid modifying the original
        result_df = df.copy()
        
        # Check if we have hash values to use for duplicate detection
        if 'hash' not in result_df.columns or result_df['hash'].isna().all():
            logger.warning("No hash values available for content-based duplicate detection")
            logger.info("Falling back to filename-based duplicate detection")
            return self._find_duplicates_by_name(result_df)
        
        # Identify duplicates by hash
        return self._find_duplicates_by_hash(result_df)
        
    def _find_duplicates_by_hash(self, df):
        """
        Find duplicate files based on content hash
        
        Args:
            df (pandas.DataFrame): DataFrame containing file information
            
        Returns:
            pandas.DataFrame: DataFrame with duplicates identified
        """
        # Create a copy with new columns for duplicate tracking
        result_df = df.copy()
        result_df['is_duplicate'] = False
        result_df['duplicate_group'] = None
        result_df['is_original'] = True
        result_df['original_path'] = None
        
        # Group by hash and find duplicates
        duplicates = result_df[result_df.duplicated(subset=['hash'], keep=False)]
        
        if len(duplicates) == 0:
            logger.info("No duplicate files found by content hash")
            return result_df
            
        # Process each group of duplicates
        duplicate_groups = duplicates.groupby('hash')
        
        for group_idx, (hash_value, group) in enumerate(duplicate_groups):
            # Skip empty hashes
            if not hash_value or pd.isna(hash_value) or hash_value == "":
                continue
                
            # Sort by creation time to identify the "original" (oldest) file
            sorted_group = group.sort_values(by='created')
            
            # The first file is considered the original
            original_path = sorted_group.iloc[0]['path']
            
            # Mark all files in this group
            for idx in sorted_group.index:
                result_df.at[idx, 'is_duplicate'] = True
                result_df.at[idx, 'duplicate_group'] = group_idx
                
                # Mark all but the first as non-original
                if result_df.at[idx, 'path'] != original_path:
                    result_df.at[idx, 'is_original'] = False
                    result_df.at[idx, 'original_path'] = original_path
                    
        # Summary statistics
        duplicate_count = len(result_df[result_df['is_duplicate'] == True])
        non_original_count = len(result_df[result_df['is_original'] == False])
        total_count = len(result_df)
        
        logger.info(f"Found {duplicate_count} files in duplicate groups")
        logger.info(f"{non_original_count} files can be removed as duplicates")
        
        return result_df
        
    def _find_duplicates_by_name(self, df):
        """
        Find potential duplicate files based on filename
        
        Args:
            df (pandas.DataFrame): DataFrame containing file information
            
        Returns:
            pandas.DataFrame: DataFrame with potential duplicates identified
        """
        # Create a copy with new columns for duplicate tracking
        result_df = df.copy()
        result_df['is_duplicate'] = False
        result_df['duplicate_group'] = None
        result_df['is_original'] = True
        result_df['original_path'] = None
        
        # Group by name (regardless of path) and find duplicates
        if 'name' in result_df.columns:
            name_duplicates = result_df[result_df.duplicated(subset=['name'], keep=False)]
            
            if len(name_duplicates) == 0:
                logger.info("No duplicate filenames found")
                return result_df
                
            # Process each group of duplicates
            name_duplicate_groups = name_duplicates.groupby('name')
            
            for group_idx, (name, group) in enumerate(name_duplicate_groups):
                # Skip empty names
                if not name or pd.isna(name) or name == "":
                    continue
                    
                # For name-based duplicates, we check size as an additional indicator
                # Files with same name and same size are more likely to be duplicates
                size_groups = group.groupby('size')
                
                for size, size_group in size_groups:
                    if len(size_group) > 1:
                        # Sort by creation time to identify the "original" (oldest) file
                        sorted_group = size_group.sort_values(by='created')
                        
                        # The first file is considered the original
                        original_path = sorted_group.iloc[0]['path']
                        
                        # Mark all files in this group
                        for idx in sorted_group.index:
                            result_df.at[idx, 'is_duplicate'] = True
                            result_df.at[idx, 'duplicate_group'] = f"{group_idx}_{size}"
                            
                            # Mark all but the first as non-original
                            if result_df.at[idx, 'path'] != original_path:
                                result_df.at[idx, 'is_original'] = False
                                result_df.at[idx, 'original_path'] = original_path
        
        # Summary statistics
        duplicate_count = len(result_df[result_df['is_duplicate'] == True])
        non_original_count = len(result_df[result_df['is_original'] == False])
        total_count = len(result_df)
        
        logger.info(f"Found {duplicate_count} files in name-based duplicate groups")
        logger.info(f"{non_original_count} files are potential duplicates (same name and size)")
        logger.info("Note: Name-based duplicate detection is less reliable than content-based detection")
        
        return result_df
        
    def get_duplicate_stats(self, df):
        """
        Get statistics about duplicate detection
        
        Args:
            df (pandas.DataFrame): DataFrame with duplicate detection results
            
        Returns:
            dict: Statistics about duplicates
        """
        if 'is_duplicate' not in df.columns:
            return {
                'total_files': len(df),
                'duplicate_groups': 0,
                'duplicate_files': 0,
                'removable_duplicates': 0,
                'space_savings': 0
            }
            
        total_files = len(df)
        duplicate_files = len(df[df['is_duplicate'] == True])
        removable_duplicates = len(df[df['is_original'] == False])
        
        # Calculate potential space savings
        space_savings = 0
        if 'size' in df.columns:
            space_savings = df[df['is_original'] == False]['size'].sum()
            
        # Count duplicate groups
        duplicate_groups = 0
        if 'duplicate_group' in df.columns:
            duplicate_groups = df['duplicate_group'].nunique()
            
        return {
            'total_files': total_files,
            'duplicate_groups': duplicate_groups,
            'duplicate_files': duplicate_files,
            'removable_duplicates': removable_duplicates,
            'space_savings': space_savings,
            'space_savings_formatted': self._format_size(space_savings)
        }
        
    def _format_size(self, size_bytes):
        """
        Format file size in human-readable format
        
        Args:
            size_bytes (int): Size in bytes
            
        Returns:
            str: Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"