#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data processor for SharePoint Data Migration Cleanup Tool.
Integrates scanning, analysis, and cleaning operations.
"""

import os
import logging
import tempfile
import pandas as pd

from core.scanner import FileSystemScanner
from core.analyzers.name_validator import SharePointNameValidator
from core.analyzers.path_analyzer import PathAnalyzer
from core.analyzers.duplicate_finder import DuplicateFinder
from core.analyzers.pii_detector import PIIDetector
from core.data_cleaner import DataCleaner

logger = logging.getLogger('sharepoint_migration_tool')

class DataProcessor:
    """Integrates scanning, analysis, and cleaning operations"""
    
    def __init__(self, config=None):
        """
        Initialize the data processor
        
        Args:
            config (dict): Configuration settings
        """
        self.config = config or {}
        
        # Initialize components
        self.scanner = FileSystemScanner()
        self.name_validator = SharePointNameValidator(self.config)
        self.path_analyzer = PathAnalyzer(self.config)
        self.duplicate_finder = DuplicateFinder(self.config)
        self.pii_detector = PIIDetector(self.config)
        self.data_cleaner = DataCleaner(self.config)
        
        # Store state
        self.scan_data = None
        self.analysis_results = {}
        self.cleaned_files = {}
        
    def start_scan(self, root_path, scan_options=None, callbacks=None):
        """
        Start scanning a directory
        
        Args:
            root_path (str): The root path to scan
            scan_options (dict): Options controlling scan behavior
            callbacks (dict): Dictionary of callback functions
        """
        # Default callbacks
        if callbacks is None:
            callbacks = {}
            
        # Start the scan
        self.scanner.start_scan(
            root_path,
            scan_options,
            progress_callback=callbacks.get('progress'),
            status_callback=callbacks.get('status'),
            error_callback=callbacks.get('error'),
            finished_callback=lambda results: self._scan_completed(results, callbacks.get('scan_completed'))
        )
        
    def _scan_completed(self, results, callback=None):
        """
        Handle scan completion
        
        Args:
            results (pandas.DataFrame): Scan results
            callback (function): Callback to invoke after processing
        """
        self.scan_data = results
        
        # Store the full dataset in the analysis results
        self.analysis_results['all_files'] = results
        
        # Invoke the callback
        if callback:
            callback(results)
            
    def analyze_data(self, feature_flags=None, callbacks=None):
        """
        Analyze scanned data for various issues
        
        Args:
            feature_flags (dict): Dictionary of feature flags
            callbacks (dict): Dictionary of callback functions
        """
        if self.scan_data is None or len(self.scan_data) == 0:
            logger.warning("No data to analyze")
            return
            
        # Default feature flags
        if feature_flags is None:
            feature_flags = {
                'name_validation': True,
                'path_length': True,
                'duplicate_detection': True,
                'pii_detection': True
            }
            
        # Default callbacks
        if callbacks is None:
            callbacks = {}
            
        # Analyze name issues
        if feature_flags.get('name_validation', True):
            self._analyze_name_issues(callbacks.get('name_validation_completed'))
            
        # Analyze path issues
        if feature_flags.get('path_length', True):
            self._analyze_path_issues(callbacks.get('path_length_completed'))
            
        # Analyze duplicates
        if feature_flags.get('duplicate_detection', True):
            self._analyze_duplicates(callbacks.get('duplicate_detection_completed'))
            
        # Analyze PII
        if feature_flags.get('pii_detection', True):
            self._analyze_pii(callbacks.get('pii_detection_completed'))
            
        # Invoke the overall completion callback
        if callbacks.get('analysis_completed'):
            callbacks['analysis_completed'](self.analysis_results)
            
    def _analyze_name_issues(self, callback=None):
        """
        Analyze file names for SharePoint compatibility
        
        Args:
            callback (function): Callback to invoke after processing
        """
        logger.info("Analyzing file names for SharePoint compatibility")
        
        try:
            name_results = self.name_validator.analyze_dataframe(self.scan_data)
            self.analysis_results['name_issues'] = name_results[name_results['name_valid'] == False]
            
            logger.info(f"Found {len(self.analysis_results['name_issues'])} files with name issues")
            
            # Invoke the callback
            if callback:
                callback(self.analysis_results['name_issues'])
                
        except Exception as e:
            logger.error(f"Error analyzing names: {e}")
            
    def _analyze_path_issues(self, callback=None):
        """
        Analyze path lengths against SharePoint limitations
        
        Args:
            callback (function): Callback to invoke after processing
        """
        logger.info("Analyzing path lengths for SharePoint compatibility")
        
        try:
            path_results = self.path_analyzer.analyze_dataframe(self.scan_data)
            self.analysis_results['path_issues'] = path_results[path_results['path_too_long'] == True]
            
            logger.info(f"Found {len(self.analysis_results['path_issues'])} files with path length issues")
            
            # Invoke the callback
            if callback:
                callback(self.analysis_results['path_issues'])
                
        except Exception as e:
            logger.error(f"Error analyzing paths: {e}")
            
    def _analyze_duplicates(self, callback=None):
        """
        Analyze files for duplicates
        
        Args:
            callback (function): Callback to invoke after processing
        """
        logger.info("Analyzing files for duplicates")
        
        try:
            duplicate_results = self.duplicate_finder.analyze_dataframe(self.scan_data)
            self.analysis_results['duplicates'] = duplicate_results[duplicate_results['is_duplicate'] == True]
            
            logger.info(f"Found {len(self.analysis_results['duplicates'])} files in duplicate groups")
            
            # Invoke the callback
            if callback:
                callback(self.analysis_results['duplicates'])
                
        except Exception as e:
            logger.error(f"Error analyzing duplicates: {e}")
            
    def _analyze_pii(self, callback=None):
        """
        Analyze files for potential PII
        
        Args:
            callback (function): Callback to invoke after processing
        """
        logger.info("Analyzing files for potential PII (placeholder)")
        
        try:
            pii_results = self.pii_detector.analyze_dataframe(self.scan_data)
            self.analysis_results['pii'] = pii_results[pii_results['potential_pii'] == True]
            
            logger.info(f"Found {len(self.analysis_results['pii'])} files with potential PII")
            
            # Invoke the callback
            if callback:
                callback(self.analysis_results['pii'])
                
        except Exception as e:
            logger.error(f"Error analyzing PII: {e}")
            
    def preview_cleaning(self, clean_options):
        """
        Generate a preview of cleaning operations
        
        Args:
            clean_options (dict): Options controlling cleaning behavior
            
        Returns:
            dict: Preview information
        """
        return self.data_cleaner.preview_fixes(self.analysis_results, clean_options)
        
    def start_cleaning(self, target_folder, clean_options, callbacks=None):
        """
        Start cleaning data based on analysis results
        
        Args:
            target_folder (str): Target folder for cleaned files
            clean_options (dict): Options controlling cleaning behavior
            callbacks (dict): Dictionary of callback functions
        """
        if not self.analysis_results:
            logger.warning("No analysis results to process")
            return
            
        # Default callbacks
        if callbacks is None:
            callbacks = {}
            
        # Start the cleaning process
        self.data_cleaner.start_cleaning(
            self.analysis_results,
            target_folder,
            clean_options,
            progress_callback=callbacks.get('progress'),
            status_callback=callbacks.get('status'),
            error_callback=callbacks.get('error'),
            file_processed_callback=callbacks.get('file_processed'),
            finished_callback=lambda cleaned_files: self._cleaning_completed(cleaned_files, callbacks.get('cleaning_completed'))
        )
        
    def _cleaning_completed(self, cleaned_files, callback=None):
        """
        Handle cleaning completion
        
        Args:
            cleaned_files (dict): Dictionary mapping original paths to cleaned paths
            callback (function): Callback to invoke after processing
        """
        self.cleaned_files = cleaned_files
        
        # Invoke the callback
        if callback:
            callback(cleaned_files)
            
    def stop_scanning(self):
        """Stop an ongoing scan"""
        self.scanner.stop_scan()
        
    def stop_cleaning(self):
        """Stop an ongoing cleaning operation"""
        self.data_cleaner.stop_cleaning()
        
    def get_scan_data(self):
        """
        Get the scan results
        
        Returns:
            pandas.DataFrame: Scan results
        """
        return self.scan_data
        
    def get_analysis_results(self):
        """
        Get the analysis results
        
        Returns:
            dict: Analysis results
        """
        return self.analysis_results
        
    def get_cleaned_files(self):
        """
        Get the cleaned files
        
        Returns:
            dict: Dictionary mapping original paths to cleaned paths
        """
        return self.cleaned_files
        
    def clean_and_upload(self, clean_options, sharepoint_config, callbacks=None):
        """
        Clean data and upload directly to SharePoint
        
        Args:
            clean_options (dict): Options controlling cleaning behavior
            sharepoint_config (dict): SharePoint configuration
            callbacks (dict): Dictionary of callback functions
            
        This is a placeholder for the automatic mode
        """
        # Create a temporary directory for cleaned files
        temp_dir = tempfile.mkdtemp(prefix="sharepoint_migration_")
        logger.info(f"Created temporary directory: {temp_dir}")
        
        # Default callbacks
        if callbacks is None:
            callbacks = {}
            
        # Start the cleaning process with a custom completion callback
        self.data_cleaner.start_cleaning(
            self.analysis_results,
            temp_dir,
            clean_options,
            progress_callback=callbacks.get('progress'),
            status_callback=callbacks.get('status'),
            error_callback=callbacks.get('error'),
            file_processed_callback=callbacks.get('file_processed'),
            finished_callback=lambda cleaned_files: self._upload_to_sharepoint(
                cleaned_files, 
                sharepoint_config, 
                callbacks
            )
        )
        
    def _upload_to_sharepoint(self, cleaned_files, sharepoint_config, callbacks):
        """
        Upload cleaned files to SharePoint
        
        Args:
            cleaned_files (dict): Dictionary mapping original paths to cleaned paths
            sharepoint_config (dict): SharePoint configuration
            callbacks (dict): Dictionary of callback functions
            
        This is a placeholder for the SharePoint upload functionality
        """
        logger.info("SharePoint upload is a placeholder in this version")
        
        # Store the cleaned files
        self.cleaned_files = cleaned_files
        
        # Simulate completion
        if callbacks.get('cleaning_completed'):
            callbacks['cleaning_completed'](cleaned_files)
            
        # Simulate upload completion
        if callbacks.get('upload_completed'):
            callbacks['upload_completed'](cleaned_files)