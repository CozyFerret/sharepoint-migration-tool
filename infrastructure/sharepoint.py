"""
SharePoint Integration Module for Migration Tool
Provides functionality for authentication, data cleaning and automatic upload to SharePoint
"""

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder

from core.data_cleaner import DataCleaner
from core.analyzers.name_validator import NameValidator
from core.analyzers.path_analyzer import PathAnalyzer
from core.fixers.name_fixer import NameFixer
from core.fixers.path_shortener import PathShortener

logger = logging.getLogger(__name__)

class SharePointIntegration:
    """
    Handles authentication, data cleaning, and uploading to SharePoint
    """
    
    def __init__(self):
        self.ctx = None  # SharePoint context
        self.site_url = None
        self.temp_dir = None  # Temporary directory for cleaned files
        self.data_cleaner = DataCleaner()
        
    def authenticate(self, site_url: str, username: str, password: str) -> bool:
        """
        Authenticate with SharePoint using username and password
        
        Args:
            site_url: SharePoint site URL
            username: User's email/username
            password: User's password
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            auth_context = AuthenticationContext(site_url)
            success = auth_context.acquire_token_for_user(username, password)
            
            if success:
                self.ctx = ClientContext(site_url, auth_context)
                self.site_url = site_url
                logger.info(f"Successfully authenticated to {site_url}")
                return True
            else:
                logger.error(f"Authentication failed: {auth_context.get_last_error()}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
            
    def authenticate_modern(self, site_url: str, client_id: str, client_secret: str) -> bool:
        """
        Authenticate with SharePoint using modern authentication (app-only)
        
        Args:
            site_url: SharePoint site URL
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            auth_context = AuthenticationContext(site_url)
            success = auth_context.acquire_token_for_app(client_id, client_secret)
            
            if success:
                self.ctx = ClientContext(site_url, auth_context)
                self.site_url = site_url
                logger.info(f"Successfully authenticated to {site_url} using app-only auth")
                return True
            else:
                logger.error(f"App-only authentication failed: {auth_context.get_last_error()}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
            
    def clean_and_export_data(self, source_dir: str, target_dir: str, 
                              fix_names: bool = True, fix_paths: bool = True, 
                              remove_duplicates: bool = False) -> Tuple[bool, str, List[str]]:
        """
        Clean data and export to a target directory without uploading to SharePoint
        
        Args:
            source_dir: Source directory with original files
            target_dir: Target directory for cleaned files
            fix_names: Whether to fix invalid SharePoint names
            fix_paths: Whether to shorten paths exceeding SharePoint limits
            remove_duplicates: Whether to remove duplicate files
            
        Returns:
            Tuple containing:
                bool: Success indicator
                str: Path to cleaned data
                List[str]: List of issues encountered
        """
        issues = []
        
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)
            
            # Set up analyzers and fixers
            analyzers = []
            fixers = []
            
            if fix_names:
                analyzers.append(NameValidator())
                fixers.append(NameFixer())
                
            if fix_paths:
                analyzers.append(PathAnalyzer())
                fixers.append(PathShortener())
                
            # Configure data cleaner
            self.data_cleaner.set_analyzers(analyzers)
            self.data_cleaner.set_fixers(fixers)
            self.data_cleaner.set_source(source_dir)
            self.data_cleaner.set_target(target_dir)
            
            # Execute cleaning
            result = self.data_cleaner.clean(remove_duplicates=remove_duplicates)
            
            # Collect issues
            issues = self.data_cleaner.get_issues()
            
            logger.info(f"Data cleaning completed. {len(issues)} issues found.")
            return True, target_dir, issues
            
        except Exception as e:
            logger.error(f"Error during data cleaning: {str(e)}")
            issues.append(f"Critical error: {str(e)}")
            return False, "", issues
            
    def clean_and_upload(self, source_dir: str, target_library: str,
                         fix_names: bool = True, fix_paths: bool = True,
                         remove_duplicates: bool = False) -> Tuple[bool, List[str], Dict]:
        """
        Clean data and upload directly to SharePoint
        
        Args:
            source_dir: Source directory with original files
            target_library: Target SharePoint document library
            fix_names: Whether to fix invalid SharePoint names
            fix_paths: Whether to shorten paths exceeding SharePoint limits
            remove_duplicates: Whether to remove duplicate files
            
        Returns:
            Tuple containing:
                bool: Success indicator
                List[str]: List of issues encountered
                Dict: Dictionary with upload statistics
        """
        issues = []
        stats = {
            "total_files": 0,
            "uploaded_files": 0,
            "failed_files": 0,
            "total_size_bytes": 0
        }
        
        if not self.ctx:
            issues.append("Not authenticated to SharePoint. Please sign in first.")
            return False, issues, stats
            
        try:
            # Create a temporary directory for cleaned files
            self.temp_dir = tempfile.mkdtemp(prefix="sp_migration_")
            
            # Clean the data
            success, temp_path, cleaning_issues = self.clean_and_export_data(
                source_dir, self.temp_dir, fix_names, fix_paths, remove_duplicates
            )
            
            issues.extend(cleaning_issues)
            
            if not success:
                issues.append("Failed to clean the data before upload.")
                return False, issues, stats
                
            # Upload the cleaned files
            upload_success, upload_issues, upload_stats = self._upload_directory(
                self.temp_dir, target_library
            )
            
            issues.extend(upload_issues)
            stats.update(upload_stats)
            
            return upload_success, issues, stats
            
        except Exception as e:
            logger.error(f"Error during clean and upload: {str(e)}")
            issues.append(f"Critical error: {str(e)}")
            return False, issues, stats
            
        finally:
            # Clean up the temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                
    def _upload_directory(self, local_dir: str, target_library: str) -> Tuple[bool, List[str], Dict]:
        """
        Upload a directory to SharePoint recursively
        
        Args:
            local_dir: Local directory path to upload
            target_library: Target SharePoint document library
            
        Returns:
            Tuple containing:
                bool: Success indicator
                List[str]: List of issues encountered
                Dict: Dictionary with upload statistics
        """
        issues = []
        stats = {
            "total_files": 0,
            "uploaded_files": 0,
            "failed_files": 0,
            "total_size_bytes": 0
        }
        
        if not self.ctx:
            issues.append("Not authenticated to SharePoint.")
            return False, issues, stats
            
        try:
            # Ensure target library exists
            target_folder = self.ctx.web.get_folder_by_server_relative_url(target_library)
            self.ctx.load(target_folder)
            self.ctx.execute_query()
            
            # Process all files and directories recursively
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    
                    # Calculate the relative path from the source directory
                    rel_path = os.path.relpath(local_file_path, local_dir)
                    target_file_path = f"{target_library}/{rel_path.replace(os.sep, '/')}"
                    
                    # Upload the file
                    try:
                        stats["total_files"] += 1
                        file_size = os.path.getsize(local_file_path)
                        stats["total_size_bytes"] += file_size
                        
                        with open(local_file_path, 'rb') as file_content:
                            file_content_bytes = file_content.read()
                            
                        # Create parent folders if needed
                        self._ensure_folders_exist(target_file_path)
                        
                        # Upload the file
                        File.save_binary(self.ctx, target_file_path, file_content_bytes)
                        self.ctx.execute_query()
                        
                        logger.info(f"Uploaded: {rel_path} -> {target_file_path}")
                        stats["uploaded_files"] += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to upload {rel_path}: {str(e)}")
                        issues.append(f"Failed to upload {rel_path}: {str(e)}")
                        stats["failed_files"] += 1
                        
            success = stats["failed_files"] == 0
            return success, issues, stats
            
        except Exception as e:
            logger.error(f"Error during directory upload: {str(e)}")
            issues.append(f"Error accessing target library: {str(e)}")
            return False, issues, stats
            
    def _ensure_folders_exist(self, file_path: str) -> None:
        """
        Ensure all parent folders exist for a given file path
        
        Args:
            file_path: SharePoint file path
        """
        # Split the path into segments
        path_parts = file_path.split('/')
        
        # Remove the file name (last part)
        folder_parts = path_parts[:-1]
        
        if len(folder_parts) <= 1:
            # File is in the root of the document library, no folders to create
            return
            
        # Build the folder path incrementally and create each folder if it doesn't exist
        current_path = folder_parts[0]  # Start with the document library
        
        for i in range(1, len(folder_parts)):
            current_path += f"/{folder_parts[i]}"
            
            try:
                folder = self.ctx.web.get_folder_by_server_relative_url(current_path)
                self.ctx.load(folder)
                self.ctx.execute_query()
                
                # Folder exists, continue
                continue
                
            except Exception:
                # Folder doesn't exist, create it
                parent_path = '/'.join(folder_parts[:i])
                folder_name = folder_parts[i]
                
                parent_folder = self.ctx.web.get_folder_by_server_relative_url(parent_path)
                parent_folder.folders.add(folder_name)
                self.ctx.execute_query()
                
                logger.info(f"Created folder: {current_path}")
                
    def get_document_libraries(self) -> List[str]:
        """
        Get a list of document libraries in the SharePoint site
        
        Returns:
            List[str]: List of document library names
        """
        if not self.ctx:
            logger.error("Not authenticated to SharePoint.")
            return []
            
        try:
            # Load all lists that are document libraries
            lists = self.ctx.web.lists
            self.ctx.load(lists, ["Title", "BaseTemplate"])
            self.ctx.execute_query()
            
            # Filter for document libraries (base template 101)
            doc_libraries = [lst.properties["Title"] for lst in lists 
                            if lst.properties["BaseTemplate"] == 101]
            
            return doc_libraries
            
        except Exception as e:
            logger.error(f"Error getting document libraries: {str(e)}")
            return []
            
    def disconnect(self) -> None:
        """
        Disconnect from SharePoint and clean up resources
        """
        self.ctx = None
        self.site_url = None
        
        # Clean up temporary directory if it exists
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            
        logger.info("Disconnected from SharePoint")