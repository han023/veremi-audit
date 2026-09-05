"""
Experiment 2c — the linkability dilemma, final protocol.

exp2  : uncontrolled. Population drifted with tau; detection used best-of-five features picked on test data.
exp2b : fixed cohort + a-priori single features + concurrency filter. Fixed the bias, but then compared a
        *trained* tracking attack against a *single-feature* detector — unfair to detection (0.67 vs exp1's
        0.97 with a trained model).

exp2c makes both sides symmetric and honest:

  * fixed cohort of benign vehicles long enough to re-key at every tau      (no population drift)
  * BOTH heads use a trained model with vehicle-disjoint train/test splits  (no test-set selection, fair)
  * detection pairs must overlap in time; tracking pairs are gap-matched    (no succession/timing shortcuts)
  * geometry features only                                                  (timing is a benchmark artefact)
  * 3 seeds, mean +/- sd
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, "workspace")
from sybilbench import analysis, loader, pseudonym_layer as P  # noqa: E402

TAUS = [15, 30, 60, 120]
SEEDS = [0, 1, 2]
MIN_DURATION = 130.0
TRACK_FEATS = ["miss", "jump", "implied_speed", "spd_diff"]          # geometry of a dead-reckoned gap
DETECT_FEATS = ["dist_mean", "dist_min", "dist_std", "spd_diff_mean", "spd_corr"]  # geometry of co-presence


def _split_by_vehicle(sa: pd.Series, sb: pd.Series, seed: int):
    """Vehicle-disjoint split: both endpoints of a pair must fall on the same side."""
    vehicles = pd.unique(pd.concat([sa, sb]).dropna())
    rng = np.random.default_rng(seed)
    test_v = set(rng.choice(vehicles, max(1, int(0.3 * len(vehicles))), replace=False).tolist())
    te = (sa.isin(test_v) & sb.isin(test_v)).to_numpy()
    tr = ((~sa.isin(test_v)) & (~sb.isin(test_v))).to_numpy()
    return np.flatnonzero(tr), np.flatnonzero(te)


def _fit_score(X, y, tr, te, seed):
    if len(te) < 40 or y[te].sum() < 5 or y[tr].sum() < 5:
        return np.nan
    m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=seed)
    m.fit(X[tr], y[tr])
    return float(roc_auc_score(y[te], m.predict_proba(X[te])[:, 1]))


def cohort_senders(ded, truth, min_duration):
    dur = ded.groupby("token", observed=True)["rcvTime"].agg(lambda t: t.max() - t.min())
    out = set()
    for tok, d in dur.items():
        s = truth.token_to_sender.get(tok)
        if s is not None and truth.sender_to_attack.get(s, 0) == 0 and d >= min_duration:
            out.add(s)
    return out


def tracking(ded, truth, tau, seed, keep_senders):
    v2, t2 = P.apply_pseudonym_change(ded, truth, tau, benign_only=False)
    pairs = P.sequential_pairs(v2, t2, max_gap_s=90, max_pairs=30_000, seed=seed)
    if pairs.empty:
        return np.nan, 0
    sa = pairs["a"].map(t2.token_to_sender)
    sb = pairs["b"].map(t2.token_to_sender)
    keep = sa.isin(keep_senders) & sb.isin(keep_senders)
    pairs, sa, sb = pairs[keep], sa[keep], sb[keep]
    if pairs.empty:
        return np.nan, 0
    y = P.label_same_vehicle(pairs, t2)
    pm, ym = P.gap_matched(pairs, y, n_neg_per_pos=20, seed=seed)
    if ym.sum() < 20:
        return np.nan, int(ym.sum())
    tr, te = _split_by_vehicle(sa.loc[pm.index], sb.loc[pm.index], seed)
    return _fit_score(pm[TRACK_FEATS].fillna(0).to_numpy(), ym.to_numpy(), tr, te, seed), int(ym.sum())


def detection(ded, truth, tau, seed):
    v2, t2 = P.apply_pseudonym_change(ded, truth, tau, benign_only=False)
    cands = analysis.pair_candidates(v2, max_pairs=25_000, seed=seed)
    if cands.empty:
        return np.nan, 0
    cands = cands[cands["overlap"] > 0]
    if cands.empty:
        return np.nan, 0
    feats = analysis.pair_features(v2, cands)
    if feats.empty:
        return np.nan, 0
    y = analysis.label_pairs(feats, t2)
    if y.sum() < 20:
        return np.nan, int(y.sum())
    sa = feats["a"].map(t2.token_to_sender)
    sb = feats["b"].map(t2.token_to_sender)
    tr, te = _split_by_vehicle(sa, sb, seed)
    return _fit_score(feats[DETECT_FEATS].fillna(0).to_numpy(), y.to_numpy(), tr, te, seed), int(y.sum())


def run(archive: str) -> pd.DataFrame:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    keep = cohort_senders(ded, truth, MIN_DURATION)
    print(f"{archive}: cohort = {len(keep)} benign vehicles (duration >= {MIN_DURATION:.0f}s)", flush=True)

    rows = []
    for tau in TAUS:
        tr, trn, de, den = [], [], [], []
        for s in SEEDS:
            a, n = tracking(ded, truth, tau, s, keep)
            if not np.isnan(a):
                tr.append(a); trn.append(n)
            b, m = detection(ded, truth, tau, s)
            if not np.isnan(b):
                de.append(b); den.append(m)
        rows.append({
            "archive": archive, "tau_s": tau,
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
    archives = sys.argv[1:] or ["GridSybil_1416"]
    out = pd.concat([run(a) for a in archives], ignore_index=True)
    out.to_csv("workspace/sybilbench/exp2c_pareto_final.csv", index=False)
    print("\nEXP2c DONE")
    print(out.to_string(index=False))
