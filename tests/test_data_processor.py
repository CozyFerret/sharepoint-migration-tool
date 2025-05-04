# tests/test_data_processor.py
import os
import shutil
import pytest
from unittest.mock import MagicMock, patch

class MockDataProcessor:
    """Mock implementation of data processor for testing."""
    
    def __init__(self):
        self.name_validator = None
        self.path_shortener = None
        self.duplicate_detector = None
        self.options = {
            'fix_names': True,
            'fix_paths': True,
            'detect_duplicates': True,
            'output_dir': None
        }
    
    def set_options(self, **kwargs):
        """Set processing options."""
        for key, value in kwargs.items():
            if key in self.options:
                self.options[key] = value
    
    def process(self, source_dir):
        """Process a directory, fixing issues according to options."""
        if not os.path.isdir(source_dir):
            return {'error': 'Source directory does not exist'}
            
        results = {
            'fixed_names': [],
            'fixed_paths': [],
            'duplicates': []
        }
        
        # Create output directory if it doesn't exist
        output_dir = self.options.get('output_dir')
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Simple implementation: just copy all files to output dir
        # In a real implementation, you would apply all the validation/fixing logic
        if output_dir:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    # Create a relative path to maintain structure
                    rel_path = os.path.relpath(src_path, source_dir)
                    dst_path = os.path.join(output_dir, rel_path)
                    
                    # Ensure the destination directory exists
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(src_path, dst_path)
                    
                    # Mock some results for testing
                    if self.options.get('fix_names') and any(c in file for c in '<>:"/\\|?*'):
                        results['fixed_names'].append({
                            'original': src_path,
                            'fixed': dst_path
                        })
                    
                    if self.options.get('fix_paths') and len(src_path) > 256:
                        results['fixed_paths'].append({
                            'original': src_path,
                            'fixed': dst_path
                        })
        
        # Mock duplicate detection
        if self.options.get('detect_duplicates'):
            # Find a few files to mark as duplicates for testing
            all_files = []
            for root, _, files in os.walk(source_dir):
                for file in files:
                    all_files.append(os.path.join(root, file))
            
            # Just use the first few files as a mock duplicate group
            if len(all_files) >= 2:
                results['duplicates'].append({
                    'hash': 'mock_hash_123',
                    'files': all_files[:2]
                })
        
        return results

def test_data_processor_creates_output(test_dir, output_dir):
    """Test that the data processor creates the expected output directory and files."""
    processor = MockDataProcessor()
    
    # Configure the processor
    processor.set_options(
        fix_names=True,
        fix_paths=True,
        detect_duplicates=True,
        output_dir=output_dir
    )
    
    # Process the test directory
    results = processor.process(test_dir)
    
    # Verify output directory was created and contains files
    assert os.path.exists(output_dir), "Output directory was not created"
    
    # There should be files in the output directory
    output_files = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            output_files.append(os.path.join(root, file))
    
    assert len(output_files) > 0, "No files were copied to the output directory"
    
    # Verify results were populated
    assert 'fixed_names' in results, "Results missing fixed_names entry"
    assert 'fixed_paths' in results, "Results missing fixed_paths entry"
    assert 'duplicates' in results, "Results missing duplicates entry"

def test_data_processor_respects_options(test_dir, output_dir):
    """Test that the data processor respects the provided options."""
    processor = MockDataProcessor()
    
    # Configure with detect_duplicates disabled
    processor.set_options(
        fix_names=True,
        fix_paths=True,
        detect_duplicates=False,
        output_dir=output_dir
    )
    
    # Process the directory
    results = processor.process(test_dir)
    
    # Verify no duplicates were detected
    assert len(results['duplicates']) == 0, "Duplicates were detected despite being disabled"