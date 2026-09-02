import flet as ft

from src.config.manager import config
from src.gui.menu import bottom_nav


def running_screen(page: ft.Page, switch_to, selected_index, screens):
    page.clean()

    log_list = ft.Column(
        controls=[ft.Text(log, color="#FFFFFF") for log in config.load_logs()],
        scroll=ft.ScrollMode.ALWAYS,
        auto_scroll=page.is_running,
    )

    async def update_logs():
        logs = config.load_logs()
        log_list.controls.clear()
        for log in logs:
            log_list.controls.append(ft.Text(log.strip(), color="#FFFFFF"))
        if page.is_running:
            await log_list.scroll_to(offset=-1, duration=300)
        page.update()

    def start_log_updater():
        import asyncio
        async def update_loop():
            while page.is_running:
                await asyncio.sleep(1)
                await update_logs()
            await update_logs()

        asyncio.create_task(update_loop())

    page.add(
        ft.Stack(
            [
                ft.Container(
                    expand=True,
                    bgcolor="#4C6186"
                ),
                ft.Container(
                    content=ft.Text(f"{config.version}", color="#FFFFFF", size=14),
                    alignment=ft.Alignment(-1, 1),
                    margin=10
                ),
                ft.Container(
                    content=bottom_nav(page, switch_to, selected_index, screens),
                    alignment=ft.Alignment.BOTTOM_CENTER
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Действия бота:", color="#FFFFFF", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=log_list,
                                expand=True,
                                border_radius=10,
                                padding=10,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    width=880,
                    height=484,
                    margin=10,
                ),
            ],
            expand=True,
        )
    )
    start_log_updater()
    page.update()