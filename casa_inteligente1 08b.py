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

    # ================= BARRAS DHT =================
    bar_width = 60
    bar_height = 220

    temp_value = ft.Text("0.0 °C")
    hum_value = ft.Text("0.0 %")

    temp_fill = ft.Container(width=bar_width, height=0, bgcolor="red")
    hum_fill = ft.Container(width=bar_width, height=0, bgcolor="blue")

    temp_bar = ft.Container(
        content=ft.Column([temp_fill], alignment=ft.MainAxisAlignment.END),
        width=bar_width,
        height=bar_height,
        bgcolor="grey"
    )

    hum_bar = ft.Container(
        content=ft.Column([hum_fill], alignment=ft.MainAxisAlignment.END),
        width=bar_width,
        height=bar_height,
        bgcolor="grey"
    )

    # ================= GRÁFICO =================
    samples = 60
    time_data = list(range(samples))
    temp_data = [0]*samples
    hum_data = [0]*samples

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.set_ylim(0, 100)
    ax.set_xlim(0, samples)
    ax.set_title("DHT11 – Medida de Temperatura e Humidade")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Valor")
    ax.grid(True, linestyle="--", alpha=0.5)

    lt, = ax.plot(time_data, temp_data, label="DHT11", color="red")
    lh, = ax.plot(time_data, hum_data, color="blue")
    ax.legend()

    chart = MatplotlibChartWithToolbar(figure=fig, height=300)

    dht_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Sensor DHT11 – Pino 11", weight="bold"),
            ft.Row([
                ft.Column([ft.Text("Temperatura"), temp_bar, temp_value],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([ft.Text("Humidade"), hum_bar, hum_value],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                chart
            ], spacing=30)
        ])
    )

    # ================= LDR =================
    ldr_bar = ft.ProgressBar(width=bar_width*2, color="yellow")
    ldr_text = ft.Text()

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

    # ================= DISTÂNCIA =================
    dist_bar = ft.ProgressBar(width=bar_width*2, color="green")
    dist_text = ft.Text()

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

    def servo_auto():
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
            threading.Thread(target=servo_auto, daemon=True).start()
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
    pwm_state = {"mode": "manual", "task": None}
    pwm_slider = ft.Slider(min=0, max=100, divisions=100, width=300)
    pwm_mode = ft.RadioGroup(
        value="manual",
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="auto", label="Automático")
        ])
    )

    async def pwm_auto():
        while pwm_state["mode"] == "auto":
            for i in range(256):
                if pwm_state["mode"] != "auto": return
                board.analog_write(PWM_PIN, i)
                await asyncio.sleep(0.03)
            for i in range(255, -1, -1):
                if pwm_state["mode"] != "auto": return
                board.analog_write(PWM_PIN, i)
                await asyncio.sleep(0.03)

    async def pwm_slider_change(e):
        if pwm_state["mode"] == "manual":
            board.analog_write(PWM_PIN, int(pwm_slider.value * 2.55))

    async def pwm_mode_change(e):
        if pwm_state["task"]:
            pwm_state["task"].cancel()
        if pwm_mode.value == "manual":
            pwm_state["mode"] = "manual"
            pwm_slider.visible = True
            board.analog_write(PWM_PIN, 0)
        else:
            pwm_state["mode"] = "auto"
            pwm_slider.visible = False
            pwm_state["task"] = asyncio.create_task(pwm_auto())
        page.update()

    pwm_slider.on_change = pwm_slider_change
    pwm_mode.on_change = pwm_mode_change

    pwm_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Motor PWM – Pino 6", weight="bold"),
            pwm_slider,
            pwm_mode
        ])
    )

    # ================= VENTOINHA MANUAL =================
    led_size = 40
    fan_manual_led = ft.Icon(ft.Icons.CIRCLE, color="red", size=led_size)
    fan_manual_text = ft.Text("Ventoinha desligada")

    def fan_on(e): fan_state["manual"] = True
    def fan_off(e): fan_state["manual"] = False

    fan_manual_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Ventoinha Manual – Pino 7", weight="bold"),
            fan_manual_led,
            fan_manual_text,
            ft.Row([
                ft.Button("Ligar", icon=ft.Icons.POWER, icon_color="green", on_click=fan_on),
                ft.Button("Desligar", icon=ft.Icons.POWER_OFF, icon_color="red", on_click=fan_off)
            ])
        ])
    )

    # ================= VENTOINHA AUTOMÁTICA =================
    fan_auto_led = ft.Icon(ft.Icons.CIRCLE, color="red", size=led_size)
    fan_auto_text = ft.Text("Ventoinha desligada")
    pir_led = ft.Icon(ft.Icons.CIRCLE, color="red", size=led_size)
    pir_text = ft.Text("Sem deteção")

    pir_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Ventoinha Automática – PIR Pino 2", weight="bold"),
            ft.Row([pir_led, pir_text], spacing=10),
            ft.Row([fan_auto_led, fan_auto_text], spacing=10)
        ])
    )

    # ================= LOOP =================
    async def loop():
        while True:
            temp_value.value = f"{temperature:.1f} °C"
            hum_value.value = f"{humidity:.1f} %"

            temp_fill.height = min((temperature/100)*bar_height, bar_height)
            hum_fill.height = min((humidity/100)*bar_height, bar_height)

            ldr_v = ldr_value * 5 / 1023
            ldr_text.value = f"Luminosidade: {ldr_v:.2f} V"
            ldr_bar.value = ldr_v / 5

            dist_text.value = f"Distância: {distance_cm/100:.2f} m"
            dist_bar.value = min(distance_cm/200, 1)

            temp_data.append(temperature)
            hum_data.append(humidity)
            temp_data.pop(0)
            hum_data.pop(0)
            lt.set_ydata(temp_data)
            lh.set_ydata(hum_data)
            chart.figure.canvas.draw_idle()

            now = time.time()
            auto_active = now < fan_auto_until

            if fan_state["manual"]:
                board.digital_write(RELE_PIN, 1)
                fan_manual_led.color = "green"
                fan_manual_text.value = "Ventoinha ligada (manual)"
            elif auto_active:
                board.digital_write(RELE_PIN, 1)
                remaining = fan_auto_until - now
                fan_auto_led.color = "green"
                fan_auto_text.value = f"Ventoinha automática ({remaining:.1f}s)"
            else:
                board.digital_write(RELE_PIN, 0)
                fan_manual_led.color = fan_auto_led.color = "red"
                fan_manual_text.value = fan_auto_text.value = "Ventoinha desligada"

            pir_led.color = "green" if auto_active else "red"
            pir_text.value = "Detetou objeto" if auto_active else "Sem deteção"

            page.update()
            await asyncio.sleep(0.2)

    asyncio.create_task(loop())

    async def on_exit(e):
        board.servo_write(SERVO_PIN, 90)
        await asyncio.sleep(0.3)
        board.digital_write(RELE_PIN, 0)
        board.shutdown()
        await page.window.destroy()

    page.add(
        ft.Column([
            dht_box,
            ft.Row([ldr_box, dist_box], spacing=20),
            ft.Row([servo_box, pwm_box], spacing=20),
            ft.Row([fan_manual_box, pir_box], spacing=20),
            ft.Button("Sair", icon=ft.Icons.EXIT_TO_APP, on_click=on_exit)
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.run(main)
