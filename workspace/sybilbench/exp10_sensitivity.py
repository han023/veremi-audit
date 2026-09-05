"""Experiment 10 - sensitivity of the result to the four knobs papers never report.

Reviewers can reasonably ask whether our conclusions survive a different operating
point. Each sweep moves one knob and holds the rest at the controlled setting
(observable aggregation, vehicle-disjoint split, no pseudonym feature).

    prevalence   0.5 % ... native            how much of the score is class balance
    jitter       0 ... 0.5 s                 the attacker's free escape from the clock
    sybils       identities per attacker     GridSybil holds 2-7, DoS families 100
    beacon       fraction of transmissions   a slower beacon starves every feature

TRIVIAL is median inter-arrival with an a-priori direction, no training. It is
plotted alongside because a learned detector that never separates from it has
demonstrated nothing about kinematics.
"""
from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/verify")
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.model_selection import GroupShuffleSplit  # noqa: E402

from sybilbench import analysis, loader  # noqa: E402
from exp9_cascade import KIN_FEATS, RATE_FEATS, identity_features  # noqa: E402
from v2_metrics import rank_auc, step_ap  # noqa: E402

SEEDS = [0, 1, 2]
DEFAULT_ARCHIVES = ["GridSybil_0709", "DoSRandomSybil_0709"]

PREVALENCES = [0.005, 0.01, 0.02, 0.03, 0.05, 0.10, 0.20, None]   # None = native
JITTERS = [0.0, 0.05, 0.10, 0.25, 0.50]
SYBIL_CAPS = [2, 3, 5, 10, 25, 50, 100, None]                     # None = uncapped
BEACON_KEEP = [1.0, 0.75, 0.5, 0.25, 0.10]


def cap_identities(ded, truth, cap, rng):
    """Keep at most `cap` identities per attacker, so attack intensity is a variable."""
    if cap is None:
        return ded
    by_sender = {}
    for tok in ded["token"].unique():
        s = truth.token_to_sender.get(tok)
        if s is None:
            continue
        by_sender.setdefault(s, []).append(tok)
    keep = set()
    for s, toks in by_sender.items():
        if truth.sender_to_attack.get(int(s), 0) != 0 and len(toks) > cap:
            toks = list(rng.choice(toks, cap, replace=False))
        keep.update(toks)
    return ded[ded["token"].isin(keep)]


def thin_beacons(ded, frac, rng):
    """Drop a fraction of transmissions uniformly: a slower effective beacon rate."""
    if frac >= 1.0:
        return ded
    m = rng.random(len(ded)) < frac
    return ded[m]


def subsample(y, target, rng):
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    keep = int(round(target * len(neg) / (1 - target)))
    if keep < 10 or keep >= len(pos):
        return None
    sel = np.concatenate([rng.choice(pos, keep, replace=False), neg])
    rng.shuffle(sel)
    return sel


def one_run(ded, truth, *, prevalence, jitter, cap, beacon, seed, drop_rate=False):
    rng = np.random.default_rng(seed)
    d = cap_identities(ded, truth, cap, rng)
    d = thin_beacons(d, beacon, rng)
    if len(d) < 5000:
        return None
    jr = np.random.default_rng(seed + 9000) if jitter > 0 else None
    if jr is not None:
        d = d.copy()
        d["rcvTime"] = d["rcvTime"].to_numpy() + jr.uniform(-jitter, jitter, len(d))
    X = identity_features(d, "token", None)
    if len(X) < 100:
        return None
    senders = np.array([truth.token_to_sender.get(t, -1) for t in X.index])
    y = np.array([1 if truth.sender_to_attack.get(int(s), 0) != 0 else 0 for s in senders])
    cols = ([] if drop_rate else RATE_FEATS) + KIN_FEATS
    F = X[cols].fillna(0.0)
    trivial = X["interval_med"].to_numpy()

    if prevalence is not None:
        sel = subsample(y, prevalence, rng)
        if sel is None:
            return None
        F, y, senders, trivial = F.iloc[sel], y[sel], senders[sel], trivial[sel]
    if y.sum() < 20 or (1 - y).sum() < 20:
        return None

    Z = F.to_numpy()
    tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=seed).split(Z, y, senders))
    assert not (set(senders[tr]) & set(senders[te]))
    if y[tr].sum() < 5 or y[te].sum() < 5:
        return None
    m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=seed)
    m.fit(Z[tr], y[tr])
    p = m.predict_proba(Z[te])[:, 1]
    return {"auc": rank_auc(y[te], p), "ap": step_ap(y[te], p),
            "trivial_auc": rank_auc(y[te], trivial[te]),
            "trivial_ap": step_ap(y[te], trivial[te]),
            "n_test": len(te), "prevalence_obs": float(y[te].mean()),
            "identities": len(X)}


def sweep(archive, name, settings, base, rows):
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    for val in settings:
        kw = dict(base)
        kw[name] = val
        res = [one_run(ded, truth, seed=s, **kw) for s in SEEDS]
        res = [r for r in res if r]
        if not res:
            print({"archive": archive, "sweep": name + ("" if kw["prevalence"] is not None else "_native"), "value": val, "note": "degenerate"}, flush=True)
            continue
        agg = {
            "archive": archive, "sweep": name + ("" if kw["prevalence"] is not None else "_native"), "value": "native" if val is None else val,
            "auc": round(float(np.mean([r["auc"] for r in res])), 4),
            "auc_sd": round(float(np.std([r["auc"] for r in res], ddof=1)), 4) if len(res) > 1 else 0.0,
            "ap": round(float(np.mean([r["ap"] for r in res])), 4),
            "trivial_auc": round(float(np.mean([r["trivial_auc"] for r in res])), 4),
            "trivial_ap": round(float(np.mean([r["trivial_ap"] for r in res])), 4),
            "prevalence_obs": round(float(np.mean([r["prevalence_obs"] for r in res])), 4),
            "identities": int(np.mean([r["identities"] for r in res])),
            "n_test": int(np.mean([r["n_test"] for r in res])),
            "seeds": len(res),
        }
        agg["ml_minus_trivial"] = round(agg["auc"] - agg["trivial_auc"], 4)
        rows.append(agg)
        print(agg, flush=True)


if __name__ == "__main__":
    archives = [a for a in sys.argv[1:] if not a.startswith("-")] or DEFAULT_ARCHIVES
    base = dict(prevalence=0.03, jitter=0.0, cap=None, beacon=1.0, drop_rate=False)
    rows = []
    for a in archives:
        if not loader.cache_path(a).exists():
            print("skip " + a, flush=True)
            continue
        t0 = time.time()
        sweep(a, "prevalence", PREVALENCES, base, rows)
        sweep(a, "jitter", JITTERS, base, rows)
        sweep(a, "cap", SYBIL_CAPS, base, rows)
        sweep(a, "beacon", BEACON_KEEP, base, rows)
        # Below 3 % prevalence a disjoint test fold holds fewer than five attacker
        # vehicles, so those sweeps are unusable noise. Repeat the two knobs that
        # matter at native prevalence, where the estimate is stable.
        wide = dict(base, prevalence=None)
        sweep(a, "jitter", JITTERS, wide, rows)
        sweep(a, "cap", SYBIL_CAPS, wide, rows)
        sweep(a, "beacon", BEACON_KEEP, wide, rows)
        print("-- {} done in {:.0f}s".format(a, time.time() - t0), flush=True)
        pd.DataFrame(rows).to_csv("workspace/sybilbench/exp10_sensitivity.csv", index=False)
    print("\nEXP10 DONE -> workspace/sybilbench/exp10_sensitivity.csv")
