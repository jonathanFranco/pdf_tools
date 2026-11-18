from pathlib import Path

from ..core import report, run_qpdf
from ..prompts import ask, ask_file

NAME = "split"
HELP = "split a PDF into chunks of N pages"


def add_arguments(p):
    p.add_argument("file", type=Path)
    p.add_argument("-n", "--pages", type=int, default=1, help="pages per file (default: 1)")
    p.add_argument("-o", "--output", type=Path, help="output folder (default: <file>_split/)")


def prompt():
    return [ask_file(), "-n", ask("Pages per file", "1")]


def run(qpdf, args):
    out_dir = args.output or args.file.with_name(f"{args.file.stem}_split")
    out_dir.mkdir(parents=True, exist_ok=True)
    ok, err = run_qpdf(qpdf, [args.file, f"--split-pages={args.pages}",
                              out_dir / f"{args.file.stem}-%d.pdf"])
    return report(ok, err, out_dir)
