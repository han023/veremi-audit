"""
Experiment 4 — replication of Findings 11-13 at a second traffic density.

Everything so far was measured on GridSybil_1416 (the denser window). A result that does not survive a change
of density is a property of one simulation run, not of the problem. This script re-runs the three load-bearing
measurements under the final protocol:

  A. Pareto over pseudonym lifetime tau     (Finding 11)
  B. evidence-per-identity control          (Finding 12)
  C. evidence-matched silence period        (Finding 13)

Protocol (unchanged, so numbers are comparable):
  * transmissions deduplicated on messageID
  * benign cohort fixed to vehicles that re-key at every tau
  * tracking: parameter-free (`miss`, direction fixed a priori), gap-matched negatives
  * detection: single a-priori feature (`spd_corr`) for cross-policy comparability, concurrency required
  * multiple seeds, mean +/- sd
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, "workspace")
from sybilbench import analysis, loader, pseudonym_layer as P  # noqa: E402

SEEDS = [0, 1, 2]
MIN_DURATION = 130.0


def _tracking(v2, t2, seed, keep_senders=None, max_gap=90):
    pr = P.sequential_pairs(v2, t2, max_gap_s=max_gap, max_pairs=30_000, seed=seed)
    if pr.empty:
        return np.nan, 0
    if keep_senders is not None:
        sa = pr["a"].map(t2.token_to_sender)
        sb = pr["b"].map(t2.token_to_sender)
        pr = pr[sa.isin(keep_senders) & sb.isin(keep_senders)]
        if pr.empty:
            return np.nan, 0
    y = P.label_same_vehicle(pr, t2)
    pm, ym = P.gap_matched(pr, y, n_neg_per_pos=20, seed=seed)
    if ym.sum() < 20 or ym.nunique() < 2:
        return np.nan, int(ym.sum())
    return float(roc_auc_score(ym, -pm["miss"].fillna(1e9))), int(ym.sum())


def _detection(v2, t2, seed):
    cd = analysis.pair_candidates(v2, max_pairs=20_000, seed=seed)
    if cd.empty:
        return np.nan, 0
    cd = cd[cd["overlap"] > 0]
    if cd.empty:
        return np.nan, 0
    ft = analysis.pair_features(v2, cd)
    if ft.empty:
        return np.nan, 0
    y = analysis.label_pairs(ft, t2)
    if y.sum() < 20 or y.nunique() < 2:
        return np.nan, int(y.sum())
    return float(roc_auc_score(y, ft["spd_corr"].fillna(0))), int(y.sum())


def _agg(vals):
    return (round(float(np.mean(vals)), 4), round(float(np.std(vals)), 4)) if vals else (np.nan, np.nan)


def run(archive: str):
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)

    dur = ded.groupby("token", observed=True)["rcvTime"].agg(lambda t: t.max() - t.min())
    cohort = {truth.token_to_sender[t] for t, d in dur.items()
              if d >= MIN_DURATION and t in truth.token_to_sender
              and truth.sender_to_attack.get(truth.token_to_sender[t], 0) == 0}
    print(f"\n### {archive} | cohort = {len(cohort)} benign vehicles (>= {MIN_DURATION:.0f}s)", flush=True)

    print("\nA. Pareto over pseudonym lifetime")
    rows_a = []
    for tau in [15, 30, 60, 120]:
        T, D, nt, nd = [], [], [], []
        for s in SEEDS:
            v2, t2 = P.apply_pseudonym_change(ded, truth, tau, benign_only=False)
            a, n = _tracking(v2, t2, s, cohort)
            if not np.isnan(a):
                T.append(a); nt.append(n)
            b, m = _detection(v2, t2, s)
            if not np.isnan(b):
                D.append(b); nd.append(m)
        tm, ts = _agg(T); dm, dsd = _agg(D)
        rows_a.append({"archive": archive, "tau_s": tau, "tracking_auc": tm, "tracking_sd": ts,
                       "tracking_pos": int(np.mean(nt)) if nt else 0,
                       "detection_auc": dm, "detection_sd": dsd,
                       "detection_pos": int(np.mean(nd)) if nd else 0})
        print("  ", rows_a[-1], flush=True)

    print("\nB. evidence control (tau fixed at 30 s, identities truncated to N messages)")
    rows_b = []
    v30, t30 = P.apply_pseudonym_change(ded, truth, 30, benign_only=False)
    for N in [5, 10, 20, 40]:
        vt = v30.sort_values("rcvTime").groupby("token", observed=True, group_keys=False).head(N)
        a, na = _tracking(vt, t30, 0)
        b, nb = _detection(vt, t30, 0)
        rows_b.append({"archive": archive, "n_msgs": N, "tracking_auc": round(a, 4), "detection_auc": round(b, 4)})
        print("  ", rows_b[-1], flush=True)

    print("\nC. evidence-matched silence (tau_eff = 30 + S)")
    rows_c = []
    for S in [0, 20]:
        T, D = [], []
        for s in SEEDS + [3, 4]:
            v2, t2 = P.apply_silent_period(ded, truth, 30 + S, S, benign_only=False)
            a, _ = _tracking(v2, t2, s, max_gap=120)
            b, _ = _detection(v2, t2, s)
            if not np.isnan(a):
                T.append(a)
            if not np.isnan(b):
                D.append(b)
        tm, ts = _agg(T); dm, dsd = _agg(D)
        rows_c.append({"archive": archive, "silence_s": S, "tracking_auc": tm, "tracking_sd": ts,
                       "detection_auc": dm, "detection_sd": dsd})
        print("  ", rows_c[-1], flush=True)
    if len(rows_c) == 2:
        print(f"   -> delta tracking {rows_c[1]['tracking_auc'] - rows_c[0]['tracking_auc']:+.4f}"
              f" | delta detection {rows_c[1]['detection_auc'] - rows_c[0]['detection_auc']:+.4f}", flush=True)

    return pd.DataFrame(rows_a), pd.DataFrame(rows_b), pd.DataFrame(rows_c)


if __name__ == "__main__":
    archives = sys.argv[1:] or ["GridSybil_0709"]
    A, B, C = [], [], []
    for a in archives:
        x, y, z = run(a)
        A.append(x); B.append(y); C.append(z)
    pd.concat(A).to_csv("workspace/sybilbench/exp4_pareto.csv", index=False)
    pd.concat(B).to_csv("workspace/sybilbench/exp4_evidence.csv", index=False)
    pd.concat(C).to_csv("workspace/sybilbench/exp4_silence.csv", index=False)
    print("\nEXP4 DONE")
