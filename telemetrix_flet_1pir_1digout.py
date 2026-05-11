import flet as ft
from telemetrix import telemetrix
import threading

# ---------------- HARDWARE ----------------
PIN_RELE = 7
PIN_PIR = 2
RELAY_ACTIVE_LOW = False  # ajusta conforme hardware

board = telemetrix.Telemetrix()
board.set_pin_mode_digital_output(PIN_RELE)

def relay_on():
    board.digital_write(PIN_RELE, 0 if RELAY_ACTIVE_LOW else 1)

def relay_off():
    board.digital_write(PIN_RELE, 1 if RELAY_ACTIVE_LOW else 0)

# garante relé desligado no arranque
relay_off()

# ---------------- APP ----------------
def main(page: ft.Page):
    page.title = "PIR + Relé (Manual / Auto)"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ---------------- UI ----------------
    pir_icon = ft.Icon(ft.Icons.CIRCLE, color="red", size=60)
    pir_text = ft.Text("Sem movimento")

    rele_icon = ft.Icon(ft.Icons.CIRCLE, color="red", size=60)
    rele_text = ft.Text("Relé desligado")

    mode_text = ft.Text("Modo: MANUAL", size=16)

    # ---------------- ESTADO ----------------
    state = {
        "auto": False,
        "pir": 0,
        "relay": False,
        "off_timer": None,
    }

    # ---------------- UI HELPERS ----------------
    def update_relay(on: bool):
        state["relay"] = on
        rele_icon.color = "green" if on else "red"
        rele_text.value = "Relé ligado" if on else "Relé desligado"
        page.update()

    def update_pir(active: bool):
        pir_icon.color = "green" if active else "red"
        pir_text.value = "Em movimento!" if active else "Sem movimento"
        page.update()

    # ---------------- MANUAL ----------------
    def ligar_manual(e):
        if not state["auto"]:
            relay_on()
            update_relay(True)

    def desligar_manual(e):
        if not state["auto"]:
            relay_off()
            update_relay(False)

    # ---------------- MODO ----------------
    def toggle_mode(e):
        state["auto"] = not state["auto"]

        # cancela qualquer timer
        if state["off_timer"]:
            state["off_timer"].cancel()
            state["off_timer"] = None

        if state["auto"]:
            mode_text.value = "Modo: AUTOMÁTICO"
            relay_off()
            update_relay(False)
            update_pir(False)
        else:
            mode_text.value = "Modo: MANUAL"
            relay_off()
            update_relay(False)

        page.update()

    # ---------------- PIR CALLBACK ----------------
    def pir_callback(msg):
        if not state["auto"]:
            return

        if not isinstance(msg, (list, tuple)) or len(msg) < 3:
            return

        value = int(msg[2])

        if value == state["pir"]:
            return  # ignora estado repetido

        state["pir"] = value

        if value == 1:
            # movimento detectado
            if state["off_timer"]:
                state["off_timer"].cancel()
                state["off_timer"] = None

            relay_on()
            page.call_from_thread(lambda: update_relay(True))
            page.call_from_thread(lambda: update_pir(True))

        else:
            # movimento terminou
            # LED do PIR verde 1s, depois vermelho
            def pir_off_delay():
                page.call_from_thread(lambda: update_pir(False))

            threading.Timer(1.0, pir_off_delay).start()

            # relé desliga após 5s
            def relay_off_delay():
                relay_off()
                page.call_from_thread(lambda: update_relay(False))

            state["off_timer"] = threading.Timer(5.0, relay_off_delay)
            state["off_timer"].start()

    board.set_pin_mode_digital_input(PIN_PIR, callback=pir_callback)

    # ---------------- SAIR ----------------
    async def on_exit(e):
        if state["off_timer"]:
            state["off_timer"].cancel()
        relay_off()
        board.shutdown()
        await page.window.destroy()

    # ---------------- LAYOUT ----------------
    page.add(
        ft.Column(
            [
                mode_text,
                ft.Row(
                    [
                        ft.Column([pir_icon, pir_text], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Column([rele_icon, rele_text], alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=40,
                ),
                ft.Row(
                    [
                        ft.Button("Ligar (manual)", on_click=ligar_manual),
                        ft.Button("Desligar (manual)", on_click=desligar_manual),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                ft.Row([ft.Button("Manual / Automático", on_click=toggle_mode)],
                       alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.Button("Sair", icon=ft.Icons.EXIT_TO_APP, on_click=on_exit)],
                       alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=25,
        )
    )

    # ---------------- FECHO DA JANELA ----------------
    def on_window_close(e):
        if state["off_timer"]:
            state["off_timer"].cancel()
        relay_off()
        board.shutdown()

    page.on_window_close = on_window_close


if __name__ == "__main__":
    ft.run(main)
