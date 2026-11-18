import os
import shutil
import subprocess
import sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)
APP_DIR = Path(sys.executable).parent if FROZEN else Path(__file__).resolve().parent.parent


def find_qpdf():
    exe = "qpdf.exe" if os.name == "nt" else "qpdf"
    bundled = APP_DIR / "qpdf" / exe
    if bundled.is_file():
        return str(bundled)
    return shutil.which("qpdf")


def run_qpdf(qpdf, args, secret_args=None):
    cmd = [qpdf, *map(str, args)]
    stdin = None
    if secret_args:
        cmd.append("@-")
        stdin = "".join(f"{a}\n" for a in secret_args)
    result = subprocess.run(cmd, input=stdin, capture_output=True, text=True)
    return result.returncode in (0, 3), result.stderr.strip()


def report(ok, err, output):
    if ok:
        print(f"✅ {output}" + (f"\n⚠️  {err}" if err else ""))
    else:
        print(f"❌ Error: {err}")
    return 0 if ok else 1


def default_output(path, suffix):
    return path.with_name(f"{path.stem}_{suffix}.pdf")
