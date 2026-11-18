import argparse
import sys

from .core import find_qpdf
from .tools import TOOLS

TOOLS_BY_NAME = {tool.NAME: tool for tool in TOOLS}


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pdftools",
        description="PDF utilities powered by qpdf. Without arguments, opens an interactive menu.")
    sub = parser.add_subparsers(dest="command", required=True)
    for tool in TOOLS:
        p = sub.add_parser(tool.NAME, help=tool.HELP, description=tool.HELP)
        tool.add_arguments(p)
        p.set_defaults(func=tool.run)
    return parser


def main(argv):
    if argv[0] not in TOOLS_BY_NAME and argv[0] not in ("-h", "--help"):
        argv = ["join", *argv]
    args = build_parser().parse_args(argv)

    qpdf = find_qpdf()
    if not qpdf:
        print("❌ qpdf not found (neither in ./qpdf nor in PATH).", file=sys.stderr)
        return 1
    return args.func(qpdf, args)


def interactive():
    print("Tip: drag a file or folder into this window to paste its path.")
    while True:
        print("\n=== PDF Tools ===")
        for i, tool in enumerate(TOOLS, 1):
            print(f"  {i}) {tool.NAME:<8} {tool.HELP}")
        print("  0) exit")
        choice = input("Choose: ").strip()
        if choice == "0":
            return 0
        if not choice.isdigit() or not 1 <= int(choice) <= len(TOOLS):
            continue
        tool = TOOLS[int(choice) - 1]
        print()
        try:
            main([tool.NAME, *tool.prompt()])
        except SystemExit:
            pass
        except KeyboardInterrupt:
            print("\n  Cancelled.")


def run():
    for stream in (sys.stdout, sys.stderr):
        if stream:
            stream.reconfigure(errors="replace")
    argv = sys.argv[1:]
    try:
        code = main(argv) if argv else interactive()
    except (KeyboardInterrupt, EOFError):
        print()
        code = 130
    sys.exit(code)
