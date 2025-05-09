import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import csv
import datetime
import re
from collections import defaultdict

COMMENT_SYNTAX = {
    '.py': {'line': ['#'], 'block': [('"""', '"""'), ("'''", "'''")]},
    '.js': {'line': ['//'], 'block': [('/*', '*/')]},
    '.ts': {'line': ['//'], 'block': [('/*', '*/')]},
    '.jsx': {'line': ['//'], 'block': [('/*', '*/')]},
    '.tsx': {'line': ['//'], 'block': [('/*', '*/')]},
    '.html': {'line': [], 'block': [('<!--', '-->')]},
    '.htm': {'line': [], 'block': [('<!--', '-->')]},
    '.xml': {'line': [], 'block': [('<!--', '-->')]},
    '.svg': {'line': [], 'block': [('<!--', '-->')]},
    '.css': {'line': [], 'block': [('/*', '*/')]},
    '.scss': {'line': ['//'], 'block': [('/*', '*/')]},
    '.sass': {'line': ['//'], 'block': [('/*', '*/')]},
    '.less': {'line': ['//'], 'block': [('/*', '*/')]},
    '.c': {'line': ['//'], 'block': [('/*', '*/')]},
    '.cpp': {'line': ['//'], 'block': [('/*', '*/')]},
    '.h': {'line': ['//'], 'block': [('/*', '*/')]},
    '.hpp': {'line': ['//'], 'block': [('/*', '*/')]},
    '.cs': {'line': ['//'], 'block': [('/*', '*/')]},
    '.java': {'line': ['//'], 'block': [('/*', '*/')]},
    '.kt': {'line': ['//'], 'block': [('/*', '*/')]},
    '.sh': {'line': ['#'], 'block': []},
    '.bash': {'line': ['#'], 'block': []},
    '.zsh': {'line': ['#'], 'block': []},
    '.ps1': {'line': ['#'], 'block': [('<#', '#>')]},
    '.rb': {'line': ['#'], 'block': [('=begin', '=end')]},
    '.pl': {'line': ['#'], 'block': [('=pod', '=cut')]},
    '.pm': {'line': ['#'], 'block': [('=pod', '=cut')]},
    '.php': {'line': ['//','#'], 'block': [('/*', '*/')]},
    '.sql': {'line': ['--'], 'block': [('/*', '*/')]},
    '.lisp': {'line': [';'], 'block': []},
    '.clj': {'line': [';'], 'block': []},
    '.hs': {'line': ['--'], 'block': [('{-', '-}')]},
    '.lua': {'line': ['--'], 'block': [('--[[', ']]')]},
    '.go': {'line': ['//'], 'block': [('/*', '*/')]},
    '.rs': {'line': ['//'], 'block': [('/*', '*/')]},
    '.cob': {'line': ['*'], 'block': []},
    '.cbl': {'line': ['*'], 'block': []},
    '.cpy': {'line': ['*'], 'block': []},
    '.esf': {'line': ['*'], 'block': []},
    '.cics': {'line': ['*'], 'block': []},
    '.cicis': {'line': ['*'], 'block': []},
    '.jcl': {'line': ['*'], 'block': []},
    '.asm': {'line': [';'], 'block': []},
    '.s': {'line': [';', '#'], 'block': []},
    '.pas': {'line': ['//'], 'block': [('{', '}'), ('(*', '*)')]},
    '.f': {'line': ['!', 'C'], 'block': []},
    '.f90': {'line': ['!'], 'block': []},
    '.yml': {'line': ['#'], 'block': []},
    '.yaml': {'line': ['#'], 'block': []},
    '.md': {'line': [], 'block': []},  # Special handling for markdown
    '.r': {'line': ['#'], 'block': []},
    '.swift': {'line': ['//'], 'block': [('/*', '*/')]},
    '.dart': {'line': ['//'], 'block': [('/*', '*/')]},
    '.groovy': {'line': ['//'], 'block': [('/*', '*/')]},
    '.scala': {'line': ['//'], 'block': [('/*', '*/')]},
    '.erl': {'line': ['%'], 'block': []},
    '.ex': {'line': ['#'], 'block': []},
    '.exs': {'line': ['#'], 'block': []},
    '.jl': {'line': ['#'], 'block': [('#=', '=#')]},
    'Dockerfile': {'line': ['#'], 'block': []},
    'Makefile': {'line': ['#'], 'block': []},
    '.mk': {'line': ['#'], 'block': []},
    '.bat': {'line': ['REM', '::'], 'block': []},
    '.cmd': {'line': ['REM', '::'], 'block': []},
    '.asp': {'line': ["'", 'Rem'], 'block': []},
}

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

