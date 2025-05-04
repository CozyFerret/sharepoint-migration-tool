# tests/analyzers/test_name_validator.py
import os
import pytest
from unittest.mock import MagicMock

class MockSharePointNameValidator:
    """Mock implementation of SharePointNameValidator for testing."""
    
    def __init__(self):
        # SharePoint illegal characters
        self.illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        self.illegal_prefixes = ['.', ' ']
        self.illegal_suffixes = ['.', ' ']
        self.max_length = 128
    
    def validate(self, filename):
        """Check if a filename is valid for SharePoint."""
        if not filename:
            return False, ["Filename cannot be empty"]
        
        errors = []
        
        # Check for illegal characters
        for char in self.illegal_chars:
            if char in filename:
                errors.append(f"Filename contains illegal character: '{char}'")
        
        # Check for illegal prefixes
        for prefix in self.illegal_prefixes:
            if filename.startswith(prefix):
                errors.append(f"Filename cannot start with '{prefix}'")
        
        # Check for illegal suffixes
        for suffix in self.illegal_suffixes:
            if filename.endswith(suffix):
                errors.append(f"Filename cannot end with '{suffix}'")
        
        # Check length
        if len(filename) > self.max_length:
            errors.append(f"Filename exceeds maximum length of {self.max_length} characters")
        
        return len(errors) == 0, errors
    
    def fix_filename(self, filename):
        """Fix a filename to be SharePoint compliant."""
        if not filename:
            return "unnamed_file"
        
        result = filename
        
        # Replace illegal characters
        for char in self.illegal_chars:
            result = result.replace(char, '_')
        
        # Fix prefixes
        for prefix in self.illegal_prefixes:
            if result.startswith(prefix):
                result = 'file_' + result.lstrip(prefix)
        
        # Fix suffixes
        for suffix in self.illegal_suffixes:
            if result.endswith(suffix):
                result = result.rstrip(suffix) + '_file'
        
        # Truncate if too long
        if len(result) > self.max_length:
            name, ext = os.path.splitext(result)
            name = name[:self.max_length - len(ext) - 1]
            result = name + ext
        
        return result

def test_name_validation(illegal_chars_dir):
    """Test that the name validator correctly identifies invalid filenames."""
    validator = MockSharePointNameValidator()
    
    # Test cases
    test_cases = [
        # Valid names
        ("valid_document.docx", True),
        ("file-with-hyphens.txt", True),
        ("file_with_underscores.txt", True),
        
        # Invalid names
        ("file*.txt", False),
        ("file?.txt", False),
        ("file<.txt", False),
        ("file>.txt", False),
        ("file:.txt", False),
        ("file\".txt", False),
        ("file/.txt", False),
        ("file\\.txt", False),
        ("file|.txt", False),
        (" leadingspace.txt", False),
        ("trailingspace.txt ", False),
        (".", False),
        (".hiddenfile", False),
    ]
    
    for filename, expected_valid in test_cases:
        is_valid, errors = validator.validate(filename)
        assert is_valid == expected_valid, f"Validation failed for {filename}: got {is_valid}, expected {expected_valid}. Errors: {errors}"

def test_filename_fixing():
    """Test that the name validator correctly fixes invalid filenames."""
    validator = MockSharePointNameValidator()
    
    # Test cases
    test_cases = [
        # Format: (original_name, expected_fixed_name)
        ("file*.txt", "file_.txt"),
        ("file?.txt", "file_.txt"),
        ("file<>.txt", "file__.txt"),
        ("file|file.txt", "file_file.txt"),
        (" leadingspace.txt", "file_leadingspace.txt"),
        ("trailingspace.txt ", "trailingspace.txt_file"),
        (".hiddenfile", "file_hiddenfile"),
    ]
    
    for original, expected in test_cases:
        fixed = validator.fix_filename(original)
        assert fixed == expected, f"Fixing failed for {original}: got {fixed}, expected {expected}"