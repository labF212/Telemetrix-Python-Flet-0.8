import flet as ft
from telemetrix import telemetrix
import asyncio
import time

# ----------------------------
# PINOS
# ----------------------------
PIN_RELE = 7
PIN_PIR = 2

# ----------------------------
# LIGAÇÃO AO ARDUINO
# ----------------------------
board = telemetrix.Telemetrix()
board.set_pin_mode_digital_output(PIN_RELE)

def control_relay(state: str):
    board.digital_write(PIN_RELE, 1 if state == "ON" else 0)

# ----------------------------
# APLICAÇÃO FLET
# ----------------------------
def main(page: ft.Page):
    page.title = "PIR + Relé / Ventoinha"
    page.theme_mode = ft.ThemeMode.DARK

    # ----------------------------
    # UI
    # ----------------------------
    pir_icon = ft.Icon(ft.Icons.CIRCLE, color="red", size=60)
    pir_status = ft.Text("Sem movimento", size=16)
    rele_icon = ft.Icon(ft.Icons.CIRCLE, color="red", size=60)
    rele_text = ft.Text("Ventoinha ligada", size=16)

    # ----------------------------
    # Estado global
    # ----------------------------
    state = {
        "pir_detected": False,
        "pir_off_time": None,
        "relay_on": False,
        "relay_off_time": None
    }

    # ----------------------------
    # Callback PIR
    # ----------------------------
    def pir_callback(msg):
        if not isinstance(msg, (list, tuple)) or len(msg) < 3:
            return
        detected = int(msg[2]) == 1
        now = time.time()

        # PIR detectado → atualiza estado e LED
        if detected:
            state["pir_detected"] = True
            state["pir_off_time"] = now + 0  # mantém LED PIR verde 1s após perder
            state["relay_on"] = True
            state["relay_off_time"] = now + 8  # mantém relé ligado 5s após último movimento
            control_relay("ON")
        else:
            state["pir_detected"] = False
            # o LED PIR ficará verde até pir_off_time expirar
            # o relé continuará ligado até relay_off_time expirar

    board.set_pin_mode_digital_input(PIN_PIR, callback=pir_callback)

    # ----------------------------
    # Loop assíncrono de atualização da UI
    # ----------------------------
    async def update_ui():
        while True:
            now = time.time()

            # Atualiza LED do PIR
            if state["pir_detected"] or (state["pir_off_time"] and now < state["pir_off_time"]):
                pir_icon.color = "green"
                pir_status.value = "Movimento!"
            else:
                pir_icon.color = "red"
                pir_status.value = "Sem movimento"

            # Relé / ventoinha
            if state["relay_on"] and state["relay_off_time"] and now >= state["relay_off_time"]:
                state["relay_on"] = False
                control_relay("OFF")
                
            # Atualiza cor e texto
            rele_icon.color = "green" if state["relay_on"] else "red"
            rele_text.value = "Ventoinha ligada" if state["relay_on"] else "Ventoinha desligada"

            page.update()
            await asyncio.sleep(0.1)

    asyncio.create_task(update_ui())

    # ----------------------------
    # Botão sair
    # ----------------------------
    async def on_exit(e):
        board.shutdown()
        await page.window.destroy()

    page.add(
        ft.Column(
            [
                ft.Row([
                    ft.Column([pir_icon, pir_status],
                              alignment=ft.MainAxisAlignment.CENTER,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([rele_icon, rele_text],
                              alignment=ft.MainAxisAlignment.CENTER,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=40),

                # Botão sair centrado
                ft.Row(
                    [ft.Button("Sair", icon=ft.Icons.EXIT_TO_APP, on_click=on_exit)],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            spacing=30,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
      

    # Cleanup ao fechar a janela
    def on_window_close(e):
        board.shutdown()
    page.on_window_close = on_window_close

# ----------------------------
# EXECUÇÃO
# ----------------------------
if __name__ == "__main__":
    ft.run(main)
