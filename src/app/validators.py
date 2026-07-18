import flet as ft

from src.config.manager import config


class AppValidator:
    @staticmethod
    def check_required_data() -> tuple[bool, str, int]:
        if not config.login.strip():
            return (
                False,
                "Введите логин!",
                0,
            )

        if not config.password.strip():
            return (
                False,
                "Введите пароль!",
                0,
            )

        return (
            True,
            "",
            -1,
        )

    @staticmethod
    def highlight_empty_fields(
        page: ft.Page,
        target_screen: int,
    ) -> None:

        if target_screen == 0:

            page.session.store.set(
                "highlight_login",
                not bool(config.login.strip()),
            )

            page.session.store.set(
                "highlight_password",
                not bool(config.password.strip()),
            )

            return

        if target_screen == 1:

            page.session.set(
                "highlight_pokemons",
                len(config.target_pokemons) == 0,
            )