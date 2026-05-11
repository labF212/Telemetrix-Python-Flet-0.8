import flet as ft
from telemetrix import telemetrix

# ---------------- HARDWARE ----------------
PIN_LED = 7

board = telemetrix.Telemetrix()
board.set_pin_mode_digital_output(PIN_LED)

# LED desligado no arranque
board.digital_write(PIN_LED, 0)

def led_on():
    board.digital_write(PIN_LED, 1)

def led_off():
    board.digital_write(PIN_LED, 0)

# ---------------- APP ----------------
def main(page: ft.Page):
    page.title = "Controlo do LED 13"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # impede fecho direto
    page.window.prevent_close = True

    status = ft.Text("LED desligado")

    # ---------------- SAIR ----------------
    async def sair_confirmado(e):
        led_off()
        board.shutdown()
        await page.window.destroy()

    def cancelar_saida(e):
        confirm_dialog.open = False
        page.update()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Aviso"),
        content=ft.Text("Deseja mesmo sair do programa?"),
        actions=[
            ft.Button("Sim", on_click=sair_confirmado),
            ft.Button("Não", on_click=cancelar_saida),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(confirm_dialog)

    # evento de fechar janela
    def window_event(e):
        if e.data == "close":
            confirm_dialog.open = True
            page.update()

    page.window.on_event = window_event

    # ---------------- BOTÕES ----------------
    def ligar(e):
        led_on()
        status.value = "LED ligado"
        page.update()

    def desligar(e):
        led_off()
        status.value = "LED desligado"
        page.update()

    def sair(e):
        confirm_dialog.open = True
        page.update()

    # ---------------- LAYOUT ----------------
    page.add(
        ft.Column(
            [
                ft.Text("Controlo do LED 13 (interno)", size=18),
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

    # fallback ao fechar
    def on_window_close(e):
        led_off()
        board.shutdown()

    page.on_window_close = on_window_close


# ---------------- RUN ----------------
if __name__ == "__main__":
    ft.run(main)
