# Conta Linha Script

Este script Python analisa um diretório especificado, conta o número total de arquivos, linhas de código e o tamanho total dos arquivos. Ele também fornece estatísticas detalhadas por tipo de arquivo (extensão) e salva um relatório detalhado em formato CSV.

## Requisitos

*   Python 3.x
*   Biblioteca `rich`

## Instalação

1.  Certifique-se de ter o Python 3 instalado em seu sistema.
2.  Clone ou baixe este repositório (ou apenas o script `contalinha.py` e o `requirements.txt`).
3.  Navegue até o diretório onde os arquivos estão localizados usando o terminal.
4.  Instale a dependência necessária executando o seguinte comando:

    ```bash
    pip install -r requirements.txt
    ```

## Uso

Você pode executar o script de duas maneiras:

1.  **Usando o script Python (com diretório como argumento):**

    ```bash
    python contalinha.py /caminho/para/seu/diretorio
    ```
    Substitua `/caminho/para/seu/diretorio` pelo caminho completo do diretório que você deseja analisar. Requer Python e a biblioteca `rich` instalados (veja a seção Instalação).

2.  **Usando o script Python (interativo):**

    ```bash
    python contalinha.py
    ```
    Se você executar o script sem fornecer um caminho de diretório, ele solicitará que você digite o caminho no terminal. Requer Python e a biblioteca `rich` instalados.

3.  **Usando o executável `contalinha.exe` (Windows - Recomendado se não tiver Python):**

    O arquivo `contalinha.exe` (localizado na pasta `dist` após o empacotamento opcional - veja seção Empacotamento) pode ser executado diretamente no Windows sem precisar instalar Python ou dependências.
    *   Abra o Prompt de Comando (cmd) ou PowerShell.
    *   Navegue até o diretório `dist`.
    *   Execute passando o diretório como argumento:
        ```bash
        .\contalinha.exe /caminho/para/seu/diretorio
        ```
        *(Nota: Em alguns terminais como PowerShell, pode ser necessário usar `.\` antes do nome do executável)*
    *   Ou execute sem argumentos para ser solicitado a inserir o caminho:
        ```bash
        .\contalinha.exe
        ```

## Saída

O script exibirá no console:

*   Um painel de resumo com o número total de arquivos, linhas e tamanho total em Kbytes.
*   Um painel de estatísticas mostrando a contagem de arquivos, linhas totais, tamanho total (KB) e porcentagem de arquivos para cada tipo de extensão encontrada, ordenado pelo número de arquivos.

Além disso, o script criará um arquivo CSV no mesmo diretório onde foi executado. O nome do arquivo seguirá o formato `result_AAAA-MM-DD-HH-MM.csv` (com a data e hora atuais). Este arquivo conterá:

1.  As estatísticas por extensão.
2.  Uma lista detalhada de cada arquivo encontrado, incluindo seu caminho relativo, tipo de arquivo (extensão), tamanho em Kbytes e número de linhas.

