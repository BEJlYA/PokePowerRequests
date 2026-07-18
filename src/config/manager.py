from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """Менеджер конфигурации приложения."""

    def __init__(
        self,
        config_path: str = "data/config.json",
        log_path: str = "logs/session_last.log",
    ):
        self._config_path = Path(config_path)
        self._log_path = Path(log_path)
        self._config = self._load()

    # ------------------------------------------------------------------
    # CONFIG
    # ------------------------------------------------------------------

    def _load(self) -> dict[str, Any]:
        if not self._config_path.exists():
            return {}

        with self._config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def save(self) -> None:
        self._config_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._config_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self._config,
                file,
                indent=4,
                ensure_ascii=False,
            )

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
        return self.get("version", "beta 0.1")

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
    def priority(self) -> list:
        return self.get(
            "priority_pokeballs",
            [],
        )

    @priority.setter
    def priority(self, value: dict):
        self.set(
            "priority_pokeballs",
            value,
        )

    @property
    def special_priority(self) -> list:
        return self.get(
            "special_priority_pokeballs",
            [],
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
    def target_pokemons(self) -> list:
        return self.get(
            "targetPokemons",
            [],
        )

    @target_pokemons.setter
    def target_pokemons(
        self,
        value: list,
    ):
        self.set(
            "targetPokemons",
            value,
        )

    def decrease_pokemon_count(self, num: str = None, name: str = None, gender: str = None, amount: int = 1):
        pokemons = self.target_pokemons
        for pokemon in pokemons:
            if (num and pokemon.get('num') == num) or (name and pokemon.get('name') == name):
                if gender is None or pokemon.get('gender') == gender or pokemon.get('gender') == 'any':
                    current = int(pokemon.get('count', 0))
                    pokemon['count'] = max(current - amount, 0)
                    break
        self.target_pokemons = pokemons
        return self.target_pokemons

    @property
    def target_items(self) -> list:
        return self.get(
            "targetItems",
            [],
        )

    @target_items.setter
    def target_items(
        self,
        value: list,
    ):
        self.set(
            "targetItems",
            value,
        )

    def decrease_item_count(self, name: str, amount: int = 1):
        items = self.target_items
        for item in items:
            if item.get('name') == name:
                current = int(item.get('count', 0))
                item['count'] = max(current - amount, 0)
                break
        self.target_items = items
        return self.target_items

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