#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Deduplicator for SharePoint Data Migration Cleanup Tool.
Handles duplicate files by selecting which ones to keep or remove.
"""

import os
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger('sharepoint_migration_tool')

class Deduplicator:
    """Handles duplicate files by selecting which ones to keep or remove"""
    
    def __init__(self, config=None):
        """
        Initialize the deduplicator
        
        Args:
            config (dict): Configuration settings
        """
        self.config = config or {}
        
        # Configure deduplication strategy
        self.dedup_config = self.config.get('deduplication', {})
        self.strategy = self.dedup_config.get('strategy', 'keep_oldest')
        
    def process_duplicates(self, duplicates_df, target_root=None):
        """
        Process duplicate files according to the chosen strategy
        
        Args:
            duplicates_df (pandas.DataFrame): DataFrame with duplicate files
            target_root (str, optional): Target root directory for copied files
            
        Returns:
            pandas.DataFrame: DataFrame with actions for each duplicate file
        """
        if duplicates_df is None or len(duplicates_df) == 0:
            logger.info("No duplicates to process")
            return pd.DataFrame()
            
        # Create a copy to avoid modifying the original
        result_df = duplicates_df.copy()
        
        # Add columns for deduplication actions
        if 'action' not in result_df.columns:
            result_df['action'] = None
            
        if 'target_path' not in result_df.columns:
            result_df['target_path'] = None
            
        # Apply the deduplication strategy
        if self.strategy == 'keep_oldest':
            return self._strategy_keep_oldest(result_df, target_root)
        elif self.strategy == 'keep_newest':
            return self._strategy_keep_newest(result_df, target_root)
        elif self.strategy == 'keep_smallest':
            return self._strategy_keep_smallest(result_df, target_root)
        elif self.strategy == 'keep_largest':
            return self._strategy_keep_largest(result_df, target_root)
        else:
            # Default to keep_oldest
            return self._strategy_keep_oldest(result_df, target_root)
            
    def _strategy_keep_oldest(self, duplicates_df, target_root=None):
        """
        Strategy: Keep the oldest file in each duplicate group
        
        Args:
            duplicates_df (pandas.DataFrame): DataFrame with duplicate files
            target_root (str, optional): Target root directory for copied files
            
        Returns:
            pandas.DataFrame: DataFrame with actions for each duplicate file
        """
        result_df = duplicates_df.copy()
        
        # Group by hash (or another duplicate identifier)
        group_by = 'hash' if 'hash' in result_df.columns else 'duplicate_group'
        
        # If neither column exists, we can't group
        if group_by not in result_df.columns:
            logger.error("Cannot group duplicates - no hash or duplicate_group column")
            return result_df
            
        # Process each group of duplicates
        for group_value, group_df in result_df.groupby(group_by):
            # Skip empty or NaN group values
            if not group_value or pd.isna(group_value):
                continue
                
            # Sort by creation time
            sorted_group = group_df.sort_values('created', ascending=True)
            
            # Get the oldest file
            oldest_file = sorted_group.iloc[0]
            oldest_path = oldest_file['path']
            
            # Mark each file in the group
            for index, row in sorted_group.iterrows():
                if row['path'] == oldest_path:
                    # Keep the oldest file
                    result_df.at[index, 'action'] = 'keep'
                    
                    # Set target path if needed
                    if target_root:
                        # Extract the filename
                        file_name = os.path.basename(row['path'])
                        
                        # Use direct path in target root for simplicity
                        target_path = os.path.join(target_root, file_name)
                        result_df.at[index, 'target_path'] = target_path
                    else:
                        result_df.at[index, 'target_path'] = row['path']
                else:
                    # Skip younger duplicates
                    result_df.at[index, 'action'] = 'skip_duplicate'
                    result_df.at[index, 'target_path'] = None
                    
        logger.info(f"Processed {len(result_df)} files with keep_oldest strategy")
        return result_df
        
    def _strategy_keep_newest(self, duplicates_df, target_root=None):
        """
        Strategy: Keep the newest file in each duplicate group
        
        Args:
            duplicates_df (pandas.DataFrame): DataFrame with duplicate files
            target_root (str, optional): Target root directory for copied files
            
        Returns:
            pandas.DataFrame: DataFrame with actions for each duplicate file
        """
        result_df = duplicates_df.copy()
        
        # Group by hash (or another duplicate identifier)
        group_by = 'hash' if 'hash' in result_df.columns else 'duplicate_group'
        
        # If neither column exists, we can't group
        if group_by not in result_df.columns:
            logger.error("Cannot group duplicates - no hash or duplicate_group column")
            return result_df
            
        # Process each group of duplicates
        for group_value, group_df in result_df.groupby(group_by):
            # Skip empty or NaN group values
            if not group_value or pd.isna(group_value):
                continue
                
            # Sort by creation time (newest first)
            sorted_group = group_df.sort_values('created', ascending=False)
            
            # Get the newest file
            newest_file = sorted_group.iloc[0]
            newest_path = newest_file['path']
            
            # Mark each file in the group
            for index, row in sorted_group.iterrows():
                if row['path'] == newest_path:
                    # Keep the newest file
                    result_df.at[index, 'action'] = 'keep'
                    
                    # Set target path if needed
                    if target_root:
                        # Extract the filename
                        file_name = os.path.basename(row['path'])
                        
                        # Use direct path in target root for simplicity
                        target_path = os.path.join(target_root, file_name)
                        result_df.at[index, 'target_path'] = target_path
                    else:
                        result_df.at[index, 'target_path'] = row['path']
                else:
                    # Skip older duplicates
                    result_df.at[index, 'action'] = 'skip_duplicate'
                    result_df.at[index, 'target_path'] = None
                    
        logger.info(f"Processed {len(result_df)} files with keep_newest strategy")
        return result_df
        
    def _strategy_keep_smallest(self, duplicates_df, target_root=None):
        """
        Strategy: Keep the smallest file in each duplicate group
        
        Args:
            duplicates_df (pandas.DataFrame): DataFrame with duplicate files
            target_root (str, optional): Target root directory for copied files
            
        Returns:
            pandas.DataFrame: DataFrame with actions for each duplicate file
        """
        result_df = duplicates_df.copy()
        
        # Group by hash (or another duplicate identifier)
        group_by = 'hash' if 'hash' in result_df.columns else 'duplicate_group'
        
        # If neither column exists, we can't group
        if group_by not in result_df.columns:
            logger.error("Cannot group duplicates - no hash or duplicate_group column")
            return result_df
            
        # Check if we have size information
        if 'size' not in result_df.columns:
            logger.warning("No size column - falling back to keep_oldest strategy")
            return self._strategy_keep_oldest(result_df, target_root)
            
        # Process each group of duplicates
        for group_value, group_df in result_df.groupby(group_by):
            # Skip empty or NaN group values
            if not group_value or pd.isna(group_value):
                continue
                
            # Sort by file size
            sorted_group = group_df.sort_values('size', ascending=True)
            
            # Get the smallest file
            smallest_file = sorted_group.iloc[0]
            smallest_path = smallest_file['path']
            
            # Mark each file in the group
            for index, row in sorted_group.iterrows():
                if row['path'] == smallest_path:
                    # Keep the smallest file
                    result_df.at[index, 'action'] = 'keep'
                    
                    # Set target path if needed
                    if target_root:
                        # Extract the filename
                        file_name = os.path.basename(row['path'])
                        
                        # Use direct path in target root for simplicity
                        target_path = os.path.join(target_root, file_name)
                        result_df.at[index, 'target_path'] = target_path
                    else:
                        result_df.at[index, 'target_path'] = row['path']
                else:
                    # Skip larger duplicates
                    result_df.at[index, 'action'] = 'skip_duplicate'
                    result_df.at[index, 'target_path'] = None
                    
        logger.info(f"Processed {len(result_df)} files with keep_smallest strategy")
        return result_df
        
    def _strategy_keep_largest(self, duplicates_df, target_root=None):
        """
        Strategy: Keep the largest file in each duplicate group
        
        Args:
            duplicates_df (pandas.DataFrame): DataFrame with duplicate files
            target_root (str, optional): Target root directory for copied files
            
        Returns:
            pandas.DataFrame: DataFrame with actions for each duplicate file
        """
        result_df = duplicates_df.copy()
        
        # Group by hash (or another duplicate identifier)
        group_by = 'hash' if 'hash' in result_df.columns else 'duplicate_group'
        
        # If neither column exists, we can't group
        if group_by not in result_df.columns:
            logger.error("Cannot group duplicates - no hash or duplicate_group column")
            return result_df
            
        # Check if we have size information
        if 'size' not in result_df.columns:
            logger.warning("No size column - falling back to keep_oldest strategy")
            return self._strategy_keep_oldest(result_df, target_root)
            
        # Process each group of duplicates
        for group_value, group_df in result_df.groupby(group_by):
            # Skip empty or NaN group values
            if not group_value or pd.isna(group_value):
                continue
                
            # Sort by file size (largest first)
            sorted_group = group_df.sort_values('size', ascending=False)
            
            # Get the largest file
            largest_file = sorted_group.iloc[0]
            largest_path = largest_file['path']
            
            # Mark each file in the group
            for index, row in sorted_group.iterrows():
                if row['path'] == largest_path:
                    # Keep the largest file
                    result_df.at[index, 'action'] = 'keep'
                    
                    # Set target path if needed
                    if target_root:
                        # Extract the filename
                        file_name = os.path.basename(row['path'])
                        
                        # Use direct path in target root for simplicity
                        target_path = os.path.join(target_root, file_name)
                        result_df.at[index, 'target_path'] = target_path
                    else:
                        result_df.at[index, 'target_path'] = row['path']
                else:
                    # Skip smaller duplicates
                    result_df.at[index, 'action'] = 'skip_duplicate'
                    result_df.at[index, 'target_path'] = None
                    
        logger.info(f"Processed {len(result_df)} files with keep_largest strategy")
        return result_df
        
    def get_duplicates_stats(self, duplicates_df):
        """
        Get statistics about duplicate files
        
        Args:
            duplicates_df (pandas.DataFrame): DataFrame with duplicate files
            
        Returns:
            dict: Statistics about duplicate files
        """
        if duplicates_df is None or len(duplicates_df) == 0:
            return {
                'total_groups': 0,
                'total_duplicates': 0,
                'space_savings': 0,
                'space_savings_formatted': '0 bytes'
            }
            
        # Count duplicate groups
        group_by = 'hash' if 'hash' in duplicates_df.columns else 'duplicate_group'
        if group_by in duplicates_df.columns:
            # Filter out empty or NaN group values
            valid_groups = duplicates_df[duplicates_df[group_by].notna()]
            total_groups = valid_groups[group_by].nunique()
        else:
            total_groups = 0
            
        # Count duplicates (non-original files)
        if 'is_original' in duplicates_df.columns:
            total_duplicates = (~duplicates_df['is_original']).sum()
        else:
            total_duplicates = len(duplicates_df)
            
        # Calculate potential space savings
        space_savings = 0
        if 'size' in duplicates_df.columns and 'is_original' in duplicates_df.columns:
            # Sum the size of non-original files
            space_savings = duplicates_df[~duplicates_df['is_original']]['size'].sum()
            
        # Format space savings
        if space_savings < 1024:
            space_savings_formatted = f"{space_savings} bytes"
        elif space_savings < 1024 * 1024:
            space_savings_formatted = f"{space_savings / 1024:.2f} KB"
        elif space_savings < 1024 * 1024 * 1024:
            space_savings_formatted = f"{space_savings / (1024 * 1024):.2f} MB"
        else:
            space_savings_formatted = f"{space_savings / (1024 * 1024 * 1024):.2f} GB"
            
        return {
            'total_groups': total_groups,
            'total_duplicates': total_duplicates,
            'space_savings': space_savings,
            'space_savings_formatted': space_savings_formatted
        }
        
    def set_strategy(self, strategy):
        """
        Set the deduplication strategy
        
        Args:
            strategy (str): Deduplication strategy
        """
        allowed_strategies = ['keep_oldest', 'keep_newest', 'keep_smallest', 'keep_largest']
        
        if strategy in allowed_strategies:
            self.strategy = strategy
            logger.info(f"Deduplication strategy set to {strategy}")
        else:
            logger.warning(f"Invalid strategy: {strategy}. Using default (keep_oldest)")
            self.strategy = 'keep_oldest'