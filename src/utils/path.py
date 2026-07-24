import os
import sys
from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent

def resource_path(relative_path: str) -> Path:
    return get_project_root() / relative_path

def get_data_path(relative_path: str) -> Path:
    return get_project_root() / "data" / relative_path

def get_app_data_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get('PROGRAMDATA', '')) / "PPRCheat"
    return Path.home() / ".local" / "share" / "PPRCheat"