latest_results_data = None

def process_line(line, file_ext, in_block_comment=None):
    if not line.strip():
        return True, False, in_block_comment
    
    if in_block_comment:
        end_marker = in_block_comment
        if end_marker in line:
            code_after = line.split(end_marker, 1)[1].strip()
            return False, not bool(code_after), None
        return False, True, in_block_comment
    
    syntax = COMMENT_SYNTAX.get(file_ext.lower(), None)
    
    if syntax:
        for marker in syntax['line']:
            if line.strip().startswith(marker):
                return False, True, None
        
        for start, end in syntax['block']:
            if start in line:
                if end in line.split(start, 1)[1]:
                    parts = line.split(start, 1)
                    before = parts[0].strip()
                    after_parts = parts[1].split(end, 1)
                    after = after_parts[1].strip() if len(after_parts) > 0 else ""
                    return False, not (before or after), None
                return False, True, end
    else:
        for pattern in LINE_COMMENT_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                return False, True, None
        
        for start_pattern, end_pattern in BLOCK_COMMENT_PATTERNS:
            start_match = re.search(start_pattern, line)
            if start_match:
                end_match = re.search(end_pattern, line[start_match.end():])
                if end_match:
                    before = line[:start_match.start()].strip()
                    after = line[start_match.end() + end_match.end():].strip()
                    return False, not (before or after), None
                return False, True, end_pattern
    
    return False, False, None

def process_file(file_path, file_ext):
    total_lines = 0
    blank_lines = 0
    comment_lines = 0
    in_block_comment = None
    
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            for line_content in f: 
                total_lines += 1
                is_blank, is_comment, in_block_comment = process_line(line_content, file_ext, in_block_comment)
                
                if is_blank:
                    blank_lines += 1
                elif is_comment:
                    comment_lines += 1
    except Exception as e:
        print(f"Erro ao processar {file_path}: {str(e)}")
    
    return total_lines, blank_lines, comment_lines

def contar_arquivos_e_linhas(diretorio):
    overall_total_arquivos = 0
    overall_total_linhas = 0
    overall_total_tamanho = 0
    
    detalhes_arquivos = []
    
    extensoes_nao_reconhecidas = set()
    arquivos_nao_reconhecidos = 0
    linhas_nao_reconhecidas = 0
    
    arquivos_por_extensao = defaultdict(int)
    linhas_por_extensao = defaultdict(int)
    linhas_branco_por_extensao = defaultdict(int)
    linhas_comentario_por_extensao = defaultdict(int)
    tamanho_por_extensao = defaultdict(float)
    
    for raiz, _, arquivos in os.walk(diretorio): 
        for arquivo in arquivos:
            extensao = os.path.splitext(arquivo)[1].lower()
            if not extensao:
                extensao = "(sem extensão)"
            
            caminho_completo = os.path.join(raiz, arquivo)
            overall_total_arquivos += 1
            arquivos_por_extensao[extensao] += 1
            
            if extensao.lower() not in COMMENT_SYNTAX:
                extensoes_nao_reconhecidas.add(extensao)
                arquivos_nao_reconhecidos += 1
            
            try:
                linhas, linhas_branco, linhas_comentario = process_file(caminho_completo, extensao)
                
                overall_total_linhas += linhas
                
                if extensao.lower() not in COMMENT_SYNTAX:
                    linhas_nao_reconhecidas += linhas
                
                linhas_por_extensao[extensao] += linhas
                linhas_branco_por_extensao[extensao] += linhas_branco
                linhas_comentario_por_extensao[extensao] += linhas_comentario
                
                tamanho = os.path.getsize(caminho_completo) / 1024
                overall_total_tamanho += tamanho
                tamanho_por_extensao[extensao] += tamanho
                
                caminho_relativo = os.path.relpath(caminho_completo, diretorio)
                billable_lines_file = linhas - linhas_branco
                detalhes_arquivos.append((caminho_relativo, extensao, round(tamanho, 2), linhas, linhas_branco, linhas_comentario, billable_lines_file))
            except FileNotFoundError:
                print(f"Arquivo não encontrado: {caminho_completo}")
            except Exception as e:
                print(f"Erro ao processar arquivo {caminho_completo}: {str(e)}")
    
    return (overall_total_arquivos, overall_total_linhas, overall_total_tamanho, detalhes_arquivos, 
            arquivos_por_extensao, linhas_por_extensao, tamanho_por_extensao,
            linhas_branco_por_extensao, linhas_comentario_por_extensao,
            extensoes_nao_reconhecidas, arquivos_nao_reconhecidos, linhas_nao_reconhecidas)

