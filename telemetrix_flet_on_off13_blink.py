import flet as ft
from telemetrix import telemetrix
import threading
import time

# ---------------- HARDWARE ----------------
PIN_LED = 13

board = telemetrix.Telemetrix()
board.set_pin_mode_digital_output(PIN_LED)

board.digital_write(PIN_LED, 0)

# ---------------- CONTROLO ----------------
piscar = False

def led_on():
    board.digital_write(PIN_LED, 1)

def led_off():
    board.digital_write(PIN_LED, 0)

def blink_loop():
    global piscar

    while piscar:
        led_on()
        time.sleep(0.5)

        led_off()
        time.sleep(0.5)

# ---------------- APP ----------------
def main(page: ft.Page):
    global piscar

    page.title = "LED Controller"

    status = ft.Text("LED desligado")

    # ---------------- BOTÕES ----------------
    def ligar(e):
        global piscar

        piscar = False
        led_on()

        status.value = "LED ligado"
        page.update()

    def desligar(e):
        global piscar

        piscar = False
        led_off()

        status.value = "LED desligado"
        page.update()

    def piscar_led(e):
        global piscar

        if not piscar:
            piscar = True

            threading.Thread(target=blink_loop, daemon=True).start()

            status.value = "LED a piscar"
            page.update()

    async def sair(e):
        global piscar

        piscar = False
        led_off()

        board.shutdown()

        await page.window.destroy()

    # ---------------- LAYOUT ----------------
    page.add(
        ft.Column(
            [
                ft.Text("Controlar LED", size=20),
                status,

                ft.Button("Ligar", on_click=ligar),
                ft.Button("Desligar", on_click=desligar),
                ft.Button("Piscar", on_click=piscar_led),

                ft.Button(
                    "Sair",
                    icon=ft.Icons.EXIT_TO_APP,
                    on_click=sair,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # ---------------- FECHAR JANELA ----------------
    def on_window_close(e):
        global piscar

        piscar = False
        led_off()

        board.shutdown()

    page.on_window_close = on_window_close


# ---------------- RUN ----------------
if __name__ == "__main__":
    ft.run(main)