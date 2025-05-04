# core/fixers/name_fixer.py
import os
import re
import unicodedata
import shutil

class NameFixer:
    """Fixes file and folder names with illegal characters, prefixes, or suffixes"""
    
    def __init__(self, strategy="Replace with Underscore"):
        self.strategy = strategy
        
        # SharePoint illegal characters
        self.illegal_chars = r'[\\/:*?"<>|#%&{}+~=]'
        
        # SharePoint reserved names
        self.reserved_names = [
            "CON", "PRN", "AUX", "NUL", 
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        ]
        
        # Illegal prefixes and suffixes
        self.illegal_prefixes = [".~", "_vti_"]
        self.illegal_suffixes = [".files", "_files", "-Dateien", ".data"]
    
    def fix_name(self, file_path):
        """Fix a file name with illegal characters or issues"""
        dir_name, file_name = os.path.split(file_path)
        file_base, file_ext = os.path.splitext(file_name)
        
        # Check if the base name (without extension) is a reserved name
        if file_base.upper() in self.reserved_names:
            file_base = f"SP_{file_base}"
        
        # Fix illegal characters based on selected strategy
        if self.strategy == "Replace with Underscore":
            file_base = re.sub(self.illegal_chars, '_', file_base)
        elif self.strategy == "Remove Characters":
            file_base = re.sub(self.illegal_chars, '', file_base)
        elif self.strategy == "Replace with ASCII Equivalents":
            # Normalize Unicode characters to closest ASCII equivalent
            file_base = unicodedata.normalize('NFKD', file_base)
            file_base = ''.join([c for c in file_base if not unicodedata.combining(c)])
            file_base = re.sub(self.illegal_chars, '_', file_base)
        
        # Fix illegal prefixes
        for prefix in self.illegal_prefixes:
            if file_base.startswith(prefix):
                file_base = f"SP_{file_base[len(prefix):]}"
                break
                
        # Fix illegal suffixes
        for suffix in self.illegal_suffixes:
            if file_base.endswith(suffix):
                file_base = f"{file_base[:-len(suffix)]}_SP"
                break
        
        # Ensure the file name is not too long (max 128 chars for SharePoint)
        if len(file_base + file_ext) > 128:
            file_base = file_base[:123 - len(file_ext)] + "_SP"
            
        return os.path.join(dir_name, file_base + file_ext)
    
    def fix_file(self, src_path, dest_dir, preserve_structure=True):
        """
        Fix a file's name and copy it to the destination directory
        
        Args:
            src_path: Source file path
            dest_dir: Destination directory
            preserve_structure: Whether to preserve the directory structure
            
        Returns:
            Tuple: (success, new_path)
        """
        try:
            # Get the fixed file name
            fixed_name = self.fix_name(src_path)
            
            # Determine the destination path
            if preserve_structure:
                # Preserve the directory structure relative to a common base
                rel_dir = os.path.dirname(fixed_name)
                dest_path = os.path.join(dest_dir, os.path.basename(fixed_name))
                
                # Create subdirectories if they don't exist
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            else:
                # Just put the file directly in the destination directory
                dest_path = os.path.join(dest_dir, os.path.basename(fixed_name))
            
            # Copy the file to the new location
            shutil.copy2(src_path, dest_path)
            
            return True, dest_path
        except Exception as e:
            print(f"Error fixing file name for {src_path}: {e}")
            return False, None