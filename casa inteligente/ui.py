
import asyncio
import time
import flet as ft
import matplotlib.pyplot as plt
from flet_charts import MatplotlibChartWithToolbar
import hardware
import logic

async def build(page: ft.Page):
    page.title = "Casa Inteligente"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    hardware.init_hardware(
        logic.dht_callback,
        logic.ldr_callback,
        logic.sonar_callback,
        logic.pir_callback
    )

    bar_h, bar_w = 220, 60
    temp_value = ft.Text()
    hum_value = ft.Text()

    temp_fill = ft.Container(width=bar_w, height=0, bgcolor="red")
    hum_fill = ft.Container(width=bar_w, height=0, bgcolor="blue")

    temp_bar = ft.Container(
        content=ft.Column([temp_fill], alignment=ft.MainAxisAlignment.END),
        width=bar_w, height=bar_h, bgcolor="grey"
    )
    hum_bar = ft.Container(
        content=ft.Column([hum_fill], alignment=ft.MainAxisAlignment.END),
        width=bar_w, height=bar_h, bgcolor="grey"
    )

    samples = 60
    x = list(range(samples))
    tdata = [0]*samples
    hdata = [0]*samples

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.set_xlim(0, samples)
    ax.set_ylim(0, 100)
    ax.set_title("Temperatura e Humidade")
    ax.set_xlabel("Tempo (s)")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    lt, = ax.plot(x, tdata, color="red", label="Temp")
    lh, = ax.plot(x, hdata, color="blue", label="Hum")
    ax.legend()

    chart = MatplotlibChartWithToolbar(figure=fig, height=300)

    fan_led = ft.Icon(ft.Icons.CIRCLE, size=40)
    fan_text = ft.Text()

    def fan_on(e): logic.fan_state["manual"] = True
    def fan_off(e): logic.fan_state["manual"] = False

    async def loop():
        while True:
            temp = logic.temperature
            hum = logic.humidity

            temp_value.value = f"{temp:.1f} °C"
            hum_value.value = f"{hum:.1f} %"

            temp_fill.height = min((temp/100)*bar_h, bar_h)
            hum_fill.height = min((hum/100)*bar_h, bar_h)

            tdata.append(temp); tdata.pop(0)
            hdata.append(hum); hdata.pop(0)
            lt.set_ydata(tdata)
            lh.set_ydata(hdata)
            chart.figure.canvas.draw_idle()

            now = time.time()
            run = logic.fan_should_run(now)
            hardware.set_fan(run)

            fan_led.color = "green" if run else "red"
            fan_text.value = "Ligada" if run else "Desligada"

            page.update()
            await asyncio.sleep(0.2)

    asyncio.create_task(loop())

    page.add(ft.Column([
        temp_bar, temp_value,
        hum_bar, hum_value,
        chart,
        fan_led, fan_text,
        ft.Row([ft.Button("Ligar", on_click=fan_on),
                ft.Button("Desligar", on_click=fan_off)])
    ], spacing=20))
