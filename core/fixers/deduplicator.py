# core/fixers/deduplicator.py
import os
import shutil
import pandas as pd
from datetime import datetime

class Deduplicator:
    """Handles duplicate files according to various strategies"""
    
    def __init__(self, strategy="Keep Newest Version"):
        self.strategy = strategy
    
    def resolve_duplicates(self, duplicate_groups, file_data_df):
        """
        Determine which files to keep from duplicate groups
        
        Args:
            duplicate_groups: List of groups of files with the same content
            file_data_df: DataFrame with file metadata
            
        Returns:
            dict: Keys are files to keep, values are lists of duplicates to remove
        """
        result = {}
        
        for group in duplicate_groups:
            if len(group) <= 1:
                continue  # Not a duplicate group
                
            # Get file metadata for this group
            group_data = file_data_df[file_data_df['path'].isin(group)]
            
            # Apply strategy to select which file to keep
            if self.strategy == "Keep Newest Version":
                # Sort by modified date descending
                group_data = group_data.sort_values('modified_date', ascending=False)
                
            elif self.strategy == "Keep Oldest Version":
                # Sort by modified date ascending
                group_data = group_data.sort_values('modified_date', ascending=True)
                
            elif self.strategy == "Keep Largest Version":
                # Sort by file size descending
                group_data = group_data.sort_values('size', ascending=False)
                
            elif self.strategy == "Keep Smallest Version":
                # Sort by file size ascending
                group_data = group_data.sort_values('size', ascending=True)
                
            elif self.strategy == "Rename All Duplicates":
                # Keep all files, but they'll be renamed later
                result.update({file: [] for file in group})
                continue
            
            # First file is the one to keep, rest are duplicates
            to_keep = group_data.iloc[0]['path']
            to_remove = [f for f in group if f != to_keep]
            
            result[to_keep] = to_remove
            
        return result
    
    def fix_file(self, src_path, dest_dir, is_duplicate=False, dup_index=0, preserve_structure=True):
        """
        Copy a file to destination directory, handling duplicates according to strategy
        
        Args:
            src_path: Source file path
            dest_dir: Destination directory
            is_duplicate: Whether this is a duplicate file
            dup_index: Index for this duplicate (for renaming)
            preserve_structure: Whether to preserve the directory structure
            
        Returns:
            Tuple: (success, new_path)
        """
        try:
            # Determine the destination path
            if preserve_structure:
                rel_dir = os.path.dirname(src_path)
                dest_subdir = os.path.join(dest_dir, os.path.basename(rel_dir))
                os.makedirs(dest_subdir, exist_ok=True)
            else:
                dest_subdir = dest_dir
            
            file_name = os.path.basename(src_path)
            file_base, file_ext = os.path.splitext(file_name)
            
            # Handle duplicates according to strategy
            if is_duplicate and self.strategy == "Rename All Duplicates":
                # Rename the file to include its duplicate index
                file_name = f"{file_base}_dup{dup_index}{file_ext}"
            
            dest_path = os.path.join(dest_subdir, file_name)
            
            # Copy the file to the new location
            shutil.copy2(src_path, dest_path)
            
            return True, dest_path
        except Exception as e:
            print(f"Error handling duplicate file {src_path}: {e}")
            return False, None