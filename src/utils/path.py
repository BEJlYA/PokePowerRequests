from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent

def resource_path(relative_path: str) -> Path:
    return get_project_root() / relative_path

def get_config_path() -> Path:
    return get_project_root() / "user_data" / "config.json"

def get_data_path(relative_path: str) -> Path:
    return get_project_root() / "data" / relative_path

def get_last_log_path() -> Path:
    log_dir = get_project_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "session_last.log"
