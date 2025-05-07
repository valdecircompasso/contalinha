import os
import csv
import datetime
import re
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Valdecir Carvalho - utilitario para contar linhas de codigo fonte para o smart engineering


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

# Mapeamento de extensões de arquivo para sintaxe de comentários
COMMENT_SYNTAX = {
    # Python
    '.py': {'line': ['#'], 'block': [('"""', '"""'), ("'''", "'''")]},
    # JavaScript/TypeScript
    '.js': {'line': ['//'], 'block': [('/*', '*/')]},
    '.ts': {'line': ['//'], 'block': [('/*', '*/')]},
    '.jsx': {'line': ['//'], 'block': [('/*', '*/')]},
    '.tsx': {'line': ['//'], 'block': [('/*', '*/')]},
    # HTML/XML
    '.html': {'line': [], 'block': [('<!--', '-->')]},
    '.htm': {'line': [], 'block': [('<!--', '-->')]},
    '.xml': {'line': [], 'block': [('<!--', '-->')]},
    '.svg': {'line': [], 'block': [('<!--', '-->')]},
    # CSS
    '.css': {'line': [], 'block': [('/*', '*/')]},
    '.scss': {'line': ['//'], 'block': [('/*', '*/')]},
    '.sass': {'line': ['//'], 'block': [('/*', '*/')]},
    '.less': {'line': ['//'], 'block': [('/*', '*/')]},
    # C-family
    '.c': {'line': ['//'], 'block': [('/*', '*/')]},
    '.cpp': {'line': ['//'], 'block': [('/*', '*/')]},
    '.h': {'line': ['//'], 'block': [('/*', '*/')]},
    '.hpp': {'line': ['//'], 'block': [('/*', '*/')]},
    '.cs': {'line': ['//'], 'block': [('/*', '*/')]},
    # Java
    '.java': {'line': ['//'], 'block': [('/*', '*/')]},
    '.kt': {'line': ['//'], 'block': [('/*', '*/')]},
    # Shell scripts
    '.sh': {'line': ['#'], 'block': []},
    '.bash': {'line': ['#'], 'block': []},
    '.zsh': {'line': ['#'], 'block': []},
    '.ps1': {'line': ['#'], 'block': [('<#', '#>')]},
    # Ruby
    '.rb': {'line': ['#'], 'block': [('=begin', '=end')]},
    # Perl
    '.pl': {'line': ['#'], 'block': [('=pod', '=cut')]},
    '.pm': {'line': ['#'], 'block': [('=pod', '=cut')]},
    # PHP
    '.php': {'line': ['//','#'], 'block': [('/*', '*/')]},
    # SQL
    '.sql': {'line': ['--'], 'block': [('/*', '*/')]},
    # Lisp family
    '.lisp': {'line': [';'], 'block': []},
    '.clj': {'line': [';'], 'block': []},
    # Haskell
    '.hs': {'line': ['--'], 'block': [('{-', '-}')]},
    # Lua
    '.lua': {'line': ['--'], 'block': [('--[[', ']]')]},
    # Go
    '.go': {'line': ['//'], 'block': [('/*', '*/')]},
    # Rust
    '.rs': {'line': ['//'], 'block': [('/*', '*/')]},
    # COBOL
    '.cob': {'line': ['*'], 'block': []},
    '.cbl': {'line': ['*'], 'block': []},
    '.cpy': {'line': ['*'], 'block': []},
    '.esf': {'line': ['*'], 'block': []},
    '.cics': {'line': ['*'], 'block': []},
    '.cicis': {'line': ['*'], 'block': []},
    '.jcl': {'line': ['*'], 'block': []},
    # Assembly
    '.asm': {'line': [';'], 'block': []},
    '.s': {'line': [';', '#'], 'block': []},
    # Pascal
    '.pas': {'line': ['//'], 'block': [('{', '}'), ('(*', '*)')]},
    # Fortran
    '.f': {'line': ['!', 'C'], 'block': []},
    '.f90': {'line': ['!'], 'block': []},
    # YAML
    '.yml': {'line': ['#'], 'block': []},
    '.yaml': {'line': ['#'], 'block': []},
    # Markdown
    '.md': {'line': [], 'block': []},  # Special handling for markdown
    # R
    '.r': {'line': ['#'], 'block': []},
    # Swift
    '.swift': {'line': ['//'], 'block': [('/*', '*/')]},
    # Dart
    '.dart': {'line': ['//'], 'block': [('/*', '*/')]},
    # Groovy
    '.groovy': {'line': ['//'], 'block': [('/*', '*/')]},
    # Scala
    '.scala': {'line': ['//'], 'block': [('/*', '*/')]},
    # Erlang
    '.erl': {'line': ['%'], 'block': []},
    # Elixir
    '.ex': {'line': ['#'], 'block': []},
    '.exs': {'line': ['#'], 'block': []},
    # Julia
    '.jl': {'line': ['#'], 'block': [('#=', '=#')]},
    # Dockerfile
    'Dockerfile': {'line': ['#'], 'block': []},
    # Makefile
    'Makefile': {'line': ['#'], 'block': []},
    '.mk': {'line': ['#'], 'block': []},
    # Batch
    '.bat': {'line': ['REM', '::'], 'block': []},
    '.cmd': {'line': ['REM', '::'], 'block': []},
    # ASP Classic
    '.asp': {'line': ["'", 'Rem'], 'block': []},

}

