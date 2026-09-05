"""
Experiment 2b — the linkability dilemma, with three controls the first version lacked.

Self-audit of exp2 found three ways the result could have been an artefact:

  C1  Population drift. At tau = 120 s only 36 % of benign vehicles re-key at all, and those that do are 47 %
      longer-lived than the ones re-keying at tau = 15 s (median 148.5 s vs 101 s). Longer-lived vehicles are
      easier to track, so the apparent "shorter tau protects privacy" trend could be pure composition.
      Control: a FIXED COHORT of vehicles long enough to re-key at every tau tested.

  C2  Test-set feature selection. exp2 reported max over five features and both directions, chosen on the
      same data it scored. Control: ONE feature per head, direction fixed a priori.
          tracking  -> `miss`     (dead-reckoning error; smaller = same vehicle)
          detection -> `spd_corr` (rigidly co-moving ghosts; larger = same attacker)

  C3  Sequential pairs leaking into the detection head. Under "all vehicles re-key" an attacker's own ghost is
      re-keyed too, so a ghost's consecutive epochs form a *sequential* positive pair — a tracking signal
      scored as detection. Control: detection pairs must genuinely OVERLAP in time.
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
MIN_DURATION = 130.0  # > max(TAUS), so every cohort vehicle re-keys at every tau


def cohort_tokens(ded: pd.DataFrame, truth, min_duration: float) -> set[str]:
    """Benign vehicles present long enough to re-key at every tau (fixes C1)."""
    dur = ded.groupby("token", observed=True)["rcvTime"].agg(lambda t: t.max() - t.min())
    out = set()
    for tok, d in dur.items():
        s = truth.token_to_sender.get(tok)
        if s is None or truth.sender_to_attack.get(s, 0) != 0:
            continue
        if d >= min_duration:
            out.add(tok)
    return out


def tracking_auc(ded, truth, tau, seed, cohort):
    v2, t2 = P.apply_pseudonym_change(ded, truth, tau, benign_only=False)
    # keep only re-keyed identities descended from the fixed cohort
    orig = ded[["token"]].copy()
    keep_senders = {truth.token_to_sender[t] for t in cohort if t in truth.token_to_sender}
    pairs = P.sequential_pairs(v2, t2, max_gap_s=90, max_pairs=30_000, seed=seed)
    if pairs.empty:
        return np.nan, 0
    sa = pairs["a"].map(t2.token_to_sender)
    sb = pairs["b"].map(t2.token_to_sender)
    keep = sa.isin(keep_senders) & sb.isin(keep_senders)
    pairs = pairs[keep]
    if pairs.empty:
        return np.nan, 0
    y = P.label_same_vehicle(pairs, t2)
    pm, ym = P.gap_matched(pairs, y, n_neg_per_pos=20, seed=seed)
    if ym.sum() < 20 or ym.nunique() < 2:
        return np.nan, int(ym.sum())
    # C2: fixed feature, fixed direction (smaller miss => same vehicle)
    return float(roc_auc_score(ym, -pm["miss"].fillna(1e9))), int(ym.sum())


def detection_auc(ded, truth, tau, seed):
    v2, t2 = P.apply_pseudonym_change(ded, truth, tau, benign_only=False)
    cands = analysis.pair_candidates(v2, max_pairs=25_000, seed=seed)
    if cands.empty:
        return np.nan, 0
    cands = cands[cands["overlap"] > 0]  # C3: concurrency, not succession
    if cands.empty:
        return np.nan, 0
    feats = analysis.pair_features(v2, cands)
    if feats.empty:
        return np.nan, 0
    y = analysis.label_pairs(feats, t2)
    if y.sum() < 20 or y.nunique() < 2:
        return np.nan, int(y.sum())
    # C2: fixed feature, fixed direction (rigid co-movement => same attacker)
    return float(roc_auc_score(y, feats["spd_corr"].fillna(0))), int(y.sum())


def run(archive: str) -> pd.DataFrame:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    cohort = cohort_tokens(ded, truth, MIN_DURATION)
    print(f"{archive}: fixed cohort = {len(cohort)} benign vehicles with duration >= {MIN_DURATION:.0f}s",
          flush=True)

    rows = []
    for tau in TAUS:
        tr, trn, de, den = [], [], [], []
        for s in SEEDS:
            a, n = tracking_auc(ded, truth, tau, s, cohort)
            if not np.isnan(a):
                tr.append(a); trn.append(n)
            b, m = detection_auc(ded, truth, tau, s)
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
    out.to_csv("workspace/sybilbench/exp2b_pareto_controlled.csv", index=False)
    print("\nEXP2b DONE")
    print(out.to_string(index=False))
