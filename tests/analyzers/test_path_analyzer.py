# tests/analyzers/test_path_analyzer.py
import os
import pytest
from core.analyzers.path_analyzer import PathAnalyzer  # Adjust import based on your structure

def test_path_length_detection(long_paths_dir):
    """Test that the path analyzer correctly identifies paths that exceed SharePoint limits."""
    analyzer = PathAnalyzer()
    max_path_length = 256  # SharePoint's path length limit
    
    # Walk through the long paths directory
    too_long_paths = []
    for root, _, files in os.walk(long_paths_dir):
        for filename in files:
            path = os.path.join(root, filename)
            if len(path) > max_path_length:
                too_long_paths.append(path)
    
    # Verify that our manual count matches what the analyzer finds
    scanner_count = 0
    for root, _, files in os.walk(long_paths_dir):
        for filename in files:
            path = os.path.join(root, filename)
            result = analyzer.is_path_too_long(path, max_path_length)
            
            if result:
                scanner_count += 1
                assert len(path) > max_path_length, f"Path incorrectly flagged as too long: {path}"
            else:
                assert len(path) <= max_path_length, f"Path incorrectly flagged as acceptable: {path}"
    
    assert scanner_count == len(too_long_paths), f"Analyzer found {scanner_count} paths too long, expected {len(too_long_paths)}"

def test_path_shortening_suggestions(long_paths_dir):
    """Test that the path analyzer suggests valid shortened paths."""
    analyzer = PathAnalyzer()
    max_path_length = 256
    
    # Test a few of the longest paths
    longest_paths = []
    for root, _, files in os.walk(long_paths_dir):
        for filename in files:
            path = os.path.join(root, filename)
            longest_paths.append((len(path), path))
    
    # Sort by length and get the top 5 longest paths
    longest_paths.sort(reverse=True)
    for _, path in longest_paths[:5]:
        # Only test paths that are actually too long
        if len(path) > max_path_length:
            shortened_path = analyzer.suggest_shorter_path(path, max_path_length)
            
            # Verify the suggested path is shorter than the max length
            assert len(shortened_path) <= max_path_length, f"Suggested path still too long: {shortened_path}"
            
            # Verify the suggested path has the same file extension
            original_ext = os.path.splitext(path)[1]
            shortened_ext = os.path.splitext(shortened_path)[1]
            assert original_ext == shortened_ext, f"File extension changed from {original_ext} to {shortened_ext}"