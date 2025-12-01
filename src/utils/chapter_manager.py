import os
import json

class ChapterManager:
    def __init__(self, project_path):
        self.project_path = project_path
        self.chapters_dir = os.path.join(project_path, "chapters")
        if not os.path.exists(self.chapters_dir):
            os.makedirs(self.chapters_dir)

    def get_chapters(self):
        """Returns list of chapter files sorted by name"""
        if not os.path.exists(self.chapters_dir):
            return []
        
        files = [f for f in os.listdir(self.chapters_dir) if f.endswith('.txt')]
        return sorted(files)

    def create_chapter(self, title):
        """Creates a new chapter file"""
        # Find next chapter number
        existing = self.get_chapters()
        chapter_num = len(existing) + 1
        
        # Sanitize title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_title:
            safe_title = "Sin título"
        
        filename = f"Capítulo {chapter_num} - {safe_title}.txt"
        filepath = os.path.join(self.chapters_dir, filename)
        
        # Create empty file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("")
        
        return filename

    def load_chapter(self, filename):
        """Loads chapter content"""
        filepath = os.path.join(self.chapters_dir, filename)
        if not os.path.exists(filepath):
            return ""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def save_chapter(self, filename, content):
        """Saves chapter content"""
        filepath = os.path.join(self.chapters_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def delete_chapter(self, filename):
        """Deletes a chapter file"""
        filepath = os.path.join(self.chapters_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    def rename_chapter(self, old_filename, new_title):
        """Renames a chapter file"""
        # Extract chapter number from old filename
        parts = old_filename.split(' - ', 1)
        if len(parts) == 2:
            chapter_prefix = parts[0]  # "Capítulo X"
        else:
            chapter_prefix = "Capítulo 1"
        
        # Sanitize new title
        safe_title = "".join(c for c in new_title if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_title:
            safe_title = "Sin título"
        
        new_filename = f"{chapter_prefix} - {safe_title}.txt"
        
        old_path = os.path.join(self.chapters_dir, old_filename)
        new_path = os.path.join(self.chapters_dir, new_filename)
        
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
        
        return new_filename
