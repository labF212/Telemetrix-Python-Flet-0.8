import flet as ft
from telemetrix import telemetrix

# ---------------- HARDWARE ----------------
PIN_LED = 7

board = telemetrix.Telemetrix()
board.set_pin_mode_digital_output(PIN_LED)

# garante LED desligado no arranque
board.digital_write(PIN_LED, 0)

def led_on():
    board.digital_write(PIN_LED, 1)

def led_off():
    board.digital_write(PIN_LED, 0)

# ---------------- APP ----------------
def main(page: ft.Page):
    page.title = "LED Controller"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    status = ft.Text("LED desligado")

    # ---------------- BOTÕES ----------------
    def ligar(e):
        led_on()
        status.value = "LED ligado"
        page.update()

    def desligar(e):
        led_off()
        status.value = "LED desligado"
        page.update()

    async def sair(e):
        led_off()
        board.shutdown()
        await page.window.destroy()

    # ---------------- LAYOUT ----------------
    page.add(
        ft.Column(
            [
                ft.Text("Controlar LED", size=18),
                status,
                ft.Button("Ligar", on_click=ligar),
                ft.Button("Desligar", on_click=desligar),
                ft.Button("Sair", icon=ft.Icons.EXIT_TO_APP, on_click=sair),
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # ---------------- FECHO DA JANELA ----------------
    def on_window_close(e):
        led_off()
        board.shutdown()

    page.on_window_close = on_window_close


# ---------------- RUN ----------------
if __name__ == "__main__":
    ft.run(main)
