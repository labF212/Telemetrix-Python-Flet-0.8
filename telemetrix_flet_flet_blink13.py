import flet as ft
import asyncio
from telemetrix import telemetrix

# --- Configuração Hardware ---
SERVO_PIN = 10
PIN_LED = 13

board = telemetrix.Telemetrix()
board.set_pin_mode_servo(SERVO_PIN)
board.set_pin_mode_digital_output(PIN_LED)
board.digital_write(PIN_LED, 0)

# --- Estado da Aplicação ---
state = {
    "run_auto": False,
    "blink_led": False
}

# --- Funções de Hardware ---
def move_servo(angle):
    board.servo_write(SERVO_PIN, angle)

def set_led(status: bool):
    board.digital_write(PIN_LED, 1 if status else 0)

# Task assíncrona para piscar o LED
async def blink_worker():
    while state["blink_led"]:
        set_led(True)
        await asyncio.sleep(0.5)
        if not state["blink_led"]:
            break
        set_led(False)
        await asyncio.sleep(0.5)
    set_led(False)

# Controlo automático assíncrono (varrimento do servo 0-180)
async def automatic_control(page, servo_text, led_status):
    state["blink_led"] = True
    page.run_task(blink_worker)
    
    led_status.value = "LED a piscar (Automático)"
    page.update()

    while state["run_auto"]:
        # Subida (0 a 180)
        for ang in range(0, 181, 5):
            if not state["run_auto"]:
                return
            move_servo(ang)
            servo_text.value = f"Servo: {ang}°"
            page.update()
            await asyncio.sleep(0.1)

        # Descida (180 a 0)
        for ang in range(180, -1, -5):
            if not state["run_auto"]:
                return
            move_servo(ang)
            servo_text.value = f"Servo: {ang}°"
            page.update()
            await asyncio.sleep(0.1)


def main(page: ft.Page):
    page.title = "Controlo Assíncrono: Servo + LED"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- Elementos de UI ---
    servo_text = ft.Text("Ângulo do Servo: 90°", size=16)
    led_status = ft.Text("LED desligado (Manual)", size=14, color=ft.Colors.GREY_400)

    # Handlers para o Slider
    def on_slider_change(e):
        if control_mode.value == "manual":
            ang = int(slider.value)
            move_servo(ang)
            servo_text.value = f"Servo: {ang}°"
            
            # Ativa o pisca-pisca enquanto o slider está a ser mexido
            if not state["blink_led"]:
                state["blink_led"] = True
                page.run_task(blink_worker)
                
            led_status.value = "LED a piscar (Manual - A mexer slider)"
            page.update()

    def on_slider_change_end(e):
        if control_mode.value == "manual":
            # Para o pisca-pisca e desliga o LED quando o dedo é retirado do slider
            state["blink_led"] = False
            set_led(False)
            led_status.value = "LED desligado (Manual - Slider parado)"
            page.update()

    slider = ft.Slider(
        min=0, 
        max=180, 
        value=90, 
        label="{value}°",
        on_change=on_slider_change,
        on_change_end=on_slider_change_end
    )

    # --- Handlers de Eventos ---
    async def shutdown_app(e=None):
        state["run_auto"] = False
        state["blink_led"] = False
        move_servo(90)
        set_led(False)
        board.shutdown()
        if e:
            await page.window.destroy()

    def on_radio_change(e):
        is_manual = (control_mode.value == "manual")
        
        if is_manual:
            state["run_auto"] = False
            state["blink_led"] = False
            slider.visible = True
            set_led(False)
            led_status.value = "LED desligado (Manual)"
            servo_text.value = f"Ângulo do Servo: {int(slider.value)}°"
        else:
            slider.visible = False
            state["run_auto"] = True
            page.run_task(automatic_control, page, servo_text, led_status)
        page.update()

    control_mode = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="automatic", label="Automático"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="manual",
        on_change=on_radio_change
    )

    # Substituído ElevatedButton por Button
    exit_button = ft.Button(
        "Sair", 
        icon=ft.Icons.EXIT_TO_APP, 
        color=ft.Colors.RED_400,
        on_click=shutdown_app
    )

    # --- Layout ---
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Controlo Arduino", size=22, weight=ft.FontWeight.BOLD),
                servo_text,
                led_status,
                slider,
                control_mode,
                ft.Divider(height=20),
                exit_button
            ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15),
            padding=20,
            width=400
        )
    )

    page.on_window_close = shutdown_app


if __name__ == "__main__":
    ft.run(main)