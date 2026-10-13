import flet as ft

from src.config.manager import config
from src.gui.menu import bottom_nav
from src.services.task_events import task_events
from src.services.tasks import Task
from src.utils.path import resource_path


def _replace_tasks_of_kind(kind: str, new_tasks: list[dict]) -> None:
    current = [t for t in config.target_tasks if t.get("kind") != kind]
    config.target_tasks = current + new_tasks

def save_items_data(fields_column):
    items: list[dict] = []
    seen: dict[str, dict] = {}

    for field in fields_column.controls:
        name_raw = field.content.controls[0].content.value
        count_raw = field.content.controls[1].content.value

        if not name_raw or not name_raw.strip():
            continue

        name = name_raw.strip()
        count = int(count_raw) if count_raw else 0

        if name in seen:
            seen[name]["count"] += count
        else:
            task = Task(
                kind="item",
                name=name,
                count=count,
            )
            entry = task.to_dict()
            seen[name] = entry
            items.append(entry)

    _replace_tasks_of_kind("item", items)

def create_item_field(page: ft.Page, fields_column, name=None, count=None, key=None):
    name_field = ft.Container(
        ft.TextField(
            label="Предмет",
            label_style=ft.TextStyle(color="#FFFFFF"),
            hint_text="Название предмета",
            hint_style=ft.TextStyle(color="#FFFFFF"),
            border_radius=15,
            bgcolor="#7092BE",
            border_color="transparent",
            color="#FFFFFF",
            cursor_color="#FFFFFF",
            selection_color=ft.Colors.BLACK_12,
            width=260,
            value = name,
            on_change = lambda e: save_items_data(fields_column),
        ),
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, -2),
        ),
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
        save_items_data(fields_column)

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
        content=ft.Row([name_field, count_field], spacing=10),
        margin=ft.Margin(bottom=10),
    )
    container.data = key
    return container


def items_screen(page: ft.Page, switch_to, selected_index, screens):
    page.clean()

    saved_items = [t for t in config.target_tasks if t.get("kind") == "item"]

    async def on_help_click(e):
        await ft.UrlLauncher().launch_url(config.help_url)


    # ============ ЛЕВАЯ КОЛОНКА ============
    fields_column = ft.Column(
        [],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    def refresh_fields():
        saved = [t for t in config.target_tasks if t.get("kind") == "item"]

        by_key = {}
        for t in saved:
            t_key = t.get("name") or ""
            by_key[t_key] = t

        for field in fields_column.controls:
            field_key = getattr(field, "data", None)
            if field_key is None:
                continue
            task = by_key.get(field_key)
            if task is None:
                continue

            count_ctrl = field.content.controls[1].content
            new_count = str(task.get("count", 0))
            if count_ctrl.value != new_count:
                count_ctrl.value = new_count

    if saved_items:
        for item in saved_items:
            item_name = item.get("name") or ""
            field = create_item_field(
                page,
                fields_column,
                name=item_name,
                count=item.get("count"),
                key=item_name,
            )
            fields_column.controls.append(field)
        if len(fields_column.controls) < 1:
            fields_column.controls.append(create_item_field(page, fields_column))
    else:
        fields_column.controls.append(create_item_field(page, fields_column))

    def add_field(e):
        fields_column.controls.append(create_item_field(page, fields_column))
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
            on_click=add_field,
        ),
        border_radius=50,
        bgcolor="#7092BE",
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, -2),
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
    right_column = ft.Container(
        content=ft.Image(
            src=str(resource_path("assets/images/help_img.png")),
            width=400,
            height=400,
            expand=True
        ),
        on_click = on_help_click,
    )

    # ============ СБОРКА ============
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
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
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