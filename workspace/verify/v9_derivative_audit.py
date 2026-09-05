"""V9 - audit the preprocessed VeReMi derivative.

The paper claims this file cannot express the Sybil task and that a receiver-disjoint
split on it degenerates. Those claims had no released script, which is the same defect
we corrected for the single-scalar table. This is that script.

Measured here:
  * row count and column list, to show no sender or pseudonym column exists
  * the receiver-identifier distribution, which is what degenerates the split
  * a receiver-disjoint attempt, reporting accuracy and F1 together

Accuracy and F1 are reported side by side deliberately. Accuracy alone looks perfect
on a split whose test fold contains a single class; F1 is what exposes it.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupShuffleSplit

CSV = Path("workspace/datasets/VeReMi_preprocessed/balanced_veremi_dataset.csv")
FEATS = ["pos_0", "pos_1", "pos_noise_0", "pos_noise_1",
         "spd_0", "spd_1", "spd_noise_0", "spd_noise_1",
         "acl_0", "acl_1", "acl_noise_0", "acl_noise_1",
         "hed_0", "hed_1", "hed_noise_0", "hed_noise_1"]


def main() -> None:
    df = pd.read_csv(CSV)
    n = len(df)
    print("rows: %d" % n)
    print("columns: %s" % ", ".join(df.columns))

    identity_cols = [c for c in df.columns
                     if c.lower() in {"sender", "senderpseudo", "pseudonym", "sender_id"}]
    print("identity columns present: %s" % (identity_cols or "NONE"))

    rc = df["ReceiverID"].value_counts()
    top2 = rc.head(2)
    singletons = int((rc == 1).sum())
    print("distinct receivers: %d" % len(rc))
    print("top two receivers hold %d rows (%.1f %% of all)"
          % (int(top2.sum()), 100 * top2.sum() / n))
    print("receivers holding exactly one row: %d" % singletons)
    print("attack types: %d" % df["AttackerType"].nunique())

    y = (df["AttackerType"].astype(str).str.lower() != "normal").astype(int).to_numpy()
    if y.mean() in (0.0, 1.0):
        y = (df["AttackerType"].astype(str) != df["AttackerType"].mode()[0]).astype(int).to_numpy()
    X = df[FEATS].to_numpy()
    groups = df["ReceiverID"].to_numpy()
    print("positive rate: %.4f" % y.mean())

    rows = []
    for seed in range(5):
        tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=seed).split(X, y, groups))
        assert not (set(groups[tr]) & set(groups[te])), "receiver leaked across the split"
        classes_in_test = len(np.unique(y[te]))
        if len(np.unique(y[tr])) < 2:
            rows.append({"seed": seed, "note": "train fold single-class",
                         "test_rows": len(te), "test_classes": classes_in_test})
            print(rows[-1], flush=True)
            continue
        # 200 trees, matching every other experiment in this work
        m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2,
                                   n_jobs=-1, random_state=seed)
        m.fit(X[tr], y[tr])
        p = m.predict(X[te])
        rows.append({
            "seed": seed,
            "train_rows": len(tr), "test_rows": len(te),
            "test_classes": classes_in_test,
            "test_positive_rate": round(float(y[te].mean()), 4),
            "accuracy": round(float(accuracy_score(y[te], p)), 4),
            "f1": round(float(f1_score(y[te], p, zero_division=0)), 4),
        })
        print(rows[-1], flush=True)

    out = pd.DataFrame(rows)
    out.to_csv("workspace/verify/v9_derivative_audit.csv", index=False)

    summary = pd.DataFrame([{
        "rows": n,
        "distinct_receivers": len(rc),
        "top2_rows": int(top2.sum()),
        "top2_share_pct": round(100 * top2.sum() / n, 1),
        "singleton_receivers": singletons,
        "attack_types": int(df["AttackerType"].nunique()),
        "identity_columns": len(identity_cols),
    }])
    summary.to_csv("workspace/verify/v9_derivative_summary.csv", index=False)
    print("\n-> workspace/verify/v9_derivative_audit.csv and _summary.csv")


if __name__ == "__main__":
    main()
