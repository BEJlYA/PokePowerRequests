import flet as ft

from src.config.manager import config
from src.gui.menu import bottom_nav
from src.services.task_events import task_events
from src.services.tasks import Task
from src.utils.path import resource_path


def _replace_tasks_of_kind(kind: str, new_tasks: list[dict]) -> None:
    current = [t for t in config.target_tasks if t.get("kind") != kind]
    config.target_tasks = current + new_tasks

def save_pokemons_data(fields_column):
    pokemons: list[dict] = []
    seen: dict[tuple, dict] = {}

    for field in fields_column.controls:
        name_raw = field.content.controls[0].content.value
        gender = field.content.controls[1].value or "Л"
        count_raw = field.content.controls[2].content.value

        if not name_raw or not name_raw.strip():
            continue

        raw = name_raw.strip()
        if raw.isdigit():
            num, name = raw.zfill(3), ""
        else:
            num, name = "", raw

        key = (num or name, gender)
        count = int(count_raw) if count_raw else 0

        if key in seen:
            seen[key]["count"] += count
        else:
            task = Task(
                kind="pokemon",
                num=num,
                name=name,
                gender=gender,
                count=count,
            )
            entry = task.to_dict()
            seen[key] = entry
            pokemons.append(entry)

    _replace_tasks_of_kind("pokemon", pokemons)

def create_pokemon_field(page: ft.Page, fields_column, name=None, num=None, gender=None, count=None, key=None):
    display_value = num or name or ""

    name_field = ft.Container(
        ft.TextField(
            label="Покемон",
            label_style=ft.TextStyle(color="#FFFFFF"),
            hint_text="009/Катерпи",
            hint_style=ft.TextStyle(color="#FFFFFF"),
            border_radius=15,
            bgcolor="#7092BE",
            border_color="transparent",
            color="#FFFFFF",
            cursor_color="#FFFFFF",
            selection_color=ft.Colors.BLACK_12,
            width=150,
            value=display_value,
            on_change=lambda e: save_pokemons_data(fields_column),
        ),
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, -2),
        ),
    )

    gender_dropdown = ft.Dropdown(
        bgcolor="#7092BE",
        border_radius=15,
        color="#FFFFFF",
        width=100,
        value=gender,
        options=[
            ft.dropdown.Option("М"),
            ft.dropdown.Option("Ж"),
            ft.dropdown.Option("Б"),
            ft.dropdown.Option("Л"),
        ],
        on_text_change=lambda e: save_pokemons_data(fields_column),
    )

    def on_count_change(e, fields_column):
        value = e.control.value
        if value:
            clean = ''.join(filter(str.isdigit, value))
            if clean:
                num = int(clean)
                if num < 1:
                    clean = "1"
                elif num > 999:
                    clean = "999"
                e.control.value = clean
            else:
                e.control.value = "1"
            e.control.update()
        save_pokemons_data(fields_column)

    count_field = ft.Container(
        content=ft.TextField(
            hint_text="Кол-во",
            hint_style=ft.TextStyle(color="#FFFFFF"),
            border_radius=15,
            bgcolor="#7092BE",
            border_color="transparent",
            color="#FFFFFF",
            cursor_color="#FFFFFF",
            selection_color=ft.Colors.BLACK_12,
            width=80,
            value=count,
            on_change=lambda e: on_count_change(e, fields_column)
        ),
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, -2),
        )
    )

    container = ft.Container(
        content=ft.Row(
            [
                name_field,
                gender_dropdown,
                count_field,
            ],
            spacing=10,
        ),
        margin=ft.Margin(bottom=10),
    )
    container.data = key
    return container