def process_directory():
    global latest_results_data
    directory = filedialog.askdirectory()
    if directory:
        selected_directory_label.config(text=f"Selected Directory: {directory}") 
        latest_results_data = contar_arquivos_e_linhas(directory)
        display_results(latest_results_data)
        save_button.config(state=tk.NORMAL) 
    else:
        selected_directory_label.config(text="Selected Directory: None")
        latest_results_data = None
        save_button.config(state=tk.DISABLED)

def display_results(result_data):
    (total_arquivos, total_linhas, total_tamanho, _detalhes_arquivos, 
     arquivos_por_extensao, linhas_por_extensao, tamanho_por_extensao,
     linhas_branco_por_extensao, linhas_comentario_por_extensao,
     _extensoes_nao_reconhecidas, _arquivos_nao_reconhecidos, _linhas_nao_reconhecidas) = result_data

    # Clear previous results from both trees
    for item in summary_tree.get_children():
        summary_tree.delete(item)
    for item in details_tree.get_children():
        details_tree.delete(item)
    
    total_linhas_branco = sum(linhas_branco_por_extensao.values())
    total_linhas_comentario = sum(linhas_comentario_por_extensao.values())
    total_linhas_codigo = total_linhas - total_linhas_branco - total_linhas_comentario
    total_billable_lines = total_linhas - total_linhas_branco

    # Populate Summary TreeView
    summary_tree.insert("", tk.END, values=("Total Files", total_arquivos, ""), tags=('summary',))
    summary_tree.insert("", tk.END, values=("Total Lines", total_linhas, ""), tags=('summary',))
    summary_tree.insert("", tk.END, values=("Total Size", f"{total_tamanho:.2f} Kbytes", ""), tags=('summary',))
    
    blank_percent = (total_linhas_branco / total_linhas * 100) if total_linhas > 0 else 0
    comment_percent = (total_linhas_comentario / total_linhas * 100) if total_linhas > 0 else 0
    code_percent = (total_linhas_codigo / total_linhas * 100) if total_linhas > 0 else 0
    billable_percent = (total_billable_lines / total_linhas * 100) if total_linhas > 0 else 0
    
    summary_tree.insert("", tk.END, values=("Blank Lines", total_linhas_branco, f"{blank_percent:.1f}%"), tags=('summary',))
    summary_tree.insert("", tk.END, values=("Comment Lines", total_linhas_comentario, f"{comment_percent:.1f}%"), tags=('summary',))
    summary_tree.insert("", tk.END, values=("Code Lines", total_linhas_codigo, f"{code_percent:.1f}%"), tags=('summary',))
    summary_tree.insert("", tk.END, values=("Billable Lines", total_billable_lines, f"{billable_percent:.1f}%"), tags=('summary',))
    
    # Populate Details TreeView (Extension Stats)
    extensoes_ordenadas = sorted(arquivos_por_extensao.keys(), 
                                 key=lambda ext: arquivos_por_extensao[ext], 
                                 reverse=True)
    
    for i, ext in enumerate(extensoes_ordenadas):
        tag = 'ext_even' if i % 2 == 0 else 'ext_odd' 
        porcentagem_arquivos = (arquivos_por_extensao[ext] / total_arquivos) * 100 if total_arquivos > 0 else 0
        linhas_codigo_ext = linhas_por_extensao[ext] - linhas_branco_por_extensao[ext] - linhas_comentario_por_extensao[ext]
        billable_lines_ext = linhas_por_extensao[ext] - linhas_branco_por_extensao[ext]
        
        details_tree.insert("", tk.END, values=(
            ext, 
            f"{arquivos_por_extensao[ext]:,}", 
            f"{linhas_por_extensao[ext]:,}", 
            f"{tamanho_por_extensao[ext]:.2f}", 
            f"{porcentagem_arquivos:.1f}%", 
            f"{linhas_branco_por_extensao[ext]:,}", 
            f"{linhas_comentario_por_extensao[ext]:,}", 
            f"{linhas_codigo_ext:,}", 
            f"{billable_lines_ext:,}"
            ), tags=(tag,))

