import os
import json
import shutil

class ProjectManager:
    def __init__(self, base_dir="D:/Kuno/Web Novel/Projects"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.current_project_path = None

    def create_project(self, project_name):
        project_path = os.path.join(self.base_dir, project_name)
        if os.path.exists(project_path):
            return False, "El proyecto ya existe."
        
        try:
            os.makedirs(project_path)
            # Create empty initial files
            self._save_file(os.path.join(project_path, "draft.txt"), "")
            self._save_json(os.path.join(project_path, "characters.json"), [])
            self._save_file(os.path.join(project_path, "notes.txt"), "")
            return True, project_path
        except Exception as e:
            return False, str(e)

    def open_project(self, project_name):
        project_path = os.path.join(self.base_dir, project_name)
        if not os.path.exists(project_path):
            return False, "El proyecto no existe."
        self.current_project_path = project_path
        return True, project_path

    def get_projects(self):
        if not os.path.exists(self.base_dir):
            return []
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

    def save_content(self, filename, content):
        if not self.current_project_path:
            return
        path = os.path.join(self.current_project_path, filename)
        if filename.endswith('.json'):
            self._save_json(path, content)
        else:
            self._save_file(path, content)

    def load_content(self, filename, default=None):
        if not self.current_project_path:
            return default
        path = os.path.join(self.current_project_path, filename)
        if not os.path.exists(path):
            return default
        
        if filename.endswith('.json'):
            return self._load_json(path, default)
        else:
            return self._load_file(path, default)

    def _save_file(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _load_file(self, path, default):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return default

    def _save_json(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4)

    def _load_json(self, path, default):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
