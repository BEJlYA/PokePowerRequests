import asyncio

import flet as ft

from src.app.validators import AppValidator
from src.config.manager import config

bot_task = None

def bottom_nav(page: ft.Page, switch_to, selected_index, screens):
    icons = [
        ft.Icons.HOME_WORK_OUTLINED,
        ft.Icons.CATCHING_POKEMON,
        ft.Icons.BACKPACK_OUTLINED,
        ft.Icons.PAUSE_OUTLINED if page.is_running else ft.Icons.PLAY_ARROW_OUTLINED,
    ]

    nav_items = []
    for i, icon in enumerate(icons):
        is_active = (i == selected_index)

        def get_on_click(idx):
            if idx == 3:
                return lambda e: handle_play_pause(e, page, switch_to, selected_index, screens)
            else:
                return lambda e, idx=idx: switch_to(idx)

        nav_item = ft.IconButton(
            icon=icon,
            icon_color="#FFFFFF" if is_active else "#b3b3b3",
            icon_size=28,
            on_click=get_on_click(i),
            padding=ft.Padding.symmetric(horizontal=18, vertical=10)
        )
        nav_items.append(nav_item)

    return ft.Container(
        content=ft.Row(
            nav_items,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=35,
        ),
        bgcolor="#008000" if page.is_running else "#B64B4B",
        padding=ft.Padding.symmetric(vertical=6, horizontal=0),
        border_radius=ft.BorderRadius.only(top_left=25, top_right=25),
        width=400,
        height=56,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK_26,
            offset=ft.Offset(0, -3),
        ),
    )


def handle_play_pause(e, page: ft.Page, switch_to, selected_index, screens):
    from src.gui.screens.running_screen import running_screen
    from src.bot.bot import main as bot_main
    from src.core.exeptions import BotShutdown
    global bot_task

    show_logs = config.viewing_logs

    def stop_bot():
        page.is_running = False
        if bot_task and not bot_task.done():
            bot_task.cancel()

        screens[selected_index](page, switch_to, selected_index, screens)

        page.update()

    if not page.is_running:
        ok, msg, target_screen = AppValidator.check_required_data()
        if not ok:
            AppValidator.highlight_empty_fields(page, target_screen)
            switch_to(target_screen)
            return

        page.is_running = True

        async def run_bot():
            try:
                await bot_main(config.login, config.password)
            except BotShutdown as e:
                stop_bot()
            except Exception as e:
                stop_bot()

        bot_task = asyncio.create_task(run_bot())

        if show_logs:
            switch_to(3)
        else:
            screens[selected_index](page, switch_to, selected_index, screens)
        return

    if selected_index == 3 and show_logs:
        page.is_running = False
        if bot_task and not bot_task.done():
            bot_task.cancel()
        running_screen(page, switch_to, selected_index, screens)
        return
    elif selected_index == 3 and not show_logs:
        page.is_running = False
        if bot_task and not bot_task.done():
            bot_task.cancel()
        return
    else:
        if show_logs:
            switch_to(3)
        else:
            page.is_running = False
            if bot_task and not bot_task.done():
                bot_task.cancel()
            screens[selected_index](page, switch_to, selected_index, screens)