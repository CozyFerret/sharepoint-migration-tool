# core/analyzers/duplicate_finder.py
import os
import hashlib
import pandas as pd
import logging

# Configure logger
logger = logging.getLogger('sharepoint_migration_tool')

class DuplicateFinder:
    """Finds duplicate files based on content hash or other attributes"""
    
    def __init__(self, config=None):
        """
        Initialize the duplicate finder with configuration
        
        Args:
            config (dict): Configuration options
        """
        self.config = config or {}
        
        # Maximum file size to hash (default 50MB)
        self.max_hash_size = self.config.get('max_hash_size', 50 * 1024 * 1024)
        
        # Chunk size for reading files (default 8KB)
        self.chunk_size = self.config.get('chunk_size', 8192)
        
        logger.info("DuplicateFinder initialized")
    
    def analyze_dataframe(self, df):
        """
        Analyze a dataframe of files to find duplicates
        
        Args:
            df (pandas.DataFrame): DataFrame with file data
            
        Returns:
            pandas.DataFrame: The input DataFrame with additional duplicate analysis columns
        """
        try:
            logger.info("Analyzing files for duplicates")
            
            # Create a copy to avoid modifying the original
            result_df = df.copy()
            
            # Add default analysis columns
            result_df['file_hash'] = ''
            result_df['is_duplicate'] = False
            result_df['duplicate_of'] = ''
            
            # Skip if DataFrame is empty
            if result_df.empty:
                logger.warning("Empty DataFrame provided to duplicate finder")
                return result_df
                
            # Check if required columns exist
            if 'path' not in result_df.columns:
                logger.warning("DataFrame missing 'path' column")
                return result_df
                
            # Create a dictionary to track unique files by hash
            unique_files = {}
            duplicate_count = 0
            
            # Process each file
            for idx, row in result_df.iterrows():
                file_path = row.get('path', '')
                file_size = row.get('size', 0)
                
                # Skip directories
                if row.get('is_folder', False):
                    continue
                
                # Skip files larger than max_hash_size
                if file_size > self.max_hash_size:
                    logger.debug(f"Skipping large file for hashing: {file_path} ({file_size} bytes)")
                    continue
                
                try:
                    # Calculate file hash
                    file_hash = self._calculate_file_hash(file_path)
                    
                    # Store the hash
                    result_df.at[idx, 'file_hash'] = file_hash
                    
                    # Check if this is a duplicate
                    if file_hash in unique_files:
                        # This is a duplicate
                        result_df.at[idx, 'is_duplicate'] = True
                        result_df.at[idx, 'duplicate_of'] = unique_files[file_hash]
                        duplicate_count += 1
                    else:
                        # This is a unique file
                        unique_files[file_hash] = file_path
                        
                except Exception as e:
                    logger.warning(f"Could not hash file {file_path}: {str(e)}")
            
            logger.info(f"Found {duplicate_count} duplicate files")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error in duplicate analysis: {str(e)}")
            # Return the original DataFrame if an error occurs
            return df
    
    def _calculate_file_hash(self, file_path):
        """
        Calculate MD5 hash of a file
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Hexadecimal hash string
        """
        md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(self.chunk_size)
                if not data:
                    break
                md5.update(data)
                
        return md5.hexdigest()