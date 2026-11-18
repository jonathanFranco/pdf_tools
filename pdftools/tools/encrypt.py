import getpass
import sys
from pathlib import Path

from ..core import default_output, report, run_qpdf
from ..prompts import ask_file

NAME = "encrypt"
HELP = "protect a PDF with a password (AES-256)"


def add_arguments(p):
    p.add_argument("file", type=Path)
    p.add_argument("-o", "--output", type=Path, help="output file (default: <file>_protected.pdf)")


def prompt():
    return [ask_file()]


def run(qpdf, args):
    password = getpass.getpass("Password: ")
    if not password or password != getpass.getpass("Confirm password: "):
        print("❌ Passwords are empty or do not match.", file=sys.stderr)
        return 1
    out = args.output or default_output(args.file, "protected")
    ok, err = run_qpdf(qpdf, [args.file, out],
                       secret_args=["--encrypt", password, password, "256", "--"])
    return report(ok, err, out)
