"""Build the artefact archive for deposit.

Ships code, result tables and documentation. Excludes the 12 GB of source archives
and the 207 MB parquet cache, both of which are reproducible from the Zenodo records
by running the ingest step.
"""
from __future__ import annotations

import hashlib
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path("workspace")
OUT = Path("workspace/release")
NAME = "veremi-audit-artefact"

INCLUDE = [
    ("sybilbench", "*.py"),
    ("sybilbench", "*.csv"),
    ("sybilbench", "*.md"),
    ("verify", "*.py"),
    ("verify", "*.csv"),
    ("verify", "*.json"),
    ("paper", "*.py"),
    ("paper", "*.tex"),
    ("paper", "*.pdf"),
    ("paper", "*.png"),
    ("paper", "*.md"),
    ("synthesis", "*.md"),
    ("notes", "*.json"),
]
TOP_LEVEL = ["REPRODUCE.md", "MANIFEST.md", "DEPOSIT.md", "make_manifest.py",
             "make_release.py", "verify_datasets.py", "deep_extract.py",
             # the paper promises a container and pinned versions; ship both
             "Dockerfile", "requirements.txt", "ZENODO_RECORD.md",
             "SUBMISSION_GUIDE.md", "ZENODO_FIELDS.md"]
EXCLUDE_DIRS = {"cache", "__pycache__", "release", "datasets", "text"}


def wanted(p: Path) -> bool:
    # "_"-prefixed names are scratch. _probe.tex, left over from a page-length
    # experiment, shipped in a release before this check existed.
    if p.name.startswith("_"):
        return False
    return not any(part in EXCLUDE_DIRS for part in p.parts)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{NAME}-{date.today().isoformat()}.zip"

    files: list[Path] = []
    for sub, pattern in INCLUDE:
        for p in sorted((ROOT / sub).rglob(pattern)):
            if p.is_file() and wanted(p):
                files.append(p)
    for name in TOP_LEVEL:
        p = ROOT / name
        if p.is_file():
            files.append(p)
    # the corpus index and bibliography live at the project root
    for name in ("index.csv", "references.bib", "README.md", "LICENSE", "CITATION.cff"):
        p = Path(name)
        if p.is_file():
            files.append(p)

    seen = set()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            if p in seen:
                continue
            seen.add(p)
            # keep the workspace/ prefix: every script addresses files as
            # workspace/..., so flattening it here would break the archive
            arc = Path(NAME) / p
            z.write(p, arc.as_posix())

    h = hashlib.sha256(target.read_bytes()).hexdigest()
    size_mb = target.stat().st_size / 1e6
    print(f"{target}")
    print(f"  files : {len(seen)}")
    print(f"  size  : {size_mb:.1f} MB")
    print(f"  sha256: {h}")

    by_dir: dict[str, int] = {}
    for p in seen:
        key = p.parent.name if p.parent != Path(".") else "(root)"
        by_dir[key] = by_dir.get(key, 0) + 1
    print("\n  contents:")
    for k, v in sorted(by_dir.items()):
        print(f"    {k:<14} {v}")
    return target


def selftest(archive: Path) -> int:
    """Unpack the archive somewhere clean and run what it promises.

    The archive shipped for several rounds with a flattened layout and with the
    JSON evidence missing, so nothing in it would have run. This catches that.
    """
    import subprocess
    import sys
    import tempfile
    import zipfile

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(archive) as z:
            z.extractall(tmp)
        root = Path(tmp) / NAME
        steps = [
            ("metric self-test", ["workspace/verify/v2_metrics.py"]),
            ("corpus counts", ["workspace/verify/v14_match_matrix.py", "--verify"]),
            ("assemble paper", ["workspace/paper/assemble.py"]),
            ("sentence check", ["workspace/paper/check_sentences.py"]),
            ("reference check", ["workspace/paper/check_refs.py"]),
            ("claim check", ["workspace/paper/check_claims.py"]),
        ]
        bad = 0
        for label, cmd in steps:
            r = subprocess.run([sys.executable] + cmd, cwd=root,
                               capture_output=True, text=True)
            tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
            ok = r.returncode == 0
            bad += not ok
            print("  %-18s %-4s %s" % (label, "ok" if ok else "FAIL", tail[:60]))
        return bad


if __name__ == "__main__":
    import sys
    target = main()
    if "--selftest" in sys.argv:
        print()
        print("self-test, from a clean unpack:")
        raise SystemExit(1 if selftest(target) else 0)
