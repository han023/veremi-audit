"""
Experiment 2 — the linkability dilemma, measured.

Sweep pseudonym lifetime tau and score the *same* kinematic-linkage inference twice on the same traces:

    privacy loss   : can an observer link an honest vehicle's successive pseudonyms?   (tracking)
    security gain  : can an observer link an attacker's concurrent identities?         (Sybil detection)

Both use dead-reckoning geometry only — no timing features, because Findings 9/10 show timing is a benchmark
artefact that a real attacker removes for free.

Controls carried over from the self-audit:
  * transmissions deduplicated on messageID (a BSM is logged once per receiver)
  * negatives gap-matched to positives (otherwise "tracking" partly measures *when* an identity reappeared)
  * multiple seeds, mean +/- sd reported
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, "workspace")
from sybilbench import analysis, loader, pseudonym_layer as P  # noqa: E402

TAUS = [15, 30, 60, 120]
SEEDS = [0, 1, 2]
GEOM_CONCURRENT = ["dist_mean", "dist_min", "dist_std", "spd_diff_mean", "spd_corr"]


def tracking_auc(ded, truth, tau: int, seed: int, everyone: bool) -> tuple[float, int]:
    """Privacy loss: AUC for linking an honest vehicle's successive pseudonyms."""
    v2, t2 = P.apply_pseudonym_change(ded, truth, tau, benign_only=not everyone)
    pairs = P.sequential_pairs(v2, t2, max_gap_s=90, max_pairs=30_000, seed=seed)
    if pairs.empty:
        return np.nan, 0
    # honest vehicles only: tracking is about drivers, not attackers
    benign = pairs["a"].map(t2.token_to_sender).map(
        lambda s: t2.sender_to_attack.get(s, 0) == 0 if pd.notna(s) else False
    )
    pairs = pairs[benign]
    if pairs.empty:
        return np.nan, 0
    y = P.label_same_vehicle(pairs, t2)
    pm, ym = P.gap_matched(pairs, y, n_neg_per_pos=20, seed=seed)
    if ym.sum() < 20 or ym.nunique() < 2:
        return np.nan, int(ym.sum())
    return float(max(roc_auc_score(ym, pm["miss"].fillna(1e9)),
                     1 - roc_auc_score(ym, pm["miss"].fillna(1e9)))), int(ym.sum())


def detection_auc(ded, truth, tau: int, seed: int, everyone: bool) -> tuple[float, int]:
    """Security gain: AUC for linking an attacker's concurrent identities, geometry only."""
    v2, t2 = P.apply_pseudonym_change(ded, truth, tau, benign_only=not everyone)
    cands = analysis.pair_candidates(v2, max_pairs=25_000, seed=seed)
    if cands.empty:
        return np.nan, 0
    feats = analysis.pair_features(v2, cands)
    if feats.empty:
        return np.nan, 0
    y = analysis.label_same_vehicle_pairs(feats, t2) if hasattr(analysis, "label_same_vehicle_pairs") \
        else analysis.label_pairs(feats, t2)
    if y.sum() < 20 or y.nunique() < 2:
        return np.nan, int(y.sum())
    # single-feature score keeps this comparable to the tracking side (no model, no fitting)
    best = 0.5
    for c in GEOM_CONCURRENT:
        v = feats[c].fillna(0)
        try:
            a = roc_auc_score(y, v)
        except ValueError:
            continue
        best = max(best, a, 1 - a)
    return float(best), int(y.sum())


def run(archive: str) -> pd.DataFrame:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)

    rows = []
    for everyone in (False, True):
        for tau in TAUS:
            tr, trn = [], []
            de, den = [], []
            for s in SEEDS:
                a, n = tracking_auc(ded, truth, tau, s, everyone)
                if not np.isnan(a):
                    tr.append(a); trn.append(n)
                b, m = detection_auc(ded, truth, tau, s, everyone)
                if not np.isnan(b):
                    de.append(b); den.append(m)
            rows.append({
                "archive": archive,
                "policy": "all vehicles re-key" if everyone else "benign re-key only",
                "tau_s": tau,
                "tracking_auc": round(float(np.mean(tr)), 4) if tr else np.nan,
                "tracking_sd": round(float(np.std(tr)), 4) if tr else np.nan,
                "tracking_pos": int(np.mean(trn)) if trn else 0,
                "detection_auc": round(float(np.mean(de)), 4) if de else np.nan,
                "detection_sd": round(float(np.std(de)), 4) if de else np.nan,
                "detection_pos": int(np.mean(den)) if den else 0,
            })
            print(rows[-1], flush=True)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    archives = sys.argv[1:] or ["GridSybil_1416", "GridSybil_0709"]
    out = pd.concat([run(a) for a in archives], ignore_index=True)
    out.to_csv("workspace/sybilbench/exp2_pareto.csv", index=False)
    print("\nEXP2 DONE -> workspace/sybilbench/exp2_pareto.csv")
    print(out.to_string(index=False))