def pokemon_screen(page: ft.Page, switch_to, selected_index, screens):
    page.clean()

    saved_pokemons = [t for t in config.target_tasks if t.get("kind") == "pokemon"]

    # ============ ДАННЫЕ ============
    priority_dict = config.priority
    priority_items = list(priority_dict.keys())

    # ============ ОБРАБОТЧИКИ ============
    def move_up(index):
        if index > 0:
            priority_items.insert(index - 1, priority_items.pop(index))
            for i, name in enumerate(priority_items):
                priority_dict[name] = i + 1
            config.priority = dict(sorted(priority_dict.items(), key=lambda x: x[1]))
            update_list()

    def move_down(index):
        if index < len(priority_items) - 1:
            priority_items.insert(index + 1, priority_items.pop(index))
            for i, name in enumerate(priority_items):
                priority_dict[name] = i + 1
            config.priority = dict(sorted(priority_dict.items(), key=lambda x: x[1]))
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
                                    disabled=True if page.is_running else (index == len(priority_items) - 0),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_DOWNWARD,
                                    icon_color="#FFFFFF",
                                    icon_size=20,
                                    on_click=lambda e, i=index: move_down(i),
                                    disabled=True if page.is_running else (index == len(priority_items) - 1),
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
    fields_column = ft.Column(
        [],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    def refresh_fields():
        saved = [t for t in config.target_tasks if t.get("kind") == "pokemon"]

        by_key = {}
        for t in saved:
            t_key = ((t.get("num") or t.get("name")), t.get("gender", "Л"))
            by_key[t_key] = t

        for field in fields_column.controls:
            field_key = getattr(field, "data", None)
            if field_key is None:
                continue
            task = by_key.get(field_key)
            if task is None:
                continue

            count_field = field.content.controls[2].content
            new_count = str(task.get("count", 0))
            if count_field.value != new_count:
                count_field.value = new_count

    if saved_pokemons:
        for pokemon in saved_pokemons:
            pokemon_num = pokemon.get("num") or ""
            pokemon_name = pokemon.get("name") or ""
            pokemon_gender = pokemon.get("gender") or "Л"

            field = create_pokemon_field(
                page,
                fields_column,
                name=pokemon_name,
                num=pokemon_num,
                gender=pokemon_gender,
                count=pokemon.get("count"),
                key=(pokemon_num or pokemon_name, pokemon_gender),
            )

            fields_column.controls.append(field)
        if len(fields_column.controls) < 1:
            fields_column.controls.append(create_pokemon_field(page, fields_column))
    else:
        fields_column.controls.append(create_pokemon_field(page, fields_column))

    def add_field(e):
        fields_column.controls.append(create_pokemon_field(page, fields_column))
        save_pokemons_data(fields_column)
        page.update()

        if len(fields_column.controls) == 7:
            plus_button.visible = False
            page.update()
            return

    plus_button = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.PLUS_ONE,
            icon_color="#FFFFFF",
            icon_size=28,
            on_click=add_field
        ),
        border_radius=50,
        bgcolor="#7092BE",
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, -2)
        )
    )

    left_column = ft.Column(
        [
            fields_column,
            plus_button
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        margin=ft.Margin.only(left=20, top=20),
        disabled=page.is_running
    )

    # ============ ПРАВАЯ КОЛОНКА ============
    list_container = ft.Column(spacing=0)

    priority_section = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "Приоритет покеболов",
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
                        src=str(resource_path("assets/images/main_background.png")),
                        fit=ft.BoxFit.COVER
                    ),
                    bgcolor="#4C6186"
                ),
                ft.Container(
                    content=ft.Text(f"{config.version}", color="#FFFFFF", size=14),
                    alignment=ft.Alignment(-1, 1),
                    margin=10,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        left_column,
                                        expand=True,
                                        alignment=ft.Alignment.CENTER,
                                    ),
                                    ft.Container(
                                        right_column,
                                        expand=True,
                                        alignment=ft.Alignment.CENTER,
                                    ),
                                ],
                                expand=True,
                            ),
                            ft.Container(
                                content=bottom_nav(page, switch_to, selected_index, screens),
                                alignment=ft.Alignment.BOTTOM_CENTER,
                            ),
                        ],
                        expand=True,
                    ),
                    expand=True,
                ),
            ],
            expand=True,
        )
    )
    page.update()

    async def on_tasks_changed():
        try:
            if fields_column.page is None:
                return
            refresh_fields()
            page.update()
        except RuntimeError:
            return

    task_events.subscribe("tasks_changed", on_tasks_changed)