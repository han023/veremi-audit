"""V20 - release the exact splits, so a later model can be compared against ours.

Reporting a number is not enough for anyone who wants to beat it. This writes the
identity-level train and test membership for the cascade's controlled protocol, per
archive and per seed, so a future detector can be scored on the same rows rather
than on its own resample.

Identities are named by their hashed token, which is what the public view carries.
The true vehicle is included because scoring needs the label; it is ground truth and
is not a feature.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/verify")
sys.path.insert(0, "workspace/sybilbench")
from sklearn.model_selection import GroupShuffleSplit  # noqa: E402

from sybilbench import analysis, loader  # noqa: E402
from exp9_cascade import KIN_FEATS, identity_features, subsample  # noqa: E402

ARCHIVES = ["GridSybil_0709", "GridSybil_1416"]
SEEDS = [0, 1, 2, 3, 4]
TARGET_PREV = 0.03
OUT = Path("workspace/verify/v20_splits.csv")


def run(archive: str) -> list[dict]:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    X = identity_features(ded, "token", None)
    senders = np.array([truth.token_to_sender.get(t, -1) for t in X.index])
    y = np.array([1 if truth.sender_to_attack.get(int(s), 0) != 0 else 0 for s in senders])
    tokens = np.array(X.index)

    rows = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        sel = subsample(y, TARGET_PREV, rng)
        ts, ys, gs = tokens[sel], y[sel], senders[sel]
        if ys.sum() < 20 or (1 - ys).sum() < 20:
            continue
        tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=seed)
                      .split(np.zeros((len(ys), 1)), ys, gs))
        if ys[tr].sum() < 5 or ys[te].sum() < 5:
            continue
        for idx, fold in ((tr, "train"), (te, "test")):
            for i in idx:
                rows.append({"archive": archive, "seed": seed, "fold": fold,
                             "token": ts[i], "vehicle": int(gs[i]),
                             "attacker": int(ys[i])})
    return rows


if __name__ == "__main__":
    out: list[dict] = []
    for a in (sys.argv[1:] or ARCHIVES):
        if not loader.cache_path(a).exists():
            continue
        r = run(a)
        out += r
        print("%-18s %d rows across %d seeds" % (a, len(r), len({x["seed"] for x in r})))
    df = pd.DataFrame(out)
    df.to_csv(OUT, index=False)
    print("\n-> %s: %d rows, %d identities, %d attacker"
          % (OUT, len(df), df.token.nunique(), int(df.attacker.sum())))
    print("   fold sizes:", df.groupby(["archive", "fold"]).size().to_dict())
