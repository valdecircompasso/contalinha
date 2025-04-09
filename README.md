# Conta Linha Script

![screenshot](screenshot.png "screenshot").

[English](#english) | [Português](#português-do-brasil)

<a name="english"></a>
## English

### Description
This Python script analyzes a specified directory, counts the total number of files, lines of code, blank lines, comment lines, and the total size of the files. It also provides detailed statistics by file type (extension) and saves a detailed report in CSV format.

### Requirements
* Python 3.x
* `rich` library

### Installation
1. Make sure you have Python 3 installed on your system.
2. Clone or download this repository (or just the `contalinha.py` script and `requirements.txt`).
3. Navigate to the directory where the files are located using the terminal.
4. Install the necessary dependency by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

### Usage
You can run the script in two ways:

1. **Using the Python script (with directory as argument):**

   ```bash
   python contalinha.py /path/to/your/directory
   ```
   Replace `/path/to/your/directory` with the full path of the directory you want to analyze. Requires Python and the `rich` library to be installed (see Installation section).

2. **Using the Python script (interactive):**

   ```bash
   python contalinha.py
   ```
   If you run the script without providing a directory path, it will prompt you to enter the path in the terminal. Requires Python and the `rich` library to be installed.

3. **Using the `contalinha.exe` executable (Windows - Recommended if you don't have Python):**

   The `contalinha.exe` file (located in the `dist` folder after optional packaging - see Packaging section) can be run directly on Windows without needing to install Python or dependencies.
   * Open Command Prompt (cmd) or PowerShell.
   * Navigate to the `dist` directory.
   * Run it by passing the directory as an argument:
     ```bash
     .\contalinha.exe /path/to/your/directory
     ```
     *(Note: In some terminals like PowerShell, you may need to use `.\` before the executable name)*
   * Or run it without arguments to be prompted to enter the path:
     ```bash
     .\contalinha.exe
     ```

### Output
The script will display in the console:

* A summary panel with the total number of files, total lines, blank lines, comment lines, code lines (total - blank - comment), and total size in Kbytes.
* A statistics panel showing the file count, total lines, blank lines, comment lines, code lines, total size (KB), and percentage of files for each extension type found, sorted by the number of files.

Additionally, the script will create a CSV file in the same directory where it was executed. The filename will follow the format `result_YYYY-MM-DD-HH-MM.csv` (with the current date and time). This file will contain:

1. Statistics by extension.
2. A detailed list of each file found, including its relative path, file type (extension), size in Kbytes, total lines, blank lines, comment lines, and code lines.

### Updates

#### April 9, 2025
* Added warning system for unrecognized file extensions
* The script now displays a highlighted warning panel when it encounters files with extensions not defined in the COMMENT_SYNTAX dictionary
* Warning includes a list of all unrecognized extensions, number and percentage of affected files and lines
* This helps identify potential inaccuracies in comment counting for files processed with generic patterns

#### April 7, 2025
* Added detection and counting of blank lines and comment lines
* Added calculation of actual code lines (total lines - blank lines - comment lines)
* Added percentage column to the summary table
* Enhanced support for detecting comments in over 50 programming languages
* Added fallback regex patterns for unrecognized file types

---

<a name="português-do-brasil"></a>
## Português do Brasil

### Descrição
Este script Python analisa um diretório especificado, conta o número total de arquivos, linhas de código, linhas em branco, linhas de comentários e o tamanho total dos arquivos. Ele também fornece estatísticas detalhadas por tipo de arquivo (extensão) e salva um relatório detalhado em formato CSV.

### Requisitos
* Python 3.x
* Biblioteca `rich`

### Instalação
1. Certifique-se de ter o Python 3 instalado em seu sistema.
2. Clone ou baixe este repositório (ou apenas o script `contalinha.py` e o `requirements.txt`).
3. Navegue até o diretório onde os arquivos estão localizados usando o terminal.
4. Instale a dependência necessária executando o seguinte comando:

   ```bash
   pip install -r requirements.txt
   ```

### Uso
Você pode executar o script de duas maneiras:

1. **Usando o script Python (com diretório como argumento):**

   ```bash
   python contalinha.py /caminho/para/seu/diretorio
   ```
   Substitua `/caminho/para/seu/diretorio` pelo caminho completo do diretório que você deseja analisar. Requer Python e a biblioteca `rich` instalados (veja a seção Instalação).

2. **Usando o script Python (interativo):**

   ```bash
   python contalinha.py
   ```
   Se você executar o script sem fornecer um caminho de diretório, ele solicitará que você digite o caminho no terminal. Requer Python e a biblioteca `rich` instalados.

3. **Usando o executável `contalinha.exe` (Windows - Recomendado se não tiver Python):**

   O arquivo `contalinha.exe` (localizado na pasta `dist` após o empacotamento opcional - veja seção Empacotamento) pode ser executado diretamente no Windows sem precisar instalar Python ou dependências.
   * Abra o Prompt de Comando (cmd) ou PowerShell.
   * Navegue até o diretório `dist`.
   * Execute passando o diretório como argumento:
     ```bash
     .\contalinha.exe /caminho/para/seu/diretorio
     ```
     *(Nota: Em alguns terminais como PowerShell, pode ser necessário usar `.\` antes do nome do executável)*
   * Ou execute sem argumentos para ser solicitado a inserir o caminho:
     ```bash
     .\contalinha.exe
     ```

### Saída
O script exibirá no console:

* Um painel de resumo com o número total de arquivos, linhas totais, linhas em branco, linhas de comentário, linhas de código (total - branco - comentário) e tamanho total em Kbytes.
* Um painel de estatísticas mostrando a contagem de arquivos, linhas totais, linhas em branco, linhas de comentário, linhas de código, tamanho total (KB) e porcentagem de arquivos para cada tipo de extensão encontrada, ordenado pelo número de arquivos.

Além disso, o script criará um arquivo CSV no mesmo diretório onde foi executado. O nome do arquivo seguirá o formato `result_AAAA-MM-DD-HH-MM.csv` (com a data e hora atuais). Este arquivo conterá:

1. As estatísticas por extensão.
2. Uma lista detalhada de cada arquivo encontrado, incluindo seu caminho relativo, tipo de arquivo (extensão), tamanho em Kbytes, número total de linhas, linhas em branco, linhas de comentário e linhas de código.

### Atualizações

#### 9 de Abril de 2025
* Adicionado sistema de aviso para extensões de arquivo não reconhecidas
* O script agora exibe um painel de aviso destacado quando encontra arquivos com extensões não definidas no dicionário COMMENT_SYNTAX
* O aviso inclui uma lista de todas as extensões não reconhecidas, número e porcentagem de arquivos e linhas afetados
* Isso ajuda a identificar possíveis imprecisões na contagem de comentários para arquivos processados com padrões genéricos

#### 7 de Abril de 2025
* Adicionada detecção e contagem de linhas em branco e linhas de comentário
* Adicionado cálculo de linhas de código reais (linhas totais - linhas em branco - linhas de comentário)
* Adicionada coluna de porcentagem à tabela de resumo
* Suporte aprimorado para detectar comentários em mais de 50 linguagens de programação
* Adicionados padrões regex de fallback para tipos de arquivo não reconhecidos
