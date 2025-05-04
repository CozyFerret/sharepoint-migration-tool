# tests/fixers/test_path_shortener.py
import os
import pytest
from unittest.mock import MagicMock

class MockPathShortener:
    """Mock implementation of path shortening for testing."""
    
    def __init__(self):
        self.max_path_length = 256
    
    def shorten_path(self, path, target_length=None):
        """Shorten a path to the target length."""
        if target_length is None:
            target_length = self.max_path_length
            
        if len(path) <= target_length:
            return path
            
        # Simple implementation: truncate directory names
        dir_name, file_name = os.path.split(path)
        
        # Make sure we have enough space for the file name
        available_length = target_length - len(file_name) - 1  # -1 for the separator
        
        if available_length <= 0:
            # If file name itself is too long, truncate it
            name, ext = os.path.splitext(file_name)
            if len(ext) >= target_length - 5:
                return name[:5]  # Really extreme case
            else:
                return name[:target_length - len(ext) - 1] + ext
        
        # Shorten the directory path
        parts = []
        remaining = dir_name
        
        while remaining and len(os.path.join(*parts, file_name)) > target_length:
            head, tail = os.path.split(remaining)
            
            if not tail:  # Root directory
                break
                
            # Truncate this component if needed
            if len(tail) > 8:
                tail = tail[:6] + '..'
                
            parts.insert(0, tail)
            remaining = head
            
            # Check if we're getting close to target length
            if len(os.path.join(remaining, *parts, file_name)) <= target_length:
                break
                
        # Ensure we don't exceed target length
        shortened_path = os.path.join(remaining, *parts, file_name)
        
        # Final check and emergency truncation
        if len(shortened_path) > target_length:
            drive, path_tail = os.path.splitdrive(shortened_path)
            name, ext = os.path.splitext(file_name)
            
            # Keep drive and extension, truncate the middle
            usable_length = target_length - len(drive) - len(ext)
            shortened_path = drive + path_tail[:usable_length] + ext
            
        return shortened_path

def test_path_shortening(long_paths_dir):
    """Test that paths are properly shortened."""
    shortener = MockPathShortener()
    max_length = 256
    
    # Find some long paths to test
    long_paths = []
    for root, _, files in os.walk(long_paths_dir):
        for file in files:
            path = os.path.join(root, file)
            if len(path) > max_length:
                long_paths.append(path)
    
    if not long_paths:
        pytest.skip("No long paths found for testing")
    
    # Test each long path
    for path in long_paths[:5]:  # Test the first 5 long paths
        shortened = shortener.shorten_path(path, max_length)
        
        # Verify the shortened path meets requirements
        assert len(shortened) <= max_length, f"Shortened path still too long: {len(shortened)} chars"
        
        # Verify file extension is preserved
        assert os.path.splitext(shortened)[1] == os.path.splitext(path)[1], "File extension not preserved"
        
        # Verify drive letter is preserved if present
        if os.path.splitdrive(path)[0]:
            assert os.path.splitdrive(shortened)[0] == os.path.splitdrive(path)[0], "Drive letter not preserved"