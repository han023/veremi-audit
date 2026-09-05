"""V19 - does the released code reproduce every table in the paper?

The paper asserts that every number traces to a released file, and the claim checker
verifies the paper against those files. This closes the other half: it re-reads each
result file and confirms the values the paper prints are the values the file holds,
table by table, naming the script that must be run to regenerate each.

It does not re-run the experiments. Re-running the cascade takes about two hours and
the outputs are seeded; this checks that what shipped matches what is printed.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

TEX = Path("workspace/paper/veremi_audit.tex").read_text(encoding="utf-8")
BODY = TEX[TEX.index(r"\begin{document}"):TEX.index(r"\begin{thebibliography}")]
BODY = re.sub(r"\\textbf\{([^}]*)\}", r"\1", BODY)


def cells(label: str) -> str:
    i = BODY.index(r"\label{tab:%s}" % label)
    return BODY[i:BODY.index(r"\end{tabular}", i)]


CHECKS = [
    ("VI  decode", "decode", "sybilbench/exp13_pseudonym_decode.csv",
     "exp13_pseudonym_decode.py",
     lambda d, c: [("%.3f" % d.decode_accuracy.mean(), c),
                   ("%.4f" % d.decode_accuracy_shuffled.mean(), c)]),
    ("VIII scalar", "scalar", "sybilbench/exp1b_rate_baseline_v2.csv",
     "exp1b_rate_baseline.py",
     lambda d, c: [("%.3f" % v, c) for v in d.AUC_interval_alone] +
                  [("%.3f" % v, c) for v in d.AUC_msgcount_alone]),
    ("XI  cascade", "cascade", "sybilbench/exp9_cascade.csv", "exp9_cascade.py",
     lambda d, c: [("%.3f" % v, c) for v in
                   d[d.archive.str.startswith("GridSybil")].auc.dropna()]),
    ("XII single-factor", "single", "sybilbench/exp14_single_factor.csv",
     "exp14_single_factor.py",
     lambda d, c: [("%+.3f" % v, c) for v in
                   d[(d.archive == "GridSybil_0709") &
                     (d.factor != "controlled baseline")].delta.dropna()]),
    ("XIII sensitivity", "sensitivity", "sybilbench/exp10_sensitivity.csv",
     "exp10_sensitivity.py",
     lambda d, c: [("%.3f" % v, c) for v in
                   d[d.sweep.isin(["prevalence", "jitter_native", "cap_native",
                                   "beacon_native"])].auc]),
    ("XIV path loss", "pathloss", "verify/v5_pathloss.csv", "v5_pathloss_replicate.py",
     lambda d, c: [("%.3f" % v, c) for v in list(d.auc_fold_mean) + list(d.auc_oof)]),
    ("XV  NextGen", "nextgen", "verify/v15_nextgen_shortcuts.csv",
     "v15_nextgen_shortcuts.py",
     lambda d, c: [("%.3f" % d.AUC_msgcount.min(), c),
                   ("%.3f" % d.AUC_msgcount.max(), c)]),
]

bad = 0
for name, label, rel, script, fn in CHECKS:
    path = Path("workspace") / rel
    if not path.exists():
        print("  %-18s MISSING %s" % (name, rel))
        bad += 1
        continue
    c = cells(label)
    pairs = fn(pd.read_csv(path), c)
    missing = [v for v, hay in pairs if v not in hay]
    status = "ok" if not missing else "MISMATCH %s" % missing[:3]
    bad += bool(missing)
    print("  %-18s %-28s %s" % (name, script, status))

print("\n%s" % ("every checked table matches its file"
                if not bad else "%d tables disagree with their files" % bad))
raise SystemExit(1 if bad else 0)
