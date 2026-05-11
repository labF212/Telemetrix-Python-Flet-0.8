import asyncio
import csv
import os
import time
import subprocess
from telemetrix import telemetrix
import flet as ft
import flet_charts as fch 

# Configuração dos pinos do HC-SR04
TRIGGER_PIN = 8
ECHO_PIN = 9

# Variáveis globais
last_distance = 0
measurements = []
min_range = 0
max_range = 200
sample_interval = 1
distance_between_measurements = 5

# Variáveis do gráfico
serie_distancia = fch.LineChartData(points=[], color="blue", stroke_width=2, curved=True)

# Função para abrir outro programa Python
async def abrir_ler_dados(page, board):
    try:
        # 1. Descobre onde este script principal está guardado
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Constrói o caminho completo para o outro ficheiro
        caminho_script = os.path.join(diretorio_atual, "telemetrix_flet_scr04_read_6files.py")

        # 3. Verifica se o ficheiro existe mesmo antes de tentar abrir
        if os.path.exists(caminho_script):
            # Inicia o processo usando o caminho absoluto
            subprocess.Popen(["python3", caminho_script])
            
            snack = ft.SnackBar(content=ft.Text("Programa de leitura iniciado!"))
            page.overlay.append(snack)
            snack.open = True
            page.update()

            # Pequena pausa para o utilizador ver a mensagem
            await asyncio.sleep(1.5)
            
            # Fecha a comunicação com o Arduino e a janela atual
            board.shutdown() 
            await page.window.close()
        else:
            # Caso o ficheiro não esteja lá, avisa no terminal e na App
            print(f"Erro: Ficheiro não encontrado em {caminho_script}")
            snack = ft.SnackBar(content=ft.Text("Erro: Ficheiro .py não encontrado!"))
            page.overlay.append(snack)
            snack.open = True
            page.update()

    except Exception as e:
        print(f"Erro ao abrir: {e}")

def sonar_callback(data):
    global last_distance
    last_distance = data[2]

def perform_readings(board, trigger_pin, echo_pin):
    board.set_pin_mode_sonar(trigger_pin, echo_pin, sonar_callback)

