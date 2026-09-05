"""
Experiment 1 — can two identities be linked to one physical vehicle from kinematics alone?

This is the primitive behind both halves of the linkability dilemma:
  * link an attacker's concurrent identities  -> Sybil detection
  * link an honest driver's successive identities -> tracking

The model never sees `sender` or the raw pseudonym. Splits are vehicle-disjoint (grouped on the true vehicle,
which is used for *splitting and scoring only*), so a vehicle cannot appear in both train and test.
"""
from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit

sys.path.insert(0, "workspace")
from sybilbench import analysis, loader  # noqa: E402

ARCHIVES = [
    "GridSybil_0709", "GridSybil_1416",
    "DataReplaySybil_0709", "DataReplaySybil_1416",
    "DoSRandomSybil_0709", "DoSRandomSybil_1416",
    "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416",
]
FEATS = ["overlap", "n_cmp", "dist_mean", "dist_min", "dist_std",
         "spd_diff_mean", "spd_corr", "dt_median", "phase"]

# Ablation. `phase`/`dt_median`/`overlap`/`n_cmp` describe *when* messages arrive. If ghosts inherit their
# attacker's transmission clock (a simulator artefact rather than a property of real attacks), timing alone
# can carry the result. GEOM keeps only claimed-trajectory geometry, which is what a real detector must use.
GEOM = ["dist_mean", "dist_min", "dist_std", "spd_diff_mean", "spd_corr"]
TIMING = ["overlap", "n_cmp", "dt_median", "phase"]
FEATURE_SETS = {"all": FEATS, "geometry_only": GEOM, "timing_only": TIMING}


def run(archive: str, max_pairs: int = 40_000, seed: int = 0) -> dict | None:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    # One row per transmission. Without this, a token's rows are duplicated once per receiver and every
    # timing feature is meaningless (see analysis.transmissions).
    view = analysis.transmissions(view)

    cands = analysis.pair_candidates(view, max_pairs=max_pairs, seed=seed)
    if cands.empty:
        return None
    feats = analysis.pair_features(view, cands)
    if feats.empty:
        return None

    y = analysis.label_pairs(feats, truth).to_numpy()
    if y.sum() < 20 or (1 - y).sum() < 20:
        return {"archive": archive, "note": f"degenerate labels pos={int(y.sum())} neg={int((1-y).sum())}"}

    # Strict vehicle-disjoint split: split *vehicles* first, then keep only pairs whose BOTH endpoints fall
    # on the same side. Grouping on one endpoint alone lets the other endpoint's vehicle straddle the split.
    sa = feats["a"].map(truth.token_to_sender)
    sb = feats["b"].map(truth.token_to_sender)
    vehicles = pd.unique(pd.concat([sa, sb]).dropna())
    rng = np.random.default_rng(seed)
    test_v = set(rng.choice(vehicles, max(1, int(0.3 * len(vehicles))), replace=False).tolist())
    in_test = sa.isin(test_v) & sb.isin(test_v)
    in_train = (~sa.isin(test_v)) & (~sb.isin(test_v))
    tr = np.flatnonzero(in_train.to_numpy())
    te = np.flatnonzero(in_test.to_numpy())
    if len(te) < 50 or y[te].sum() < 5 or y[tr].sum() < 5:
        return {"archive": archive, "note": f"split too small (train={len(tr)} test={len(te)} pos_te={int(y[te].sum())})"}

    res = {"archive": archive, "pairs": len(feats), "positive_rate": float(y.mean())}
    for name, cols in FEATURE_SETS.items():
        X = feats[cols].fillna(0).to_numpy()
        m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=seed)
        m.fit(X[tr], y[tr])
        p = m.predict_proba(X[te])[:, 1]
        res[f"auc_{name}"] = round(float(roc_auc_score(y[te], p)), 4)
        res[f"ap_{name}"] = round(float(average_precision_score(y[te], p)), 4)
        if name == "all":
            res["top_features"] = "; ".join(
                f"{k}={v:.2f}" for k, v in sorted(zip(cols, m.feature_importances_), key=lambda kv: -kv[1])[:4]
            )
    return res


if __name__ == "__main__":
    out = []
    for a in ARCHIVES:
        if not loader.cache_path(a).exists():
            print(f"skip {a} (not cached)", flush=True)
            continue
        t0 = time.time()
        try:
            r = run(a)
        except Exception as e:  # keep going; report at the end
            r = {"archive": a, "note": f"{type(e).__name__}: {e}"}
        if r is None:
            r = {"archive": a, "note": "no candidate pairs"}
        r["secs"] = round(time.time() - t0, 1)
        out.append(r)
        print(r, flush=True)
    pd.DataFrame(out).to_csv("workspace/sybilbench/exp1_results.csv", index=False)
    print("\nEXP1 DONE -> workspace/sybilbench/exp1_results.csv", flush=True)
