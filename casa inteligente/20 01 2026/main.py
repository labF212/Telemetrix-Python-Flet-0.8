""" casa_inteligente/ 
│ 
├── main.py ← 🚀 FICHEIRO DE ARRANQUE 
├── hardware.py ← Arduino / Telemetrix 
├── logic.py ← Estados + regras 
└── ui.py ← Flet (interface) 
"""


# main.py
import flet as ft
import hardware
from ui import build

async def main(page: ft.Page):
    hardware.init()
    await build(page)

ft.run(main)