import asyncio
import threading
import time
import flet as ft
import matplotlib.pyplot as plt
from flet_charts import MatplotlibChartWithToolbar
from telemetrix import telemetrix

# ================= HARDWARE =================
DHT_PIN = 11
LDR_PIN = 0
TRIG_PIN = 8
ECHO_PIN = 9
PWM_PIN = 6
RELE_PIN = 7
PIR_PIN = 2
SERVO_PIN = 10

board = telemetrix.Telemetrix()

# ================= VARIÁVEIS =================
temperature = 0.0
humidity = 0.0
ldr_value = 0
distance_cm = 0

fan_state = {"manual": False}
fan_auto_until = 0.0
FAN_AUTO_TIME = 5.0

# ================= CALLBACKS =================
def dht_callback(data):
    global temperature, humidity
    if data[1] == 0:
        humidity = data[4]
        temperature = data[5]

def ldr_callback(data):
    global ldr_value
    ldr_value = data[2]

def sonar_callback(data):
    global distance_cm
    distance_cm = data[2]

def pir_callback(data):
    global fan_auto_until
    if data[2] == 1:
        fan_auto_until = time.time() + FAN_AUTO_TIME

# ================= INIT =================
board.set_pin_mode_dht(DHT_PIN, dht_type=22, callback=dht_callback)
board.set_pin_mode_analog_input(LDR_PIN, callback=ldr_callback)
board.set_pin_mode_sonar(TRIG_PIN, ECHO_PIN, callback=sonar_callback)
board.set_pin_mode_digital_input(PIR_PIN, callback=pir_callback)
board.set_pin_mode_analog_output(PWM_PIN)
board.set_pin_mode_digital_output(RELE_PIN)
board.set_pin_mode_servo(SERVO_PIN)