# Padrões comuns de comentários por linha para arquivos não reconhecidos
LINE_COMMENT_PATTERNS = [
    r'^\s*#',        # Python, Shell, Ruby
    r'^\s*//',       # C-like, Java, JS, Go
    r'^\s*;',        # Lisp, Assembly
    r'^\s*--',       # SQL, Ada, Haskell
    r'^\s*\*',       # Dentro de /* ... */ blocos ou COBOL
    r'^\s*REM\s',    # Batch files (case insensitive)
    r'^\s*::',       # Batch files alternative
    r'^\s*%',        # Erlang
    r'^\s*!'         # Fortran
]

# Padrões comuns de blocos de comentários para arquivos não reconhecidos
BLOCK_COMMENT_PATTERNS = [
    (r'/\*', r'\*/'),         # C, Java, JavaScript
    (r'\(\*', r'\*\)'),       # Pascal, OCaml
    (r'"""', r'"""'),         # Python
    (r"'''", r"'''"),         # Python
    (r'<!--', r'-->'),        # HTML, XML
    (r'{-', r'-}'),           # Haskell
    (r'=begin', r'=end'),     # Ruby
    (r'=pod', r'=cut'),       # Perl
    (r'<#', r'#>'),           # PowerShell
    (r'#=', r'=#'),           # Julia
]

def process_line(line, file_ext, in_block_comment=None):
    """
    Processa uma linha para determinar se é em branco, comentário ou código.
    
    Args:
        line (str): A linha a ser processada
        file_ext (str): Extensão do arquivo para determinar a sintaxe de comentário
        in_block_comment (str ou None): Se estiver dentro de um comentário de bloco, contém o marcador de fim
        
    Returns:
        tuple: (is_blank, is_comment, new_in_block_comment)
    """
    # Verifica se a linha está em branco (vazia ou apenas espaços)
    if not line.strip():
        return True, False, in_block_comment
        
    # Se estamos dentro de um comentário de bloco, verifica se ele termina nesta linha
    if in_block_comment:
        end_marker = in_block_comment
        if end_marker in line:
            # Verifica se há código após o marcador de fim
            code_after = line.split(end_marker, 1)[1].strip()
            return False, not bool(code_after), None
        return False, True, in_block_comment
    
    # Obtém a sintaxe de comentário para este tipo de arquivo
    syntax = COMMENT_SYNTAX.get(file_ext.lower(), None)
    
    if syntax:
        # Verifica comentários de linha
        for marker in syntax['line']:
            if line.strip().startswith(marker):
                return False, True, None
                
        # Verifica comentários de bloco
        for start, end in syntax['block']:
            if start in line:
                # Se o comentário de bloco começa e termina na mesma linha
                if end in line.split(start, 1)[1]:
                    # Verifica se há código antes do marcador de início ou após o marcador de fim
                    parts = line.split(start, 1)
                    before = parts[0].strip()
                    after_parts = parts[1].split(end, 1)
                    after = after_parts[1].strip() if len(after_parts) > 1 else ""
                    return False, not (before or after), None
                return False, True, end
    else:
        # Usa padrões regex para tipos de arquivo desconhecidos
        for pattern in LINE_COMMENT_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                return False, True, None
                
        for start_pattern, end_pattern in BLOCK_COMMENT_PATTERNS:
            start_match = re.search(start_pattern, line)
            if start_match:
                # Verifica se o comentário de bloco termina na mesma linha
                end_match = re.search(end_pattern, line[start_match.end():])
                if end_match:
                    # Verifica se há código antes ou depois do comentário
                    before = line[:start_match.start()].strip()
                    after = line[start_match.end() + end_match.end():].strip()
                    return False, not (before or after), None
                return False, True, end_pattern
    
    # Se chegamos aqui, é uma linha de código
    return False, False, None

