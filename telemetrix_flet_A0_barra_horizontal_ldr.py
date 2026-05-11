import time
import threading
import asyncio
import flet as ft
import matplotlib.pyplot as plt
from flet_charts import MatplotlibChartWithToolbar
from telemetrix import telemetrix

# ---------------- PINO ANALÓGICO ----------------
ANALOG_PIN0 = 0  # LDR analógico A0

# ---------------- PLACA ----------------
board = telemetrix.Telemetrix()
analog_values = {ANALOG_PIN0: 0}

# ---------------- CALLBACK ----------------
def ldr_callback(data):
    pin = data[1]
    value = data[2]
    analog_values[pin] = value

board.set_pin_mode_analog_input(ANALOG_PIN0, callback=ldr_callback)

# Thread para manter a placa "ativa"
def read_analog():
    while True:
        time.sleep(0.1)

threading.Thread(target=read_analog, daemon=True).start()

# ---------------- APP ----------------
async def main(page: ft.Page):
    page.title = "Luminosidade LDR"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ---------------- BARRA DE LUMINOSIDADE ----------------
    bar_width = 400
    bar_height = 30

    progress_bar = ft.ProgressBar(value=0, width=bar_width, height=bar_height, color="yellow")
    progress_text = ft.Text("0.00 V", size=20)

    ldr_container = ft.Container(
        content=ft.Column([
            ft.Text("Sensor LDR - Luminosidade", size=20, weight="bold"),
            ft.Row([
                ft.Text("Claro", size=16),
                progress_bar,
                ft.Text("Escuro", size=16),
            ], alignment=ft.MainAxisAlignment.CENTER),
            progress_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        bgcolor="black",
        padding=20,
        border_radius=15,
        expand=True
    )

    # ---------------- GRÁFICO ----------------
    samples = 100
    x = list(range(samples))
    ldr_data = [0]*samples

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.set_ylim(0, 5)
    ax.set_xlim(0, samples-1)
    ax.set_title("Luminosidade em tempo real")
    ax.set_xlabel("Amostras")
    ax.set_ylabel("Tensão (V)")
    ax.grid(True, linestyle="--", alpha=0.5)
    line_ldr, = ax.plot(x, ldr_data, color="yellow", label="Luminosidade (V)")
    ax.legend()
    fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.2)  # deixa "Amostras" visível

    chart = MatplotlibChartWithToolbar(figure=fig, expand=True, height=300)

    # ---------------- BOTÃO SAIR ----------------
    async def sair():
        board.shutdown()
        await page.window.close()

    exit_btn = ft.Button("Sair", icon=ft.Icons.EXIT_TO_APP, on_click=sair)

    # ---------------- LAYOUT ----------------
    page.add(
        ft.Column([
            ldr_container,
            ft.Container(chart, width=600, height=300),
            exit_btn
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # ---------------- LOOP PRINCIPAL ----------------
    while True:
        # Lê o valor do LDR
        ldr_value = analog_values[ANALOG_PIN0]
        voltage = ldr_value * (5.0 / 1023)

        # Atualiza barra e texto
        progress_bar.value = voltage / 5.0
        progress_text.value = f"{voltage:.2f} V"

        # Atualiza gráfico
        ldr_data.append(voltage)
        ldr_data.pop(0)
        line_ldr.set_ydata(ldr_data)
        fig.canvas.draw_idle()  # corrige travamento do gráfico

        page.update()
        await asyncio.sleep(0.2)

# ---------------- EXECUÇÃO ----------------
ft.run(main)
