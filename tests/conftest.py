# tests/conftest.py
import pytest
import os
import sys
import shutil
import tempfile

# Add the project root to the Python path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_dir():
    """Return the path to the test_sharepoint_data directory."""
    # Adjust this path if your test directory is in a different location
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_sharepoint_data'))
    if not os.path.exists(test_dir):
        pytest.fail(f"Test directory not found: {test_dir}. Run create_test_dir.py first.")
    return test_dir

@pytest.fixture
def output_dir():
    """Create a temporary directory for output files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after tests
    shutil.rmtree(temp_dir)

@pytest.fixture
def normal_files_dir(test_dir):
    """Return the path to the normal files directory."""
    return os.path.join(test_dir, "normal_files")

@pytest.fixture
def illegal_chars_dir(test_dir):
    """Return the path to the directory with illegal character files."""
    return os.path.join(test_dir, "illegal_characters")

@pytest.fixture
def long_paths_dir(test_dir):
    """Return the path to the directory with long path files."""
    return os.path.join(test_dir, "long_paths")

@pytest.fixture
def duplicates_dir(test_dir):
    """Return the path to the directory with duplicate files."""
    return os.path.join(test_dir, "duplicates")

@pytest.fixture
def pii_dir(test_dir):
    """Return the path to the directory with PII data files."""
    return os.path.join(test_dir, "pii_data")

@pytest.fixture
def spaces_dir(test_dir):
    """Return the path to the directory with spaces and special characters."""
    return os.path.join(test_dir, "spaces and special chars")

@pytest.fixture
def complex_dir(test_dir):
    """Return the path to the complex mixed issues directory."""
    return os.path.join(test_dir, "complex_mixed_issues")