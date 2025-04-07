import os
import csv
import datetime
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

print("""
 #####  #     #    #    ######  #######    ####### #     #  #####  ### #     # ####### ####### ######  ### #     #  #####  
#     # ##   ##   # #   #     #    #       #       ##    # #     #  #  ##    # #       #       #     #  #  ##    # #     # 
#       # # # #  #   #  #     #    #       #       # #   # #        #  # #   # #       #       #     #  #  # #   # #       
 #####  #  #  # #     # ######     #       #####   #  #  # #  ####  #  #  #  # #####   #####   ######   #  #  #  # #  #### 
      # #     # ####### #   #      #       #       #   # # #     #  #  #   # # #       #       #   #    #  #   # # #     # 
#     # #     # #     # #    #     #       #       #    ## #     #  #  #    ## #       #       #    #   #  #    ## #     # 
 #####  #     # #     # #     #    #       ####### #     #  #####  ### #     # ####### ####### #     # ### #     #  #####
""")

# Inicializar o console Rich
console = Console()

def contar_arquivos_e_linhas(diretorio):
    """Conta os arquivos, linhas e tamanho em um diretório dado.

    Args:
        diretorio (str): Caminho completo do diretório.

    Returns:
        int: Número total de arquivos.
        int: Número total de linhas em todos os arquivos.
        int: Tamanho total dos arquivos em Kbytes.
        list: Lista de detalhes dos arquivos.
        dict: Contagem de arquivos por extensão.
        dict: Contagem de linhas por extensão.
    """

    total_arquivos = 0
    total_linhas = 0
    total_tamanho = 0
    detalhes_arquivos = []
    
    # Dicionários para contar arquivos e linhas por extensão
    arquivos_por_extensao = defaultdict(int)
    linhas_por_extensao = defaultdict(int)
    tamanho_por_extensao = defaultdict(float)
    
    # Processar os arquivos e coletar informações
    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            extensao = os.path.splitext(arquivo)[1].lower()
            if not extensao:
                extensao = "(sem extensão)"
                
            caminho_completo = os.path.join(raiz, arquivo)
            total_arquivos += 1
            arquivos_por_extensao[extensao] += 1

            try:
                with open(caminho_completo, 'r', encoding='latin-1') as f:
                    linhas = len(f.readlines())
                    total_linhas += linhas
                    linhas_por_extensao[extensao] += linhas

                tamanho = os.path.getsize(caminho_completo) / 1024  # tamanho em Kbytes
                total_tamanho += tamanho
                tamanho_por_extensao[extensao] += tamanho

                caminho_relativo = os.path.relpath(caminho_completo, diretorio)
                detalhes_arquivos.append((caminho_relativo, extensao, round(tamanho, 2), linhas))
            except FileNotFoundError:
                print(f"Arquivo não encontrado: {caminho_completo}")
                continue
            except Exception as e:
                print(f"Erro ao processar arquivo {caminho_completo}: {str(e)}")
                continue

    # Não ordenar por tamanho para manter a ordem original de processamento
    # detalhes_arquivos.sort(key=lambda x: x[2], reverse=True)

    return total_arquivos, total_linhas, total_tamanho, detalhes_arquivos, arquivos_por_extensao, linhas_por_extensao, tamanho_por_extensao

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        diretorio = sys.argv[1]
    else:
        diretorio = input("Digite o caminho do diretório: ")

    total_arquivos, total_linhas, total_tamanho, detalhes_arquivos, arquivos_por_extensao, linhas_por_extensao, tamanho_por_extensao = contar_arquivos_e_linhas(diretorio)

    # Criar tabela de resumo
    summary_table = Table(title=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Total Files", f"{total_arquivos:,}")
    summary_table.add_row("Total Lines", f"{total_linhas:,}")
    summary_table.add_row("Total Size", f"{total_tamanho:.2f} Kbytes")
    
    # Criar painel de resumo
    summary_panel = Panel(summary_table, title="Summary", border_style="white")
    
    # Criar tabela de estatísticas por extensão
    stats_table = Table(title=None)
    stats_table.add_column("File Type", style="cyan")
    stats_table.add_column("Files", style="magenta")
    stats_table.add_column("Total Lines", style="green")
    stats_table.add_column("Size (KB)", style="blue")
    stats_table.add_column("% of Files", style="yellow")
    
    # Ordenar extensões pelo número de arquivos (decrescente)
    extensoes_ordenadas = sorted(arquivos_por_extensao.keys(), 
                                key=lambda ext: arquivos_por_extensao[ext], 
                                reverse=True)
    
    # Adicionar linhas à tabela de estatísticas
    for ext in extensoes_ordenadas:
        porcentagem_arquivos = (arquivos_por_extensao[ext] / total_arquivos) * 100 if total_arquivos > 0 else 0
        stats_table.add_row(
            ext,
            f"{arquivos_por_extensao[ext]:,}",
            f"{linhas_por_extensao[ext]:,}",
            f"{tamanho_por_extensao[ext]:.2f}",
            f"{porcentagem_arquivos:.1f}%"
        )
    
    # Criar painel de estatísticas
    stats_panel = Panel(stats_table, title="Statistics by File Type", border_style="white")
    
    # Exibir os painéis
    console.print(summary_panel)
    console.print(stats_panel)
    
    # Obter a data e hora atual
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M")
    
    # Salvar em CSV com timestamp
    filename = f'result_{timestamp}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Adicionar estatísticas por extensão no início do arquivo
        csvwriter.writerow(["Estatísticas por extensão"])
        csvwriter.writerow(["Extensão", "Arquivos", "Linhas", "Tamanho (KB)"])
        
        for ext in extensoes_ordenadas:
            csvwriter.writerow([ext, arquivos_por_extensao[ext], linhas_por_extensao[ext], round(tamanho_por_extensao[ext], 2)])
        
        # Adicionar linha em branco para separar as seções
        csvwriter.writerow([])
        
        # Adicionar detalhes dos arquivos
        csvwriter.writerow(["Relative Path", "File Type", "File Size (Kbytes)", "Total of Lines"])
        csvwriter.writerows(detalhes_arquivos)
    
    # Exibir resultado formatado como no exemplo
#    print("\nResultado formatado:")
#    print(" Relative Path,File Type,File Size (Kbytes),Total of Lines")
#    for i, (caminho, tipo, tamanho, linhas) in enumerate(detalhes_arquivos, 2):  # Começando de 2 como no exemplo
#        print(f"{i:4d}   │ {caminho},{tipo},{tamanho},{linhas}")

    print(f"\nResultado salvo em {filename}")
