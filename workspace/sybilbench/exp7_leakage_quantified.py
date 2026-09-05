"""
Experiment 7 — how much of a published-style result is dataset artefact?

The audit (Findings 1, 4, 8, 10) says the VeReMi Sybil archives contain shortcuts. This experiment turns that
claim into a number by running the *same* detector pipeline under two protocols and reporting the gap.

NAIVE — the protocol reconstructed from common practice in the corpus:
  * features aggregated per vehicle using the ground-truth `sender` key
        (Azam 2022, the most-cited recent ML paper on this data, aggregates "movement pattern of the mobile
         nodes" per node before PCA/eigenvalues; a real receiver cannot do this — it must *infer* the
         partition, which is the hard part of the problem)
  * the raw pseudonym offered as a numeric feature   (Finding 1: it encodes the sender id 87-100 % of the time)
  * random k-fold cross-validation over pooled rows  (Azam 2022 uses random k-fold; one vehicle then appears
                                                      in both train and test)
  * the dataset's native ~30 % attacker prevalence   (Finding 4)

CONTROLLED — what the same pipeline scores once the shortcuts are removed:
  * aggregation keyed on `senderPseudo` only (no ground-truth identity anywhere in the features)
  * pseudonyms hashed to identity-free tokens
  * vehicle-disjoint splits
  * attacker prevalence subsampled to a realistic 3 % (Soderhall 2025: 3 % of users already cost 20 % travel time)
  * scored per attack family, because Finding 5 shows families differ by 50x in identity count

The difference is the inflation. Reported per family, because Finding 10 shows GridSybil is the only family
where the task is non-trivial at all.

Run:
    python -u workspace/sybilbench/exp7_leakage_quantified.py
    python -u workspace/sybilbench/exp7_leakage_quantified.py GridSybil_1416 DoSRandomSybil_0709
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, StratifiedKFold

sys.path.insert(0, "workspace")
from sybilbench import analysis, loader  # noqa: E402

ARCHIVES = [
    "GridSybil_0709", "GridSybil_1416",
    "DataReplaySybil_0709", "DataReplaySybil_1416",
    "DoSRandomSybil_0709", "DoSRandomSybil_1416",
    "DoSDisruptiveSybil_0709", "DoSDisruptiveSybil_1416",
]
SEEDS = [0, 1, 2]
TARGET_PREVALENCE = 0.03
# set by the CLI flag --drop-rate; see build_features
DROP_RATE_FEATURES = "--drop-rate" in sys.argv


def build_features(view: pd.DataFrame, key: str) -> pd.DataFrame:
    """Per-identity behavioural summary, aggregated on `key`.

    key='sender'      -> the naive protocol (ground-truth identity: a receiver cannot do this)
    key='token'       -> the controlled protocol (only what a receiver can observe)
    """
    g = view.groupby(key, observed=True)
    out = g.agg(
        n_msgs=("rcvTime", "size"),
        duration=("rcvTime", lambda t: t.max() - t.min()),
        spd_x_mean=("spd_x", "mean"), spd_y_mean=("spd_y", "mean"),
        spd_x_std=("spd_x", "std"), spd_y_std=("spd_y", "std"),
        acl_x_std=("acl_x", "std"), acl_y_std=("acl_y", "std"),
        pos_x_span=("pos_x", lambda v: v.max() - v.min()),
        pos_y_span=("pos_y", lambda v: v.max() - v.min()),
        posnoise=("pos_noise_x", "mean"),
        hednoise=("hed_noise_x", "mean"),
    )
    ded = view.drop_duplicates("messageID")
    iv = ded.sort_values("rcvTime").groupby(key, observed=True)["rcvTime"].apply(
        lambda t: float(np.median(np.diff(t.to_numpy()))) if len(t) > 1 else np.nan
    )
    out["interval_med"] = iv
    if DROP_RATE_FEATURES:
        # Finding 10: per-identity message rate and count alone separate 6 of 8 archives (AUC 1.000 / 0.994).
        # Leaving them in means both arms ride that shortcut, and the comparison measures nothing about
        # identity leakage. Dropping them isolates genuinely behavioural evidence.
        out = out.drop(columns=[c for c in ("n_msgs", "interval_med", "duration") if c in out])
    return out.fillna(0.0)


def subsample_prevalence(idx: pd.Index, y: np.ndarray, target: float, seed: int):
    """Down-sample the positive class to a realistic attacker prevalence."""
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero(y == 1)
    neg = np.flatnonzero(y == 0)
    keep_pos = int(round(target * len(neg) / (1 - target)))
    if keep_pos < 10 or keep_pos >= len(pos):
        return np.arange(len(y))
    pos = rng.choice(pos, keep_pos, replace=False)
    sel = np.concatenate([pos, neg])
    rng.shuffle(sel)
    return sel


def score_naive(view, truth, seed):
    """Ground-truth aggregation + pseudonym feature + random k-fold + native prevalence."""
    v = view.copy()
    v["sender"] = v["token"].map(truth.token_to_sender)
    v = v[v["sender"].notna()]
    X = build_features(v, "sender")
    # the leak: an identifier offered as a feature, as it appears in the raw files
    pseudo_num = v.groupby("sender", observed=True)["token"].first().map(lambda t: int(t[:8], 16) % 10**7)
    X["pseudo_id"] = pseudo_num
    y = np.array([1 if truth.sender_to_attack.get(int(s), 0) != 0 else 0 for s in X.index])
    if y.sum() < 20 or (1 - y).sum() < 20:
        return np.nan, np.nan
    Z = PCA(n_components=min(6, X.shape[1]), random_state=seed).fit_transform(
        (X - X.mean()) / (X.std().replace(0, 1))
    )
    aucs, aps = [], []
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(Z, y):
        m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=seed)
        m.fit(Z[tr], y[tr])
        p = m.predict_proba(Z[te])[:, 1]
        aucs.append(roc_auc_score(y[te], p))
        aps.append(average_precision_score(y[te], p))
    return float(np.mean(aucs)), float(np.mean(aps))


def score_controlled(view, truth, seed):
    """Observable aggregation only + vehicle-disjoint split + realistic prevalence."""
    X = build_features(view, "token")
    senders = pd.Series(X.index.map(lambda t: truth.token_to_sender.get(t, -1)), index=X.index)
    y = np.array([1 if truth.sender_to_attack.get(int(s), 0) != 0 else 0 for s in senders])
    if y.sum() < 20 or (1 - y).sum() < 20:
        return np.nan, np.nan

    sel = subsample_prevalence(X.index, y, TARGET_PREVALENCE, seed)
    Xs, ys, gs = X.iloc[sel], y[sel], senders.iloc[sel].to_numpy()
    if ys.sum() < 10:
        return np.nan, np.nan
    Z = ((Xs - Xs.mean()) / Xs.std().replace(0, 1)).to_numpy()

    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=seed).split(Z, ys, gs))
    if ys[te].sum() < 5 or ys[tr].sum() < 5:
        return np.nan, np.nan
    m = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=seed)
    m.fit(Z[tr], ys[tr])
    p = m.predict_proba(Z[te])[:, 1]
    return float(roc_auc_score(ys[te], p)), float(average_precision_score(ys[te], p))


def run(archive: str) -> dict:
    view, truth = loader.load_cache(archive)
    view["token"] = view["token"].astype(str)
    ded = analysis.transmissions(view)

    n_auc, n_ap, c_auc, c_ap = [], [], [], []
    for s in SEEDS:
        a, b = score_naive(ded, truth, s)
        if not np.isnan(a):
            n_auc.append(a); n_ap.append(b)
        a, b = score_controlled(ded, truth, s)
        if not np.isnan(a):
            c_auc.append(a); c_ap.append(b)

    r = {
        "archive": archive,
        "naive_auc": round(float(np.mean(n_auc)), 4) if n_auc else np.nan,
        "naive_ap": round(float(np.mean(n_ap)), 4) if n_ap else np.nan,
        "controlled_auc": round(float(np.mean(c_auc)), 4) if c_auc else np.nan,
        "controlled_ap": round(float(np.mean(c_ap)), 4) if c_ap else np.nan,
    }
    if n_auc and c_auc:
        r["auc_inflation"] = round(r["naive_auc"] - r["controlled_auc"], 4)
        r["ap_inflation"] = round(r["naive_ap"] - r["controlled_ap"], 4)
    print(r, flush=True)
    return r


if __name__ == "__main__":
    archives = [a for a in sys.argv[1:] if not a.startswith("--")] or ARCHIVES
    suffix = "_norate" if DROP_RATE_FEATURES else ""
    rows = []
    for a in archives:
        if not loader.cache_path(a).exists():
            print(f"skip {a} (not cached — run run_ingest.py first)", flush=True)
            continue
        try:
            rows.append(run(a))
        except Exception as e:
            print(f"{a}: FAILED {type(e).__name__}: {e}", flush=True)
    out = pd.DataFrame(rows)
    path = f"workspace/sybilbench/exp7_leakage_quantified{suffix}.csv"
    out.to_csv(path, index=False)
    print(f"\nEXP7 DONE -> {path}")
    print(out.to_string(index=False))
    if "auc_inflation" in out:
        print(f"\nmean AUC inflation {out.auc_inflation.mean():.3f} | mean AP inflation {out.ap_inflation.mean():.3f}")
