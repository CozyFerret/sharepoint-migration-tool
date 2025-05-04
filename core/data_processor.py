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
import threading

from core.scanner import Scanner
from core.analyzers.name_validator import SharePointNameValidator
from core.analyzers.path_analyzer import PathAnalyzer
from core.analyzers.duplicate_finder import DuplicateFinder
from core.analyzers.pii_detector import PIIDetector

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
        self.scanner = Scanner(None)  # Initialize without source_folder
        self.name_validator = SharePointNameValidator(self.config)
        self.path_analyzer = PathAnalyzer(self.config)
        self.duplicate_finder = DuplicateFinder(self.config)
        self.pii_detector = PIIDetector(self.config)
        
        # Store state
        self.scan_data = None
        self.analysis_results = {}
        self.cleaned_files = {}
        
        # Thread tracking
        self.scan_thread = None
        self.analysis_thread = None
        
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
        
        # Initialize a new Scanner with the proper source_folder
        self.scanner = Scanner(root_path)
        
        # Connect signals to callbacks
        if 'progress' in callbacks:
            self.scanner.progress_updated.connect(callbacks['progress'])
        
        if 'error' in callbacks:
            self.scanner.error_occurred.connect(callbacks['error'])
        
        # Custom completion handler to transform data
        def on_scan_completed(results):
            self._scan_completed(results, callbacks.get('scan_completed'))
        
        self.scanner.scan_completed.connect(on_scan_completed)
        
        # Start the scanner thread
        self.scanner.start()
        
    def _scan_completed(self, results, callback=None):
        """
        Handle scan completion
        
        Args:
            results (dict): Scan results
            callback (function): Callback to invoke after processing
        """
        # Convert results to pandas DataFrame (if needed)
        self._process_scan_results(results)
        
        # Store the full dataset in the analysis results
        self.analysis_results['all_files'] = self.scan_data
        
        # Invoke the callback
        if callback:
            callback(self.scan_data)
    
    def _process_scan_results(self, results):
        """
        Process raw scan results into pandas DataFrame
        
        Args:
            results (dict): Raw scan results
        """
        # This would collect all files into a flat DataFrame
        file_list = []
        
        # Extract files from file_structure
        for dir_path, dir_data in results.get('file_structure', {}).items():
            # Add files
            for file_info in dir_data.get('files', []):
                file_list.append({
                    'path': file_info.get('path', ''),
                    'name': file_info.get('name', ''),
                    'size': file_info.get('size', 0),
                    'extension': file_info.get('extension', ''),
                    'is_folder': False
                })
            
            # Add folders
            for folder_info in dir_data.get('folders', []):
                file_list.append({
                    'path': folder_info.get('path', ''),
                    'name': folder_info.get('name', ''),
                    'size': 0,
                    'extension': '',
                    'is_folder': True
                })
        
        # Create DataFrame
        self.scan_data = pd.DataFrame(file_list)
        
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
        
        # Run analysis in a separate thread
        self.analysis_thread = threading.Thread(
            target=self._analyze_thread,
            args=(feature_flags, callbacks)
        )
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def _analyze_thread(self, feature_flags, callbacks):
        """Thread for running analysis"""
        try:
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
                
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            
            if callbacks.get('error'):
                callbacks['error'](str(e))
            
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
        
        # Import DataCleaner here to avoid circular imports
        from core.data_cleaner import DataCleaner
        
        # Create data cleaner
        data_cleaner = DataCleaner(self.config)
        
        # Start the cleaning process
        data_cleaner.start_cleaning(
            self.analysis_results,
            target_folder,
            clean_options,
            progress_callback=callbacks.get('progress'),
            status_callback=callbacks.get('status'),
            error_callback=callbacks.get('error'),
            file_processed_callback=callbacks.get('file_processed'),
            finished_callback=lambda cleaned_files: self._cleaning_completed(cleaned_files, callbacks.get('cleaning_completed'))
        )
        
        # Store reference to data cleaner
        self.data_cleaner = data_cleaner
    
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
        if hasattr(self, 'scanner') and self.scanner:
            self.scanner.requestInterruption()
    
    def stop_cleaning(self):
        """Stop an ongoing cleaning operation"""
        if hasattr(self, 'data_cleaner') and self.data_cleaner:
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
        
        # Create a custom completion callback to handle upload
        def cleaning_completed(cleaned_files):
            self._upload_to_sharepoint(
                cleaned_files, 
                sharepoint_config, 
                callbacks
            )
        
        # Start the cleaning process
        self.start_cleaning(
            temp_dir,
            clean_options,
            {
                'progress': callbacks.get('progress'),
                'status': callbacks.get('status'),
                'error': callbacks.get('error'),
                'file_processed': callbacks.get('file_processed'),
                'cleaning_completed': cleaning_completed
            }
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