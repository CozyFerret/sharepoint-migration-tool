# core/analyzers/path_analyzer.py
import os
import pandas as pd
import logging

# Configure logger
logger = logging.getLogger('sharepoint_migration_tool')

class PathAnalyzer:
    """Analyzes file paths for SharePoint compatibility issues"""
    
    def __init__(self, config=None):
        """
        Initialize the path analyzer with configuration
        
        Args:
            config (dict): Configuration options
        """
        self.config = config or {}
        
        # SharePoint path length limit (default 256)
        self.max_path_length = self.config.get('max_path_length', 256)
        
        # SharePoint URL length limit
        self.max_url_length = self.config.get('max_url_length', 400)
        
        logger.info("PathAnalyzer initialized")
    
    def analyze_dataframe(self, df):
        """
        Analyze a dataframe of files for path length issues
        
        Args:
            df (pandas.DataFrame): DataFrame with file data
            
        Returns:
            pandas.DataFrame: The input DataFrame with additional path analysis columns
        """
        try:
            logger.info("Analyzing path lengths for SharePoint compatibility")
            
            # Create a copy to avoid modifying the original
            result_df = df.copy()
            
            # Add default analysis columns
            result_df['path_too_long'] = False
            result_df['path_length'] = 0
            result_df['url_too_long'] = False
            result_df['url_length'] = 0
            
            # Skip if DataFrame is empty
            if result_df.empty:
                logger.warning("Empty DataFrame provided to path analyzer")
                return result_df
                
            # Check if required columns exist
            if 'path' not in result_df.columns:
                logger.warning("DataFrame missing 'path' column")
                return result_df
                
            # Process each file
            for idx, row in result_df.iterrows():
                file_path = row.get('path', '')
                
                # Calculate path length
                path_length = len(file_path)
                result_df.at[idx, 'path_length'] = path_length
                
                # Check if path is too long
                if path_length > self.max_path_length:
                    result_df.at[idx, 'path_too_long'] = True
                
                # Estimate URL length (approximate)
                # In SharePoint, URLs are often longer than file paths due to
                # additional components like site URL, library name, etc.
                url_length = path_length + 50  # Add buffer for SharePoint URL components
                result_df.at[idx, 'url_length'] = url_length
                
                if url_length > self.max_url_length:
                    result_df.at[idx, 'url_too_long'] = True
            
            # Count issues
            path_issues = len(result_df[result_df['path_too_long'] == True])
            url_issues = len(result_df[result_df['url_too_long'] == True])
            
            logger.info(f"Found {path_issues} files with path length issues")
            logger.info(f"Found {url_issues} files with potential URL length issues")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error in path analysis: {str(e)}")
            # Return the original DataFrame if an error occurs
            return df