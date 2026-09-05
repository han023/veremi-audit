"""Experiment 1b - the trivial single-scalar baseline (paper Table `tab:scalar`).

Two statistics per identity, no training, no linkage, no physics:
    interval_med  median inter-arrival time of that identity's transmissions
    n_msgs        how many transmissions it sent

Direction is fixed A PRIORI, not chosen on the scores:
    an attacker splits one transmit budget across many ghosts, so each ghost
    sends *less often* -> larger interval, smaller count. We therefore score
    +interval_med and -n_msgs. Reporting max(a, 1-a) would be orientation
    selection on the test set; the signed value is what appears in the paper.

Metrics come from workspace/verify/v2_metrics.py, which is sklearn-free and
self-tested against sklearn and scipy.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/verify")
from sybilbench import analysis, loader  # noqa: E402
from v2_metrics import bootstrap_ci, rank_auc  # noqa: E402

ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]


def run(archive: str) -> dict:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)          # one row per transmission, not per reception

    rows = []
    for tok, g in ded.groupby("token", observed=True):
        t = np.sort(g["rcvTime"].to_numpy())
        if len(t) < 2:
            continue
        rows.append((tok, len(t), float(np.median(np.diff(t)))))
    f = pd.DataFrame(rows, columns=["token", "n_msgs", "interval_med"])
    f["y"] = f["token"].map(truth.is_attacker).astype(int)

    y = f["y"].to_numpy()
    sender = f["token"].map(truth.token_to_sender)
    ben = f.loc[y == 0, "interval_med"]
    atk = f.loc[y == 1, "interval_med"]

    auc_int = rank_auc(y, f["interval_med"].to_numpy())      # a priori: larger interval => attacker
    auc_cnt = rank_auc(y, -f["n_msgs"].to_numpy())           # a priori: fewer messages => attacker
    ci_int = bootstrap_ci(y, f["interval_med"].to_numpy(), n_boot=1000)
    ci_cnt = bootstrap_ci(y, -f["n_msgs"].to_numpy(), n_boot=1000)

    return {
        "archive": archive,
        "identities": len(f),
        "vehicles": int(sender.nunique()),
        "attacker_vehicles": int(sender[y == 1].nunique()),
        "prevalence_vehicles": round(float(sender[y == 1].nunique() / max(1, sender.nunique())), 4),
        "attacker_frac_identities": round(float(y.mean()), 4),
        "benign_interval_med": round(float(ben.median()), 3),
        "attacker_interval_med": round(float(atk.median()), 3),
        "AUC_interval_alone": round(auc_int, 4),
        "AUC_interval_lo": round(ci_int[0], 4), "AUC_interval_hi": round(ci_int[1], 4),
        "AUC_msgcount_alone": round(auc_cnt, 4),
        "AUC_msgcount_lo": round(ci_cnt[0], 4), "AUC_msgcount_hi": round(ci_cnt[1], 4),
    }


if __name__ == "__main__":
    out = []
    for a in ARCHIVES:
        if not loader.cache_path(a).exists():
            print(f"skip {a}", flush=True)
            continue
        r = run(a)
        out.append(r)
        print(r, flush=True)
    pd.DataFrame(out).to_csv("workspace/sybilbench/exp1b_rate_baseline_v2.csv", index=False)
    print("\n-> workspace/sybilbench/exp1b_rate_baseline_v2.csv")
