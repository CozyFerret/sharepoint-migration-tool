import os
import hashlib
import shutil
import random
import string
import argparse

def create_test_directory(base_dir, complexity='normal'):
    """
    Create a test directory structure with various SharePoint migration challenges.
    
    Args:
        base_dir (str): The base directory where to create the test structure
        complexity (str): Level of complexity - 'simple', 'normal', or 'complex'
    """
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    os.makedirs(base_dir)
    print(f"Created base directory: {base_dir}")
    
    # Create normal files
    create_normal_files(base_dir)
    
    # Create files with illegal characters
    create_files_with_illegal_chars(base_dir)
    
    # Create files with long paths
    create_long_path_files(base_dir, complexity)
    
    # Create duplicate files
    create_duplicate_files(base_dir, complexity)
    
    # Create files with PII (mock)
    create_files_with_pii(base_dir)
    
    # Create files with spaces and special characters
    create_files_with_spaces(base_dir)
    
    # If complex mode, create a very messy structure
    if complexity == 'complex':
        create_complex_structure(base_dir)
    
    print(f"Test directory created successfully at: {base_dir}")

def create_normal_files(base_dir):
    """Create a set of normal files that don't violate any SharePoint rules."""
    normal_dir = os.path.join(base_dir, "normal_files")
    os.makedirs(normal_dir)
    
    # Create some text files
    for i in range(5):
        with open(os.path.join(normal_dir, f"document_{i}.txt"), "w") as f:
            f.write(f"This is test document {i}")
    
    # Create some mock document files
    for i in range(3):
        with open(os.path.join(normal_dir, f"report_{i}.docx"), "wb") as f:
            f.write(b"Mock DOCX content")
            
    # Create a subfolder with more files
    sub_dir = os.path.join(normal_dir, "subfolder")
    os.makedirs(sub_dir)
    for i in range(3):
        with open(os.path.join(sub_dir, f"subfile_{i}.txt"), "w") as f:
            f.write(f"This is a file in a subfolder {i}")
            
    print("Created normal files")

def create_files_with_illegal_chars(base_dir):
    """Create files with characters that are illegal in SharePoint."""
    illegal_dir = os.path.join(base_dir, "illegal_characters")
    os.makedirs(illegal_dir)
    
    # SharePoint illegal characters: " * : < > ? / \ |
    illegal_filenames = [
        "file_with_asterisk*.txt",
        "file_with_quote\".txt",
        "file_with_colon:.txt",
        "file_with_less_than<.txt",
        "file_with_greater_than>.txt",
        "file_with_question?.txt",
        "file_with_slash/.txt",
        "file_with_backslash\\.txt",
        "file_with_pipe|.txt",
        "file_with_trailing_space .txt",
        "file_with_trailing_dot.",
        "file_with_multiple_illegal_*:?<>|.txt"
    ]
    
    for filename in illegal_filenames:
        try:
            # This will fail on some platforms with certain illegal characters
            # We use try/except to handle this
            with open(os.path.join(illegal_dir, filename), "w") as f:
                f.write(f"This file has an illegal character: {filename}")
            print(f"Created file with illegal character: {filename}")
        except (OSError, IOError) as e:
            # For files that can't be created due to OS restrictions,
            # create a proxy file with a description
            safe_name = "".join(c if c.isalnum() or c in ".-_ " else "_" for c in filename)
            with open(os.path.join(illegal_dir, f"proxy_{safe_name}"), "w") as f:
                f.write(f"This file represents {filename} which couldn't be created directly")
            print(f"Created proxy for file with illegal character: {filename}")
    
    print("Created files with illegal characters")

def create_long_path_files(base_dir, complexity):
    """Create files with paths that exceed SharePoint's 256 character limit."""
    long_path_dir = os.path.join(base_dir, "long_paths")
    os.makedirs(long_path_dir)
    
    # Create a deep directory structure
    depth = 10 if complexity == 'simple' else 20 if complexity == 'normal' else 30
    
    current_dir = long_path_dir
    for i in range(depth):
        current_dir = os.path.join(current_dir, f"level_{i:02d}_with_somewhat_long_directory_name")
        os.makedirs(current_dir, exist_ok=True)
        
        # Add files at each level
        with open(os.path.join(current_dir, f"file_at_level_{i}.txt"), "w") as f:
            f.write(f"This file is at depth level {i}")
            
    # Create a file with a very long name at the deepest level
    long_filename = "extremely_" + "long_" * 20 + "filename.txt"
    with open(os.path.join(current_dir, long_filename), "w") as f:
        f.write("This file has a very long name")
        
    # Calculate and print the longest path
    longest_path = os.path.join(current_dir, long_filename)
    print(f"Created long path files. Longest path is {len(longest_path)} characters: {longest_path}")

def create_duplicate_files(base_dir, complexity):
    """Create duplicate files with identical content but different names/locations."""
    duplicate_dir = os.path.join(base_dir, "duplicates")
    os.makedirs(duplicate_dir)
    
    # Number of duplicate sets to create
    num_sets = 3 if complexity == 'simple' else 5 if complexity == 'normal' else 10
    
    for set_num in range(num_sets):
        # Create a unique content for this set
        content = f"This is duplicate content for set {set_num}\n"
        content += "".join(random.choice(string.ascii_letters) for _ in range(100))
        
        # Create the first file in the set
        with open(os.path.join(duplicate_dir, f"original_{set_num}.txt"), "w") as f:
            f.write(content)
        
        # Create 2-5 duplicates with different names/locations
        num_duplicates = random.randint(2, 5)
        for dup_num in range(num_duplicates):
            # Create some duplicates in subfolders
            if dup_num % 2 == 0:
                subfolder = os.path.join(duplicate_dir, f"subfolder_{set_num}_{dup_num}")
                os.makedirs(subfolder, exist_ok=True)
                path = os.path.join(subfolder, f"duplicate_{set_num}_{dup_num}.txt")
            else:
                path = os.path.join(duplicate_dir, f"duplicate_{set_num}_{dup_num}.txt")
                
            with open(path, "w") as f:
                f.write(content)
                
    print(f"Created {num_sets} sets of duplicate files")

