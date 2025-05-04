# tests/mock_modules.py
"""Mock implementations of modules for testing."""

class MockPIIDetector:
    """Mock implementation of PIIDetector for testing."""
    
    def __init__(self):
        self.patterns = []
    
    def scan_text(self, text):
        """Mock method to scan text for PII."""
        return []
    
    def scan_file(self, file_path):
        """Mock method to scan a file for PII."""
        return []