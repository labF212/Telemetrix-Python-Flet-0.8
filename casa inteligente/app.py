
# app.py
import flet as ft
from ui import build

async def main(page: ft.Page):
    await build(page)

ft.run(main)
