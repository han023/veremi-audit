"""Experiment 14 - single-factor add-back, to test the cascade's ordering.

The cascade removes advantages cumulatively, so each increment is conditional on
what was already removed. That is a fair objection: a different order could
redistribute the effect, and stages may interact.

This answers it from the other end. Starting from the fully controlled protocol,
we add back exactly one advantage at a time and measure the change. These effects
are order-independent by construction: every one is measured against the same
baseline, not against its predecessor.

If the cascade's ordering were carrying the story, the two designs would disagree
about which advantage matters. If they agree, the ordering is not doing the work.

Where an added factor leaves the test rows unchanged, the comparison is paired and
the interval comes from a paired bootstrap over those rows. Where the factor changes
which rows exist -- ground-truth aggregation changes the unit from identity to
vehicle, and prevalence subsampling changes the population -- pairing is impossible
and we say so rather than reporting a paired interval that is not one.
"""
from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/verify")
sys.path.insert(0, "workspace/sybilbench")
from sybilbench import analysis, loader  # noqa: E402
from exp9_cascade import load_pseudomap, run_stage  # noqa: E402
from v2_metrics import rank_auc  # noqa: E402

ARCHIVES = ["GridSybil_0709", "GridSybil_1416"]
SEEDS = [0, 1, 2, 3, 4]
N_BOOT = 2000

# the fully controlled protocol: every advantage removed
BASE = dict(gt_agg=False, pseudo=False, disjoint=True, prev=True, jitter=True, rate=False)

# adding one advantage back means flipping one switch
FACTORS = {
    "ground-truth key": ("gt_agg", True),
    "pseudonym feature": ("pseudo", True),
    "random folds": ("disjoint", False),
    "native prevalence": ("prev", False),
    "no jitter": ("jitter", False),
    "rate features": ("rate", True),
}
# these change which rows exist, so a paired test is not defined
UNPAIRABLE = {"ground-truth key", "native prevalence"}


def paired_delta_ci(y, p_base, p_alt, seed=11):
    """Bootstrap the AUC difference on the same rows, resampled together."""
    rng = np.random.default_rng(seed)
    n = len(y)
    out = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        if 0 < y[idx].sum() < n:
            out.append(rank_auc(y[idx], p_alt[idx]) - rank_auc(y[idx], p_base[idx]))
    if not out:
        return float("nan"), float("nan")
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(lo), float(hi)


def run(archive: str) -> list[dict]:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    pmap = load_pseudomap(archive)

    base = [run_stage(ded, truth, pmap, BASE, s) for s in SEEDS]
    base = [b for b in base if b]
    if not base:
        return []
    base_auc = np.array([b["auc"] for b in base])

    rows = [{
        "archive": archive, "factor": "controlled baseline",
        "auc": round(float(base_auc.mean()), 4),
        "auc_sd": round(float(base_auc.std(ddof=1)), 4),
        "delta": 0.0, "paired": True,
    }]

    for label, (key, value) in FACTORS.items():
        cfg = dict(BASE)
        cfg[key] = value
        alt = [run_stage(ded, truth, pmap, cfg, s) for s in SEEDS]
        alt = [a for a in alt if a]
        if not alt:
            rows.append({"archive": archive, "factor": label, "note": "degenerate"})
            print(rows[-1], flush=True)
            continue
        alt_auc = np.array([a["auc"] for a in alt])
        rec = {
            "archive": archive, "factor": label,
            "auc": round(float(alt_auc.mean()), 4),
            "auc_sd": round(float(alt_auc.std(ddof=1)), 4),
            "delta": round(float(alt_auc.mean() - base_auc.mean()), 4),
            "paired": label not in UNPAIRABLE,
        }
        # Paired interval where the two arms score the same rows. The interval is
        # computed on one seed's rows, so it must be reported beside THAT seed's
        # delta, not beside the five-seed mean. Printing a mean next to a
        # single-split interval is the defect this paper criticises elsewhere.
        if rec["paired"]:
            b0, a0 = base[0], alt[0]
            if len(b0["_y"]) == len(a0["_y"]) and (b0["_y"] == a0["_y"]).all():
                d0 = rank_auc(b0["_y"], a0["_p"]) - rank_auc(b0["_y"], b0["_p"])
                lo, hi = paired_delta_ci(b0["_y"], b0["_p"], a0["_p"])
                rec["delta_seed0"] = round(float(d0), 4)
                rec["delta_seed0_lo"], rec["delta_seed0_hi"] = round(lo, 4), round(hi, 4)
                rec["excludes_zero"] = bool(lo > 0 or hi < 0)
                assert lo <= d0 <= hi, "paired delta outside its own interval"
            else:
                rec["paired"] = False
        rows.append(rec)
        print(rec, flush=True)
    return rows


if __name__ == "__main__":
    out = []
    for a in (sys.argv[1:] or ARCHIVES):
        if not loader.cache_path(a).exists():
            continue
        t0 = time.time()
        out += run(a)
        print("-- %s in %.0fs" % (a, time.time() - t0), flush=True)
        pd.DataFrame(out).to_csv("workspace/sybilbench/exp14_single_factor.csv", index=False)
    print("\n-> workspace/sybilbench/exp14_single_factor.csv")
