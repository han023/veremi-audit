"""V17 - one machine-readable census of all eight archives.

The paper prints a census table, but a table in a PDF is not a dataset. This joins
every per-archive measurement we made into a single wide CSV so a reader can use the
numbers rather than retype them.

Columns come from the raw scans, the identity census, the pseudonym map, the
single-scalar baseline, the linkage ablation and the cascade.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

V = Path("workspace/verify")
B = Path("workspace/sybilbench")

SOURCES = [
    (V / "v3c_identity_census.csv", "archive", None),
    (V / "v1b_raw_refined.csv", "archive",
     ["gt_messages", "identities", "copies_median", "copies_mean",
      "recv_records", "unique_transmissions", "shared_pseudonym_msgs"]),
    (V / "v3b_pseudomap.csv", "archive",
     ["distinct_pseudonyms", "encoding_pct_pairs", "encoding_pct_messages", "messages"]),
    (B / "exp1b_rate_baseline_v2.csv", "archive",
     ["benign_interval_med", "attacker_interval_med",
      "AUC_interval_alone", "AUC_interval_lo", "AUC_interval_hi",
      "AUC_msgcount_alone", "AUC_msgcount_lo", "AUC_msgcount_hi"]),
    (B / "exp1_results.csv", "archive",
     ["pairs", "positive_rate", "auc_all", "auc_geometry_only", "auc_timing_only"]),
    (B / "exp13_pseudonym_decode.csv", "archive",
     ["decode_accuracy", "decode_accuracy_shuffled", "chance_accuracy",
      "AUC_common_substring", "AUC_common_substring_shuffled"]),
]


def main() -> None:
    out = None
    for path, key, cols in SOURCES:
        if not path.exists():
            print("  missing, skipped: %s" % path.name)
            continue
        d = pd.read_csv(path)
        if cols:
            keep = [c for c in cols if c in d.columns]
            d = d[[key] + keep]
        d = d.add_prefix("")
        out = d if out is None else out.merge(d, on=key, how="outer",
                                              suffixes=("", "_" + path.stem[:6]))
        print("  merged %-34s %d columns" % (path.name, d.shape[1] - 1))

    # the cascade is long-form; pivot the headline stage values in
    casc = B / "exp9_cascade.csv"
    if casc.exists():
        c = pd.read_csv(casc).pivot(index="archive", columns="stage", values="auc")
        c.columns = ["cascade_" + str(x) for x in c.columns]
        out = out.merge(c.reset_index(), on="archive", how="outer")
        print("  merged %-34s %d columns" % (casc.name, c.shape[1]))

    out = out.sort_values("archive")
    dest = V / "v17_master_census.csv"
    out.to_csv(dest, index=False)
    print("\n-> %s: %d archives x %d columns" % (dest, len(out), out.shape[1]))
    print("   columns: %s ..." % ", ".join(list(out.columns)[:8]))


if __name__ == "__main__":
    main()