def process_file(file_path, file_ext):
    """
    Processa um arquivo para contar linhas totais, em branco e de comentário.
    
    Args:
        file_path (str): Caminho para o arquivo
        file_ext (str): Extensão do arquivo
        
    Returns:
        tuple: (total_lines, blank_lines, comment_lines)
    """
    total_lines = 0
    blank_lines = 0
    comment_lines = 0
    in_block_comment = None
    
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            for line in f:
                total_lines += 1
                is_blank, is_comment, in_block_comment = process_line(line, file_ext, in_block_comment)
                
                if is_blank:
                    blank_lines += 1
                elif is_comment:
                    comment_lines += 1
    except Exception as e:
        print(f"Erro ao processar {file_path}: {str(e)}")
        
    return total_lines, blank_lines, comment_lines

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
        dict: Tamanho por extensão.
        dict: Contagem de linhas em branco por extensão.
        dict: Contagem de linhas de comentário por extensão.
    """

    total_arquivos = 0
    total_linhas = 0
    total_linhas_branco = 0
    total_linhas_comentario = 0
    total_tamanho = 0
    detalhes_arquivos = []
    
    # Conjunto para rastrear extensões não reconhecidas
    extensoes_nao_reconhecidas = set()
    arquivos_nao_reconhecidos = 0
    linhas_nao_reconhecidas = 0
    
    # Dicionários para contar arquivos e linhas por extensão
    arquivos_por_extensao = defaultdict(int)
    linhas_por_extensao = defaultdict(int)
    linhas_branco_por_extensao = defaultdict(int)
    linhas_comentario_por_extensao = defaultdict(int)
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
            
            # Verificar se a extensão é reconhecida
            if extensao.lower() not in COMMENT_SYNTAX:
                extensoes_nao_reconhecidas.add(extensao)
                arquivos_nao_reconhecidos += 1

            try:
                # Processar o arquivo para contar linhas totais, em branco e de comentário
                linhas, linhas_branco, linhas_comentario = process_file(caminho_completo, extensao)
                
                total_linhas += linhas
                total_linhas_branco += linhas_branco
                total_linhas_comentario += linhas_comentario
                
                # Contar linhas em arquivos não reconhecidos
                if extensao.lower() not in COMMENT_SYNTAX:
                    linhas_nao_reconhecidas += linhas
                
                linhas_por_extensao[extensao] += linhas
                linhas_branco_por_extensao[extensao] += linhas_branco
                linhas_comentario_por_extensao[extensao] += linhas_comentario

                tamanho = os.path.getsize(caminho_completo) / 1024  # tamanho em Kbytes
                total_tamanho += tamanho
                tamanho_por_extensao[extensao] += tamanho

                caminho_relativo = os.path.relpath(caminho_completo, diretorio)
                billable_lines_file = linhas - linhas_branco
                detalhes_arquivos.append((caminho_relativo, extensao, round(tamanho, 2), linhas, linhas_branco, linhas_comentario, billable_lines_file))
            except FileNotFoundError:
                print(f"Arquivo não encontrado: {caminho_completo}")
                continue
            except Exception as e:
                print(f"Erro ao processar arquivo {caminho_completo}: {str(e)}")
                continue

    # Não ordenar por tamanho para manter a ordem original de processamento
    # detalhes_arquivos.sort(key=lambda x: x[2], reverse=True)

    return (total_arquivos, total_linhas, total_tamanho, detalhes_arquivos, 
            arquivos_por_extensao, linhas_por_extensao, tamanho_por_extensao,
            linhas_branco_por_extensao, linhas_comentario_por_extensao,
            extensoes_nao_reconhecidas, arquivos_nao_reconhecidos, linhas_nao_reconhecidas)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        diretorio = sys.argv[1]
    else:
        diretorio = input("Digite o caminho do diretório: ")

    (total_arquivos, total_linhas, total_tamanho, detalhes_arquivos, 
     arquivos_por_extensao, linhas_por_extensao, tamanho_por_extensao,
     linhas_branco_por_extensao, linhas_comentario_por_extensao,
     extensoes_nao_reconhecidas, arquivos_nao_reconhecidos, linhas_nao_reconhecidas) = contar_arquivos_e_linhas(diretorio)

    # Calcular totais de linhas em branco e de comentário
    total_linhas_branco = sum(linhas_branco_por_extensao.values())
    total_linhas_comentario = sum(linhas_comentario_por_extensao.values())
    
    # Calcular linhas de código (total - branco - comentário)
    total_linhas_codigo = total_linhas - total_linhas_branco - total_linhas_comentario

    # Criar tabela de resumo
    summary_table = Table(title=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    summary_table.add_column("Percentage", style="yellow")
    
    # Adicionar linhas à tabela de resumo com percentuais
    summary_table.add_row("Total Files", f"{total_arquivos:,}", "100.0%")
    summary_table.add_row("Total Lines", f"{total_linhas:,}", "100.0%")
    
    # Calcular percentuais para os tipos de linhas
    blank_percent = (total_linhas_branco / total_linhas * 100) if total_linhas > 0 else 0
    comment_percent = (total_linhas_comentario / total_linhas * 100) if total_linhas > 0 else 0
    code_percent = (total_linhas_codigo / total_linhas * 100) if total_linhas > 0 else 0
    
    summary_table.add_row("Blank Lines", f"{total_linhas_branco:,}", f"{blank_percent:.1f}%")
    summary_table.add_row("Comment Lines", f"{total_linhas_comentario:,}", f"{comment_percent:.1f}%")
    summary_table.add_row("Code Lines", f"{total_linhas_codigo:,}", f"{code_percent:.1f}%")
    summary_table.add_row("Total Size", f"{total_tamanho:.2f} Kbytes", "100.0%")
    
    # Criar painel de resumo
    summary_panel = Panel(summary_table, title="Summary", border_style="white")
    
    # Criar tabela de estatísticas por extensão
    stats_table = Table(title=None)
    stats_table.add_column("File Type", style="cyan")
    stats_table.add_column("Files", style="magenta")
    stats_table.add_column("Total Lines", style="green")
    stats_table.add_column("Size (KB)", style="blue")
    stats_table.add_column("% of Files", style="yellow")
    stats_table.add_column("Blank Lines", style="cyan")
    stats_table.add_column("Comment Lines", style="magenta")
    stats_table.add_column("Code Lines", style="green")
    stats_table.add_column("Billable Lines", style="blue")
    
    # Ordenar extensões pelo número de arquivos (decrescente)
    extensoes_ordenadas = sorted(arquivos_por_extensao.keys(), 
                                key=lambda ext: arquivos_por_extensao[ext], 
                                reverse=True)
    
    # Adicionar linhas à tabela de estatísticas
    for ext in extensoes_ordenadas:
        porcentagem_arquivos = (arquivos_por_extensao[ext] / total_arquivos) * 100 if total_arquivos > 0 else 0
        linhas_codigo = linhas_por_extensao[ext] - linhas_branco_por_extensao[ext] - linhas_comentario_por_extensao[ext]
        stats_table.add_row(
            ext,
            f"{arquivos_por_extensao[ext]:,}",
            f"{linhas_por_extensao[ext]:,}",
            f"{tamanho_por_extensao[ext]:.2f}",
            f"{porcentagem_arquivos:.1f}%",
            f"{linhas_branco_por_extensao[ext]:,}",
            f"{linhas_comentario_por_extensao[ext]:,}",
            f"{linhas_codigo:,}",
            f"{(linhas_por_extensao[ext] - linhas_branco_por_extensao[ext]):,}"
        )
    
    # Criar painel de estatísticas
    stats_panel = Panel(stats_table, title="Statistics by File Type", border_style="white")
    
    # Exibir os painéis
    console.print(summary_panel)
    console.print(stats_panel)
    
    # Exibir aviso sobre extensões não reconhecidas
    if extensoes_nao_reconhecidas:
        porcentagem_arquivos = (arquivos_nao_reconhecidos / total_arquivos) * 100 if total_arquivos > 0 else 0
        porcentagem_linhas = (linhas_nao_reconhecidas / total_linhas) * 100 if total_linhas > 0 else 0
        
        warning_text = (
            f"[bold]Foram encontrados {arquivos_nao_reconhecidos:,} arquivos ({porcentagem_arquivos:.1f}%) "
            f"com extensões não reconhecidas:[/]\n"
            f"{', '.join(sorted(extensoes_nao_reconhecidas))}\n\n"
            f"Estes arquivos contêm {linhas_nao_reconhecidas:,} linhas ({porcentagem_linhas:.1f}% do total).\n"
            f"Os comentários nesses arquivos foram identificados usando padrões genéricos, "
            f"o que pode resultar em contagens imprecisas.\n\n"
            f"[italic]Considere adicionar essas extensões ao dicionário COMMENT_SYNTAX com as regras apropriadas.[/]"
        )
        
        console.print(Panel(
            warning_text,
            title="[bold yellow]AVISO: Extensões Não Reconhecidas[/]",
            border_style="yellow"
        ))
    
    # Obter a data e hora atual
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M")
    
    # Salvar em CSV com timestamp
    filename = f'result_{timestamp}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Adicionar estatísticas por extensão no início do arquivo
        csvwriter.writerow(["Estatísticas por extensão"])
        csvwriter.writerow(["Extensão", "Arquivos", "Linhas", "Tamanho (KB)", "Linhas em Branco", "Linhas de Comentário", "Linhas de Código", "Billable Lines"])
        
        for ext in extensoes_ordenadas:
            linhas_codigo = linhas_por_extensao[ext] - linhas_branco_por_extensao[ext] - linhas_comentario_por_extensao[ext]
            billable_lines_ext = linhas_por_extensao[ext] - linhas_branco_por_extensao[ext]
            csvwriter.writerow([
                ext, 
                arquivos_por_extensao[ext], 
                linhas_por_extensao[ext], 
                round(tamanho_por_extensao[ext], 2),
                linhas_branco_por_extensao[ext],
                linhas_comentario_por_extensao[ext],
                linhas_codigo,
                billable_lines_ext
            ])
        
        # Adicionar linha em branco para separar as seções
        csvwriter.writerow([])
        
        # Adicionar detalhes dos arquivos
        csvwriter.writerow(["Relative Path", "File Type", "File Size (Kbytes)", "Total of Lines", "Blank Lines", "Comment Lines", "Code Lines", "Billable Lines"])
        
        # Adicionar cada arquivo com suas estatísticas
        for arquivo in detalhes_arquivos:
            caminho, ext, tamanho, linhas, linhas_branco, linhas_comentario, billable_lines_file = arquivo # Unpack new value
            linhas_codigo = linhas - linhas_branco - linhas_comentario
            csvwriter.writerow([caminho, ext, tamanho, linhas, linhas_branco, linhas_comentario, linhas_codigo, billable_lines_file])
    
    # Exibir resultado formatado como no exemplo
#    print("\nResultado formatado:")
#    print(" Relative Path,File Type,File Size (Kbytes),Total of Lines")
#    for i, (caminho, tipo, tamanho, linhas) in enumerate(detalhes_arquivos, 2):  # Começando de 2 como no exemplo
#        print(f"{i:4d}   │ {caminho},{tipo},{tamanho},{linhas}")

    print(f"\nResultado salvo em {filename}")
