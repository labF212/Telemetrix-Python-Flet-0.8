import time
import asyncio
import threading
import flet as ft
from telemetrix import telemetrix
import matplotlib.pyplot as plt
from flet.matplotlib_chart import MatplotlibChart

# -------------------------------
# CONFIGURAÇÃO DOS SENSORES
# -------------------------------
DHT_PIN = 11
ANALOG_PIN0 = 0
PIN_RELE = 7
PIN_PIR = 2
TRIGGER_PIN = 8
ECHO_PIN = 9
SERVO_PIN = 10
DIGITAL_PIN6 = 6

board = telemetrix.Telemetrix()

temperature = 0.0
humidity = 0.0
analog_values = {ANALOG_PIN0: 0}
last_distance = None
error_message = ""
min_range = 0
max_range = 400

off_timer = {"t": None}

# -------------------------------
# CALLBACKS
# -------------------------------
def dht_callback(data):
    global temperature, humidity
    if data[1] == 0:
        humidity = data[4]
        temperature = data[5]

def ldr_callback(data):
    analog_values[data[1]] = data[2]

def sonar_callback(data):
    global last_distance, error_message
    last_distance = data[2]
    error_message = ""

def control_relay(state: str):
    board.digital_write(PIN_RELE, 1 if state == "ON" else 0)

def move_servo(angle):
    board.servo_write(SERVO_PIN, angle)

# Inicializa sensores
board.set_pin_mode_dht(DHT_PIN, dht_type=22, callback=dht_callback)
board.set_pin_mode_analog_input(ANALOG_PIN0, callback=ldr_callback)
board.set_pin_mode_digital_output(PIN_RELE)
board.set_pin_mode_sonar(TRIGGER_PIN, ECHO_PIN, sonar_callback)
board.set_pin_mode_servo(SERVO_PIN)
board.set_pin_mode_analog_output(DIGITAL_PIN6)

