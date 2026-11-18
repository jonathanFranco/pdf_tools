import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from ..core import report, run_qpdf
from ..prompts import ask

NAME = "join"
HELP = "merge PDFs grouped by file name prefix"


def add_arguments(p):
    p.add_argument("input", nargs="?", type=Path, default=Path.cwd(),
                   help="input folder (default: current folder)")
    p.add_argument("-o", "--output", type=Path,
                   help="output folder (default: <input>/output)")
    p.add_argument("-s", "--separator", default="-",
                   help="separator between the name and the rest of the file name (default: '-')")


def prompt():
    folder = Path(ask("Folder", str(Path.cwd()))).expanduser()
    return [str(folder), "-s", ask("Name separator", "-")]


def natural_key(path, root):
    rel = path.relative_to(root).as_posix().casefold()
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", rel)]


def collect(root, output_dir, separator):
    groups = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if Path(dirpath, d).resolve() != output_dir]
        for name in filenames:
            if name.lower().endswith(".pdf"):
                key = Path(name).stem.split(separator)[0].strip().casefold()
                groups[key].append(Path(dirpath, name))
    return groups


def run(qpdf, args):
    root = args.input.resolve()
    if not root.is_dir():
        print(f"❌ Folder not found: {root}", file=sys.stderr)
        return 1
    output_dir = (args.output or root / "output").resolve()

    print(f"📂 Base folder: {root}")
    groups = collect(root, output_dir, args.separator)
    if not groups:
        print("⚠️  No PDFs found.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    jobs = []
    for key, files in sorted(groups.items()):
        files.sort(key=lambda p: natural_key(p, root))
        safe_name = re.sub(r'[\\/:*?"<>|\s]+', "_", key)
        jobs.append((key, files, output_dir / f"{safe_name}_{timestamp}.pdf"))

    def merge(job):
        _, files, out = job
        return run_qpdf(qpdf, ["--empty", "--pages", *files, "--", out])

    with ThreadPoolExecutor() as pool:
        results = pool.map(merge, jobs)

    failures = 0
    for (key, files, out), (ok, err) in zip(jobs, results):
        print(f"\n🔗 '{key}':")
        for f in files:
            print(f"  👉 {f.relative_to(root)}")
        failures += report(ok, err, out)

    print(f"\n✅ {len(jobs) - failures}/{len(jobs)} PDFs written to {output_dir}")
    return 1 if failures else 0
