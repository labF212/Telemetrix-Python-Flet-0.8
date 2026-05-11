import flet as ft
from telemetrix import telemetrix

# Inicializa o Arduino
board = telemetrix.Telemetrix()

# Define os pinos para os relés
PIN_4 = 4
PIN_5 = 5
PIN_6 = 6
PIN_13 = 7

# Configura os pinos como saídas digitais
for pin in [PIN_4, PIN_5, PIN_6, PIN_13]:
    board.set_pin_mode_digital_output(pin)

def main(page: ft.Page):
    page.title = "Controlo de Relés"
    page.theme_mode = ft.ThemeMode.DARK

    # Funções para ligar/desligar relés e atualizar LED
    def ligar_rele(pin, led_icon):
        board.digital_write(pin, 1)
        led_icon.color = "green"
        led_icon.update()

    def desligar_rele(pin, led_icon):
        board.digital_write(pin, 0)
        led_icon.color = "red"
        led_icon.update()

    title = ft.Text("Controlo de Relés", size=24, weight=ft.FontWeight.BOLD)

    def create_rele_controls(rele_number, pin):
        # LED
        led_icon = ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, color="red", size=60)
        led_label = ft.Text(f"Relé {rele_number}", size=14, color="black")

        led_container = ft.Container(
            content=ft.Column(
                [led_icon, led_label],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
            bgcolor="yellow",
            border_radius=8,
            width=120,
            height=100,
            alignment=ft.Alignment.CENTER,
        )

        # Botões
        ligar_button = ft.Button(
            f"Ligar Relé {rele_number}",
            icon=ft.Icons.POWER,
            on_click=lambda e: ligar_rele(pin, led_icon),
        )

        desligar_button = ft.Button(
            f"Desligar Relé {rele_number}",
            icon=ft.Icons.POWER_OFF,
            on_click=lambda e: desligar_rele(pin, led_icon),
        )

        buttons_container = ft.Container(
            content=ft.Row(
                [ligar_button, desligar_button],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=10,
            bgcolor="yellow",
            border_radius=8,
            width=350,
            height=100,
            alignment=ft.Alignment.CENTER,
        )

        return ft.Row(
            [buttons_container, led_container],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

    # Adiciona título e linhas de controles
    page.add(
        title,
        ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        "Entradas",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    width=350,
                ),
                ft.Container(
                    content=ft.Text(
                        "Saídas",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    width=120,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        ),
        create_rele_controls(1, PIN_4),
        create_rele_controls(2, PIN_5),
        create_rele_controls(3, PIN_6),
        create_rele_controls(4, PIN_13),
    )

    # Botão de saída assíncrono
    async def exit_app(e):
        board.shutdown()
        await page.window.destroy()

    exit_button = ft.Button(
        "Exit",
        icon=ft.Icons.EXIT_TO_APP,
        on_click=exit_app,
        style=ft.ButtonStyle(padding=20),
    )

    page.add(ft.Row([exit_button], alignment=ft.MainAxisAlignment.CENTER))

    # Cleanup ao fechar a janela
    def on_window_close(e):
        board.shutdown()
    page.on_window_close = on_window_close

# ---------------- RUN ----------------
if __name__ == "__main__":
    ft.run(main)