def save_statistics_to_csv():
    global latest_results_data
    if not latest_results_data:
        messagebox.showwarning("No Data", "Please process a directory first to generate statistics.")
        return

    (_total_arquivos, _total_linhas, _total_tamanho, detalhes_arquivos, 
     arquivos_por_extensao, linhas_por_extensao, tamanho_por_extensao,
     linhas_branco_por_extensao, linhas_comentario_por_extensao,
     _extensoes_nao_reconhecidas, _arquivos_nao_reconhecidos, _linhas_nao_reconhecidas) = latest_results_data

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M")
    default_filename = f'result_{timestamp}.csv'

    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile=default_filename,
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if not filepath: 
        return

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            csvwriter.writerow(["Estatísticas por extensão"]) # This seems like a title for the section below
            csvwriter.writerow(["Extensão", "Arquivos", "Linhas", "Tamanho (KB)", "Linhas em Branco", "Linhas de Comentário", "Linhas de Código", "Billable Lines"])
            
            extensoes_ordenadas = sorted(arquivos_por_extensao.keys(), 
                                         key=lambda ext: arquivos_por_extensao[ext], 
                                         reverse=True)
            for ext in extensoes_ordenadas:
                linhas_codigo_ext = linhas_por_extensao[ext] - linhas_branco_por_extensao[ext] - linhas_comentario_por_extensao[ext]
                billable_lines_ext = linhas_por_extensao[ext] - linhas_branco_por_extensao[ext]
                csvwriter.writerow([
                    ext, 
                    arquivos_por_extensao[ext], 
                    linhas_por_extensao[ext], 
                    round(tamanho_por_extensao[ext], 2),
                    linhas_branco_por_extensao[ext],
                    linhas_comentario_por_extensao[ext],
                    linhas_codigo_ext,
                    billable_lines_ext
                ])
            
            csvwriter.writerow([]) 
            
            csvwriter.writerow(["Relative Path", "File Type", "File Size (Kbytes)", "Total of Lines", "Blank Lines", "Comment Lines", "Code Lines", "Billable Lines"])
            
            for arquivo_detalhe in detalhes_arquivos: # This is the per-file detail, not summary or per-extension
                caminho, ext_detalhe, tamanho_detalhe, linhas_detalhe, linhas_branco_detalhe, linhas_comentario_detalhe, billable_lines_file_detalhe = arquivo_detalhe
                linhas_codigo_detalhe = linhas_detalhe - linhas_branco_detalhe - linhas_comentario_detalhe
                csvwriter.writerow([caminho, ext_detalhe, tamanho_detalhe, linhas_detalhe, linhas_branco_detalhe, linhas_comentario_detalhe, linhas_codigo_detalhe, billable_lines_file_detalhe])
        
        messagebox.showinfo("Save Successful", f"Statistics saved to {filepath}")
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save file: {str(e)}")

