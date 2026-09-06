"""Record exactly what produced the paper's numbers.

The paper promises a release that pins code and library versions. This writes that
record: a SHA-256 for every script and result file, plus the interpreter and library
versions the results were produced with. It replaces a commit hash, which this
working tree does not have.
"""
from __future__ import annotations

import hashlib
import platform
import sys
from datetime import date
from pathlib import Path

ROOT = Path("workspace")
GROUPS = [
    ("loader and analysis", ["sybilbench/loader.py", "sybilbench/loader_veremi2018.py",
                             "sybilbench/analysis.py", "sybilbench/pseudonym_layer.py"]),
    ("experiments", sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "sybilbench").glob("exp*.py"))),
    ("independent verification", sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "verify").glob("v*.py"))),
    # globbed, not listed: a hardcoded list silently drops scripts added later,
    # and the paper promises a hash per file
    # "_"-prefixed files are scratch: a probe file left behind by a page-length
    # experiment was hashed here and shipped in the release before this filter
    ("paper", sorted(p.relative_to(ROOT).as_posix()
                     for ext in ("*.py", "*.tex", "*.pdf")
                     for p in (ROOT / "paper").glob(ext)
                     if not p.name.startswith("_"))),
    ("results", sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "sybilbench").glob("*.csv"))
                + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "verify").glob("*.csv"))),
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def versions() -> list[str]:
    out = ["python           " + sys.version.split()[0],
           "platform         " + platform.platform()]
    for mod in ("numpy", "pandas", "sklearn", "scipy", "matplotlib", "pyarrow"):
        try:
            m = __import__(mod)
            out.append("%-16s %s" % (mod, getattr(m, "__version__", "unknown")))
        except ImportError:
            out.append("%-16s not installed" % mod)
    return out


def main() -> None:
    lines = ["# Manifest", "",
             "Generated " + date.today().isoformat() + ".",
             "SHA-256 of every file that produced a number in the paper.", "",
             "## Environment", "", "```"]
    lines += versions()
    lines += ["```", ""]
    missing = []
    for title, files in GROUPS:
        lines += ["## " + title, "", "```"]
        for rel in files:
            p = ROOT / rel
            if not p.exists():
                missing.append(rel)
                continue
            lines.append("%s  %s" % (sha(p)[:16], rel))
        lines += ["```", ""]
    if missing:
        lines += ["## Referenced but absent", "", "```"] + missing + ["```", ""]
    (ROOT / "MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote workspace/MANIFEST.md")
    if missing:
        print("missing:", missing)


if __name__ == "__main__":
    main()
