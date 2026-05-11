import asyncio
import csv
import os
import flet as ft
import flet_charts as fch 

# ===================== FUNÇÃO DE LEITURA CSV =====================
def ler_ficheiro_sonar(nome_arquivo):
    ensaios, esp, lido = [], [], []
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(diretorio_script, nome_arquivo)
    
    try:
        with open(caminho_completo, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader) 
            next(reader) 
            for row in reader:
                if len(row) >= 4:
                    ensaios.append(int(row[0]))
                    esp.append(float(row[2]))
                    lido.append(float(row[3]))
        return ensaios, esp, lido
    except Exception as e:
        print(f"Erro ao abrir {nome_arquivo}: {e}")
        return None, None, None

# ===================== APP FLET =====================
async def main(page: ft.Page):
    page.title = "Analisador Sonar - HC-SR04"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    # Corrigido para String para evitar erro de atributo no módulo flet
    cor_tema = "blue400" 

    # --- GRÁFICO (flet_charts) ---
    serie_esperada = fch.LineChartData(points=[], color="blue", stroke_width=2, curved=True)
    serie_lida = fch.LineChartData(points=[], color="red", stroke_width=2, curved=True)
    
    chart = fch.LineChart(
        data_series=[serie_esperada, serie_lida],
        border=ft.Border(
            ft.BorderSide(1, "grey800"), ft.BorderSide(1, "grey800"),
            ft.BorderSide(1, "grey800"), ft.BorderSide(1, "grey800")
        ),
        left_axis=fch.ChartAxis(
            title=ft.Text("Distância (cm)", weight="bold", color=cor_tema),
            label_size=40
        ),
        bottom_axis=fch.ChartAxis(
            title=ft.Text("Número do Ensaio", weight="bold", color=cor_tema),
            label_size=40
        ),
        expand=True
    )

    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nº")),
            ft.DataColumn(ft.Text("Esperado (cm)")),
            ft.DataColumn(ft.Text("Lido (cm)")),
        ],
        rows=[]
    )

    # --- LÓGICA DE CARREGAMENTO ---
    def carregar_dados(e):
        nome_f = e.control.data 
        ens, esp, lido = ler_ficheiro_sonar(nome_f)
        if ens:
            tabela.rows.clear()
            pts_esp, pts_lido = [], []
            for i in range(len(ens)):
                tabela.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(ens[i]))),
                    ft.DataCell(ft.Text(f"{esp[i]:.2f}")),
                    ft.DataCell(ft.Text(f"{lido[i]:.2f}"))
                ]))
                pts_esp.append(fch.LineChartDataPoint(ens[i], esp[i]))
                pts_lido.append(fch.LineChartDataPoint(ens[i], lido[i]))
            
            serie_esperada.points = pts_esp
            serie_lida.points = pts_lido
            chart.max_y = max(max(esp), max(lido)) + 5
            chart.max_x = max(ens)
            page.update()

    # --- FUNÇÃO SAIR ASSÍNCRONA ---
    async def sair(e):
        await page.window.destroy()

    def criar_btn(nome_f):
        return ft.FilledButton(
            content=ft.Text(nome_f),
            data=nome_f,
            on_click=carregar_dados
        )

    # --- CONSTRUÇÃO DA PÁGINA ---
    page.add(
        # Título Centrado com a cor dos botões
        ft.Row(
            [ft.Text("Analisador Sonar - HC-SR04", size=32, weight="bold", color=cor_tema)],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        ft.Divider(height=20, color="transparent"),
        
        # Botões de ficheiros centrados
        ft.Row([
            criar_btn("LeituraSubidaSonar1.csv"),
            criar_btn("LeituraSubidaSonar2.csv"),
            criar_btn("LeituraSubidaSonar3.csv"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        
        ft.Row([
            criar_btn("LeituraDescidaSonar1.csv"),
            criar_btn("LeituraDescidaSonar2.csv"),
            criar_btn("LeituraDescidaSonar3.csv"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        
        ft.Row([
            ft.Container(
                content=ft.Column([tabela], scroll=ft.ScrollMode.ALWAYS),
                width=350, height=450, bgcolor="#1A1A1A", border_radius=10
            ),
            ft.Container(
                content=chart, expand=True, height=450, padding=30
            )
        ]),
        
        ft.Divider(),
        
        # Botão Sair centrado com Ícone
        ft.Row(
            [
                ft.FilledButton(
                    content=ft.Text("Sair"),
                    icon=ft.Icons.EXIT_TO_APP,
                    on_click=sair
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.run(main)