# -------------------------------
# FUNÇÃO PRINCIPAL FLET
# -------------------------------
async def main(page: ft.Page):
    page.title = "Casa Inteligente Comandada por Arduino"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ALWAYS

    txt = ft.Row([
        ft.Image(
            src="Flet-for-arduino-with-Telemetrix-main/ips_tecno.jpg",
            width=200,
            height=120,
            fit=ft.ImageFit.CONTAIN
        ),
        ft.Text(
            "Bem vindo à nossa casa. Está a ver o resultado de um conjunto de sensores e atuadores",
            text_align="CENTER",
            weight="BOLD",
            size=18,
        )
    ], alignment="center", spacing=20)
    

    # ------------------- DHT22 -------------------
    bar_width, bar_height = 280, 50
    temp_text = ft.Text("Temperatura: 0.0 ºC", size=16)
    humid_text = ft.Text("Humidade: 0.0 %", size=16)
    temp_value_text = ft.Text("0.0 ºC", size=14, weight="bold")
    humid_value_text = ft.Text("0.0 %", size=14, weight="bold")

    temp_bar = ft.Container(content=ft.Stack([
        ft.Container(width=bar_width, height=bar_height, bgcolor="grey"),
        ft.Container(width=0, height=bar_height, bgcolor="red", alignment=ft.alignment.top_left),
        ft.Container(content=temp_value_text, alignment=ft.alignment.center),
    ]), width=bar_width, height=bar_height)

    humid_bar = ft.Container(content=ft.Stack([
        ft.Container(width=bar_width, height=bar_height, bgcolor="grey"),
        ft.Container(width=0, height=bar_height, bgcolor="blue", alignment=ft.alignment.top_left),
        ft.Container(content=humid_value_text, alignment=ft.alignment.center),
    ]), width=bar_width, height=bar_height)

    times = list(range(100))
    temp_data, humid_data = [0] * 100, [0] * 100
    fig_dht, ax_dht = plt.subplots(figsize=(6, 3))
    ax_dht.set_ylim(0, 100)
    line_temp, = ax_dht.plot(times, temp_data, label="Temperatura (ºC)", color='red')
    line_humid, = ax_dht.plot(times, humid_data, label="Humidade (%)", color='blue')
    ax_dht.legend(); ax_dht.grid(True)
    chart_dht = MatplotlibChart(fig_dht, expand=True)

    dht22_container = ft.Container(
        content=ft.Column([ft.Text("Sensor DHT22 - Temperatura e Humidade", size=20, weight="bold"),
            temp_text, temp_bar, humid_text, humid_bar,
            ft.Container(content=chart_dht, padding=10, width=600, height=300)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        bgcolor="black", padding=20, border_radius=15, expand=True
    )


    # ------------------- LDR -------------------
    ldr_text = ft.Text("Luminosidade: 0.00 V", size=16)
    bar_ldr_value = ft.Text("0.00 V", size=14, color="black", weight="bold")

    bar_ldr = ft.Container(content=ft.Stack([
        ft.Container(width=bar_width-50, height=bar_height, bgcolor="grey"),
        ft.Container(width=0, height=bar_height, bgcolor="yellow", alignment=ft.alignment.top_left),
        ft.Container(content=bar_ldr_value, alignment=ft.alignment.center),
    ]), width=bar_width-50, height=bar_height)

    ldr_container = ft.Container(
        content=ft.Column([
            ft.Text("Sensor LDR - Luminosidade", size=20, weight="bold"),
            ft.Row([ft.Text("Claro", size=16), bar_ldr, ft.Text("Escuro", size=16)], alignment="center"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        bgcolor="black", padding=20, border_radius=15, expand=True
    )

    # ------------------- PIR + RELÉ -------------------
    pir_icon = ft.Icon(ft.Icons.CIRCLE, color="red", size=60)
    pir_status = ft.Text("Sem movimento", size=16)
    rele_icon = ft.Icon(ft.Icons.CIRCLE, color="red", size=60)
    fan_status = ft.Text("Ventoinha desligada", size=16)

    def pir_callback(msg):
        if len(msg) < 3:
            return
        value = int(msg[2])
        if value == 1:
            if off_timer["t"]:
                off_timer["t"].cancel()
                off_timer["t"] = None
            control_relay("ON")
            pir_icon.color = "green"
            pir_status.value = "Movimento!"
            rele_icon.color = "green"
            fan_status.value = "Ventoinha ligada"
        else:
            pir_icon.color = "red"
            pir_status.value = "Sem movimento"
            def delayed_off():
                control_relay("OFF")
                rele_icon.color = "red"
                fan_status.value = "Ventoinha desligada"
                page.update()
            off_timer["t"] = threading.Timer(5.0, delayed_off)
            off_timer["t"].start()
        page.update()

    board.set_pin_mode_digital_input(PIN_PIR, callback=pir_callback)

    pir_container = ft.Container(
        content=ft.Column([
            ft.Text("Sensor PIR + Relé", size=20, weight="bold"),
            ft.Row([  
                ft.Column([pir_icon, pir_status], alignment="center", horizontal_alignment="center"),
                ft.Column([rele_icon, fan_status], alignment="center", horizontal_alignment="center")
            ], alignment="center", spacing=80)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20),
        bgcolor="black", padding=20, border_radius=15, expand=True
    )

    # ------------------- HC-SR04 -------------------
    distance_text = ft.Text("Distância: 0.00 cm", size=16)
    bar_a5_value = ft.Text("0.00 cm", size=14, weight="bold")
    bar_a5 = ft.Container(content=ft.Stack([
        ft.Container(width=bar_width, height=bar_height, bgcolor="grey"),
        ft.Container(width=0, height=bar_height, bgcolor="red", alignment=ft.alignment.top_left),
        ft.Container(content=bar_a5_value, alignment=ft.alignment.center)
    ]), width=bar_width, height=bar_height)

    hc_container = ft.Container(
        content=ft.Column([
            ft.Text("Sensor HC-SR04 - Distância", size=20, weight="bold"),
            distance_text,
            bar_a5
        ], spacing=15, horizontal_alignment="center"),
        bgcolor="black", padding=20, border_radius=15, expand=True
    )

    # ------------------- SERVO -------------------
    servo_text = ft.Text("Servo: --°", size=20, weight="bold")
    flag = {"run": False}

    def on_slider_change(e):
        if control_mode.value == "manual":
            ang = int(slider.value)
            move_servo(ang)
            servo_text.value = f"Servo: {ang}°"
            page.update()

    def automatic_control():
        while flag["run"]:
            for ang in range(0, 181, 5):
                if not flag["run"]: return
                move_servo(ang); servo_text.value = f"Servo: {ang}°"; page.update(); time.sleep(0.1)
            for ang in range(180, -1, -5):
                if not flag["run"]: return
                move_servo(ang); servo_text.value = f"Servo: {ang}°"; page.update(); time.sleep(0.1)

    def on_radio_change(e):
        if control_mode.value == "manual":
            flag["run"] = False
            slider.visible = True
        else:
            flag["run"] = True
            slider.visible = False
            threading.Thread(target=automatic_control, daemon=True).start()
        page.update()

    slider = ft.Slider(min=0, max=180, value=90, on_change=on_slider_change)

    control_mode = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="automatic", label="Automático")
        ]),
        value="manual",
        on_change=on_radio_change
    )

    servo_container = ft.Container(
        content=ft.Column([
            ft.Text("Controlo do Servo (pino 10)", size=20, weight="bold"),
            ft.Row([slider, servo_text]),
            control_mode
        ], spacing=15, horizontal_alignment="center"),
        bgcolor="black", padding=20, border_radius=15, expand=True
    )

    # ------------------- LED PWM pino 6 -------------------
    led6_text = ft.Text("PWM: 0", size=20, weight="bold")
    slider1 = ft.Slider(min=0, max=100, value=0)
    stop_flag_led6 = [False]

    def update_led_pwm(value):
        pwm_value = int(value * 2.55)
        board.analog_write(DIGITAL_PIN6, pwm_value)
        led6_text.value = f"{pwm_value} PWM"

    def on_slider1_change(e):
        if manual_control_led6.value == "manual":
            update_led_pwm(slider1.value)
            page.update()

    def automatic_control_led6():
        while stop_flag_led6[0]:
            for i in range(256):
                if not stop_flag_led6[0]: return
                board.analog_write(DIGITAL_PIN6, i)
                led6_text.value = f"{i} PWM"
                page.update()
                time.sleep(0.05)
            for i in range(255, -1, -1):
                if not stop_flag_led6[0]: return
                board.analog_write(DIGITAL_PIN6, i)
                led6_text.value = f"{i} PWM"
                page.update()
                time.sleep(0.05)

    def on_radio_led6_change(e):
        if manual_control_led6.value == "manual":
            stop_flag_led6[0] = False
            slider1.visible = True
        else:
            stop_flag_led6[0] = True
            slider1.visible = False
            threading.Thread(target=automatic_control_led6, daemon=True).start()
        page.update()

    manual_control_led6 = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="automatic", label="Automático")
        ]),
        value="manual",
        on_change=on_radio_led6_change
    )

    slider1.on_change = on_slider1_change

    led6_container = ft.Container(
        content=ft.Column([
            ft.Text("Controlo Velocidade Motor (pino 6)", size=20, weight="bold"),
            ft.Row([slider1, led6_text]),
            manual_control_led6
        ], spacing=10, horizontal_alignment="center"),
        bgcolor="black", padding=20, border_radius=15, expand=True
    )
    
    # Ajusta altura dos containers LDR e HC-SR04
    ldr_container.height = 180
    hc_container.height = 180

    # ------------------- DIÁLOGOS -------------------
    def close_dialog(dialog):
        dialog.open = False
        page.update()

    help_dialog = ft.AlertDialog(
        title=ft.Text("Ajuda"),
        content=ft.Text(
            "Este painel controla os sensores e atuadores da casa inteligente.\n\n"
            "- O slider do servo ajusta o servo manualmente ou em modo automático.\n"
            "- O slider PWM controla a velocidade do motor.\n"
            "- O sensor PIR liga a ventoinha automaticamente.\n"
            "- As barras mostram temperatura, humidade, luminosidade e distância."
        ),
        actions=[ft.TextButton("Fechar", on_click=lambda e: close_dialog(help_dialog))],
        actions_alignment=ft.MainAxisAlignment.END
    )

    about_dialog = ft.AlertDialog(
        title=ft.Text("Sobre"),
        content=ft.Text(
            "Projeto: Casa Inteligente com Arduino e Flet\n"
            "Desenvolvido para demonstração de sensores e atuadores.\n"
            "Autor: A nossa Equipa / Nome\n"
            "Data: 2025"
        ),
        actions=[ft.TextButton("Fechar", on_click=lambda e: close_dialog(about_dialog))],
        actions_alignment=ft.MainAxisAlignment.END
    )

    def show_help(page):
        page.dialog = help_dialog
        help_dialog.open = True
        page.update()

    def show_about(page):
        page.dialog = about_dialog
        about_dialog.open = True
        page.update()

    # ------------------- BOTÕES -------------------
    exit_btn = ft.Button(
        text="Sair", icon=ft.Icons.EXIT_TO_APP, width=200, height=60,
        tooltip="Sair do Programa",
        on_click=lambda _: (
            flag.update({"run": False}),
            move_servo(90),
            board.analog_write(DIGITAL_PIN6, 0),
            board.shutdown(),
            page.window.close()
        )
    )

    help_btn = ft.Button(
        text="Ajuda", icon=ft.Icons.HELP, width=200, height=60,
        tooltip="Ajuda e instruções de utilização",
        on_click=lambda e: show_help(page)
    )

    about_btn = ft.Button(
        text="Sobre", icon=ft.Icons.INFO, width=200, height=60,
        tooltip="Informações sobre o projeto",
        on_click=lambda e: show_about(page)
    )

    # ------------------- LAYOUT FINAL -------------------
    page.add(
        ft.Column([
            txt,
            ft.Row([
                dht22_container,
                ft.Column([
                    ft.Row([ldr_container, hc_container], spacing=20, alignment="center"),
                    pir_container,
                    ft.Row([servo_container, led6_container], spacing=20, alignment="center"),
                ], spacing=20, expand=True)
            ], alignment="center", spacing=20),
            ft.Row([about_btn, help_btn, exit_btn], alignment="center", spacing=20)
        ], spacing=20, horizontal_alignment="center")
    )

    # ------------------- LOOP PRINCIPAL EM BACKGROUND -------------------
    async def update_ui():
        while True:
            temp_text.value = f"Temperatura: {temperature:.1f} ºC"
            humid_text.value = f"Humidade: {humidity:.1f} %"
            temp_value_text.value = f"{temperature:.1f} ºC"
            humid_value_text.value = f"{humidity:.1f} %"
            temp_bar.content.controls[1].width = max(0, min((temperature / 50) * bar_width, bar_width))
            humid_bar.content.controls[1].width = max(0, min((humidity / 100) * bar_width, bar_width))
            temp_data.append(temperature); humid_data.append(humidity)
            temp_data.pop(0); humid_data.pop(0)
            line_temp.set_ydata(temp_data); line_humid.set_ydata(humid_data); chart_dht.update()

            ldr_value = analog_values[ANALOG_PIN0]
            ldr_voltage = ldr_value * (5.0 / 1023)
            ldr_text.value = f"Luminosidade: {ldr_voltage:.2f} V"
            bar_ldr_value.value = f"{ldr_voltage:.2f} V"
            bar_ldr.content.controls[1].width = (ldr_voltage / 5.0) * bar_width

            if last_distance is not None:
                distance_text.value = f"Distância: {last_distance:.2f} cm"
                bar_a5.content.controls[1].width = ((last_distance - min_range) / (max_range - min_range)) * bar_width
                bar_a5_value.value = f"{last_distance:.2f} cm"

            page.update()
            await asyncio.sleep(0.2)

    asyncio.create_task(update_ui())

# -------------------------------
# EXECUÇÃO
# -------------------------------
ft.run(main)
