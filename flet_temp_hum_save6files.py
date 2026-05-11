import flet as ft
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import random
import asyncio
from collections import deque
from datetime import datetime

MAX_PONTOS = 100

# ---------------- FUNÇÃO GERADOR SUAVE ----------------
def criar_gerador_suave(valor_inicial, passo=0.5, minimo=0, maximo=100):
    valor = valor_inicial
    def gerar():
        nonlocal valor
        variacao = random.uniform(-passo, passo)
        valor = max(min(valor + variacao, maximo), minimo)
        return round(valor, 2)
    return gerar

# ---------------- FUNÇÃO PRINCIPAL ----------------
async def main(page: ft.Page):
    page.title = "Temperatura e Humidade - Gráfico e Gravação"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ---------------- DADOS ----------------
    temperaturas = deque([0]*MAX_PONTOS, maxlen=MAX_PONTOS)
    humidades = deque([0]*MAX_PONTOS, maxlen=MAX_PONTOS)

    gerar_temp = criar_gerador_suave(25, passo=0.3, minimo=15, maximo=35)
    gerar_hum = criar_gerador_suave(55, passo=1, minimo=30, maximo=80)

    gravando = False
    contador_gravacao = 0
    dados_gravados = []
    ficheiro_actual = None

    # ---------------- LABELS ----------------
    lbl_temp = ft.Text("Temperatura: -- °C", size=18)
    lbl_hum = ft.Text("Humidade: -- %", size=18)
    lbl_relogio = ft.Text("Data/Hora: --", size=16)
    progresso = ft.ProgressBar(width=300, value=0, visible=False)
    lbl_status = ft.Text("", size=18)

    # ---------------- BOTÕES DE GRAVAÇÃO ----------------
    def iniciar_gravacao(letra):
        def func(e):
            nonlocal gravando, contador_gravacao, dados_gravados, ficheiro_actual
            gravando = True
            contador_gravacao = 0
            dados_gravados = []
            ficheiro_actual = letra
            progresso.visible = True
            progresso.value = 0
            lbl_status.value = f"Gravando 100 medidas - Ficheiro {letra}"
            page.update()
        return func

    botoes_coluna = ft.Column(
        controls=[
            ft.Button(f"Gravar {letra}", on_click=iniciar_gravacao(letra))
            for letra in ["A", "B", "C", "D", "E", "F"]
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=8
    )

    # ---------------- CONFIGURAÇÃO DO GRÁFICO ----------------
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.subplots_adjust(bottom=0.25)
    ax.set_ylim(0, 100)
    ax.set_xlim(0, MAX_PONTOS-1)
    ax.set_title("Temperatura e Humidade")
    ax.set_xlabel("Amostras")
    ax.set_ylabel("Valor")

    linha_temp, = ax.plot(range(MAX_PONTOS), temperaturas, color="red", label="Temperatura")
    linha_hum, = ax.plot(range(MAX_PONTOS), humidades, color="blue", label="Humidade")

    ax.legend()
    ax.grid(True)

    buf = BytesIO()
    def fig_to_base64():
        buf.seek(0)
        buf.truncate(0)
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_b64}"

    chart_image = ft.Image(src=fig_to_base64(), width=500, height=300)

    # ---------------- LAYOUT PRINCIPAL ----------------
    conteudo = ft.Row([
        botoes_coluna,
        chart_image
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=30)

    page.add(
        lbl_temp,
        lbl_hum,
        lbl_relogio,
        conteudo,
        progresso,
        lbl_status
    )

    # ---------------- LOOP DE ATUALIZAÇÃO ----------------
    while True:
        agora = datetime.now()
        lbl_relogio.value = f"Data/Hora: {agora.strftime('%d-%m-%Y %H:%M:%S')}"

        nova_temp = gerar_temp()
        nova_hum = gerar_hum()
        temperaturas.append(nova_temp)
        humidades.append(nova_hum)

        lbl_temp.value = f"Temperatura: {nova_temp:.1f} °C"
        lbl_hum.value = f"Humidade: {nova_hum:.1f} %"

        # Atualiza linhas do gráfico
        linha_temp.set_ydata(temperaturas)
        linha_hum.set_ydata(humidades)
        chart_image.src = fig_to_base64()

        # ---------------- GRAVAÇÃO ----------------
        if gravando:
            contador_gravacao += 1
            dados_gravados.append((agora, nova_temp, nova_hum))
            progresso.value = contador_gravacao / 100

            if contador_gravacao >= 100:
                gravando = False
                nome = f"ficheiro_{ficheiro_actual}.csv"
                with open(nome, "w") as f:
                    f.write("Data,Hora,Temperatura,Humidade\n")
                    for dt, t, h in dados_gravados:
                        f.write(f"{dt.strftime('%d-%m-%Y')},{dt.strftime('%H:%M:%S')},{t},{h}\n")
                lbl_status.value = f"Gravação concluída: {nome}"
                progresso.visible = False
                progresso.value = 0

        page.update()
        await asyncio.sleep(0.2)

# ---------------- INICIALIZAÇÃO ----------------
ft.app(target=main)
