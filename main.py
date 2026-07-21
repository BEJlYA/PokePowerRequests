import flet as ft

from src.config.manager import config
from src.gui.screens.activation import activation_screen
from src.gui.screens.items_screen import items_screen
from src.gui.screens.main_screen import main_screen
from src.gui.screens.pokemon_screen import pokemon_screen
from src.gui.screens.running_screen import running_screen
from src.utils.path import resource_path


async def main(page: ft.Page):
    # ============ НАСТРОЙКИ ОКНА ============
    page.window.icon = str(resource_path("assets/images/favicon.ico"))
    page.title = "PPRCheat"
    page.window.width = 900
    page.window.height = 600
    page.window.resizable = False
    page.window.maximizable = False
    page.window.minimizable = True
    await page.window.center()

    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.margin = 0

    page.fonts = {
        "Rubik": str(resource_path("assets/fonts/Rubik-Medium.ttf")),
    }
    page.theme = ft.Theme(font_family="Rubik")

    selected_index = 0
    page.is_running = False

    screens = {
        0: main_screen,
        1: pokemon_screen,
        2: items_screen,
        3: running_screen,
    }

    def switch_to(index):
        nonlocal selected_index
        selected_index = index
        screens[index](page, switch_to, selected_index, screens)

    if config.activated:
        main_screen(page, switch_to, selected_index, screens)
    else:
        activation_screen(page, switch_to, selected_index, screens)


ft.run(main)