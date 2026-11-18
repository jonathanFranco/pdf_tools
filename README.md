# pdftools

Utilitários de PDF em linha de comando, usando o [qpdf](https://qpdf.readthedocs.io/): juntar, dividir, extrair páginas, rotacionar e proteger com senha.

| Comando | O que faz |
|---|---|
| [`join`](#join--juntar-pdfs-por-pessoa) (padrão) | Junta vários PDFs em um só por pessoa (ou qualquer prefixo) |
| [`split`](#split--dividir) | Divide um PDF em arquivos de N páginas |
| [`extract`](#extract--extrair-páginas) | Extrai páginas para um novo PDF |
| [`rotate`](#rotate--rotacionar) | Rotaciona páginas |
| [`encrypt`](#encrypt--proteger-com-senha) | Protege o PDF com senha (AES-256) |

## Instalação

### Windows (.exe)

1. Baixe o artifact **`pdftools-exe`** da última execução do workflow [Build EXE](../../actions/workflows/build-exe.yml).
2. Extraia `pdftools.exe` e a pasta `qpdf/` juntos (a pasta `qpdf/` precisa ficar ao lado do `.exe`).

Não precisa de Python instalado. Dê **duplo clique** no `pdftools.exe` para abrir o [menu interativo](#menu-interativo).

### Linux

Debian/Ubuntu (instala o qpdf via `apt` se faltar):

```bash
./run.sh                      # menu interativo
./run.sh <comando> [opções]   # linha de comando
```

Outras distros: instale o `qpdf` pelo gerenciador de pacotes e rode `python3 main.py`.

## Menu interativo

Abrindo sem argumentos (duplo clique no `.exe`, `./run.sh` ou `python3 main.py`), aparece um menu:

```
=== PDF Tools ===
  1) join     merge PDFs grouped by file name prefix
  2) split    split a PDF into chunks of N pages
  3) extract  extract pages into a new PDF
  4) rotate   rotate pages
  5) encrypt  protect a PDF with a password (AES-256)
  0) exit
Choose:
```

Escolha o número e responda as perguntas. Dicas:

- **Arraste o arquivo/pasta para a janela** para colar o caminho.
- `Enter` aceita o valor padrão mostrado entre `[colchetes]`.
- `Ctrl+C` cancela a ferramenta atual e volta ao menu.

## Linha de comando

> Nos exemplos abaixo, `pdftools` = `pdftools.exe`, `./run.sh` ou `python3 main.py`.

Todos os comandos que recebem um arquivo **não alteram o original**: geram um novo ao lado dele (ou em `-o`).

Intervalos de páginas seguem a sintaxe do qpdf: `1-3,5,8-z` (`z` = última página, `r1` = última, `r2` = penúltima…).

### `join` — juntar PDFs por pessoa

Percorre a pasta (e subpastas), agrupa os PDFs pelo texto **antes do primeiro `-`** no nome do arquivo e gera um PDF por grupo em `output/`.

```
documentos/
├── 1 - Identificação/
│   ├── João - RG.pdf
│   └── Maria - RG.pdf
├── 2 - Comprovantes/
│   ├── João - Residência.pdf
│   └── Maria - Residência.pdf
└── output/                      ← gerado
    ├── joão_2026-11-18_14-30.pdf    (RG + Residência)
    └── maria_2026-11-18_14-30.pdf
```

- **Agrupamento:** não diferencia maiúsculas/minúsculas (`João` = `joão`). Arquivo sem `-` usa o nome inteiro.
- **Ordem das páginas:** ordenação natural pelo caminho — numere as pastas (`1 -`, `2 -`, …, `10 -`) para controlar a ordem. Pastas sem número vão para o fim.
- **Pasta `output/`:** ignorada na busca, então rodar de novo não junta resultados antigos.

```
pdftools [join] [input] [-o OUTPUT] [-s SEPARATOR]
```

| Opção | Padrão | Descrição |
|---|---|---|
| `input` | pasta atual | Pasta com os PDFs |
| `-o`, `--output` | `<input>/output` | Pasta de saída |
| `-s`, `--separator` | `-` | Separador entre o nome do grupo e o resto do arquivo |

```bash
pdftools ~/documentos                          # "join" é o comando padrão
pdftools join ~/documentos -o ~/prontos -s _   # "joao_rg.pdf" → grupo "joao"
```

### `split` — dividir

```bash
pdftools split contrato.pdf            # 1 página por arquivo → contrato_split/contrato-01.pdf, ...
pdftools split contrato.pdf -n 5       # blocos de 5 páginas
pdftools split contrato.pdf -o partes/
```

### `extract` — extrair páginas

```bash
pdftools extract contrato.pdf 1-3,7    # → contrato_pages.pdf
pdftools extract contrato.pdf 2-z -o sem_capa.pdf
```

### `rotate` — rotacionar

Ângulo no sentido horário: `90`, `180`, `270` ou `-90`.

```bash
pdftools rotate scan.pdf 90            # todas as páginas → scan_rotated.pdf
pdftools rotate scan.pdf 180 -p 2,4    # só as páginas 2 e 4
```

### `encrypt` — proteger com senha

A senha é pedida no terminal (não aparece na tela, no histórico do shell nem na lista de processos).

```bash
pdftools encrypt contrato.pdf          # → contrato_protected.pdf
pdftools encrypt contrato.pdf -o seguro.pdf
```

## Código de saída

`0` em sucesso, `1` se algo falhar (no `join`, se qualquer grupo falhar).

## Requisitos (rodando pelo script)

- Python 3.8+ (sem dependências externas)
- `qpdf` no `PATH` ou em `qpdf/` na raiz do projeto

## Estrutura

```
main.py                 # entrada (CLI ou menu)
pdftools/
├── cli.py              # argparse + menu, montados a partir de TOOLS
├── core.py             # qpdf: localizar, executar, reportar
├── prompts.py          # perguntas do menu
└── tools/
    ├── __init__.py     # TOOLS = [join, split, extract, rotate, encrypt]
    └── <tool>.py       # uma ferramenta por arquivo
```

### Adicionando uma ferramenta

Crie `pdftools/tools/<nome>.py` com:

```python
NAME = "nome"
HELP = "descrição curta"

def add_arguments(p): ...   # argumentos da CLI (argparse)
def prompt(): ...           # perguntas do menu → lista de argumentos da CLI
def run(qpdf, args): ...    # executa; retorna 0 (ok) ou 1 (erro)
```

e adicione o módulo em `TOOLS` (`pdftools/tools/__init__.py`). CLI e menu passam a mostrá-la automaticamente.

## Build

O workflow [`.github/workflows/build-exe.yml`](.github/workflows/build-exe.yml) gera o `pdftools.exe` com PyInstaller a cada push na `master` (ou manualmente via *Run workflow*) e empacota o qpdf junto.
