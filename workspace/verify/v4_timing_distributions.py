"""V4 - the timing shortcut, as a distribution rather than a single AUC.

The paper claims sibling identities share a transmission clock: their send-time
difference is an exact multiple of the beacon period, so (dt mod 0.5) collapses
to ~1e-5 for sibling pairs and sits near uniform for unrelated pairs. An AUC
alone cannot show that. This dumps the two distributions, their quantiles, a
bootstrap interval on the separation, and a rank-sum test.

Also measures what jitter does to the same quantity, which is the escape an
attacker gets for free.
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
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]
PERIOD = 0.5
JITTER = 0.25
QS = [0.05, 0.25, 0.5, 0.75, 0.95]


def phase_of(view, truth, seed=0, max_pairs=40000, jitter=0.0):
    v = analysis.transmissions(view)
    if jitter:
        rng = np.random.default_rng(seed + 500)
        v = v.copy()
        v["rcvTime"] = v["rcvTime"].to_numpy() + rng.uniform(-jitter, jitter, len(v))
    cands = analysis.pair_candidates(v, max_pairs=max_pairs, seed=seed)
    if cands.empty:
        return None
    feats = analysis.pair_features(v, cands)
    if feats.empty or "phase" not in feats:
        return None
    y = analysis.label_pairs(feats, truth).to_numpy()
    return feats["phase"].to_numpy(), y


def summarise(archive, jitter=0.0):
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    got = phase_of(view, truth, jitter=jitter)
    if got is None:
        return None
    phase, y = got
    sib, oth = phase[y == 1], phase[y == 0]
    if len(sib) < 20 or len(oth) < 20:
        return None
    # lower phase => same clock => sibling, so score -phase
    auc = rank_auc(y, -phase)
    lo, hi = bootstrap_ci(y, -phase, n_boot=2000, seed=3)
    from scipy.stats import mannwhitneyu
    u = mannwhitneyu(sib, oth, alternative="less")
    row = {"archive": archive, "jitter_s": jitter,
           "n_sibling": len(sib), "n_unrelated": len(oth),
           "sib_median": float(np.median(sib)), "oth_median": float(np.median(oth)),
           "phase_auc": round(auc, 4), "auc_lo": round(lo, 4), "auc_hi": round(hi, 4),
           "mannwhitney_p": float(u.pvalue)}
    for q in QS:
        row["sib_q%02d" % int(q * 100)] = float(np.quantile(sib, q))
        row["oth_q%02d" % int(q * 100)] = float(np.quantile(oth, q))
    return row


if __name__ == "__main__":
    rows = []
    for a in ARCHIVES:
        if not loader.cache_path(a).exists():
            continue
        for j in (0.0, JITTER):
            r = summarise(a, jitter=j)
            if r:
                rows.append(r)
                print({k: r[k] for k in ("archive", "jitter_s", "sib_median", "oth_median",
                                         "phase_auc", "auc_lo", "auc_hi", "mannwhitney_p")}, flush=True)
    pd.DataFrame(rows).to_csv("workspace/verify/v4_timing_distributions.csv", index=False)
    print("\n-> workspace/verify/v4_timing_distributions.csv")
