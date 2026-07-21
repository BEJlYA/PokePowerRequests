from pathlib import Path

def get_project_root() -> Path:
    """Корень проекта (папка с main.py)"""
    return Path(__file__).parent.parent.parent

def resource_path(relative_path: str) -> Path:
    """Путь к ресурсам (assets/, data/) — всегда из корня проекта"""
    return get_project_root() / relative_path

def get_config_path() -> Path:
    """config.json — при разработке из проекта, в сборке из AppData"""
    return get_project_root() / "user_data" / "config.json"

def get_data_path(relative_path: str) -> Path:
    return get_project_root() / "data" / relative_path

def get_last_log_path() -> Path:
    """session_last.log — при разработке из проекта, в сборке из AppData"""
    log_dir = get_project_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "session_last.log"
