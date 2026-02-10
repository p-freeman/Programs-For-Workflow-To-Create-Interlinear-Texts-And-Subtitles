"""
Project I/O Module for Interlinear Text Creator

Handles reading and writing project files.
"""

import os
import json

def save_text_file(folder, filename, text):
    """
    Save text content to a file.
    """
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def load_text_file(folder, filename):
    """
    Load text content from a file.
    """
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_project_json(folder, title, data):
    """
    Save project metadata as JSON.
    """
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{title}.project.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def load_project_json(path):
    """
    Load project metadata from JSON file.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