async def main(page: ft.Page):
    global min_range, max_range, last_distance
    
    page.title = "Leitura HC-SR04 com Telemetrix e Flet"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ALWAYS
    page.padding = 20
    
    cor_tema = "blue400"

    # --- UI COMPONENTS ---
    distance_text = ft.Text(value="Distância", size=20, color=cor_tema, weight="bold")
    
    # Texto que fica dentro da barra (Removido o 'id' problemático)
    bar_text_value = ft.Text("0.00 cm", color="white", weight="bold")
    
    bar_width = 300
    bar_fill = ft.Container(
        width=0, 
        height=30, 
        bgcolor="blue", 
        border_radius=5, 
        # Use ft.Animation e o nome da curva como string ou ft.AnimationCurve
        animate=ft.Animation(300, ft.AnimationCurve.DECELERATE)
    )
    
    bar_container = ft.Container(
            content=ft.Stack([
                # Fundo da barra
                ft.Container(width=bar_width, height=30, bgcolor="grey800", border_radius=5),
                
                # Preenchimento da barra (o bar_fill que definimos antes)
                bar_fill,
                
                # Texto centralizado (corrigido para 'center' minúsculo)
                ft.Container(
                    content=bar_text_value, 
                    alignment=ft.Alignment(0, 0)  # <-- Aqui estava o erro
                )
            ]),
            width=bar_width
        )

    chart = fch.LineChart(
        data_series=[serie_distancia],
        border=ft.Border(ft.BorderSide(1, "grey800"), ft.BorderSide(1, "grey800"), ft.BorderSide(1, "grey800"), ft.BorderSide(1, "grey800")),
        left_axis=fch.ChartAxis(title=ft.Text("Distância (cm)", color=cor_tema, weight="bold"), label_size=40),
        bottom_axis=fch.ChartAxis(title=ft.Text("Amostras", color=cor_tema, weight="bold"), label_size=40),
        expand=True,
        min_y=0,
        max_y=200
    )

    table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Hora")), ft.DataColumn(ft.Text("Distância (cm)"))],
        rows=[]
    )

    # --- LÓGICA DE GRAVAÇÃO ---
    def save_measurements(file_name):
        global last_distance

        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_completo = os.path.join(diretorio_atual, file_name)

        range_span = max_range - min_range
        num_samples = max(1, range_span // distance_between_measurements)
        current_date = time.strftime('%d-%m-%Y')
        
        try:
        # Usamos 'w' para criar/sobrescrever o ficheiro
            with open(caminho_completo, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([f'Medidas feitas em: {current_date}'])
                writer.writerow(['Ensaio Nº', 'Hora', 'Distância Esperada (cm)', 'Distância Lida (cm)'])

                for i in range(num_samples + 1):
                    dist_esperada = min_range + (i * distance_between_measurements)
                    if dist_esperada > max_range: dist_esperada = max_range
                    
                    # Aguarda o sensor atualizar
                    time.sleep(0.5) 
                    
                    val_lido = f"{last_distance:.2f}" if last_distance is not None else "0.00"
                    writer.writerow([i + 1, time.strftime('%H:%M:%S'), dist_esperada, val_lido])
                    
            # Feedback visual na App
            page.overlay.append(ft.SnackBar(ft.Text(f"Ficheiro criado em: {caminho_completo}"), open=True))
            page.update()
            print(f"Ficheiro gravado com sucesso em: {caminho_completo}")

        except Exception as e:
            print(f"ERRO CRÍTICO AO GRAVAR: {e}")

    async def fechar_programa(e):
        # Primeiro fechamos a ligação com a board
        if 'board' in locals():
            board.shutdown()
        # Depois aguardamos o fecho da janela
        await page.window.close()


    def criar_btn_save(texto, file):
        return ft.FilledButton(
            content=ft.Text(texto),
            icon=ft.Icons.SAVE,
            on_click=lambda _: save_measurements(file),
            width=200
        )

    # --- LAYOUT ---
    page.add(
        ft.Row([ft.Text("Analisador Sonar HC-SR04", size=32, weight="bold", color=cor_tema)], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=10, color="transparent"),
        ft.Row([distance_text, bar_container], alignment=ft.MainAxisAlignment.CENTER, spacing=50),
        
        ft.Column([
            ft.Text("Gama de Medida", size=16, weight="bold"),
            ft.RangeSlider(
                min=0, max=400, start_value=0, end_value=200, divisions=40, label="{value}cm",
                on_change=lambda e: (setattr(main, 'min_range', int(e.control.start_value)), 
                                    setattr(main, 'max_range', int(e.control.end_value)))
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),

        ft.Row([
            ft.Container(content=ft.Column([table], scroll=ft.ScrollMode.ALWAYS), width=350, height=400, bgcolor="#1A1A1A", border_radius=10, padding=10),
            ft.Container(content=chart, expand=True, height=400, padding=20)
        ]),

        ft.Column([
            ft.Row([criar_btn_save("Gravar Subida 1", "LeituraSubidaSonar1.csv"), criar_btn_save("Gravar Subida 2", "LeituraSubidaSonar2.csv"), criar_btn_save("Gravar Subida 3", "LeituraSubidaSonar3.csv")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([criar_btn_save("Gravar Descida 1", "LeituraDescidaSonar1.csv"), criar_btn_save("Gravar Descida 2", "LeituraDescidaSonar2.csv"), criar_btn_save("Gravar Descida 3", "LeituraDescidaSonar3.csv")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.FilledButton(
                    content=ft.Text("Ler Dados"), 
                    icon=ft.Icons.UPLOAD_FILE, 
                    on_click=lambda e: page.run_task(abrir_ler_dados, page, board), # Esta é a forma recomendada pelo Flet
                    width=200
                ),
                                
                ft.FilledButton(
                    content=ft.Text("Sair"), 
                    icon=ft.Icons.EXIT_TO_APP, 
                    on_click=fechar_programa, # Chama a função assíncrona
                    width=200
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=10)
    )

    # --- CICLO DE ATUALIZAÇÃO ---
    board = telemetrix.Telemetrix()
    perform_readings(board, TRIGGER_PIN, ECHO_PIN)
    
    count = 0
    try:
        while True:
            dist_atual = last_distance if last_distance is not None else 0.0
            
            # 1. Atualizar Barra de Progresso
            pct = (dist_atual / 400) * bar_width
            bar_fill.width = min(max(0, pct), bar_width)
            bar_text_value.value = f"{dist_atual:.2f} cm"
            
            # 2. Atualizar Texto Principal
            #distance_text.value = f"Distância: {dist_atual:.2f} cm"
            
            # 3. Só adicionar à tabela e ao gráfico se houver leitura real
            if last_distance is not None:
                if len(table.rows) > 5: table.rows.pop(0)
                table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(time.strftime('%H:%M:%S'))), 
                    ft.DataCell(ft.Text(f"{dist_atual:.2f}"))
                ]))
                
                if len(serie_distancia.points) > 50: serie_distancia.points.pop(0)
                serie_distancia.points.append(fch.LineChartDataPoint(count, dist_atual))
                chart.max_y = max_range
                count += 1
            
            # Atualiza a página em cada ciclo do loop
            page.update()
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Erro no loop: {e}")
        board.shutdown()

if __name__ == "__main__":
    ft.run(main)