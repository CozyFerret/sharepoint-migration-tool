# core/fixers/permission_fixer.py
import os
import shutil
import stat

class PermissionFixer:
    """Fixes permission issues with files, particularly read-only files"""
    
    def __init__(self):
        pass
    
    def fix_permissions(self, file_path):
        """
        Fix permissions on a file, making it writable if it's read-only
        
        Args:
            file_path: Path to the file to fix
            
        Returns:
            bool: True if permissions were fixed, False otherwise
        """
        try:
            # Check if file is read-only
            if not os.access(file_path, os.W_OK):
                # Make file writable by modifying its mode
                os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                return True
            return False  # No change needed
        except Exception as e:
            print(f"Error fixing permissions for {file_path}: {e}")
            return False
    
    def fix_file(self, src_path, dest_dir, preserve_structure=True):
        """
        Fix a file's permissions and copy it to the destination directory
        
        Args:
            src_path: Source file path
            dest_dir: Destination directory
            preserve_structure: Whether to preserve the directory structure
            
        Returns:
            Tuple: (success, new_path)
        """
        try:
            # First, fix permissions on the source file so we can read it
            self.fix_permissions(src_path)
            
            # Determine the destination path
            if preserve_structure:
                # Preserve the directory structure relative to a common base
                rel_dir = os.path.dirname(src_path)
                dest_subdir = os.path.join(dest_dir, os.path.basename(rel_dir))
                os.makedirs(dest_subdir, exist_ok=True)
            else:
                dest_subdir = dest_dir
            
            dest_path = os.path.join(dest_subdir, os.path.basename(src_path))
            
            # Copy the file to the new location
            shutil.copy2(src_path, dest_path)
            
            # Ensure the copied file is not read-only
            os.chmod(dest_path, stat.S_IWRITE | stat.S_IREAD)
            
            return True, dest_path
        except Exception as e:
            print(f"Error fixing permissions for {src_path}: {e}")
            return False, None