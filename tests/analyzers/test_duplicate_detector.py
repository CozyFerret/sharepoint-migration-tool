# tests/analyzers/test_duplicate_detector.py
import os
import hashlib
import pytest
from unittest.mock import MagicMock

class MockDuplicateDetector:
    """Mock implementation of duplicate file detection for testing."""
    
    def __init__(self):
        self.chunk_size = 8192  # 8KB chunks for file reading
    
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of a file."""
        if not os.path.isfile(file_path):
            return None
            
        md5 = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(self.chunk_size), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception as e:
            print(f"Error hashing file {file_path}: {e}")
            return None
    
    def find_duplicates(self, directory):
        """Find duplicate files in a directory."""
        if not os.path.isdir(directory):
            return []
            
        # Track hashes and files
        hashes = {}
        duplicates = []
        
        # Process all files
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = self.get_file_hash(file_path)
                
                if not file_hash:
                    continue
                    
                if file_hash in hashes:
                    # This is a duplicate
                    if len(hashes[file_hash]) == 1:
                        # First duplicate of this file, add the original to the list
                        duplicates.append({
                            'hash': file_hash,
                            'files': [hashes[file_hash][0], file_path]
                        })
                    else:
                        # Additional duplicate, add to existing group
                        for dup_group in duplicates:
                            if dup_group['hash'] == file_hash:
                                dup_group['files'].append(file_path)
                                break
                    
                    # Add to the hash tracking
                    hashes[file_hash].append(file_path)
                else:
                    # First instance of this hash
                    hashes[file_hash] = [file_path]
        
        return duplicates

def test_duplicate_detection(duplicates_dir):
    """Test that duplicate files are correctly identified."""
    detector = MockDuplicateDetector()
    
    # Find duplicates
    duplicate_groups = detector.find_duplicates(duplicates_dir)
    
    # We should have found at least one group of duplicates
    assert len(duplicate_groups) > 0, "No duplicate groups found"
    
    # Verify each group contains actual duplicates
    for group in duplicate_groups:
        # Should have at least 2 files in a duplicate group
        assert len(group['files']) >= 2, f"Duplicate group does not have enough files: {group}"
        
        # Verify all files in a group have the same hash
        first_file_hash = detector.get_file_hash(group['files'][0])
        for file in group['files'][1:]:
            file_hash = detector.get_file_hash(file)
            assert file_hash == first_file_hash, f"Files in duplicate group have different hashes: {file} vs {group['files'][0]}"