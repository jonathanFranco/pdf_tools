from pathlib import Path

from ..core import default_output, report, run_qpdf
from ..prompts import ask_file, ask_pages

NAME = "extract"
HELP = "extract pages into a new PDF"


def add_arguments(p):
    p.add_argument("file", type=Path)
    p.add_argument("pages", help="page ranges, e.g. 1-3,5,8-z (z = last page)")
    p.add_argument("-o", "--output", type=Path, help="output file (default: <file>_pages.pdf)")


def prompt():
    return [ask_file(), ask_pages("Pages", required=True)]


def run(qpdf, args):
    out = args.output or default_output(args.file, "pages")
    ok, err = run_qpdf(qpdf, [args.file, "--pages", ".", args.pages, "--", out])
    return report(ok, err, out)
