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
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        app_dir = Path(base) / "PPRCheat"
    else:
        app_dir = Path.home() / ".local" / "share" / "PPRCheat"

    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir