"""V6 - the exact prevalence below which these archives stop supporting evaluation.

The paper says the archives cannot be evaluated below 3 %, while its own table
carries a 3 % row. That reads as a contradiction unless the floor is stated
exactly, so this measures it.

The mechanism is arithmetic, not a modelling choice. Subsampling to prevalence p
keeps k = round(p * N_benign / (1 - p)) attacker identities against a fixed benign
pool. A vehicle-disjoint test fold then receives roughly 30 % of those, and an AUC
computed on fewer than five positives is not an estimate of anything. This reports
the surviving positives per prevalence, measured rather than assumed.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/verify")
sys.path.insert(0, "workspace/sybilbench")
from sybilbench import analysis, loader  # noqa: E402
from exp9_cascade import identity_features  # noqa: E402

PREVALENCES = [0.005, 0.01, 0.02, 0.03, 0.05, 0.10, 0.20]
SEEDS = [0, 1, 2, 3, 4]
MIN_TEST_POS = 5          # the threshold every experiment in this work applies
ARCHIVES = ["GridSybil_0709", "GridSybil_1416"]


def subsample(y, target, rng):
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    keep = int(round(target * len(neg) / (1 - target)))
    if keep < 10 or keep >= len(pos):
        return None, keep
    sel = np.concatenate([rng.choice(pos, keep, replace=False), neg])
    rng.shuffle(sel)
    return sel, keep


def run(archive: str) -> list[dict]:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    X = identity_features(ded, "token", None)
    senders = np.array([truth.token_to_sender.get(t, -1) for t in X.index])
    y = np.array([1 if truth.sender_to_attack.get(int(s), 0) != 0 else 0 for s in senders])
    n_neg = int((y == 0).sum())
    n_pos = int(y.sum())

    rows = []
    for p in PREVALENCES:
        test_pos, ok = [], 0
        kept = None
        for s in SEEDS:
            rng = np.random.default_rng(s)
            sel, kept = subsample(y, p, rng)
            if sel is None:
                continue
            ys, gs = y[sel], senders[sel]
            if ys.sum() < 20 or (1 - ys).sum() < 20:
                continue
            tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=s)
                          .split(np.zeros((len(ys), 1)), ys, gs))
            test_pos.append(int(ys[te].sum()))
            ok += int(ys[te].sum() >= MIN_TEST_POS and ys[tr].sum() >= MIN_TEST_POS)
        rows.append({
            "archive": archive,
            "prevalence": p,
            "benign_identities": n_neg,
            "attacker_identities_available": n_pos,
            "attacker_identities_kept": kept,
            "test_positives_mean": round(float(np.mean(test_pos)), 1) if test_pos else 0.0,
            "test_positives_min": int(np.min(test_pos)) if test_pos else 0,
            "seeds_usable": ok,
            "usable": ok == len(SEEDS),
        })
        print(rows[-1], flush=True)
    return rows


if __name__ == "__main__":
    out = []
    for a in (sys.argv[1:] or ARCHIVES):
        out += run(a)
    df = pd.DataFrame(out)
    df.to_csv("workspace/verify/v6_prevalence_floor.csv", index=False)
    print("\n--- lowest fully usable prevalence per archive ---")
    for a, g in df.groupby("archive"):
        good = g[g.usable]
        print("%-18s %s" % (a, ("%.1f%%" % (100 * good.prevalence.min())) if len(good) else "none"))
    print("\n-> workspace/verify/v6_prevalence_floor.csv")
