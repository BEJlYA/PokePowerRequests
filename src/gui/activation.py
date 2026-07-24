import flet as ft

from src.config.manager import config
from src.gui.main_screen import main_screen
from src.utils.path import resource_path


def activation_screen(page: ft.Page, switch_to, selected_index, screens):
    page.clean()

    def on_activate(e):
        key = key_field.content.value
        if len(key) > 0 and key == "1111":
            config.activated = True
            main_screen(page, switch_to, selected_index, screens)
        else:
            key_field.content.value = ""
            key_field.content.hint_text = "Неверный ключ!"
            key_field.content.hint_style = ft.TextStyle(color="#B64B4B")
            key_field.content.update()

    async def on_logo_click(e):
        await ft.UrlLauncher().launch_url("https://pokepower.ru")

    key_field = (ft.Container(
        content=ft.TextField(
            hint_text="Введите ключ активации...",
            hint_style=ft.TextStyle(color="#FFFFFF"),
            border_radius=15,
            bgcolor="#7092BE",
            border_color="#7092BE",
            color="#FFFFFF",
            cursor_color="#FFFFFF",
            selection_color=ft.Colors.BLACK_12,
            on_submit=on_activate
        ),
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, -2),
        ),
    )
    )

    page.add(
        ft.Stack(
            [
                ft.Container( #Background
                    expand=True,
                    image=ft.DecorationImage(
                        src=str(resource_path("assets/images/activation_background.png")),
                        fit=ft.BoxFit.COVER,
                        color_filter=ft.ColorFilter(
                            color="#4C6186",
                            blend_mode=ft.BlendMode.MULTIPLY,
                        )
                    ),
                    bgcolor="#4C6186",
                ), # Text beta
                ft.Container(
                    content=ft.Text(f"{config.version}", color="#FFFFFF", size=14),
                    alignment=ft.Alignment(-1, 1),
                    margin=10
                ),
                ft.Container( #logo central
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Image( #Central logo
                                    src=str(resource_path("assets/images/logo.png")),
                                    width=161,
                                    height=161,
                                ),
                                on_click=on_logo_click,
                            ),
                            key_field, #input key field
                            ft.Container(
                                content=ft.FilledButton( #actavate button
                                    "Активировать",
                                    on_click=on_activate,
                                    style=ft.ButtonStyle(
                                        color="#FFFFFF",
                                        bgcolor="#B64B4B",
                                        shape=ft.RoundedRectangleBorder(radius=20)
                                    )
                                ),
                                shadow=ft.BoxShadow(
                                    blur_radius=10,
                                    color=ft.Colors.BLACK_26,
                                    offset=ft.Offset(0, -2),
                                ),
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        tight=True
                    ),
                    alignment=ft.Alignment.CENTER
                )
            ],
            expand=True,
        )
    )

    page.update()
