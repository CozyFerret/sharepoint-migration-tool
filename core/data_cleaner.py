#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data cleaner for SharePoint Data Migration Cleanup Tool.
Implements file cleaning operations.
"""

import os
import logging
import shutil
import re
import threading
import time

# Import only what's needed directly
from core.fixers.name_fixer import NameFixer
from core.fixers.path_shortener import PathShortener
from core.fixers.deduplicator import Deduplicator

logger = logging.getLogger('sharepoint_migration_tool')

class DataCleaner:
    """Implements file cleaning operations"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # Initialize fixers
        self.name_fixer = NameFixer(self.config)
        self.path_shortener = PathShortener(self.config)
        self.deduplicator = Deduplicator(self.config)
        
        # Track processing state
        self.is_cleaning = False
        self.cleaned_files = {}
        self.cleaning_thread = None
    
    def preview_fixes(self, analysis_results, clean_options):
        """
        Generate a preview of cleaning operations
        
        Args:
            analysis_results (dict): Analysis results
            clean_options (dict): Options controlling cleaning behavior
            
        Returns:
            dict: Preview information
        """
        preview = {
            'name_fixes': [],
            'path_fixes': [],
            'duplicate_fixes': [],
            'total_fixes': 0
        }
        
        # Preview name fixes
        if clean_options.get('fix_name_issues', True) and 'name_issues' in analysis_results:
            for _, row in analysis_results['name_issues'].iterrows():
                original_path = row.get('path', '')
                fixed_path = self.name_fixer.fix_path(original_path)
                
                if original_path != fixed_path:
                    preview['name_fixes'].append({
                        'original': original_path,
                        'fixed': fixed_path
                    })
        
        # Preview path fixes
        if clean_options.get('fix_path_issues', True) and 'path_issues' in analysis_results:
            for _, row in analysis_results['path_issues'].iterrows():
                original_path = row.get('path', '')
                fixed_path = self.path_shortener.fix_path(original_path)
                
                if original_path != fixed_path:
                    preview['path_fixes'].append({
                        'original': original_path,
                        'fixed': fixed_path
                    })
        
        # Preview duplicate fixes
        if clean_options.get('fix_duplicates', True) and 'duplicates' in analysis_results:
            duplicate_groups = {}
            
            for _, row in analysis_results['duplicates'].iterrows():
                file_path = row.get('path', '')
                hash_value = row.get('file_hash', '')
                
                if hash_value not in duplicate_groups:
                    duplicate_groups[hash_value] = []
                
                duplicate_groups[hash_value].append(file_path)
            
            for hash_value, paths in duplicate_groups.items():
                if len(paths) > 1:
                    # Keep the first file, fix the rest
                    original = paths[0]
                    for duplicate in paths[1:]:
                        strategy = clean_options.get('duplicate_strategy', 'keep_first')
                        fixed_path = self.deduplicator.fix_duplicate(duplicate, original, strategy)
                        
                        preview['duplicate_fixes'].append({
                            'original': duplicate,
                            'fixed': fixed_path,
                            'reference': original
                        })
        
        # Calculate total fixes
        preview['total_fixes'] = len(preview['name_fixes']) + len(preview['path_fixes']) + len(preview['duplicate_fixes'])
        
        return preview
    
    def start_cleaning(self, analysis_results, target_folder, clean_options, 
                     progress_callback=None, status_callback=None, 
                     error_callback=None, file_processed_callback=None,
                     finished_callback=None):
        """
        Start cleaning data based on analysis results
        
        Args:
            analysis_results (dict): Analysis results
            target_folder (str): Target folder for cleaned files
            clean_options (dict): Options controlling cleaning behavior
            progress_callback (function): Callback for progress updates
            status_callback (function): Callback for status updates
            error_callback (function): Callback for errors
            file_processed_callback (function): Callback for each processed file
            finished_callback (function): Callback for completion
        """
        if self.is_cleaning:
            if error_callback:
                error_callback("Cleaning already in progress")
            return
        
        # Create target folder if it doesn't exist
        os.makedirs(target_folder, exist_ok=True)
        
        # Start cleaning in a separate thread
        self.is_cleaning = True
        self.cleaning_thread = threading.Thread(
            target=self._cleaning_thread,
            args=(analysis_results, target_folder, clean_options,
                  progress_callback, status_callback, error_callback,
                  file_processed_callback, finished_callback)
        )
        self.cleaning_thread.daemon = True
        self.cleaning_thread.start()
    
    def _cleaning_thread(self, analysis_results, target_folder, clean_options,
                        progress_callback, status_callback, error_callback,
                        file_processed_callback, finished_callback):
        """Thread that performs the actual cleaning operations"""
        try:
            # Reset cleaned files
            self.cleaned_files = {}
            
            # Get all files to process
            all_files = analysis_results.get('all_files')
            if all_files is None or len(all_files) == 0:
                if status_callback:
                    status_callback("No files to process")
                return
            
            # Calculate total files
            total_files = len(all_files)
            processed_files = 0
            
            # Update status
            if status_callback:
                status_callback(f"Processing {total_files} files")
            
            # Process each file
            for _, row in all_files.iterrows():
                if not self.is_cleaning:
                    # Cleaning was stopped
                    break
                
                # Get file information
                file_path = row.get('path', '')
                
                try:
                    # Process the file
                    processed_path = self._process_file(
                        file_path, target_folder, analysis_results, clean_options
                    )
                    
                    # Store the result
                    if processed_path:
                        self.cleaned_files[file_path] = processed_path
                    
                    # Invoke callback
                    if file_processed_callback:
                        file_processed_callback(file_path, processed_path)
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    
                    if error_callback:
                        error_callback(f"Error processing file {file_path}: {e}")
                
                # Update progress
                processed_files += 1
                if progress_callback:
                    progress_callback(processed_files, total_files)
            
            # Finalize
            self.is_cleaning = False
            
            # Invoke completion callback
            if finished_callback:
                finished_callback(self.cleaned_files)
                
        except Exception as e:
            logger.error(f"Error during cleaning: {e}")
            
            if error_callback:
                error_callback(f"Error during cleaning: {e}")
            
            self.is_cleaning = False
    
    def _process_file(self, file_path, target_folder, analysis_results, clean_options):
        """
        Process a single file
        
        Args:
            file_path (str): Path to the file
            target_folder (str): Target folder for cleaned files
            analysis_results (dict): Analysis results
            clean_options (dict): Options controlling cleaning behavior
            
        Returns:
            str: Path to the processed file, or None if not processed
        """
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return None
        
        # Get file information
        file_name = os.path.basename(file_path)
        relative_path = os.path.relpath(file_path, clean_options.get('source_folder', ''))
        target_path = os.path.join(target_folder, relative_path)
        
        # Check if file has issues
        has_name_issue = False
        has_path_issue = False
        is_duplicate = False
        
        # Check for name issues
        if 'name_issues' in analysis_results:
            name_issues = analysis_results['name_issues']
            has_name_issue = any(name_issues['path'] == file_path)
        
        # Check for path issues
        if 'path_issues' in analysis_results:
            path_issues = analysis_results['path_issues']
            has_path_issue = any(path_issues['path'] == file_path)
        
        # Check for duplicates
        if 'duplicates' in analysis_results:
            duplicates = analysis_results['duplicates']
            is_duplicate = any(duplicates['path'] == file_path)
        
        # Skip certain files based on options
        if clean_options.get('process_only_issues', False):
            if not (has_name_issue or has_path_issue or is_duplicate):
                return None
        
        # Apply fixes if needed
        if has_name_issue and clean_options.get('fix_name_issues', True):
            target_path = self.name_fixer.fix_path(target_path)
        
        if has_path_issue and clean_options.get('fix_path_issues', True):
            target_path = self.path_shortener.fix_path(target_path)
        
        if is_duplicate and clean_options.get('fix_duplicates', True):
            # Find the original file in this duplicate group
            duplicates = analysis_results['duplicates']
            duplicate_group = duplicates[duplicates['path'] == file_path]
            
            if len(duplicate_group) > 0:
                file_hash = duplicate_group.iloc[0].get('file_hash', '')
                
                # Find all files with this hash
                group_files = duplicates[duplicates['file_hash'] == file_hash]['path'].tolist()
                
                if len(group_files) > 0:
                    # First file is the original, this file is a duplicate
                    original = group_files[0]
                    
                    if file_path != original:
                        # This is a duplicate
                        strategy = clean_options.get('duplicate_strategy', 'keep_first')
                        target_path = self.deduplicator.fix_duplicate(target_path, original, strategy)
        
        # Ensure target directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Copy the file
        shutil.copy2(file_path, target_path)
        
        return target_path
    
    def stop_cleaning(self):
        """Stop an ongoing cleaning operation"""
        self.is_cleaning = False