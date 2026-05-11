import time
import threading
import asyncio
import flet as ft
from telemetrix import telemetrix
import matplotlib.pyplot as plt
from flet_charts import MatplotlibChartWithToolbar

# ---------------- PINOS ----------------
TEMP_PIN = 1
HUMIDITY_PIN = 5

board = telemetrix.Telemetrix()
analog_values = {TEMP_PIN: 0, HUMIDITY_PIN: 0}

# ---------------- CALLBACK ----------------
def callback(data):
    analog_values[data[1]] = data[2]

board.set_pin_mode_analog_input(TEMP_PIN, callback=callback)
board.set_pin_mode_analog_input(HUMIDITY_PIN, callback=callback)

def read_analog_values():
    while True:
        time.sleep(0.1)

threading.Thread(target=read_analog_values, daemon=True).start()

# ---------------- CONVERSÕES ----------------
def voltage_to_temperature(v):
    return (v / 5.0) * 120

def voltage_to_humidity(v):
    return 20 + (v / 5.0) * 60

# ---------------- APP ----------------
async def main(page: ft.Page):
    page.title = "Temperatura e Humidade - Flet + Telemetrix"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    bar_width, bar_height = 280, 50

    # Textos
    temp_text = ft.Text("Temperatura: 0.0 ºC", size=16)
    humid_text = ft.Text("Humidade: 0.0 %", size=16)

    temp_value_text = ft.Text("0.0 ºC")
    humid_value_text = ft.Text("0.0 %")

    # ---------------- BARRAS ----------------
    temp_bar = ft.Container(
        content=ft.Stack([
            ft.Container(width=bar_width, height=bar_height, bgcolor="grey"),
            ft.Container(
                width=0,
                height=bar_height,
                bgcolor="red",
                alignment=ft.Alignment(-1, -1)
            ),
            ft.Container(
                content=temp_value_text,
                alignment=ft.Alignment(0, 0)
            ),
        ]),
        width=bar_width,
        height=bar_height,
    )

    humid_bar = ft.Container(
        content=ft.Stack([
            ft.Container(width=bar_width, height=bar_height, bgcolor="grey"),
            ft.Container(
                width=0,
                height=bar_height,
                bgcolor="blue",
                alignment=ft.Alignment(-1, -1)
            ),
            ft.Container(
                content=humid_value_text,
                alignment=ft.Alignment(0, 0)
            ),
        ]),
        width=bar_width,
        height=bar_height,
    )

    # ---------------- MATPLOTLIB ----------------
    samples = 100
    x = list(range(samples))
    temp_data = [0] * samples
    humid_data = [0] * samples

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.set_ylim(0, 130)
    ax.set_xlim(0, samples - 1)
    ax.set_title("Leituras em Tempo Real")
    ax.set_xlabel("Amostras")
    ax.set_ylabel("Valor")
    ax.grid(True, linestyle="--", alpha=0.5)

    line_temp, = ax.plot(x, temp_data, color="red", label="Temperatura (ºC)")
    line_hum, = ax.plot(x, humid_data, color="blue", label="Humidade (%)")
    ax.legend()

    chart = MatplotlibChartWithToolbar(
        figure=fig,
        expand=True,
        height=300
    )

    # ---------------- BOTÃO SAIR (CORRETO NO 0.8) ----------------
    async def on_exit(e):
        board.shutdown()
        await page.window.close()

    exit_btn = ft.Button(
        "Sair",
        icon=ft.Icons.EXIT_TO_APP,
        on_click=on_exit
    )

    # ---------------- LAYOUT ----------------
    page.add(
        ft.Column([
            temp_text,
            temp_bar,
            humid_text,
            humid_bar,
            ft.Container(chart, width=600, height=300),
            exit_btn
        ], spacing=15)
    )

    # ---------------- LOOP ----------------
    while True:
        v_temp = analog_values[TEMP_PIN] * (5.0 / 1023)
        v_hum = analog_values[HUMIDITY_PIN] * (5.0 / 1023)

        temperature = voltage_to_temperature(v_temp)
        humidity = voltage_to_humidity(v_hum)

        temp_text.value = f"Temperatura: {temperature:.1f} ºC"
        humid_text.value = f"Humidade: {humidity:.1f} %"

        temp_value_text.value = f"{temperature:.1f} ºC"
        humid_value_text.value = f"{humidity:.1f} %"

        temp_bar.content.controls[1].width = min((temperature / 120) * bar_width, bar_width)
        humid_bar.content.controls[1].width = min(((humidity - 20) / 60) * bar_width, bar_width)

        temp_data.append(temperature)
        humid_data.append(humidity)
        temp_data.pop(0)
        humid_data.pop(0)

        line_temp.set_ydata(temp_data)
        line_hum.set_ydata(humid_data)

        chart.figure.canvas.draw_idle()

        page.update()
        await asyncio.sleep(0.5)

# ---------------- RUN ----------------
ft.run(main)
