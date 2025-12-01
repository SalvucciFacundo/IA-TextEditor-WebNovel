import os
import json

SETTINGS_FILE = "settings.json"

def load_theme_preference():
    """Load theme preference from settings file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('dark_mode', True)
        except:
            pass
    return True  # Default to dark mode

def save_theme_preference(is_dark):
    """Save theme preference to settings file"""
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except:
            pass
    
    settings['dark_mode'] = is_dark
    
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)

def load_ollama_url():
    """Load Ollama API URL from settings file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('ollama_url', 'http://localhost:11434/api/generate')
        except:
            pass
    return 'http://localhost:11434/api/generate'  # Default URL

def save_ollama_url(url):
    """Save Ollama API URL to settings file"""
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except:
            pass
    
    settings['ollama_url'] = url
    
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)

def load_ollama_model():
    """Load selected Ollama model from settings file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('ollama_model', None)
        except:
            pass
    return None

def save_ollama_model(model):
    """Save selected Ollama model to settings file"""
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except:
            pass
    
    settings['ollama_model'] = model
    
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)

def load_style_preference():
    """Load style preferences (auto_mode, last_style)"""
    default = {"auto_style": True, "last_style": "Normal"}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return {
                    "auto_style": settings.get('auto_style', True),
                    "last_style": settings.get('last_style', "Normal")
                }
        except:
            pass
    return default

def save_style_preference(auto_style, last_style):
    """Save style preferences"""
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except:
            pass
    
    settings['auto_style'] = auto_style
    settings['last_style'] = last_style
    
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)


