import asyncio
import io
import base64
import matplotlib.pyplot as plt
import matplotlib
# Força o backend para não abrir janelas
matplotlib.use("agg")

import flet as ft
from telemetrix import telemetrix

# ===================== HARDWARE =====================
TRIGGER_PIN = 8
ECHO_PIN = 9
last_distance = 0

def sonar_callback(msg):
    global last_distance
    last_distance = msg[2]

try:
    board = telemetrix.Telemetrix()
    board.set_pin_mode_sonar(TRIGGER_PIN, ECHO_PIN, sonar_callback)
except Exception as e:
    print(f"Erro Hardware: {e}")
    board = None

# ===================== APP =====================
async def main(page: ft.Page):
    page.title = "HC-SR04 + Matplotlib (Telemetria Completa)"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    
    max_points = 50
    data = [0.0] * max_points
    x_axis = list(range(max_points))

    # --- CONFIGURAÇÃO DO MATPLOTLIB ---
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='#111111')
    ax.set_facecolor('#111111')
    
    line, = ax.plot(x_axis, data, color="cyan", linewidth=2)
    
    # Títulos e Rótulos dos Eixos
    ax.set_title("Telemetria Ultrassônica", color="white", fontsize=14, fontweight='bold')
    ax.set_xlabel("Tempo (Amostras)", color="white")
    ax.set_ylabel("Distância (cm)", color="white")
    
    ax.set_ylim(0, 400)
    ax.tick_params(axis='both', colors='white')
    
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    # Ajuste de layout para que os nomes dos eixos apareçam corretamente
    fig.tight_layout()

    chart_img = ft.Image(src="", width=650, height=400)
    dist_text = ft.Text("0.0 cm", size=40, color="cyan", weight="bold")

    def update_chart():
        line.set_ydata(data)
        buf = io.BytesIO()
        # Removido bbox_inches para manter a performance estável
        fig.savefig(
            buf, 
            format="png", 
            facecolor=fig.get_facecolor(),
            transparent=False
        )
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        chart_img.src = f"data:image/png;base64,{img_b64}"
        buf.close()

    async def close_app(e):
        if board:
            board.shutdown()
        await page.window.destroy()

    btn_sair = ft.Button("Sair", on_click=close_app)

    # Borda manual para versão 0.85
    border_style = ft.Border(
        ft.BorderSide(1, "#333333"),
        ft.BorderSide(1, "#333333"),
        ft.BorderSide(1, "#333333"),
        ft.BorderSide(1, "#333333")
    )

    page.add(
        ft.Column([
            ft.Text("Monitoramento HC-SR04", size=16, color="white"),
            dist_text,
            ft.Container(
                content=chart_img, 
                padding=5, 
                bgcolor="#111111", 
                border_radius=10,
                border=border_style
            ),
            btn_sair
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    while True:
        try:
            data.append(last_distance)
            data.pop(0)
            dist_text.value = f"{last_distance:.1f} cm"
            update_chart()
            page.update()
            await asyncio.sleep(1)
        except:
            break

ft.run(main)