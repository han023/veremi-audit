"""Experiment 9 - the staged benchmark audit.

One pipeline, one detector, seven protocols. Each stage removes exactly one
advantage that the published-style protocol enjoys, so the drop attributable to
each advantage is read off directly.

    S0  published style   ground-truth aggregation, real pseudonym as a feature,
                          random k-fold, native ~30 % prevalence, all features
    S1  - pseudonym       the identifier is no longer offered as a feature
    S2  - GT aggregation  identities are grouped by what a receiver sees, not by
                          the true vehicle: the partition must now be inferred
    S3  + disjoint split  no vehicle appears in both train and test
    S4  + realistic rate  attacker prevalence subsampled to 3 %
    S5  + jitter          transmission times perturbed by U(-0.25, 0.25) s
    S6  - rate features   message count, duration and inter-arrival dropped

Alongside every stage we score TRIVIAL: median inter-arrival alone, no training,
direction fixed a priori. A detector that cannot beat that line has shown nothing.

Metrics come from workspace/verify/v2_metrics.py (no sklearn) and are also
recomputed with sklearn; the run aborts if the two ever disagree.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, "workspace")
sys.path.insert(0, "workspace/verify")
from sybilbench import analysis, loader  # noqa: E402
from v2_metrics import bootstrap_ci, rank_auc, step_ap  # noqa: E402

ARCHIVES = ["GridSybil_0709", "GridSybil_1416",
            "DataReplaySybil_0709", "DataReplaySybil_1416",
            "DoSRandomSybil_0709", "DoSRandomSybil_1416",
            "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416"]
SEEDS = [0, 1, 2, 3, 4]
JITTER = 0.25          # seconds, uniform either side; a beacon period is 1.0 s
TARGET_PREV = 0.03

# The paper proposes this cascade as a check others can run, so the detector is a
# parameter rather than a constant. The default is the forest every published number
# in this work used; --model swaps it without touching anything else.
MODELS = {
    "forest": lambda seed: RandomForestClassifier(
        n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=seed),
    "boost": lambda seed: GradientBoostingClassifier(random_state=seed),
    "tree": lambda seed: DecisionTreeClassifier(min_samples_leaf=2, random_state=seed),
    "logistic": lambda seed: make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed)),
}


def _selected_model() -> str:
    for arg in sys.argv[1:]:
        if arg.startswith("--model="):
            name = arg.split("=", 1)[1]
            if name not in MODELS:
                raise SystemExit("unknown model %r; choose from %s"
                                 % (name, ", ".join(sorted(MODELS))))
            return name
    return "forest"


MODEL = _selected_model()

RATE_FEATS = ["n_msgs", "duration", "interval_med", "interval_std"]
KIN_FEATS = ["spd_mean", "spd_std", "spd_max", "acl_mean", "acl_std",
             "pos_x_span", "pos_y_span", "step_mean", "step_std",
             "kin_resid_mean", "posnoise", "hednoise"]

# stage -> (aggregate on ground truth?, pseudonym feature?, disjoint split?,
#           subsample prevalence?, jitter?, keep rate features?)
STAGES = {
    "S0_published":     dict(gt_agg=True,  pseudo=True,  disjoint=False, prev=False, jitter=False, rate=True),
    "S1_no_pseudonym":  dict(gt_agg=True,  pseudo=False, disjoint=False, prev=False, jitter=False, rate=True),
    "S2_no_gt_agg":     dict(gt_agg=False, pseudo=False, disjoint=False, prev=False, jitter=False, rate=True),
    "S3_disjoint":      dict(gt_agg=False, pseudo=False, disjoint=True,  prev=False, jitter=False, rate=True),
    "S4_prevalence_3":  dict(gt_agg=False, pseudo=False, disjoint=True,  prev=True,  jitter=False, rate=True),
    "S5_jitter":        dict(gt_agg=False, pseudo=False, disjoint=True,  prev=True,  jitter=True,  rate=True),
    "S6_no_rate":       dict(gt_agg=False, pseudo=False, disjoint=True,  prev=True,  jitter=True,  rate=False),
}


def out_path(targets) -> str:
    """Name the output after the run, not after the experiment.

    A partial run, or a run with a different model, must not overwrite the file
    that backs the published table. That happened once; the filename now carries
    both the model and whether the run covered every archive.
    """
    base = "workspace/sybilbench/exp9_cascade"
    if MODEL != "forest":
        base += "_" + MODEL
    if set(targets) != set(ARCHIVES):
        base += "_partial"
    return base + ".csv"


def load_pseudomap(archive: str) -> dict[str, int]:
    p = Path("workspace/sybilbench/cache") / f"{archive}.pseudomap.json"
    if not p.exists():
        raise FileNotFoundError(str(p) + " - run workspace/verify/v3_pseudomap.py first")
    with open(p, encoding="utf-8") as f:
        return {k: int(v) for k, v in json.load(f)["token_to_pseudo"].items()}


def identity_features(ded: pd.DataFrame, key: str, jitter_rng) -> pd.DataFrame:
    """One row per identity. `ded` is already one row per transmission."""
    d = ded
    if jitter_rng is not None:
        d = d.copy()
        d["rcvTime"] = d["rcvTime"].to_numpy() + jitter_rng.uniform(-JITTER, JITTER, len(d))
    d = d.sort_values("rcvTime")
    spd = np.hypot(d["spd_x"].to_numpy(), d["spd_y"].to_numpy())
    acl = np.hypot(d["acl_x"].to_numpy(), d["acl_y"].to_numpy())
    d = d.assign(_spd=spd, _acl=acl)

    rows = []
    for k, g in d.groupby(key, observed=True, sort=False):
        t = g["rcvTime"].to_numpy()
        if len(t) < 2:
            continue
        dt = np.diff(t)
        x, y = g["pos_x"].to_numpy(), g["pos_y"].to_numpy()
        step = np.hypot(np.diff(x), np.diff(y))
        with np.errstate(divide="ignore", invalid="ignore"):
            implied = np.where(dt > 0, step / dt, np.nan)
        resid = np.abs(implied - g["_spd"].to_numpy()[1:])
        rows.append({
            key: k,
            "n_msgs": len(t), "duration": float(t[-1] - t[0]),
            "interval_med": float(np.median(dt)), "interval_std": float(np.std(dt)),
            "spd_mean": float(g["_spd"].mean()), "spd_std": float(g["_spd"].std()),
            "spd_max": float(g["_spd"].max()),
            "acl_mean": float(g["_acl"].mean()), "acl_std": float(g["_acl"].std()),
            "pos_x_span": float(x.max() - x.min()), "pos_y_span": float(y.max() - y.min()),
            "step_mean": float(np.nanmean(step)) if len(step) else np.nan,
            "step_std": float(np.nanstd(step)) if len(step) else np.nan,
            "kin_resid_mean": float(np.nanmean(resid)) if len(resid) else np.nan,
            "posnoise": float(np.hypot(g["pos_noise_x"], g["pos_noise_y"]).mean()),
            "hednoise": float(np.hypot(g["hed_noise_x"], g["hed_noise_y"]).mean()),
        })
    return pd.DataFrame(rows).set_index(key)


def subsample(y: np.ndarray, target: float, rng) -> np.ndarray:
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    keep = int(round(target * len(neg) / (1 - target)))
    if keep < 10 or keep >= len(pos):
        return np.arange(len(y))
    sel = np.concatenate([rng.choice(pos, keep, replace=False), neg])
    rng.shuffle(sel)
    return sel


def agree(y, p):
    """Score with the independent implementation, then confirm sklearn agrees."""
    a, ap = rank_auc(y, p), step_ap(y, p)
    a2, ap2 = roc_auc_score(y, p), average_precision_score(y, p)
    assert abs(a - a2) < 1e-9 and abs(ap - ap2) < 1e-9, "metric mismatch"
    return a, ap


def run_stage(ded, truth, pseudomap, cfg, seed):
    rng = np.random.default_rng(seed)
    jr = np.random.default_rng(seed + 9000) if cfg["jitter"] else None

    if cfg["gt_agg"]:
        d = ded.assign(sender=ded["token"].map(truth.token_to_sender))
        d = d[d["sender"].notna()]
        X = identity_features(d, "sender", jr)
        senders = pd.Series(X.index.astype(int), index=X.index)
        # the real leak: the pseudonym exactly as it appears in the archive
        first_tok = d.groupby("sender", observed=True)["token"].first()
        pseudo = first_tok.map(pseudomap).reindex(X.index)
    else:
        X = identity_features(ded, "token", jr)
        senders = pd.Series([truth.token_to_sender.get(t, -1) for t in X.index], index=X.index)
        pseudo = pd.Series([pseudomap.get(t, np.nan) for t in X.index], index=X.index)

    y = np.array([1 if truth.sender_to_attack.get(int(s), 0) != 0 else 0 for s in senders])
    cols = (RATE_FEATS if cfg["rate"] else []) + KIN_FEATS
    F = X[cols].copy()
    if cfg["pseudo"]:
        F["pseudo_id"] = pseudo.to_numpy()
    F = F.fillna(0.0)

    trivial_raw = X["interval_med"].to_numpy()      # a-priori: slower identity => ghost
    g = senders.to_numpy()

    if cfg["prev"]:
        sel = subsample(y, TARGET_PREV, rng)
        F, y, g, trivial_raw = F.iloc[sel], y[sel], g[sel], trivial_raw[sel]
    if y.sum() < 20 or (1 - y).sum() < 20:
        return None
    Z = F.to_numpy()

    if cfg["disjoint"]:
        tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=seed).split(Z, y, g))
        assert not (set(g[tr]) & set(g[te])), "vehicle leaked across the split"
        folds = [(tr, te)]
    else:
        folds = list(StratifiedKFold(5, shuffle=True, random_state=seed).split(Z, y))

    ys, ps, ts = [], [], []
    for tr, te in folds:
        if y[tr].sum() < 5 or y[te].sum() < 5:
            continue
        m = MODELS[MODEL](seed)
        m.fit(Z[tr], y[tr])
        ys.append(y[te])
        ps.append(m.predict_proba(Z[te])[:, 1])
        ts.append(trivial_raw[te])
    if not ys:
        return None
    yv, pv, tv = np.concatenate(ys), np.concatenate(ps), np.concatenate(ts)

    auc, ap = agree(yv, pv)
    t_auc, t_ap = agree(yv, tv)
    return {"auc": auc, "ap": ap, "trivial_auc": t_auc, "trivial_ap": t_ap,
            "n_test": len(yv), "prevalence": float(yv.mean()),
            "_y": yv, "_p": pv, "_t": tv}


def run(archive: str):
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)
    pseudomap = load_pseudomap(archive)
    out = []
    for name, cfg in STAGES.items():
        per_seed = [run_stage(ded, truth, pseudomap, cfg, s) for s in SEEDS]
        per_seed = [r for r in per_seed if r]
        if not per_seed:
            out.append({"archive": archive, "stage": name, "note": "degenerate"})
            continue
        aucs = np.array([r["auc"] for r in per_seed])
        aps = np.array([r["ap"] for r in per_seed])
        t_aucs = np.array([r["trivial_auc"] for r in per_seed])
        lo, hi = bootstrap_ci(per_seed[0]["_y"], per_seed[0]["_p"], n_boot=1000, seed=7)
        rec = {
            "archive": archive, "stage": name,
            "auc": round(float(aucs.mean()), 4),
            "auc_sd_over_seeds": round(float(aucs.std(ddof=1)), 4) if len(aucs) > 1 else 0.0,
            # bootstrap over the first seed's test set only; `auc` above is a mean
            # over five seeds, so the two describe different quantities and the
            # column names must say so.
            "auc_boot_lo_seed0": round(lo, 4), "auc_boot_hi_seed0": round(hi, 4),
            "ap": round(float(aps.mean()), 4),
            "trivial_auc": round(float(t_aucs.mean()), 4),
            "ml_minus_trivial": round(float(aucs.mean() - t_aucs.mean()), 4),
            "n_test": int(np.mean([r["n_test"] for r in per_seed])),
            "prevalence": round(float(np.mean([r["prevalence"] for r in per_seed])), 4),
            "seeds": len(per_seed),
        }
        out.append(rec)
        print(rec, flush=True)
    return out


if __name__ == "__main__":
    targets = [a for a in sys.argv[1:] if not a.startswith("-")] or ARCHIVES
    rows = []
    for a in targets:
        if not loader.cache_path(a).exists():
            print("skip " + a, flush=True)
            continue
        t0 = time.time()
        rows += run(a)
        print("-- {} done in {:.0f}s".format(a, time.time() - t0), flush=True)
        pd.DataFrame(rows).to_csv(out_path(targets), index=False)
    print("\nEXP9 DONE (model=%s) -> %s" % (MODEL, out_path(targets)))
