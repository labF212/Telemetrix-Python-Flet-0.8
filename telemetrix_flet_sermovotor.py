import flet as ft
import threading
import time
from telemetrix import telemetrix

# --- Configuração hardware ---
SERVO_PIN = 10   # pino digital PWM para o servo

# Cria a ligação ao Arduino
board = telemetrix.Telemetrix()

# Configura o pino como servo
board.set_pin_mode_servo(SERVO_PIN)


# Função para mover o servo
def move_servo(angle):
    board.servo_write(SERVO_PIN, angle)


# Controlo automático (servo "varrendo" de 0 a 180)
def automatic_control(page, servo_text, flag):
    while flag["run"]:
        # sobe
        for ang in range(0, 181, 5):
            if not flag["run"]:
                return
            move_servo(ang)
            servo_text.value = f"Servo: {ang}°"
            page.update()
            time.sleep(0.1)

        # desce
        for ang in range(180, -1, -5):
            if not flag["run"]:
                return
            move_servo(ang)
            servo_text.value = f"Servo: {ang}°"
            page.update()
            time.sleep(0.1)


def main(page: ft.Page):
    page.title = "Controlo de um servomotor em Arduino"
    page.theme_mode = ft.ThemeMode.DARK

    flag = {"run": False}

    # Event handler para sair
    async def on_exit(e):
        flag["run"] = False
        move_servo(90)  # posição neutra
        board.shutdown()
        await page.window.destroy()

    # slider em modo manual
    def on_slider_change(e):
        if control_mode.value == "manual":
            ang = int(slider.value)
            move_servo(ang)
            servo_text.value = f"Servo: {ang}°"
            page.update()

    # troca manual/automático
    def on_radio_change(e):
        if control_mode.value == "manual":
            flag["run"] = False
            slider.visible = True
        else:
            flag["run"] = True
            slider.visible = False
            threading.Thread(
                target=automatic_control,
                args=(page, servo_text, flag),
                daemon=True
            ).start()
        page.update()

    # UI
    servo_text = ft.Text("Ângulo do Servo: --°")
    slider = ft.Slider(min=0, max=180, value=90, on_change=on_slider_change)

    control_mode = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="automatic", label="Automático"),
        ]),
        value="manual",
        on_change=on_radio_change
    )

    exit_button = ft.Button("Exit", on_click=on_exit)

    layout = ft.Column([
        ft.Text("Controlo do Servo (pino 10)"),
        ft.Row([slider, servo_text]),
        control_mode,
        exit_button
    ], alignment=ft.MainAxisAlignment.CENTER)

    page.add(layout)
    page.on_window_close = on_exit


# ---------------- RUN ----------------
if __name__ == "__main__":
    ft.run(main)
