# core/analyzers/name_validator.py
import re
import os
import pandas as pd
import logging

# Configure logger
logger = logging.getLogger('sharepoint_migration_tool')

class SharePointNameValidator:
    """Validates file and folder names against SharePoint naming restrictions"""
    
    def __init__(self, config=None):
        """
        Initialize the validator with configuration
        
        Args:
            config (dict): Configuration options
        """
        self.config = config or {}
        
        # SharePoint illegal characters
        self.illegal_chars = r'[~#%&*{}\\:<>?/|"]'
        
        # SharePoint reserved names
        self.reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL', 
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        # Illegal prefixes and suffixes
        self.illegal_prefixes = ['.~', '_vti_']
        self.illegal_suffixes = ['.files', '_files', '-Dateien', '.data']
        
        # Maximum filename length in SharePoint
        self.max_filename_length = 128
        
        logger.info("SharePointNameValidator initialized")
    
    def analyze_dataframe(self, df):
        """
        Analyze a dataframe of files for SharePoint naming issues
        
        Args:
            df (pandas.DataFrame): DataFrame with file data
            
        Returns:
            pandas.DataFrame: The input DataFrame with additional validation columns
        """
        try:
            logger.info("Analyzing file names for SharePoint compatibility")
            
            # Create a copy to avoid modifying the original
            result_df = df.copy()
            
            # Add default validation columns
            result_df['name_valid'] = True
            result_df['name_issues'] = ''
            
            # Skip if DataFrame is empty
            if result_df.empty:
                logger.warning("Empty DataFrame provided to name validator")
                return result_df
                
            # Check if required columns exist
            if 'name' not in result_df.columns:
                logger.warning("DataFrame missing 'name' column")
                return result_df
                
            # Process each file
            for idx, row in result_df.iterrows():
                issues = []
                file_name = row.get('name', '')
                
                # Check filename length
                if len(file_name) > self.max_filename_length:
                    issues.append('filename_too_long')
                
                # Check for illegal characters
                if re.search(self.illegal_chars, file_name):
                    issues.append('illegal_characters')
                
                # Check for reserved names
                name_without_ext = os.path.splitext(file_name)[0].upper()
                if name_without_ext in self.reserved_names:
                    issues.append('reserved_name')
                
                # Check for illegal prefixes
                for prefix in self.illegal_prefixes:
                    if file_name.startswith(prefix):
                        issues.append('illegal_prefix')
                        break
                
                # Check for illegal suffixes
                for suffix in self.illegal_suffixes:
                    if name_without_ext.endswith(suffix):
                        issues.append('illegal_suffix')
                        break
                
                # Update the row with validation results
                if issues:
                    result_df.at[idx, 'name_valid'] = False
                    result_df.at[idx, 'name_issues'] = ','.join(issues)
            
            # Count issues
            issue_count = len(result_df[result_df['name_valid'] == False])
            logger.info(f"Found {issue_count} files with name issues")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error in name validation: {str(e)}")
            # Return the original DataFrame if an error occurs
            return df