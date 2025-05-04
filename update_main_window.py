#!/usr/bin/env python3
"""
Update script for main_window.py

This script updates the main_window.py file with the enhanced tab implementations.
It replaces the placeholder tab creation functions with the full implementations.
"""

import os
import sys
import re
import shutil
from datetime import datetime

# Define the path to the main_window.py file
MAIN_WINDOW_PATH = "ui/main_window.py"

# Check if the file exists
if not os.path.exists(MAIN_WINDOW_PATH):
    print(f"Error: Cannot find {MAIN_WINDOW_PATH}")
    print("Please run this script from the project root directory.")
    sys.exit(1)

# Create a backup of the original file
backup_path = f"{MAIN_WINDOW_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
shutil.copy2(MAIN_WINDOW_PATH, backup_path)
print(f"Created backup at {backup_path}")

# Read the original file content
with open(MAIN_WINDOW_PATH, 'r') as f:
    content = f.read()

# Load the enhanced tab implementations
with open("analyze_tab_implementation.py", 'r') as f:
    analyze_tab_impl = f.read()

with open("clean_tab_implementation.py", 'r') as f:
    clean_tab_impl = f.read()

with open("settings_tab_implementation.py", 'r') as f:
    settings_tab_impl = f.read()

# Function to replace a method in the content
def replace_method(content, method_name, new_implementation):
    # Regex pattern to match the method declaration and its body
    pattern = fr'def {method_name}\([^)]*\):.*?(?=\n\s*def|\Z)'
    # Use re.DOTALL to match across multiple lines
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Replace the method with the new implementation
        return content.replace(match.group(0), new_implementation)
    else:
        print(f"Warning: Could not find method {method_name}")
        return content

# Replace the placeholder tab creation methods
content = replace_method(content, "create_analyze_tab", analyze_tab_impl)
content = replace_method(content, "create_clean_tab", clean_tab_impl)
content = replace_method(content, "create_settings_tab", settings_tab_impl)

# Write the updated content back to the file
with open(MAIN_WINDOW_PATH, 'w') as f:
    f.write(content)

print(f"Updated {MAIN_WINDOW_PATH} with enhanced tab implementations")
print("Please check the file for any issues before running the application.")