# core/fixers/path_shortener.py
import os
import re
import shutil

class PathShortener:
    """Shortens paths that exceed SharePoint's 256 character limit"""
    
    def __init__(self, strategy="Abbreviate Directories"):
        self.strategy = strategy
        self.max_path_length = 256
        
    def shorten_path(self, file_path):
        """
        Shorten a path that exceeds the maximum path length
        
        Args:
            file_path: The file path to shorten
            
        Returns:
            str: The shortened path
        """
        if len(file_path) <= self.max_path_length:
            return file_path
            
        # Choose strategy based on the setting
        if self.strategy == "Abbreviate Directories":
            return self._abbreviate_directories(file_path)
        elif self.strategy == "Remove Middle Directories":
            return self._remove_middle_directories(file_path)
        elif self.strategy == "Truncate Names":
            return self._truncate_names(file_path)
        elif self.strategy == "Minimal Path":
            return self._minimal_path(file_path)
        else:
            # Default to abbreviate directories
            return self._abbreviate_directories(file_path)
    
    def _abbreviate_directories(self, file_path):
        """
        Shorten path by abbreviating directory names
        Example: "Development Documentation" → "Dev~Doc"
        """
        dir_name, file_name = os.path.split(file_path)
        dirs = dir_name.split(os.path.sep)
        
        # Don't abbreviate the drive letter (if on Windows)
        start_idx = 1 if os.name == 'nt' and ':' in dirs[0] else 0
        
        # Abbreviate directory names
        for i in range(start_idx, len(dirs)):
            if len(dirs[i]) > 5:
                words = re.findall(r'[A-Z][a-z]*|[a-z]+', dirs[i])
                if len(words) > 1:
                    # Use first 3 chars of first word and first char of rest
                    abbr = words[0][:3] + ''.join(w[0] for w in words[1:])
                    dirs[i] = abbr
                else:
                    # Just truncate to 5 chars with a tilde
                    dirs[i] = dirs[i][:4] + '~'
        
        new_path = os.path.sep.join(dirs) + os.path.sep + file_name
        
        # If still too long, try another strategy
        if len(new_path) > self.max_path_length:
            return self._truncate_names(new_path)
            
        return new_path
    
    def _remove_middle_directories(self, file_path):
        """
        Shorten path by keeping first and last directories, replacing middle with "..."
        Example: "/Dept/Team/Projects/2023/Q4/Reports/" → "/Dept/.../Reports/"
        """
        dir_name, file_name = os.path.split(file_path)
        dirs = dir_name.split(os.path.sep)
        
        # Keep the root and at most 2 levels, then ellipsis, then last 2 levels
        if len(dirs) > 5:
            # On Windows, keep the drive letter
            if os.name == 'nt' and ':' in dirs[0]:
                shortened_dirs = [dirs[0], dirs[1], '...'] + dirs[-2:]
            else:
                shortened_dirs = [dirs[0], '...'] + dirs[-2:]
                
            dir_name = os.path.sep.join(shortened_dirs)
            new_path = os.path.join(dir_name, file_name)
            
            # If still too long, try another strategy
            if len(new_path) > self.max_path_length:
                return self._truncate_names(new_path)
                
            return new_path
        else:
            # Not enough directories to shorten this way, try another strategy
            return self._truncate_names(file_path)
    
    def _truncate_names(self, file_path):
        """
        Shorten path by truncating all directory and file names
        Example: "Quarterly Financial Analysis Report.xlsx" → "Quar Fin Analy Rep.xlsx"
        """
        dir_name, file_name = os.path.split(file_path)
        file_base, file_ext = os.path.splitext(file_name)
        
        # Truncate the filename to 20 chars max plus extension
        if len(file_base) > 20:
            file_base = file_base[:17] + '...'
        
        # Split and truncate directory names
        dirs = dir_name.split(os.path.sep)
        for i in range(len(dirs)):
            if len(dirs[i]) > 10:
                dirs[i] = dirs[i][:8] + '..'
        
        shortened_dir = os.path.sep.join(dirs)
        new_path = os.path.join(shortened_dir, file_base + file_ext)
        
        # If still too long, use the most aggressive strategy
        if len(new_path) > self.max_path_length:
            return self._minimal_path(file_path)
            
        return new_path
    
    def _minimal_path(self, file_path):
        """
        Create a minimal path by keeping only essential components
        Example: "C:/Very/Long/Path/To/File.docx" → "C:/ShortPath/File.docx"
        """
        dir_name, file_name = os.path.split(file_path)
        
        # For Windows, keep the drive letter
        if os.name == 'nt' and ':' in dir_name:
            drive = dir_name.split(':')[0] + ':'
            new_dir = drive + os.path.sep + 'ShortPath'
        else:
            new_dir = os.path.sep + 'ShortPath'
        
        # Ensure filename is not too long
        file_base, file_ext = os.path.splitext(file_name)
        if len(file_base) > 20:
            file_base = file_base[:17] + '...'
        
        return os.path.join(new_dir, file_base + file_ext)
    
    def fix_file(self, src_path, dest_dir, preserve_structure=False):
        """
        Fix a file's path and copy it to the destination directory
        
        Args:
            src_path: Source file path
            dest_dir: Destination directory
            preserve_structure: Whether to preserve the directory structure
            
        Returns:
            Tuple: (success, new_path)
        """
        try:
            # Get the shortened path
            shortened_path = self.shorten_path(src_path)
            
            # Determine the destination path
            if preserve_structure:
                # This doesn't make sense for path shortening since we're changing the structure
                # Instead, recreate the shortened path structure
                rel_path = os.path.relpath(shortened_path, os.path.dirname(shortened_path))
                dest_path = os.path.join(dest_dir, rel_path)
            else:
                # Just use the shortened filename in the destination directory
                dest_path = os.path.join(dest_dir, os.path.basename(shortened_path))
            
            # Create subdirectories if they don't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copy the file to the new location
            shutil.copy2(src_path, dest_path)
            
            return True, dest_path
        except Exception as e:
            print(f"Error fixing path for {src_path}: {e}")
            return False, None