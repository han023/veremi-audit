"""V14 - the derived evidence that makes the corpus counts checkable without the corpus.

Three released verifiers read `workspace/text`, the 92 extracted full texts. Those
are other people's papers and we do not redistribute them, so from the artefact
alone v7, v11 and v12 cannot run and their counts cannot be checked. That makes
Table III unverifiable for a reader, which is precisely the failure this paper
complains about elsewhere.

The fix is to ship the derived data rather than the source. This emits one boolean
per (paper, item): did the pattern match anywhere in that paper's text. Every count
in Table III, in the dataset-usage figures and in the ns-2 claim is a column sum of
this matrix, so a reader can recompute all of them from the artefact.

Run with `--verify` to recompute the counts from the shipped matrix and compare them
against the CSVs the other scripts produced.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "workspace/verify")

TEXT = Path("workspace/text")
MATRIX = Path("workspace/verify/v14_match_matrix.csv")

from v11_reporting_table import ADDED, ORIGINAL  # noqa: E402
from v7_dataset_usage import PATTERNS, SIMULATORS  # noqa: E402

ITEMS: dict[str, str] = {}
ITEMS.update({("report:" + k): v for k, v in ORIGINAL.items()})
ITEMS.update({("report:" + k): v for k, v in ADDED.items()})
ITEMS.update({("usage:" + k): v for k, v in PATTERNS.items()})
ITEMS.update({("sim:" + k): v for k, v in SIMULATORS.items()})


def build() -> pd.DataFrame:
    files = sorted(TEXT.glob("*.txt"))
    if not files:
        raise SystemExit("workspace/text is empty; run this where the corpus lives")
    rows = []
    for f in files:
        t = f.read_text(encoding="utf-8", errors="ignore")
        row = {"file": f.name, "year": f.name[:4] if f.name[:4].isdigit() else ""}
        for item, pat in ITEMS.items():
            row[item] = bool(re.search(pat, t, re.I | re.S))
        rows.append(row)
    return pd.DataFrame(rows)


def verify(df: pd.DataFrame) -> int:
    """Recompute the published counts from the matrix alone."""
    bad = 0
    rep = pd.read_csv("workspace/verify/v11_reporting_table.csv").set_index("item")
    for item in list(ORIGINAL) + list(ADDED):
        got = int(df["report:" + item].sum())
        want = int(rep.loc[item, "papers"])
        ok = got == want
        bad += not ok
        print("  %-38s matrix %3d  file %3d  %s" % (item, got, want, "ok" if ok else "MISMATCH"))

    use = pd.read_csv("workspace/verify/v7_dataset_usage.csv").set_index("item")
    for item in PATTERNS:
        got = int(df["usage:" + item].sum())
        want = int(use.loc[item, "papers"])
        ok = got == want
        bad += not ok
        print("  %-38s matrix %3d  file %3d  %s" % (item, got, want, "ok" if ok else "MISMATCH"))

    cf = pd.read_csv("workspace/verify/v12_corpus_facts.csv").iloc[0]
    recent = df[df.year.astype(str) >= "2021"]
    got = int(recent["sim:NS-2"].sum())
    want = int(cf.ns2_since_2021)
    ok = got == want
    bad += not ok
    print("  %-38s matrix %3d  file %3d  %s" % ("ns-2 since 2021", got, want,
                                                "ok" if ok else "MISMATCH"))
    return bad


if __name__ == "__main__":
    if "--verify" in sys.argv and MATRIX.exists():
        df = pd.read_csv(MATRIX)
        print("verifying published counts against the shipped matrix (%d papers)\n" % len(df))
        bad = verify(df)
        print("\n%s" % ("all counts reproduce from the matrix" if not bad
                        else "%d MISMATCHES" % bad))
        sys.exit(1 if bad else 0)

    df = build()
    df.to_csv(MATRIX, index=False)
    print("wrote %s: %d papers x %d items\n" % (MATRIX, len(df), len(ITEMS)))
    bad = verify(df)
    print("\n%s" % ("all counts reproduce from the matrix" if not bad else "%d MISMATCHES" % bad))
    sys.exit(1 if bad else 0)
