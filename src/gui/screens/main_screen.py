import flet as ft

from src.config.manager import config
from src.gui.screens.menu import bottom_nav


def main_screen(page: ft.Page, switch_to, selected_index, screens):
    page.clean()

    highlight_login = page.session.store.get("highlight_login")
    highlight_password = page.session.store.get("highlight_password")

    # ============ КАСТОМНЫЕ ВИДЖЕТЫ ============
    def styled_text_field(label: str, password: bool = False, bgcolor: str = "#7092BE", **kwargs):
        return ft.Container(
            ft.TextField(
                label=label,
                label_style=ft.TextStyle(color="#FFFFFF"),
                border_radius=15,
                bgcolor=bgcolor,
                border_color="transparent",
                color="#FFFFFF",
                cursor_color="#FFFFFF",
                selection_color=ft.Colors.BLACK_12,
                password=password,
                can_reveal_password=password,
                width=300,
                **kwargs
            ),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.BLACK_26,
                offset=ft.Offset(0, -2),
            ),
        )

    def styled_checkbox(label: str, value: bool = True, **kwargs):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(label, color="#FFFFFF", size=16, margin=10),
                    ft.Checkbox(
                        value=value,
                        active_color="#4C6186",
                        check_color="#FFFFFF",
                        margin=-3,
                        **kwargs
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#7092BE",
            border_radius=15,
            padding=4,
            width=300,
            height=50,
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.BLACK_26,
                offset=ft.Offset(0, -2),
            ),
        )

    def on_focus(e, field_type: str):
        page.session.store.set(f"highlight_{field_type}", False)
        e.control.bgcolor = "#7092BE"
        e.control.update()

    # ============ ПОЛЯ С ПОДСВЕТКОЙ ============
    login_field = styled_text_field(
        "Логин",
        value=config.login,
        bgcolor="#B64B4B" if highlight_login else "#7092BE",
        on_change=lambda e: setattr(config, "login", e.control.value),
        on_focus=lambda e: (config.set("login", e.control.value), on_focus(e, "login")),
    )

    password_field = styled_text_field(
        "Пароль",
        password=True,
        value=config.password,
        bgcolor="#B64B4B" if highlight_password else "#7092BE",
        on_change=lambda e: setattr(config, "password", e.control.value),
        on_focus=lambda e: (config.set("password", e.control.value), on_focus(e, "password")),
    )

    # ============ ДАННЫЕ ============
    priority_dict = config.special_priority
    priority_items = list(priority_dict.keys())

    # ============ ОБРАБОТЧИКИ ============
    def move_up(index):
        if index > 0:
            priority_items.insert(index - 1, priority_items.pop(index))
            for i, name in enumerate(priority_items):
                priority_dict[name] = i + 1
            config.special_priority = dict(sorted(priority_dict.items(), key=lambda x: x[1]))
            update_list()

    def move_down(index):
        if index < len(priority_items) - 1:
            priority_items.insert(index + 1, priority_items.pop(index))
            for i, name in enumerate(priority_items):
                priority_dict[name] = i + 1
            config.special_priority = dict(sorted(priority_dict.items(), key=lambda x: x[1]))
            update_list()

    # ============ ОБНОВЛЕНИЕ СПИСКА ============
    def update_list():
        list_container.controls.clear()
        for index, item in enumerate(priority_items):

            item_card = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                f"{index + 1}.",
                                color="#FFFFFF",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            width=20,
                            alignment=ft.Alignment.CENTER
                        ),
                        ft.Text(item, color="#FFFFFF", size=16, expand=True),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_UPWARD,
                                    icon_color="#FFFFFF",
                                    icon_size=20,
                                    on_click=lambda e, i=index: move_up(i),
                                    disabled=(index == len(priority_items) - 0),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_DOWNWARD,
                                    icon_color="#FFFFFF",
                                    icon_size=20,
                                    on_click=lambda e, i=index: move_down(i),
                                    disabled=(index == len(priority_items) - 1),
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor="#7092BE" if index % 2 == 0 else "#3C4E6B",
                border_radius=10,
                padding=1,
                margin=1
            )
            list_container.controls.append(item_card)
        page.update()

    # ============ ЛЕВАЯ КОЛОНКА ============
    left_column = ft.Column(
        [
            login_field,
            password_field,
            styled_checkbox(
                label="Ловить шайни и сбегов",
                value=config.catch_shiny,
                on_change=lambda e: setattr(config, "catch_shiny", e.control.value),
            ),
            styled_checkbox(
                label="Отображать действия",
                value=config.viewing_logs,
                on_change=lambda e: setattr(config, "viewing_logs", e.control.value),
            ),
            styled_checkbox(
                label="Менять покемонов в бою",
                value=config.not_change_hero,
                on_change=lambda e: setattr(config, "not_change_hero", e.control.value),
            ),
        ],
        margin=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=37,
    )

    # ============ ПРАВАЯ КОЛОНКА ============
    list_container = ft.Column(spacing=0)

    priority_section = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "Приоритет покеболов (Шайни и Сбегов)",
                        color="#FFFFFF",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    padding=5,
                ),
                list_container,
            ],
            spacing=0,
        ),
        bgcolor="#3C4E6B",
        border_radius=15,
        padding=3,
        width=400,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, -2),
        ),
    )

    right_column = ft.Column(
        [priority_section],
        margin=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # ============ СБОРКА ============
    update_list()

    page.add(
        ft.Stack(
            [
                ft.Container(
                    expand=True,
                    image=ft.DecorationImage(
                        src="assets/images/main_background.png",
                        fit=ft.BoxFit.COVER
                    ),
                    bgcolor="#4C6186"
                ),
                ft.Container(
                    content=ft.Text(f"{config.version}", color="#FFFFFF", size=14),
                    alignment=ft.Alignment(-1, 1),
                    margin=10
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(left_column, expand=True, alignment=ft.Alignment.TOP_LEFT),
                                    ft.Container(right_column, expand=True, alignment=ft.Alignment.CENTER),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                disabled=page.is_running
                            ),
                            ft.Container(
                                content=bottom_nav(page, switch_to, selected_index, screens),
                                alignment=ft.Alignment.BOTTOM_CENTER,
                                expand=True
                            ),
                        ],
                    ),
                ),
            ],
            expand=True,
        )
    )

    page.update()