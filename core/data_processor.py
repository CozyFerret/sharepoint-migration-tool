"""
Enhanced Data Processor for SharePoint Migration Cleanup Tool.
Supports both destructive and non-destructive operations with extended options.
"""

import os
import logging
import tempfile
import pandas as pd
import threading
import shutil
from pathlib import Path

from core.scanner import Scanner
from core.analyzers.name_validator import SharePointNameValidator
from core.analyzers.path_analyzer import PathAnalyzer
from core.analyzers.duplicate_finder import DuplicateFinder
from core.analyzers.pii_detector import PIIDetector
from core.fixers.name_fixer import NameFixer
from core.fixers.path_shortener import PathShortener
from core.fixers.deduplicator import Deduplicator

logger = logging.getLogger('sharepoint_migration_tool')

class DataProcessor:
    """Integrates scanning, analysis, and cleaning operations with extended options"""
    
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
        
        # Initialize fixers
        self.name_fixer = NameFixer(self.config)
        self.path_shortener = PathShortener(self.config)
        self.deduplicator = Deduplicator(self.config)
        
        # Store state
        self.scan_data = None
        self.analysis_results = {}
        self.cleaned_files = {}
        
        # Thread tracking
        self.scan_thread = None
        self.analysis_thread = None
        self.cleaning_thread = None
        
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
        Handle scan completion and prepare results for UI components
        
        Args:
            results (dict): Scan results
            callback (function): Callback to invoke after processing
        """
        # Convert results to pandas DataFrame if needed
        self._process_scan_results(results)
        
        # Store the full dataset in the analysis results
        self.analysis_results['all_files'] = self.scan_data
        
        # Create a complete results dictionary with all required keys
        complete_results = {}
        
        # First add raw scan data if it's a dictionary
        if isinstance(results, dict):
            complete_results.update(results)
        
        # Add core metrics that UI components expect
        complete_results['scan_data'] = self.scan_data  
        complete_results['files_df'] = self.scan_data
        
        # Make sure all required metrics are present with proper defaults
        if 'total_files' not in complete_results:
            complete_results['total_files'] = len(self.scan_data) if self.scan_data is not None else 0
            
        if 'total_folders' not in complete_results:
            complete_results['total_folders'] = results.get('total_folders', 0) if isinstance(results, dict) else 0
            
        if 'total_size' not in complete_results:
            if self.scan_data is not None:
                if 'size_bytes' in self.scan_data.columns:
                    complete_results['total_size'] = self.scan_data['size_bytes'].sum()
                elif 'size' in self.scan_data.columns:
                    complete_results['total_size'] = self.scan_data['size'].sum()
                else:
                    complete_results['total_size'] = 0
            else:
                complete_results['total_size'] = 0
                
        if 'avg_path_length' not in complete_results:
            if self.scan_data is not None and 'path_length' in self.scan_data.columns:
                complete_results['avg_path_length'] = int(self.scan_data['path_length'].mean())
            else:
                complete_results['avg_path_length'] = 0
                
        if 'max_path_length' not in complete_results:
            if self.scan_data is not None and 'path_length' in self.scan_data.columns:
                complete_results['max_path_length'] = int(self.scan_data['path_length'].max())
            else:
                complete_results['max_path_length'] = 0
                
        if 'total_issues' not in complete_results:
            if self.scan_data is not None and 'issue_count' in self.scan_data.columns:
                complete_results['total_issues'] = self.scan_data['issue_count'].sum()
            elif isinstance(results, dict) and 'issues' in results:
                complete_results['total_issues'] = len(results['issues'])
            else:
                complete_results['total_issues'] = 0
        
        # Generate file types distribution if not present
        if 'file_types' not in complete_results or not complete_results.get('file_types'):
            file_types = {}
            if self.scan_data is not None:
                for _, row in self.scan_data.iterrows():
                    ext = ''
                    if 'extension' in row:
                        ext = row['extension']
                    elif 'filename' in row:
                        ext = os.path.splitext(row['filename'])[1].lower()
                    elif 'name' in row:
                        ext = os.path.splitext(row['name'])[1].lower()
                    
                    if ext not in file_types:
                        file_types[ext] = 0
                    file_types[ext] += 1
            complete_results['file_types'] = file_types
        
        # Generate path length distribution if not present
        if 'path_length_distribution' not in complete_results or not complete_results.get('path_length_distribution'):
            distribution = {50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0}
            if self.scan_data is not None:
                path_length_col = None
                for col in ['path_length', 'full_path', 'path']:
                    if col in self.scan_data.columns:
                        path_length_col = col
                        break
                        
                if path_length_col:
                    for _, row in self.scan_data.iterrows():
                        length = row[path_length_col]
                        if path_length_col != 'path_length':
                            length = len(length)
                        
                        for bin_val in sorted(distribution.keys()):
                            if length <= bin_val:
                                distribution[bin_val] += 1
                                break
                                
            complete_results['path_length_distribution'] = distribution
        
        # Ensure issues are properly formatted
        if 'issues' not in complete_results:
            if self.analysis_results.get('path_issues') is not None:
                issues = self.analysis_results['path_issues'].to_dict('records')
                if 'name_issues' in self.analysis_results:
                    issues.extend(self.analysis_results['name_issues'].to_dict('records'))
                if 'duplicates' in self.analysis_results:
                    issues.extend(self.analysis_results['duplicates'].to_dict('records'))
                complete_results['issues'] = issues
            else:
                complete_results['issues'] = []
        
        # Invoke the callback with the fully populated results
        if callback:
            callback(complete_results)

    def _process_scan_results(self, results):
        """
        Process raw scan results into pandas DataFrame
        
        Args:
            results (dict): Raw scan results
        """
        # Check if results is already a DataFrame
        if isinstance(results, pd.DataFrame):
            self.scan_data = results
            return
            
        # Handle various possible formats of results
        if isinstance(results, dict):
            # Check if results have a files array
            if 'files' in results and isinstance(results['files'], list):
                self.scan_data = pd.DataFrame(results['files'])
                return
                
            # Check if results have a files_df DataFrame
            if 'files_df' in results and isinstance(results['files_df'], pd.DataFrame):
                self.scan_data = results['files_df']
                return
                
            # Check if results have a scan_data DataFrame
            if 'scan_data' in results and isinstance(results['scan_data'], pd.DataFrame):
                self.scan_data = results['scan_data']
                return
                
            # Extract files from file_structure if present
            if 'file_structure' in results and isinstance(results['file_structure'], dict):
                file_list = []
                
                # Extract files from file_structure
                for dir_path, dir_data in results['file_structure'].items():
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
                return
        
        # If we get here, create an empty DataFrame with expected columns
        self.scan_data = pd.DataFrame(columns=['path', 'name', 'size', 'extension', 'is_folder'])
        
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
    
    def start_cleaning(self, source_dir, target_dir, clean_options=None, callbacks=None):
        """
        Start cleaning data based on analysis results
        
        Args:
            source_dir (str): Source directory with original files
            target_dir (str): Target directory for cleaned files (not used in destructive mode)
            clean_options (dict): Options controlling cleaning behavior
            callbacks (dict): Dictionary of callback functions
        """
        # Default clean options
        if clean_options is None:
            clean_options = {
                'fix_names': True,
                'fix_paths': True,
                'remove_duplicates': False,
                'destructive_mode': False,
                'preserve_timestamps': True,
                'ignore_hidden': True
            }
            
        # Default callbacks
        if callbacks is None:
            callbacks = {}
        
        # Set source directory for scanning if not already done
        if self.scan_data is None:
            self.start_scan(source_dir, callbacks={
                'scan_completed': lambda results: self.analyze_data(callbacks={
                    'analysis_completed': lambda analysis_results: self._start_cleaning_process(
                        source_dir, target_dir, clean_options, callbacks
                    )
                })
            })
        else:
            # Start cleaning process directly
            self._start_cleaning_process(source_dir, target_dir, clean_options, callbacks)
    
    def _start_cleaning_process(self, source_dir, target_dir, clean_options, callbacks):
        """
        Start the actual cleaning process after scanning and analysis
        
        Args:
            source_dir (str): Source directory with original files
            target_dir (str): Target directory for cleaned files (not used in destructive mode)
            clean_options (dict): Options controlling cleaning behavior
            callbacks (dict): Dictionary of callback functions
        """
        # Check if we're in destructive mode
        destructive_mode = clean_options.get('destructive_mode', False)
        
        if destructive_mode:
            logger.warning("Running in destructive mode - original files will be modified")
            # In destructive mode, we don't need a target directory (modifications are in-place)
            
            # Log a warning message about destructive operations
            logger.warning("DESTRUCTIVE MODE: Original files will be modified directly")
            
            # Check source directory exists
            if not os.path.isdir(source_dir):
                error_msg = f"Source directory does not exist: {source_dir}"
                logger.error(error_msg)
                if 'error' in callbacks:
                    callbacks['error'](error_msg)
                return
        else:
            # Non-destructive mode, check target directory
            if not target_dir:
                error_msg = "Target directory not specified for non-destructive mode"
                logger.error(error_msg)
                if 'error' in callbacks:
                    callbacks['error'](error_msg)
                return
                
            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)
        
        # Start the cleaning thread
        self.cleaning_thread = threading.Thread(
            target=self._cleaning_thread,
            args=(source_dir, target_dir, clean_options, callbacks)
        )
        self.cleaning_thread.daemon = True
        self.cleaning_thread.start()
    
    def _cleaning_thread(self, source_dir, target_dir, clean_options, callbacks):
        """
        Thread for running the cleaning process
        
        Args:
            source_dir (str): Source directory with original files
            target_dir (str): Target directory for cleaned files (not used in destructive mode)
            clean_options (dict): Options controlling cleaning behavior
            callbacks (dict): Dictionary of callback functions
        """
        try:
            # Check if we need to perform analysis
            if not self.analysis_results:
                logger.info("No analysis results found, running analysis")
                
                # Perform analysis first
                self.analyze_data(callbacks={
                    'analysis_completed': lambda results: self._perform_cleaning(
                        source_dir, target_dir, clean_options, callbacks
                    )
                })
            else:
                # Perform cleaning directly
                self._perform_cleaning(source_dir, target_dir, clean_options, callbacks)
                
        except Exception as e:
            logger.error(f"Error in cleaning thread: {e}")
            
            if 'error' in callbacks:
                callbacks['error'](str(e))
    
    def _perform_cleaning(self, source_dir, target_dir, clean_options, callbacks):
        """
        Perform the actual cleaning operations
        
        Args:
            source_dir (str): Source directory with original files
            target_dir (str): Target directory for cleaned files (not used in destructive mode)
            clean_options (dict): Options controlling cleaning behavior
            callbacks (dict): Dictionary of callback functions
        """
        logger.info("Starting cleaning operations")
        
        # Extract options
        fix_names = clean_options.get('fix_names', True)
        fix_paths = clean_options.get('fix_paths', True)
        remove_duplicates = clean_options.get('remove_duplicates', False)
        destructive_mode = clean_options.get('destructive_mode', False)
        preserve_timestamps = clean_options.get('preserve_timestamps', True)
        ignore_hidden = clean_options.get('ignore_hidden', True)
        
        # Progress tracking
        total_files = len(self.scan_data) if self.scan_data is not None else 0
        processed_files = 0
        issues_fixed = 0
        
        # Check if we have issues to fix
        have_name_issues = 'name_issues' in self.analysis_results and len(self.analysis_results['name_issues']) > 0
        have_path_issues = 'path_issues' in self.analysis_results and len(self.analysis_results['path_issues']) > 0
        have_duplicates = 'duplicates' in self.analysis_results and len(self.analysis_results['duplicates']) > 0
        
        # Update initial progress
        if 'progress' in callbacks:
            callbacks['progress'](processed_files, total_files)
        
        # Process files
        try:
            # Get list of files to process
            files_to_process = []
            
            if self.scan_data is not None:
                for _, row in self.scan_data.iterrows():
                    # Skip folders
                    if row.get('is_folder', False):
                        continue
                    
                    # Skip hidden files if requested
                    if ignore_hidden and os.path.basename(row['path']).startswith('.'):
                        continue
                    
                    files_to_process.append(row['path'])
            
            # Update total for progress tracking
            total_files = len(files_to_process)
            
            # Process each file
            for file_path in files_to_process:
                # Check if the file exists
                if not os.path.exists(file_path):
                    logger.warning(f"File not found: {file_path}")
                    continue
                
                # Check if this file has issues
                has_name_issue = have_name_issues and file_path in self.analysis_results['name_issues']['path'].values
                has_path_issue = have_path_issues and file_path in self.analysis_results['path_issues']['path'].values
                is_duplicate = have_duplicates and file_path in self.analysis_results['duplicates']['path'].values
                
                needs_fixing = (fix_names and has_name_issue) or (fix_paths and has_path_issue) or (remove_duplicates and is_duplicate)
                
                # Skip if no issues to fix
                if not needs_fixing:
                    # In non-destructive mode, we still need to copy the file
                    if not destructive_mode:
                        # Create target path
                        rel_path = os.path.relpath(file_path, source_dir)
                        dest_path = os.path.join(target_dir, rel_path)
                        
                        # Create target directory
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        
                        # Copy the file
                        shutil.copy2(file_path, dest_path)
                        
                        # Store in cleaned files
                        self.cleaned_files[file_path] = dest_path
                
                # Fix issues if needed
                elif destructive_mode:
                    # Destructive mode - fix in place
                    fixed = False
                    
                    # Fix name issues
                    if fix_names and has_name_issue:
                        new_name = self.name_fixer.fix_name(os.path.basename(file_path))
                        if new_name != os.path.basename(file_path):
                            # Create new path
                            new_path = os.path.join(os.path.dirname(file_path), new_name)
                            
                            # Rename the file
                            os.rename(file_path, new_path)
                            logger.info(f"Renamed: {file_path} -> {new_path}")
                            
                            # Update file_path for subsequent operations
                            file_path = new_path
                            fixed = True
                            issues_fixed += 1
                    
                    # Fix path issues
                    if fix_paths and has_path_issue:
                        if len(file_path) > 256:  # SharePoint limit
                            # Create shortened path
                            shortened_path = self.path_shortener.shorten_path(file_path)
                            
                            if shortened_path != file_path:
                                # Create target directory
                                os.makedirs(os.path.dirname(shortened_path), exist_ok=True)
                                
                                # Move the file
                                shutil.move(file_path, shortened_path)
                                logger.info(f"Shortened path: {file_path} -> {shortened_path}")
                                
                                # Update file_path for subsequent operations
                                file_path = shortened_path
                                fixed = True
                                issues_fixed += 1
                    
                    # Handle duplicates
                    if remove_duplicates and is_duplicate:
                        # Find the original in the duplicate group
                        duplicate_group = self.analysis_results['duplicates'][
                            self.analysis_results['duplicates']['path'] == file_path
                        ]
                        
                        if not duplicate_group.empty:
                            group_id = duplicate_group.iloc[0]['duplicate_group']
                            group_files = self.analysis_results['duplicates'][
                                self.analysis_results['duplicates']['duplicate_group'] == group_id
                            ]
                            
                            # Find the original file (usually the first in the group)
                            original_file = None
                            for _, row in group_files.iterrows():
                                if row['is_original']:
                                    original_file = row['path']
                                    break
                            
                            # If this is not the original and we found the original
                            if not duplicate_group.iloc[0]['is_original'] and original_file:
                                # Check if the original exists
                                if os.path.exists(original_file):
                                    # Remove the duplicate
                                    os.remove(file_path)
                                    logger.info(f"Removed duplicate: {file_path} (original: {original_file})")
                                    fixed = True
                                    issues_fixed += 1
                    
                    # Store in cleaned files map if any fixes were applied
                    if fixed:
                        self.cleaned_files[file_path] = file_path
                
                else:
                    # Non-destructive mode - create fixed copy
                    fixed_path = file_path
                    fixed = False
                    
                    # Fix name issues
                    if fix_names and has_name_issue:
                        name_without_ext, ext = os.path.splitext(os.path.basename(fixed_path))
                        fixed_name = self.name_fixer.fix_name(name_without_ext) + ext
                        if fixed_name != os.path.basename(fixed_path):
                            # Update the path
                            fixed_path = os.path.join(os.path.dirname(fixed_path), fixed_name)
                            fixed = True
                            issues_fixed += 1
                    
                    # Fix path issues
                    if fix_paths and has_path_issue:
                        if len(fixed_path) > 256:  # SharePoint limit
                            # Create shortened path relative to target directory
                            rel_path = os.path.relpath(fixed_path, source_dir)
                            target_path = os.path.join(target_dir, rel_path)
                            
                            if len(target_path) > 256:
                                shortened_path = self.path_shortener.shorten_path(target_path)
                                fixed_path = shortened_path
                                fixed = True
                                issues_fixed += 1
                    
                    # Create relative path for copying
                    rel_path = os.path.relpath(file_path, source_dir)
                    
                    # Handle duplicates
                    skip_copy = False
                    if remove_duplicates and is_duplicate:
                        # Find the original in the duplicate group
                        duplicate_group = self.analysis_results['duplicates'][
                            self.analysis_results['duplicates']['path'] == file_path
                        ]
                        
                        if not duplicate_group.empty:
                            # Skip if this is not the original file
                            if not duplicate_group.iloc[0]['is_original']:
                                skip_copy = True
                                fixed = True
                                issues_fixed += 1
                    
                    if not skip_copy:
                        # Determine target path
                        if fixed:
                            # Use the fixed path
                            dest_path = fixed_path
                        else:
                            # Create default target path
                            dest_path = os.path.join(target_dir, rel_path)
                        
                        # Create target directory
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        
                        # Copy the file
                        if preserve_timestamps:
                            shutil.copy2(file_path, dest_path)
                        else:
                            shutil.copy(file_path, dest_path)
                        
                        # Store in cleaned files
                        self.cleaned_files[file_path] = dest_path
                
                # Update progress
                processed_files += 1
                if 'progress' in callbacks and processed_files % 10 == 0:  # Update every 10 files
                    callbacks['progress'](processed_files, total_files)
            
            # Final progress update
            if 'progress' in callbacks:
                callbacks['progress'](processed_files, total_files)
            
            # Call completion callback
            if 'cleaning_completed' in callbacks:
                result = {
                    'success': True,
                    'total_processed': processed_files,
                    'issues_fixed': issues_fixed,
                    'destructive_mode': destructive_mode
                }
                callbacks['cleaning_completed'](result)
                
        except Exception as e:
            logger.error(f"Error during cleaning: {e}")
            
            if 'error' in callbacks:
                callbacks['error'](str(e))
    
    def clean_and_upload(self, source_dir, sharepoint_config, clean_options=None, callbacks=None):
        """
        Clean data and upload directly to SharePoint
        
        Args:
            source_dir (str): Source directory with original files
            sharepoint_config (dict): SharePoint configuration
            clean_options (dict): Options controlling cleaning behavior
            callbacks (dict): Dictionary of callback functions
        """
        # Default clean options
        if clean_options is None:
            clean_options = {
                'fix_names': True,
                'fix_paths': True,
                'remove_duplicates': False,
                'destructive_mode': False,
                'preserve_timestamps': True,
                'ignore_hidden': True
            }
            
        # Default callbacks
        if callbacks is None:
            callbacks = {}
        
        # Create a temporary directory for cleaned files (if not in destructive mode)
        if not clean_options.get('destructive_mode', False):
            temp_dir = tempfile.mkdtemp(prefix="sharepoint_migration_")
        else:
            # In destructive mode, modifications happen in-place
            temp_dir = None
        
        logger.info(f"Starting clean and upload: {'Destructive' if clean_options.get('destructive_mode', False) else 'Non-destructive'} mode")
        
        # Define callbacks for cleaning process
        def cleaning_completed(result):
            logger.info(f"Cleaning completed: {result}")
            
            # Only upload if cleaning was successful
            if result.get('success', False):
                self._upload_to_sharepoint(
                    source_dir, 
                    temp_dir,
                    sharepoint_config, 
                    clean_options,
                    callbacks
                )
            else:
                if 'cleaning_completed' in callbacks:
                    callbacks['cleaning_completed'](result)
        
        # Start cleaning process
        if temp_dir:
            # Non-destructive mode - clean to temp directory then upload
            self.start_cleaning(
                source_dir=source_dir,
                target_dir=temp_dir,
                clean_options=clean_options,
                callbacks={
                    'progress': callbacks.get('progress'),
                    'error': callbacks.get('error'),
                    'cleaning_completed': cleaning_completed
                }
            )
        else:
            # Destructive mode - clean in place then upload
            self.start_cleaning(
                source_dir=source_dir,
                target_dir=None,  # No target dir in destructive mode
                clean_options=clean_options,
                callbacks={
                    'progress': callbacks.get('progress'),
                    'error': callbacks.get('error'),
                    'cleaning_completed': cleaning_completed
                }
            )
    
    def _upload_to_sharepoint(self, source_dir, temp_dir, sharepoint_config, clean_options, callbacks):
        """
        Upload cleaned files to SharePoint
        
        Args:
            source_dir (str): Original source directory
            temp_dir (str): Temporary directory with cleaned files (None in destructive mode)
            sharepoint_config (dict): SharePoint configuration
            clean_options (dict): Options controlling cleaning behavior
            callbacks (dict): Dictionary of callback functions
        """
        logger.info("Starting SharePoint upload")
        
        # Extract SharePoint configuration
        sp_integration = sharepoint_config.get('integration')
        target_library = sharepoint_config.get('library')
        
        if not sp_integration or not target_library:
            error_msg = "Missing SharePoint integration or target library"
            logger.error(error_msg)
            
            if 'error' in callbacks:
                callbacks['error'](error_msg)
            return
        
        # In destructive mode, upload from the original source
        # In non-destructive mode, upload from the temp directory
        upload_from_dir = source_dir if clean_options.get('destructive_mode', False) else temp_dir
        
        try:
            # Start the upload
            upload_success, upload_issues, upload_stats = sp_integration.upload_directory(
                upload_from_dir, target_library
            )
            
            # Create result
            result = {
                'success': upload_success,
                'issues': upload_issues,
                'stats': upload_stats,
                'destructive_mode': clean_options.get('destructive_mode', False)
            }
            
            # Call completion callback
            if 'cleaning_completed' in callbacks:
                callbacks['cleaning_completed'](result)
                
        except Exception as e:
            logger.error(f"Error during SharePoint upload: {e}")
            
            if 'error' in callbacks:
                callbacks['error'](str(e))
        
        finally:
            # Clean up the temporary directory if one was created
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Removed temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Error removing temporary directory: {e}")
    
    def stop_scanning(self):
        """Stop an ongoing scan"""
        if hasattr(self, 'scanner') and self.scanner:
            self.scanner.requestInterruption()
    
    def stop_cleaning(self):
        """Stop an ongoing cleaning operation"""
        # Set a flag to stop the cleaning thread
        self._stop_cleaning = True
    
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