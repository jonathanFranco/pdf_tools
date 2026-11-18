from pathlib import Path


def ask(prompt, default=None, required=False):
    hint = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt}{hint}: ").strip().strip("\"'") or default
        if value or not required:
            return value


def ask_file():
    while True:
        path = Path(ask("PDF file", required=True)).expanduser()
        if path.is_file():
            return str(path)
        print(f"  File not found: {path}")


def ask_pages(prompt, required=False):
    return ask(f"{prompt} (e.g. 1-3,5,8-z)", required=required)
