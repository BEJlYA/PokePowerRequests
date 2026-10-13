import json
from pathlib import Path
from typing import Any

from src.services.tasks import Task, GENDER_MAP
from src.utils.path import get_app_data_dir

DEFAULT_CONFIG = {
    "version": "beta 0.9.4",
    "activated": False,
    "login": "",
    "password": "",
    "catchShiny": True,
    "viewingLogs": False,
    "notChageHero": True,
    "special_priority_pokeballs": {
        "Взломанный Шайнибол": 1,
        "Шайнибол": 2,
        "Генобол": 3,
        "Мастербол": 4,
        "Ультрабол": 5,
        "Дистанцбол": 6,
        "Покебол": 7,
        "Гритбол": 8
    },
    "priority_pokeballs": {
        "Покебол": 1,
        "Ультрабол": 2,
        "Гритбол": 3,
        "Генобол": 4,
        "Дистанцбол": 5,
        "Мастербол": 6,
        "Шайнибол": 7,
        "Взломанный Шайнибол": 8
    },
    "targetTasks": []
}

class ConfigManager:
    """Менеджер конфигурации приложения."""
    def __init__(
        self,
        config_path: Path = get_app_data_dir() / "user_data" /"config.json",
        log_path: Path = get_app_data_dir() / "logs" / "session_last.log",
    ):
        self._config_path = config_path
        self._log_path = log_path
        self._config = self._load()

    # ------------------------------------------------------------------
    # CONFIG
    # ------------------------------------------------------------------

    def _load(self) -> dict[str, Any]:
        """Читает конфиг с диска. Если файла нет — создаёт дефолтный."""
        if not self._config_path.exists():
            config = DEFAULT_CONFIG.copy()
            self._write(config)
            return config

        try:
            with self._config_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            config = DEFAULT_CONFIG.copy()
            self._write(config)
            return config

        for key, value in DEFAULT_CONFIG.items():
            data.setdefault(key, value)
        return data

    def _write(self, data: dict[str, Any]) -> None:
        """Атомарно записывает конфиг на диск."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with self._config_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def save(self) -> None:
        self._write(self._config)

    # ------------------------------------------------------------------
    # GENERIC API
    # ------------------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._config.get(key, default)

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._config[key] = value
        self.save()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def activated(self) -> bool:
        return self.get("activated", False)

    @activated.setter
    def activated(self, value: bool):
        self.set("activated", value)

    @property
    def version(self) -> str:
        return self.get("version", "beta 0.9.4")

    @property
    def login(self) -> str:
        return self.get("login", "")

    @login.setter
    def login(self, value: str):
        self.set("login", value)

    @property
    def password(self) -> str:
        return self.get("password", "")

    @password.setter
    def password(self, value: str):
        self.set("password", value)

    @property
    def catch_shiny(self) -> bool:
        return self.get("catchShiny", True)

    @catch_shiny.setter
    def catch_shiny(self, value: bool):
        self.set("catchShiny", value)

    @property
    def viewing_logs(self) -> bool:
        return self.get("viewingLogs", False)


    @viewing_logs.setter
    def viewing_logs(self, value: bool):
        self.set("viewingLogs", value)

    @property
    def not_change_hero(self) -> bool:
        return self.get("notChageHero", True)

    @not_change_hero.setter
    def not_change_hero(self, value: bool):
        self.set("notChageHero", value)

    @property
    def help_url(self) -> str:
        return self.get(
            "help_url",
            "https://pokepower.ru",
        )

    @property
    def priority(self) -> dict:
        return self.get(
            "priority_pokeballs",
            {},
        )

    @priority.setter
    def priority(self, value: dict):
        self.set(
            "priority_pokeballs",
            value,
        )

    @property
    def special_priority(self) -> dict:
        return self.get(
            "special_priority_pokeballs",
            {},
        )

    @special_priority.setter
    def special_priority(
        self,
        value: list,
    ):
        self.set(
            "special_priority_pokeballs",
            value,
        )

    @property
    def target_tasks(self) -> list[dict]:
        return self.get("targetTasks", [])

    @target_tasks.setter
    def target_tasks(self, value: list[dict]) -> None:
        self.set("targetTasks", value)

    async def decrease_task_count(self, task: Task, amount: int = 1) -> list[dict]:
        for entry in self.target_tasks:
            if entry.get("kind") != task.kind:
                continue

            if task.kind == "pokemon":
                entry_id = entry.get("num") or entry.get("name")
                task_id = task.num or task.name
                if entry_id != task_id:
                    continue

                entry_gender_ui = entry.get("gender", "Л")
                if entry_gender_ui != "Л" and GENDER_MAP.get(entry_gender_ui) != task.gender:
                    continue
            else:
                if entry.get("name") != task.name:
                    continue

            entry["count"] = max(int(entry.get("count", 0)) - amount, 0)
            break

        self.target_tasks = [e for e in self.target_tasks if int(e.get("count", 0)) > 0]

        from src.services.task_events import task_events
        await task_events.emit("tasks_changed")

        return self.target_tasks

    # ------------------------------------------------------------------
    # LOGS
    # ------------------------------------------------------------------

    def save_log(self, message: str) -> None:
        self._log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._log_path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(message + "\n")

    def load_logs(self) -> list[str]:
        if not self._log_path.exists():
            return []

        with self._log_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return [
                line.rstrip()
                for line in file.readlines()
            ]

    def clear_logs(self) -> None:
        if self._log_path.exists():
            self._log_path.unlink()


config = ConfigManager()