app = tk.Tk()
app.title("Contalinha UI")
app.configure(bg='#f0f0f0') 

style = ttk.Style(app)
style.theme_use("clam") 

style.configure("TButton", padding=6, relief="flat", background="#cccccc", foreground="black", font=('Calibri', 10))
style.map("TButton", background=[('active', '#b0b0b0')])
style.configure("TLabel", padding=5, background="#f0f0f0", font=('Calibri', 10))
style.configure("Treeview.Heading", 
                background="#e1e1e1", 
                foreground="black", 
                relief="flat", 
                font=('Calibri', 10, 'bold'))
style.map("Treeview.Heading", background=[('active', '#d1d1d1')])

# Common Treeview row font
tree_font = ('Calibri', 10)

# Summary TreeView
summary_columns = ("Metric", "Value", "Percentage")
summary_tree = ttk.Treeview(app, columns=summary_columns, show="headings", height=7) # height for ~7 summary rows
summary_tree.heading("Metric", text="Metric")
summary_tree.heading("Value", text="Value")
summary_tree.heading("Percentage", text="Percentage")
summary_tree.column("Metric", width=150, anchor='w')
summary_tree.column("Value", width=100, anchor='e')
summary_tree.column("Percentage", width=100, anchor='e')
summary_tree.tag_configure('summary', background='#e6f3ff', font=tree_font)
style.configure('summary.Treeview', font=tree_font, rowheight=25) # Apply base style for summary rows

# Details TreeView (Extension Stats)
details_columns = ("File Type", "Files", "Total Lines", "Size (KB)", "% of Files", "Blank Lines", "Comment Lines", "Code Lines", "Billable Lines")
details_tree = ttk.Treeview(app, columns=details_columns, show="headings")
details_tree.heading("File Type", text="File Type")
details_tree.heading("Files", text="Files")
details_tree.heading("Total Lines", text="Total Lines")
details_tree.heading("Size (KB)", text="Size (KB)")
details_tree.heading("% of Files", text="% of Files")
details_tree.heading("Blank Lines", text="Blank Lines")
details_tree.heading("Comment Lines", text="Comment Lines")
details_tree.heading("Code Lines", text="Code Lines")
details_tree.heading("Billable Lines", text="Billable Lines")

details_tree.tag_configure('ext_even', background='white', font=tree_font)
details_tree.tag_configure('ext_odd', background='#f0f8ff', font=tree_font) # AliceBlue
style.configure('details.Treeview', font=tree_font, rowheight=25) # Apply base style for details rows

for col_id in details_columns:
    details_tree.column(col_id, width=100, anchor='e' if col_id not in ["File Type"] else 'w')


instruction_label = ttk.Label(app, text="Select a directory to process:")
instruction_label.pack(pady=5)

process_button = ttk.Button(app, text="Select Directory", command=process_directory)
process_button.pack(pady=5)

selected_directory_label = ttk.Label(app, text="Selected Directory: None") 
selected_directory_label.pack(pady=5)

save_button = ttk.Button(app, text="Save Statistics", command=save_statistics_to_csv, state=tk.DISABLED) 
save_button.pack(pady=5)

# Add a label for the Summary section
summary_label = ttk.Label(app, text="Summary", font=('Calibri', 12, 'bold'))
summary_label.pack(pady=(10,0))
summary_tree.pack(pady=5, fill="x", expand=False) # Summary tree doesn't need to expand y

# Add a label for the Extension Statistics section
details_label = ttk.Label(app, text="Statistics by File Type", font=('Calibri', 12, 'bold'))
details_label.pack(pady=(10,0))
details_tree.pack(pady=10, fill="both", expand=True)


app.mainloop()