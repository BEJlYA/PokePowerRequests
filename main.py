import asyncio

import flet as ft
import flet_notifications as ftn

from src.config.manager import config
from src.gui.activation import activation_screen
from src.gui.items_screen import items_screen
from src.gui.main_screen import main_screen
from src.gui.pokemon_screen import pokemon_screen
from src.gui.running_screen import running_screen
from src.services.task_events import task_events
from src.utils.path import resource_path


async def main(page: ft.Page):
    # ============ НАСТРОЙКИ ОКНА ============
    page.title = "PPRCheat"

    page.is_desktop = page.platform not in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS)

    if page.is_desktop:
        page.window.width = 900
        page.window.height = 600
        page.window.resizable = False
        page.window.maximizable = False
        page.window.minimizable = True
        page.window.icon = str(resource_path("assets/favicon.ico"))
    page.adaptive = True

    page.is_running = False
    page.notifications = ftn.Notifications()


    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.margin = 0

    page.fonts = {
        "Rubik": str(resource_path("assets/fonts/Rubik-Medium.ttf")),
    }
    page.theme = ft.Theme(
        font_family="Rubik"
    )
    page.bgcolor = ft.Colors.TRANSPARENT
    page.decoration = ft.BoxDecoration(
        bgcolor="#4C6186",
        image=ft.DecorationImage(
            src=str(
                resource_path("assets/images/main_background.png")
            ),
            fit=ft.BoxFit.COVER
        )
    )

    selected_index = 0
    screens = {
        0: main_screen,
        1: pokemon_screen,
        2: items_screen,
        3: running_screen,
    }

    main_container = ft.Container(expand=True)

    def switch_to(index):
        for attr in ("_log_task", "_screen_task"):
            task = getattr(page, attr, None)
            if task and not task.done():
                task.cancel()

        task_events.clear_topic("tasks_changed")

        main_container.content = None

        screens[index](page, switch_to, index, screens, main_container)

    def cleanup(e=None):
        for attr in ("_log_task", "_screen_task"):
            task = getattr(page, attr, None)
            if task and not task.done():
                task.cancel()
        task_events.clear_topic("tasks_changed")

    page.on_disconnect = cleanup

    if config.activated:
        main_screen(page, switch_to, selected_index, screens, main_container)
    else:
        activation_screen(page, switch_to, selected_index, screens, main_container)

    page.add(
        ft.SafeArea(
            content=main_container,
            expand=True,
            maintain_bottom_view_padding=True
        )
    )

    if not page.is_desktop:
        asyncio.create_task(
            page.notifications.request_permissions()
        )

    if page.is_desktop:
        await page.window.center()
        page.window.visible = True

ft.run(main, view = ft.AppView.FLET_APP_HIDDEN)