def create_files_with_pii(base_dir):
    """Create files containing mock PII data for testing PII detection."""
    pii_dir = os.path.join(base_dir, "pii_data")
    os.makedirs(pii_dir)
    
    # Mock social security numbers
    with open(os.path.join(pii_dir, "employee_data.txt"), "w") as f:
        f.write("Employee Records\n\n")
        for i in range(5):
            f.write(f"Name: Test Person {i}\n")
            f.write(f"SSN: {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}\n")
            f.write(f"DOB: {random.randint(1, 12)}/{random.randint(1, 28)}/{random.randint(1950, 2000)}\n\n")
    
    # Mock credit card numbers
    with open(os.path.join(pii_dir, "payment_info.txt"), "w") as f:
        f.write("Payment Information\n\n")
        for i in range(3):
            f.write(f"Customer: Customer {i}\n")
            f.write(f"Credit Card: {random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}\n")
            f.write(f"Expiration: {random.randint(1, 12)}/{random.randint(23, 30)}\n\n")
    
    # Mock email addresses
    with open(os.path.join(pii_dir, "contact_list.txt"), "w") as f:
        f.write("Contact List\n\n")
        for i in range(10):
            name = f"person{i}"
            domains = ["example.com", "test.org", "mockmail.net"]
            f.write(f"{name}@{random.choice(domains)}\n")
            
    print("Created files with mock PII data")

def create_files_with_spaces(base_dir):
    """Create files with spaces and other special characters that are allowed but might cause issues."""
    spaces_dir = os.path.join(base_dir, "spaces and special chars")
    os.makedirs(spaces_dir)
    
    filenames = [
        "file with spaces.txt",
        "file-with-hyphens.txt",
        "file_with_underscores.txt",
        "file with trailing space .txt",
        "  file with leading spaces.txt",
        "file with (parentheses).txt",
        "file with [brackets].txt",
        "file with &ampersand.txt",
        "file with 'quotes'.txt",
        "file with multiple   spaces.txt"
    ]
    
    for filename in filenames:
        with open(os.path.join(spaces_dir, filename), "w") as f:
            f.write(f"This file has special characters in its name: {filename}")
            
    print("Created files with spaces and special characters")

def create_complex_structure(base_dir):
    """Create a very complex structure with mixed issues for thorough testing."""
    complex_dir = os.path.join(base_dir, "complex_mixed_issues")
    os.makedirs(complex_dir)
    
    # Create a deeply nested structure with mixed issues
    depth = 15
    current_dir = complex_dir
    
    for i in range(depth):
        # Mix normal and problematic folder names
        if i % 3 == 0:
            current_dir = os.path.join(current_dir, f"level_{i}")
        elif i % 3 == 1:
            current_dir = os.path.join(current_dir, f"level {i} with spaces")
        else:
            try:
                current_dir = os.path.join(current_dir, f"level_{i}*special")
            except (OSError, IOError):
                # If OS doesn't allow, use a fallback
                current_dir = os.path.join(current_dir, f"level_{i}_special")
                
        os.makedirs(current_dir, exist_ok=True)
        
        # Add a mix of files at each level
        # Normal file
        with open(os.path.join(current_dir, f"normal_{i}.txt"), "w") as f:
            f.write(f"Normal file at level {i}")
            
        # File with spaces
        with open(os.path.join(current_dir, f"spaces {i}.txt"), "w") as f:
            f.write(f"File with spaces at level {i}")
            
        # Try to create a file with illegal chars
        try:
            with open(os.path.join(current_dir, f"illegal_{i}?.txt"), "w") as f:
                f.write(f"File with illegal character at level {i}")
        except (OSError, IOError):
            # Create a proxy if OS doesn't allow
            with open(os.path.join(current_dir, f"proxy_illegal_{i}.txt"), "w") as f:
                f.write(f"Proxy for file with illegal character at level {i}")
                
    # Create duplicate content across different parts of the structure
    for i in range(3):
        content = f"Duplicate content set {i}\n" + "x" * 100
        
        # Place duplicates in different parts of the tree
        folders = []
        current = complex_dir
        for j in range(0, depth, 5):
            current = os.path.join(complex_dir, f"level_{j}")
            if os.path.exists(current):
                folders.append(current)
                
        for j, folder in enumerate(folders):
            with open(os.path.join(folder, f"dup_{i}_{j}.txt"), "w") as f:
                f.write(content)
                
    print("Created complex mixed structure")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a test directory for SharePoint migration testing")
    parser.add_argument("--dir", default="test_sharepoint_data", help="Directory to create the test structure in")
    parser.add_argument("--complexity", choices=["simple", "normal", "complex"], default="normal", 
                        help="Complexity level of the test structure")
    
    args = parser.parse_args()
    create_test_directory(args.dir, args.complexity)