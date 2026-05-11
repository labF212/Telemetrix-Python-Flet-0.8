import asyncio
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

fan_auto_until = 0.0
FAN_AUTO_TIME = 5.0
fan_state = {"manual": False}

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

    # ================= DHT11 – BARRAS VERTICAIS =================
    bar_width = 40
    bar_height = 220

    temp_text = ft.Text("0.0 °C")
    hum_text = ft.Text("0.0 %")

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

    # ======== GRÁFICO ========
    samples = 60
    x = list(range(samples))
    temp_data = [0]*samples
    hum_data = [0]*samples

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.set_title("DHT11 – Tempo (s)")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Valor")
    ax.set_ylim(0, 100)
    ax.grid(True)

    lt, = ax.plot(x, temp_data, label="Temp (°C)", color="red")
    lh, = ax.plot(x, hum_data, label="Hum (%)", color="blue")
    ax.legend()

    chart = MatplotlibChartWithToolbar(figure=fig, height=300)

    dht_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Medição de Temperatura e Humidade – DHT11 (Pino 11)", weight="bold"),
            ft.Row([
                ft.Column([ft.Text("Temperatura"), temp_bar, temp_text],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([ft.Text("Humidade"), hum_bar, hum_text],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
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

    def servo_manual(e):
        ang = int(servo_slider.value)
        board.servo_write(SERVO_PIN, ang)
        servo_text.value = f"Ângulo: {ang} °"
        page.update()

    servo_slider.on_change = servo_manual

    servo_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Servo – Pino 10", weight="bold"),
            servo_text,
            servo_slider
        ])
    )

    # ================= VENTOINHA MANUAL =================
    fan_manual_led = ft.Icon(ft.Icons.CIRCLE, color="red", size=30)
    fan_manual_text = ft.Text("Ventoinha desligada")

    def fan_on(e):
        fan_state["manual"] = True

    def fan_off(e):
        fan_state["manual"] = False

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

    # ================= PIR AUTO =================
    pir_led = ft.Icon(ft.Icons.CIRCLE, color="red", size=30)
    fan_auto_text = ft.Text("Ventoinha desligada")

    pir_box = ft.Container(
        padding=15,
        bgcolor="black",
        border_radius=12,
        content=ft.Column([
            ft.Text("Ventoinha Automática – PIR Pino 2", weight="bold"),
            pir_led,
            fan_auto_text
        ])
    )

    # ================= LOOP =================
    async def loop():
        while True:
            temp_text.value = f"{temperature:.1f} °C"
            hum_text.value = f"{humidity:.1f} %"

            temp_fill.height = min((temperature / 50) * bar_height, bar_height)
            hum_fill.height = min((humidity / 100) * bar_height, bar_height)

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

            if fan_state["manual"] or auto_active:
                board.digital_write(RELE_PIN, 1)
                fan_manual_led.color = "green" if fan_state["manual"] else "red"
                fan_auto_text.value = (
                    f"Ventoinha automática ({fan_auto_until-now:.1f}s)"
                    if auto_active else "Ventoinha manual ligada"
                )
            else:
                board.digital_write(RELE_PIN, 0)
                fan_manual_led.color = "red"
                fan_auto_text.value = "Ventoinha desligada"

            pir_led.color = "green" if auto_active else "red"

            page.update()
            await asyncio.sleep(0.2)

    asyncio.create_task(loop())

    # ================= SAIR =================
    async def on_exit(e):
        board.servo_write(SERVO_PIN, 90)
        await asyncio.sleep(0.3)
        board.digital_write(RELE_PIN, 0)
        board.shutdown()
        await page.window.destroy()

    # ================= LAYOUT =================
    page.add(
        ft.Column([
            dht_box,
            ft.Row([ldr_box, dist_box], spacing=20),
            servo_box,
            ft.Row([fan_manual_box, pir_box], spacing=20),
            ft.Button("Sair", icon=ft.Icons.EXIT_TO_APP, on_click=on_exit)
        ], spacing=20)
    )

ft.run(main)