# ================= APP =================
async def main(page: ft.Page):
    page.title = "Casa Inteligente – Arduino + Flet"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # =========================================================
    # DHT11 – BARRAS VERTICAIS CORRIGIDAS
    # =========================================================
    bar_width = 50
    bar_height = 220

    temp_value = ft.Text("0.0 °C")
    hum_value = ft.Text("0.0 %")

    temp_fill = ft.Container(width=bar_width, height=0, bgcolor="red")
    hum_fill = ft.Container(width=bar_width, height=0, bgcolor="blue")

    temp_bar = ft.Container(
        width=bar_width,
        height=bar_height,
        bgcolor="#444444",
        content=ft.Column([temp_fill], alignment=ft.MainAxisAlignment.END)
    )

    hum_bar = ft.Container(
        width=bar_width,
        height=bar_height,
        bgcolor="#444444",
        content=ft.Column([hum_fill], alignment=ft.MainAxisAlignment.END)
    )

    # ================= GRÁFICO =================
    samples = 60
    x = list(range(samples))
    temp_data = [0] * samples
    hum_data = [0] * samples

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.set_title("DHT11")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Valor")
    ax.set_ylim(0, 100)
    ax.grid(True)

    lt, = ax.plot(x, temp_data, label="Temperatura (°C)", color="red")
    lh, = ax.plot(x, hum_data, label="Humidade (%)", color="blue")
    ax.legend()

    chart = MatplotlibChartWithToolbar(figure=fig, height=300)

    dht_box = ft.Container(
        padding=20,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Medição de Temperatura e Humidade – DHT11 (Pino 11)", weight="bold"),
            ft.Row([
                ft.Column([
                    ft.Text("Temperatura"),
                    temp_bar,
                    temp_value
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.Text("Humidade"),
                    hum_bar,
                    hum_value
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                chart
            ], spacing=30)
        ])
    )

    # ================= LDR =================
    ldr_bar = ft.ProgressBar(width=300, color="yellow")
    ldr_text = ft.Text()

    ldr_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Sensor de Luminosidade (LDR) – A0", weight="bold"),
            ldr_text,
            ldr_bar
        ])
    )

    # ================= DISTÂNCIA =================
    dist_bar = ft.ProgressBar(width=300, color="green")
    dist_text = ft.Text()

    dist_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Sensor Ultrassónico – TRIG 8 / ECHO 9", weight="bold"),
            dist_text,
            dist_bar
        ])
    )

    # ================= SERVO =================
    servo_text = ft.Text("Ângulo: 90 °")
    servo_slider = ft.Slider(min=0, max=180, value=90)
    servo_mode = ft.RadioGroup(
        value="manual",
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="auto", label="Automático")
        ])
    )
    servo_flag = {"run": False}

    def servo_manual(e):
        if servo_mode.value == "manual":
            ang = int(servo_slider.value)
            board.servo_write(SERVO_PIN, ang)
            servo_text.value = f"Ângulo: {ang} °"
            page.update()

    def servo_auto_run():
        while servo_flag["run"]:
            for ang in range(0, 181, 5):
                if not servo_flag["run"]:
                    return
                board.servo_write(SERVO_PIN, ang)
                servo_text.value = f"Ângulo: {ang} °"
                page.update()
                time.sleep(0.1)
            for ang in range(180, -1, -5):
                if not servo_flag["run"]:
                    return
                board.servo_write(SERVO_PIN, ang)
                servo_text.value = f"Ângulo: {ang} °"
                page.update()
                time.sleep(0.1)

    def servo_mode_change(e):
        if servo_mode.value == "manual":
            servo_flag["run"] = False
            servo_slider.visible = True
        else:
            servo_flag["run"] = True
            servo_slider.visible = False
            threading.Thread(target=servo_auto_run, daemon=True).start()
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

    # ================= MOTOR PWM =================
    pwm_state = {"value": 0, "mode": "manual", "task": None}
    pwm_text = ft.Text("0 PWM")
    pwm_slider = ft.Slider(min=0, max=100, divisions=100, width=300)
    pwm_mode = ft.RadioGroup(
        value="manual",
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="auto", label="Automático")
        ])
    )

    async def pwm_auto():
        try:
            while pwm_state["mode"] == "auto":
                for i in range(256):
                    if pwm_state["mode"] != "auto":
                        return
                    board.analog_write(PWM_PIN, i)
                    await asyncio.sleep(0.03)
                for i in range(255, -1, -1):
                    if pwm_state["mode"] != "auto":
                        return
                    board.analog_write(PWM_PIN, i)
                    await asyncio.sleep(0.03)
        except asyncio.CancelledError:
            pass

    async def on_slider(e):
        if pwm_state["mode"] == "manual":
            val = int(pwm_slider.value * 2.55)
            board.analog_write(PWM_PIN, val)

    async def on_mode(e):
        if pwm_state["task"]:
            pwm_state["task"].cancel()
            pwm_state["task"] = None
        if pwm_mode.value == "manual":
            pwm_state["mode"] = "manual"
            pwm_slider.visible = True
            board.analog_write(PWM_PIN, 0)
        else:
            pwm_state["mode"] = "auto"
            pwm_slider.visible = False
            pwm_state["task"] = asyncio.create_task(pwm_auto())
        page.update()

    pwm_slider.on_change = on_slider
    pwm_mode.on_change = on_mode

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

    # ================= LOOP PRINCIPAL =================
    async def loop():
        while True:
            # DHT
            temp_value.value = f"{temperature:.1f} °C"
            hum_value.value = f"{humidity:.1f} %"

            temp_fill.height = min((temperature / 50) * bar_height, bar_height)
            hum_fill.height = min((humidity / 100) * bar_height, bar_height)

            temp_data.append(temperature)
            hum_data.append(humidity)
            temp_data.pop(0)
            hum_data.pop(0)
            lt.set_ydata(temp_data)
            lh.set_ydata(hum_data)
            chart.figure.canvas.draw_idle()

            # LDR
            ldr_v = ldr_value * 5 / 1023
            ldr_text.value = f"Luminosidade: {ldr_v:.2f} V"
            ldr_bar.value = ldr_v / 5

            # DIST
            dist_text.value = f"Distância: {distance_cm/100:.2f} m"
            dist_bar.value = min(distance_cm / 200, 1)

            page.update()
            await asyncio.sleep(0.2)

    asyncio.create_task(loop())

    page.add(
        ft.Column([
            dht_box,
            ft.Row([ldr_box, dist_box], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([servo_box, pwm_box], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    )

ft.run(main)
