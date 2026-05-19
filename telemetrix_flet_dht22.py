import asyncio
import flet as ft
from telemetrix import telemetrix
import flet_charts as fch

# =========================================================
# CONFIGURAÇÃO DO DHT22
# =========================================================

DHT_PIN = 7

board = telemetrix.Telemetrix()

temperature = 0.0
humidity = 0.0


def dht_callback(data):
    """
    data = [
        report_type,
        error,
        pin,
        dht_type,
        humidity,
        temperature,
        timestamp
    ]
    """

    global temperature, humidity

    error = data[1]

    if error == 0:
        humidity = float(data[4])
        temperature = float(data[5])

    else:
        print(f"Erro leitura DHT22 no pino {data[2]}")


# Inicializa sensor
board.set_pin_mode_dht(
    DHT_PIN,
    dht_type=11,
    callback=dht_callback
)

# =========================================================
# APP FLET
# =========================================================

async def main(page: ft.Page):

    page.title = "Monitor DHT22"
    page.theme_mode = ft.ThemeMode.SYSTEM

    page.window_width = 900
    page.window_height = 700

    # =====================================================
    # VARIÁVEIS
    # =====================================================

    BAR_WIDTH = 300
    BAR_HEIGHT = 35

    MAX_POINTS = 30

    temp_points = []
    humid_points = []

    x_index = 0

    # =====================================================
    # TEXTOS
    # =====================================================

    title = ft.Text(
        "Monitor de Temperatura e Humidade",
        size=28,
        weight=ft.FontWeight.BOLD
    )

    temp_text = ft.Text(
        "Temperatura: 0.0 ºC",
        size=18
    )

    humid_text = ft.Text(
        "Humidade: 0.0 %",
        size=18
    )

    # =====================================================
    # BARRA TEMPERATURA
    # =====================================================

    temp_fill = ft.Container(
        width=0,
        height=BAR_HEIGHT,
        bgcolor=ft.Colors.RED,
        border_radius=10
    )

    temp_value = ft.Text(
        "0.0 ºC",
        color=ft.Colors.WHITE,
        weight=ft.FontWeight.BOLD
    )

    temp_bar = ft.Stack([
        ft.Container(
            width=BAR_WIDTH,
            height=BAR_HEIGHT,
            bgcolor=ft.Colors.GREY_800,
            border_radius=10
        ),

        temp_fill,

        ft.Container(
            width=BAR_WIDTH,
            height=BAR_HEIGHT,
            alignment=ft.Alignment(0, 0),
            content=temp_value
        )
    ])

    # =====================================================
    # BARRA HUMIDADE
    # =====================================================

    humid_fill = ft.Container(
        width=0,
        height=BAR_HEIGHT,
        bgcolor=ft.Colors.BLUE,
        border_radius=10
    )

    humid_value = ft.Text(
        "0.0 %",
        color=ft.Colors.WHITE,
        weight=ft.FontWeight.BOLD
    )

    humid_bar = ft.Stack([
        ft.Container(
            width=BAR_WIDTH,
            height=BAR_HEIGHT,
            bgcolor=ft.Colors.GREY_800,
            border_radius=10
        ),

        humid_fill,

        ft.Container(
            width=BAR_WIDTH,
            height=BAR_HEIGHT,
            alignment=ft.Alignment(0, 0),
            content=humid_value
        )
    ])

    # =====================================================
    # GRÁFICO NATIVO FLET
    # =====================================================

    temp_series = fch.LineChartData(
        points=[],
        stroke_width=3,
        color=ft.Colors.RED,
        curved=True,
    )

    humid_series = fch.LineChartData(
        points=[],
        stroke_width=3,
        color=ft.Colors.BLUE,
        curved=True,
    )

    chart = fch.LineChart(
        data_series=[
            temp_series,
            humid_series
        ],

        border=ft.Border(
            left=ft.BorderSide(1, ft.Colors.GREY_700),
            top=ft.BorderSide(1, ft.Colors.GREY_700),
            right=ft.BorderSide(1, ft.Colors.GREY_700),
            bottom=ft.BorderSide(1, ft.Colors.GREY_700),
        ),

        horizontal_grid_lines=fch.ChartGridLines(
            interval=10,
            color=ft.Colors.GREY_800,
            width=1
        ),

        vertical_grid_lines=fch.ChartGridLines(
            interval=5,
            color=ft.Colors.GREY_800,
            width=1
        ),

        left_axis=fch.ChartAxis(
            label_size=40,
            title=ft.Text("Valores")
        ),

        bottom_axis=fch.ChartAxis(
            label_size=40,
            title=ft.Text("Tempo")
        ),

        min_y=0,
        max_y=100,

        expand=True
    )

    # =====================================================
    # BOTÃO SAIR
    # =====================================================

    async def close_app(e):
        board.shutdown()
        await page.window.destroy()
        
    exit_btn = ft.Button(
        "Sair",
        icon=ft.Icons.EXIT_TO_APP,
        on_click=close_app
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    page.add(
        ft.Column(
            [
                title,

                ft.Divider(),

                temp_text,
                temp_bar,

                ft.Container(height=10),

                humid_text,
                humid_bar,

                ft.Divider(),

                ft.Container(
                    content=chart,
                    expand=True,
                    height=400
                ),

                exit_btn
            ],

            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
    )

    # =====================================================
    # LOOP PRINCIPAL
    # =====================================================

    while True:

        # -------------------------------------------------
        # Atualiza textos
        # -------------------------------------------------

        temp_text.value = f"Temperatura: {temperature:.1f} ºC"
        humid_text.value = f"Humidade: {humidity:.1f} %"

        temp_value.value = f"{temperature:.1f} ºC"
        humid_value.value = f"{humidity:.1f} %"

        # -------------------------------------------------
        # Atualiza barras
        # -------------------------------------------------

        temp_fill.width = max(
            0,
            min((temperature / 80) * BAR_WIDTH, BAR_WIDTH)
        )

        humid_fill.width = max(
            0,
            min((humidity / 100) * BAR_WIDTH, BAR_WIDTH)
        )

        # -------------------------------------------------
        # Atualiza dados gráfico
        # -------------------------------------------------

        temp_points.append(
            fch.LineChartDataPoint(x_index, temperature)
        )

        humid_points.append(
            fch.LineChartDataPoint(x_index, humidity)
        )

        # Limita quantidade de pontos
        if len(temp_points) > MAX_POINTS:
            temp_points.pop(0)

        if len(humid_points) > MAX_POINTS:
            humid_points.pop(0)

        temp_series.points = temp_points
        humid_series.points = humid_points

        # Atualiza eixo X
        chart.min_x = max(0, x_index - MAX_POINTS)
        chart.max_x = x_index + 1

        x_index += 1

        # -------------------------------------------------
        # Atualiza tela
        # -------------------------------------------------

        chart.update()
        page.update()

        await asyncio.sleep(1)



# ---------------- RUN ----------------
if __name__ == "__main__":
    ft.run(main)