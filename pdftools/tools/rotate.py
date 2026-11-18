from pathlib import Path

from ..core import default_output, report, run_qpdf
from ..prompts import ask, ask_file, ask_pages

NAME = "rotate"
HELP = "rotate pages"
ANGLES = ["90", "180", "270", "-90"]


def add_arguments(p):
    p.add_argument("file", type=Path)
    p.add_argument("angle", choices=ANGLES, help="clockwise degrees")
    p.add_argument("-p", "--pages", help="page ranges (default: all)")
    p.add_argument("-o", "--output", type=Path, help="output file (default: <file>_rotated.pdf)")


def prompt():
    argv = [ask_file(), ask(f"Angle ({', '.join(ANGLES)})", "90")]
    pages = ask_pages("Pages, blank = all")
    return argv + (["-p", pages] if pages else [])


def run(qpdf, args):
    angle = args.angle if args.angle.startswith("-") else f"+{args.angle}"
    pages = f":{args.pages}" if args.pages else ""
    out = args.output or default_output(args.file, "rotated")
    ok, err = run_qpdf(qpdf, [args.file, f"--rotate={angle}{pages}", out])
    return report(ok, err, out)
