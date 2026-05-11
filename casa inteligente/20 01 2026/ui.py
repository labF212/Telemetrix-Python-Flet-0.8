# ui.py
import flet as ft
import asyncio
import time
import threading
import hardware
import logic
import matplotlib.pyplot as plt
from flet_charts import MatplotlibChartWithToolbar


async def build(page: ft.Page):
    page.title = "Casa Inteligente – Arduino + Flet"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    bar_width = 60
    bar_height = 220

    
    # ======================= DHT =============================
    
    temp_value = ft.Text("0.0 °C")
    hum_value = ft.Text("0.0 %")

    temp_fill = ft.Container(width=bar_width, height=0, bgcolor="red")
    hum_fill = ft.Container(width=bar_width, height=0, bgcolor="blue")

    temp_bar = ft.Container(
        width=bar_width,
        height=bar_height,
        bgcolor="grey",
        content=ft.Column([temp_fill], alignment=ft.MainAxisAlignment.END)
    )

    hum_bar = ft.Container(
        width=bar_width,
        height=bar_height,
        bgcolor="grey",
        content=ft.Column([hum_fill], alignment=ft.MainAxisAlignment.END)
    )

    temp_col = ft.Column([
        ft.Text("Temperatura", weight="bold"),
        temp_bar,
        temp_value
    ], alignment=ft.MainAxisAlignment.CENTER)

    hum_col = ft.Column([
        ft.Text("Humidade", weight="bold"),
        hum_bar,
        hum_value
    ], alignment=ft.MainAxisAlignment.CENTER)

    # --------- Gráfico ----------
    samples = 60
    temp_data = [0] * samples
    hum_data = [0] * samples
    time_data = list(range(samples))

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.set_ylim(0, 100)
    ax.set_xlim(0, samples)
    ax.set_title("DHT11")
    lt, = ax.plot(time_data, temp_data, label="Temp", color="red")
    lh, = ax.plot(time_data, hum_data, label="Hum", color="blue")
    ax.legend()

    chart = MatplotlibChartWithToolbar(figure=fig, height=260)

    dht_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Row(
            [
                ft.Row([temp_col, hum_col], spacing=40),
                chart
            ],
            spacing=40
        )
    )

    
    # ======================== LDR ============================
    
    ldr_text = ft.Text()
    ldr_bar = ft.ProgressBar(width=bar_width * 2, color="yellow")

    ldr_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Sensor Luminosidade – A0", weight="bold"),
            ldr_text,
            ldr_bar
        ])
    )

    
    # ===================== DISTÂNCIA =========================
    
    dist_text = ft.Text()
    dist_bar = ft.ProgressBar(width=bar_width * 2, color="green")

    dist_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Ultrassónico – TRIG 8 / ECHO 9", weight="bold"),
            dist_text,
            dist_bar
        ])
    )

    
    # ======================== SERVO ==========================
    
    servo_text = ft.Text("Ângulo: 90 °")
    servo_slider = ft.Slider(min=0, max=180, value=90)

    servo_mode = ft.RadioGroup(
        value="manual",
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="auto", label="Automático")
        ])
    )

    def servo_manual(e):
        if servo_mode.value == "manual":
            ang = int(servo_slider.value)
            logic.servo_write(ang)
            servo_text.value = f"Ângulo: {ang} °"
            page.update()

    def servo_mode_change(e):
        if servo_mode.value == "manual":
            logic.stop_servo_auto()
            servo_slider.visible = True
        else:
            servo_slider.visible = False
            logic.start_servo_auto(
                lambda ang: (
                    setattr(servo_text, "value", f"Ângulo: {ang} °"),
                    page.update()
                )
            )
        page.update()

    servo_slider.on_change = servo_manual
    servo_mode.on_change = servo_mode_change

    servo_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Servo – Pino 10", weight="bold"),
            servo_text,
            servo_slider,
            servo_mode
        ])
    )

    
    # ======================== PWM ============================
    
    pwm_slider = ft.Slider(min=0, max=100, divisions=100, width=300)
    pwm_text = ft.Text("PWM: 0 a 254")

    pwm_mode = ft.RadioGroup(
        value="manual",
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="auto", label="Automático")
        ])
    )

    async def pwm_slider_change(e):
        if logic.pwm_state["mode"] == "manual":
            pwm_255 = int(pwm_slider.value * 2.55)
            logic.pwm_manual(pwm_slider.value)
            pwm_text.value = f"PWM: {pwm_255}"
            page.update()
            #logic.pwm_manual(pwm_slider.value)

    async def pwm_mode_change(e):
        if logic.pwm_state["task"]:
            logic.pwm_state["task"].cancel()

        if pwm_mode.value == "manual":
            logic.pwm_state["mode"] = "manual"
            pwm_slider.visible = True
            logic.pwm_manual(0)
        else:
            logic.pwm_state["mode"] = "auto"
            pwm_slider.visible = False
            logic.pwm_state["task"] = asyncio.create_task(logic.pwm_auto())

        page.update()

    pwm_slider.on_change = pwm_slider_change
    pwm_mode.on_change = pwm_mode_change

    pwm_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Motor PWM – Pino 6", weight="bold"),
            pwm_text,
            pwm_slider,
            pwm_mode
        ])
    )

    
    # ===================== VENTOINHAS ========================
    
    fan_led = ft.Icon(ft.Icons.CIRCLE, color="red", size=40)
    fan_text = ft.Text("Ventoinha desligada")

    pir_led = ft.Icon(ft.Icons.CIRCLE, color="red", size=40)
    pir_text = ft.Text("Sem deteção")

    fan_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Ventoinha – Pino 7 / PIR 2", weight="bold"),
            ft.Row([fan_led, fan_text]),
            ft.Row([pir_led, pir_text]),
            ft.Row([
                ft.Button("Ligar", on_click=lambda e: logic.fan_on()),
                ft.Button("Desligar", on_click=lambda e: logic.fan_off())
            ])
        ])
    )

    
    # ======================= LOOP ============================
 
    async def loop():
        while True:
            # DHT
            temp_value.value = f"{hardware.temperature:.1f} °C"
            hum_value.value = f"{hardware.humidity:.1f} %"
            temp_fill.height = min((hardware.temperature / 100) * bar_height, bar_height)
            hum_fill.height = min((hardware.humidity / 100) * bar_height, bar_height)

            temp_data.append(hardware.temperature)
            hum_data.append(hardware.humidity)
            temp_data.pop(0)
            hum_data.pop(0)
            lt.set_ydata(temp_data)
            lh.set_ydata(hum_data)
            chart.figure.canvas.draw_idle()

            # LDR
            ldr_v = hardware.ldr_value * 5 / 1023
            ldr_text.value = f"Luminosidade: {ldr_v:.2f} V"
            ldr_bar.value = ldr_v / 5

            # Distância
            dist_text.value = f"Distância: {hardware.distance_cm / 100:.2f} m"
            dist_bar.value = min(hardware.distance_cm / 200, 1)

            # Ventoinha
            fan_on_state, auto_active = logic.update_fan()
            fan_led.color = "green" if fan_on_state else "red"
            fan_text.value = "Ventoinha ligada" if fan_on_state else "Ventoinha desligada"
            pir_led.color = "green" if auto_active else "red"
            pir_text.value = "Detetou objeto" if auto_active else "Sem deteção"

            page.update()
            await asyncio.sleep(0.2)

    asyncio.create_task(loop())

 
    # ====================== SAIR =============================
   
    async def on_exit(e):
        logic.stop_servo_auto()
        hardware.board.servo_write(hardware.SERVO_PIN, 90)
        await asyncio.sleep(0.3)
        hardware.board.digital_write(hardware.RELE_PIN, 0)
        hardware.board.shutdown()
        await page.window.destroy()

 
    # ======================= UI ==============================

    page.add(
        ft.Column([
            dht_box,
            ft.Row([ldr_box, dist_box], spacing=20),
            ft.Row([servo_box, pwm_box], spacing=20),
            fan_box,
            ft.Button("Sair", icon=ft.Icons.EXIT_TO_APP, on_click=on_exit)
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
